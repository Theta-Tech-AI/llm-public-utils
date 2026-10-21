---
name: deslop-data-layer-index-defeaters
description: Deslop principle — Know What Defeats an Index: Leading wildcards, functions on columns, type mismatches.
---

# Know What Defeats an Index

Most "why is this slow" is a predicate written so the index *can't* be used. The recurring ones:

- **Leading wildcard** — `LIKE '%term%'` cannot use a B-tree; use a `pg_trgm` GIN index (or full-text search).
- **A function or cast on the indexed column** — `WHERE lower(email) = ?` or `WHERE created_at::date = ?` ignores a plain index on the bare column. Index the expression, or rewrite the predicate to leave the column bare (`created_at >= ? AND created_at < ?`).
- **Implicit type mismatch** — comparing a `uuid` to a text literal, or `bigint` to `numeric`, can force a cast that skips the index.
- **Low selectivity** — indexing a boolean, or a status that's 90% one value, rarely helps; a partial index on the rare value does.

The arbiter is `EXPLAIN (ANALYZE, BUFFERS)` on the real query at real data volume: a `Seq Scan` where you expected an `Index Scan` is the bug. "Fast on my 100-row dev table" proves nothing — a sequential scan of 100 rows is instant and of 100 million is an outage.

---

In relation to other principles, index defeaters:

| Principle | Relationship |
|-----------|--------------|
| [**Match the Index to the Query Shape**](index-query-shape.md) | Defeaters are predicates written so the index can't be used |
| [**Every Index Is Used or It's Dropped**](unused-indexes.md) | `EXPLAIN` is the arbiter for both |
