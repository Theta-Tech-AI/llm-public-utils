---
name: deslop
description: "Analyze and refactor code against a library of 50+ coding principles — clean code, architecture, reliability, and data layer — finding and fixing slop, duplication, dead code, over-abstraction, god files and needless complexity, measuring it honestly, and running whole-codebase simplification campaigns. It also extends the library, by researching a missing principle and merging it in. Use for deslop passes, code-quality and PR review, dedup and cleanup sweeps, tech-debt triage, refactor planning, complexity analysis, or when code is called messy, bloated, overcomplicated, copy-pasted, hard to read, or in need of a cleanup."
---

# Deslop: Code Quality Analysis Command
<sub><sup>Note: This skill is ≈17k tokens across SKILL.md + references/ as of 2026-09-16 (≈44k including every per-principle file; open a principle file only when a finding implicates it)</sup></sub>

> A comprehensive command `/deslop` or $deslop (depending on your harness) for identifying and fixing "slop" in your codebase.

This command combines a code analysis workflow with an extensive library of coding principles living in [references/](references/). When you run `/deslop [file-or-directory]`, or even just `/deslop` or perhaps `/deslop my frontend typescript code` the AI will read your code, cross-reference it against these principles, and suggest specific fixes with before/after examples.

**Scoped pass or whole-codebase campaign?** The default is a pass over the file, directory, or diff you name. When the ask is a **campaign** — "massive simplification", "across the board", "minimum 30% LOC", "break up the god files", "get it all done, no excuses, present me a PR" — follow [references/modes/campaign.md](references/modes/campaign.md) instead, and measure it with [references/library/measuring.md](references/library/measuring.md).

Whether or not you use this deslop command on your code base, you should read all the coding principles yourself, as a human - you might actually learn something useful.

---

## How the library is organised

`references/` is a taxonomy by **role in the pass**, not by topic — topic is already carried by the principle
category. The directory a file sits in tells a reader what to do with it, and the check in
`scripts/swarm_lenses.py --check` fails if a markdown has no role:

| Directory | Role | Read |
|---|---|---|
| `references/stages/` | the four moments of a pass — `planning`, `aggregation`, `consolidation`, `reporting` | at its stage, in order |
| `references/readings/` | what a single reading carries — `auditing` (the report format and census), `when-to-relax` (the guardrail), `duplication` (the dedup sweep), `detecting-slop` (why detection is prose) | `auditing` and `when-to-relax` in **every** reading |
| `references/modes/` | modes a pass can run in — `campaign` (measured whole-codebase programme), `loop-until-dry` | when the ask names the mode |
| `references/principles/` | `<category>.md` is a category **index** (read first: the stance and the tells); `<category>/<slug>.md` is one principle | the index first, then every file of an assigned group, in full |
| `references/library/` | about the library itself — extend it, measure it, cite it, see it worked | on request |
| `references/lenses.json` | the principle partition, the indexes each group reads, and the trigger for each stage/mode/library file | by the scripts, and by anyone planning |

**This file is the manifest.** No harness builds one: only `SKILL.md` loads when the skill activates, and every
other file is read on demand *by path* — so a reference nothing here leads to (directly, or through an index that
does) is a file nobody opens. Three checks enforce that, and they run in CI on every push and pull request
(`.github/workflows/skill-checks.yml`):

```bash
python3 scripts/check_reachability.py     # every markdown reachable by following links from this file
python3 scripts/swarm_lenses.py --check   # every principle in exactly one group; no unclassified markdown
python3 -m py_compile scripts/*.py        # the instruments still load
```

Add, rename or move a file and CI names the orphan and which index should link it — so reorganising the library
cannot silently leave a principle behind.

## Workflow references (read these to run a pass)

