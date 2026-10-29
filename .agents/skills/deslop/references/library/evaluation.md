---
name: deslop-evaluation
description: What a pass actually proved — the control runs, their numbers, and how to add the next one.
---

# Evaluation

A pass is a claim about coverage, and a claim needs evidence of two different kinds. Keep them apart, because a
control that shows a rule **fires** says nothing about whether the rule is **right**, and the reverse.

| Instrument | Question | How |
|---|---|---|
| **control** | does the reading find the planted defect, and decline the look-alike? | a planted fixture, a fresh agent, a neutral prompt, read-only |
| **review** | is the rule true — semantics, overreach, decidability, prior-art honesty | an independent harness with a challenging brief and a verdict (SOUND / NEEDS-CHANGE / UNSOUND) |

## Recorded runs

| Date | Run | Result |
|---|---|---|
| 2026-10-20 | `_truthy` → *A Helper That Must Exist Is an Architecture Finding*: ten control runs across fresh agents | v1 framed at the type and passed its control **2 of 2** while being **UNSOUND** on review (a context signals cancellation, it never establishes completion); v2 was sound and fired **0 of 1**; restoring the trigger in the index row got it to **1 of 1**. The lesson — soundness and recall are separate properties — is in `readings/detecting-slop.md` |
| 2026-10-21 | one directory, **monolithic** pass vs **eight group readings**, same commit, neutral prompt | monolith: 19 findings / 9 principles. Groups: **55 findings, 54 distinct, 25 principles**, of which **17 were never touched** by the monolith (`encapsulation`, `orthogonality`, `SOLID`, `immutability`, `observability`, `least-privilege`, `fail-fast`, the helper principle, `small-functions`, `SLAP`, `cognitive-load`, `guard-clauses`, `KISS`, `self-documenting-code`, `documentation-discipline`, `least-surprise`, `elegance`). `data-layer` returned **0 with an explicit no-schema statement** — a healthy declining cell. 34 loci were charged under two principles, 0 corroborated |
| 2026-10-21 | data layer, **planted fixture** (unindexed FK used by a join and a parent delete, hand-maintained total, comma-joined column, copied address), two arms | baseline charged the per-project query loop as **KISS**; the enriched group charged it under *Every Join Needs an Access Path on the Side Being Probed* — **fired 1 of 1**. The normal-form additions changed **no** detection: the baseline already caught the column and the copy |
| 2026-10-22 | taxonomy, **two independent reviews** (Claude Code, OMP) | both endorsed role-in-the-pass, both found the same single misplacement (`readings/detecting-slop.md` classified as a library reference in the data) and the same unenforced property (folder-vs-role was claimed, never checked) |
| 2026-10-28 | nine **codebase slop indicators** folded in as seven files (five architecture, one reliability, one promoted out of `parse-dont-validate`), planted **14-file fixture** with a layer-first tree and a real commit history, two arms | baseline (54 principles): 8 distinct principles, **none** of the seven existed; it still *reached* the illegal-state model and charged it under **Parse, Don't Validate**, and reached the domain/model boundary crossings under **Separation of Concerns** — the defect was found, the owner was wrong. Treatment (61 principles): **10 distinct principles**, and the pass **hit its 10-finding cap**, so discovery fired **5 of 7** (`implicit coupling`, `shotgun surgery`, `layering violations`, `illegal states unrepresentable`, `errors at the boundary`). The two the cap displaced were given **usability controls**: `god-file` fired **1 of 1** and `pass-through-wrappers` **3 of 1** (three instances, with the legitimate store seam and the policy-carrying helpers correctly declined). Both usability runs then corrected their own files — `god-file` said "three tests" and listed five, and had no history threshold (now ten commits, with the name test sufficient alone on a squashed history) |

## Adding a run

1. **Plant the defect, do not source it from the rule.** A fixture derived from the principle under test proves
   consistency, not detection. One small repo per principle lives under `fixtures/`.
2. **Declare the alternatives** the fixture contains: the legitimate cases a reading must *decline*. The
   corpora live in [../../fixtures/README.md](../../fixtures/README.md) — three small repos, two of them planted and
   one deliberately clean.
3. **Two arms minimum** — the shipped reading as the baseline, the changed reading as the treatment — same commit,
   same prompt, read-only.
4. **Record the verdict here**, including the failures; a table with only passes is a decoration.
5. **Say which instrument produced which claim.** "Fired 2 of 2" is a recall measurement; "sound" is a review.
   Never let one speak for the other.
