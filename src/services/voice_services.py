from livekit.agents.llm import LLM
from livekit.agents.stt import STT
from livekit.agents.tts import TTS
from livekit.plugins import azure, deepgram, openai, silero

from config import Config


class VoiceServices:
    """Voice assistant services including LLM, STT, TTS, and VAD."""

    def __init__(self, llm: LLM, stt: STT, tts: TTS, vad: silero.VAD) -> None:
        """Initialize the voice assistant services."""
        self._llm: LLM = llm
        self._stt: STT = stt
        self._tts: TTS = tts
        self._vad: silero.VAD = vad
        pass

    @property
    def vad(self) -> silero.VAD:
        """Get the VAD instance."""
        return self._vad

    @property
    def llm(self) -> LLM:
        """Get the LLM instance."""
        return self._llm

    @property
    def stt(self) -> STT:
        """Get the STT instance."""
        return self._stt

    @property
    def tts(self) -> TTS:
        """Get the TTS instance."""
        return self._tts

    @staticmethod
    def with_azure() -> "VoiceServices":
        """Initialize Azure services for LLM, STT, and TTS from configuration."""

        assert Config.AZURE_OPENAI_API_KEY is not None, "AZURE_OPENAI_API_KEY is not set"
        assert Config.AZURE_OPENAI_ENDPOINT is not None, "AZURE_OPENAI_ENDPOINT is not set"
        assert Config.LLM_MODEL is not None, "LLM_MODEL is not set"
        assert Config.LLM_TEMPERATURE is not None, "LLM_TEMPERATURE is not set"
        assert Config.AZURE_SPEECH_KEY is not None, "AZURE_SPEECH_KEY is not set"
        assert Config.AZURE_SPEECH_REGION is not None, "AZURE_SPEECH_REGION is not set"
        assert Config.STT_LANGUAGES is not None, "STT_LANGUAGES is not set"
        assert Config.TTS_VOICE is not None, "TTS_VOICE is not set"

        llm = openai.LLM.with_azure(
            azure_endpoint = Config.AZURE_OPENAI_ENDPOINT,
            api_key = Config.AZURE_OPENAI_API_KEY,
            model = Config.LLM_MODEL,
            temperature = Config.LLM_TEMPERATURE
        )

        stt = deepgram.STT(
            api_key="e3dad98357cdf75ca2630fa7f5523ea8fe87e864"
        )

        # stt = azure.STT(
        #     languages=Config.STT_LANGUAGES,
        #     speech_key=Config.AZURE_SPEECH_KEY,
        #     speech_region=Config.AZURE_SPEECH_REGION
        # )

        tts = azure.TTS(
            voice = Config.TTS_VOICE,
            speech_key = Config.AZURE_SPEECH_KEY,
            speech_region = Config.AZURE_SPEECH_REGION
        )

        vad = silero.VAD.load()

        return VoiceServices(llm=llm, stt=stt, tts=tts, vad=vad)
