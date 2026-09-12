"""Chroma vector store initialization and management using sentence-transformers."""

import os
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import chromadb
from src.config import CHROMA_DIR, EMBEDDING_MODEL_NAME, COLLECTION_NAME

# Suppress HF symlinks warning on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

_embeddings_instance: Optional[HuggingFaceEmbeddings] = None


def get_embedding_function() -> HuggingFaceEmbeddings:
    """Singleton getter for the local HuggingFace embedding model."""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embeddings_instance


def get_vectorstore(persist_directory: Optional[Path] = None) -> Chroma:
    """Retrieve or initialize the persistent Chroma vector store."""
    directory = str(persist_directory or CHROMA_DIR)
    embeddings = get_embedding_function()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=directory
    )


def vectorstore_exists(persist_directory: Optional[Path] = None) -> bool:
    """Check whether a non-empty Chroma collection exists."""
    directory = persist_directory or CHROMA_DIR
    if not directory.exists():
        return False
    try:
        store = get_vectorstore(directory)
        count = store._collection.count()
        return count > 0
    except Exception:
        return False


def build_vectorstore(documents: List[Document], persist_directory: Optional[Path] = None) -> Chroma:
    """Build and persist a Chroma collection from a list of Document objects."""
    directory = str(persist_directory or CHROMA_DIR)
    embeddings = get_embedding_function()
    store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=directory
    )
    return store
