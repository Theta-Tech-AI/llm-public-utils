---
name: deslop-data-layer-domain-constraints
description: Deslop principle — Constrain the Domain in the Schema: CHECK/ENUM/FK for closed vocabularies, NOT NULL, range checks.
---

# Constrain the Domain in the Schema

A `status text` column the application "knows" holds only five values is an unconstrained domain: the day a typo, a renamed constant, or a manual SQL fix writes a sixth, every `WHERE status IN (...)` and every partial index silently stops matching that row. Push the domain into the schema — a `CHECK (status IN (...))`, a real `ENUM`, or a foreign key to a lookup table — so the bad write fails at the boundary instead of corrupting query results downstream. This is [Parse, Don't Validate](../architecture/parse-dont-validate.md) and [Fail-Fast](../reliability/fail-fast.md) for data at rest: the column's type, not a code comment, is the spec. `NOT NULL`, `UNIQUE`, range checks (`rank >= 1`), and cross-column checks belong here for the same reason — one enforcement point for every writer beats the same check copy-pasted into every service and forgotten by the next.

```sql
-- ❌ Wrong - the vocabulary lives only in Python; the DB accepts anything
status text NOT NULL

-- ✅ Correct - the illegal write is rejected where it happens
status text NOT NULL CHECK (status IN ('pending', 'running', 'done', 'failed')),
CHECK (ends_at >= starts_at)
```

---

In relation to other principles, domain constraints:

| Principle | Relationship |
|-----------|--------------|
| [**Parse, Don't Validate**](../architecture/parse-dont-validate.md) | The column's type, not a comment, is the spec |
| [**Fail-Fast**](../reliability/fail-fast.md) | The illegal write fails where it happens |
| [**Foreign Keys Are Not Optional**](foreign-keys.md) | A lookup-table FK is a domain constraint by reference |
