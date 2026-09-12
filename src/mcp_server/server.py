"""Model Context Protocol (MCP) server for DocuMind.
Exposes document semantic search and spreadsheet analysis as standard MCP tools.
"""

import sys
from pathlib import Path
from typing import Optional

# Setup root path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
from mcp.server.mcpserver import MCPServer
from src.config import SAMPLE_DOCS_DIR
from src.retrieval.search import search_documents
from src.agents.spreadsheet_node import get_spreadsheet_dataframes

# Initialize MCP server
server = MCPServer("DocuMind")


@server.tool()
def search_docs(query: str) -> str:
    """Semantic vector search across indexed enterprise documents (PDF, PPTX, MD, policies, architecture).
    
    Args:
        query: The search question or topic.
        
    Returns:
        Formatted passages with source citations and metadata.
    """
    docs = search_documents(query=query, k=4)
    if not docs:
        return f"No relevant passages found for query: '{query}'"

    formatted_passages = []
    for idx, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        filetype = doc.metadata.get("type", "doc")
        extra = ""
        if "page" in doc.metadata:
            extra = f", Page {doc.metadata['page']}"
        elif "slide" in doc.metadata:
            extra = f", Slide {doc.metadata['slide']}"
        elif "sheet" in doc.metadata:
            extra = f", Sheet {doc.metadata['sheet']}"

        formatted_passages.append(
            f"--- Result {idx} [Source: {source} ({filetype}{extra})] ---\n{doc.page_content}"
        )

    return "\n\n".join(formatted_passages)


@server.tool()
def summarize_sheet(filename: str = "financial_q3.xlsx") -> str:
    """Summarize and inspect tabular data and numerical columns from an ingested spreadsheet.
    
    Args:
        filename: Name of the spreadsheet file in sample_docs/ (default: 'financial_q3.xlsx').
        
    Returns:
        Summary statistics, row records, and schema info.
    """
    target_path = SAMPLE_DOCS_DIR / filename
    if not target_path.exists():
        available = [f.name for f in SAMPLE_DOCS_DIR.glob("*.xlsx")]
        return f"File '{filename}' not found. Available sheets: {', '.join(available)}"

    xls = pd.ExcelFile(target_path)
    output_lines = [f"=== Spreadsheet Summary: {filename} ==="]
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        output_lines.append(f"\n[Sheet: {sheet_name}] ({len(df)} rows, {len(df.columns)} columns)")
        output_lines.append(f"Columns: {', '.join(df.columns.astype(str))}\n")
        output_lines.append("Data Preview:")
        output_lines.append(df.to_string(index=False))

        # Numeric summary if numeric columns exist
        numeric_cols = df.select_dtypes(include="number").columns
        if len(numeric_cols) > 0:
            output_lines.append("\nSummary Statistics:")
            output_lines.append(df[numeric_cols].describe().to_string())

    return "\n".join(output_lines)


def main():
    """Run the MCP server over standard input/output transport."""
    server.run()


if __name__ == "__main__":
    main()
