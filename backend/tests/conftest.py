from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from backend.app import app

# Ensure backend is importable when running tests from non-root
try:
    REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
except Exception:
    pass


@pytest.fixture
def client():
    return TestClient(app)


# New fixture returning the desired SQLite URL
@pytest.fixture
def ecommerce_db_path() -> str:
    # Ensure tests use a URL, not a plain path
    return "sqlite://./ecommerce.db"
