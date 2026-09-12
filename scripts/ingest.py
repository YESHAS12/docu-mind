"""Ingestion pipeline script for DocuMind.
Loads all documents from sample_docs/, chunks them, embeds them locally,
and populates the persistent ChromaDB collection.
"""

import sys
from pathlib import Path

# Add project root to sys.path so src imports work cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config import SAMPLE_DOCS_DIR, CHROMA_DIR
from src.ingestion.loaders import load_directory
from src.ingestion.chunking import split_documents
from src.retrieval.vectorstore import build_vectorstore, get_vectorstore


def run_ingestion(docs_dir: Path = SAMPLE_DOCS_DIR, persist_dir: Path = CHROMA_DIR):
    """Execute complete ingestion pipeline."""
    print(f"=== DocuMind Ingestion Pipeline ===")
    print(f"Loading documents from: {docs_dir}")

    if not docs_dir.exists():
        raise FileNotFoundError(f"Source documents directory not found: {docs_dir}")

    raw_docs = load_directory(docs_dir)
    print(f"Successfully loaded {len(raw_docs)} raw document segments.")
    for doc in raw_docs:
        print(f"  - {doc.metadata.get('source')} (type: {doc.metadata.get('type')})")

    print("\nChunking documents...")
    chunks = split_documents(raw_docs)
    print(f"Generated {len(chunks)} text chunks.")

    print(f"\nEmbedding chunks and writing to ChromaDB at: {persist_dir}...")
    vectorstore = build_vectorstore(chunks, persist_directory=persist_dir)
    total_count = vectorstore._collection.count()
    print(f"ChromaDB collection successfully updated! Total items in store: {total_count}")

    # Run quick relevance verification
    print("\n--- Running Ingestion Sanity Checks ---")
    test_queries = [
        "What is the remote work policy?",
        "What is the system uptime SLA?",
        "What are the quarterly achievements for Q3?",
    ]
    for query in test_queries:
        results = vectorstore.similarity_search(query, k=2)
        top_match = results[0] if results else None
        print(f"Query: '{query}'")
        if top_match:
            print(f"  -> Top Result Source: {top_match.metadata.get('source')} (Score chunk {top_match.metadata.get('chunk_id')})")
            snippet = top_match.page_content.replace('\n', ' ')[:100]
            print(f"     Snippet: {snippet}...")
        else:
            print("  -> No match found.")

    print("\n=== Ingestion Complete & Verified ===")


if __name__ == "__main__":
    run_ingestion()
