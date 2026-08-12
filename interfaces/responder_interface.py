from abc import ABC, abstractmethod

from domain.message import Message


class IResponder(ABC):
    """
    Anything that can turn a conversation-so-far into the next reply must
    implement this. Kept separate from IPublisher/ISubscriber (Interface
    Segregation Principle): generating text has nothing to do with sending
    or receiving it over Redis.
    """

    @abstractmethod
    def respond(self, system_prompt: str, history: list[Message]) -> str:
        ...
