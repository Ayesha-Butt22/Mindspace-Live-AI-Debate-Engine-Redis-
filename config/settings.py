REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

DATABASE_NAME = "chat.db"

CHANNEL_A_TO_B = "channel_a_to_b"
CHANNEL_B_TO_A = "channel_b_to_a"

# Separate channels for the AI-to-AI conversation, so it never mixes
# with messages from the human chat_app.py.
CHANNEL_AI_A_TO_B = "channel_ai_a_to_b"
CHANNEL_AI_B_TO_A = "channel_ai_b_to_a"
