---
name: deslop-data-layer-database-timestamps
description: Deslop principle — Let the Database Own Timestamps and Derived Values: DEFAULT now() plus a BEFORE UPDATE trigger.
---

# Let the Database Own Timestamps and Derived Values

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
