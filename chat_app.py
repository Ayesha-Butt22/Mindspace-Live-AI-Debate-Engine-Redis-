import sys
from config.redis_client import get_redis_connection
from config.users import USERS
from db.connection import create_table
from services.redis_queue_service import RedisQueueService
from services.chat_service import ChatService
from listeners.message_listener import MessageListener


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in USERS:
        valid = " | ".join(USERS.keys())
        print(f"Usage: python chat_app.py <{valid}>")
        return

    user = USERS[sys.argv[1]]
    create_table()

    # ---- This block is the ONLY place that wires Redis into the app ----
    redis_connection = get_redis_connection()
    queue_service = RedisQueueService(redis_connection)
    # To switch technology later: queue_service = ActiveMQQueueService(...)
    # Nothing below this line needs to change.
    # ----------------------------------------------------------------------

    chat_service = ChatService(user=user, publisher=queue_service)
    listener = MessageListener(
        subscriber=queue_service,
        channel=user.listen_channel,
        on_message=chat_service.handle_incoming
    )
    chat_service.attach_listener(listener)
    chat_service.start_listening()

    print(f"=== {user.name} Chat Started ===")
    print("Type a message and press Enter to send. Type 'exit' to quit.\n")

    while True:
        msg = input(f"{user.name}> ")
        if msg.lower() == "exit":
            print("Closing chat...")
            break
        chat_service.send(msg)


if __name__ == "__main__":
    main()
