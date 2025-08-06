def test_query_debug_exhausted(client, ecommerce_db_path, monkeypatch):
    # LLM always produces bad SQL so debug loop will also produce bad SQL
    from backend import deps

    def always_bad(_prompt: str) -> str:
        return "SELECT * FROM not_a_table;"

    monkeypatch.setenv("DB_PATH", ecommerce_db_path)
    monkeypatch.setattr(deps, "call_llm", always_bad)

    payload = {
        "natural_query": "Try something impossible",
        "max_debug_attempts": 1
    }
    res = client.post("/query", json=payload)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["ok"] is False
    assert body["error"] is not None
    assert body["attempts"] >= 1
