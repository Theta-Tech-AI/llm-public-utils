---
name: deslop-pattern-vocabulary-drift
description: Deslop pattern — Vocabulary Drift: one closed set of values spelled as literals in several layers, with the spellings or the set differing; one enum at the owner.
---

# Vocabulary drift across layers

## The structural tell

One closed set of values (status, kind, reason) is spelled as string literals in several modules and again in the UI, and the spellings or the **set** differ: `cancelling` handled in one switch, absent from another. Count the places that spell the set, then diff the members.

## Variant: the field list

Here the set that gets repeated is the list of fields of a record.

- A function that copies an object names all eleven of its fields by hand.
- One type is converted to another field by field, under a comment that says "add new fields here too".
- A table's columns are listed where the table is created, again where it is upgraded, and again where rows are written.
- An insert statement passes twenty-nine values by position.

When someone adds a field, the code still runs, and the new field is silently dropped at the one list nobody updated. Count the places that list the fields and compare them. Build the copies from the one definition (for example with `dataclasses.replace`), or arrange it so that a missing field is an error.

## Why it arises

Strings cross every boundary for free, so each layer typed its own copy. A new member is added where the author looked and nowhere else.

In the schema it shows as a `status text` or `*_type text` column with no `CHECK`: a closed vocabulary the application knows and the database does not. A partial index that hardcodes `WHERE status IN (...)` proves the set exists and is not enforced.

## Repair shape, owner first

One enum or table per vocabulary, produced at the owner. A schema constraint where it is stored, a generated or shared type where it crosses the wire. A switch over it must fail loudly on a new member.

## Who owns the mechanism

| Principle | Owns | Boundary with this pattern |
|---|---|---|
| [implicit-coupling](../principles/architecture/implicit-coupling.md) | agreement held only by matching strings | the mechanism; the vocabulary test is its detector |
| [domain-constraints](../principles/data-layer/domain-constraints.md) | the stored set, refused by the database | the storage end of the set |
| [illegal-states-unrepresentable](../principles/architecture/illegal-states-unrepresentable.md) | a type that cannot hold a non-member | the in-code end of the set |

## Caught by

Lenses `coupling` and `data-integrity`.

## Measured

584 findings, 47 high. Heuristic classes; they overlap.

## Example

```python
# ❌ the same statuses spelled in the worker, the API filter and the SPA
if run.status in ("queued", "running", "cancelling"): ...
# ✅ one owner of the set
class RunStatus(StrEnum): QUEUED = "queued"; RUNNING = "running"; CANCELLING = "cancelling"; CANCELLED = "cancelled"
ACTIVE = {RunStatus.QUEUED, RunStatus.RUNNING, RunStatus.CANCELLING}
```
