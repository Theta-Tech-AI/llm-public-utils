---
name: deslop-data-layer-slop-tells
description: Deslop principle — The Common Slop Tells: Grep-able schema smells, each mapping to a principle above.
---

# The Common Slop Tells

> *These are the patterns a generator emitting one `CREATE TABLE` at a time produces by default. Each table looks complete in isolation — but integrity lives **between** tables (a foreign key is a relationship, a normalized fact has one home, an invariant spans rows), and a per-table view never sees it. So the very things that make a schema trustworthy are what get dropped first. Grep for these; each maps to a principle above.*

- **`uuid NOT NULL` named `*_id` / `*_by` with no `REFERENCES`** — the number-one tell: a reference the database doesn't enforce. If a sibling table references the same parent correctly, it wasn't a judgment call, it was forgotten.
- **`status text` / `*_type text` with no `CHECK`** — a closed vocabulary the app "knows" and the schema doesn't. A partial index that hardcodes `WHERE status IN (...)` is proof the vocabulary exists and isn't enforced.
- **`updated_at = now()` written inside an `UPDATE`** — timestamp logic that belongs in a `BEFORE UPDATE` trigger. Grep finds both the statements that forgot it (stale) and the ones redundant with a trigger that's already there.
- **Two columns for one fact** — `status` + `stage`, a JSON blob plus scalar columns projected out of it, a "current" snapshot beside a versions table. A `# kept in sync by the app` comment is the confession.
- **A stored `*_count` / `total_*`** — a value the app maintains where a `COUNT(*)`, a view, or a `GENERATED ALWAYS AS` column is the actual source of truth. Doubly wrong when stored immutably (it can never be corrected).
- **`SELECT max(seq) + 1` then `INSERT`** — an ordering the database should generate; it races behind its own unique index and surfaces as a random 500.
- **`SELECT …; if not found: INSERT`** — a uniqueness check that should be a `UNIQUE` constraint plus `ON CONFLICT`.
- **A multi-statement cascade in application code** — several `DELETE`s in a loop standing in for the `ON DELETE CASCADE` the schema never declared.
- **An "append-only" table with no block-mutation trigger** — immutability as a convention, not an enforced rule; and its dangerous cousin, a trigger guarded by `IF pg_trigger_depth() = 0` (never true inside a trigger body — a silent no-op that *looks* installed).
- **A foreign key with no index** — Postgres indexes primary keys and unique constraints, not FKs; the parent delete and every join quietly go sequential.
