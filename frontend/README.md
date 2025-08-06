Text-to-SQL Minimal Web Client

Usage
1) Start backend:
   uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
2) Open frontend/index.html directly in your browser, or serve statically:
   python -m http.server -d frontend 8080
3) Enter the backend base URL (default http://localhost:8000), type a natural language query, and click Run Query.

Notes
- No build tools, pure HTML/CSS/JS.
- Supports overriding db_path, max_debug_attempts, include_schema flags.
- Displays raw JSON response to keep UI minimal.
- Health check button verifies connectivity.

That’s it—no external dependencies or frameworks are introduced.
