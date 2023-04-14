from confluent_kafka import  SerializingProducer, Consumer
from confluent_kafka.cimpl import Producer as ProducerImpl, Consumer as ConsumerImpl
from lib.utils.serializer import json_serialize
import dataclasses

@dataclasses.dataclass
class KafkaClientConfig:
    broker_uri: str
    consumer_group_id: str
    transaction_id: str

class KafkaClient():
    _consumer:ConsumerImpl
    _producer:ProducerImpl
    _consumer_conf:dict
    _producer_conf:dict

    def __init__(self, config:KafkaClientConfig) -> None:
        super().__init__()
        print("init kafka client")

        self._consumer_conf = {
                'bootstrap.servers': config.broker_uri,
                'group.id': config.consumer_group_id,
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': False,
                'enable.partition.eof': True,
        }

        self._consumer = Consumer(self._consumer_conf)

        self._producer_conf = {
                'bootstrap.servers': config.broker_uri,
                'transactional.id': config.transaction_id,
                'enable.idempotence': True,
                'value.serializer': json_serialize
        }
        self._producer = SerializingProducer(self._producer_conf)

    @property
    def consumer(self) -> ConsumerImpl:
        return self._consumer

    @property
    def producer(self) -> ProducerImpl:
        return self._producer

    @property
    def consumer_config(self) -> dict:
        return self._consumer_conf

    @property
    def producer_conf(self) -> dict:
        return self._producer_conf
       