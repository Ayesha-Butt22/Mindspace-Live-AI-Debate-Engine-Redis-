from abc import ABC, abstractmethod
from typing import Callable


class ISubscriber(ABC):
    """
    Any queue technology that can RECEIVE messages must implement this.
    `on_message` is a callback: whenever a message arrives, this interface's
    implementation must call on_message(channel, message_text).
    """

    @abstractmethod
    def subscribe(self, channel: str, on_message: Callable[[str, str], None]) -> None:
        ...
