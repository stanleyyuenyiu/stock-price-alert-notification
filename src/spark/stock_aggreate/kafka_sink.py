# import os
# import sys
# sys.path.insert(0, os.path.abspath('..'))

# from foreach_sink_operator import ForEachOperator
# from confluent_kafka import Producer
# from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
# from confluent_kafka.schema_registry import SchemaRegistryClient

# class KafkaProducer:
#     def __init__(self) -> None:
#         self.conf = None
#         self.producer = None

#     def createProducer(self, conf):
#         producer_conf = {}
#         prefix = "kafka."

#         for key in conf:
#             if key.startswith(prefix):
#                producer_conf[key[len(prefix):]] = conf[key]

#         self.producer = Producer(producer_conf)
#         self.conf = conf

#         schema_registry_conf = {'url': conf['schema_registry']}
#         schema_registry_client = SchemaRegistryClient(schema_registry_conf)

#         self.string_serializer = StringSerializer('utf8')
#         self.protobuf_serializer = ProtobufSerializer(KafkaMessage.MessageCompress, schema_registry_client, {'use.deprecated.format': False})

#         return self

#     def send(self, message):
#         self.producer.produce(topic=self.conf['topic'], partition=self.conf['partition'],
#                             value=self.protobuf_serializer(message, SerializationContext(self.conf['topic'], MessageField.VALUE)))
#         self.producer.poll(1)

# class KafkaSink:
#     def __init__(self, conf) -> None:
#         self.conf = conf
        
#     def send(self, message) :
#         self.producer = KafkaProducer().createProducer(self.conf)
#         self.producer.send(message)


# class KafkaSinkOperator(ForEachOperator):
#     def __init__(self, producer) -> None:
#         self.producer = producer

#     def open(self, partition_id, epoch_id):
#         return True

#     def process(self, row):
#         message = KafkaMessage.MessageCompress(
#             symbol=row.Symbol, 
#             count=int(row.Count),
#             min_price=float(row.Min_Price), 
#             max_price=float(row.Max_Price)
#         )
#         self.producer.value.send(message)

#     def close(self, err):
#         if err:
#             raise err