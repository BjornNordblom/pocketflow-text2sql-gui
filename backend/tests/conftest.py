import os
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

@pytest.fixture
def client():
    return TestClient(app)

# New fixture returning the desired SQLite URL
@pytest.fixture
def ecommerce_db_path() -> str:
    # Ensure tests use a URL, not a plain path
    return "sqlite://./ecommerce.db"
