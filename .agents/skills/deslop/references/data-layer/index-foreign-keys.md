---
name: deslop-data-layer-index-foreign-keys
description: Deslop principle — Index Every Foreign Key: Postgres does not auto-index FKs.
---

# Index Every Foreign Key

Postgres automatically indexes primary keys and unique constraints — but **not** foreign keys. An unindexed FK is a quiet two-way tax: every delete or update on the *parent* sequentially scans the whole child table to check for references (one parent row delete can read millions of child rows), and every join from parent to child has no index to ride. Add a plain B-tree index on every FK column. This is the single most common missing index precisely because the FK and the index that should accompany it are declared in different places — easy to write one and forget the other.

```sql
project_id uuid NOT NULL REFERENCES project(id) ON DELETE CASCADE;
CREATE INDEX idx_document_project ON document (project_id);   -- NOT automatic — add it
```
