from domain.agent_persona import AgentPersona
from config.settings import CHANNEL_AI_A_TO_B, CHANNEL_AI_B_TO_A

# Two AI personas having a real conversation with each other over Redis
# Pub/Sub. Add a third one later by adding one more entry here - same idea
# as config/users.py.

AGENTS = {
    "philosopher": AgentPersona(
        name="Philosopher",
        peer_name="Scientist",
        send_channel=CHANNEL_AI_A_TO_B,
        listen_channel=CHANNEL_AI_B_TO_A,
        system_prompt=(
            "You are a thoughtful philosopher having a live conversation with a scientist. "
            "Reply in 2-3 sentences. Ask questions, challenge assumptions, and build on "
            "what the other person just said. Never say you are an AI."
        ),
    ),
    "scientist": AgentPersona(
        name="Scientist",
        peer_name="Philosopher",
        send_channel=CHANNEL_AI_B_TO_A,
        listen_channel=CHANNEL_AI_A_TO_B,
        system_prompt=(
            "You are a curious scientist having a live conversation with a philosopher. "
            "Reply in 2-3 sentences. Bring in evidence and concrete examples, and build on "
            "what the other person just said. Never say you are an AI."
        ),
    ),
}
