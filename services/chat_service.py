from domain.user import User
from interfaces.publisher_interface import IPublisher
from listeners.message_listener import MessageListener
from controllers import message_controller


class ChatService:
    """
    The single source of chat behavior - used no matter which user is chatting.
    This is what used to be duplicated inside user_a.py and user_b.py.

    Depends only on IPublisher (an interface), not on RedisQueueService directly.
    This is Dependency Inversion: swap Redis for anything else and this class
    never needs to change.
    """

    def __init__(self, user: User, publisher: IPublisher):
        self._user = user
        self._publisher = publisher
        self._listener: MessageListener | None = None

    def attach_listener(self, listener: MessageListener) -> None:
        self._listener = listener

    def start_listening(self):
        if self._listener is None:
            raise RuntimeError("No listener attached. Call attach_listener() first.")
        self._listener.start()

    def send(self, text: str) -> None:
        if not text.strip():
            return
        self._publisher.publish(self._user.send_channel, text)
        message_controller.create_message(self._user.name, text)

    def handle_incoming(self, channel: str, text: str) -> None:
        print(f"\n[{self._user.peer_name} says]: {text}")
        message_controller.create_message(self._user.peer_name, text)
        print(f"{self._user.name}> ", end="", flush=True)
