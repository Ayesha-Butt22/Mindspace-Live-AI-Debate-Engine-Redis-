import os

from google import genai
from google.genai import types

from config.ai_settings import GEMINI_MODEL
from domain.message import Message
from interfaces.responder_interface import IResponder


class GeminiResponder(IResponder):
    """
    THIS is the only file that knows Google Gemini exists - same role as
    ClaudeResponder, just a different AI provider behind the same IResponder
    contract. AIChatService does not know or care which of the two is
    plugged in (Dependency Inversion + Liskov Substitution in action).
    """

    def __init__(self, my_name: str):
        # genai.Client() automatically reads the GEMINI_API_KEY environment
        # variable - we never touch the key directly.
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._my_name = my_name

    def respond(self, system_prompt: str, history: list[Message]) -> str:
        # Gemini's API needs each past message tagged as "model" (me) or
        # "user" (the other agent) - it doesn't know about names.
        contents = [
            types.Content(
                role="model" if message.sender == self._my_name else "user",
                parts=[types.Part(text=message.content)],
            )
            for message in history
        ]

        response = self._client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
        )

        return response.text
