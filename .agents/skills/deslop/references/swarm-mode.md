---
name: deslop-swarm-mode
description: Deslop swarm mode — dispatch one parallel agent per principle lens, each forced to read its assigned principle files in full, then merge and adjudicate the reports. Use when the ask is coverage rather than speed, or when a named concern (separation of concerns, coupling) has been missed before.
---

# Swarm mode: coverage by construction

A single deslop pass has a structural blind spot, and it is not diligence. `SKILL.md` tells the pass to
*read the four category indexes up front and open a principle's full file only when a finding implicates it*.
That is a sound rule for cost and a fatal one for coverage: the pass can only open the file of a principle it
has **already suspected**. Principles whose names are visible triggers get opened — "this function is 300 lines"
summons Small Functions. Principles that require holding a boundary in mind do not. **Separation of Concerns**
is one table row reading *high cohesion, low coupling; one concern per part*; a pass reading a provider adapter
sees a working adapter and never opens the file, because nothing in the index row tells it what a violated
boundary looks like.

Measured consequence, on a real directory: six monolithic neutral passes reported behaviour defects, an
unowned setting, and a duplicated retry policy — and **not one separation-of-concerns finding**. Directed to
look at separation of concerns alone, an agent found several in the same directory within one pass. The
principle was never weak. It was never read.

Swarm mode fixes that with assignment rather than exhortation: **the principle library is partitioned into
lenses, every per-principle file belongs to exactly one lens, and a script refuses to dispatch unless that
partition is complete.** Each lens is one agent that reads its files in full and then scans the same target.
The orchestrator merges the reports. Coverage stops being a property of an agent's attention and becomes a
property of the assignment.

## 1. The instruments

Both live in [scripts/](../scripts/) and are run from the skill root:

```bash
python3 scripts/swarm_plan.py --repo <root> --target <dir> --out /tmp/deslop-plan   # plan first (§2)
python3 scripts/swarm_lenses.py --check                 # exit 1 unless every principle file is assigned once
python3 scripts/swarm_lenses.py --list                  # the lens table
python3 scripts/swarm_lenses.py --emit /tmp/deslop-swarm --target <dir> --repo <repo-root> --run 1
python3 scripts/swarm_merge.py /tmp/deslop-swarm/findings-*.jsonl --out /tmp/deslop-swarm/merged.md
```

The assignment itself is data, in [lenses.json](lenses.json) — eight lenses over 53 principle files, grouped
by **reading stance** rather than by category, because a lens is a way of looking, not a folder:

| Lens | Principles | The question it holds |
|---|---|---|
| `boundaries` | Separation of Concerns, Modularity, One Logical Unit One Home, Encapsulation, Orthogonality | Where does this code belong, and does each part hold one concern? |
| `duplication` | DRY, Single Source of Truth, Code Reusability | What knowledge exists more than once, and where is its single owner? |
| `coupling` | Law of Demeter, DI, Composition Over Inheritance, SOLID, CQS, Convention Over Configuration | What does each unit know about, or construct, that it should have been handed? |
| `parsing` | Parse Don't Validate, A Helper That Must Exist Is an Architecture Finding, No Silent Defaults, Fail-Fast, Postel's Law, Design by Contract | Where does an external value enter, and which single component turns it into a decision? |
| `shape` | Small Functions, Guard Clauses, Cognitive Load, Cyclomatic Complexity, SLAP, KISS, YAGNI | How big and how tangled is each unit's control flow? |
| `legibility` | Self-Documenting Code, Documentation Discipline, Elegance, Legibility, Least Surprise, Patchwork, Decide Don't Cope | Can a competent stranger read this without the author present? |
| `guarantees` | An Unclaimed Guarantee, Immutability, Idempotency, Observability, Resilience, Least Privilege, Boy Scout Rule | What is promised, who claims the promise, what happens when it breaks? |
| `data-layer` | the twelve database principles | What does the schema promise, and where is an invariant only in application code? |

