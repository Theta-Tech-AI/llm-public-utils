---
name: deslop-data-layer-join-access-paths
description: Deslop principle — Every Join Needs an Access Path on the Side Being Probed: an index on the driver's key is not enough, and the plan decides which side that is.
---

# Every Join Needs an Access Path on the Side Being Probed

A join is not a property of the schema; it is a property of the **pair** — a driving row set, and a probe into
the other table for each row it produces. A schema can be perfectly normalized, every foreign key declared, and
every column correctly typed, and still collapse under production data because only one side of that pair has an
access path. This is the gap left by [Index Every Foreign Key](index-foreign-keys.md): that principle says the
reference column needs an index, and this one says **why, and which side of a given query that column is on**.

Two facts do most of the work, and both are widely misremembered:

- **The target side of a foreign key is indexed automatically; the source side is not.** The referenced columns
  must be a primary key or unique constraint, and Postgres implements those with a unique index — so
  `parent(id)` is covered for free. `child(parent_id)` is not, and the cost is twofold: a join from parent to
  child has nothing to ride, and every `DELETE`/`UPDATE` of a parent row must scan the child table to prove no
  row would be orphaned.
- **Which side needs the index depends on the plan the optimizer chooses.** A nested-loop join reads the outer
  (driving) rows and probes the inner table by key, so the *inner* side needs the index on the join predicate. A
  hash join scans both sides once and needs no index on the predicate at all — adding one buys nothing. A
  sort-merge join wants an index whose order matches the sort keys. "Index every join column" is therefore right
  in effect and wrong as a rule: the predicate columns need an index **because the cheap plan is the one that
  uses them**, and a low-cardinality column (a `status`, a boolean, a type discriminator) can carry an index that
  no plan ever chooses.

```sql
-- ❌ Wrong — the FK is declared, the predicate column has no index, and the loop is in the client
SELECT id FROM project WHERE status = 'active';          -- 400 rows
-- then, per row, from application code:
SELECT * FROM document WHERE project_id = ?;             -- 400 round trips, each a seq scan

-- ✅ Correct — one join, access path on the probed side, composite ordered for the predicate + sort
CREATE INDEX idx_document_project_created ON document (project_id, created_at DESC);
SELECT d.* FROM project p JOIN document d ON d.project_id = p.id
 WHERE p.status = 'active' ORDER BY d.created_at DESC;
```

**The N+1 in application code is the same defect.** An ORM that fetches children per parent row has implemented a
nested-loop join in the client, paying network latency on top of the missing index — and it is usually invisible
in review because every individual query looks reasonable. The tell is a loop in application code over rows whose
children are then loaded one at a time, or an ORM lazy relationship touched inside a serialisation loop.

**Verify with the plan, not the intent.** `EXPLAIN (ANALYZE, BUFFERS)` on the real query, against a table with
production-scale row counts: an `Index Scan`/`Index Only Scan` on the probed side is the pass; a `Seq Scan` on a
large inner table, or `rows=` estimates off by orders of magnitude, is the finding. Estimates matter because they
are how the optimizer chose the plan at all — stale statistics produce a hash join where a nested loop was
correct, which reads as "the database is slow" rather than "the schema is unanalysed".

**Also check the shape, not only the existence, of the index.** A composite index serves predicates on its
leading columns only — `(a, b)` answers `a` and `a, b`, never `b` alone — so a join predicate on `b` needs `b`
somewhere at the front. Order composite keys by equality columns first, then the range or sort column, and see
[Match the Index to the Query Shape](index-query-shape.md) for the rest.

**And use bind parameters.** A join statement built with literals instead of parameters is re-planned on every
execution: the optimizer must evaluate the join-order permutations afresh, and the plan it would have cached is
thrown away. That is a slop tell at the call site, not in the schema, and it hides in code that "works".

---

In relation to other principles, join access paths:

| Principle | Relationship |
|-----------|--------------|
| [**Index Every Foreign Key**](index-foreign-keys.md) | The declaration rule; this principle is the *why* and the which-side |
| [**Match the Index to the Query Shape**](index-query-shape.md) | Column order within a composite key; partial and covering forms |
| [**Know What Defeats an Index**](index-defeaters.md) | A perfect index that no predicate can use is not an access path |
| [**Every Index Is Used or It's Dropped**](unused-indexes.md) | The converse smell — an index built for no query |
| [**Enforce Invariants with Constraints, Not Application Code**](invariant-constraints.md) | Referential integrity belongs to the database; materialising it in a loop does not make it one |
| [**Normalize to a Single Source of Truth**](normalization.md) | Joins are the cost normalization accepts; the access path is how you pay it |

## Control

Planted fixture (a three-file repo: a schema with an unindexed `document.project_id` used by a per-project query
loop, a parent `DELETE`, a comma-joined `tags`, a hand-maintained `total_tokens`, and a copied
`customer_email`/`address`), run read-only with a neutral prompt, two arms:

| Arm | What ran | Result |
|---|---|---|
| baseline | the shipped skill, one monolithic pass | found the missing FK indexes and the per-project query loop — but charged the loop as **KISS** ("executed once per project"), a style complaint with no access-path framing |
| treatment | this group alone, forced to read its files in full | charged the same loop under **Every Join Needs an Access Path on the Side Being Probed**, naming the N+1 as a nested-loop join run in the client, alongside the missing source-side indexes and the parent-delete scan |

The honest reading: the rule **fired 1 of 1** on the planted N+1 and reframed an existing finding rather than
inventing a new one. The normal-form additions did not change detection — the baseline's `normalization` row
already caught the comma-joined column and the copied address — they change what the *repair* says and why, which
is the point of naming an anomaly.

## Prior art

The nested-loop / hash / sort-merge distinction, the equality-then-range column order, and the N+1 pattern are
Markus Winand's, from [*Use The Index, Luke*](https://use-the-index-luke.com/sql/join) and
[*The right column order in multi-column indexes*](https://use-the-index-luke.com/sql/where-clause/the-equals-operator/concatenated-keys).
The FK-side asymmetry — target auto-indexed, source not, and the parent-`DELETE` scan as the second cost — is
Laurenz Albe's, [*Foreign key indexing and performance in PostgreSQL*](https://www.cybertec-postgresql.com/en/index-your-foreign-key/),
against the PostgreSQL manual's [*Constraints*](https://www.postgresql.org/docs/current/ddl-constraints.html) and
[*Indexes*](https://www.postgresql.org/docs/current/indexes.html). This library's contribution is the framing:
the join is a *pair* with one probed side, so "add an index on every join column" is not the rule — the rule is
that the predicate columns must be cheap to probe, and the plan is the only proof.
