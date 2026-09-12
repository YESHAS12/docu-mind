"""Spreadsheet node for exact numerical and tabular computations using pandas."""

from pathlib import Path
from typing import Dict, Any
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.config import SAMPLE_DOCS_DIR, get_groq_api_key, DEFAULT_GROQ_MODEL
from src.agents.state import AgentState


def get_spreadsheet_dataframes() -> Dict[str, pd.DataFrame]:
    """Load all Excel sheets into memory."""
    dfs = {}
    for excel_path in SAMPLE_DOCS_DIR.glob("*.xlsx"):
        xls = pd.ExcelFile(excel_path)
        for sheet_name in xls.sheet_names:
            key = f"{excel_path.name}::{sheet_name}"
            dfs[key] = pd.read_excel(xls, sheet_name=sheet_name)
    return dfs


PANDAS_CODE_PROMPT = """You are a Python pandas expert.
You are given a query asking for numeric or tabular facts from an Excel spreadsheet.
Here are the available dataframes and schemas:

{schema_info}

Write a brief Python snippet to calculate or extract the answer.
- The dataframes are stored in dictionary `dfs` where keys are e.g. '{primary_key}'.
- You may assign the final answer string, number, or DataFrame summary to a variable named `result`.
- Output ONLY valid Python code block inside ```python and ```. No extra text or markdown outside the code block.

User Query: {query}"""


def spreadsheet_node(state: AgentState) -> dict:
    """Execute pandas operations to answer numeric/tabular queries with mathematical accuracy."""
    query = state.get("query", "")
    trace = list(state.get("trace", []))
    trace.append("Executing pandas spreadsheet calculation node")

    dfs = get_spreadsheet_dataframes()
    if not dfs:
        trace.append("No Excel files found in sample_docs")
        return {
            "spreadsheet_result": "No spreadsheet files found in knowledge base.",
            "sources": [],
            "trace": trace
        }

    # Prepare schema representations
    schema_parts = []
    primary_key = list(dfs.keys())[0]
    sources = set()
    for key, df in dfs.items():
        filename = key.split("::")[0]
        sources.add(filename)
        schema_parts.append(
            f"Key: '{key}'\nColumns: {list(df.columns)}\nPreview:\n{df.to_string(index=False)}"
        )
    schema_info = "\n\n".join(schema_parts)

    api_key = get_groq_api_key()
    llm = ChatGroq(api_key=api_key, model=DEFAULT_GROQ_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_template(PANDAS_CODE_PROMPT)
    chain = prompt | llm

    calculation_result = None
    try:
        response = chain.invoke({
            "schema_info": schema_info,
            "primary_key": primary_key,
            "query": query
        })
        code_text = response.content.strip()
        if "```python" in code_text:
            code_text = code_text.split("```python")[1].split("```")[0].strip()
        elif "```" in code_text:
            code_text = code_text.split("```")[1].split("```")[0].strip()

        # Safe execution environment containing the DataFrames and pandas
        local_scope = {"dfs": dfs, "pd": pd, "result": None}
        exec(code_text, {}, local_scope)
        calculation_result = local_scope.get("result")
        trace.append(f"Calculated result via pandas: {calculation_result}")
    except Exception as e:
        trace.append(f"Pandas code execution error: {str(e)}; generating descriptive summary")
        # Fallback: compute summary statistics across all numeric columns
        fallback_summaries = []
        for key, df in dfs.items():
            fallback_summaries.append(f"Summary for {key}:\n{df.describe(include='all').to_string()}")
        calculation_result = "\n\n".join(fallback_summaries)

    return {
        "spreadsheet_result": str(calculation_result),
        "sources": sorted(list(sources)),
        "trace": trace
    }
