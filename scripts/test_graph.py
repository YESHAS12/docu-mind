"""Test script for Phase 4: LangGraph Multi-Agent State Machine.
Tests router, retrieval, self-correcting grading & rewrite loop, spreadsheet calculations, and synthesis.
"""

import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.agents.graph import run_agent


def test_queries():
    queries = [
        "What is the policy on home office equipment reimbursement?",
        "What is the total actual spend across all departments in Q3, and what was the budget for Engineering?",
        "Which department has the highest headcount and how many people are in it?",
        "Hello! Who are you and what documents can you assist me with?",
        "Tell me about stuff breaking and how quickly people must jump on it",
        "What is the company policy on bringing pet llamas to work?",
    ]

    for idx, q in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST {idx}: {q}")
        print(f"{'='*70}")
        result = run_agent(q)
        print(f"Route Selected: {result.get('route')}")
        print(f"Retry Count:    {result.get('retry_count')}")
        print(f"Sources Cited:  {result.get('sources')}")
        print("\nWorkflow Execution Trace:")
        for step in result.get("trace", []):
            print(f"  • {step}")
        print(f"\nFinal Answer:\n{result.get('answer')}\n")


if __name__ == "__main__":
    test_queries()
