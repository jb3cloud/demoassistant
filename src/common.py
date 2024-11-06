from dataclasses import dataclass
from typing import Optional

from livekit.rtc import VideoFrame


@dataclass
class Common:
    frame: Optional[VideoFrame] = None
