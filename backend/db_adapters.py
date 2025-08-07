from __future__ import annotations

import os
import sqlite3
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Protocol, Tuple


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

    Windows: prefer sqlite://C:/path form (no extra leading slash).
    POSIX:   use sqlite:////abs/path form.
    """
    # Already a URL?
    if "://" in db_path_or_url:
        return db_path_or_url
    # Treat as filesystem path; resolve relative paths against server CWD
    p = Path(db_path_or_url).expanduser().resolve()
    # Windows: emit sqlite://C:/path form (no extra leading slash)
    if os.name == "nt":
        drive = p.drive  # like 'C:'
        if drive:
            # Build Windows URI: sqlite://C:/path/to/db
            tail = p.as_posix()[len(drive):].lstrip("/")  # strip 'C:' from start, then any '/'
            return f"sqlite://{drive}/{tail}"
    # POSIX or no drive letter: sqlite:////abs/path
    posix = p.as_posix()
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
        scheme = parts.scheme
        db_file = ""

        if scheme == "file":
            # file:///abs/path or file://localhost/abs/path
            db_file = (parts.netloc + parts.path) if parts.netloc else (parts.path or "")
        else:
            # sqlite scheme; accept both Windows and POSIX forms
            # Windows URI form: sqlite://C:/path/file.db  => netloc='C:', path='/path/file.db'
            # POSIX absolute:   sqlite:////abs/path.db    => netloc='',  path='/abs/path.db'
            # POSIX relative:   sqlite:///rel/path.db     => netloc='',  path='/rel/path.db'
            if os.name == "nt" and parts.netloc and parts.path:
                # Windows drive in netloc
                db_file = f"{parts.netloc}{parts.path}"
            else:
                db_file = parts.path or ""
                if parts.netloc and not db_file:
                    db_file = parts.netloc

        # Normalize:
        # - '/C:/x' -> 'C:/x' (Windows)
        if os.name == "nt" and len(db_file) >= 3 and db_file[0] == "/" and db_file[2] == ":":
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
