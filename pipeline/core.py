import os
from abc import ABC, abstractmethod
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, struct, to_json, split, when
from pyspark.sql.functions import window, mean, stddev, count
from . import config


class STATUS:
    SAFE = "SAFE"
    WARN = 'WARN'
    ERROR = "ERROR"


class Pipeline(ABC):
    _spark = None
    """
        An ETL class to read data from kafka and preprocess on it and write data to kafka

    """

    @property
    @abstractmethod
    def spark_configs(self) -> dict:
        pass

    @property
    @abstractmethod
    def kafka_read_configs(self) -> dict:
        pass

    @property
    @abstractmethod
    def kafka_write_configs(self) -> dict:
        pass

    @property
    @abstractmethod
    def topic(self) -> str:
        pass

    @property
    def spark(self) -> SparkSession:
        """
        :return:  A singleton sparkSession object
        """
        if self._spark is not None:
            return self._spark

        builder = SparkSession.builder
        for key, value in self.spark_configs.items():
            builder.config(key, value)

        # return spark session
        self._spark = builder.getOrCreate()
        return self._spark

    def read_from_kafka(self) -> DataFrame:
        df = self.spark.readStream.format('kafka').options(**self.kafka_read_configs).load()
        df = df.withColumn("data", split(col("value").cast("string"), ','))
        df = df.select(col('key').cast("string").alias("_key"), (df.data[0] / 1000).cast("timestamp").alias("timestamp"), df.data[1].alias("cpu"))
        return df

    @abstractmethod
    def transform(self, df: DataFrame) -> DataFrame:
        pass

    def write_to_kafka(self, df: DataFrame):
        df = df.withColumnRenamed("_key", "key")
        df = df.withColumn("value", to_json(struct('*').dropFields("key")))
        df.writeStream.format('kafka').outputMode("update").options(**self.kafka_write_configs).start()

    def write_to_console(self, df):
        df.writeStream.format('console').outputMode("update").start()

    def wait(self):
        self.spark.streams.awaitAnyTermination()
        pass

    def start(self):
        df = self.transform(self.read_from_kafka())
        self.write_to_kafka(df)
        self.write_to_console(df)
        self.wait()


class AnomalyPipeline(Pipeline):
    spark_configs = {
        'spark.app.name': 'anomaly-pipeline',
        'spark.master': 'local',
        # PyArrow
        'spark.sql.execution.arrow.pyspark.enabled': 'true',
        # Dynamic Allocation
        'spark.shuffle.service.enabled': 'true',
        'spark.dynamicAllocation.enabled': 'true',
        'spark.dynamicAllocation.initialExecutors': 1,

        # Backpressure
        'spark.streaming.backpressure.enabled': 'true',

    }
    topic = "cpu-usage"

    kafka_read_configs = {
        # read policy
        'failOnDataLoss': 'false',
        'startingOffsets': 'earliest',

        # kafka connection
        'kafka.bootstrap.servers': config.KAFKA_SERVERS,

        # topic
        'subscribe': topic,
        'maxOffsetsPerTrigger': int(os.getenv('KAFKA_MAX_OFFSETS_PER_TRIGGER', 200)),

    }

    kafka_write_configs = {
        'kafka.bootstrap.servers': config.KAFKA_SERVERS,
        'checkpointLocation': config.PATH_CHECKPOINT,
        "topic": f"anomaly"
    }

    def transform(self, df: DataFrame) -> DataFrame:
        condition = when((col("mean") > (config.NORMAL_MEAN + 2 * config.NORMAL_STDDEV)) | (col("mean") < (config.NORMAL_MEAN - 2 * config.NORMAL_STDDEV)), lit(STATUS.ERROR)) \
            .when((col("mean") > (config.NORMAL_MEAN + config.NORMAL_STDDEV)) | (col("mean") < (config.NORMAL_MEAN - config.NORMAL_STDDEV)), lit(STATUS.WARN)) \
            .otherwise(lit(STATUS.SAFE))

        df = df.groupby(window(col("timestamp"), "500 millisecond")).agg(mean(col("cpu")).alias("mean"), stddev(col("cpu")).alias("stddev"), count(col("cpu")))
        df = df.withColumn("status", condition)
        return df

    def write_to_console(self, df):
        df.writeStream.format('console').outputMode("update").foreach(lambda x: print(x["status"], x) if x["status"] != STATUS.SAFE else None).start()
