import anthropic

from config.ai_settings import ANTHROPIC_MODEL
from domain.message import Message
from interfaces.responder_interface import IResponder


class ClaudeResponder(IResponder):
    """
    THIS is the only file that knows Claude/Anthropic exists.
    If tomorrow you switch to a different AI provider, you write a new class
    that implements IResponder the same way - nothing else in the project
    changes (Dependency Inversion, same pattern as RedisQueueService).
    """

    def __init__(self, my_name: str):
        # anthropic.Anthropic() automatically reads the ANTHROPIC_API_KEY
        # environment variable - we never touch the key directly.
        self._client = anthropic.Anthropic()
        self._my_name = my_name

    def respond(self, system_prompt: str, history: list[Message]) -> str:
        # Claude's API needs each past message tagged as "assistant" (me) or
        # "user" (the other agent) - it doesn't know about names.
        messages = [
            {
                "role": "assistant" if message.sender == self._my_name else "user",
                "content": message.content,
            }
            for message in history
        ]

        response = self._client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=300,
            system=system_prompt,
            messages=messages,
        )

        return next(block.text for block in response.content if block.type == "text")
