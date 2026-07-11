---
name: stress
description: Stress-test apps (especially webapps) by combing happy paths, causing mischief, and hunting bugs in code — via agent browser, API scripts, or both. Use whenever the user wants to find bugs, edge cases, knots, break an app, harden UX or APIs, QA a flow, or catch issues before users do — even if they only say "try the app", "test this", "hit the API", or "see what breaks".
---

# Stress: Unearth Bugs Before Users Do

Three complementary modes for hardening an app's *functionality* (not load/scale — that can be a future `load.md`):

| Mode | Temper | Read when |
|------|--------|-----------|
| **Comb** | Gentle, repeated happy-path grooming | User wants polish, subtle UX knots, or "make it silky" |
| **Mischief** | Hostile, out-of-order chaos | User wants to break it, abuse flows, or harden against weird users |
| **Bug hunter** | Code-first, multi-angle review | User wants static/code bugs, smell hunts, or architecture-level defects |

You may run one mode, or all three. Decide from the user's intent; if unclear, start with **comb**, then escalate to **mischief** and/or **bug hunter**.

> **If the product is a webapp, start at the front door.** The user only ever touches the UI — every backend route, worker, and DB invariant exists to serve what renders in the browser. A pass that only probes the API or reads code is testing a surface no user sees; it will over-report backend defects and miss the UX, state, timing, and copy bugs that are what actually reach people. Default your *hands* to the agent browser for any webapp, and drive it like a real user, not a quick screenshot check. The frontend driving playbook in [driving.md](references/driving.md) is the core of doing this well.
>
> This is a **rebalancing, not a replacement.** The code-first ([bug-hunter.md](references/bug-hunter.md)) and API hunts find a different and equally real class — data loss, authz holes, races, audit/compliance gaps, silent corruption — that never shows up on screen until it bites a user. Keep doing that hunt; it's essential. The correction is only that it had been *crowding out* the front door: lead with the browser, then go deep on the backend too. Do both.

## Shared references (read these)

| File | When |
|------|------|
| [references/driving.md](references/driving.md) | Choosing **browser vs API vs hybrid** — different surfaces catch different bugs |
| [references/findings.md](references/findings.md) | **What to do with bugs** (GitHub issues by default, artifacts, auto-fix) |

## Mode references (read the ones you will use)

- [references/comb.md](references/comb.md)
- [references/mischief.md](references/mischief.md)
- [references/bug-hunter.md](references/bug-hunter.md)

## Before you start

1. Read **driving** + **findings**, then the mode file(s) for this pass.
2. **Get set up** — auth may live in env vars, docs, a local-dev skill, token scripts, or a bypass.
3. Pick a **drive surface** (browser, API, or hybrid) from [driving.md](references/driving.md). Webapp UX work → browser-heavy; contracts/concurrency/repetition → API-heavy; best results usually hybrid.
4. Confirm reporting only if the user contradicted [findings.md](references/findings.md).

## How to choose a mode

- **"Walk through the happy path" / "comb" / polish** → comb
- **"Break it" / "try to mess it up" / chaos** → mischief (optionally after one comb pass so you know the happy path)
- **"Review the code for bugs"** → bug hunter
- **"Hit the API" / contract / concurrency stress** → comb or mischief with an **API-first** drive plan
- **"Stress test this" / vague** → comb first, then mischief; bug-hunt ugly code along the way

## Your job

Stress the system. Unearth bugs. Record them per [findings.md](references/findings.md) (or fix if asked). Summarize with links. Leave the app harder to break than you found it.
