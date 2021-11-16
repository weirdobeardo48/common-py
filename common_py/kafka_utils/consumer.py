from kafka import KafkaConsumer
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from kafka.coordinator.assignors.range import RangePartitionAssignor
from kafka.consumer.subscription_state import ConsumerRebalanceListener
import logging
from json import loads
import time
import redis

LOG = logging.getLogger(__name__)


class Consumer():
    def __new__(cls, **kwargs) -> KafkaConsumer:
        KAFKA_BOOTSTRAP_SERVERS = kwargs.get('bootstrap_servers', None)
        KAFKA_CONSUMER_SUBSCRIBE_TOPIC = kwargs.get('topics', None)
        CLIENT_ID = kwargs.get('client_id', None)
        GROUP_ID = kwargs.get('group_id', None)
        AUTO_COMMIT = kwargs.get('auto_commit', False)
        __redis: redis.Redis = kwargs.get('redis', None)
        consumer = KafkaConsumer(
            KAFKA_CONSUMER_SUBSCRIBE_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: loads(x.decode('utf-8')),
            group_id=GROUP_ID,
            client_id=CLIENT_ID,
            session_timeout_ms=10000,
            heartbeat_interval_ms=5000,
            max_poll_interval_ms=30000,
            partition_assignment_strategy=[
                RoundRobinPartitionAssignor, RangePartitionAssignor],
            enable_auto_commit=AUTO_COMMIT,
        )
        CustomRebalanceHandler: ConsumerRebalanceListener = kwargs.get(
            'rebalance_listener', None)

        class RedisSeekOffsetHandler(ConsumerRebalanceListener):
            __redis: redis.Redis = None

            def __init__(self, **k):
                self.__redis = k.get('redis', None)

            def on_partitions_assigned(self, assigned):
                LOG.warning("Seeking redis to its offset")
                if self.__redis:
                    for partition in assigned:
                        key = f'{KAFKA_CONSUMER_SUBSCRIBE_TOPIC}_{partition.partition}_offset'
                        value = self.__redis.get(key)
                        LOG.info(f'Redis: Return value of key {key} is {value}')
                        if value:
                            LOG.warning(
                                f'Seeking offset of topic {partition.topic} partition {partition.partition} to offset {value}')
                            consumer.seek(partition, int(value.decode()) + 1)
                        pass

            def on_partitions_revoked(self, revoked):
                return super().on_partitions_revoked(revoked)

        class RebalanceHandler(ConsumerRebalanceListener):
            def __init__(self, **k):
                self.__redis = k.get('redis', None)

            def on_partitions_revoked(self, revoked):
                for part in revoked:
                    LOG.warning(f'{part} is being revoked')
                RedisSeekOffsetHandler(redis=self.__redis).on_partitions_revoked(revoked)
                if CustomRebalanceHandler:
                    CustomRebalanceHandler().on_partitions_revoked(revoked)

            def on_partitions_assigned(self, assigned):
                for part in assigned:
                    LOG.warning(f'{part} is being assigned')
                RedisSeekOffsetHandler(redis=self.__redis).on_partitions_assigned(assigned)
                if CustomRebalanceHandler:
                    CustomRebalanceHandler().on_partitions_assigned(assigned)

        consumer.subscribe(
            topics=KAFKA_CONSUMER_SUBSCRIBE_TOPIC, listener=RebalanceHandler(redis=__redis))

        while len(consumer.assignment()) == 0:
            LOG.info(
                f'Polling topic {KAFKA_CONSUMER_SUBSCRIBE_TOPIC} at {KAFKA_BOOTSTRAP_SERVERS}')
            consumer.poll()
            time.sleep(2)

        return consumer

    def __init__(self, **kwargs) -> None:
        pass
