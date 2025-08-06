import os
import json
from backend.tests.utils import llm_generate_sql

def test_query_success(client, ecommerce_db_path, monkeypatch):
    # Patch env DB_PATH so default is our ecommerce DB unless request overrides
    monkeypatch.setenv("DB_PATH", ecommerce_db_path)

    # Patch LLM
    from backend import deps
    monkeypatch.setattr(deps, "call_llm", llm_generate_sql)

    payload = {
        "natural_query": "Show total sales for June 2025",
        # rely on env DB_PATH
    }
    # Optionally pass db_path explicitly
    payload["db_path"] = ecommerce_db_path

    res = client.post("/query", json=payload)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["ok"] is True
    # We cannot assert exact totals without knowing ecommerce.db contents;
    # keep generic structure assertions.
    assert "generated_sql" in body
    assert body["error"] is None
