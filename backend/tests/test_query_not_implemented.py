def test_query_not_implemented(client, ecommerce_db_path, monkeypatch):
    # We do NOT patch deps.call_llm here to simulate default NotImplementedError
    monkeypatch.setenv("DB_PATH", ecommerce_db_path)

    payload = {"natural_query": "anything"}
    res = client.post("/query", json=payload)
    assert res.status_code == 501
    body = res.json()
    assert "not implemented" in body["detail"].lower()
