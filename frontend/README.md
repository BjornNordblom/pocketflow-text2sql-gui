Text-to-SQL Minimal Web Client

Usage
1) Start backend (cross-platform):
   python tools/run_dev.py
   Or on Unix:
   ./backend/main.sh
2) Open the client:
   - Open frontend/index.html directly in your browser, or
   - Serve statically: python -m http.server -d frontend 8080
3) Use the UI:
   - API Base URL defaults to http://localhost:8000
   - Enter Natural Language Query
   - Optional: db_path, max_debug_attempts, include_schema

Notes
- No build tools; pure HTML/CSS/JS.
- Lint the whole project:
   python tools/lint_all.py
   python tools/lint_all.py --fix
- Frontend lint requires Node.js (ESLint); backend lint uses Ruff.