Every lens also reads [auditing.md](auditing.md) (the report format and the input census) and
[when-to-relax.md](when-to-relax.md) (the guardrail against manufacturing violations). Grouping is deliberate:
principles whose findings would otherwise be reported twice under two names sit in the same lens, so the merge
step sees one finding rather than a phantom corroboration.

## 2. Plan the partition before you dispatch

Eight lenses over every directory is the cross-product, and it is the wrong shape twice: expensive, and
**mis-scoped** — a boundary defect is invisible to an agent that reads one file at a time, while a data-layer
drill over a module with no SQL produces nothing but an agent justifying its reading list. So the target is
partitioned first, and the partition is a written artifact:

```bash
python3 scripts/swarm_plan.py --repo <root> --target <dir> --out /tmp/deslop-plan --budget 24
# writes plan.md (selected cells, wave order), candidates.md (the whole permutation space + every score
# component + why each cell stood or fell), and dispatch.sh (ready to run)
```

The plan is four steps — **enumerate, score, select, order** — and the slice families it enumerates are
only these:

| Tier | What runs | Why this scope |
|---|---|---|
| **Orientation** | `boundaries`, `coupling`, `shape`, `legibility`, `duplication` — whole target, one agent each | these findings *span* modules; split them per module and the evidence that two places disagree is cut in half |
| **Module drill** | a signal-gated lens over **one module**: `parsing` where external input enters, `guarantees` where async/retry/lock/lifetime appears, `data-layer` where SQL, migrations or an ORM model does | the finding is local to the module and only visible if the reader holds that one principle while reading that one directory |
| **Archetype drill** | the lenses a module's *role* characteristically violates, inferred from its path segment — an `adapters/` or `providers/` module gets boundaries + parsing + coupling, a `workers/`/`scheduler/` module gets guarantees, a `repo/`/`store/`/`migrations/` module gets data-layer | roles have signature defects; the grep is quiet precisely when the code is confidently wrong |

Plus a fourth family the table above cannot hold: **cross-folder concept clusters** — every retry, every env
reader, every provider adapter, every logger, wherever they live. Those are cells a directory walk cannot
express, and they are where duplicated knowledge hides.

### Scoring, budget, waves

`swarm_plan.py` prints every component, so the ranking can be argued with rather than trusted:

```
score = 0.34·signal + 0.26·fit + 0.18·cross + 0.22·size      then  ×(1 − 0.35·overlap)
```

- **signal** — evidence density: does the slice contain the thing at all (env access, async/retry/lock, SQL).
- **fit** — observed signal (1.0) beats concept (0.9) beats role archetype (0.72): a grep is stronger evidence
  than a directory name.
- **cross** — the slice crosses folders; only concept clusters do.
- **size** — mid-size slices score highest: big enough for a defect to hide, cheap enough to afford.
- **overlap** — *per lens*, never across lenses. Different lenses on the same files is the point of a swarm;
  the same lens re-reading the same files is money burnt. This is the rule that stops a whole-tree concept
  cluster from vetoing every module cell.

Selection is greedy under `--budget` (default 24 agents) with caps — at most `--per-module` (2) cells per
module, a per-lens cap of `max(3, budget/5)`, and `candidates.md` recording for **every** rejected cell whether
it lost to budget, to a cap, or to redundancy. The chosen cells are then ordered into waves of `--wave` (4),
orientation first, cheapest evidence next.

`swarm_plan.py` also reports LOC, file count and the biggest file per module and the signal counts that earned
each cell, so the plan can be argued with before it is paid for. Two rules it enforces because they are how
planning goes wrong:

- **Never split a global lens per module**, and never add a lens to every module to look thorough. If a plan
  looks thin, add **modules**, not lenses.
- **Test trees are not slop targets** by default. They are fixtures, they are allowed to repeat themselves,
  and a guarantees drill over them reports the harness. `--include-tests` opts in when a test *is* the target.

The orchestrator owns the plan, not the script: the archetype tier is a heuristic on a path name, so drop a
cell whose evidence is only that word, and add a cell where you know the codebase and the grep does not.

### The directed deep dive

