from typing import Tuple, List

from config import get_settings, Settings
from modules.rules.models import RuleModel

from modules.rules.services import RuleService

from lib.kafka.client import KafkaClient
from lib.kafka.decorators import kafka_listener, kafka_deserializer

from . import deserializer

import logging

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('alert_remove')
logger.setLevel('DEBUG')

setting:Settings = get_settings(configuration_file="alert_remove")

class RemoveAlertConsumer():
    _rule_service:RuleService
    _kafka_client:KafkaClient

    def __init__(self, 
        rule_service:RuleService,
        kafka_client:KafkaClient
    ):
        self._rule_service = rule_service
        self._kafka_client = kafka_client

    @kafka_listener(
        topic=setting.broker_config.inbound_topic, 
        group_id=setting.broker_config.consumer_group_id, 
        partition=setting.broker_config.inbound_partition, 
        idempotent=True
    )
    async def __call__(self, headers:List[Tuple[str, bytes]], key:str, value:bytes, topic:str, partition:int):
        logger.debug(f"Receive key: {key}, topic: {topic}, data: {value}, Headers: {headers}, partition:{partition}")

        rule_models = self.deserialize(value, topic)

        await self._rule_service.remove_rules(rule_models)
   

    @kafka_deserializer(deserizlier=deserializer.Deserializer, schema=setting.broker_config.deserializer_schema)
    def deserialize(self, message:List[RuleModel], topic:str):
        logger.debug(f"Deserialize data: {message}")
        return message
