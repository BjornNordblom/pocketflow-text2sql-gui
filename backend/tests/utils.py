from __future__ import annotations

def llm_generate_sql(prompt: str) -> str:
    # Simple heuristic to produce SQL for our seeded schema.
    # If asked for total sales for June 2025, sum amounts from orders in June 2025.
    lower = prompt.lower()
    if "failed sql" in lower and "error" in lower:
        # Debug path: fix known mistakes by returning a correct query
        return "SELECT SUM(amount) FROM orders WHERE strftime('%Y-%m', created_at) = '2025-06';"
    if "total" in lower or "sum" in lower:
        return "SELECT SUM(amount) FROM orders WHERE strftime('%Y-%m', created_at) = '2025-06';"
    # Default: select all
    return "SELECT * FROM orders;"

def llm_generate_bad_then_fix(prompt: str) -> str:
    # First attempt returns bad SQL (to trigger debug), second attempt returns fixed SQL.
    # We use a counter embedded in the prompt to decide, but since we don't have shared state,
    # we'll deliberately return a bad table name if it's the initial generation prompt.
    lower = prompt.lower()
    if "failed sql" in lower:
        # Debug round
        return "SELECT SUM(amount) FROM orders WHERE strftime('%Y-%m', created_at) = '2025-06';"
    # Initial generation
    return "SELECT SUM(amount) FROM orderz WHERE strftime('%Y-%m', created_at) = '2025-06';"
