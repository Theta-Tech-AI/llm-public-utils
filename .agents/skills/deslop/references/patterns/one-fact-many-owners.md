---
name: deslop-pattern-one-fact-many-owners
description: Deslop pattern — One Fact, Many Owners: two places decide the same thing and already disagree on an input; name the single owner first, then delete the copies.
---

# One fact, many owners

**Why this is slop:** Changing one of several independent copies leaves other consumers following a conflicting version of the same rule.

The single-fact disease and the costliest pattern in the field run. Each copy was correct when written; no module was ever named the owner, so each drifted.

## The structural tell

Two or more places decide the same thing — a threshold, a status label, a permission rule, a default, a mapping — and **their answers differ on at least one input**. Test disagreement, not resemblance: feed both the edge case. Four projections of one run status that disagree on *cancelling* versus *cancelled* are one instance. Two copies that cannot disagree (generated code, a deliberately independent module) are a guardrail case, not this pattern.

## Why it arises

A second consumer needed the answer, and copying four lines was faster than finding or creating the owner. Nothing couples the copies, so a change to one is invisible to the rest.

## File the first copy

Never wait for a second copy before filing. Waiting is how the fork happens: the second consumer arrives and writes its own version with a slightly different token set, and the finding then looks like duplication and is fixed as duplication, leaving both versions where they are. Two token sets for one concept are the fork already; use that as corroboration, never as the trigger. A unit noticed spread across boundaries is the finding: if it is only noted ("this looks similar to X"), the next reader must re-notice, re-scope and re-decide it.

## Repair shape, owner first

1. Pick the module whose change would be least surprising to the others.
2. Expose the decision as one function or table.
3. Route every consumer through it and delete the copies **in the same change**.

Polishing one copy of a fact that has several is the commonest wasted fix. Disagreeing copies are a bug report, not a style note.

## Variant: the fact stored twice

In the schema the same shape is the update anomaly: one fact on several rows, or in two columns (`status` plus `stage`, a JSON blob beside the scalars projected out of it, a "current" snapshot beside a versions table), so an update touches all of them or leaves them disagreeing. It survives in production for years because both reads still "work". A `# kept in sync by the app` comment is the confession. The repair is the same: one home for the fact, the rest derived (a view, a generated column).

## Variant: a status and its message

How a job or a check ended is one fact: its outcome, and the words that tell a person about it. Look at a job that runs three checks, where one check fails. The job writes `status = "succeeded"`. The failed check writes its own `error` text, and the job also adds a "check did not run" finding. Then two screens decide what to say. One says "wait for the checks to finish". The other says "two checks failed; run them again". Each copy is right by its own definition, and the person cannot tell which one to believe. The tell is a status in one place and a message about it composed in another place that can disagree with it. Repair:
1. Give each unit one outcome value, written once by the code that knows how the unit ended. Use a closed set, for example `pending`, `retrying(at)`, `needs_person(action)`, `failed(incident)`, `done`.
2. Derive the parent's status from its children's outcomes and its own steps (a final save or publish) by one rule that also says which children are required.
3. Make the status wording a lookup from that value in one table. Keep the diagnostic detail (which claim, the refused value, the provider's message) in the outcome's payload, not in a second status.
4. Delete the separate fields and extra findings that state the status a second time. The unit of the outcome is the unit of work: see [match the grain](../principles/reliability/match-the-grain.md).

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
