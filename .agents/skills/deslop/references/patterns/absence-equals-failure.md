---
name: deslop-pattern-absence-equals-failure
description: Deslop pattern — Absence Equals Failure: one value answers both "nothing there" and "the read failed"; make them two values and let the caller choose.
---

# Absence and failure share one value

## The structural tell

One return value (`None`, `[]`, `""`, `"not available"`, a `fallback=` argument) answers both "nothing is saved" and "the read failed". A catch-all wrapper turns every exception into the empty answer, so the caller cannot choose between *show empty* and *show an outage*.

Its quieter form is a helper that settles what absence means for everyone: `_coerce_int_or_zero(text)` (is absence zero or an error?) or `_get_or_default(d, k, v)` (who may invent a missing value?). The owner is the parser at the boundary with a stated policy, or a type that cannot be partial.

## Variant: absence read as the favourable answer

The same collapse with the sign flipped: no evidence is recorded as the answer that lets work proceed. A check passes because its probe printed nothing; a report starts `complete = True` and is only ever set false; a cost with no amount becomes a charged zero; a stop signal defaults to "never stopped"; a record with no status is taken as active just before a destructive step. The tell is a pass condition phrased as "no failure seen", or a default that happens to be the permissive member. The repair is the same third value: *unknown* is neither pass nor fail, and the favourable answer must be earned by evidence.

## Variant: several failures under one label

Distinct causes leave through one name, and the name is the first cause the author met. A token of the wrong type is reported as a wrong audience; any failed status call reads as "still running"; every provider error becomes "not found"; a callback that throws after a successful start is reported as a failed start. The tell is a handler narrower in its message than in its `except` clause: read the clause, list what it admits, compare with what the label says. Narrow the clause to the cause the label names, or classify inside it. A caller cannot recover from a failure it was told was a different one.

## Why it arises

An error once crashed a page, so someone wrapped the call. The wrapper's fallback happened to be the empty value.

## Repair shape, owner first

Make the two cases different values — a result type, a raised error, an explicit "unavailable" variant. A degrade wrapper may exist only where the policy is named, at the boundary that owns it.

## Who owns the mechanism

| Principle | Owns | Boundary with this pattern |
|---|---|---|
| [no-silent-defaults](../principles/reliability/no-silent-defaults.md) | a default must never hide a missing value | the mechanism; this pattern is its failure-versus-empty case |
| [errors-at-the-boundary](../principles/reliability/errors-at-the-boundary.md) | where failures are translated | where the "unavailable" answer is chosen |
| [fail-fast](../principles/reliability/fail-fast.md) | surfacing the error at the point of failure | what the catch-all swallowed |

## Caught by

Lenses `parsing` and `guarantees`.

## Measured

433 findings, 33 high. Heuristic classes; they overlap.

## Example

```python
# ❌ the UI shows "no drafts" while the database is down
def drafts(user): return degrade(lambda: db.drafts(user), fallback=[])
# ✅ empty is a result; failure is not
def drafts(user) -> list[Draft]: return db.drafts(user)   # raises Unavailable; the route maps it to 503
```
