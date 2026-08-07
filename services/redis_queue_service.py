from interfaces.publisher_interface import IPublisher
from interfaces.subscriber_interface import ISubscriber


class RedisQueueService(IPublisher, ISubscriber):
    """
    THIS is the only file that knows Redis exists.
    If tomorrow you switch to ActiveMQ, RabbitMQ, or Kafka, you write a new
    class (e.g. ActiveMQQueueService) that implements IPublisher/ISubscriber
    the same way - nothing else in the project changes.
    """

    def __init__(self, redis_connection):
        self._redis = redis_connection

    def publish(self, channel: str, message: str) -> None:
        self._redis.publish(channel, message)

    def subscribe(self, channel: str, on_message) -> None:
        pubsub = self._redis.pubsub()
        pubsub.subscribe(channel)

        for event in pubsub.listen():
            if event['type'] == 'message':
                text = event['data'].decode('utf-8')
                on_message(channel, text)
