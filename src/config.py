from dotenv import load_dotenv
from dataclasses import dataclass
import os

load_dotenv()


@dataclass
class Config:
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
    AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
    AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
    AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
    BING_API_KEY = os.getenv("BING_API_KEY")
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
    LIVEKIT_URL = os.getenv("LIVEKIT_URL")
    LLM_MODEL = os.getenv("LLM_MODEL")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    LLM_PROMPT = os.getenv("LLM_PROMPT")
    STT_LANGUAGES = ["en-US"]
    TEXT_EMBEDDING_MODEL = os.getenv("TEXT_EMBEDDING_MODEL")
    TTS_VOICE = os.getenv("TTS_VOICE")
    DEMO_DATABASE = os.getenv("DEMO_DATABASE")

