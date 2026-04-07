"""
iQuery — SQLite metadata database.

Manages three tables:
- documents  : tracks every ingested document (filename, timestamp, chunks, status)
- query_logs : logs every chat query with answer preview and latency
- feedback   : stores user ratings and comments on answers

Uses Python's built-in sqlite3 module — no extra dependencies needed.
"""

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

from app.config import get_settings

# Thread-local storage so each thread gets its own connection
_local = threading.local()


def _get_db_path() -> str:
    return get_settings().db_path


def _init_connection(conn: sqlite3.Connection) -> None:
    """Apply pragmas and create tables if they don't exist."""
    conn.row_factory = sqlite3.Row  # returns dict-like rows
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT    NOT NULL UNIQUE,
            upload_ts   TEXT    NOT NULL,
            chunk_count INTEGER NOT NULL DEFAULT 0,
            status      TEXT    NOT NULL DEFAULT 'indexed'
        );

        CREATE TABLE IF NOT EXISTS query_logs (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            query            TEXT    NOT NULL,
            answer_preview   TEXT,
            chunks_retrieved INTEGER NOT NULL DEFAULT 0,
            latency_s        REAL    NOT NULL DEFAULT 0,
            ts               TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            query    TEXT    NOT NULL,
            answer   TEXT,
            rating   INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            comment  TEXT,
            ts       TEXT    NOT NULL
        );
    """)
    conn.commit()


@contextmanager
def get_db():
    """
    Context manager that yields a live sqlite3.Connection.
    Creates the DB file and tables on first use.
    """
    db_path = _get_db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    _init_connection(conn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
