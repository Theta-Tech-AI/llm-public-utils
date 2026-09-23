---
name: deslop-clean-code-patchwork
description: Deslop principle — Patchwork: compensating code you cannot simplify by deleting; find the decision it re-derives and re-state it.
---

# Patchwork

> "There's no way this is the cleanest way to simply achieve the goal. This is patchwork upon patchwork."
> — the report that motivated this principle, from a reader who could not name a single wrong line

Patchwork is code that **cannot be made simpler by deleting**. Every line answers a real incident. Every
branch was added for a reason someone can still cite. A reviewer can spend an hour in the file and find
nothing they are willing to remove — and still know, correctly, that the whole thing is wrong.

That gap between "no wrong line" and "obviously wrong file" is what this principle names. It is the
failure mode a LOC campaign cannot see, because patchwork is neither duplicated nor dead: it is
**load-bearing against history**.

## Why it happens

Patchwork is what you get when the code answers at **run time** a question that a decision would have
answered at **design time**.

The mechanism is unremarkable at every step:

1. An incident happens. A guard is added at the site where it happened.
2. The guard returns an untyped "something went wrong" that the next layer proxies upward.
3. A second incident happens, adjacent. A second guard is added beside the first.
4. Nobody is wrong at any point. Each commit is small, reviewed, and justified by a bug.

There is no moment where a bad decision is made — which is exactly why there is no moment where the
design gets reconsidered. The shape is never chosen; it is *accumulated*. Ten incidents later the reader
meets a sequence of independent checks around one mutation, and asks the only useful question:

> **Why does this code believe it must re-derive the legality of state it just created?**

## What the reader is actually seeing

Three tells, in the order they usually surface:

- **A guard ladder.** `problem = check_a(...); if problem is not None: return problem` repeated until the
  mutation finally happens. This is a decision procedure written as a linear scan. It cannot be composed,
  it cannot tell you that a case is missing, and its order is load-bearing in a way nothing states.
- **A self-referential module docstring.** Docstrings that recite which check precedes which, why one
  guard is not blocking, which incident produced which branch. When the docs explain the guard order, the
  guards are the design.
- **A "must stay" list.** A comment or an issue enumerating the parts of this file that cannot be touched.
  Patchwork grows that list every time; a design would not need it.

## The diagnostics

Run these before proposing any simplification of a file that felt like patchwork.

**1. Count compensating lines against doing lines.** State the module's purpose in one sentence. Every
line that exists to check, repair, coerce, align, de-duplicate, recover, or police the doing is
*compensating*. When compensating outnumbers doing, the interface declined a decision — and that, not any
individual line, is the finding. (Worked figure below.)

**2. Name the decision the code is re-deriving.** If you can write it as one sentence — "a paragraph is
identified by the node it belongs to, not by a heading the model typed" — then the repair exists, and it
is at the interface. If you *cannot* write that sentence, stop: the code has no design yet, and
simplifying it now will only produce a better-organised patchwork.

**3. Ask what would make the branch unrepresentable.** Not "how do I make this guard cheaper" but "what
change to the shape means this guard has nothing to guard?". A guard whose condition cannot arise in the
new representation is deleted, not ported.

## Why subtraction fails — and what to do instead

**You cannot simplify patchwork incrementally.** Delete one guard of thirteen and you have moved the
failure, not removed it: the remaining twelve were calibrated against the first one's behaviour. This is
the property that makes patchwork feel undefeatable, and it is why "reduce LOC by 30%" campaigns stall on
exactly these files while sailing through everything else.

The repair is a **re-decide**, and it has a characteristic shape:

1. **State the interface decision** — the one that makes the illegal combination unrepresentable.
2. **Change the interface**, not the guards.
3. **Let the guards collapse together** in the same change. They were never independent; porting them
   one at a time is what makes the change look unsafe.
4. **Prove behaviour parity on the artifact, not the diff.** Accreted code encodes incidents that tests
   named after them. Regenerate the real output and diff it against ground truth; run the suite; then
   delete the incidents the new shape cannot produce.

And one caution, because this is the expensive one: **a re-decide is a behaviour-change review, not a
cleanup.** It belongs in a `changes-behaviour` lane with an owner, not in a mechanical sweep. Sending a
sweep at patchwork produces churn — or worse, a "simplification" that quietly drops the incident the
tenth guard existed to prevent.

## Worked example (anonymized)

A production regulatory-authoring product, one agent's tool layer, 3,902 non-test lines across 16 modules
for three jobs: draft paragraphs, prove they are all drafted, ground them in citable evidence.

- Grounding — named as the *least* important of the three by its own operator — carried **53%** of the
  lines.
- Inside it, ~187 lines were heading normalisation, forced-heading identity alignment, sibling-heading
  collision detection and duplicate fingerprinting. None of that is grounding. It is the system
  **reconstructing structure the write interface failed to carry**: the agent handed over a heading string
  and a body, so the code afterwards had to guess whether the heading duplicated a sibling, whether the
  body repeated an earlier paragraph, whether the heading was doubled inside the content, and what depth
  it belonged at.
- Diagnosis by the three questions: *(1)* compensating lines outnumbered doing lines in the write path.
  *(2)* the decision was nameable in one sentence — **a paragraph belongs to a node, not to a heading
  string**. *(3)* with a node-keyed write, the heading string does not exist to be aligned, the sibling
  cannot be collided with, the depth cannot be coerced, and a re-write overwrites instead of needing a
  duplicate fingerprint.

The repair was not a trim. One interface change (`write_subsection(node_id, body, citations)`) plus one
typed result collapses the heading/dedupe family, four policing mechanisms, a count target and its
padding breaker, three race checks, two completion helpers — and **retires an entire 471-line remediation
module**, because the state it repaired (a persisted paragraph with no citation) becomes unrepresentable
at the write boundary.

## Relationship to the neighbouring principles

| Principle | Relationship |
|---|---|
| [**Decide, Don't Cope**](decide-dont-cope.md) | The parent diagnosis: patchwork *is* unmade decisions compounding as entropy. This file is its repair procedure. |
| [**Parse, Don't Validate**](../architecture/parse-dont-validate.md) | The usual shape of the fix — illegal states made unrepresentable at the boundary |
| [**Single Source of Truth**](../architecture/single-source-of-truth.md) | The symptom patchwork most often masquerades as: several places agreeing by hand |
| [**Boy Scout Rule**](../reliability/boy-scout-rule.md) | The rule that does **not** fix patchwork — incremental tidying is what produced it |
| [**Measuring a campaign**](../measuring.md) | LOC and duplication harnesses cannot see patchwork; say so in the report rather than implying coverage |
| [**Campaign mode**](../campaign-mode.md) | Sweeps find dead weight and duplication. Patchwork needs the `changes-behaviour` lane instead. |
| [**Legibility**](legibility.md) | The reader's experience: patchwork is the file where the map in the reader's head cannot be built from anything on screen |

## Summary

1. **Patchwork is not one bad decision — it is the absence of a decision**, accumulated one justified
   incident at a time.
2. **The tell is irreducibility**: every line is defended, and the whole is unowned.
3. **Diagnose by compensation ratio, by naming the re-derived decision, and by asking what would make the
   branch unrepresentable.**
4. **Repair by re-deciding the interface and letting the guards collapse together** — never by removing
   them one at a time.
5. **Do not send a mechanical sweep at it.** Sweeps find duplication and dead code; patchwork has neither,
   and a sweep that "simplifies" it can silently drop the incident a guard existed to prevent.
