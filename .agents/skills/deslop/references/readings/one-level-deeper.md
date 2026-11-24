---
name: deslop-one-level-deeper
description: Review every repair one level deeper than the bug — six questions that find the decision a fix did not make, before it ships as a patch.
---

# One Level Deeper: Review the Repair, Not Only the Bug

*A bug is evidence of a decision the design never made. A repair that makes the symptom go away without making that decision is a patch, and the next incident in the same place adds another.*

Every finding in a pass comes with a repair, and every repair a person or a lane proposes passes through here before it is ranked or shipped. The questions are the ones an experienced owner asks when a fix is shown to them; asking them first is how a review predicts the owner's critique instead of receiving it.

## The six questions, in order

| # | Question | The patch it catches | The repair it points to |
|---|---|---|---|
| 1 | **Should the mechanism exist at all?** | Guarding, extending or loosening a control, notice, marker, cache key or flag that only exists to compensate | Delete it; build what it compensated for ([Patchwork](../principles/clean-code/patchwork.md)) |
| 2 | **Who owns this fact or shape?** Count the independent implementations | A second definition kept in step by hand: a reader's model beside the writer's dict, a cache key beside a freshness test | One owner; every other place derives from it ([Single Source of Truth](../principles/architecture/single-source-of-truth.md)) |
| 3 | **Is the information in the right channel?** | Metadata in content (markers, status sentences, sentinels, notes appended to prose); meaning recovered from text | A typed field, annotation, state or finding beside the content ([Metadata Beside Content](../principles/architecture/metadata-beside-content.md)) |
| 4 | **What moves this state forward, and what happens when it fails?** | A person as the hidden owner (a Retry button, a runbook); a failure that ends quietly | An owner per state; transient → bounded automatic recovery; unexpected → stop safely and fail loudly ([Liveness](../principles/reliability/liveness.md)) |
| 5 | **Is there a silent default?** | A reader of the system's **own** stored records that ignores keys it does not know (the writer and reader have drifted); a fallback value for a required field; a catch-all that logs and continues | An explicit legacy reader, a typed refusal, a loud failure someone must acknowledge ([No Silent Defaults](../principles/reliability/no-silent-defaults.md)). Tolerating optional extra fields from an **external** source is fine ([Postel's Law](../principles/reliability/postels-law.md)) |
| 6 | **What did the repair delete?** | A fix that only adds: a guard, an exemption, a special case | A repair that removes owners, branches and lines; report the [simplicity ledger](../library/measuring.md) |

Stop at the first question that changes the repair, then restart from question 1 with the new repair: a better repair often fails a later question the old one passed.

## Write the critique, then the repair

For each finding, write two sentences before proposing code:

> *The fix stops the symptom by* … *The bug is evidence that* … *was never decided; the repair is* … *and it deletes* …

If the second sentence cannot be written, either the finding is not understood yet (read the code that creates the state, not the code that fails on it), or the decision exists and was implemented wrongly: an off-by-one against a written contract is fixed in place, and the second sentence says *the existing decision* … *was implemented incorrectly*. If the repair deletes nothing, say why adding is right this time.

## What it found in practice (anonymized, one product, one day)

| Symptom | The first fix | One level deeper |
|---|---|---|
| A table was paid for again after a prompt change | Make the manual "draft again" path smarter | The manual path's reuse test and the screen's freshness test were two definitions of "current" (Q2); a fallback control with no decision behind it, beside a system that already redrafts, should not exist (Q1, Q4), while an expert's deliberate regenerate stays |
| Exported documents carried half sentences | Keep the marker in the export instead of stripping it | Metadata lived inside the prose (Q3); every renderer re-parsed it (Q2) |
| A summary told the regulator "not yet confirmed" after approval | Stop the generator writing status sentences | Workflow status is metadata (Q3); a derived document must go stale when its inputs change (Q4) |
| A signed record could not be read back | Add the missing field to the response model; ignore unknown keys elsewhere | Writer and reader each described the shape (Q2); "ignore" is a silent default (Q5); an unreadable signed record must fail loudly and be acknowledged (Q4) |
| Runs failed and waited for a person | A clearer Retry button | Transient failures need an automatic owner; a control with no decision behind it should not exist; a control that stands for a real decision stays (Q1, Q4) |

## When to stop

One level deeper, not five. If the deeper repair is a redesign, file it with its own model and ledger and ship the small fix now, labelled as the stopgap it is, linked to the redesign. Never let "the real fix is bigger" leave a user-facing bug open.

## See also

- [Patchwork](../principles/clean-code/patchwork.md), [A Special Case Is a Requirement](../principles/clean-code/special-cases.md), [Decide, Don't Cope](../principles/clean-code/decide-dont-cope.md): the diagnoses this reading applies to a repair.
- [When to relax](when-to-relax.md): the counterweight; a deeper repair that makes the code worse is not one.
