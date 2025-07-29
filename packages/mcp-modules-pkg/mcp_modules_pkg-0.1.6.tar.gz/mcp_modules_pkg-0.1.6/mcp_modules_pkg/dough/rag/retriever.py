
import logging
import os
from typing import Any, Dict, List, Sequence, Union

from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseLanguageModel
from langchain_core.vectorstores import VectorStore
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class Base:
    def __init__(
        self,
        collection_name: str,
        vectorstore: VectorStore = None,  # 사용하고자 하는 vectorstore가 없으면 기본 값으로 설정 (milvus)
        embedding_function: Embeddings = None,
    ):
        """Initializes the Base class with collection name, vector store, and embedding function.

        This class serves as a base for building retrievers that utilize vector stores
        and embedding functions for document retrieval.

        Args:
            collection_name (str): The name of the collection for searches.
            vectorstore (VectorStore, optional): The vector store for storing/searching. Defaults to None, which implies a Milvus vector store will be used if no vector store is provided.
            embedding_function (Embeddings, optional): The embedding function to use for generating embeddings. Defaults to None, indicating that OpenAI embeddings will be used if no embedding function is provided.
        """
        self.collection_name = collection_name
        self.set_default_embedding_function(embedding_function)
        self.set_default_vectorstore(vectorstore)

    def set_default_vectorstore(self, vectorstore: VectorStore):
        """Sets a default vector store if none is provided.

        If no vector store is specified, initializes a Milvus vector store with default connection parameters.

        Args:
            vectorstore (VectorStore): The vector store to use. If None, initializes a Milvus vector store.
        """
        self.vectorstore = vectorstore
        if self.vectorstore is None:
            from dough.db_connector.milvus import MilvusConnectionInfo
            from langchain_community.vectorstores.milvus import Milvus

            self.conn = MilvusConnectionInfo("milvus").conn
            self.vectorstore = Milvus(
                embedding_function=self.embedding_function,
                connection_args={"host": self.conn.host, "port": str(self.conn.port)},
                collection_name=self.collection_name,
                search_params={"ef": 50},
            )

    def set_default_embedding_function(self, embedding_function: Embeddings):
        """Sets a default embedding function if none is provided.

        If no embedding function is specified, uses OpenAI embeddings with the API key obtained from environment variables.

        Args:
            embedding_function (Embeddings): The embedding function to use. If None, uses OpenAI embeddings.
        """
        self.embedding_function = embedding_function
        if self.embedding_function is None:
            from langchain_openai import OpenAIEmbeddings

            self.embedding_function = OpenAIEmbeddings(
                api_key=self.get_openai_api_key()
            )

    def get_openai_api_key(self) -> str:
        """Retrieves the OpenAI API key from environment variables.

        Returns:
            str: The OpenAI API key.

        Raises:
            KeyError: If the OPENAI_API_KEY environment variable is not found.
        """
        return os.environ["OPENAI_API_KEY"]


