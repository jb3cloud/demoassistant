import logging
from pathlib import Path

from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import SQLDatabase
from sqlalchemy import create_engine

from config import Config

logger = logging.getLogger('db_query')


class DBQuery:
    """
    DBQuery class for handling database query operations.
    """

    def __init__(self, llm: LLM, embedding_model: BaseEmbedding) -> None:
        p = Path(__file__).with_name(Config.DEMO_DATABASE)
        engine = create_engine(f"sqlite:///{p.absolute()}")
        db = SQLDatabase(engine)
        self._query_engine = NLSQLTableQueryEngine(
            sql_database=db,
            llm=llm,
            embed_model=embedding_model
        )
        pass


    def execute_sql_query(self, query: str) -> str:
        """
        Query the search index.

        :param query: The query string to search for.
        :return: The search response.
        """
        assert self._query_engine is not None, "Query engine is not loaded"
        logger.info(f"Querying database using: {query}")
        result = self._query_engine.query(query)
        logger.info(f"Query result: {result}")
        return str(result)

    @staticmethod
    def with_azure() -> 'DBQuery':
        """
        Create a DBQuery instance configured to use Azure services.

        :return: A configured DBQuery instance.
        """
        llm = AzureOpenAI(
            model=Config.LLM_MODEL,
            engine=Config.LLM_MODEL,
            api_key=Config.AZURE_OPENAI_API_KEY,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )

        embed_model = AzureOpenAIEmbedding(
            model=Config.TEXT_EMBEDDING_MODEL,
            api_key=Config.AZURE_OPENAI_API_KEY,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT)

        return DBQuery(llm, embed_model)
