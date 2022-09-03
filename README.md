# Introduction

we want to find out anomaly which will occur if  mean of cpu-usage in a window of time be 
greater than a number that is specified in .env file .
if this difference be more than standard deviation we will count it as a WARN
and if this difference be more than double of standard deviation we will count it as an ERROR .

we read data from a kafka topic, and then
we calculate mean and stddev of every window with spark then 
write spark streaming results to the console and in another kafka topic.

windows are slots of time every 500 millisecond's . 
and our spark's output mode  is "update mode" 


# Install

```bash

sudo apt update -y
sudo apt install -y git python3 python3-pip python3-venv

git clone https://github.com/hoseinlook/cpu-anomaly-detection-with-spark.git

cp -n .env.example .env
nano .env

python3.8 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt

```

# Run

to run this project
at first provide infrastructure like kafka and zookeeper with docker

##### start kafka:

```bash
docker-compose up
```

+ kafka bootstrap host: [ localhost:9093 ]( localhost:9093 )
+ zookeeper server: [ localhost:2181 ]( localhost:2181 )

##### start pipeline:

now start pyspark pipeline

```bash
source venv/bin/activate
python -m pipeline
```

+ spark webUI: [ localhost:4040 ]( localhost:4040 )

##### produce example data to kafka:
```bash
bash send-data-to-kafka.sh
```

####  Note:

you can watch checkpoint's and data of kafka and data of zookeeper in storage directory