class Retriever(Base):
    def __init__(
        self,
        collection_name: str,
        vectorstore: VectorStore = None,
        embedding_function: Embeddings = None,
    ):
        """Initializes the Retriever class for performing document retrieval tasks.

        Inherits from the Base class and utilizes its initialization for setting up collection name, vector store, and embedding function.

        Args:
            collection_name (str): The name of the collection for searches.
            vectorstore (VectorStore, optional): The vector store for storing/searching. Defaults to None.
            embedding_function (Embeddings, optional): The embedding function to use for generating embeddings. Defaults to None.
        """
        super().__init__(collection_name, vectorstore, embedding_function)

    def search(
        self, query: str, k=4, expr: str = None, **kwargs: Any
    ) -> List[Document]:
        """Performs a similarity search for the query.

        Searches the vector store for documents similar to the query, optionally applying a filter expression.

        Args:
            query (str): The search query.
            k (int, optional): Number of results to return. Defaults to 4.
            expr (str, optional): Filter expression to apply to search results. Examples include "(year == 2024)" or "(year == 2024) and (repoid == 'wordcookies')". Defaults to None.
            **kwargs: Additional keyword arguments passed to the vector store's similarity search method.

        Returns:
            List[Document]: A list of similar Documents.
        """
        kwargs["expr"] = expr
        if isinstance(k, str):
            k = int(k)
        return self.vectorstore.similarity_search(query, k, **kwargs)

    def mmr_search(self, query: str) -> List[Document]:
        """Performs an MMR search for the query.

        Maximizes relevance while minimizing redundancy in the returned documents.

        Args:
            query (str): The search query.

        Returns:
            List[Document]: A list of Documents ranked by MMR relevance.
        """
        retriever = self.vectorstore.as_retriever(search_type="mmr")
        return retriever.get_relevant_documents(query)

    def similarity_threshold_search(
        self, query: str, threshold: float = 0.7
    ) -> List[Document]:
        """Performs a similarity search with a threshold for relevance.

        Only returns documents that meet the specified similarity threshold.

        Args:
            query (str): The search query.
            threshold (float, optional): The similarity threshold for relevance. Defaults to 0.7.

        Returns:
            List[Document]: A list of Documents that meet the similarity threshold.

        Raises:
            NotImplementedError: If the vector store does not support threshold searches.
        """
        try:
            retriever = self.vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"score_threshold": threshold},
            )
            docs = retriever.get_relevant_documents(query)
        except NotImplementedError:
            raise NotImplementedError(
                "Similarity threshold search is not supported for this vector store."
            )
        return docs

    def self_query(
        self,
        query: str,
        documents_description: str,
        metadata_field_info: Sequence[Union[AttributeInfo, Dict]],
        llm: BaseLanguageModel = None,
        k: int = 4,
        **kwargs,
    ) -> List[Document]:
        """Performs a self-query using a language model.

        This method allows querying documents based on their descriptions and metadata fields, utilizing a language model for understanding and relevance.

        Args:
            query (str): The search query.
            documents_description (str): Description of the documents for the LLM.
            metadata_field_info (Sequence[Union[AttributeInfo, Dict]]): Metadata fields for document filtering.
            llm (BaseLanguageModel, optional): The language model to use. Defaults to ChatOpenAI if None.
            k (int, optional): Number of results to return. Defaults to 4.
            **kwargs: Additional arguments for the search.

        Returns:
            List[Document]: A list of Documents relevant to the query
        """
        if llm is None:
            llm = ChatOpenAI(temperature=0, openai_api_key=self.get_openai_api_key())

        retriever = SelfQueryRetriever.from_llm(
            llm,
            self.vectorstore,
            documents_description,
            metadata_field_info,
            search_kwargs={"k": k},
        )
        return retriever.get_relevant_documents(query, **kwargs)


class LoadableRetriever(Base):
    def __init__(
        self,
        collection_name: str,
        vectorstore: VectorStore = None,
        embedding_function: Embeddings = None,
    ):
        """Initializes the LoadableRetriever class for document insertion tasks.

        Inherits from the Base class and utilizes its initialization for setting up collection name, vector store, and embedding function.

        Args:
            collection_name (str): The name of the collection for searches.
            vectorstore (VectorStore, optional): The vector store for storing/searching. Defaults to None.
            embedding_function (Embeddings, optional): The embedding function to use for generating embeddings. Defaults to None.
        """
        super().__init__(collection_name, vectorstore, embedding_function)

    def insert(
        self, df: "pd.DataFrame", vector_field: str
    ):
        """Inserts documents into the vector store.

        Processes a DataFrame to create Document objects with specified content and metadata, which are then inserted into the vector store.

        Args:
            df (pd.DataFrame): The DataFrame containing the documents to insert.
            vector_field (str): The column name in the DataFrame that contains the document content.

        Note:
            Requires pandas to be installed and imported as pd in the calling environment.
        """
        metadata_columns = [field for field in df.columns if field != vector_field]
        df['metadata'] = df.loc[:, metadata_columns].to_dict(orient='records')
        docs = [
            Document(page_content=row[vector_field], metadata=row["metadata"])
            for _, row in df.iterrows()
        ]
        from langchain_community.vectorstores.milvus import Milvus
        Milvus.from_documents(
            docs,
            self.embedding_function,
            connection_args={"host": self.conn.host, "port": str(self.conn.port)},
            collection_name=self.collection_name,
        )

    def drop_collection(self):
        """Drops the current collection from the Milvus vector store."""
        try:
            from pymilvus import connections, utility
            connections.connect(alias="default", host=self.conn.host, port=self.conn.port)
            if utility.has_collection(self.collection_name):
                utility.drop_collection(self.collection_name)
                logger.info(f"Collection '{self.collection_name}' dropped successfully.")
            else:
                logger.warning(f"Collection '{self.collection_name}' does not exist.")
        except Exception as e:
            logger.error(f"Failed to drop collection '{self.collection_name}': {e}")
            raise