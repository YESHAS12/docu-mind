# Project Brief for Antigravity Agent: "DocuMind" — Multi-Agent Document Intelligence Assistant

> **Instructions for the agent reading this file:** This is a complete, self-contained specification. Do not ask clarifying questions about scope, tech stack, or architecture — every decision has already been made below to keep this unambiguous. If you hit a genuine blocker (e.g. a missing API key), stop and ask only for that specific missing item. Work through the phases in order. After each phase, run and verify before moving to the next. Use Plan Mode to generate an implementation plan first, then execute.

---

## 0. Prerequisites (the human has already done these — do not attempt to sign up for accounts yourself)

Before this task starts, the human will have:
1. Created a free Groq account at console.groq.com and generated an API key.
2. Created a free GitHub account (if not already) — this is where the source repo will live.
3. Created a free Streamlit Community Cloud account at share.streamlit.io, signed in via GitHub — this is the deployment target (see note below on why, replacing an earlier Hugging Face Spaces plan).
4. The Groq API key will be provided to you directly in chat/terminal when you reach a step that needs it — **never write the raw key into any file in this repo, including this brief, README.md, or any config file. It belongs only in a local, git-ignored `.env` file and in Streamlit Community Cloud's "Secrets" panel at deploy time.**

> **Note on hosting choice:** Hugging Face Spaces changed its free tier — Gradio and Docker Spaces (which a Python/Streamlit backend needs) now require a paid plan; only static HTML Spaces remain free, which doesn't work for this app. **Streamlit Community Cloud (share.streamlit.io) is the replacement — it remains fully free for public apps and deploys directly from a GitHub repo.** All references to "Hugging Face Spaces" elsewhere in this brief should be read as "Streamlit Community Cloud." A Hugging Face account/token is not needed anywhere in this project.

If the Groq key is missing when you reach a step that needs it, stop and ask for exactly that item, then continue.

## 0a. Local project location

Create and work out of this exact folder (already exists, empty, on the Desktop):

```
~/Desktop/docu-mind-agent
```

(On Windows this is `C:\Users\<username>\Desktop\docu-mind-agent`; on macOS/Linux `~/Desktop/docu-mind-agent`.) Everything in Section 4's repo structure goes directly inside this folder — this folder itself is the git repo root.

---

## 1. Objective

Build and deploy **DocuMind**: a document-question-answering agent that:
- Ingests a folder of mixed documents (PDF, PPTX, XLSX, TXT/MD).
- Lets a user ask natural-language questions in a chat UI and get grounded answers with source citations.
- Uses a **LangGraph** state machine (not a single linear chain) with a router, a retrieval step, a self-correcting retrieval-grading/retry loop, and a spreadsheet-aware calculation path.
- Is exposed as an **MCP server** so its tools are callable from any MCP-compatible client.
- Is deployed publicly, for **$0 cost**, on Streamlit Community Cloud, using Groq's free-tier LLM API and a local ChromaDB vector store (no paid database).

**Definition of done:** a public Streamlit Community Cloud URL that a stranger can open, ask a question about the seeded sample documents, and get a correct, cited answer — with the full source code in a GitHub repo.

---

## 2. Hard constraints

- **Zero cost, end to end.** Every service used must have a free tier sufficient for a personal demo: Groq (free LLM API), ChromaDB (runs in-process, no hosted DB), Streamlit Community Cloud (free public app hosting), GitHub (free).
- **Python only**, 3.11+.
- **No paid API keys anywhere** — if you're tempted to reach for OpenAI/Anthropic/Pinecone, stop and use the free alternative specified below instead.
- **Never commit secrets.** API keys go in a `.env` file (git-ignored locally) and in Streamlit Community Cloud's "Secrets" settings for deployment — never in code, never in git history.
- The final app must run **both locally and on Streamlit Community Cloud** without code changes (read all secrets from environment variables).

---

