import asyncio
import io
import logging
import random

from livekit.agents.llm import ChatContext
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.rtc import ChatManager, ChatMessage, Participant, Room

from config import Config
from pathlib import Path

logger = logging.getLogger("chat_handler")


class ChatHandler:
    """Responsible for handling chat interactions with room participants."""

    def __init__(self, agent: VoicePipelineAgent, room: Room, participant: Participant) -> None:
        """Initialize the chat handler."""
        self._participant = participant
        self._agent = agent
        self._room = room
        self._chat_manager = ChatManager(room)

    @property
    def assistant(self) -> VoicePipelineAgent:
        """Get the voice assistant instance."""
        return self._agent

    @property
    def participant(self) -> Participant:
        """Get the participant instance."""
        return self._participant

    @property
    def chat_manager(self) -> ChatManager:
        """Get the chat manager instance."""
        return self._chat_manager

    @property
    def room(self) -> Room:
        """Get the room instance."""
        return self._room

    async def start(self, prompt_filename: str = Config.LLM_PROMPT) -> None:
        """Start the chat handler."""

        # Clear and set the initial chat context for the agent persona
        self.assistant.chat_ctx.messages.clear()
        self.create_agent_persona(self.assistant.chat_ctx, prompt_filename)

        # Register event handlers
        self.chat_manager.on("message_received", self.on_chat_received)

        # Say the initial agent greeting
        logger.info("saying greeting")
        await self.assistant.say(
            source=self.get_greeting(),
            allow_interruptions=True,
            add_to_chat_ctx=True
        )

    def on_chat_received(self, msg: ChatMessage) -> None:
        """Called when a chat message is received."""
        if msg.message:
            logger.info(f"received chat message {msg.message} from {msg.participant.identity}")
            asyncio.create_task(self.respond_to_message(msg.message))

    async def respond_to_message(self, message: str) -> None:
        """Respond to a user message."""
        try:
            # Add the user's message to the chat context
            chat_ctx = self.assistant.chat_ctx.append(role="user", text=message)
            # Send the message to the LLM and get a streaming response
            response = self.assistant.llm.chat(chat_ctx=chat_ctx)
            # Say the response to the user
            logger.info(f"llm response: {response}")
            await self.assistant.say(response)

        except asyncio.TimeoutError:
            logger.error("LLM response timed out")
        except Exception as e:
            logger.error(f"Error during response generation: {e}")

    @staticmethod
    def get_greeting() -> str:
        """Returns a random greeting from a predefined list of greetings."""
        greetings: list[str] = [
            "Hello! How may I help you?",
            "Hey! What can I do for you today?",
            "Hi there, how can I assist you today?",
            "Hi! How can I help you today?"
            "Hi! What would you like help with?",
        ]
        return random.choice(greetings)

    @staticmethod
    def create_agent_persona(ctx: ChatContext, prompt_filename: str) -> ChatContext:
        """Create the chat context for the agent persona."""
        p = Path(__file__).with_name(prompt_filename)
        logger.info(f"loading LLM prompt from {p}")
        with p.open('r') as f:
            ctx.append(
                role="system",
                text=f.read()
            )
        return ctx
