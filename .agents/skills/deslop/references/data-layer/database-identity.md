---
name: deslop-data-layer-database-identity
description: Deslop principle — Generate Identity and Order in the Database: IDENTITY/SEQUENCE + ON CONFLICT; never SELECT-then-INSERT.
---

# Generate Identity and Order in the Database

`SELECT max(seq) + 1` then `INSERT` is a race: two transactions read the same max and write the same number. It survives only behind a unique index — which turns the race into a surprise error — or a lock you remembered to take. Let the database generate monotonic values (`GENERATED ALWAYS AS IDENTITY`, a `SEQUENCE`, `gen_random_uuid()`/`uuidv7()` for keys) and enforce uniqueness with a constraint, never a `SELECT`-then-`INSERT` existence check. Pair that with `INSERT ... ON CONFLICT` so concurrent and retried writers converge instead of colliding. This is [Idempotency](../architecture/idempotency.md) at the storage layer: the unique constraint *is* the idempotency key, and the database is the only actor that sees all writers at once.

```python
# ❌ Wrong - check-then-act across two statements; races and double-writes
row = db.execute("SELECT id FROM membership WHERE team=%s AND user=%s", ...)
if not row:
    db.execute("INSERT INTO membership ...")

# ✅ Correct - one atomic statement; concurrent callers converge
db.execute("""INSERT INTO membership (team_id, user_id) VALUES (%s, %s)
              ON CONFLICT (team_id, user_id) DO NOTHING""", ...)
```
