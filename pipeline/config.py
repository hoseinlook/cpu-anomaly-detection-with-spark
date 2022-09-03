import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 pyspark-shell'

PATH_ROOT = Path(__file__).parent.parent
PATH_STORAGE = PATH_ROOT.joinpath('storage')
PATH_CHECKPOINT = PATH_STORAGE.joinpath('checkpoint')
PATH_OUTPUT = PATH_STORAGE.joinpath('output')

PATH_CHECKPOINT.mkdir(parents=True, exist_ok=True)
PATH_OUTPUT.mkdir(parents=True, exist_ok=True)

# kafka
KAFKA_SERVERS = os.getenv('KAFKA_SERVERS', '127.0.0.1:9093')

# Metrics
NORMAL_MEAN = float(os.getenv('NORMAL_MEAN', 14.5))
NORMAL_STDDEV = float(os.getenv('NORMAL_STDDEV', 2.7))
