from typing import Optional,Dict
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,StructField,TimestampType,IntegerType,StringType,FloatType
from pyspark.sql.functions import from_json, window, to_json,col,struct, session_window, lit, sha2,concat_ws, current_timestamp, unix_timestamp, explode
from pyspark.sql.avro.functions import from_avro, to_avro
from pyspark.sql import functions as F
from lib.utils.schema import load_spark_schema

from abc import ABC, abstractmethod
from . import db_sink
# from kafka_sink import KafkaSink, KafkaSinkOperator
import json

salt_value = "test"
class SparkAppConfig: 
    def __init__(self, appname:str, sparkAppConfig:Optional[Dict[str, str]], readConfig:Optional[Dict[str, str]], writeConfig:Optional[Dict[str, str]], loggingLevel:str = "ERROR" ) -> None:
        self.appName = appname
        self.sparkAppConfig = sparkAppConfig
        self.loggingLevel = loggingLevel
        self.readConfig = readConfig
        self.writeConfig = writeConfig

class SparkStreamController(ABC):
      def __init__(self, sparkConfig:SparkAppConfig) -> None:
        super().__init__()
        self.sparkConfig = sparkConfig
        self.sparkSession = self.createSparkSession(sparkConfig)
        self.sparkSession.sparkContext.setLogLevel(sparkConfig.loggingLevel)
        self.dataFrame = None
        # obj = KafkaSink(self.sparkConfig.writeConfig)
        # self.kafkaProducer = self.sparkSession.sparkContext.broadcast(obj)

        self._schema = load_spark_schema('spark_stock_schema.json')
 

      def createSparkSession(self, sparkConfig:SparkAppConfig) -> SparkSession:
            sessionBuilder = SparkSession \
                                .builder \
                                .appName(sparkConfig.appName)
            for k in sparkConfig.sparkAppConfig:
                  sessionBuilder.config(k, sparkConfig.sparkAppConfig[k])
            return sessionBuilder.getOrCreate()

      def readStream(self): 
            self.dataFrame = self.sparkSession \
                .readStream \
                .format("kafka") \
                .options(**self.sparkConfig.readConfig) \
                .load() 

      def aggregate(self): 
            schema = StructType.fromJson(self._schema)

            self.dataFrame =  self.dataFrame.selectExpr("CAST(value AS STRING) as valueStr"). \
                select(from_json(col("valueStr"), schema).alias("data")).\
                select(
                    col("data.payload.Id").alias("id"),
                    col("data.payload.Symbol").alias("symbol"),
                    col("data.payload.Price").alias("price"),
                    col("data.payload.Timestamp").alias("timestamp")
                ) .\
                withWatermark("timestamp", "1 second"). \
                groupBy(
                    window("timestamp", "10 seconds"),
                    "symbol"
                ). \
                agg(
                    F.count("*").alias("count"), 
                    F.min("price").alias("min_price"),
                    F.max("price").alias("max_price")
                ) 

      def fatten(self):
            self.dataFrame = self.dataFrame.selectExpr("max_price", "min_price","symbol", "count", "window", "CAST(window AS STRING) as windowStr").\
                withColumn('key', 
                sha2(concat_ws(
                    '_',
                     lit(salt_value), 
                     col('symbol'), 
                     col('windowStr'), 
                     col('min_price'), 
                     col('max_price')
                     ), 256)
                ).\
                withColumn('version', lit(1)).\
                withColumn('created_at', unix_timestamp())
            
      
            self.dataFrame = self.dataFrame.select(col('key'),col('version'), col('created_at'),  struct("max_price", "min_price","symbol", "count", "window").alias("payload"))

      def toJson(self, colName:str = "value") :
            self.dataFrame = self.dataFrame.select(
                    to_json(struct("*"))
                ).toDF(colName)

      def toAvro(self, colName:str = "value") :
          self.dataFrame = self.dataFrame.select(to_avro(struct("*"))).toDF(colName)


      def sinkConsole(self): 
            self.dataFrame.select("*",lit(1).alias('partition')).writeStream \
                .format("console") \
                .outputMode("update") \
                .option("truncate", False) \
                .option("numRows", 10000) \
                .start() \
                .awaitTermination()

      def sinkKafka(self): 
            if "partition" in self.sparkConfig.writeConfig:
                self.dataFrame = self.dataFrame.select("*",lit(self.sparkConfig.writeConfig['partition']).alias('partition'))

            self.dataFrame.writeStream \
                .format("kafka") \
                .outputMode("update") \
                .option("checkpointLocation", "checkpt") \
                .options(**self.sparkConfig.writeConfig) \
                .start() \
                .awaitTermination()

      def writeDB(self): 
          self.dataFrame.writeStream.foreach(db_sink.DbSinkOperator()).outputMode("update").start().awaitTermination()
      
    #   def wrtieKafka(self):
    #         self.dataFrame.writeStream.foreach(KafkaSinkOperator(self.kafkaProducer)).outputMode("update").start().awaitTermination()

      def writeDBByBatch(self): 
          self.dataFrame.writeStream.foreachBatch(self.writeToPostgresql).start().awaitTermination()

      def writeToPostgresql(self, batchDF, batch_id):
        try:
            #batchDF.persist()
            print(batchDF.show(10000, truncate=False))
            # batchDF.write \
            # .format("jdbc") \
            # .option("url", "jdbc:postgresql://localhost:5432/kafka") \
            # .option("driver", "org.postgresql.Driver") \
            # .option("dbtable", "stock_agg") \
            # .option("user", "postgres") \
            # .option("password", "postgres") \
            # .option("checkpointLocation", "chk-point-dir") \
            # .mode("append") \
            # .save()
            #batchDF.unpersist()
        except Exception as e:
           print(f"Error writing batch {batch_id}: {e}")



def app():
    partition = 10

    sparkAppConfig = {"spark.driver.host":"localhost"}

    input =  json.dumps({"incoming":[partition]})

    readConfig = {
        "kafka.bootstrap.servers": "localhost:9092",
        "assign": input,
        "startingOffsets": "earliest"
    }
    writeConfig = {
        "kafka.bootstrap.servers": "localhost:9092",
        "schema_registry":"http://localhost:8081",
        "topic": "compress",
        "partition": partition
    }    

    config = SparkAppConfig(appname="SparkStructuredStreaming", sparkAppConfig=sparkAppConfig, readConfig=readConfig, writeConfig=writeConfig)
    controller = SparkStreamController(config)
    controller.readStream()
    controller.aggregate()
    controller.fatten()
    controller.toJson()
    # #controller.toAvro()
    controller.sinkKafka()

