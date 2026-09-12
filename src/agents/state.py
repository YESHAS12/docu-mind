"""State schema definition for the DocuMind LangGraph workflow."""

from typing import TypedDict, List, Optional, Literal
from langchain_core.documents import Document


class AgentState(TypedDict):
    """Shared state dictionary representing the workflow context."""
    query: str
    route: Optional[Literal["docs", "spreadsheet", "general"]]
    retrieved_docs: List[Document]
    is_relevant: bool
    rewritten_query: Optional[str]
    retry_count: int
    spreadsheet_result: Optional[str]
    answer: str
    sources: List[str]
    trace: List[str]
