---
name: process
description: The standard stress run — get the deployment lay of the land, then 1-3 reliability passes, 1-3 e2e comb passes, and 1-3 mischief passes, then the code-first bug hunt (optionally in parallel), filing findings throughout. Use as the default shape of a full stress engagement.
---

# Process: The Standard Stress Run

A full stress run has a shape. Not a straitjacket — user intent and whatever you find always win — but a default that keeps you from red-teaming a system whose happy path is broken. Four phases, in order; 1-3 passes each for the app-driving phases:

| Phase | Mode | Passes | Question it answers |
|-------|------|--------|---------------------|
| 1 | [Reliability](reliability.md) | 1-3 | Does the happy path *consistently* complete? |
| 2 | E2E stress — [comb](comb.md) | 1-3 | Where are the knots on and around the happy path? |
| 3 | [Mischief](mischief.md) | 1-3 | What breaks under hostile, out-of-order abuse? |
| 4 | [Bug hunt](bug-hunter.md) | once per area | What do layers, workflows, and data models hide? |

Each phase hands context to the next: reliability proves the path works, comb maps where it's rough, mischief attacks whatever turns out to be load-bearing, and the bug hunt finds the code address of every knot and crack. Phase 4 is **code review, not app driving** — it never touches the running app, so it may run **in parallel** (a subagent reading code while you drive phases 1-3) instead of strictly last.

## Phase 0 — Deployment lay of the land

Before any pass, per [reliability.md](reliability.md): know which environments exist (localhost, cloud dev, staging, prod), which one you're allowed to stress, and how they deploy. Scout the CI/CD yaml; ask if unclear. **Never touch prod unless explicitly instructed, and confirm any prod change with the user before acting.** Do all real iteration on staging or lower; prod is a final "works just like staging" checkbox, and prod-only bugs get reproduced on staging first.

## Phase 1 — Reliability gate (1-3 passes)

Run the primary happy path end to end. Then again, up to 3 times total. Details and motivation: [reliability.md](reliability.md).

- **Pass** = the run completes successfully, with the same result each time — no flakiness, silent retries, or console/network errors along the way.
- **Fail** = stop. File per [findings.md](findings.md) and hold the run here. There is no point combing or attacking a system that can't reliably do its one job — fix (or report and wait) before continuing.

If the happy path is already proven reliable (fresh green e2e in CI, a just-completed reliability pass on this deploy), a single confirmation pass suffices.

## Phase 2 — E2E stress / comb (1-3 passes)

Once the path reliably completes, groom it per [comb.md](comb.md): repeat the happy path with slight deviations — different data, states, accounts, valid payloads — teasing out knots (wrong copy, stale state, dead ends, loading polish). Start wide, go finer each pass. Browser-heavy for webapps per [driving.md](driving.md); API or hybrid when the happy path is a call sequence.

## Phase 3 — Mischief (1-3 passes)

Now that you know the happy path cold, refuse it per [mischief.md](mischief.md): wrong order, double-submit, mid-abandon, garbage input, concurrent mutation across tabs/clients. Aim the waves at whatever Phase 2 revealed as load-bearing.

## Phase 4 — Bug hunt (last, or in parallel)

Code-first, per [bug-hunter.md](bug-hunter.md): multi-angle review of layers, workflows, data models, and error handling. Because it never touches the running app, it doesn't contend for it — either run it **in parallel** (a subagent reading code while you drive phases 1-3) or as the final sweep once the app-driving phases are done. Feed it what the earlier phases smelled: every knot from comb and every crack from mischief has a code address, and ugly code surfaced in any phase is fair game.

## Throughout

- **File findings as you go** per [findings.md](findings.md); never batch them to the end.
- **Drive deliberately** per [driving.md](driving.md) — webapp work defaults to the agent browser, with API scripts for seeding, repetition, and backend truth-checks.

## When to deviate

- The user asked for one mode only → run that mode. This process is the default for an open-ended "stress test this."
- Time-boxed → one real pass per phase beats three shallow ones or skipping a phase.
- Phase 1 keeps failing → the run legitimately ends early; a broken happy path *is* the headline finding.
