---
name: deslop-data-layer
description: Deslop principles, Part IV: The Data Layer — schema integrity (FKs, normalization, domain constraints), pushing logic into the database, indexing/access paths, and the common slop tells.
---

# Part IV: The Data Layer

> *Slop in the schema is the most expensive kind. Application code is rewritten, ported between languages, and bypassed by migrations, scripts, and the next service — but the database outlives all of them and is the one place an invariant can be made true for every writer at once. These principles govern integrity, where logic lives, and how rows are reached.*

**Contents:**

- [Schema Integrity](#schema-integrity)
  - [Foreign Keys Are Not Optional](#foreign-keys-are-not-optional)
  - [Normalize to a Single Source of Truth](#normalize-to-a-single-source-of-truth)
  - [Constrain the Domain in the Schema](#constrain-the-domain-in-the-schema)
- [Push Logic Into the Database](#push-logic-into-the-database)
  - [Let the Database Own Timestamps and Derived Values](#let-the-database-own-timestamps-and-derived-values)
  - [Enforce Invariants with Constraints, Not Application Code](#enforce-invariants-with-constraints-not-application-code)
  - [Generate Identity and Order in the Database](#generate-identity-and-order-in-the-database)
- [Access Paths](#access-paths)
  - [Index Every Foreign Key](#index-every-foreign-key)
  - [Index What You Filter, Join, and Sort On](#index-what-you-filter-join-and-sort-on)
  - [Match the Index to the Query Shape](#match-the-index-to-the-query-shape)
  - [Know What Defeats an Index](#know-what-defeats-an-index)
  - [Every Index Is Used or It's Dropped](#every-index-is-used-or-its-dropped)
- [The Common Slop Tells](#the-common-slop-tells)

---

## Schema Integrity

---

### Foreign Keys Are Not Optional

> "A foreign key is a promise the database keeps; a naming convention is a promise you hope everyone remembers."

Every column holding another row's identity (`*_id`, `*_by`, `*_run_id`) must carry a `REFERENCES` constraint with an explicit `ON DELETE` action. A bare `uuid NOT NULL` named `project_id` is an unenforced reference — nothing stops an insert pointing at a project that never existed or was deleted years ago, and the orphan surfaces as a baffling error three joins away. The tell that the constraint was knowable and merely omitted: a sibling table in the same schema references the same parent correctly. Omitting the FK also forfeits cascade, so deletes get hand-rolled as multiple application `DELETE`s that drift out of sync with the schema. Choose the delete behavior deliberately; only a genuinely external identity (a row in a search index, an object store, another service's database) can't be a FK — document those as soft references rather than leaving every reference unconstrained.

```sql
-- ❌ Wrong - an unenforced reference; orphans on delete, integrity is "hope"
CREATE TABLE document (
    id          uuid PRIMARY KEY,
    project_id  uuid NOT NULL,          -- looks like an FK, enforces nothing
    created_by  uuid                    -- a user that may not exist
);

-- ✅ Correct - the database guarantees the graph stays connected
CREATE TABLE document (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id  uuid NOT NULL REFERENCES project(id)  ON DELETE CASCADE,
    created_by  uuid          REFERENCES app_user(id) ON DELETE SET NULL
);
```

- `CASCADE` for owned children, `SET NULL` for optional links, `RESTRICT`/`NO ACTION` for rows that must not be orphaned (audit subjects, referenced catalogues).

---

### Normalize to a Single Source of Truth

This is [Single Source of Truth](architecture.md#single-source-of-truth) applied to schema: each fact lives in exactly one column of one row, and everything else derives from it by join or computation. The recurring violations are a "current" snapshot column duplicated against an authoritative versions/history table and synced by application code; scalar columns promoted out of a JSON blob that still holds the same value; stored counts that are really `COUNT(*)` over a child table; and a `total` written by hand next to its parts. Each is two places one truth can live, and they diverge the instant one write path forgets the other — silently, because both reads still "work." Normalize until every non-key column depends on the key, the whole key, and nothing but the key. When you genuinely need a denormalized copy for performance, make the *database* own the derivation so it cannot drift — a generated column, a view, or a trigger — never a second hand-maintained column.

```sql
-- ❌ Wrong - total can disagree with its parts; nothing enforces the sum
total_tokens integer  -- written by the app as input + output

-- ✅ Correct - the database computes it; it can never drift
total_tokens integer GENERATED ALWAYS AS (input_tokens + output_tokens) STORED
```

---

### Constrain the Domain in the Schema

A `status text` column the application "knows" holds only five values is an unconstrained domain: the day a typo, a renamed constant, or a manual SQL fix writes a sixth, every `WHERE status IN (...)` and every partial index silently stops matching that row. Push the domain into the schema — a `CHECK (status IN (...))`, a real `ENUM`, or a foreign key to a lookup table — so the bad write fails at the boundary instead of corrupting query results downstream. This is [Parse, Don't Validate](architecture.md#parse-dont-validate) and [Fail-Fast](reliability.md#fail-fast--defensive-programming) for data at rest: the column's type, not a code comment, is the spec. `NOT NULL`, `UNIQUE`, range checks (`rank >= 1`), and cross-column checks belong here for the same reason — one enforcement point for every writer beats the same check copy-pasted into every service and forgotten by the next.

```sql
-- ❌ Wrong - the vocabulary lives only in Python; the DB accepts anything
status text NOT NULL

-- ✅ Correct - the illegal write is rejected where it happens
status text NOT NULL CHECK (status IN ('pending', 'running', 'done', 'failed')),
CHECK (ends_at >= starts_at)
```

---

## Push Logic Into the Database

> *Foreign keys, timestamps, uniqueness, immutability — these are mechanical invariants, not business decisions. Enforcing them in the database is [Separation of Concerns](architecture.md#separation-of-concerns): the data layer owns "the data is always well-formed," which frees the application layer to read as what it actually **decides**. Every `updated_at = now()` or hand-rolled uniqueness check sitting in application code is mechanism that has leaked upward — it raises [cognitive load](clean-code.md#cognitive-load) on every future reader, who now has to separate the load-bearing logic from the bookkeeping. Push the bookkeeping down so the code that's left is the decisions; a reader should never have to wonder whether a timestamp or a referential check is where the real logic lives.*

---

### Let the Database Own Timestamps and Derived Values

`created_at` and `updated_at` are the textbook case of logic that belongs one layer down. `created_at timestamptz NOT NULL DEFAULT now()` is set correctly on every insert from any client, forever. `updated_at` is the trap: a `DEFAULT now()` fires only on insert, so teams "fix" it by writing `updated_at = now()` in every `UPDATE` — which means every statement that forgets the clause silently ships a stale timestamp, and the ones that remember are redundant with each other and overwritten anyway. Maintain it with one `BEFORE UPDATE` trigger so the column is right whether the write came from the service, a migration, or a one-off `psql` session.

```sql
-- ❌ Wrong - every writer must remember; the one that forgets corrupts the trail
UPDATE document SET title = %s, updated_at = now() WHERE id = %s;

-- ✅ Correct - define it once; every UPDATE is covered, including ones you didn't write
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_document_updated_at
    BEFORE UPDATE ON document
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

---

### Enforce Invariants with Constraints, Not Application Code

Any rule of the form "X can never happen" belongs where X is written, not where the application happens to call. An append-only audit table needs `BEFORE UPDATE`/`BEFORE DELETE` triggers that raise — not a code-review convention that nobody issues a `DELETE`. A two-party state ("resolved" requires both parties' columns populated) is a `CHECK`. A polymorphic reference a plain FK can't express is a validation trigger. The test that an invariant is actually enforced is adversarial: as a writer who bypasses your service layer, attempt the forbidden write and confirm the database rejects it — "the application never does that" is not enforcement, because the next service, the next migration, and the analyst at a psql prompt are all writers too.

```sql
-- ✅ Append-only: the table itself refuses to be rewritten
CREATE OR REPLACE FUNCTION block_mutation() RETURNS trigger AS $$
BEGIN RAISE EXCEPTION 'audit rows are immutable'; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_block
    BEFORE UPDATE OR DELETE ON audit_event
    FOR EACH ROW EXECUTE FUNCTION block_mutation();
```

- Verify the trigger truly fires — a guard like `IF pg_trigger_depth() = 0` is never true inside a trigger body, a classic silent no-op.

---

### Generate Identity and Order in the Database

`SELECT max(seq) + 1` then `INSERT` is a race: two transactions read the same max and write the same number. It survives only behind a unique index — which turns the race into a surprise error — or a lock you remembered to take. Let the database generate monotonic values (`GENERATED ALWAYS AS IDENTITY`, a `SEQUENCE`, `gen_random_uuid()`/`uuidv7()` for keys) and enforce uniqueness with a constraint, never a `SELECT`-then-`INSERT` existence check. Pair that with `INSERT ... ON CONFLICT` so concurrent and retried writers converge instead of colliding. This is [Idempotency](architecture.md#idempotency) at the storage layer: the unique constraint *is* the idempotency key, and the database is the only actor that sees all writers at once.

```python
# ❌ Wrong - check-then-act across two statements; races and double-writes
row = db.execute("SELECT id FROM membership WHERE team=%s AND user=%s", ...)
if not row:
    db.execute("INSERT INTO membership ...")

# ✅ Correct - one atomic statement; concurrent callers converge
db.execute("""INSERT INTO membership (team_id, user_id) VALUES (%s, %s)
              ON CONFLICT (team_id, user_id) DO NOTHING""", ...)
```

---

## Access Paths

> *Indexes are what keep a database fast as it grows — and the first thing single-table-at-a-time code skips, because a missing index "works" on an empty dev table and only bites at production scale. The loop is the same every time: know the queries the table must serve, index for them, and `EXPLAIN` to confirm the planner actually uses what you built. A query with no index to use and an index no query uses are equal and opposite smells.*

---

### Index Every Foreign Key

Postgres automatically indexes primary keys and unique constraints — but **not** foreign keys. An unindexed FK is a quiet two-way tax: every delete or update on the *parent* sequentially scans the whole child table to check for references (one parent row delete can read millions of child rows), and every join from parent to child has no index to ride. Add a plain B-tree index on every FK column. This is the single most common missing index precisely because the FK and the index that should accompany it are declared in different places — easy to write one and forget the other.

```sql
project_id uuid NOT NULL REFERENCES project(id) ON DELETE CASCADE;
CREATE INDEX idx_document_project ON document (project_id);   -- NOT automatic — add it
```

---

### Index What You Filter, Join, and Sort On

Beyond foreign keys, the index set is dictated by the queries the table actually serves: every column that recurs in a `WHERE`, a `JOIN` condition, or an `ORDER BY` is an index candidate. Don't guess — collect the real queries against the table and index their access paths. An `ORDER BY created_at DESC LIMIT 20` feed wants `created_at DESC` indexed so the database reads 20 rows instead of sorting the whole table; a recurring `WHERE status = ?` wants `status` reachable by index. The discipline is bidirectional: a hot predicate with no index to use is a latent slow query, and an index no query ever uses is pure write-time cost (see "Every Index Is Used or It's Dropped").

---

### Match the Index to the Query Shape

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

### Know What Defeats an Index

Most "why is this slow" is a predicate written so the index *can't* be used. The recurring ones:

- **Leading wildcard** — `LIKE '%term%'` cannot use a B-tree; use a `pg_trgm` GIN index (or full-text search).
- **A function or cast on the indexed column** — `WHERE lower(email) = ?` or `WHERE created_at::date = ?` ignores a plain index on the bare column. Index the expression, or rewrite the predicate to leave the column bare (`created_at >= ? AND created_at < ?`).
- **Implicit type mismatch** — comparing a `uuid` to a text literal, or `bigint` to `numeric`, can force a cast that skips the index.
- **Low selectivity** — indexing a boolean, or a status that's 90% one value, rarely helps; a partial index on the rare value does.

The arbiter is `EXPLAIN (ANALYZE, BUFFERS)` on the real query at real data volume: a `Seq Scan` where you expected an `Index Scan` is the bug. "Fast on my 100-row dev table" proves nothing — a sequential scan of 100 rows is instant and of 100 million is an outage.

---

### Every Index Is Used or It's Dropped

An index is not a quantity to minimize — it's a binary. Either a real query uses it, so it earns the write cost it imposes on every `INSERT`/`UPDATE`/`DELETE` (plus storage and planner time), or no query uses it and it is pure loss. There is no "nice to have" index. So the *count* is irrelevant: ten indexes that each serve a query are all correct; one index that serves none is the bug. Judge each index by that single question — *which query uses this, and does the planner actually pick it?* — and `EXPLAIN` to confirm. The ones that reliably fail the test and should be deleted: a plain index that is a left-prefix of an existing composite (`(a)` when `(a, b)` exists — the composite already serves `a`), a non-unique index duplicating a `UNIQUE` constraint (the unique index already serves every read the plain one would), and any index `pg_stat_user_indexes` reports has never been scanned (`idx_scan = 0`). If you can't name the query an index serves, that's your answer.

---

## The Common Slop Tells

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
