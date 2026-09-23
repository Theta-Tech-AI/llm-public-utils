---
name: deslop
description: Analyze code quality and perform targeted refactoring against established coding principles. Use when identifying and fixing "slop" in a codebase, running dedup sweeps, or reviewing code for maintainability violations.
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
| [references/auditing.md](references/auditing.md) | **Always** — the audit itself: persona, the mode question, the autonomy rule, violation report format |
| [references/loop-until-dry.md](references/loop-until-dry.md) | Thorough passes ("keep going") — iterate until a full scan finds nothing actionable |
| [references/campaign-mode.md](references/campaign-mode.md) | **Whole-codebase campaigns** — "massive simplification", "across the board", "minimum 30% LOC", "get it all done", "present me a PR". The five sweeps, the target discipline, running it at scale, and the delivery protocol |
| [references/measuring.md](references/measuring.md) | **Any pass that will claim a number** — the four measurement harnesses, the unbiased task corpus, the metrics that carry the story (nesting depth, `elif` chains, cyclomatic complexity), and the honest before/after reporting skeleton |

## Principle references (indexes)

Each index below is a short table of principles and their one-line essences, linking to self-contained per-principle files under `references/<category>/`. **Read the indexes up front; open a principle's full file only when a finding implicates it** (or when fixing a violation of it).

| File | Contents |
|------|----------|
| [references/clean-code.md](references/clean-code.md) | **Clean Code** — KISS, YAGNI, Small Functions, Guard Clauses, Decide Don't Cope, Cognitive Load, SLAP, Self-Documenting Code, Documentation Discipline, Elegance, Legibility, Least Surprise, Patchwork |
| [references/architecture.md](references/architecture.md) | **Architecture** — DRY, Single Source of Truth, Separation of Concerns, Modularity, Encapsulation, Law of Demeter, Orthogonality, DI, Composition Over Inheritance, SOLID, Convention Over Configuration, CQS, Reusability, Parse Don't Validate, Immutability, Idempotency |
| [references/reliability.md](references/reliability.md) | **Reliability** — Fail-Fast, Design by Contract, Postel's Law, Resilience & Graceful Degradation, Least Privilege, Boy Scout Rule, Observability |
| [references/when-to-relax.md](references/when-to-relax.md) | **When to relax rules** — contexts where principles are over-applied, plus the meta-principle |

## Situational references (read when relevant)

| File | Read when |
|------|-----------|
| [references/data-layer.md](references/data-layer.md) | The target has a database — schema, SQL, migrations, indexes (**The Data Layer**) |
| [references/duplication.md](references/duplication.md) | Running a dedup sweep — hunting duplication beyond token scanners |
| [references/case-study-simplification-agent-fleet.md](references/case-study-simplification-agent-fleet.md) | Worked KISS example — a real pass that collapsed an LLM agent fleet into one agent |
| [references/further-reading.md](references/further-reading.md) | Background bibliography and concept attribution (not needed mid-audit) |

---

*Run `/deslop [file-or-directory]` to analyze your code against these principles and let the agent fix any slop it detects.*
