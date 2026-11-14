"""Rewrite node for reformulating queries when initial retrieval is insufficient.
Uses the fast 8B model — query reformulation doesn't need a 70B model.
"""

import time
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from groq import RateLimitError
from src.config import get_groq_api_key, FAST_GROQ_MODEL
from src.agents.state import AgentState

REWRITE_PROMPT = """You are an expert search query optimizer.
The user asked a question, but initial semantic retrieval failed to find sufficiently relevant passages in the document knowledge base.
Reformulate the query into a more specific, direct, and keyword-rich search string optimized for semantic vector retrieval over corporate policies, architecture guides, slide decks, and engineering handbooks.

Original Question: {question}
Previous Attempt: {previous_query}

Provide ONLY the reformulated search query. Do not include quotes, explanations, or introductory text."""


def _call_with_retry(chain, inputs: dict, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return chain.invoke(inputs)
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
        except Exception:
            raise


def rewrite_node(state: AgentState) -> dict:
    """Reformulate the user query to attempt better retrieval."""
    question = state.get("query", "")
    current_attempt = state.get("rewritten_query") or question
    retry_count = state.get("retry_count", 0) + 1
    trace = list(state.get("trace", []))

    api_key = get_groq_api_key()
    llm = ChatGroq(api_key=api_key, model=FAST_GROQ_MODEL, temperature=0.2)
    prompt = ChatPromptTemplate.from_template(REWRITE_PROMPT)
    chain = prompt | llm

    try:
        response = _call_with_retry(chain, {
            "question": question,
            "previous_query": current_attempt
        })
        rewritten = response.content.strip().strip('"')
    except Exception as e:
        trace.append(f"Rewrite error: {str(e)}; retaining previous query")
        rewritten = current_attempt

    trace.append(f"Retry #{retry_count}: Rewrote query to '{rewritten}'")
    return {
        "rewritten_query": rewritten,
        "retry_count": retry_count,
        "trace": trace
    }
