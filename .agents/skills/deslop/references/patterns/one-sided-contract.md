---
name: deslop-pattern-one-sided-contract
description: Deslop pattern — One-Sided Contract: one end of an agreement exists without the other; walk each end to its partner, then implement the missing side or delete the present one.
---

# One-sided contract

## The structural tell

One end of an agreement exists without the other: the client retries and polls on an error code the server never emits; an idempotency key is sent and never honoured; a configured group list is parsed and logged but used only as an on/off switch. Walk each end to its partner. The end with none is the finding.

## Why it arises

The two ends were written by different people at different times, and no shared constant or schema ties them.

## Repair shape, owner first

Implement the missing side or delete the present one. Put the shared constant or schema where both ends import it.

## Who owns the mechanism

| Principle | Owns | Boundary with this pattern |
|---|---|---|
| [unclaimed-guarantee](../principles/clean-code/unclaimed-guarantee.md) | a promise with no keeper | the end without a partner is exactly that |
| [idempotency](../principles/architecture/idempotency.md) | what honouring a key means | the missing server half of a sent key |
| [implicit-coupling](../principles/architecture/implicit-coupling.md) | agreement by convention | the unshared constant |
| [design-by-contract](../principles/reliability/design-by-contract.md) | both sides of a contract checked | what a two-sided contract looks like |

## Caught by

Lenses `parsing`, `guarantees`.

## Measured

123 findings, 16 high — the rarest pattern, and cheap to verify by walking one end. Heuristic classes; they overlap.

## Example

```typescript
// ❌ retries on "RATE_LIMITED"; the API answers 429 with no such code
if (err.code === "RATE_LIMITED") return retry(call);
// ✅ the status both sides share
if (err.status === 429) return retry(call);
```
