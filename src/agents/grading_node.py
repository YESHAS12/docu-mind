"""Grading node evaluating relevance of retrieved documents to the query."""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.config import get_groq_api_key, DEFAULT_GROQ_MODEL
from src.agents.state import AgentState

GRADING_PROMPT = """You are an objective document relevance evaluator.
Assess whether the retrieved context passages contain information relevant to answering the user question.

User Question:
{question}

Retrieved Context Passages:
{context}

Respond strictly with ONLY ONE of the following two words:
'yes' - if the context contains relevant information that helps answer the question.
'no'  - if the context is completely unrelated, off-topic, or lacks information to address the question.

Do not include any explanation or extra characters."""


def grading_node(state: AgentState) -> dict:
    """Evaluate whether the retrieved documents are relevant to the query."""
    question = state.get("query", "")
    docs = state.get("retrieved_docs", [])
    trace = list(state.get("trace", []))

    if not docs:
        trace.append("Grading: No documents to evaluate -> False")
        return {"is_relevant": False, "trace": trace}

    context_snippets = "\n---\n".join([d.page_content for d in docs[:3]])

    api_key = get_groq_api_key()
    llm = ChatGroq(api_key=api_key, model=DEFAULT_GROQ_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_template(GRADING_PROMPT)
    chain = prompt | llm

    try:
        response = chain.invoke({
            "question": question,
            "context": context_snippets
        })
        verdict = response.content.strip().lower()
        is_relevant = "yes" in verdict
    except Exception as e:
        trace.append(f"Grading error: {str(e)}; assuming relevant")
        is_relevant = True

    trace.append(f"Grading evaluated relevance as: {is_relevant}")
    return {
        "is_relevant": is_relevant,
        "trace": trace
    }
