"""Retrieval node for fetching relevant document chunks."""

from src.retrieval.search import search_documents
from src.agents.state import AgentState


def retrieval_node(state: AgentState) -> dict:
    """Retrieve document chunks from vector store using active query."""
    search_query = state.get("rewritten_query") or state.get("query", "")
    trace = list(state.get("trace", []))
    
    trace.append(f"Retrieving top document chunks for search query: '{search_query}'")
    docs = search_documents(query=search_query, k=4)
    trace.append(f"Retrieved {len(docs)} chunks from vector store")

    return {
        "retrieved_docs": docs,
        "trace": trace
    }
