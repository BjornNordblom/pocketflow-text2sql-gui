Backend – FastAPI Text-to-SQL Service

Run (dev)
- Cross-platform: python tools/run_dev.py
- Unix: ./backend/main.sh

Endpoints
- GET /health
- POST /query (see repo README for payload/response schema)

Lint
- Whole project: python tools/lint_all.py
- Backend-only: ruff check backend

Tests
- pytest -q backend/tests

Settings
- DB_PATH (env), MAX_DEBUG_ATTEMPTS (env)
- Per-request overrides via QueryRequest fields; include_schema to echo schema.

Flow
- GetSchema → GenerateSQL → ExecuteSQL; on error → DebugSQL → ExecuteSQL loop.
- LLM call via backend/deps.py:call_llm (currently NotImplementedError).
