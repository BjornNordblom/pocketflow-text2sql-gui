import os
import sqlite3
import tempfile
import contextlib
import pytest
from fastapi.testclient import TestClient

# Ensure the backend package is importable when running pytest from repo root
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app import app
from backend import settings

@contextlib.contextmanager
def temp_sqlite_with_schema(seed_sql: str | None = None):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        if seed_sql:
            cur.executescript(seed_sql)
        conn.commit()
        conn.close()
        yield path
    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def simple_db_path():
    seed_sql = """
    DROP TABLE IF EXISTS orders;
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer TEXT,
        amount REAL,
        created_at TEXT
    );
    INSERT INTO orders (customer, amount, created_at) VALUES
    ('Alice', 100.0, '2025-06-01'),
    ('Bob',   50.5,  '2025-06-03'),
    ('Alice', 25.0,  '2025-06-15');
    """
    with temp_sqlite_with_schema(seed_sql) as p:
        yield p
