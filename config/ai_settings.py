from dotenv import load_dotenv

# Reads the .env file (if present) and copies its values into the environment,
# so ANTHROPIC_API_KEY / GEMINI_API_KEY are available to the SDKs without
# hardcoding any key anywhere in the source code.
load_dotenv()

# claude-opus-5 is Anthropic's current flagship model. Swap to
# "claude-haiku-4-5" here if you want a much cheaper/faster model while
# you're testing - the rest of the code never needs to change.
ANTHROPIC_MODEL = "claude-opus-5"

# Google's free-tier-eligible Gemini model - used by GeminiResponder.
# The "lite" variant has a much higher free-tier requests-per-minute quota
# than the full "flash" model, so it's less likely to hit rate limits
# during a back-and-forth AI conversation. "-latest" always points at
# Google's current version, so this keeps working after Google retires
# today's specific snapshot.
GEMINI_MODEL = "gemini-flash-lite-latest"

# Safety limit: how many replies EACH agent is allowed to send before the
# conversation auto-stops. Without this, two AI agents would reply to each
# other forever, burning API credits with no one watching.
MAX_TURNS = 6
