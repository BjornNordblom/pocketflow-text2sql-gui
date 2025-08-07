# Text-to-SQL (PocketFlow-style) – Backend + Minimal Frontend

Overview
- Backend: FastAPI service implementing a PocketFlow-style Node/Flow pipeline to generate, execute, and auto-debug SQL via an LLM hook.
- Frontend: Minimal HTML/CSS/JS client (no build tools).
- Cross-platform tooling: Python scripts to run the dev server and lint both backend and frontend on Windows/macOS/Linux.

Project layout
- backend/: FastAPI app (app.py), flow nodes (flow_nodes.py), DB adapters (db_adapters.py), models, settings, tests
- frontend/: Static client (index.html, app.js, style.css)
- tools/: Cross-platform helpers (lint_all.py, run_dev.py)
- flow.py: Convenience factory to create the text-to-SQL flow for scripts
- lint_all.sh: Unix convenience wrapper around tools/lint_all.py
- main.py, nodes.py, utils/: Standalone script/demo using a PocketFlow package (separate from backend)

Requirements

Backend
- Python 3.11+ recommended
- Install: pip install -r backend/requirements.txt
- For tests: pip install -r backend/requirements-test.txt
- sqlite3 is part of the Python stdlib in most environments.

Frontend
- Modern browser
- Node.js only needed for ESLint (linting)

LLM dependency
- backend/deps.py implements call_llm(prompt: str) using OpenRouter /v1/completions. App startup requires OPENROUTER_API_KEY; otherwise the server fails fast.
- OPENROUTER_MODEL defaults to "qwen/qwen3-coder" (see backend/settings.py).

Run the backend (dev)

Option A (cross-platform, recommended)
- python tools/run_dev.py

Option B (Unix)
- ./backend/main.sh

Starts:
- uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

Scripted usage
- For a simple script demo outside FastAPI, see flow.py (create_text_to_sql_flow) and main.py. Note: nodes.py/utils.call_llm.py illustrate a PocketFlow-based variant separate from the backend’s built-in flow.

API Endpoints
- GET /health → { status: "ok", db_url }
- GET /schema → returns { ok, db_url, schema, has_tables, db_path }. Query params: db_path or db_url (optional; falls back to server default). Note: db_path is a deprecated alias in the response.
- POST /query → QueryResponse
  Body (QueryRequest):
    - natural_query: string (required)
    - max_debug_attempts: int [0..10] (optional; defaults from settings)
    - db_path: string (optional) or db_url: string (optional)
    - include_schema: bool (optional)
  Response (QueryResponse):
    - ok: bool
    - result: list | null
    - error: string | null
    - generated_sql: string | null
    - attempts: int | null
    - schema: string | null
    - db_url: string | null

Text-to-SQL flow
- Backend flow (backend/flow_nodes.py): GetSchema → GenerateSQL → ExecuteSQL, with error branch ExecuteSQL -"error_retry" → DebugSQL → ExecuteSQL.
- Shared state keys include: schema, generated_sql, debug_attempts, final_result/final_error.
Use build_text_to_sql_flow() and run_text_to_sql() in backend/flow_nodes.py.

Database adapters & URLs
- backend/db_adapters.py provides a pluggable DBAdapter protocol and registry (register, get_adapter_for).
- normalize_to_url accepts a filesystem path or URL and returns a normalized URL.
- SQLiteAdapter is built-in (schemes: sqlite, file). Implement get_schema(url) and execute(url, sql) to add more databases.
- Both GET /schema and POST /query accept db_path or db_url; the server normalizes and routes to the correct adapter.

Run the frontend
- Open frontend/index.html directly in your browser, or serve statically:
  - python -m http.server -d frontend 8080
- Default API base: http://localhost:8000
- UI lets you set db_path, max_debug_attempts, include_schema and shows raw JSON responses.
- Schema button calls GET /schema with db_path when provided.
- Run Query posts to /query. Responses are displayed as raw JSON.
- Default API base: http://localhost:8000 (configurable in the UI).

Linting (cross-platform)
Option A (cross-platform)
- python tools/lint_all.py
- Auto-fix where supported: python tools/lint_all.py --fix

Option B (Unix)
- ./lint_all.sh
- ./lint_all.sh --fix

Under the hood
- Backend lint: ruff check backend
- Frontend lint: npx eslint "frontend/**/*.js"
- Requires: Ruff (pip install ruff) and Node.js for ESLint

Testing
- Run backend tests: pytest -q backend/tests
- Test coverage includes: health check, schema endpoint (SQLite), success path, auto-debug loop, debug-exhaustion, not-implemented LLM (via mocks).

Configuration
- backend/settings.py
  - DB_PATH: default "ecommerce.db" (override via env DB_PATH)
  - MAX_DEBUG_ATTEMPTS: default 3 (override via env MAX_DEBUG_ATTEMPTS)
  - OPENROUTER_API_KEY: required at startup to enable LLM calls
  - OPENROUTER_MODEL: default "qwen/qwen3-coder"

LLM integration
- Implement backend/deps.py:call_llm(prompt: str) with your provider (e.g., OpenAI).
- Once implemented, the flow generates SQL, executes it, and auto-debug retries on SQLite errors.

Security notes
- Demo only: consider parameterized queries, table/column whitelists, and strict output validation in production.
