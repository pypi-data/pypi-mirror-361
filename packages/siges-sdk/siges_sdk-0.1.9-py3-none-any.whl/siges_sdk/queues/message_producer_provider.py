from siges_sdk.queues.redis_message_producer import RedisMessageProducer
from siges_sdk.queues.message_producer import QueueMessageProducer

def get_message_producer() -> QueueMessageProducer:
    return RedisMessageProducer()