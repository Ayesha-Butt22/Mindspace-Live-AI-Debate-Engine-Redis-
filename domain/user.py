from dataclasses import dataclass


@dataclass
class User:
    """
    Represents a chat participant. This is a pure domain object -
    it just holds data, it doesn't know about Redis, threads, or the database.
    """
    name: str
    peer_name: str
    send_channel: str
    listen_channel: str
