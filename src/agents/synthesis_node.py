"""Synthesis node producing the final grounded answer with source citations."""

from typing import List, Set
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.config import get_groq_api_key, DEFAULT_GROQ_MODEL
from src.agents.state import AgentState

DOCS_SYNTHESIS_PROMPT = """You are DocuMind, an enterprise document intelligence assistant.
Synthesize a clear, accurate, and helpful response to the user's question based strictly on the provided context passages.
Always cite the source document filenames for facts you mention.

Context Passages:
{context}

User Question:
{question}

Answer with explicit inline source citations (e.g. [company_policy.pdf]):"""

SPREADSHEET_SYNTHESIS_PROMPT = """You are DocuMind, an enterprise document intelligence assistant.
Formulate a clear and direct answer to the user's query using the exact pandas mathematical calculation results provided below.
Do not recalculate or estimate numbers — report the exact figures computed.

Pandas Calculation Results:
{calculation_result}

User Question:
{question}

Source: {sources}

Answer clearly with the exact figures and cite the source spreadsheet file:"""

GENERAL_SYNTHESIS_PROMPT = """You are DocuMind, an AI-powered document intelligence assistant.
Respond politely and helpfully to the user's conversational greeting or general inquiry.
Explain that you are an agentic document assistant capable of answering questions from corporate documents, engineering policies, slide decks, and spreadsheets (with exact numeric calculations).

User Message: {question}"""


def synthesis_node(state: AgentState) -> dict:
    """Produce the final answer and compiled list of cited sources."""
    query = state.get("query", "")
    route = state.get("route", "docs")
    trace = list(state.get("trace", []))
    trace.append("Executing synthesis node")

    api_key = get_groq_api_key()
    llm = ChatGroq(api_key=api_key, model=DEFAULT_GROQ_MODEL, temperature=0.1)

    sources: Set[str] = set(state.get("sources", []))
    answer = ""

    if route == "spreadsheet":
        calc_result = state.get("spreadsheet_result", "")
        sources_str = ", ".join(sources) if sources else "financial_q3.xlsx"
        prompt = ChatPromptTemplate.from_template(SPREADSHEET_SYNTHESIS_PROMPT)
        chain = prompt | llm
        try:
            resp = chain.invoke({
                "calculation_result": calc_result,
                "question": query,
                "sources": sources_str
            })
            answer = resp.content.strip()
        except Exception as e:
            answer = f"According to {sources_str}, the calculated result is:\n{calc_result}"
        sources = sources or {"financial_q3.xlsx"}

    elif route == "general":
        prompt = ChatPromptTemplate.from_template(GENERAL_SYNTHESIS_PROMPT)
        chain = prompt | llm
        try:
            resp = chain.invoke({"question": query})
            answer = resp.content.strip()
        except Exception as e:
            answer = "Hello! I am DocuMind, your document intelligence assistant. How can I assist you with your documents today?"

    else:
        # Route == "docs"
        docs = state.get("retrieved_docs", [])
        is_relevant = state.get("is_relevant", True)

        if not docs or not is_relevant:
            answer = "I could not find sufficient information in the provided documents to answer your question."
        else:
            context_blocks = []
            for idx, doc in enumerate(docs):
                source = doc.metadata.get("source", "document")
                sources.add(source)
                context_blocks.append(f"[{idx+1}] (Source: {source})\n{doc.page_content}")

            context_str = "\n\n".join(context_blocks)
            prompt = ChatPromptTemplate.from_template(DOCS_SYNTHESIS_PROMPT)
            chain = prompt | llm
            try:
                resp = chain.invoke({
                    "context": context_str,
                    "question": query
                })
                answer = resp.content.strip()
            except Exception as e:
                answer = f"Error generating answer: {str(e)}"

    return {
        "answer": answer,
        "sources": sorted(list(sources)),
        "trace": trace
    }
