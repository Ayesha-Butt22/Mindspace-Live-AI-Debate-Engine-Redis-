import queue

from config.agents import AGENTS
from config.redis_client import get_redis_connection
from db.connection import create_table
from listeners.message_listener import MessageListener
from services.ai_chat_service import AIChatService
from services.gemini_responder import GeminiResponder
from services.redis_queue_service import RedisQueueService


class ConversationManager:
    """
    Wires up the same building blocks ai_chat.py uses (RedisQueueService,
    GeminiResponder, AIChatService) - one instance per persona in
    config/agents.py - and adds a thin relay on top so the web frontend can
    watch the conversation live. It does not change how the chat itself
    works; it only observes the same Redis Pub/Sub channels the AI agents
    already publish to.
    """

    def __init__(self, broadcast_queue: "queue.Queue"):
        self._broadcast_queue = broadcast_queue
        create_table()

        redis_connection = get_redis_connection()
        self._queue_service = RedisQueueService(redis_connection)

        self._chat_services: dict[str, AIChatService] = {
            key: AIChatService(
                agent=agent,
                publisher=self._queue_service,
                responder=GeminiResponder(my_name=agent.name),
            )
            for key, agent in AGENTS.items()
        }
        self._listeners_started = False

    def start_listeners(self) -> None:
        """Subscribe every agent to its channel exactly once, for the
        lifetime of the web server."""
        if self._listeners_started:
            return

        for key, agent in AGENTS.items():
            chat_service = self._chat_services[key]
            handler = self._relaying_handler(chat_service, speaker_name=agent.peer_name)
            listener = MessageListener(
                subscriber=self._queue_service,
                channel=agent.listen_channel,
                on_message=handler,
            )
            chat_service.attach_listener(listener)
            chat_service.start_listening()

        self._listeners_started = True

    def start_conversation(self, topic: str) -> None:
        """Reset both agents and have the philosopher kick things off."""
        for chat_service in self._chat_services.values():
            chat_service.reset()
        self._chat_services["philosopher"].start_conversation(topic)

    def _relaying_handler(self, chat_service: AIChatService, speaker_name: str):
        """Wraps a chat service's normal handle_incoming so every message
        is also pushed onto the broadcast queue for the WebSocket clients,
        tagged with who actually said it."""

        def handler(channel: str, text: str) -> None:
            self._broadcast_queue.put({"sender": speaker_name, "text": text})
            chat_service.handle_incoming(channel, text)

        return handler
