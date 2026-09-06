import os
import queue
import threading
from contextlib import contextmanager
from typing import Iterator

import pyodbc

"""
Connection pooling notes (Part C - production readiness):

- No connection string or credentials are hardcoded anywhere in source.
  Locally, values come from local.settings.json (git-ignored) which maps to
  os.environ.* when running via `func start`. In Azure, the same variable
  names are set as Application Settings, and in production should be
  configured as Key Vault references rather than plain values.

- Unlike Node's `mssql` package, pyodbc has no built-in pool, and a single
  shared pyodbc connection is NOT safe to use across concurrent threads.
  The Azure Functions Python host can run multiple invocations concurrently
  in the same worker process, so this module keeps a small fixed-size pool
  of connections in a thread-safe queue.Queue and hands one out per request
  via a `with get_connection() as conn:` context manager, returning it to
  the pool afterwards - avoiding a fresh TCP+TLS handshake on every call
  while staying safe under concurrency.
"""

_POOL_SIZE = int(os.environ.get("SQL_POOL_SIZE", "5"))
_pool: "queue.Queue[pyodbc.Connection]" = queue.Queue(maxsize=_POOL_SIZE)
_pool_lock = threading.Lock()
_initialized = False


def _build_connection_string() -> str:
    server = os.environ.get("SQL_SERVER")
    database = os.environ.get("SQL_DATABASE")
    user = os.environ.get("SQL_USER")
    password = os.environ.get("SQL_PASSWORD")
    driver = os.environ.get("SQL_DRIVER", "{ODBC Driver 18 for SQL Server}")
    encrypt = os.environ.get("SQL_ENCRYPT", "yes")

    if not all([server, database, user, password]):
        raise RuntimeError(
            "Missing SQL configuration. Ensure SQL_SERVER, SQL_DATABASE, SQL_USER "
            "and SQL_PASSWORD are set as environment variables / Application Settings."
        )

    return (
        f"DRIVER={driver};SERVER={server};DATABASE={database};"
        f"UID={user};PWD={password};Encrypt={encrypt};TrustServerCertificate=no;"
    )


def _create_connection() -> pyodbc.Connection:
    return pyodbc.connect(_build_connection_string(), autocommit=True)


def _initialize_pool() -> None:
    global _initialized
    if _initialized:
        return
    with _pool_lock:
        if _initialized:  # re-check inside the lock
            return
        for _ in range(_POOL_SIZE):
            _pool.put(_create_connection())
        _initialized = True


@contextmanager
def get_connection() -> Iterator[pyodbc.Connection]:
    """Borrow a pooled connection, revalidating it, and always return it."""
    _initialize_pool()
    conn = _pool.get()
    try:
        conn.cursor().execute("SELECT 1")
    except pyodbc.Error:
        conn = _create_connection()
    try:
        yield conn
    finally:
        _pool.put(conn)
