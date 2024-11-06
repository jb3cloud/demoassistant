import logging
from typing import Optional

from livekit.agents import AutoSubscribe, JobContext, JobProcess, WorkerOptions, cli
from livekit.agents.llm import ChatContext, ChatImage, ChatMessage
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.rtc import VideoFrame

from handlers.room_handler import RoomHandler
from services.agent_tools import AgentTools
from services.voice_services import VoiceServices

logger = logging.getLogger("main")


def initialize(proc: JobProcess) -> None:
    """
    Initializes the voice assistant shared services for the process
    including the Voice Activity Detection (VAD) and Azure services.
    """
    logger.info("initializing shared services")
    proc.userdata["services"] = VoiceServices.with_azure()
    proc.userdata["tools"] = AgentTools()


async def update_chat_context(chat_ctx: ChatContext, frame: Optional[VideoFrame]) -> None:
    """Updates the chat context"""

    # Limit the number of messages in the context to 15
    if len(chat_ctx.messages) > 15:
        chat_ctx.messages = chat_ctx.messages[-15:]

    # Add the most recent camera image to the chat context
    if frame:
        logging.debug("Adding camera image to chat context")
        chat_ctx.messages.insert(-1,
                                 ChatMessage.create(
                                     role="user",
                                     text="Camera image",
                                     images=[ChatImage(frame)]
                                 )
                                 )

    # Log the chat context
    for message in chat_ctx.messages:
        logger.debug(f"chat_ctx: {message}")


async def entrypoint(job_ctx: JobContext) -> None:
    """
    The entrypoint for the voice assistant job assigned to us.
    """
    room = job_ctx.room

    # Create the LiveKit voice assistant
    services: VoiceServices = job_ctx.proc.userdata["services"]
    tools: AgentTools = job_ctx.proc.userdata["tools"]
    agent = VoicePipelineAgent(
        vad=services.vad,
        stt=services.stt,
        llm=services.llm,
        tts=services.tts,
        fnc_ctx=tools,
        preemptive_synthesis=True,
        before_llm_cb=lambda _, chat_ctx:
        update_chat_context(chat_ctx, room_handler.frame)
    )

    # Connect to the LiveKit room
    logger.info(f"connecting to room {job_ctx.room.name}")
    await job_ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)

    # Wait for the participant to join
    logger.info("waiting for participant")
    participant = await job_ctx.wait_for_participant()

    # Start the room handler
    room_handler = RoomHandler(room, participant, agent)
    room_handler.start()


"""Main program"""
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.info("use https://agents-playground.livekit.io/ to test the agent")
    cli.run_app(opts=WorkerOptions(
        prewarm_fnc=initialize,
        entrypoint_fnc=entrypoint
    ))
