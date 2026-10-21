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
| [references/pass-planning.md](references/pass-planning.md) | **Before a pass that must cover the library** — or after a pass that missed something: survey, slice, group the principles, write the permutation list, rank it against a budget, choose the execution mechanism you actually have |
| [references/aggregating-findings.md](references/aggregating-findings.md) | **The moment more than one reading has reported** — merge on locus + principle into corroborated / single / disputed, account for coverage, and mark a cell that quotes nothing as a failed reading |
| [references/consolidating-and-triage.md](references/consolidating-and-triage.md) | **After aggregation, before anything is reported or filed** — verify, apply the guardrail, bucket into now / next / wait-or-drop, collapse findings into concerns, group into a milestone |
| [references/reporting-results.md](references/reporting-results.md) | **Immediately before you speak to the person who asked** — lead with the answer, bucket the work, keep it short, and never bury the result in method |
| [references/campaign-mode.md](references/campaign-mode.md) | **Whole-codebase campaigns** — "massive simplification", "across the board", "minimum 30% LOC", "get it all done", "present me a PR". The five sweeps, the target discipline, running it at scale, and the delivery protocol |
| [references/measuring.md](references/measuring.md) | **Any pass that will claim a number** — the four measurement harnesses, the unbiased task corpus, the metrics that carry the story (nesting depth, `elif` chains, cyclomatic complexity), and the honest before/after reporting skeleton |
| [references/extending-the-library.md](references/extending-the-library.md) | **Adding a principle** — the ask is a *gap* in the library, not a pass over code: discovery against every existing principle, research, the house draft format, both indexes, and the publish path |

## Plan the pass before you audit

**A pass is planned, not merely started.** The empirical fact this section exists for: slop is found when a
reader is looking at **a specific piece of code with a specific set of principles in mind**, and much less when
it is told to "audit this directory" — a general pass reads the indexes, picks what *looks* implicated, and the
principles that need a boundary held in mind are never opened at all. So the unit of work is a **cell**: one
group of principles × one slice of the code × one reading, whose report is merged with the others afterwards.

The full protocol — slicing families, grouping rules, scoring, aggregation, triage — is
[references/pass-planning.md](references/pass-planning.md). The short form, in order:

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
5. **Choose the mechanism — whatever you have.** The decomposition is fixed; the execution is not. You may have
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

1. **[aggregating-findings.md](references/aggregating-findings.md)** — merge on locus + principle (corroborated /
   single / disputed), account for coverage, and treat a cell that reports nothing and quotes nothing as a *failed
   reading*. Corroboration is a hint; a single instance is enough to be a real finding.
2. **[consolidating-and-triage.md](references/consolidating-and-triage.md)** — verify at the source line, apply
   [when-to-relax.md](references/when-to-relax.md), then bucket by severity × blast radius ÷ fix cost into **now /
   next / wait-or-drop**, collapse findings into concerns (one issue per concern, never per finding), group the
   work into a milestone with a denominator, and state what was skipped or relaxed.
3. **[reporting-results.md](references/reporting-results.md)** — the shape of the message: the answer first, the
   short "fix first" list, the contained work, what was left out, then stop. Method goes in one line at most.

## Principle references (indexes)

Each index below is a short table of principles and their one-line essences, linking to self-contained per-principle files under `references/<category>/`. **Read the indexes up front; open a principle's full file only when a finding implicates it** (or when fixing a violation of it).

Know the cost of that rule: the pass can only open a principle it has already suspected, so principles that need a boundary held in mind — above all **Separation of Concerns** — are routinely never read. When the ask is coverage rather than speed, or a named concern has been missed before, run [references/pass-planning.md](references/pass-planning.md) instead of reading harder: it partitions the library into lenses, forces each agent to read its files before scanning, and merges the reports.

| File | Contents |
|------|----------|
| [references/clean-code.md](references/clean-code.md) | **Clean Code** — KISS, YAGNI, Small Functions, Guard Clauses, Decide Don't Cope, Cognitive Load, Cyclomatic Complexity, SLAP, Self-Documenting Code, Documentation Discipline, Elegance, Legibility, Least Surprise, Patchwork, An Unclaimed Guarantee |
| [references/architecture.md](references/architecture.md) | **Architecture** — DRY, Single Source of Truth, Separation of Concerns, Modularity, One Logical Unit One Home, Encapsulation, Law of Demeter, Orthogonality, DI, Composition Over Inheritance, SOLID, Convention Over Configuration, CQS, Reusability, Parse Don't Validate, A Helper That Must Exist Is an Architecture Finding, Immutability, Idempotency |
| [references/reliability.md](references/reliability.md) | **Reliability** — Fail-Fast, No Silent Defaults, Design by Contract, Postel's Law, Resilience & Graceful Degradation, Least Privilege, Boy Scout Rule, Observability |
| [references/when-to-relax.md](references/when-to-relax.md) | **When to relax rules** — contexts where principles are over-applied, plus the meta-principle |

## Situational references (read when relevant)

| File | Read when |
|------|-----------|
| [references/data-layer.md](references/data-layer.md) | The target has a database — schema, SQL, migrations, foreign keys, normalization, constraints, **indexes and join access paths alongside the queries that must use them** (**The Data Layer**). Treat the schema as a slice in its own right: it usually sits outside the directory being audited, and no index finding is provable from the DDL alone |
| [references/lenses.json](references/lenses.json) | Grouping the principles for a planned pass — the default partition of 53 principle files into 8 reading stances (validated by `scripts/swarm_lenses.py --check`); regroup it if the codebase asks for different stances |
| [references/duplication.md](references/duplication.md) | Running a dedup sweep — hunting duplication beyond token scanners: the primitives to grep for, the field-overlap recipe for one entity described many times, and the shape-clone scripts in [scripts/](scripts/) |
| [references/detecting-slop.md](references/detecting-slop.md) | Building or questioning a detector — what the tools cannot see, and the control a detector script must pass to earn its lines |
| [references/case-study-simplification-agent-fleet.md](references/case-study-simplification-agent-fleet.md) | Worked KISS example — a real pass that collapsed an LLM agent fleet into one agent |
| [references/further-reading.md](references/further-reading.md) | Background bibliography and concept attribution (not needed mid-audit) |

---

*Run `/deslop [file-or-directory]` to analyze your code against these principles and let the agent fix any slop it detects.*
