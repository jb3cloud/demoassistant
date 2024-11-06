import logging
from datetime import datetime

from livekit.agents.llm import ChatContext, ChatImage
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.rtc import Participant, Room

from config import Config
from pathlib import Path

logger = logging.getLogger("chat_handler")


class ChatHandler:
    """Responsible for handling chat interactions with room participants."""

    def __init__(self, room: Room, participant: Participant, agent: VoicePipelineAgent) -> None:
        """Initialize the chat handler."""
        self._participant = participant
        self._agent = agent
        self._room = room

    @property
    def assistant(self) -> VoicePipelineAgent:
        """Get the voice assistant instance."""
        return self._agent

    @property
    def participant(self) -> Participant:
        """Get the participant instance."""
        return self._participant

    @property
    def room(self) -> Room:
        """Get the room instance."""
        return self._room

    def start(self, prompt_filename: str = Config.LLM_PROMPT) -> None:
        """Start the chat handler."""
        logger.info("starting chat handler")

        # Clear and set the initial chat context for the agent persona
        self.assistant.chat_ctx.messages.clear()
        self.create_agent_persona(self.assistant.chat_ctx, prompt_filename)

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
        # Provide the current date and time
        ctx.append(
            role="system",
            text=f"The current date and time is {datetime.now().strftime('%A, %B %d, %Y %I:%M %p')}"
        )
        return ctx
