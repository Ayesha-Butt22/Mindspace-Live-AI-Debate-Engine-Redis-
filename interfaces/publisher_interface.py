from abc import ABC, abstractmethod


class IPublisher(ABC):
    """
    Any queue technology that can SEND messages must implement this.
    Kept separate from ISubscriber on purpose (Interface Segregation Principle):
    a component that only sends messages should not be forced to implement
    listening logic it never uses, and vice versa.
    """

    @abstractmethod
    def publish(self, channel: str, message: str) -> None:
        ...
