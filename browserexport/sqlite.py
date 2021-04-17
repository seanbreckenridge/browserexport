import sqlite3

from typing import Iterator

from .common import expand_path, PathIshOrConn


def _execute_conn(conn: sqlite3.Connection, query: str) -> Iterator[sqlite3.Row]:
    """
    Given an open sqlite3 connection, execute a query
    """
    conn.row_factory = sqlite3.Row
    conn.text_factory = lambda b: b.decode(errors="ignore")
    for row in conn.execute(query):
        yield row


def _execute_query(sqlite_path: PathIshOrConn, query: str) -> Iterator[sqlite3.Row]:
    """
    Given a str, path, or sqlite3 connection, execute a query
    """
    if isinstance(sqlite_path, sqlite3.Connection):
        # WARNING: if this happens but you're yielding lazily from a function
        # the connection might close before this query finishes executing
        yield from _execute_conn(sqlite_path, query)
    else:
        p: str = str(expand_path(sqlite_path))
        with sqlite3.connect(f"file:{p}?immutable=1", uri=True) as c:
            yield from _execute_conn(c, query)
