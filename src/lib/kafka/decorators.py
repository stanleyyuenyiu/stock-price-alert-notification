from . import services
import functools
from abc import ABCMeta
from typing import Any, Callable, Optional
from inspect import iscoroutinefunction
from lib.utils.schema import load_schema

from confluent_kafka.serialization import SerializationContext, MessageField

def kafka_listener(topic:str, group_id:str, partition:int, idempotent:bool):
    def inner_decorator(f:Callable):
        @functools.wraps(f)
        async def wrapped(funcself):
            consumer = services.KafkaConsumer(topic, group_id, partition, idempotent)
            await consumer(f, funcself)
        return wrapped
    return inner_decorator


def kafka_producer(topic:str, partition:int = -1):
    def inner_decorator(f:Callable):
        @functools.wraps(f)
        async def wrapped(funcself, *args, **kwargs):
            producer = services.KafkaProducer()
           
            async for key,message in f(funcself, *args, **kwargs):
                producer.publish(
                    topic=topic, 
                    key=key, 
                    msg=message, 
                    partition=partition)
        return wrapped
    return inner_decorator

def kafka_deserializer(deserizlier:ABCMeta, schema:Optional[str]):
    deserializer_instance = deserizlier(load_schema(schema))
 
    def inner_decorator(f:Callable):
        @functools.wraps(f)
        async def async_wrapper(funcself:Any, msg:bytes, topic:str):
            deserialized_msg = deserializer_instance(msg, SerializationContext(topic, MessageField.VALUE))
            return await f(funcself, deserialized_msg, topic)

        @functools.wraps(f)
        def wrapper(funcself:Any, msg:bytes, topic:str):
            deserialized_msg = deserializer_instance(msg, SerializationContext(topic, MessageField.VALUE))
            return f(funcself, deserialized_msg, topic)

        return async_wrapper if iscoroutinefunction(f) else wrapper
    return inner_decorator
