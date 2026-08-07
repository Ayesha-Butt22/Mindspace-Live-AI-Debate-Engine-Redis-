import threading
from interfaces.subscriber_interface import ISubscriber


class MessageListener:
    """
    Responsible ONLY for running a subscriber's blocking listen loop
    on a background thread, so the main program can keep accepting
    user input at the same time.

    This class doesn't know or care whether the subscriber is Redis,
    ActiveMQ, or anything else - it only depends on ISubscriber.
    """

    def __init__(self, subscriber: ISubscriber, channel: str, on_message):
        self._subscriber = subscriber
        self._channel = channel
        self._on_message = on_message
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        self._subscriber.subscribe(self._channel, self._on_message)
