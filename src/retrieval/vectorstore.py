"""Chroma vector store initialization and management using fastembed (ONNX-based, no PyTorch)."""

import os
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_chroma import Chroma
from src.config import CHROMA_DIR, EMBEDDING_MODEL_NAME, COLLECTION_NAME

# Suppress HF symlinks warning on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

_embeddings_instance: Optional[FastEmbedEmbeddings] = None


def get_embedding_function() -> FastEmbedEmbeddings:
    """Singleton getter for the local fastembed (ONNX) embedding model — no PyTorch required."""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = FastEmbedEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
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


def add_file_to_vectorstore(file_path: Path, persist_directory: Optional[Path] = None) -> int:
    """Ingest, chunk, and embed a newly uploaded file into the existing Chroma collection."""
    from src.ingestion.loaders import load_document
    from src.ingestion.chunking import split_documents

    raw_docs = load_document(file_path)
    if not raw_docs:
        return 0

    chunks = split_documents(raw_docs)
    store = get_vectorstore(persist_directory)
    store.add_documents(chunks)
    return len(chunks)
