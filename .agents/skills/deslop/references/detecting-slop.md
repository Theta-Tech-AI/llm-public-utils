---
name: deslop-detecting-slop
description: How deslop detection is packaged — what automated tools cannot see, why the detector is prose an agent applies, and the control a detector script must pass to earn its lines.
---

# Detecting Slop

Two questions decide how much of this library ever gets used: **which failures detection can see at all**,
and **where detection lives**. Both are operational rather than philosophical — a rule no pass ever trips
over may as well not be in the library.

## What the tools cannot see

Run the standard tools, believe what they cover, and state what they do not. Their blind spots are not
exotic; they are precisely where the expensive slop lives.

- **Cyclomatic complexity counts decisions inside a function.** When a specialist module is forked from a
  general one, the general one gains no branches — the complexity is *outside the metric's view*, in a
  second file. A codebase can carry thousands of lines of silent duplication at a mean cyclomatic
  complexity of 4.
- **Clone scanners compare text, or AST shape.** The expensive copies rename everything, reorder branches
  and re-express one design in another idiom. A copy renames its files, functions and variables and shares
  no lines, so name-matching finds only the copies nobody bothered to rename. What survives a rename is what the
  code *does*: the primitives it calls. (The behaviour-first hunt is in
  [duplication.md](duplication.md) and [one-logical-unit-one-home.md](architecture/one-logical-unit-one-home.md).)
- **Linters and type checkers see contracts, never cohesion.** A unit split across four packages is
  perfectly typed and perfectly linted.
- **Coverage sees what tests touch**, and a fork is usually well covered — that is why it was written.

So a real finding is often *the reader's*: someone opened three files to answer one question. **Treat that
as data.** It is the highest-yield detector in this library and the one no tool replaces.

## Detection is prose, and that is the design

Instructions an agent applies generalise. A script encodes one generation of one rule.

The library **is** the detector. When a pass needs a tell, the tell belongs here, as text an agent reads and
applies with judgement — not as a program that must be rewritten every time a principle's wording sharpens.
A detector script is a **second source of truth for "what slop looks like"**, and second sources drift: the
script keeps firing at a pattern the principle has since narrowed, and the pass then reports findings the
library no longer supports.

**A script must earn its lines.** Settle it with a control, not an opinion:

1. Take a genuinely fresh agent — not the session that wrote the rule, which already knows the answer — and
   give it **only the markdown**, on the same checkout.
2. Give it the same task: find this class of finding.
3. Compare findings, tool calls and wall time.
4. If the markdown-only agent finds the same things in comparable effort, **delete the script**.

**Verify a finding on the current tip before you file it** — a copy may already be consolidated, and an
unverified report costs the reader the check you skipped. File it with the evidence, never as a note.

Reference results, for calibration. Each fresh agent had only the markdown, on a ~100k-line backend:

| Detector tried | Fresh markdown-only agent | Verdict |
|----------------|---------------------------|---------|
| File-name and role-word scanner, ~130 lines; its first version missed the main finding, and its later sections were fitted to one example | Found the main sibling set plus lock and activity copies in 12 calls, about a minute | **Deleted** |
| Name-blind fingerprint scanner, ~90 lines (library calls, SQL tables, status values, exceptions per file, ranked by overlap) | Nine verified sets in 39 calls and under three minutes, by grepping for a primitive and reading the hits: lease-heartbeat threads (6), content hashing (6), TTL caches (4), schema bootstrap (6), run-worker skeletons (4), retrying HTTP clients, project-lock context managers, object-store wrappers (8), CSV exports — the scanner ranked the heartbeats and the object-store wrappers first and missed most of the rest | **Deleted**; the method is in [duplication.md](duplication.md) |
| Field-overlap clustering of record shapes, ~160 lines | Ten calls and under a minute, by writing a throwaway field-overlap script: the activity event described 6 times, user identity 5 times | **Deleted**; the recipe is in [duplication.md](duplication.md) |

The pattern repeats: a detector fitted to the finding in hand describes that finding, while an agent working
from a *method* (grep for the primitive, group by content, read the hits) generalises past it. Each scanner
cost more lines than the method and missed sets the method reached — which is why none of the three ships
with this library.

## Where a script does earn its keep

Three properties, all required:

- **Mechanical** — no judgement anywhere in the decision it makes.
- **Exhaustive** — it must sweep the whole tree; a sample is not a sweep.
- **Stable** — the rule it encodes will not move as the principles are refined.

Token and AST clone matching qualifies — `jscpd`, `pmd-cpd`, and `scripts/astdup.py` / `scripts/tsdup.cjs`,
which hash function bodies with every name and constant erased so renamed copies collapse, and print a
redundant-line total usable as a CI ratchet. This class is admitted on its **properties**, not on a control:
the decision is mechanical, the sweep is exhaustive, and the rule does not move when a principle is reworded.
Finding *which primitive a mechanism uses* does not qualify — that is one grep, and shell is the ceiling for
cheap views.

```bash
# every file that hand-rolls a heartbeat thread — then read the hits
grep -rlE 'Event\(\)' <src> --include='*.py' | xargs grep -lE '\.wait\(' | xargs grep -lE 'Thread\('
```

If a view fits in one command, it belongs in the instructions, not in a file. See
[duplication.md](duplication.md) for the primitives to grep for and the token scanner's proper role.

## Detection runs twice: at design, and at audit

The views above audit code that already exists. The cheapest place for this library is the design, before
the second copy exists: **re-read the applicable principles while designing, not only when auditing.** The
design-time question is not "is this slop?" but "am I about to make a second home for something that
already has one?" ([one-logical-unit-one-home.md](architecture/one-logical-unit-one-home.md)). A fork caught
while it is still a plan costs nothing to avoid; the same fork after it has callers costs a consolidation
campaign.

## A finding is an issue, not a note

The audit's output contract, and the reason a good observation still goes to waste: **a finding that changes
code must leave the pass as an actionable item.** For a consolidation that means the proposal — the unit
named, the owning module named, the pieces to move listed. "This looks similar to X" in a report is a note;
the next reader must re-notice it, re-scope it and re-decide it on your behalf. A note is a finding you
declined to finish.

In relation to other references, detecting slop governs the detector rather than the code:

| Reference | Relationship |
|-----------|--------------|
| [**Hunting Duplication**](duplication.md) | Its scanners look for repeated text; this file is about the detector's own packaging |
| [**Auditing**](auditing.md) | The pass this file arms — the judgment stays with the agent |
| [**Measuring a Campaign**](measuring.md) | The same discipline, a different object: measure the mechanism, not your part in it |
| [**Extending the Library**](extending-the-library.md) | A detector script is a library artifact; the discovery-first rule applies before writing one |
| [**One Logical Unit, One Home**](architecture/one-logical-unit-one-home.md) | The finding class that motivated the control test |

## Summary

1. **State what your tools cannot see.** Complexity counts decisions inside a function; clone scanners
   compare text; neither sees a design forked into a second file.
2. **A copy renames everything except what it does**, so search by primitive and by field content, never by
   file or function name. "I opened three files to answer one question" is a finding, not a feeling.
3. **Detection is prose an agent applies** — a script is a second source of truth and drifts from the
   principles it encodes.
4. **Make a script pass a control**: a fresh, markdown-only agent on the same checkout. Match its findings
   and the script is deleted.
5. **One-line shell is the ceiling for cheap views**, and a finding that changes code leaves the pass as a
   named, actionable item — never a note.