## 3. Tech stack (fixed — do not substitute)

| Layer | Choice |
|---|---|
| LLM | Groq API, model `llama-3.3-70b-versatile` (free tier) |
| Agent orchestration | LangGraph (`langgraph`) |
| LLM framework | LangChain (`langchain`, `langchain-groq`) |
| Vector store | ChromaDB (`chromadb`), local persistent directory, no hosted service |
| Embeddings | A free local sentence-transformers model via `langchain-huggingface` (e.g. `sentence-transformers/all-MiniLM-L6-v2`) — **do not use a paid embeddings API** |
| Document loaders | `pypdf` (PDF), `python-pptx` (PPTX), `openpyxl` (XLSX), plain file read (TXT/MD) |
| Spreadsheet math | `pandas` |
| UI | Streamlit (`streamlit`) |
| MCP server | official `mcp` Python SDK |
| Hosting | Streamlit Community Cloud (share.streamlit.io), free tier |
| Env management | `python-dotenv` |

---

## 4. Repository structure to create

```
docu-mind-agent/
├── app.py                     # Streamlit entrypoint (chat UI) — this is what HF Spaces runs
├── requirements.txt
├── .env.example                # documents required env vars, no real secrets
├── .gitignore                  # must include .env, __pycache__/, chroma_db/, *.pyc
├── README.md                   # setup, architecture diagram, live demo link, screenshots
├── sample_docs/                # 4-6 seed documents so the public demo has something to query
│   ├── (a couple of small PDFs, a PPTX, an XLSX, a markdown file — placeholder/sample content is fine)
├── src/
│   ├── __init__.py
│   ├── config.py               # loads env vars via python-dotenv, central place for constants
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loaders.py          # one function per file type -> list[Document]
│   │   └── chunking.py         # RecursiveCharacterTextSplitter wrapper
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vectorstore.py      # build/load Chroma collection, embedding model setup
│   │   └── search.py           # top-k semantic search function
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── state.py            # TypedDict/State schema shared across the LangGraph graph
│   │   ├── router.py           # classifies query -> "docs" | "spreadsheet" | "general"
│   │   ├── retrieval_node.py   # runs semantic search, populates state
│   │   ├── grading_node.py     # LLM call: "do these chunks answer the question?" -> bool
│   │   ├── rewrite_node.py     # LLM call: reformulate the query for a retry
│   │   ├── spreadsheet_node.py # pandas-based Q&A over ingested XLSX data
│   │   ├── synthesis_node.py   # final answer + citations
│   │   └── graph.py            # builds and compiles the LangGraph StateGraph, wires all nodes/edges + the retry loop
│   └── mcp_server/
│       ├── __init__.py
│       └── server.py           # exposes search_docs, summarize_sheet as MCP tools
├── scripts/
│   └── ingest.py                # one-off CLI script: run ingestion pipeline over sample_docs/ into chroma_db/
└── tests/
    └── test_eval_set.py         # 10-15 hardcoded Q&A pairs against sample_docs/, asserts retrieval finds relevant chunks
```

---

## 5. Build phases — execute in order, verify after each

### Phase 1 — Scaffold and environment
1. Create the repo structure above (empty files where noted).
2. Write `requirements.txt`:
   ```
   langgraph
   langchain
   langchain-groq
   langchain-huggingface
   langchain-community
   chromadb
   sentence-transformers
   pypdf
   python-pptx
   openpyxl
   pandas
   streamlit
   python-dotenv
   mcp
   ```
3. Write `.env.example`:
   ```
   GROQ_API_KEY=your_groq_key_here
   ```
4. Write `.gitignore` excluding `.env`, `__pycache__/`, `chroma_db/`, `.venv/`, `*.pyc`.
5. Set up a virtual environment and `pip install -r requirements.txt`. Confirm it installs cleanly with no errors.
6. **Verify:** running `python -c "import langgraph, chromadb, langchain_groq"` succeeds with no import errors.

