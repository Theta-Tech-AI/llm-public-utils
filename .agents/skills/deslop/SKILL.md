---
name: deslop
description: "Analyze and refactor code against a library of 50+ coding principles — clean code, architecture, reliability, and data layer — finding and fixing slop, duplication, dead code, over-abstraction, god files and needless complexity, measuring it honestly, and running whole-codebase simplification campaigns. It also extends the library, by researching a missing principle and merging it in. Use for deslop passes, code-quality and PR review, dedup and cleanup sweeps, tech-debt triage, refactor planning, complexity analysis, or when code is called messy, bloated, overcomplicated, copy-pasted, hard to read, or in need of a cleanup."
---

# Deslop: Code Quality Analysis Command
<sub><sup>Note: This skill is ≈17k tokens across SKILL.md + references/ as of 2026-09-16 (≈44k including every per-principle file; open a principle file only when a finding implicates it)</sup></sub>

> A comprehensive command `/deslop` or $deslop (depending on your harness) for identifying and fixing "slop" in your codebase.

This command combines a code analysis workflow with an extensive library of coding principles living in [references/](references/). When you run `/deslop [file-or-directory]`, or even just `/deslop` or perhaps `/deslop my frontend typescript code` the AI will read your code, cross-reference it against these principles, and suggest specific fixes with before/after examples.

**Scoped pass or whole-codebase campaign?** The default is a pass over the file, directory, or diff you name. When the ask is a **campaign** — "massive simplification", "across the board", "minimum 30% LOC", "break up the god files", "get it all done, no excuses, present me a PR" — follow [references/campaign-mode.md](references/campaign-mode.md) instead, and measure it with [references/measuring.md](references/measuring.md).

Whether or not you use this deslop command on your code base, you should read all the coding principles yourself, as a human - you might actually learn something useful.

---

## Workflow references (read these to run a pass)

| File | When |
|------|------|
| [references/auditing.md](references/auditing.md) | **Always** — the audit itself: persona, the mode question, the autonomy rule, violation report format, and the **input census** (for each external input: who owns turning it into a decision, and how many places re-interpret it — zero owners or several is a finding, reported even when it ranks last) |
| [references/loop-until-dry.md](references/loop-until-dry.md) | Thorough passes ("keep going") — iterate until a full scan finds nothing actionable |
| [references/swarm-mode.md](references/swarm-mode.md) | **Coverage passes** — "look for X specifically", "we keep missing things", or any audit that must cover the whole library: one parallel agent per principle lens (8 lenses over 53 principle files), each forced to read its assigned files in full, planned per module by `scripts/swarm_plan.py`, merged and adjudicated by `scripts/swarm_merge.py` |
| [references/campaign-mode.md](references/campaign-mode.md) | **Whole-codebase campaigns** — "massive simplification", "across the board", "minimum 30% LOC", "get it all done", "present me a PR". The five sweeps, the target discipline, running it at scale, and the delivery protocol |
| [references/measuring.md](references/measuring.md) | **Any pass that will claim a number** — the four measurement harnesses, the unbiased task corpus, the metrics that carry the story (nesting depth, `elif` chains, cyclomatic complexity), and the honest before/after reporting skeleton |
| [references/extending-the-library.md](references/extending-the-library.md) | **Adding a principle** — the ask is a *gap* in the library, not a pass over code: discovery against every existing principle, research, the house draft format, both indexes, and the publish path |

## Plan the pass before you audit (the planning step)

**A pass is planned, not merely started.** The empirical fact this section exists for: an agent reliably finds
slop when it is pointed at **a specific piece of code with a specific principle in mind**, and finds
substantially less when told to "audit this directory" — the general pass reads the indexes, picks what
*looks* implicated, and the principles that need a boundary held in mind are never opened at all. So work is
decomposed into **cells**: one principle group against one slice of code. Four steps, in this order:

1. **Enumerate the permutations.** The slices are not only directories. Name them all before choosing:
   the whole target; each module; each module × the role it plays (an `adapters/` module against boundaries and
   parsing, a `workers/` module against guarantees, a `migrations/` module against the data layer); and
   **cross-folder concept clusters** — every retry implementation, every env reader, every provider adapter,
   every logger, wherever they live. That last family is the one a directory walk cannot express, and it is
   where duplicated knowledge hides. The principles side of the permutation is the lens grouping in
   [references/lenses.json](references/lenses.json) (8 lenses over 53 principle files).
2. **Score the cells** on evidence, not enthusiasm: does the slice actually contain the signal (env access,
   async/retry/lock, SQL), how well does the lens fit (observed signal > role archetype > concept), is the
   slice cross-cutting, and is it the right size — mid-size slices both hide defects and remain affordable.
