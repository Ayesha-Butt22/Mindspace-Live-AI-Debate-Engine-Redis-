from dataclasses import dataclass


@dataclass
class AgentPersona:
    """
    Represents an AI chat participant. Same shape as domain.user.User
    (name, peer, channels) plus a system_prompt that tells Claude who to
    be. Pure data - no Redis, no API calls, no threads.
    """
    name: str
    peer_name: str
    send_channel: str
    listen_channel: str
    system_prompt: str
