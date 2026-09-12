"""Semantic retrieval module for DocuMind.
Performs top-k vector similarity search over the persistent ChromaDB collection.
"""

from typing import List, Tuple, Optional
from langchain_core.documents import Document
from src.retrieval.vectorstore import get_vectorstore


def search_documents(query: str, k: int = 4) -> List[Document]:
    """Retrieve top-k relevant document chunks for a query."""
    store = get_vectorstore()
    return store.similarity_search(query=query, k=k)


def search_documents_with_scores(query: str, k: int = 4) -> List[Tuple[Document, float]]:
    """Retrieve top-k relevant document chunks along with distance scores."""
    store = get_vectorstore()
    return store.similarity_search_with_score(query=query, k=k)
