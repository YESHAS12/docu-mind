"""Configuration settings for DocuMind.
Supports local .env via python-dotenv and Streamlit secrets for deployment.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DOCS_DIR = BASE_DIR / "sample_docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

# Load local environment variables if .env exists, overriding any stale system-wide vars
load_dotenv(BASE_DIR / ".env", override=True)


def get_groq_api_key() -> str:
    """Retrieve Groq API key from Streamlit secrets (if deployed) or environment variable."""
    # First check Streamlit secrets if running inside Streamlit
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    # Fallback to standard environment variable
    key = os.getenv("GROQ_API_KEY", "")
    if key:
        os.environ["GROQ_API_KEY"] = key
    return key


# Model constants
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "documind_docs"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
