from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """Represents a single chat message. Pure data, no behavior."""
    sender: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
