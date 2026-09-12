"""Evaluation test suite asserting that semantic retrieval finds expected source documents.
Runnable via pytest tests/.
"""

import sys
from pathlib import Path
import pytest

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.retrieval.search import search_documents

# 13 Hardcoded benchmark evaluation pairs
EVAL_PAIRS = [
    {
        "id": "eval_01",
        "query": "What is the remote work policy and how many days can employees work from home?",
        "expected_source": "company_policy.pdf"
    },
    {
        "id": "eval_02",
        "query": "How many days of annual paid leave and sick leave do employees get?",
        "expected_source": "company_policy.pdf"
    },
    {
        "id": "eval_03",
        "query": "What is the one-time home office equipment reimbursement budget?",
        "expected_source": "company_policy.pdf"
    },
    {
        "id": "eval_04",
        "query": "How much is the recurring monthly internet and connectivity stipend?",
        "expected_source": "company_policy.pdf"
    },
    {
        "id": "eval_05",
        "query": "What is the annual system uptime availability SLA?",
        "expected_source": "cloud_architecture.pdf"
    },
    {
        "id": "eval_06",
        "query": "What is the P95 and P99 API latency budget target?",
        "expected_source": "cloud_architecture.pdf"
    },
    {
        "id": "eval_07",
        "query": "What is the database automated point-in-time recovery backup retention period?",
        "expected_source": "cloud_architecture.pdf"
    },
    {
        "id": "eval_08",
        "query": "How many peer approvals are mandatory for merging a Pull Request?",
        "expected_source": "team_handbook.md"
    },
    {
        "id": "eval_09",
        "query": "On which days and times are production deployments scheduled?",
        "expected_source": "team_handbook.md"
    },
    {
        "id": "eval_10",
        "query": "What is the on-call response time SLA for P1 critical incidents?",
        "expected_source": "team_handbook.md"
    },
    {
        "id": "eval_11",
        "query": "How many active monthly enterprise users were achieved in Q3 milestones?",
        "expected_source": "quarterly_presentation.pptx"
    },
    {
        "id": "eval_12",
        "query": "What are the strategic roadmap objectives for Q4?",
        "expected_source": "quarterly_presentation.pptx"
    },
    {
        "id": "eval_13",
        "query": "What are the department budgets and revenue contributions in the spreadsheet?",
        "expected_source": "financial_q3.xlsx"
    },
]


@pytest.mark.parametrize("item", EVAL_PAIRS, ids=[i["id"] for i in EVAL_PAIRS])
def test_retrieval_finds_expected_source(item):
    """Assert semantic search returns chunks containing the expected source document."""
    query = item["query"]
    expected_source = item["expected_source"]

    retrieved_chunks = search_documents(query, k=4)
    assert len(retrieved_chunks) > 0, f"No chunks retrieved for query: '{query}'"

    retrieved_sources = [c.metadata.get("source") for c in retrieved_chunks]
    assert expected_source in retrieved_sources, (
        f"Query: '{query}'\n"
        f"Expected: {expected_source}\n"
        f"Retrieved: {retrieved_sources}"
    )
