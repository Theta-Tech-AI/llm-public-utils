---
name: deslop-data-layer-foreign-keys
description: Deslop principle — Foreign Keys Are Not Optional: Every reference column gets REFERENCES + an explicit ON DELETE.
---

# Foreign Keys Are Not Optional

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

In relation to other principles, foreign keys:

| Principle | Relationship |
|-----------|--------------|
| [**Normalize to a Single Source of Truth**](normalization.md) | FKs keep the graph's single truth connected |
| [**Enforce Invariants with Constraints**](invariant-constraints.md) | Referential integrity is the canonical DB-owned invariant |
| [**Index Every Foreign Key**](index-foreign-keys.md) | The FK and its index are declared in different places — both are required |
