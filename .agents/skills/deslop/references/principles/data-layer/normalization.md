---
name: deslop-data-layer-normalization
description: Deslop principle — Normalize to a Single Source of Truth: Each fact lives in one column; the DB owns derivations.
---

# Normalize to a Single Source of Truth

This is [Single Source of Truth](../architecture/single-source-of-truth.md) applied to schema: each fact lives in exactly one column of one row, and everything else derives from it by join or computation. The recurring violations are a "current" snapshot column duplicated against an authoritative versions/history table and synced by application code; scalar columns promoted out of a JSON blob that still holds the same value; stored counts that are really `COUNT(*)` over a child table; and a `total` written by hand next to its parts. Each is two places one truth can live, and they diverge the instant one write path forgets the other — silently, because both reads still "work." Normalize until every non-key column depends on the key, the whole key, and nothing but the key. When you genuinely need a denormalized copy for performance, make the *database* own the derivation so it cannot drift — a generated column, a view, or a trigger — never a second hand-maintained column.

```sql
-- ❌ Wrong - total can disagree with its parts; nothing enforces the sum
total_tokens integer  -- written by the app as input + output

-- ✅ Correct - the database computes it; it can never drift
total_tokens integer GENERATED ALWAYS AS (input_tokens + output_tokens) STORED
```

### The forms, named — with the anomaly each one prevents

The one-line rule above ("the key, the whole key, and nothing but the key") is the short form of a ladder, and
naming the rungs is what lets a finding be argued rather than asserted. Each rung exists to prevent a specific,
nameable failure:

| Form | The rule | The anomaly it prevents |
|---|---|---|
| **1NF** | Every column holds a single atomic value; no repeating groups, no comma-joined ids, no "column per item" | Values that cannot be filtered, joined or constrained — `tags = 'a,b,c'` makes "everything with tag b" a `LIKE` scan |
| **2NF** | Every non-key column depends on the **whole** key, not part of it | A composite key where one attribute is fixed by half of it: update the fact in one row and the others now disagree |
| **3NF** | No non-key column depends on another non-key column (no transitive dependency) | `order(customer_id, customer_address)` — change the customer's address and every historical order silently keeps the old one |
| **BCNF** | Every determinant is a candidate key | A table where a non-key column determines part of the key: rows can disagree about a fact whose owner is that column |

The failure modes those rungs exist to prevent have names too, and they are the sentences to use in a report:

- **Insertion anomaly** — a fact cannot be recorded because it has nowhere to live. A newly hired employee with
  no project yet cannot be stored without inventing a null project row.
- **Update anomaly** — the same fact appears on several rows, so an update either touches all of them or leaves
  them disagreeing. This is the one that survives in production for years, because both reads still "work".
- **Deletion anomaly** — deleting a row destroys an unrelated fact. Delete the last order for a customer and the
  customer's own record disappears with it.

### Denormalization has a contract

Normalization is the default, and denormalization is legitimate — joins cost, and a reporting table that reads
five tables per query is a real expense. But a denormalized copy is only admissible under a written contract,
because otherwise it is exactly the drift this principle exists to prevent:

1. **The database owns the derivation**, not the application: a `GENERATED ALWAYS AS … STORED` column, a
   trigger, a view, or a materialized view with a defined refresh. Two writers is the defect; one writer that is
   the database is the repair.
2. **The copy is checkable**: a constraint, a generated expression, or a maintenance query that proves copy ==
   truth. "We update it in the same transaction" is not checkability — every write path has to remember, which is
   the definition of a fact held twice.
3. **The reason is written down** next to the column: measured cost, the query it serves, and what would let it be
   removed. An unexplained denormalized column is indistinguishable from slop that happened to be fast.

A stored `COUNT(*)`, a hand-maintained `total`, a `latest_status` snapshot, and a `customer_name` copied for
convenience are all the same finding. Store the derivation in the database or do not store it.

---

In relation to other principles, normalization:

| Principle | Relationship |
|-----------|--------------|
| [**Single Source of Truth**](../architecture/single-source-of-truth.md) | This is SSoT applied to schema |
| [**Let the Database Own Timestamps and Derived Values**](database-timestamps.md) | Generated columns are DB-owned derivation |
| [**DRY**](../architecture/dry.md) | Two columns for one fact is knowledge duplication at rest |
| [**Enforce Invariants with Constraints, Not Application Code**](invariant-constraints.md) | A normal form the schema does not enforce is a convention, and conventions drift |
| [**Every Join Needs an Access Path on the Side Being Probed**](join-access-paths.md) | Normalization accepts joins as the cost; the access path is how the cost is paid |

## Prior art

Normalization, its normal forms, and the insert/update/delete anomalies are E. F. Codd's — *A Relational Model of
Data for Large Shared Data Banks* (1970) and *Further Normalization of the Data Base Relational Model* (1971),
summarized in [Wikipedia's *Database normalization*](https://en.wikipedia.org/wiki/Database_normalization). The
generated-column repair is defined in the PostgreSQL manual,
[*Generated Columns*](https://www.postgresql.org/docs/current/ddl-generated-columns.html). This library's
contribution is the framing of denormalization as a **contract** — one writer (the database), a checkable copy,
a written reason — rather than a performance choice made per column.
