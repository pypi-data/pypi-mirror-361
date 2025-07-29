from siges_sdk.queues.redis_message_consumer import RedisQueueMessageConsumer
from siges_sdk.queues.message_consumer import QueueMessageConsumer
from typing import Callable, Any, Optional

def get_message_consumer(queue_name: str, consumer_group: str, callback: Callable[[dict], Any], max_stream_length: Optional[int] = None) -> QueueMessageConsumer:
    return RedisQueueMessageConsumer(queue_name, callback, consumer_group, max_stream_length)