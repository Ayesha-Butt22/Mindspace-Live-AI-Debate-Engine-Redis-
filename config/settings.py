import os

# REDIS_URL lets a cloud Redis provider (e.g. Upstash, Redis Cloud) be used
# in production just by setting one environment variable - e.g.
# "rediss://default:password@host:port". Local development is unaffected:
# leave REDIS_URL unset and it falls back to plain localhost.
REDIS_URL = os.environ.get("REDIS_URL")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))

DATABASE_NAME = "chat.db"

CHANNEL_A_TO_B = "channel_a_to_b"
CHANNEL_B_TO_A = "channel_b_to_a"

# Separate channels for the AI-to-AI conversation, so it never mixes
# with messages from the human chat_app.py.
CHANNEL_AI_A_TO_B = "channel_ai_a_to_b"
CHANNEL_AI_B_TO_A = "channel_ai_b_to_a"
