from typing import Tuple, List
import logging

from lib.utils.hashing import sha256_hex_hash
from lib.database.decorators import transaction
from lib.kafka.client import KafkaClient
from lib.kafka.decorators import kafka_listener, kafka_deserializer
from lib.consumer import ConsumerListenerImp

from modules.idempotent_event.services import IdempotentEventService
from modules.outbox import OutboxServiceImpl
from modules.outbox.models import Event

from modules.rules.models import RuleDocModel, RuleModel
from modules.rules.services import RuleService

from config import get_settings, Settings

from .models import StockAggreateModel
from .deserializer import StockAggreateDeserializer

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('alert_search')
logger.setLevel('DEBUG')

setting:Settings = get_settings(configuration_file="alert_search")


class SearchAlertConsumer(ConsumerListenerImp):
    _kafka_client:KafkaClient
    _rule_service:RuleService
    _outbox_service:OutboxServiceImpl
    _idempotent_service:IdempotentEventService

    def __init__(self, 
        kafka_client:KafkaClient ,
        rule_service:RuleService,
        outbox_service:OutboxServiceImpl,
        idempotent_service:IdempotentEventService
    ):
        self._kafka_client = kafka_client
        self._rule_service = rule_service
        self._outbox_service = outbox_service
        self._idempotent_service = idempotent_service

    @kafka_listener(
        topic=setting.broker_config.inbound_topic, 
        group_id=setting.broker_config.consumer_group_id, 
        partition=setting.broker_config.inbound_partition, 
        idempotent=True
    )
    async def __call__(self, headers:List[Tuple[str, bytes]], key:str, value:bytes, topic:str, partition:int):

        logger.debug(f"Receive key: {key}, topic: {topic}, data: {value}, Headers: {headers}, partition:{partition}")

        deserialized_obj = self.deserialize(value, topic)

        rules:List[RuleModel] = await self.search_rule(deserialized_obj)

        self.emit_outbox_event(rules)
    
    async def search_rule(self, item:StockAggreateModel):
        logger.debug(f"Search rule data by: {item.__dict__}")
        
        search:List[RuleDocModel] = [
            RuleDocModel(
                value=item.max_price,
                symbol=item.symbol
            )
        ]

        if item.max_price != item.min_price:
            search.append(
                RuleDocModel(
                    value=item.min_price,
                    symbol=item.symbol
                )
            )
      
        data = await self._rule_service.find_all(search)
        logger.debug(f"return {len(data)} rule data")
        return data

    @transaction
    def emit_outbox_event(self, rules:List[RuleModel]) :
        
        logger.debug(f"process oubbox event start")

        events = []
        ids = []

        for i in range(len(rules)):
            rule = rules[i]
            id = rule.rule_id
            
            self._outbox_service.save( Event( key=id, payload=rule.dict() ) )
        
            events.append(rule.dict())
            ids.append(id)

            if (i+1)%1 == 0 or i == len(rules)-1:
                self.emit_event(events, ids)
                ids = []
                events = []
                
        logger.debug(f"process oubbox event done")
        
    def emit_event(self, events, ids) :
        payload = Event(
                    key=sha256_hex_hash(''.join(ids)),
                    payload=events
                )
        
        topic = setting.broker_config.outbound_topic 
        key = payload.key
        message = payload.dict()
        partition = setting.broker_config.outbound_partition
        
        self._kafka_client.producer.produce(
                    topic=topic, 
                    key=key, 
                    value=message, 
                    partition=partition)
    
    @kafka_deserializer(deserizlier=StockAggreateDeserializer, schema=setting.broker_config.deserializer_schema)
    def deserialize(self, message:StockAggreateModel, topic:str):
        logger.debug(f"Deserialize data: {message.__dict__}")
        return message