| File | When |
|------|------|
| [references/readings/auditing.md](references/readings/auditing.md) | **Always** — the audit itself: persona, the mode question, the autonomy rule, violation report format, and the **input census** (for each external input: who owns turning it into a decision, and how many places re-interpret it — zero owners or several is a finding, reported even when it ranks last) |
| [references/modes/loop-until-dry.md](references/modes/loop-until-dry.md) | Thorough passes ("keep going") — iterate until a full scan finds nothing actionable |
| [references/stages/planning.md](references/stages/planning.md) | **Before a pass that must cover the library** — or after a pass that missed something: survey, slice, group the principles, write the permutation list, rank it against a budget, choose the execution mechanism you actually have |
| [references/stages/aggregation.md](references/stages/aggregation.md) | **The moment more than one reading has reported** — merge on locus + principle into corroborated / single / disputed, account for coverage, and mark a cell that quotes nothing as a failed reading |
| [references/stages/consolidation.md](references/stages/consolidation.md) | **After aggregation, before anything is reported or filed** — verify, apply the guardrail, bucket into now / next / wait-or-drop, collapse findings into concerns, group into a milestone |
| [references/stages/reporting.md](references/stages/reporting.md) | **Immediately before you speak to the person who asked** — lead with the answer, bucket the work, keep it short, and never bury the result in method |
| [references/modes/campaign.md](references/modes/campaign.md) | **Whole-codebase campaigns** — "massive simplification", "across the board", "minimum 30% LOC", "get it all done", "present me a PR". The five sweeps, the target discipline, running it at scale, and the delivery protocol |
| [references/library/measuring.md](references/library/measuring.md) | **Any pass that will claim a number** — the four measurement harnesses, the unbiased task corpus, the metrics that carry the story (nesting depth, `elif` chains, cyclomatic complexity), and the honest before/after reporting skeleton |
| [references/library/extending-the-library.md](references/library/extending-the-library.md) | **Adding a principle** — the ask is a *gap* in the library, not a pass over code: discovery against every existing principle, research, the house draft format, both indexes, and the publish path |

## Plan the pass before you audit

**A pass is planned, not merely started.** The empirical fact this section exists for: slop is found when a
reader is looking at **a specific piece of code with a specific set of principles in mind**, and much less when
it is told to "audit this directory" — a general pass reads the indexes, picks what *looks* implicated, and the
principles that need a boundary held in mind are never opened at all. So the unit of work is a **cell**: one
group of principles × one slice of the code × one reading, whose report is merged with the others afterwards.

The full protocol — slicing families, grouping rules, scoring, aggregation, triage — is
[references/stages/planning.md](references/stages/planning.md). The short form, in order:

1. **Survey first.** Read the code's shape before slicing it: the units, the entry points, the seams where
   requests and the outside world are reached, the cross-cutting concerns (every config read, every retry,
   every logger), the roles directories play, and any history or existing findings. Write a short note; a pass
   that skips this is guessing at its own scope.
2. **Design the slices.** Not only directories. Modules; modules read as the role they play; **concept clusters**
   — every retry, every env reader, every provider adapter, wherever they live (the slices a directory walk
   cannot express, and where duplicated knowledge hides); **the schema and the queries that reach it**; flows
   end-to-end; the callers of one contract; a diff. Name each in one sentence. One file is a legitimate slice
   when four concerns share one home.
3. **Group the principles.** Each group is a *reading stance*: the principles you must weigh against each other
   while reading the same code. [references/lenses.json](references/lenses.json) ships a default — 8 groups over
   53 principle files — and you may regroup. Two constraints: related principles stay together (or one defect
   gets reported twice under two names), and every principle file sits in exactly one group (a principle in no
   group is silently never read; in two groups, paid for twice).
4. **Write the permutation list, then triage it.** Cells = slices × groups, written down rather than run. Rank
   by evidence strength, blast radius, prior misses, verification cost — and never penalise overlap *across*
   groups: different principles reading the same files is the point, while the same group twice is waste. Cut
   into must-run / if-budget / explicitly-skipped, with the skipped cells named and justified.
5. **Rotate the rounds.** A second pass over the same code is the **complement of the first**, never a re-run:
   plan it with `swarm_plan.py --ledger <path> --round N+1`, which excludes cells already run, keeps whole-target
   orientation cells from repeating unless `--reorient`, down-weights groups already exercised, and states in
   `plan.md` which groups remain unread. Report that rotation state as part of the result — the reader should not
   have to ask for "another angle" to get one.
6. **Choose the mechanism — whatever you have.** The decomposition is fixed; the execution is not. You may have
   parallel subagents, a harness that fans out on its own, model tiers (a strong model for the judgement-heavy
   groups, a cheap one for mechanical sweeps, a second model as an independent opinion), or just this context,
   one cell at a time. All are legitimate. What must hold: one cell per reading, whole files not snippets,
   read-only, prompts passed through verbatim, groups never merged to save budget, and **if the plan looks thin
   add slices — never a group across every module.**

Optional instruments for the bookkeeping (the plan is the deliverable, not the script):

```bash
python3 scripts/swarm_plan.py --repo <root> --target <dir> --out /tmp/deslop-plan --budget 24
#   → plan.md        selected cells in wave order, with the reasoning per cell
#   → candidates.md  the whole permutation list: score components, and why each cell stood or fell
#   → dispatch.sh    ready-to-run prompts, one per selected cell
python3 scripts/swarm_lenses.py --check     # prove every principle file sits in exactly one group
```