There is a class of slop that only a **one-module, one-principle** agent finds: the agent reads every file in
the module holding exactly one principle, not eight. It surfaces as a dialog rather than a sweep, and it is the
right instrument in two cases — a sweep hinted at a defect and could not substantiate it, or the module *is*
the archetype of a concern (a provider adapter and separation of concerns). Dispatch it with the drill form:

```bash
python3 scripts/swarm_lenses.py --emit /tmp/deep --repo <root> --target <one-module> \
  --only separation-of-concerns-lens --label <module> --run 1
```

`--only <lens>` is also the answer to *"look at X specifically"* — the ask that a general pass cannot satisfy,
because the general pass decides for itself what to open.

## 3. Dispatch

The contract is harness-neutral: **one process per lens, the emitted prompt passed through verbatim**, all
launched in parallel. That is a shell loop with `&` and a background runner in Codex/Claude/OpenCode, or a
`delegate_task` fan-out from an orchestrating agent. What must not vary:

- **The prompt is not paraphrased.** It carries the reading list, the read-before-scan order, the read-only
  constraint, and the JSONL contract the merge step consumes.
- **Fresh checkout per run, read-only.** An agent that can write is an agent that refactors while auditing,
  and the next lens then reports the wreckage.
- **Never merge lenses to save agents.** Four lenses over 53 principles puts SoC and Modularity back in the
  same context as size and style, which is exactly the ranking contest that loses.
- **`--only <lens>` is the directed pass.** When the ask is *"look at separation of concerns specifically"*,
  that is one lens, not the whole library — and it is the correct answer to a finding that a general pass missed.

## 4. Merge, adjudicate, then file

`swarm_merge.py` collapses N JSONL reports into three tables:

| Table | Meaning | What the orchestrator owes it |
|---|---|---|
| **Corroborated** | same locus, same principle, ≥2 lenses | read the source line before believing it: two lenses can share one misreading |
| **Single-lens** | one lens, one instance | **not weaker.** One instance is enough to be a real finding; a swarm only says it was subtle. Verify at the line, then file |
| **Disputed** | same locus charged under two different principles | an adjudication, not a duplicate — one defect, one owner, one principle |

Then file **one issue per concern**, never one per lens, each verified at its source line. The merge is a
bookkeeping instrument, not a verdict: a swarm multiplies false positives exactly as readily as true ones,
because eight agents each under pressure to justify their reading list will invent findings. A lens that
reports zero findings and quotes no code is a **failed lens**, not a clean target — re-run it.

## 5. Cost and when not to use it

| Ask | Mode |
|---|---|
| "is this diff sloppy?", one file, a PR review | ordinary pass — swarm cost is unjustified |
| "run a deslop pass over this directory" | ordinary pass, then a swarm if the report looks thin in one dimension |
| "we keep missing X" / a named concern came back empty | `--only <lens>` first, then a swarm over the whole target |
| campaign ("across the board", LOC targets) | [campaign-mode.md](campaign-mode.md) for the rewrites; a swarm first for the findings |

Rule of thumb: a swarm is **8 processes against one target commit**. On a large codebase, split the target
directory per wave — the merge step unions waves perfectly well, and a wave that dies does not lose the others.

## 6. Control

A protocol that promises coverage is tested like a detector: does the swarm find what the monolithic pass
missed, on the same commit and the same neutral prompt? Recorded runs go here, version → what changed →
verdict, including failures.

| Run | Setup | Result |
|---|---|---|
| 1 | *(to be recorded)* | |

## 7. What this is not

- **Not a substitute for reading the code.** Eight lenses against a skimmed file produce eight confident
  misreadings; the prompt says whole files for that reason.
- **Not a licence to skip the indexes.** The lens prompt is budgeted to open 5–12 files; the indexes still
  explain how the library is organised when the target's first findings need a second principle.
- **Not the campaign fleet.** Campaign mode's parallelism is over *files being rewritten*, with file-level
  disjointness so agents do not clobber each other. This is parallelism over *principles being applied* to the
  same files, read-only. Confusing the two produces eight agents editing one file.
