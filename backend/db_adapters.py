from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Dict, List, Tuple
import urllib.parse
import sqlite3
import os
from pathlib import Path


class DBAdapter(Protocol):
    name: str
    schemes: tuple[str, ...]
    def get_schema(self, url: str) -> str: ...
    def execute(self, url: str, sql: str) -> List[Tuple]: ...


_REGISTRY: Dict[str, DBAdapter] = {}


def register(adapter: DBAdapter) -> None:
    for s in adapter.schemes:
        _REGISTRY[s] = adapter


def parse_scheme(url: str) -> str | None:
    parts = urllib.parse.urlparse(url)
    return parts.scheme or None


def normalize_to_url(db_path_or_url: str) -> str:
    """
    Normalize a legacy filesystem path into a URL.
    If it already looks like a URL (has ://), return as-is.
    Otherwise treat it as a SQLite path.
    """
    # Already a URL?
    if "://" in db_path_or_url:
        return db_path_or_url
    # Treat as filesystem path; resolve relative paths against server CWD
    p = Path(db_path_or_url).expanduser().resolve()
    # Convert to POSIX-style path string (forward slashes)
    posix = p.as_posix()
    # Build absolute sqlite URL: sqlite:////abs/path
    return f"sqlite:////{posix}"


def get_adapter_for(url: str) -> DBAdapter:
    scheme = parse_scheme(url)
    if not scheme:
        raise ValueError(f"Database URL missing scheme: {url}")
    adapter = _REGISTRY.get(scheme)
    if not adapter:
        raise ValueError(f"No adapter registered for scheme '{scheme}'")
    return adapter


@dataclass
class SQLiteAdapter:
    name: str = "sqlite"
    schemes: tuple[str, ...] = ("sqlite", "file")

    def _connect(self, url: str) -> sqlite3.Connection:
        parts = urllib.parse.urlparse(url)
        if parts.scheme == "file":
            # file:///abs/path or file://localhost/abs/path
            netloc = parts.netloc
            path = parts.path or ""
            db_file = f"{netloc}{path}" if netloc else path
        else:
            # sqlite scheme
            db_file = parts.path or ""
            if parts.netloc:
                db_file = f"{parts.netloc}{parts.path}"
        # Windows drive letter fix: '/C:/x' -> 'C:/x'
        if len(db_file) >= 3 and db_file[0] == "/" and db_file[2] == ":":
            db_file = db_file[1:]
        db_file = os.path.normpath(db_file)
        return sqlite3.connect(db_file)

    def get_schema(self, url: str) -> str:
        conn = self._connect(url)
        try:
            cur = conn.cursor()
            cur.execute("SELECT sql FROM sqlite_master WHERE type='table';")
            rows = cur.fetchall()
            schema = "\n".join(row[0] for row in rows if row and row[0])
            return schema
        finally:
            conn.close()

    def execute(self, url: str, sql: str) -> List[Tuple]:
        conn = self._connect(url)
        try:
            cur = conn.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            return data
        finally:
            conn.close()


# Register default adapter
register(SQLiteAdapter())
