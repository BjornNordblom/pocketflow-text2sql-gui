from backend.tests.utils import llm_generate_bad_then_fix

def test_query_autodebug_succeeds(client, simple_db_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", simple_db_path)

    from backend import deps
    monkeypatch.setattr(deps, "call_llm", llm_generate_bad_then_fix)

    payload = {
        "natural_query": "Total sales for June 2025",
        "max_debug_attempts": 2
    }
    res = client.post("/query", json=payload)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["ok"] is True
    assert body["attempts"] >= 1
    assert body["error"] is None
