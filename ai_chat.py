import sys
import time

from config.agents import AGENTS
from config.redis_client import get_redis_connection
from db.connection import create_table
from listeners.message_listener import MessageListener
from services.ai_chat_service import AIChatService
from services.gemini_responder import GeminiResponder
from services.redis_queue_service import RedisQueueService


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in AGENTS:
        valid = " | ".join(AGENTS.keys())
        print(f"Usage: python ai_chat.py <{valid}> [\"opening line\" - only the agent that starts needs this]")
        return

    agent = AGENTS[sys.argv[1]]
    create_table()

    # ---- Same wiring pattern as chat_app.py: only this block knows Redis ----
    redis_connection = get_redis_connection()
    queue_service = RedisQueueService(redis_connection)
    responder = GeminiResponder(my_name=agent.name)
    # ---------------------------------------------------------------------

    chat_service = AIChatService(agent=agent, publisher=queue_service, responder=responder)
    listener = MessageListener(
        subscriber=queue_service,
        channel=agent.listen_channel,
        on_message=chat_service.handle_incoming,
    )
    chat_service.attach_listener(listener)
    chat_service.start_listening()

    print(f"=== {agent.name} is online, listening for {agent.peer_name} ===")

    opening_line = " ".join(sys.argv[2:])
    if opening_line:
        chat_service.start_conversation(opening_line)

    print("Press Ctrl+C to stop.\n")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
