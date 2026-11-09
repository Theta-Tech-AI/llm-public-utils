---
name: deslop-pattern-one-fact-many-owners
description: Deslop pattern — One Fact, Many Owners: two places decide the same thing and already disagree on an input; name the single owner first, then delete the copies.
---

# One fact, many owners

The single-fact disease and the costliest pattern in the field run. Each copy was correct when written; no module was ever named the owner, so each drifted.

## The structural tell

Two or more places decide the same thing — a threshold, a status label, a permission rule, a default, a mapping — and **their answers differ on at least one input**. Test disagreement, not resemblance: feed both the edge case. Four projections of one run status that disagree on *cancelling* versus *cancelled* are one instance. Two copies that cannot disagree (generated code, a deliberately independent module) are a guardrail case, not this pattern.

## Why it arises

A second consumer needed the answer, and copying four lines was faster than finding or creating the owner. Nothing couples the copies, so a change to one is invisible to the rest.

## Repair shape, owner first

1. Pick the module whose change would be least surprising to the others.
2. Expose the decision as one function or table.
3. Route every consumer through it and delete the copies **in the same change**.

Polishing one copy of a fact that has several is the commonest wasted fix. Disagreeing copies are a bug report, not a style note.

## Who owns the mechanism

| Principle | Owns | Boundary with this pattern |
|---|---|---|
| [single-source-of-truth](../principles/architecture/single-source-of-truth.md) | one authoritative location for a datum | the rule; this pattern is the observed violation at scale |
| [dry](../principles/architecture/dry.md) | one representation of knowledge, fixed at the second occurrence | the code and logic copy; says nothing about which copy wins |
| [one-logical-unit-one-home](../principles/architecture/one-logical-unit-one-home.md) | where a unit lives | item 8 there names copies that already disagree |
| [helper-is-an-architecture-finding](../principles/architecture/helper-is-an-architecture-finding.md) | the missing owner behind a helper | the helper is a symptom of a missing owner |

File each instance under the owning principle; this pattern only groups and orders them.

## Caught by

Lenses `duplication` and `boundaries`. The field run also surfaced it from parsing and data cells, because one fact usually hides inside another pattern.

## Measured

705 findings, 171 high — 40% of all high findings in the run. Counts are heuristic text classes and overlap other patterns; do not add them.

## Example

```python
# ❌ two owners of "is this invoice overdue?" — they disagree on the due date itself
def badge(inv):  return "overdue" if inv.due < today() else "ok"          # api/serializers
def reminder(inv): return inv.due <= today() and not inv.paid              # jobs/reminders
# ✅ one owner, both call it
def is_overdue(inv, today): return inv.due < today and not inv.paid
```