### Phase 2 — Sample corpus + ingestion pipeline
1. Populate `sample_docs/` with a handful of realistic small files (a couple of short PDFs with generated placeholder text, a small PPTX, a small XLSX with a couple of numeric columns, one markdown file). These exist purely so the public demo has content to answer questions about.
2. Implement `src/ingestion/loaders.py`: one function per file type that returns a list of LangChain `Document` objects with `metadata={"source": filename, "type": filetype}`.
3. Implement `src/ingestion/chunking.py` using `RecursiveCharacterTextSplitter` (chunk_size ~700, overlap ~100).
4. Implement `src/retrieval/vectorstore.py`: builds a persistent Chroma collection at `./chroma_db` using the local `sentence-transformers/all-MiniLM-L6-v2` embedding model.
5. Implement `scripts/ingest.py`: loads every file in `sample_docs/`, chunks, embeds, and writes to the Chroma store. Runnable via `python scripts/ingest.py`.
6. **Verify:** run `scripts/ingest.py`, confirm `chroma_db/` is created and populated, and write a tiny throwaway test that queries it and prints results with reasonable relevance.

### Phase 3 — Baseline RAG (no agent yet)
1. Implement `src/retrieval/search.py`: given a query string, returns top-k chunks with metadata.
2. Wire a minimal script (temporary, can live in `scripts/`) that does: query → retrieve → stuff into a prompt → call Groq via `langchain-groq` → print answer with cited filenames.
3. **Verify:** ask 3-4 manual questions about the sample docs and confirm answers are grounded and cite the right source files.

### Phase 4 — LangGraph agent with retry loop
1. Implement `src/agents/state.py`: a `TypedDict` with fields like `query`, `route`, `retrieved_docs`, `is_relevant`, `rewritten_query`, `retry_count`, `answer`.
2. Implement `src/agents/router.py`: LLM call classifying the query into `docs`, `spreadsheet`, or `general`.
3. Implement `src/agents/retrieval_node.py`: calls `search.py`, populates `retrieved_docs`.
4. Implement `src/agents/grading_node.py`: LLM call returning whether `retrieved_docs` actually answer `query` (boolean/structured output).
5. Implement `src/agents/rewrite_node.py`: LLM call producing a reformulated query when grading fails.
6. Implement `src/agents/spreadsheet_node.py`: loads ingested XLSX data into a pandas DataFrame and answers numeric questions directly (not by asking the LLM to "read" numbers from retrieved text).
7. Implement `src/agents/synthesis_node.py`: produces the final answer with source citations.
8. Implement `src/agents/graph.py`: builds the `StateGraph`, wires nodes and conditional edges — specifically: `router → (retrieval_node | spreadsheet_node | synthesis_node)`, and after `retrieval_node → grading_node`, with a conditional edge that goes to `synthesis_node` if relevant, or `rewrite_node → retrieval_node` (capped at 2 retries via `retry_count` to avoid infinite loops) if not.
9. **Verify:** run the compiled graph against 5-6 test questions, including at least one that should trigger the retry loop (an intentionally vague or oddly-phrased question) and one spreadsheet-numeric question. Confirm the loop actually re-queries and eventually terminates.

### Phase 5 — MCP server
1. Implement `src/mcp_server/server.py` using the official `mcp` Python SDK, exposing `search_docs(query: str)` and `summarize_sheet(filename: str)` as MCP tools that call into the existing `retrieval` and `spreadsheet_node` logic.
2. **Verify:** run the MCP server locally and confirm it starts without error and responds to a tool-list request. (Full external MCP-client testing is a stretch goal — a working, correctly-structured server that starts cleanly is sufficient for Definition of Done.)

