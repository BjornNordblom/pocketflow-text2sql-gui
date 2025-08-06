def test_schema_sqlite_ok(client, ecommerce_db_path):
    res = client.get("/schema", params={"db_path": ecommerce_db_path})
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert isinstance(body["db_url"], str)
    assert isinstance(body["schema"], str)
    assert "has_tables" in body
