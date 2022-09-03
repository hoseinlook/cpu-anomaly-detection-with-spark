## Run kafka commands in docker
KAFKA_COMPOSE_SERVICE=kafka_producer
BASH_SOURCE=$0
ROOT_OF_PROJECT=$(dirname ${BASH_SOURCE})
PATH_OF_DATA="$ROOT_OF_PROJECT/storage/data/cpu_usage.data"
KAFKA_HOME="/opt/bitnami/kafka/bin"
KAFKA_TOPIC=cpu-usage

docker-compose  run $KAFKA_COMPOSE_SERVICE $KAFKA_HOME/kafka-topics.sh -topic ${KAFKA_TOPIC} -create --bootstrap-server kafka-broker:9092
echo "sending data ..."
tail -n +2 $PATH_OF_DATA | docker-compose  run $KAFKA_COMPOSE_SERVICE $KAFKA_HOME/kafka-console-producer.sh --topic $KAFKA_TOPIC --bootstrap-server kafka-broker:9092
echo "finished"

## Run kafka commands without docker in local
##

#BASH_SOURCE=$0
#ROOT_OF_PROJECT=$(dirname ${BASH_SOURCE})
#PATH_OF_DATA="$ROOT_OF_PROJECT/storage/data/cpu_usage.data"
#KAFKA_HOME="$ROOT_OF_PROJECT/kafka/bin"
#KAFKA_TOPIC=cpu-usage
#
#$KAFKA_HOME/kafka-topics.sh -topic ${KAFKA_TOPIC} -create --bootstrap-server localhost:9093
#echo "sending data ..."
#tail -n +2 $PATH_OF_DATA | $KAFKA_HOME/kafka-console-producer.sh --topic $KAFKA_TOPIC --bootstrap-server localhost:9093
#echo "finished"
