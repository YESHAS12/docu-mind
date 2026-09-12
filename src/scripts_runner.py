"""Initialization helpers for auto-ingesting sample documents on boot."""

import os
from pathlib import Path
from src.config import CHROMA_DIR, SAMPLE_DOCS_DIR
from src.retrieval.vectorstore import vectorstore_exists
from scripts.ingest import run_ingestion


def ensure_knowledge_base_ready():
    """Check if ChromaDB collection exists; if not, automatically run ingestion."""
    if not vectorstore_exists(CHROMA_DIR):
        print("ChromaDB not detected or empty. Running initial ingestion pipeline...")
        run_ingestion(docs_dir=SAMPLE_DOCS_DIR, persist_dir=CHROMA_DIR)
        print("Knowledge base successfully initialized!")