For a **specific ask** — *"look at separation of concerns in the provider adapters"* — skip the plan and read one
cell: `swarm_lenses.py --emit <dir> --only boundaries --target <module>`, or simply open that group's principle
files and read the module whole. That request is the one a general pass cannot satisfy, because a general pass
decides for itself what to open.

## Aggregate, consolidate, then report

A pass always finds more than anyone should act on at once, and a flat list is not a triage. Three stages follow
the readings, each with its own file so that planning does not carry context it has not earned yet:

1. **[aggregating-findings.md](references/stages/aggregation.md)** — merge on locus + principle (corroborated /
   single / disputed), account for coverage, and treat a cell that reports nothing and quotes nothing as a *failed
   reading*. Corroboration is a hint; a single instance is enough to be a real finding.
2. **[consolidating-and-triage.md](references/stages/consolidation.md)** — verify at the source line, apply
   [when-to-relax.md](references/readings/when-to-relax.md), then bucket by severity × blast radius ÷ fix cost into **now /
   next / wait-or-drop**, collapse findings into concerns (one issue per concern, never per finding), group the
   work into a milestone with a denominator, and state what was skipped or relaxed.
3. **[reporting-results.md](references/stages/reporting.md)** — the shape of the message: the answer first, the
   short "fix first" list, the contained work, what was left out, then stop. Method goes in one line at most.

## Principle references (indexes)

Each index below is a short table of principles and their one-line essences, linking to self-contained per-principle files under `references/<category>/`. **Read the indexes up front; open a principle's full file only when a finding implicates it** (or when fixing a violation of it).

Know the cost of that rule: the pass can only open a principle it has already suspected, so principles that need a boundary held in mind — above all **Separation of Concerns** — are routinely never read. When the ask is coverage rather than speed, or a named concern has been missed before, run [references/stages/planning.md](references/stages/planning.md) instead of reading harder: it partitions the library into lenses, forces each agent to read its files before scanning, and merges the reports.

| File | Contents |
|------|----------|
| [references/principles/clean-code.md](references/principles/clean-code.md) | **Clean Code** — KISS, YAGNI, Small Functions, Guard Clauses, Decide Don't Cope, Cognitive Load, Cyclomatic Complexity, SLAP, Self-Documenting Code, Documentation Discipline, Elegance, Legibility, Least Surprise, Patchwork, An Unclaimed Guarantee |
| [references/principles/architecture.md](references/principles/architecture.md) | **Architecture** — DRY, Single Source of Truth, Separation of Concerns, Modularity, One Logical Unit One Home, Encapsulation, Law of Demeter, Orthogonality, DI, Composition Over Inheritance, SOLID, Convention Over Configuration, CQS, Reusability, Parse Don't Validate, A Helper That Must Exist Is an Architecture Finding, Immutability, Idempotency |
| [references/principles/reliability.md](references/principles/reliability.md) | **Reliability** — Fail-Fast, No Silent Defaults, Design by Contract, Postel's Law, Resilience & Graceful Degradation, Least Privilege, Boy Scout Rule, Observability |
| [references/readings/when-to-relax.md](references/readings/when-to-relax.md) | **When to relax rules** — contexts where principles are over-applied, plus the meta-principle |

## Situational references (read when relevant)

| File | Read when |
|------|-----------|
| [references/principles/data-layer.md](references/principles/data-layer.md) | The target has a database — schema, SQL, migrations, foreign keys, normalization, constraints, **indexes and join access paths alongside the queries that must use them** (**The Data Layer**). Treat the schema as a slice in its own right: it usually sits outside the directory being audited, and no index finding is provable from the DDL alone |
| [references/lenses.json](references/lenses.json) | Grouping the principles for a planned pass — the default partition of 53 principle files into 8 reading stances (validated by `scripts/swarm_lenses.py --check`); regroup it if the codebase asks for different stances |
| [references/readings/duplication.md](references/readings/duplication.md) | Running a dedup sweep — hunting duplication beyond token scanners: the primitives to grep for, the field-overlap recipe for one entity described many times, and the shape-clone scripts in [scripts/](scripts/) |
| [references/readings/detecting-slop.md](references/readings/detecting-slop.md) | Building or questioning a detector — what the tools cannot see, and the control a detector script must pass to earn its lines |
| [references/library/case-study-simplification-agent-fleet.md](references/library/case-study-simplification-agent-fleet.md) | Worked KISS example — a real pass that collapsed an LLM agent fleet into one agent |
| [references/library/further-reading.md](references/library/further-reading.md) | Background bibliography and concept attribution (not needed mid-audit) |

---

*Run `/deslop [file-or-directory]` to analyze your code against these principles and let the agent fix any slop it detects.*
