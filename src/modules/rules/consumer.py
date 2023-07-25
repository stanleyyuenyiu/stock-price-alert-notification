from typing import Tuple, List, Dict, Any
import logging

from lib.kafka.client import KafkaClient
from lib.kafka.models import IdempotentConfig

from lib.kafka.decorators import kafka_listener, kafka_deserializer
from lib.consumer import ConsumerListenerImp

from modules.outbox.models import Event

from modules.rules.models import  RuleModel
from modules.rules.services import RuleSearchService

from config import get_settings, Settings

from .deserializer import Deserializer

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('alert_search')
logger.setLevel('DEBUG')

setting:Settings = get_settings(configuration_file="outbox_rule")

from enum import Enum

class OutboxMessageHeader(Enum):
    EVEMT_TYPE = "eventType"
    ID = "id"

class EventType(Enum):
    ADD = "add"
    UPDATE = "update"
    DEL = "delete"


class RuleOutboxConsumer(ConsumerListenerImp):
    _kafka_client:KafkaClient
    _rule_service:RuleSearchService

    def __init__(self, 
        kafka_client:KafkaClient ,
        rule_search_service:RuleSearchService,
    ):
        self._kafka_client = kafka_client
        self._rule_service = rule_search_service

    @kafka_listener(
        topic=setting.broker_config.inbound_topic, 
        group_id=setting.broker_config.consumer_group_id, 
        partition=setting.broker_config.inbound_partition, 
        idempotent=IdempotentConfig( enable=False,id_placement = "headers.id" )
    )
    async def __call__(self, headers:Dict[str, Any], key:str, value:bytes, topic:str, partition:int):

        logger.debug(f"Receive key: {key}, topic: {topic}, data: {value}, Headers: {headers}, partition:{partition}")

        event:Event = self.deserialize(value, topic)

        event_type = OutboxMessageHeader.EVEMT_TYPE.value
        
        try:
            if event_type in headers:
                action = headers[event_type]
                if action == EventType.ADD.value:
                    await self._rule_service.create_rule(event.payload) 
                elif action == EventType.UPDATE.value:
                    await self._rule_service.update_rule(event.payload)
                elif action == EventType.DEL.value:
                    await self._rule_service.delete_rule(event.key)
        except Exception as e:
            logger.debug(e)
            pass
        
    
    @kafka_deserializer(deserizlier=Deserializer, schema=setting.broker_config.deserializer_schema)
    def deserialize(self, message:RuleModel, topic:str):
        logger.debug(f"Deserialize data: {message.__dict__}")
        return message
