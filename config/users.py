from domain.user import User
from config.settings import CHANNEL_A_TO_B, CHANNEL_B_TO_A

# Real, meaningful users instead of duplicate "user_a.py" / "user_b.py" scripts.
# Add a third person to the chat later by adding one more entry here -
# no new file, no new script needed.

USERS = {
    "ahmed": User(name="Ahmed", peer_name="Sara", send_channel=CHANNEL_A_TO_B, listen_channel=CHANNEL_B_TO_A),
    "sara": User(name="Sara", peer_name="Ahmed", send_channel=CHANNEL_B_TO_A, listen_channel=CHANNEL_A_TO_B),
}
