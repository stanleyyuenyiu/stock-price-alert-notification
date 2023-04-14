
from lib.kafka.client import KafkaClient
from typing import Optional, Any, Callable
import asyncio
from dependency_injector.wiring import Provide, inject
from confluent_kafka.cimpl import Producer as ProducerImpl, Consumer as ConsumerImpl
from confluent_kafka import KafkaError, TopicPartition, KafkaException
from confluent_kafka.serialization import SerializationError

from modules.idempotent_event.services import IdempotentEventService
from lib.database.decorators import transaction
from exceptions.duplicate_event import DuplicateEventException
from exceptions.retrable_event import RetrableEventException
from exceptions.abort_event import  AbortEventException

from lib.utils.signal import LifeSpanMgr
import logging

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('Broker')
logger.setLevel('DEBUG')


class KafkaProducer():
    @inject
    def __init__(self, 
        kafka_client:KafkaClient = Provide["kafka_client"],
    ):
        self._producer = kafka_client.producer

    @property
    def producer(self) -> ProducerImpl:
        return self._producer

    def poll(self, interval:int):
        return self._producer.poll(interval)

    def acked(self, err, msg) -> None:
        pass
        # if err is not None:
        #     print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
        # else:
        #     print("Message produced: key %s; offset %s; value %s" % ( msg.key(), msg.offset(), msg.value()))


    def publish(self, topic:str, key:str, msg:Any, partition:Optional[int] = -1, on_delivery:Optional[Callable] = None):
        if on_delivery is None:
            on_delivery = self.acked

        if partition < 0:
            self._producer.produce(topic=topic, key=key, value=msg, on_delivery=on_delivery)
        else:
            self._producer.produce(topic=topic, key=key, value=msg, partition=partition, on_delivery=on_delivery)


class KafkaConsumer():
    @inject
    def __init__(self, 
        topic:str, 
        group_id:str, 
        partition:int = -1, 
        idempotent:bool = True,
        kafka_client:KafkaClient = Provide["kafka_client"],
        idempotent_service:IdempotentEventService = Provide["idempotent_event_module.idempotent_event_service"],
    ):
        self._topic:str = topic
        self._group_id:str = group_id
        self._partition:int = partition
        self._kafka_client = kafka_client
        self._producer, self._consumer = kafka_client.producer, kafka_client.consumer
        self._idempotent_service:IdempotentEventService = idempotent_service
        self._idempotent = idempotent

    @property
    def topic(self):
        return self._topic

    @property
    def group_id(self):
        return self._group_id

    @property
    def partition(self):
        return self._partition
        
    @property
    def consumer(self) -> ConsumerImpl:
        return self._consumer

    @property
    def producer(self) -> ProducerImpl:
        return self._producer
    
    def begin_transaction(self):
        try:
            self._producer.init_transactions()
        except Exception as e:
            raise AbortEventException(e)

    def commit(self):
        try:
            position = self._consumer.position(self._consumer.assignment())
            metadata = self._consumer.consumer_group_metadata()
            logger.debug(f"commiting offset - {position}")
            #self._producer.send_offsets_to_transaction(position,metadata)
            self._producer.commit_transaction()
            self._producer.begin_transaction()
        except KafkaException as e:
            if e.args[0].retriable():
                raise RetrableEventException(e)
            elif e.args[0].txn_requires_abort():
                self._producer.abort_transaction()
                self._producer.begin_transaction()
            else:
                raise AbortEventException(e)
        except Exception as e:
            raise AbortEventException(e)

    def prepare_consume(self, topic: str, partition:Optional[int] = -1):
        if partition < 0:
            logger.debug(f"listen to topic {topic}")
            self._consumer.subscribe([topic])
        else:
            logger.debug(f"listen to topic {topic}, partition {partition}")
            self._consumer.assign([TopicPartition(topic, partition)])

    def consume(self):
        return self._consumer.poll(1)
    
    def stop_consume(self):
        self._consumer.close()

    def is_eof(self, msg):
        return msg.error().code() == KafkaError._PARTITION_EOF

    async def __call__(self, handler:Callable, handler_instance:object) -> None:
        try:
            self.begin_transaction()
            self._producer.begin_transaction()
            self.prepare_consume(self.topic, self.partition)
            
            while not LifeSpanMgr.is_shutdown():
                try:
                    message = self.consume()
                    logger.debug("pull message")
                    
                    if message:
                        if not message.error():
                            if self._idempotent and message.key():
                                self.deduplicate(message.key().decode('utf-8'), self._kafka_client.consumer_config['group.id'])
                                
                            await handler(handler_instance, message.headers(), message.key(), message.value(), message.topic(), message.partition())
                            
                            logger.debug("[normal] commit transaction")

                            self.commit()
                        else:
                            if self.is_eof(message):
                                logger.debug("Reach Eof")
                            else:
                                logger.error(f"message error:{message.error()}")
                    
                    await asyncio.sleep(0.02)
                except DuplicateEventException as e:
                    logger.error(f"Throwing DuplicateEventException:{e}")
                    self.abort("[DuplicateEventException]")
                    self.commit()
                    logger.error(f"[Exception] move next")
                except RetrableEventException as e:
                    logger.error(f"Throwing RetrableEventException:{e}")
                    self.abort("[RetrableEventException]")
                    logger.error(f"go to other queue")
                    self.commit()
                except AbortEventException as e:
                    logger.error(f"Throwing AbortEventException:{e}")
                    self.abort("[AbortEventException]")
                    raise
                except Exception as e:
                    logger.error(f"Throwing unknown Exception:{e}")
                    self.abort("[Exception]")
                    raise

        except Exception as e:
            logger.error(f"Throwing error:{e}")
            logger.error(f"[Final] abort transaction")
            self._producer.abort_transaction()
            self.stop_consume()
            raise
        finally:
            logger.info("shutdown")
    
    @transaction
    def deduplicate(self, key:str, group_id:str):
        self._idempotent_service.save_and_flush(f"{group_id}-{key}")

    def abort(self, section):
        logger.error(f"{section} abort transaction")
        self._producer.abort_transaction()
        logger.error(f"{section} start new transaction")
        self._producer.begin_transaction()