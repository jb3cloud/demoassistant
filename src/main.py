import logging

from livekit.agents import AutoSubscribe, JobContext, JobProcess, WorkerOptions, cli
from livekit.agents.pipeline import VoicePipelineAgent

from chat_handler import ChatHandler
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


async def entrypoint(job_ctx: JobContext) -> None:
    """
    The entrypoint for the voice assistant job assigned to us.
    """
    # Connect to the LiveKit room and wait for a participant to join
    logger.info(f"connecting to room {job_ctx.room.name}")
    await job_ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    logger.info("waiting for participant")
    participant = await job_ctx.wait_for_participant()

    # Create the LiveKit voice assistant
    room = job_ctx.room
    services: VoiceServices = job_ctx.proc.userdata["services"]
    tools = AgentTools(services)
    agent = VoicePipelineAgent(
        vad = services.vad,
        stt = services.stt,
        llm = services.llm,
        tts = services.tts,
        fnc_ctx=tools,
        preemptive_synthesis = True
    )

    # Start the voice assistant
    logger.info(f"starting room {room.name} assistant for {participant.identity}")
    agent.start(room, participant)

    # Start the chat handler
    logger.info("starting chat handler")
    handler = ChatHandler(agent, room, participant)
    await handler.start()


"""Main program"""
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.info("use https://agents-playground.livekit.io/ to test the agent")
    cli.run_app(opts=WorkerOptions(
        prewarm_fnc=initialize,
        entrypoint_fnc=entrypoint
    ))
