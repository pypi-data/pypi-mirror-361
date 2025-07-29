from abc import ABC, abstractmethod
from typing import Callable, Any

class QueueMessageConsumer(ABC):
    def __init__(self, queue_name: str, callback: Callable[[dict], Any]):
        self.queue_name = queue_name
        self.callback = callback

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass