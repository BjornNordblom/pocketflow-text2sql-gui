import os
from typing import Optional

DB_PATH = os.getenv("DB_PATH", "ecommerce.db")
MAX_DEBUG_ATTEMPTS = int(os.getenv("MAX_DEBUG_ATTEMPTS", "3"))

OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-coder")
