---
name: deslop-pattern-fork-instead-of-extension
description: Deslop pattern — Fork Instead of Extension: a downstream module copies an upstream one and edits it; extend through the upstream seam or add the seam, then delete the copy.
---

# Fork of upstream instead of extension

## The structural tell

A downstream module copies an upstream module and edits it; the two drift, and sometimes both write a store (two receipts for one "verified" fact). Tell by behaviour, not by name: same job, same inputs, two writers.

## Why it arises

The upstream had no seam for the change, and waiting for one was slower than copying. The copy then stopped receiving upstream fixes.

## Repair shape, owner first

Extend through the upstream's own seam (a hook, a subclass, a config). Where there is none, add the seam upstream, then delete the copy. Never paste an upstream fix downstream.

## Who owns the mechanism

| Principle | Owns | Boundary with this pattern |
|---|---|---|
| [code-reusability](../principles/architecture/code-reusability.md) | when reuse beats a copy | names the fork as the opposite error |
| [one-logical-unit-one-home](../principles/architecture/one-logical-unit-one-home.md) | one home per unit | the two homes of one job |
| [dependency-stability](../principles/architecture/dependency-stability.md) | depending toward the stable side | why the seam belongs upstream |
| [duplication sweep](../readings/duplication.md) | the cross-repo hunt | the recipe to find the pairs |

## Caught by

Lens `duplication`.

## Measured

211 findings, 40 high — few findings, but a high share are severe. Heuristic classes; they overlap.

## Example

```python
# ❌ the overlay carries its own copy of the verifier and writes its own receipt
def verify_bearer(token): ...   # forked from upstream auth.verify_bearer, now different
# ✅ configure the upstream verifier; one receipt
auth.configure(verifier=Verifier(audience=settings.audience))
```
