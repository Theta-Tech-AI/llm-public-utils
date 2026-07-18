---
name: deslop-data-layer
description: Deslop principles — The Data Layer: schema integrity (FKs, normalization, domain constraints), pushing logic into the database, indexing/access paths, and the common slop tells.
---

# The Data Layer

> *Slop in the schema is the most expensive kind. Application code is rewritten, ported between languages, and bypassed by migrations, scripts, and the next service — but the database outlives all of them and is the one place an invariant can be made true for every writer at once. These principles govern integrity, where logic lives, and how rows are reached.*

Each principle is a self-contained file — open it when a finding implicates that principle.

## Schema Integrity

| Principle | What it says |
|-------------|----------------|
| [Foreign Keys Are Not Optional](data-layer/foreign-keys.md) | Every reference column gets REFERENCES + an explicit ON DELETE |
| [Normalize to a Single Source of Truth](data-layer/normalization.md) | Each fact lives in one column; the DB owns derivations |
| [Constrain the Domain in the Schema](data-layer/domain-constraints.md) | CHECK/ENUM/FK for closed vocabularies, NOT NULL, range checks |

## Push Logic Into the Database

> *Foreign keys, timestamps, uniqueness, immutability — these are mechanical invariants, not business decisions. Enforcing them in the database is [Separation of Concerns](architecture/separation-of-concerns.md): the data layer owns "the data is always well-formed," which frees the application layer to read as what it actually **decides**. Every `updated_at = now()` or hand-rolled uniqueness check sitting in application code is mechanism that has leaked upward — it raises [cognitive load](clean-code/cognitive-load.md) on every future reader, who now has to separate the load-bearing logic from the bookkeeping. Push the bookkeeping down so the code that's left is the decisions; a reader should never have to wonder whether a timestamp or a referential check is where the real logic lives.*

| Principle | What it says |
|-------------|----------------|
| [Let the Database Own Timestamps and Derived Values](data-layer/database-timestamps.md) | DEFAULT now() plus a BEFORE UPDATE trigger |
| [Enforce Invariants with Constraints, Not Application Code](data-layer/invariant-constraints.md) | Rules live where writes happen, not where the app calls |
| [Generate Identity and Order in the Database](data-layer/database-identity.md) | IDENTITY/SEQUENCE + ON CONFLICT; never SELECT-then-INSERT |

## Access Paths

> *Indexes are what keep a database fast as it grows — and the first thing single-table-at-a-time code skips, because a missing index "works" on an empty dev table and only bites at production scale. The loop is the same every time: know the queries the table must serve, index for them, and `EXPLAIN` to confirm the planner actually uses what you built. A query with no index to use and an index no query uses are equal and opposite smells.*

| Principle | What it says |
|-------------|----------------|
| [Index Every Foreign Key](data-layer/index-foreign-keys.md) | Postgres does not auto-index FKs |
| [Index What You Filter, Join, and Sort On](data-layer/index-access-columns.md) | Index the queries the table actually serves |
| [Match the Index to the Query Shape](data-layer/index-query-shape.md) | Composite order, partial, covering, the right index type |
| [Know What Defeats an Index](data-layer/index-defeaters.md) | Leading wildcards, functions on columns, type mismatches |
| [Every Index Is Used or It's Dropped](data-layer/unused-indexes.md) | An index no query uses is pure loss |

## The Common Slop Tells

| Principle | What it says |
|-------------|----------------|
| [The Common Slop Tells](data-layer/slop-tells.md) | Grep-able schema smells, each mapping to a principle above |
