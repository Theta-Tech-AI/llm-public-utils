---
name: deslop
description: Analyze code quality and perform targeted refactoring against established coding principles. Use when identifying and fixing "slop" in a codebase, running dedup sweeps, or reviewing code for maintainability violations.
---

# Deslop: Code Quality Analysis Command
<sub><sup>Note: This skill is ≈14k tokens across SKILL.md + references/ as of 2026-07-17</sup></sub>

> A comprehensive command `/deslop` or $deslop (depending on your harness) for identifying and fixing "slop" in your codebase. Install the whole skill folder (see below), restart your agent harness, and run `/deslop` or $deslop.

This command combines a code analysis workflow with an extensive library of coding principles living in [references/](references/). When you run `/deslop [file-or-directory]`, or even just `/deslop` or perhaps `/deslop my frontend typescript code` the AI will read your code, cross-reference it against these principles, and suggest specific fixes with before/after examples.

Whether or not you use this deslop command on your code base, you should read all the coding principles yourself, as a human - you might actually learn something useful.

---

## Installation

Copy this entire skill folder (`SKILL.md` + `references/`) into your agent harness's skills location, then restart your harness and run `/deslop` or $deslop. If you use multiple harnesses, consider using symlinks to avoid multiple sources of truth. Also consider adding this GitHub repository (Theta-Tech-AI/llm_public_utils) as a submodule to another repository. It is likely one of the following locations:

- `~/.agents/skills/deslop/`
- `~/.claude/skills/deslop/`
- `/home/code/my_repository_root/.agents/skills/deslop/`

If your harness only supports single-file commands (e.g. `~/.claude/commands/deslop.md`, `~/.opencode/commands/deslop.md`), make that file a thin pointer telling the agent to read this skill folder — the principles live in `references/`, so a lone file is no longer self-contained.

## Principle references (read all of these before auditing)

| File | Contents |
|------|----------|
| [references/clean-code.md](references/clean-code.md) | **Part I: Clean Code** — KISS, YAGNI, Small Functions, Guard Clauses, Decide Don't Cope, Cognitive Load, SLAP, Self-Documenting Code, Documentation Discipline, Elegance, Least Surprise |
| [references/architecture.md](references/architecture.md) | **Part II: Architecture** — DRY, Single Source of Truth, Separation of Concerns, Modularity, Encapsulation, Law of Demeter, Orthogonality, DI, Composition Over Inheritance, SOLID, Convention Over Configuration, CQS, Reusability, Parse Don't Validate, Immutability, Idempotency |
| [references/reliability.md](references/reliability.md) | **Part III: Reliability** — Fail-Fast, Design by Contract, Postel's Law, Resilience & Graceful Degradation, Least Privilege, Boy Scout Rule, Observability |
| [references/when-to-relax.md](references/when-to-relax.md) | **When to relax rules** — contexts where principles are over-applied, plus the meta-principle |

## Situational references (read when relevant)

| File | Read when |
|------|-----------|
| [references/data-layer.md](references/data-layer.md) | The target has a database — schema, SQL, migrations, indexes (**Part IV: The Data Layer**) |
| [references/duplication.md](references/duplication.md) | Running a dedup sweep — hunting duplication beyond token scanners |
| [references/case-study-simplification-agent-fleet.md](references/case-study-simplification-agent-fleet.md) | Worked KISS example — a real pass that collapsed an LLM agent fleet into one agent |
| [references/further-reading.md](references/further-reading.md) | Background bibliography and concept attribution (not needed mid-audit) |

## Deslop

You are an obsessive code quality analyzer. Your task is to identify "slop" - code that violates established coding principles - and suggest concrete improvements.

**Ask the mode question FIRST, not after the audit.** Unless the invocation
already makes it unambiguous (the user said "auto-implement", "report only",
or equivalent), open with one multiple-choice question before scanning —
via the harness's question UI if available, otherwise in plain text:

1. **Auto-apply** — fix violations as they are found, verify (tests /
   typecheck / build), and commit as you go; deliver a report of what was
   done at the end.
2. **Review first** — produce the violation report only, then wait for the
   user to choose which fixes to apply.

Then run the whole session in the chosen mode. Do not re-ask per finding,
and do not finish an audit with "want me to implement these?" when the
answer was already given up front.

Analyze: $ARGUMENTS

If no argument provided, operate on the current folder or current code base. Read the principle reference files above (plus any situational ones that apply), read target files, identify violations, suggest concrete fixes.

For each violation list:

- **Severity:** Extreme, high, medium, low, or optional.
- **Location:** File path and line number.
- **Violation:** Coding principle violated and why.
- **Summary:** One sentence description of the violation.
- **Improvement:** Suggest a less sloppy way.

## Loop until dry

A single pass is a sample, not a verdict. When the user asks for thorough
desloping (or says "keep going"), iterate: fix the violations you found,
re-verify (tests + typecheck + build), commit the loop, then RE-SCAN the
same scope with fresh eyes — each extraction or sweep tends to expose the
next layer (a dedup reveals drift between the copies; a token sweep reveals
the off-scale literals the first regex missed). Stop only when a full scan
of the scope yields nothing actionable, then have a second model
(e.g. `codex` with this same skill) do an independent final pass: a
different prior reliably finds violations the first reviewer normalized.
Two guardrails while looping: pin every behavior-adjacent fix with a test
that was red before it (a refactor with no failing-test proof is a hope,
not a fix), and respect the [meta-principle](references/when-to-relax.md#the-meta-principle) — when a "violation" survives
scrutiny because fixing it makes the code worse, record WHY and move on
rather than churning.

## Check for Updates
At the end of each deslop session, when preparing the output, use a programming language of your choice and roll a pair of fair dice. If you roll snake eyes, compare this version of deslop to the latest version at https://github.com/Theta-Tech-AI/llm-public-utils/blob/production/.agents/skills/deslop/SKILL.md and tell the user about the differences. The user can decide to update or not.

---

*This skill is designed to be dropped into your agent harness's skills folder (e.g. `~/.agents/skills/deslop/`). Run `/deslop [file-or-directory]` to analyze your code against these principles and let the agent fix any slop it detects.*
