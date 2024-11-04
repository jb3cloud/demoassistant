import logging
from typing import Annotated, List

from livekit.agents.llm import FunctionContext, TypeInfo, ai_callable

from config import Config
from services.voice_services import VoiceServices
from tools.bing_search import bing_news_search_impl
from tools.db_query import DBQuery
from tools.weather import get_weather_impl
from tools.rag_search import RagSearch
from tools.code_runner import run_code

logger = logging.getLogger("agent_tools")

class AgentTools(FunctionContext):
    """
    The class defines a set of LLM tools that the assistant can execute.
    """

    def __init__(self, services: VoiceServices) -> None:
        """Initialize the AgentTools instance."""
        super().__init__()
        self._services = services
        self._rag_search = RagSearch.with_azure(Config.AZURE_SEARCH_INDEX_NAME)
        self._db_query = DBQuery.with_azure()

    @ai_callable(description="Get the current weather for the provided location")
    async def get_weather(
        self,
        location: Annotated[
            str, TypeInfo(description="The location to get the weather for")
        ],
    ) -> str:
        """Called when the user asks about the weather. This function will return the weather for the given location."""
        # ctx = AssistantCallContext.get_current()
        # messages = ctx.assistant.chat_ctx.messages
        return await get_weather_impl(location)


    @ai_callable(description="Search current news articles")
    async def search_news(
        self,
        query: Annotated[
            str, TypeInfo(description="The query used to search for current news articles")
        ],
    ) -> str:
        return await bing_news_search_impl(query)

    @ai_callable(description="Look up information about a specified topic")
    def query_info(
            self,
            query: Annotated[
                str, TypeInfo(description="The query used to search for information on a topic")
            ],
    ) -> str:
        result = self._rag_search.query(query)
        return str(result)

    @ai_callable(description="Execute code in a sandboxed environment")
    def execute_code(
            self,
            lang: Annotated[
                str, TypeInfo(description="The language of the code must be one of ['python', 'java', 'javascript', 'cpp', 'go', 'ruby']")
            ],
            code: Annotated[
                str, TypeInfo(description="The code to run in the sandboxed environment")
            ],
            libraries: Annotated[
                str, TypeInfo(description="Optional comma separated list of libraries to use")
            ],
    ) -> str:
        library_list = libraries.split(",") if libraries else None
        return run_code(lang, code, library_list)

    @ai_callable(description="Search the database for a given english query")
    def search_database(self,
                      query: Annotated[
                            str, TypeInfo(description="The english query used to search the database")
                        ],
                      ) -> str:
        result = self._db_query.execute_sql_query(query)
        return str(result)
