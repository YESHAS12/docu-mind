"""LangGraph compilation and orchestration for DocuMind multi-agent workflow."""

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END

from src.agents.state import AgentState
from src.agents.router import router_node
from src.agents.retrieval_node import retrieval_node
from src.agents.grading_node import grading_node
from src.agents.rewrite_node import rewrite_node
from src.agents.spreadsheet_node import spreadsheet_node
from src.agents.synthesis_node import synthesis_node


def decide_route(state: AgentState) -> str:
    """Determine next node from router outcome."""
    route = state.get("route", "docs")
    if route == "spreadsheet":
        return "spreadsheet"
    elif route == "general":
        return "synthesis"
    return "retrieval"


def decide_after_grading(state: AgentState) -> str:
    """Route to synthesis if relevant or retry limit reached; otherwise rewrite query."""
    is_relevant = state.get("is_relevant", False)
    retry_count = state.get("retry_count", 0)

    if is_relevant:
        return "synthesis"
    if retry_count < 2:
        return "rewrite"
    return "synthesis"


def build_graph():
    """Build and compile the StateGraph."""
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("router", router_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("grading", grading_node)
    workflow.add_node("rewrite", rewrite_node)
    workflow.add_node("spreadsheet", spreadsheet_node)
    workflow.add_node("synthesis", synthesis_node)

    # Define edges
    workflow.add_edge(START, "router")

    workflow.add_conditional_edges(
        "router",
        decide_route,
        {
            "spreadsheet": "spreadsheet",
            "synthesis": "synthesis",
            "retrieval": "retrieval"
        }
    )

    workflow.add_edge("spreadsheet", "synthesis")
    workflow.add_edge("retrieval", "grading")

    workflow.add_conditional_edges(
        "grading",
        decide_after_grading,
        {
            "synthesis": "synthesis",
            "rewrite": "rewrite"
        }
    )

    workflow.add_edge("rewrite", "retrieval")
    workflow.add_edge("synthesis", END)

    return workflow.compile()


# Compiled singleton graph
documind_agent = build_graph()


def run_agent(query: str) -> Dict[str, Any]:
    """Convenience execution entrypoint for Streamlit UI and CLI tests."""
    initial_state: AgentState = {
        "query": query,
        "route": None,
        "retrieved_docs": [],
        "is_relevant": False,
        "rewritten_query": None,
        "retry_count": 0,
        "spreadsheet_result": None,
        "answer": "",
        "sources": [],
        "trace": [f"Received query: '{query}'"]
    }
    return documind_agent.invoke(initial_state)