### Phase 6 — Streamlit UI (`app.py`)
1. Build a chat interface: message history, input box, "thinking" indicator while the graph runs.
2. On startup, check whether `chroma_db/` exists; if not, run the ingestion pipeline automatically against `sample_docs/` (so a fresh deploy self-initializes with no manual step).
3. Display the final answer plus a small "Sources" expander listing cited filenames.
4. Add a lightweight sidebar stats panel: total queries this session, average retry-loop count — a small nod to usage/engagement tracking.
5. Read `GROQ_API_KEY` from `st.secrets` when running on Streamlit Community Cloud, falling back to `os.environ` (via `python-dotenv`) when running locally. Do not hardcode a key anywhere.
6. **Verify:** `streamlit run app.py` locally, ask several questions through the UI, confirm citations render correctly and the app doesn't crash on an off-topic or nonsense question (should gracefully say it can't find an answer, not error out).

### Phase 7 — Guardrails and eval
1. Add basic input handling: cap input length, strip/ignore obvious prompt-injection attempts (e.g. "ignore previous instructions"), and add a simple per-session query counter to avoid runaway API usage on the free tier.
2. Write `tests/test_eval_set.py`: 10-15 hardcoded Q&A pairs against `sample_docs/` content, asserting the retrieval step returns chunks containing the expected source file. Runnable via `pytest`.
3. **Verify:** `pytest tests/` passes.

### Phase 8 — README and repo polish
1. Write `README.md` covering: what the project is, architecture diagram (ASCII is fine), the retry-loop design decision and why, setup instructions (local run), the live demo link (fill in after Phase 9), and a short "why this relates to production document-migration/semantic-search work" paragraph.
2. Confirm no secrets exist anywhere in git history (`git log -p | grep -i groq` style sanity check) before the first commit.

### Phase 9 — Deploy to Streamlit Community Cloud (free)
1. Initialize git, commit everything except `.env` and `chroma_db/`.
2. Push to a new GitHub repo (ask the human for the repo name/visibility if not already specified) — the repo must be public, or at least accessible to Streamlit Community Cloud via the human's connected GitHub account.
3. Direct the human to share.streamlit.io (they'll already be signed in via GitHub from the Prerequisites step): click "New app", select the repo, branch (`main`), and main file path (`app.py`), then deploy. This step happens in the Streamlit Cloud UI — you cannot do it programmatically, so hand it back to the human here if you've been running autonomously.
4. In the app's Settings → "Secrets" (in the Streamlit Cloud dashboard), add:
   ```
   GROQ_API_KEY = "the_actual_key"
   ```
   The human pastes the real value directly into that UI — you do not need to see or handle the raw key.
5. Confirm the app builds successfully (check the deploy logs in the Streamlit Cloud dashboard) and boots without error.
6. **Verify (final Definition of Done check):** open the public `*.streamlit.app` URL in a fresh session, ask a question about the sample documents, and confirm a correct, cited answer comes back. Update `README.md` with the live URL.

---

## 6. What "done" looks like — final checklist

- [ ] Public Streamlit Community Cloud URL loads and answers questions correctly
- [ ] Retry loop demonstrably fires and self-corrects on at least one test query
- [ ] Spreadsheet-numeric questions are answered via pandas, not LLM guessing
- [ ] MCP server starts cleanly and lists its tools
- [ ] `pytest tests/` passes
- [ ] No secrets anywhere in git history or source files
- [ ] README explains the architecture and links the live demo
- [ ] App runs locally with `streamlit run app.py` and on Streamlit Community Cloud with zero code differences

---

## 7. Notes / things to explicitly avoid

- Do not swap in a paid LLM or embeddings API "just to make it easier" — the whole point is a $0 deployable demo.
- Do not skip the retry loop and just ship plain RAG — the self-correcting loop is the specific thing that justifies using LangGraph over a simple LangChain chain, and it's the main technical talking point of this project.
- Do not hardcode or print API keys anywhere, including in logs.
- Keep `sample_docs/` small (a handful of files) — this is a portfolio demo, not a real migration job.
