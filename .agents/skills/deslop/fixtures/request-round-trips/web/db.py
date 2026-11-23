"""The one place a statement is sent. The database runs on its own host, behind a connection pooler."""
from typing import Any

Row = dict[str, Any]


def rows(conn: Any, sql: str, params: tuple = ()) -> list[Row]:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def one(conn: Any, sql: str, params: tuple = ()) -> Row | None:
    found = rows(conn, sql, params)
    return found[0] if found else None


def execute(conn: Any, sql: str, params: tuple = ()) -> None:
    with conn.cursor() as cur:
        cur.execute(sql, params)
