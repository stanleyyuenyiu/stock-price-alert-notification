# from typing import List,Any, Optional, Callable
# from datetime import datetime
# from lib.kafka.client import KafkaClient

# from lib.utils.serializer import json_serialize_str
# from lib.utils.queue import load_msg_schema
# from lib.utils.hashing import sha256_hex_hash

# from modules.outbox.entities import SearchAlertEntity
# from modules.outbox import OutboxRepositoryImpl
# from modules.outbox.models import Event

# from lib.database.client import transaction


# class SearchAlertService():

#     def __init__(self,
#         kafka_client:KafkaClient ,
#         search_alert_repo:OutboxRepository
#     ) -> None:
#         self._kafka_client = kafka_client
#         self._outbox_repo = search_alert_repo

#     @transaction
#     def publish_outbox_event(self, events:List[object], topic:str, partition:int):
#         msg_count = 0
#         subevents = []
#         subevent_id = ""

#         for i in range(len(events)):
#             rule = events[i]

#             self._outbox_repo.save(SearchAlertEntity(data=json_serialize_str(rule), id=rule['_id'], version="1", created_at=int(datetime.utcnow().timestamp())))
            
#             # subevent_id += rule['_id']
#             # subevents.append(rule)
#             # msg_count += 1

#             # if msg_count%5 == 0 or i == len(events)-1:
#             #     payload = Event(
#             #         key=sha256_hex_hash(subevent_id),
#             #         payload=subevents
#             #     )
#             #     self.publish(topic , payload.key, payload.dict(), partition)
#             #     subevent_id = ""
#             #     subevents = []

  
#     def publish(self, topic:str, key:str, msg:Any, partition:Optional[int] = -1, on_delivery:Optional[Callable] = None):
#         if partition < 0:
#             self._kafka_client.producer.produce(topic=topic, key=key, value=msg, on_delivery=on_delivery)
#         else:
#             self._kafka_client.producer.produce(topic=topic, key=key, value=msg, partition=partition, on_delivery=on_delivery)