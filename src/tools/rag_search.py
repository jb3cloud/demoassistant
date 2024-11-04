import logging

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient

from llama_index.core import QueryBundle, VectorStoreIndex
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.base.response.schema import PydanticResponse, Response
from llama_index.core.llms import LLM
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.vector_stores.azureaisearch import AzureAISearchVectorStore, IndexManagement

from config import Config

logger = logging.getLogger('rag_search')


class RagSearch:
    """
    RagSearch class for handling search operations using embeddings and vector stores.
    """

    def __init__(self, embedding_model: BaseEmbedding, vector_store: BasePydanticVectorStore, llm: LLM) -> None:
        """
        Initialize the RagSearch instance.

        :param embedding_model: The embedding model to use for generating embeddings.
        :param vector_store: The vector store to use for storing and querying vectors.
        """
        self._embedding_model = embedding_model
        self._llm = llm
        self._vector_store = vector_store
        self._index = VectorStoreIndex.from_vector_store(vector_store, self._embedding_model)
        self._query_engine = self._index.as_query_engine(llm=llm, streaming=False)
        pass


    def query(self, query: str | QueryBundle) -> Response:
        """
        Query the search index.

        :param query: The query string to search for.
        :return: The search response.
        """
        assert self._index is not None, "Index is not loaded"
        logger.info(f"Querying search index using: {query}")
        return self._query_engine.query(query)


    @staticmethod
    def with_azure(index_name: str) -> 'RagSearch':
        """
        Create a RagSearch instance configured to use Azure services.

        :return: A configured RagSearch instance.
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

        search_index_client = SearchIndexClient(
            endpoint=Config.AZURE_SEARCH_ENDPOINT,
            credential=AzureKeyCredential(Config.AZURE_SEARCH_API_KEY)
        )

        vector_store = AzureAISearchVectorStore(
            search_or_index_client=search_index_client,
            index_name=index_name,
            index_management=IndexManagement.CREATE_IF_NOT_EXISTS,
            id_field_key="chunk_id",
            chunk_field_key="chunk",
            doc_id_field_key="title",
            embedding_field_key="text_vector",
            metadata_string_field_key="metadata"
        )

        return RagSearch(embed_model, vector_store, llm)
