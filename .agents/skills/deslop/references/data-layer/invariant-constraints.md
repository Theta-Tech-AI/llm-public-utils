---
name: deslop-data-layer-invariant-constraints
description: Deslop principle — Enforce Invariants with Constraints, Not Application Code: Rules live where writes happen, not where the app calls.
---

# Enforce Invariants with Constraints, Not Application Code

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
