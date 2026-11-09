---
name: deslop-pattern-consumer-redecides-producer
description: Deslop pattern — Consumer Re-Decides the Producer: a client or later stage reconciles what the producer already decided; return the decision, delete the reconciler.
---

# Consumer re-decides the producer's decision

## The structural tell

The client, or a later stage, reconciles answers the producer already reconciled: merging two server lists into one view, parsing again a field the API already typed, hand-copying a server rule ("orders over 50 ship free") into the SPA.

The tell is **structural and needs no vocabulary**: a consumer holding the vocabulary of a decision instead of asking its owner — a set of literal tokens compared against a string, a `startswith` on an identifier that names a thing, a first-non-empty scan over alternative spellings of one setting, a literal default sitting beside a lookup. Where those appear, ask what component should have answered and why the caller could not ask it. A reader of a type that must re-derive which of its fields are valid (an optional field meaningful in only one mode) is the same shape inside one codebase.

## Why it arises

The producer returned raw ingredients, or the consumer did not trust the contract. The consumer's copy of the rule then ages independently.

## Repair shape, owner first

The producer returns the decision (a field, a typed variant); the consumer renders it. One producer, one decision. Delete the reconciler rather than hardening it.

## Who owns the mechanism

| Principle | Owns | Boundary with this pattern |
|---|---|---|
| [helper-is-an-architecture-finding](../principles/architecture/helper-is-an-architecture-finding.md) | the missing owner behind a helper | here the owner is the producer's response |
| [parse-dont-validate](../principles/architecture/parse-dont-validate.md) | turning input into a typed value once | the typed field the consumer re-parses |
| [dry](../principles/architecture/dry.md) | one representation of a rule | the copy of the rule across the wire |

## Caught by

Lenses `parsing` and, when the copy is a rule, `duplication`.

## Measured

736 findings, 54 high. Heuristic classes; they overlap.

## Example

```typescript
// ❌ the SPA recomputes what the server knows
const shipsFree = order.total >= 50 && !order.items.some(i => i.oversize);
// ✅ the server sent the decision
const shipsFree = order.shipping.free;
```
