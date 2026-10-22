"""Planted: the N+1 join, a leading-wildcard search, and an expression predicate with no index."""
from typing import Any


def active_project_documents(conn: Any) -> list:
    out = []
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM project")
        for (pid,) in cur.fetchall():
            cur.execute("SELECT * FROM document WHERE project_id = %s", (pid,))   # N+1
            out.extend(cur.fetchall())
    return out


def by_tag(conn: Any, tag: str) -> list:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM document WHERE tags LIKE %s", (f"%{tag}%",))  # leading wildcard
        return cur.fetchall()


def customer_by_email(conn: Any, email: str) -> list:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM customer WHERE lower(email) = lower(%s)", (email,))   # expression
        return cur.fetchall()
