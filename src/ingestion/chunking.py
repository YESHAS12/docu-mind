"""Chunking logic using RecursiveCharacterTextSplitter."""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP


def get_text_splitter(
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> RecursiveCharacterTextSplitter:
    """Create a configured RecursiveCharacterTextSplitter instance."""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len
    )


def split_documents(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Document]:
    """Split a list of raw documents into chunks preserving metadata."""
    splitter = get_text_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(documents)
    # Add chunk index to metadata
    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = idx
    return chunks
