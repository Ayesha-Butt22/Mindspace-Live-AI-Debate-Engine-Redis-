from domain.agent_persona import AgentPersona
from domain.message import Message
from interfaces.publisher_interface import IPublisher
from interfaces.responder_interface import IResponder
from listeners.message_listener import MessageListener
from controllers import message_controller
from config.ai_settings import MAX_TURNS


class AIChatService:
    """
    Same role as ChatService, but the "typing" is done by an IResponder
    (Claude) instead of a human. Depends only on IPublisher and IResponder -
    interfaces, not concrete classes - so the Redis transport and the AI
    provider can each be swapped without touching this class.
    """

    def __init__(self, agent: AgentPersona, publisher: IPublisher, responder: IResponder):
        self._agent = agent
        self._publisher = publisher
        self._responder = responder
        self._listener: MessageListener | None = None
        self._history: list[Message] = []
        self._turns_sent = 0

    def attach_listener(self, listener: MessageListener) -> None:
        self._listener = listener

    def start_listening(self) -> None:
        if self._listener is None:
            raise RuntimeError("No listener attached. Call attach_listener() first.")
        self._listener.start()

    def start_conversation(self, opening_line: str) -> None:
        """Call this only on the one agent that should speak first."""
        self._send(opening_line)

    def handle_incoming(self, channel: str, text: str) -> None:
        """Called automatically whenever the peer agent's message arrives."""
        print(f"\n[{self._agent.peer_name}]: {text}")
        self._history.append(Message(sender=self._agent.peer_name, content=text))
        message_controller.create_message(self._agent.peer_name, text)

        if self._turns_sent >= MAX_TURNS:
            print(f"\n=== {self._agent.name} reached the {MAX_TURNS}-turn limit. Staying quiet. ===")
            return

        # The AI call crosses a network boundary (rate limits, timeouts,
        # temporary outages) - catch failures here so one bad response
        # doesn't kill the whole listener thread and end the conversation.
        try:
            reply = self._responder.respond(self._agent.system_prompt, self._history)
        except Exception as error:
            print(f"\n=== {self._agent.name} could not generate a reply: {error} ===")
            return

        self._send(reply)

    def _send(self, text: str) -> None:
        print(f"\n[{self._agent.name}]: {text}")
        self._history.append(Message(sender=self._agent.name, content=text))
        self._publisher.publish(self._agent.send_channel, text)
        message_controller.create_message(self._agent.name, text)
        self._turns_sent += 1
