from siges_sdk.queues.message_producer import QueueMessageProducer
from siges_sdk.queues.message_producer_provider import get_message_producer
from siges_sdk.queues.message_consumer import QueueMessageConsumer
from siges_sdk.queues.message_consumer_provider import get_message_consumer

try:
    __all__ = [
        "QueueMessageProducer", 
        "get_message_producer",
        "QueueMessageConsumer",
        "get_message_consumer"
    ]
except ImportError:
    __all__ = [
        "QueueMessageProducer", 
        "get_message_producer",
        "QueueMessageConsumer",
        "get_message_consumer"
    ] 