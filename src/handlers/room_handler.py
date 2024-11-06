import asyncio
import logging
import random
from pathlib import Path
from typing import Optional

from livekit.agents.pipeline import VoicePipelineAgent
from livekit.rtc import RemoteParticipant, RemoteTrackPublication, Room, Track, TrackKind, VideoBufferType, VideoFrame, \
    VideoStream

from handlers.chat_handler import ChatHandler


class RoomHandler:
    """Responsible for handling room interactions with participants."""

    def __init__(self, room: Room, participant: RemoteParticipant, agent: VoicePipelineAgent) -> None:
        """Initialize the room handler."""
        self._room = room
        self._participant = participant
        self._agent = agent
        self._chat_handler = ChatHandler(room, participant, agent)
        self._frame: Optional[VideoFrame] = None
        self.logger = logging.getLogger(f"room_handler_{room.name}")

    @property
    def agent(self) -> VoicePipelineAgent:
        """The LiveKit voice assistant."""
        return self._agent

    @property
    def chat_handler(self) -> ChatHandler:
        """The chat handler."""
        return self._chat_handler

    @property
    def participant(self) -> RemoteParticipant:
        """The LiveKit participant."""
        return self._participant

    @property
    def room(self) -> Room:
        """The LiveKit room."""
        return self._room

    @property
    def frame(self) -> Optional[VideoFrame]:
        """The most recent video frame."""
        return self._frame

    def start(self) -> None:
        """Start the room handler."""
        self.logger.info("starting room handler")
        self.room.on("track_subscribed", self.on_track_subscribed)

    def on_track_subscribed(self,
                            track: Track,
                            publication: RemoteTrackPublication,
                            participant: RemoteParticipant) -> None:
        """Handle a track being published to the room."""
        if track.kind == TrackKind.KIND_AUDIO:
            asyncio.create_task(self.on_audio_track_subscribed(participant))
        elif track.kind == TrackKind.KIND_VIDEO:
            asyncio.create_task(self.on_video_track_subscribed(track, publication, participant))

    async def on_audio_track_subscribed(self, participant: RemoteParticipant) -> None:
        """Handle an audio track being published to the room."""
        self.logger.info(f"audio track subscribed from {participant.identity}")
        self.chat_handler.start()
        self.agent.start(self.room, self.participant)
        await self.agent.say(
            source=self.get_greeting(),
            allow_interruptions=True,
            add_to_chat_ctx=False
        )

    async def on_video_track_subscribed(self,
                                        track: Track,
                                        publication: RemoteTrackPublication,
                                        participant: RemoteParticipant) -> None:
        """Handle a video track being published to the room."""
        width = publication.width
        height = publication.height
        self.logger.info(f"video track subscribed from {participant.identity} ({width}x{height})")
        video_stream = VideoStream(track, format=VideoBufferType.RGBA)
        async for frame in video_stream:
            self._frame = frame.frame

    def get_greeting(self) -> str:
        """Returns a random greeting from a predefined list."""

        p = Path(__file__).with_name("greetings.txt")
        self.logger.info(f"loading greetings from {p}")
        with p.open('r') as f:
            greetings = f.readlines()

        return random.choice(greetings)
