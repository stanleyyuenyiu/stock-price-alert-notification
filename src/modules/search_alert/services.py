from typing import List,Any, Optional, Callable
import logging

from datetime import datetime
from lib.kafka.client import KafkaClient

from lib.utils.serializer import json_serialize_str
from lib.utils.queue import load_msg_schema
from lib.utils.hashing import sha256_hex_hash

from modules.outbox.entities import Outbox
from modules.rules.services import RuleService
from .models import StockAggreateModel
from lib.database.decorators import transactional
from modules.rules.models import RuleDocModel, RuleModel

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('alert_search')
logger.setLevel('DEBUG')

class SearchAlertService():

    def __init__(self,
        kafka_client:KafkaClient ,
        rule_service:RuleService
    ) -> None:
        self._kafka_client = kafka_client
        self._rule_service = rule_service

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
      
        data = await self._rule_service.search(search)
        logger.debug(f"return {len(data)} rule data")
        return data
 
    @transactional
    def publish_event(self, rules:List[RuleModel]) :
        
        logger.debug(f"process oubbox event start")

        self._rule_service.find_all_by_ids()

        events = []
        ids = []

        for i in range(len(rules)):
            rule = rules[i]
            id = rule.rule_id
            
            self._rule_service.trigger( Event( key=id, payload=rule.dict() ))
        
            events.append(rule.dict())
            ids.append(id)

            if (i+1)%1 == 0 or i == len(rules)-1:
                self._emit_event(events, ids)
                ids = []
                events = []
                
        logger.debug(f"process oubbox event done")