---
name: stress
description: "Stress-test apps (especially webapps) — confirm reliability, comb happy paths, cause mischief, run a panel of distinct first-time users, and hunt bugs in code — via agent browser, API scripts, or both, alone or as a swarm of parallel lanes. Use whenever the user wants to find bugs, edge cases, knots, break an app, harden UX or APIs, QA a flow, run launch or onboarding QA, test what confuses real users, simulate different users or personas, run an API-only or headless stress run, or catch issues before users do — even if they only say try the app, test this, hit the API, or see what breaks."
---

# Stress: unearth bugs before users do

A stress run hardens an app's *functionality* (not load or scale). It is **sequential**, not a pick-list: prove the happy path works (reliability), groom it (comb), attack it (mischief), and hunt the code (bug hunt). A failed reliability gate ends the run early. Two drive modes put hands on the system — **API mode**, the contract every client inherits, and **browser mode**, what the person actually experiences — and they work best dueling: each finds what the other cannot.

## Read in this order

| # | File | Read it for |
|---|------|-------------|
| 1 | [process.md](references/process.md) | **The standard run**: setup, then 1-3 reliability → 1-3 comb → 1-3 mischief passes, the bug hunt, the persona panel, and when to deviate |
| 2 | [driving.md](references/driving.md) | **The two modes, dueling**: why each works, what only each finds, what each costs, how to run them against each other |
| 3 | [api.md](references/api.md) | **API mode**: the flow map (the API document), shared tools, the tester as a model, and the checks — the reader table first, the role matrix, out-of-order moves, races, refusals and audit, oracles |
| 3 | [browser.md](references/browser.md) | **Browser mode**: agent browser, and the frontend driving playbook |
| 4 | [reliability.md](references/reliability.md) · [comb.md](references/comb.md) · [mischief.md](references/mischief.md) · [bug-hunter.md](references/bug-hunter.md) · [personas.md](references/personas.md) | **The mode** for this pass (see below) |
| 5 | [findings.md](references/findings.md) | **What to do with bugs**: search, file, label, fix the issue behind the issue, talk a fixed bug through with its owner |
| 6 | [lanes.md](references/lanes.md) | **Many testers at once**: lane split, briefs, start and end of a lane, the report shape, the coordinator, auto-fix through gated fixers |

## Three separate choices

**1. Which phase**, by the request:

- **"Does it work?" / sanity check / pre-release confidence** → [reliability](references/reliability.md)
- **"Walk through the happy path" / "comb" / polish** → [comb](references/comb.md)
- **"Break it" / "try to mess it up" / chaos** → [mischief](references/mischief.md) (optionally after one comb pass so you know the happy path)
- **"Review the code for bugs"** → [bug hunter](references/bug-hunter.md)
- **"Test it as a real user" / launch QA / onboarding / "what confuses people" / "simulate N different users"** → the [persona panel](references/personas.md): independent first-time-user agents, findings ranked by how many personas hit them, then a rerun of the identical panel to prove the fixes
- **"Stress test this" / vague** → the standard run in [process.md](references/process.md)

**2. Which drive mode leads**, by the question: [driving.md → Choose the lead mode](references/driving.md#choose-the-lead-mode-by-the-question). "Hit the API", API-only, headless, contract, authorization or concurrency stress, or late stages nobody reaches in the browser → [API mode](references/api.md) for the requested phase; a webapp's UX → [browser mode](references/browser.md); most webapps → both.

**3. One tester or many lanes.** One tester by default. Run [lanes](references/lanes.md) when the user asks for a swarm, or when breadth across the app or its late stages needs testers in parallel.

## Your job

Stress the system. Unearth bugs. Record them per [findings.md](references/findings.md) (or fix if asked: every fix passes the three-paragraph gate in steps 4 and 7 of [Fix the issue behind the issue](references/findings.md#fix-the-issue-behind-the-issue): written before and after the fix, reread by a fresh reader where one is available, else a disclosed self-review). Summarize with links. Leave the app harder to break than you found it.

**Always look for the issue behind the issue.** A bug is evidence that a design let it happen: a fact with two owners, a rule enforced in one layer only, a check-then-act with no lock, a status and its message decided apart, freshness judged by time instead of content. When you file, name that design decision as your best hypothesis and propose the fix at its owner; when you are fixing, fix it there so the whole class cannot recur ([findings.md → Fix the issue behind the issue](references/findings.md#fix-the-issue-behind-the-issue)).
