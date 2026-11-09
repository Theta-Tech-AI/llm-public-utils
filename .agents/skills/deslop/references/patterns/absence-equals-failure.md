---
name: deslop-pattern-absence-equals-failure
description: Deslop pattern — Absence Equals Failure: one value answers both "nothing there" and "the read failed"; make them two values and let the caller choose.
---

# Absence and failure share one value

## The structural tell

One return value (`None`, `[]`, `""`, `"not available"`, a `fallback=` argument) answers both "nothing is saved" and "the read failed". A catch-all wrapper turns every exception into the empty answer, so the caller cannot choose between *show empty* and *show an outage*.

Its quieter form is a helper that settles what absence means for everyone: `_coerce_int_or_zero(text)` (is absence zero or an error?) or `_get_or_default(d, k, v)` (who may invent a missing value?). The owner is the parser at the boundary with a stated policy, or a type that cannot be partial.

## Variant: absence read as the favourable answer

The same mistake, turned around: when the code has no information, it reports the good result.

- A health check passes because the command it ran printed nothing.
- A report starts with `complete = True` and only changes to false when a problem is noticed.
- A bill with no amount is saved as a paid bill of zero.
- A "should I stop?" signal that nobody connected answers "no, keep going".
- A record with no status is treated as active, just before a step that deletes things.

Look for a test that means "I saw no failure", or a default value that happens to be the one that lets the work continue. Fix it the same way as the main pattern: add a third answer, *unknown*, that is neither pass nor fail. The good result has to come from evidence, not from silence.

## Variant: several failures under one label

Different things went wrong, and the code reports all of them with one message. The message names the first problem its author happened to hit.

- A login token of the wrong kind is reported as "wrong audience".
- A status request fails for any reason, and the code says "still running".
- Every error from a provider is reported as "not found".
- A job starts fine, a later step throws, and the user is told the job failed to start.

Read the `except` (or `catch`) line and list every error it can catch. Then read the message. If the list is longer than the message admits, that is the finding. Either catch only the error the message names, or check which error it was and report each one truthfully. The caller cannot fix a problem it was told was a different problem.

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
