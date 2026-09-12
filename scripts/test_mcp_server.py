"""Verification script for Phase 5: MCP Server.
Verifies tool registration, tool listing, and tool invocation.
"""

import sys
import asyncio
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.mcp_server.server import server, search_docs, summarize_sheet


async def verify_mcp():
    print("=== Testing DocuMind MCP Server ===")
    
    # 1. Verify registered tools
    tools = await server.list_tools()
    tool_names = [t.name for t in tools]
    print(f"Registered MCP Tools count: {len(tool_names)}")
    print(f"Tool names: {tool_names}")
    assert "search_docs" in tool_names, "Missing search_docs tool"
    assert "summarize_sheet" in tool_names, "Missing summarize_sheet tool"
    print("✓ Tool listing verified successfully!")

    # 2. Test search_docs tool call
    print("\n--- Testing 'search_docs' Tool Call ---")
    search_result = search_docs("What is the uptime SLA?")
    print(f"Result snippet:\n{search_result[:250]}...\n")
    assert "cloud_architecture.pdf" in search_result, "Expected cloud_architecture.pdf in search result"
    print("✓ search_docs tool invocation verified!")

    # 3. Test summarize_sheet tool call
    print("\n--- Testing 'summarize_sheet' Tool Call ---")
    sheet_result = summarize_sheet("financial_q3.xlsx")
    print(f"Result snippet:\n{sheet_result[:250]}...\n")
    assert "Engineering" in sheet_result, "Expected Engineering department in spreadsheet summary"
    print("✓ summarize_sheet tool invocation verified!")

    print("\n=== Phase 5 MCP Server Complete & Fully Verified! ===")


if __name__ == "__main__":
    asyncio.run(verify_mcp())
