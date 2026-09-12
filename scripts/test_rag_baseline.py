"""Baseline RAG test script.
Queries ChromaDB, constructs a context prompt, calls Groq LLM, and prints grounded response with citations.
"""

import sys
from pathlib import Path

# Force UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.config import get_groq_api_key, DEFAULT_GROQ_MODEL
from src.retrieval.search import search_documents


RAG_PROMPT_TEMPLATE = """You are DocuMind, an intelligent document question-answering assistant.
Answer the user's question based strictly and truthfully on the provided context passages.
If the context does not contain sufficient information to answer the question, clearly state: "I cannot find this information in the provided documents."

Context Passages:
{context}

Question:
{question}

Answer with specific citations referencing the source filenames."""


def run_baseline_rag(question: str):
    """Execute simple RAG query."""
    print(f"\n==========================================")
    print(f"Question: {question}")

    api_key = get_groq_api_key()
    if not api_key:
        print("Error: GROQ_API_KEY is not set in .env")
        return

    # 1. Retrieve
    docs = search_documents(question, k=3)
    if not docs:
        print("No documents retrieved.")
        return

    # Format context and track sources
    context_blocks = []
    sources = set()
    for idx, doc in enumerate(docs):
        source = doc.metadata.get("source", "unknown")
        sources.add(source)
        context_blocks.append(f"[{idx+1}] (Source: {source})\n{doc.page_content}")

    context_str = "\n\n".join(context_blocks)

    # 2. Call Groq
    llm = ChatGroq(api_key=api_key, model=DEFAULT_GROQ_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    chain = prompt | llm

    response = chain.invoke({
        "context": context_str,
        "question": question
    })

    print(f"\nAnswer:\n{response.content}")
    print(f"\nCited Sources: {', '.join(sorted(sources))}")
    print(f"==========================================")


if __name__ == "__main__":
    test_questions = [
        "What is the company's remote work policy and how many days can employees work from home?",
        "What is the system uptime SLA and what is the target P95 latency?",
        "What are the code review requirements and on-call response SLAs?",
    ]
    for q in test_questions:
        run_baseline_rag(q)
