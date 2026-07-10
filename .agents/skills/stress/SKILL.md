---
name: stress
description: Stress-test apps (especially webapps) by combing happy paths, causing mischief, and hunting bugs in code. Use whenever the user wants to find bugs, edge cases, knots, break an app, harden UX, QA a flow, or catch issues before users do — even if they only say "try the app", "test this", or "see what breaks".
---

# Stress: Unearth Bugs Before Users Do

Three complementary modes for hardening an app's *functionality* (not load/scale — that can be a future `load.md`):

| Mode | Temper | Read when |
|------|--------|-----------|
| **Comb** | Gentle, repeated happy-path grooming | User wants polish, subtle UX knots, or "make it silky" |
| **Mischief** | Hostile, out-of-order chaos | User wants to break it, abuse flows, or harden against weird users |
| **Bug hunter** | Code-first, multi-angle review | User wants static/code bugs, smell hunts, or architecture-level defects |

You may run one mode, or all three. Decide from the user's intent; if unclear, start with **comb**, then escalate to **mischief** and/or **bug hunter**.

## Before you start

1. **Read the mode file(s)** you will use:
   - [references/comb.md](references/comb.md)
   - [references/mischief.md](references/mischief.md)
   - [references/bug-hunter.md](references/bug-hunter.md)
2. **Get set up to actually use the app.** Auth may live in env vars, docs, a local-dev skill, or a bypass. Prefer driving the real UI (agent-browser / equivalent) over API-only when the surface is a webapp.
3. **Confirm how to report findings** (see below) if the user hasn't said.

## Reporting findings (default)

| Situation | Default |
|-----------|---------|
| Repo has GitHub + you can file issues | File one issue per real finding; give the user hyperlinks |
| No GitHub / no permission | Write a markdown or HTML artifact in-repo (or where the user asks) |
| User asks to auto-fix | Fix as you go (small, tested knots); still log larger ones |

**GitHub smoke test:** if you plan to file issues, create a throwaway issue and delete it first to prove permissions — then file the real ones.

Do **not** invent bugs from a single flaky signal. Cross-check UI + network/console + backend/API (and infra/deploy state) before filing. Prefer filing over silent "I'll remember it."

## How to choose

- **"Walk through the happy path" / "comb" / polish** → comb only
- **"Break it" / "try to mess it up" / chaos** → mischief (optionally after one comb pass so you know the happy path)
- **"Review the code for bugs"** → bug hunter
- **"Stress test this" / vague** → comb first, then mischief; bug-hunt any ugly code you notice along the way

## Your job

Stress the system. Unearth bugs. Record them (or fix them if asked). Summarize what you found with links. Leave the app harder to break than you found it.
