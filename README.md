# Text-to-SQL (PocketFlow-style) – Backend + Minimal Frontend

Overview
- Backend: FastAPI service implementing a PocketFlow-style Node/Flow pipeline to generate, execute, and auto-debug SQL via an LLM hook.
- Frontend: Minimal HTML/CSS/JS client (no build tools).
- Cross-platform tooling: Python scripts to run the dev server and lint both backend and frontend on Windows/macOS/Linux.

Project layout
- backend/: FastAPI app, flow nodes, models, settings, tests
- frontend/: Static client (index.html, app.js, style.css)
- tools/: Cross-platform helpers (lint_all.py, run_dev.py)
- lint_all.sh: Unix convenience wrapper around tools/lint_all.py

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
- backend/deps.py defines call_llm(prompt: str) and currently raises NotImplementedError.
- Until implemented, POST /query returns HTTP 501.

Run the backend (dev)

Option A (cross-platform, recommended)
- python tools/run_dev.py

Option B (Unix)
- ./backend/main.sh

Starts:
- uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

API Endpoints
- GET /health → {"status":"ok"}
- POST /query → QueryResponse
  Body (QueryRequest):
    - natural_query: string (required)
    - max_debug_attempts: int [0..10] (optional; defaults from settings or request)
    - db_path: string (optional; defaults from settings)
    - include_schema: bool (optional; include DB schema in response)

Text-to-SQL flow
- GetSchema → GenerateSQL → ExecuteSQL; on SQL error: DebugSQL → ExecuteSQL loop until success or attempts exhausted.
- Shared state includes: schema, generated_sql, debug_attempts, final_result/final_error.

Run the frontend
- Open frontend/index.html directly in your browser, or serve statically:
  - python -m http.server -d frontend 8080
- Default API base: http://localhost:8000
- UI lets you set db_path, max_debug_attempts, include_schema and shows raw JSON responses.

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
- Test coverage includes: health check, success path, auto-debug loop, debug-exhaustion, not-implemented LLM.

Configuration
- backend/settings.py
  - DB_PATH: default "example.db" (override via env DB_PATH)
  - MAX_DEBUG_ATTEMPTS: default 3 (override via env MAX_DEBUG_ATTEMPTS)
- Request-level overrides: QueryRequest.db_path and QueryRequest.max_debug_attempts; include_schema toggles schema echo.

LLM integration
- Implement backend/deps.py:call_llm(prompt: str) with your provider (e.g., OpenAI).
- Once implemented, the flow generates SQL, executes it, and auto-debug retries on SQLite errors.

Security notes
- Demo only: consider parameterized queries, table/column whitelists, and strict output validation in production.
