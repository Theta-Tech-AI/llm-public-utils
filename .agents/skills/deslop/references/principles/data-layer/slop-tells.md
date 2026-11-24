---
name: deslop-data-layer-slop-tells
description: Deslop principle — The Common Slop Tells: grep-able schema and call-site smells, each mapped to the principle that owns it.
---

# The Common Slop Tells

**Why this is slop:** Reading schemas and callers in isolation misses unenforced relationships, conflicting copies and repeated reads whose costs appear only when the pieces interact.

> *These are the patterns a generator emitting one `CREATE TABLE` at a time produces by default. Each table looks complete in isolation — but integrity lives **between** tables (a foreign key is a relationship, a normalized fact has one home, an invariant spans rows), and a per-table view never sees it. So the very things that make a schema trustworthy are what get dropped first. Grep for these; each maps to a principle above.*

- **`uuid NOT NULL` named `*_id` / `*_by` with no `REFERENCES`** — the number-one tell: a reference the database doesn't enforce. If a sibling table references the same parent correctly, it wasn't a judgment call, it was forgotten.
- **`status text` / `*_type text` with no `CHECK`** — a closed vocabulary the app "knows" and the schema doesn't ([vocabulary drift](../../patterns/vocabulary-drift.md)).
- **`updated_at = now()` written inside an `UPDATE`** — timestamp logic that belongs in a `BEFORE UPDATE` trigger. Grep finds both the statements that forgot it (stale) and the ones redundant with a trigger that's already there.
- **Two columns for one fact** — `status` + `stage`, a JSON blob plus scalar columns projected out of it, a "current" snapshot beside a versions table ([the fact stored twice](../../patterns/one-fact-many-owners.md#variant-the-fact-stored-twice)).
- **A stored `*_count` / `total_*`** — a value the app maintains where a `COUNT(*)`, a view, or a `GENERATED ALWAYS AS` column is the actual source of truth. Doubly wrong when stored immutably (it can never be corrected).
- **`SELECT max(seq) + 1` then `INSERT`** — an ordering the database should generate; it races behind its own unique index and surfaces as a random 500.
- **`SELECT …; if not found: INSERT`** — a uniqueness check that should be a `UNIQUE` constraint plus `ON CONFLICT`.
- **A multi-statement cascade in application code** — several `DELETE`s in a loop standing in for the `ON DELETE CASCADE` the schema never declared.
- **An "append-only" table with no block-mutation trigger** — immutability as a convention, not an enforced rule; and its dangerous cousin, a trigger guarded by `IF pg_trigger_depth() = 0` (never true inside a trigger body — a silent no-op that *looks* installed).
- **A foreign key with no index** — Postgres indexes primary keys and unique constraints, not FKs; the parent delete and every join quietly go sequential.

## At the call site

The same generator, one function at a time: each function reads what it needs and looks complete alone. The cost
lives **between** functions, in the one request that calls them all. Most of these belong to
[Every Request Has a Round-Trip Budget](round-trips-per-request.md); the others name their owner.

- **A reader `def f(conn, some_id)` called beside others of the same shape**: each loads the row it needs, so one request reads that row several times.
- **A check that reads a row and returns `None` or a `bool`**: the handler's next line reads the row again ([the check discards its answer](../architecture/parse-dont-validate.md)).
- **A context object built inside a loop over options**: every fact is read again for each candidate move.
- **One statement per section of a polled page, or a statement inside a loop over rows**: `UNION ALL`, a join, `= ANY(%s)`.
- **`SELECT *` as an existence test**: a wide row fetched to learn that it exists, where `EXISTS` answers.
- **A statement counter in the query helper**: `BEGIN`/`COMMIT`, batch executes and raw-cursor statements are not counted, so every budget built on it is low.
- **A polled `GET` that performs an `UPDATE`** (a lease renewed on read, a "mark settled" inside a poll): one write per open tab per interval, in a route that claims only to answer ([Command-Query Separation](../architecture/command-query-separation.md)).
- **`FOR SHARE` or `FOR UPDATE` in a read route**: a row-lock write on every read. Name the invariant the lock protects and its competing writers first: a read-side `FOR SHARE` that keeps a multi-statement read consistent against them is justified; one that protects nothing is not.
- **A `LIKE` pattern built from a column** (`WHERE path LIKE parent.prefix || '%'`): the pattern is unknown when the statement is planned, so no B-tree serves it ([Know What Defeats an Index](index-defeaters.md)).
- **A link table indexed on one column**: "the newest run of kind K for this parent" reads every run of the parent. Index the columns the lookup filters and sorts on, in that order ([Match the Index to the Query Shape](index-query-shape.md)).
