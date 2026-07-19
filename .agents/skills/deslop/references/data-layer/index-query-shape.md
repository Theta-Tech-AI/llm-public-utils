---
name: deslop-data-layer-index-query-shape
description: Deslop principle — Match the Index to the Query Shape: Composite order, partial, covering, the right index type.
---

# Match the Index to the Query Shape

An index helps only if its shape matches how the query reads. The rules that pay the most rent:

- **Composite order is left-to-right.** An index on `(a, b, c)` serves predicates on `a`, on `a, b`, and on `a, b, c` — but **not** on `b` alone or `c` alone. Lead with the column that's always equality-filtered, then the range/sort column: `WHERE project_id = ? ORDER BY created_at DESC` wants `(project_id, created_at DESC)`, in that order.
- **Partial indexes** for queries that always carry the same filter (`WHERE deleted_at IS NULL`, `WHERE status = 'active'`): the index covers only the live rows — smaller and faster — and a partial `UNIQUE` doubles as a clean "one active row per key" enforcement.
- **Covering indexes** (`INCLUDE (...)`) let an index-only scan answer the query without touching the heap when you select a few extra columns alongside the key.
- **Pick the index type for the data:** B-tree (default) for equality and ranges; **GIN** for `jsonb`, arrays, and full-text; **GiST** for ranges, geometry, and 2-D / bounding-box predicates a B-tree can't answer; **BRIN** for huge, naturally-ordered append-only tables (time-series) where a tiny block-range index beats a giant B-tree.
- **Expression indexes** when you filter on a function of a column: `CREATE INDEX ON users (lower(email))` so `WHERE lower(email) = ?` is indexable.

```sql
-- ✅ Composite ordered for the query, partial to the live rows
CREATE INDEX idx_doc_project_recent ON document (project_id, created_at DESC)
    WHERE deleted_at IS NULL;
```

---

In relation to other principles, matching index to query shape:

| Principle | Relationship |
|-----------|--------------|
| [**Index What You Filter, Join, and Sort On**](index-access-columns.md) | The query set dictates which shapes are needed |
| [**Know What Defeats an Index**](index-defeaters.md) | The right shape only helps if the predicate can use it |
