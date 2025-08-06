import os
import json
from backend.tests.utils import llm_generate_sql

def test_query_success(client, simple_db_path, monkeypatch):
    # Patch env DB_PATH so default is our temp DB unless request overrides
    monkeypatch.setenv("DB_PATH", simple_db_path)

    # Patch LLM
    from backend import deps
    monkeypatch.setattr(deps, "call_llm", llm_generate_sql)

    payload = {
        "natural_query": "Show total sales for June 2025",
        # rely on env DB_PATH
    }
    res = client.post("/query", json=payload)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["ok"] is True
    # 100 + 50.5 + 25.0 = 175.5
    assert body["result"] in ([[175.5]], [(175.5,)], [[175.5,]], [[{"SUM(amount)": 175.5}]]) or body["result"][0][0] == 175.5
    assert "generated_sql" in body
    assert body["error"] is None
