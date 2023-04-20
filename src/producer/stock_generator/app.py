from typing import Optional
from confluent_kafka import SerializingProducer

from config.config_stock_generator import get_settings

import random
import asyncio
from datetime import datetime
from uuid import uuid4
from abc import ABC, abstractmethod
from lib.utils.serializer import json_serialize
from lib.utils.queue import load_msg_schema
from lib.utils.hashing import object2hash, consistent_hash

from lib.kafka.models import Event

from lib.kafka.services import KafkaProducer

class StreamEvent(ABC):
     def __init__(self) -> None:
         self.Id = "0"
         self.Timestamp = str(datetime.now())

class StockEvent(StreamEvent):
    def __init__(self) -> None:
        super().__init__()
        self.Symbol = None
        self.Price = 0
        self.Vol = 0

class StockEventMock():
    def __init__(self, mock = "abcdefghijklmnopqrstu") -> None:
        self.mock = mock
    
    def generate(self, id = uuid4()):
        event = StockEvent()
        event.Symbol = str(int(random.random() * 1000))
        event.Price = int(random.random() * 1000)
        event.Vol = int(random.random() * 1000)
        event.Id = id
        return event

class StockGenerator():
    def __init__(self, producer:KafkaProducer, outbound_topic, outbound_partition_range, message_cnt) -> None:
        super().__init__()
        self._outbound_partition_range = outbound_partition_range
        self._outbound_topic = outbound_topic
        self._producer = producer
        self._message_cnt = message_cnt

    def acked(self, err, msg):
        if err is not None:
            print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
        else:
            print("Message produced: key %s; offset %s; value %s" % ( msg.key(), msg.offset(), msg.value()))
    
    async def run(self):
        i = self._message_cnt
        
        mockEvent = StockEventMock()

        while i > 0:
            
            event = mockEvent.generate(i)

            key = object2hash(event.__dict__)

            msg = Event(key=key, payload=event.__dict__)

            self._producer.publish(
                topic=self._outbound_topic, 
                key=key, 
                msg=msg.dict(), 
                partition=consistent_hash(event.Symbol, self._outbound_partition_range), 
                on_delivery=self.acked)

            self._producer.poll(1)

            await asyncio.sleep(0.01)

            i -= 1

async def app(message_cnt:Optional[int] = 200):
    setting = get_settings()
    producer_conf = {
            'bootstrap.servers': setting.broker_uri,
            'enable.idempotence': True,
            'value.serializer': json_serialize
    }

    producer = Producer(producer=SerializingProducer(producer_conf))
    
    generator = StockGenerator( 
        producer=producer, 
        outbound_topic=setting.outbound_topic, 
        outbound_partition_range=setting.outbound_partition_range, 
        message_cnt=message_cnt)

    await generator.run()
  