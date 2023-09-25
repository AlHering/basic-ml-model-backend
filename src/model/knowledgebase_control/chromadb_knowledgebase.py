# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import Any, List
from chromadb.api.types import EmbeddingFunction, Embeddings, Documents
from chromadb.config import Settings
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.vectorstores.base import VectorStoreRetriever
from src.configuration import configuration as cfg
from src.utility.bronze.hashing_utility import hash_text_with_sha256
from src.model.knowledgebase_control.abstract_knowledgebase import KnowledgeBase
from src.utility.silver import embedding_utility


class ChromaKnowledgeBase(KnowledgeBase):
    """
    Class for handling knowledge base interaction with ChromaDB.
    """

    def __init__(self, peristant_directory: str, metadata: dict = None, base_embedding_function: EmbeddingFunction = None, implementation: str = None) -> None:
        """
        Initiation method.
        :param peristant_directory: Persistant directory for ChromaDB data.
        :param metadata: Embedding collection metadata. Defaults to None.
        :param base_embedding_function: Embedding function for base collection. Defaults to T5 large.
        """
        if not os.path.exists(peristant_directory):
            os.makedirs(peristant_directory)
        self.peristant_directory = peristant_directory
        self.base_embedding_function = embedding_utility.LocalHuggingFaceEmbeddings(
            cfg.PATHS.INSTRUCT_XL_PATH
        ) if base_embedding_function is None else base_embedding_function
        self.client_settings = Settings(persist_directory=peristant_directory,
                                        chroma_db_impl="duckdb+parquet" if implementation is None else implementation)

        self.collections = {}
        self.base_chromadb = self.get_or_create_collection(
            "base", metadata=metadata)

    # Override
    def delete_document(self, document_id: Any, collection: str = "base") -> None:
        """
        Method for deleting a document from the knowledgebase.
        :param document_id: Document ID.
        :param collection: Collection to remove document from.
        """
        self.collections[collection].delete_document(document_id)
        self.collections[collection].persist()

    # Override
    def wipe_knowledgebase(self) -> None:
        """
        Method for wiping knowledgebase.
        """
        pass

    # Override
    def get_or_create_collection(self, collection: str, metadata: dict = None, embedding_function: EmbeddingFunction = None) -> Chroma:
        """
        Method for retrieving or creating a collection.
        :param collection: Collection collection.
        :param metadata: Embedding collection metadata. Defaults to None.
        :param embedding_function: Embedding function for the collection. Defaults to base embedding function.
        :return: Database API.
        """
        if collection not in self.collections:
            self.collections[collection] = Chroma(
                persist_directory=self.peristant_directory,
                embedding_function=self.base_embedding_function if embedding_function is None else embedding_function,
                collection_name=collection,
                collection_metadata=metadata,
                client_settings=self.client_settings
            )
        return self.collections[collection]

    # Override
    def get_retriever(self, collection: str = "base", search_type: str = "similarity", search_kwargs: dict = {"k": 4, "include_metadata": True}) -> VectorStoreRetriever:
        """
        Method for acquiring a retriever.
        :param collection: Collection to use.
            Defaults to "base" collection.
        :param search_type: The retriever's search type. Defaults to "similarity".
        :param search_kwargs: The retrievery search keyword arguments. Defaults to {"k": 4, "include_metadata": True}.
        :return: Retriever instance.
        """
        db = self.collections.get(collection, self.collections["base"])
        search_kwargs["k"] = min(
            search_kwargs["k"], len(db.get()["ids"]))
        return db.as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )

    # Override
    def embed_documents(self, documents: List[Document], metadatas: List[dict] = None, ids: List[str] = None, collection: str = "base", compute_metadata: bool = False) -> None:
        """
        Method for embedding documents.
        :param documents: Documents to embed.
        :param metadatas: Metadata entries. 
            Defaults to None.
        :param ids: Custom IDs to add. 
            Defaults to the hash of the document contents.
        :param collection: Collection to use.
            Defaults to "base".
        :param compute_metadata: Flag for declaring, whether to compute metadata.
            Defaults to False.
        """
        if metadatas is None:
            metadatas = [{} for _ in documents]
        if compute_metadata:
            for doc_index, doc_content in enumerate(documents):
                metadatas[doc_index] = metadatas[doc_index].update(
                    self.compute_metadata(doc_content, collection))

        self.collections[collection].add_documents(documents=documents, metadatas=metadatas, ids=[
            hash_text_with_sha256(document.page_content) for document in documents] if ids is None else ids)

        self.collections[collection].persist()