3. **Select under a budget.** Never run the cross-product. Pick the best N cells (default budget ~24 agents)
   with caps — at most 2 cells per module, a per-lens cap, and a redundancy penalty for the same lens
   re-reading files it is already reading. Different lenses on the same files is the *point* of a swarm; the
   same lens twice is money burnt.
4. **Order into waves**, cheapest evidence first, and let each wave reroute the next: a thin cell is evidence
   about the code, and a rich one marks a neighbourhood worth a one-module, one-principle deep dive.

All four are implemented — run them, do not improvise them:

```bash
python3 scripts/swarm_plan.py --repo <root> --target <dir> --out /tmp/deslop-plan --budget 24
#   → plan.md        selected cells in wave order, with the reasoning per cell
#   → candidates.md  the whole permutation space: every score component, and why each cell stood or fell
#   → dispatch.sh    ready-to-run prompts, one agent per selected cell
```

Mechanics, prompt contract, merge and adjudication: [references/swarm-mode.md](references/swarm-mode.md). For a
one-module or one-principle ask — *"look at separation of concerns in the provider adapters"* — skip the plan
and dispatch the cell directly: `swarm_lenses.py --emit <dir> --only boundaries --target <module>`.

**The plan is a draft for the orchestrator, not a verdict.** The archetype tier guesses from a path name, so
drop a cell whose only evidence is that word, and add one where you know the codebase and the grep does not. If
a plan looks thin, add **slices**, never a lens across every module — that cross-product is the thousand-agent
swarm this step exists to prevent.

## Principle references (indexes)

Each index below is a short table of principles and their one-line essences, linking to self-contained per-principle files under `references/<category>/`. **Read the indexes up front; open a principle's full file only when a finding implicates it** (or when fixing a violation of it).

Know the cost of that rule: the pass can only open a principle it has already suspected, so principles that need a boundary held in mind — above all **Separation of Concerns** — are routinely never read. When the ask is coverage rather than speed, or a named concern has been missed before, run [references/swarm-mode.md](references/swarm-mode.md) instead of reading harder: it partitions the library into lenses, forces each agent to read its files before scanning, and merges the reports.

| File | Contents |
|------|----------|
| [references/clean-code.md](references/clean-code.md) | **Clean Code** — KISS, YAGNI, Small Functions, Guard Clauses, Decide Don't Cope, Cognitive Load, Cyclomatic Complexity, SLAP, Self-Documenting Code, Documentation Discipline, Elegance, Legibility, Least Surprise, Patchwork, An Unclaimed Guarantee |
| [references/architecture.md](references/architecture.md) | **Architecture** — DRY, Single Source of Truth, Separation of Concerns, Modularity, One Logical Unit One Home, Encapsulation, Law of Demeter, Orthogonality, DI, Composition Over Inheritance, SOLID, Convention Over Configuration, CQS, Reusability, Parse Don't Validate, A Helper That Must Exist Is an Architecture Finding, Immutability, Idempotency |
| [references/reliability.md](references/reliability.md) | **Reliability** — Fail-Fast, No Silent Defaults, Design by Contract, Postel's Law, Resilience & Graceful Degradation, Least Privilege, Boy Scout Rule, Observability |
| [references/when-to-relax.md](references/when-to-relax.md) | **When to relax rules** — contexts where principles are over-applied, plus the meta-principle |

## Situational references (read when relevant)

| File | Read when |
|------|-----------|
| [references/data-layer.md](references/data-layer.md) | The target has a database — schema, SQL, migrations, indexes (**The Data Layer**) |
| [references/lenses.json](references/lenses.json) + [references/swarm-mode.md](references/swarm-mode.md) | Dispatching a swarm pass — the lens assignment and the dispatch/merge protocol (validated by `scripts/swarm_lenses.py --check`) |
| [references/duplication.md](references/duplication.md) | Running a dedup sweep — hunting duplication beyond token scanners: the primitives to grep for, the field-overlap recipe for one entity described many times, and the shape-clone scripts in [scripts/](scripts/) |
| [references/detecting-slop.md](references/detecting-slop.md) | Building or questioning a detector — what the tools cannot see, and the control a detector script must pass to earn its lines |
| [references/case-study-simplification-agent-fleet.md](references/case-study-simplification-agent-fleet.md) | Worked KISS example — a real pass that collapsed an LLM agent fleet into one agent |
| [references/further-reading.md](references/further-reading.md) | Background bibliography and concept attribution (not needed mid-audit) |

---

*Run `/deslop [file-or-directory]` to analyze your code against these principles and let the agent fix any slop it detects.*
