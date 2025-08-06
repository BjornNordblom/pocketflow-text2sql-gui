import os

DB_PATH = os.getenv("DB_PATH", "example.db")
MAX_DEBUG_ATTEMPTS = int(os.getenv("MAX_DEBUG_ATTEMPTS", "3"))
