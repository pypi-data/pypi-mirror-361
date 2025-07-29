from abc import ABC, abstractmethod
from typing import Any

class QueueMessageProducer(ABC):
    @abstractmethod
    def send_message(self, queue_name: str, message: dict[str, Any]) -> None:
        pass