BASH_SOURCE=$0
ROOT_OF_PROJECT=$(dirname ${BASH_SOURCE})
PATH_OF_DATA="$ROOT_OF_PROJECT/storage/data/cpu_usage.data"
KAFKA_HOME="$ROOT_OF_PROJECT/kafka/bin"
$KAFKA_HOME/kafka-topics.sh -topic test -create --bootstrap-server localhost:9093
echo "sending data ..."
tail -n +2 $PATH_OF_DATA | $KAFKA_HOME/kafka-console-producer.sh --topic test  --bootstrap-server localhost:9093
echo "finished"
