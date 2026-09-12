# DocuMind — Multi-Agent Document Intelligence Assistant

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Groq API](https://img.shields.io/badge/LLM-Groq%20Free%20Tier-green.svg)](https://console.groq.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io)
[![MCP Server](https://img.shields.io/badge/MCP-Official%20SDK-purple.svg)](https://modelcontextprotocol.io)
[![Cost](https://img.shields.io/badge/Deployment%20Cost-%240%20Free-brightgreen.svg)]()

**DocuMind** is an enterprise-grade, multi-agent document intelligence assistant built to ingest mixed document corpora (PDF, PPTX, XLSX, TXT, Markdown), route user intent, execute exact spreadsheet mathematics without LLM hallucination, self-correct retrieval failures via a cyclic query rewriter loop, and expose its capabilities through both a chat UI and a Model Context Protocol (MCP) server.

The entire stack is built to run **100% free ($0 cost)** using Groq's high-speed free tier, local `sentence-transformers` embeddings, in-process ChromaDB vector store, and Streamlit Community Cloud.

---

## 🏛️ Architecture & State Machine

DocuMind is orchestrated via a **LangGraph StateGraph** state machine rather than a simple linear chain:

```
                          ┌────────────────────────┐
                          │   User Query (Chat/MCP)│
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │      Router Node       │
                          └───────────┬────────────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             │ (docs)                 │ (spreadsheet)          │ (general)
             ▼                        ▼                        ▼
   ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
   │  Retrieval Node   │    │ Spreadsheet Node  │    │  Synthesis Node   │
   │ (ChromaDB Vector) │    │  (pandas execute) │    │ (Direct Response) │
   └─────────┬─────────┘    └─────────┬─────────┘    └─────────┬─────────┘
             │                        │                        │
             ▼                        │                        │
   ┌───────────────────┐              │                        │
   │   Grading Node    │              │                        │
   │ (LLM Evaluator)   │              │                        │
   └─────────┬─────────┘              │                        │
             │                        │                        │
       Relevant?                      │                        │
       /       \                      │                        │
    (Yes)      (No & retry < 2)       │                        │
     │            \                   │                        │
     │             ▼                  │                        │
     │   ┌───────────────────┐        │                        │
     │   │   Rewrite Node    │        │                        │
     │   │ (Query Optimizer) │        │                        │
     │   └─────────┬─────────┘        │                        │
     │             │ (retry search)   │                        │
     │             └───────► Retrieval│                        │
     │                                │                        │
     └────────────────────────────────┼────────────────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │     Synthesis Node     │
                          │   Answer + Citations   │
                          └────────────────────────┘
```

### Why the Self-Correcting Retry Loop?
Standard Retrieval-Augmented Generation (RAG) pipelines fail silently when a user asks a question with colloquialisms, vague terminology, or partial keywords (e.g., *"tell me about stuff breaking and how quickly people jump on it"*). A single linear retrieval step fetches weak semantic matches and feeds them to the generator, resulting in hallucinations or generic failures.

DocuMind solves this using a **LangGraph cyclic feedback loop**:
1. **Grading Node**: An LLM judge evaluates whether retrieved passages actually contain relevant information to answer the question.
2. **Rewrite Node**: If graded irrelevant, the query rewriter optimizes keywords (e.g. converting colloquial terms to enterprise policy keywords) and triggers a second retrieval pass.
3. **Loop Safeguard**: A strict `retry_count < 2` guardrail guarantees the loop always terminates and falls back gracefully.

### Why Dedicated Spreadsheet Math?
LLMs are notoriously prone to arithmetic hallucinations when asked to sum or aggregate columns from tabular text. DocuMind routes numeric and tabular questions to a dedicated **Spreadsheet Node** that executes real Python `pandas` operations against the underlying `.xlsx` file, producing mathematically exact numbers every time.

---

## 🚀 Key Features

- **Mixed Document Ingestion**: Native parsers for `.pdf` (`pypdf`), `.pptx` (`python-pptx`), `.xlsx` (`openpyxl` / `pandas`), and `.md`/`.txt`.
- **Zero Cost & Local Embeddings**: Uses `sentence-transformers/all-MiniLM-L6-v2` running on CPU in-process — no paid OpenAI/Cohere embedding API keys.
- **Model Context Protocol (MCP)**: Exposes `search_docs` and `summarize_sheet` as standardized tools callable by any MCP client (Claude Desktop, Cursor, etc.).
- **Self-Healing Knowledge Base**: The Streamlit application auto-detects if `chroma_db/` exists on boot and initializes from `sample_docs/` automatically.
- **Enterprise Guardrails**: Built-in input length capping (max 500 chars), prompt injection screening, and session usage tracking.
- **Strict Citation Grounding**: Every factual statement is cited with its exact source filename.

---

## 🛠️ Project Structure

```
docu-mind/
├── app.py                     # Streamlit web entrypoint & Chat UI
├── requirements.txt           # Python dependencies
├── .env.example               # Template for environment variables
├── .gitignore                 # Excludes .env, chroma_db/, .venv/, etc.
├── README.md                  # System architecture and documentation
├── sample_docs/               # Seeded corpus for testing and public demo
│   ├── company_policy.pdf     # Employee policies, leave, WFH, stipends
│   ├── cloud_architecture.pdf # System design, 99.99% SLA, latency budgets
│   ├── quarterly_presentation.pptx # Strategy slides & Q3 metrics
│   ├── financial_q3.xlsx      # Financials: budget, actual spend, headcount
│   └── team_handbook.md       # PR review standards, deployment cadence, on-call
├── src/
│   ├── config.py              # Configuration & hybrid secrets loader
│   ├── scripts_runner.py      # Auto-initialization boot check
│   ├── ingestion/
│   │   ├── loaders.py         # Multi-format document parsers
│   │   └── chunking.py        # RecursiveCharacterTextSplitter logic
│   ├── retrieval/
│   │   ├── vectorstore.py     # ChromaDB & sentence-transformers setup
│   │   └── search.py          # Top-k similarity search
│   ├── agents/
│   │   ├── state.py           # Shared AgentState TypedDict
│   │   ├── router.py          # Query classifier (docs | spreadsheet | general)
│   │   ├── retrieval_node.py  # Vector search retrieval node
│   │   ├── grading_node.py    # Document relevance evaluator
│   │   ├── rewrite_node.py    # Query rewriter for retries
│   │   ├── spreadsheet_node.py# pandas execution node
│   │   ├── synthesis_node.py  # Final answer with citations
│   │   └── graph.py           # LangGraph StateGraph definition
│   └── mcp_server/
│       └── server.py          # Official MCP server implementation
├── scripts/
│   ├── ingest.py              # CLI ingestion pipeline script
│   ├── generate_sample_docs.py# Sample document generator
│   ├── test_rag_baseline.py   # Baseline RAG verification test
│   ├── test_graph.py          # LangGraph agent verification test
│   └── test_mcp_server.py     # MCP server tool verification test
└── tests/
    └── test_eval_set.py       # 13 benchmark evaluation tests (pytest)
```

---

## ⚙️ Quickstart (Local Run)

### 1. Clone & Set Up Environment
```bash
git clone <your-repo-url>
cd docu-mind

# Create and activate Python 3.11 virtual environment
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file in the project root:
```ini
GROQ_API_KEY=gsk_your_groq_api_key_here
```
*(Get a free key at [console.groq.com](https://console.groq.com). No credit card required.)*

### 3. Run Ingestion (Optional — auto-initializes on startup)
```bash
python scripts/ingest.py
```

### 4. Launch the Streamlit App
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

### 5. Run Evaluation Suite
```bash
pytest tests/
```

---

## 🔌 Running the MCP Server
To expose DocuMind's search and spreadsheet tools to any MCP client (Claude Desktop, Antigravity, Cursor):

```bash
python src/mcp_server/server.py
```

To test MCP tool listing and execution programmatically:
```bash
python scripts/test_mcp_server.py
```

---

## 🌐 Deploying to Streamlit Community Cloud ($0 Free)

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: initial commit of DocuMind document intelligence assistant"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and click **New app**.
3. Select your repository, branch (`main`), and set **Main file path** to `app.py`.
4. Under **Advanced settings** -> **Secrets**, paste your Groq API key:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_key_here"
   ```
5. Click **Deploy**. On the first run, DocuMind will automatically ingest `sample_docs/` into ChromaDB and start serving answers immediately!

---

## 💡 Production Context: Document Migration & Semantic Search
DocuMind reflects enterprise document migration architectures. When migrating unstructured legacy drives (PDFs, presentations, Excel spreadsheets, confluence pages) into vector search systems, linear RAG fails due to ambiguous queries and numerical inaccuracy. By combining **intent classification**, **self-correcting verification loops**, and **code execution for structured data**, DocuMind demonstrates production-grade document intelligence without costly proprietary infrastructure.
