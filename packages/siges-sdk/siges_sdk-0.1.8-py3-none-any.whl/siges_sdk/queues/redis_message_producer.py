from siges_sdk.queues.message_producer import QueueMessageProducer
import redis
from typing import Any
import uuid

class RedisMessageProducer(QueueMessageProducer):
    redis_host = 'redis'
    redis_port = 6379
    redis_db = 0

    def __init__(self):
        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)

    def send_message(self, queue_name: str, message: dict[str, Any]) -> None:
        message_id = str(uuid.uuid4())
        message['id'] = message_id
        self.redis_client.xadd(queue_name, message)