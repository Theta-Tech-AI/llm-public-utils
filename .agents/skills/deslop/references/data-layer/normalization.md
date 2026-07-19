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

---

In relation to other principles, normalization:

| Principle | Relationship |
|-----------|--------------|
| [**Single Source of Truth**](../architecture/single-source-of-truth.md) | This is SSoT applied to schema |
| [**Let the Database Own Timestamps and Derived Values**](database-timestamps.md) | Generated columns are DB-owned derivation |
| [**DRY**](../architecture/dry.md) | Two columns for one fact is knowledge duplication at rest |
