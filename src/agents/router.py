"""Router node for classifying user query intent.
Uses the fast 8B model — only classifies into one of three words, needs zero quality headroom.
"""

import time
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from groq import RateLimitError
from src.config import get_groq_api_key, FAST_GROQ_MODEL
from src.agents.state import AgentState

ROUTER_PROMPT = """You are an expert query classifier for an enterprise intelligence system.
Classify the given user query into one of three distinct routes:

1. 'spreadsheet': The query requires mathematical calculations, aggregation, budget numbers, actual spend, headcount, or financial comparisons from spreadsheets/tables (e.g. "What is the total budget?", "Which department spent the most?", "Calculate the margin").
2. 'docs': The query asks about policies, engineering standards, architecture, SLAs, company roadmap, guidelines, or factual document knowledge (e.g. "What is the remote work policy?", "What is the uptime SLA?", "How many approvals for a PR?").
3. 'general': The query is a conversational greeting, general question, or chit-chat not requiring internal document lookup (e.g. "Hello", "How are you?", "What can you do?").

Query: {query}

Respond strictly with ONLY ONE of the following three words: 'spreadsheet', 'docs', or 'general'."""


def _call_with_retry(chain, inputs: dict, max_retries: int = 3):
    """Call a LangChain chain with exponential backoff on 429 rate limit errors."""
    for attempt in range(max_retries):
        try:
            return chain.invoke(inputs)
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
        except Exception:
            raise


def router_node(state: AgentState) -> dict:
    """Classify the incoming user query into docs, spreadsheet, or general."""
    query = state.get("query", "").strip()
    trace = list(state.get("trace", []))

    api_key = get_groq_api_key()
    llm = ChatGroq(api_key=api_key, model=FAST_GROQ_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_template(ROUTER_PROMPT)
    chain = prompt | llm

    try:
        response = _call_with_retry(chain, {"query": query})
        raw_route = response.content.strip().lower()
        if "spreadsheet" in raw_route:
            route = "spreadsheet"
        elif "general" in raw_route:
            route = "general"
        else:
            route = "docs"
    except Exception as e:
        trace.append(f"Router error: {str(e)}; defaulting to 'docs'")
        route = "docs"

    trace.append(f"Router classified query as '{route}'")
    return {
        "route": route,
        "trace": trace
    }
