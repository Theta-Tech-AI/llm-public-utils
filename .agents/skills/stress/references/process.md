---
name: process
description: The standard stress run — the snapshot → choose → predict → act → measure loop at every step, a living inventory and a triaged run list in parallel lanes, then 1-3 reliability, 1-3 comb and 1-3 mischief passes and the code-first bug hunt, ending with a coverage check. Use as the default shape of a full stress engagement.
---

# Process: The Standard Stress Run

A full run has a default shape. User intent and what you find always win. The phases, their order and their parallel rule are in the table in [SKILL.md](../SKILL.md); this file says how to run each one. Each phase hands context to the next: the step loop and inventory say what exists, reliability proves the path works, comb maps where it is rough, mischief attacks what is load-bearing, and the bug hunt finds the code address of each knot and crack.

## Before you start — deployment

Know which environments exist (localhost, cloud dev, staging, prod), which one you may stress, and how each one deploys. Read the CI/CD yaml; ask if it is not clear. **Never touch prod unless explicitly instructed, and confirm any prod change with the user before acting.** Detail: [reliability.md](reliability.md).

## The step loop — at every step of every phase

**Principle: know what you can do right now, and say what should happen before you do it.** A run that drives only the flows it remembers misses whole affordances; the typical miss is a chat box that shows only on a finished result, so no pass ever asks it for a change. A run that predicts nothing cannot be wrong, so it cannot find a bug. Use the app like a scientist who tests a hypothesis against reality.

At every step in the browser (and every call in an API sequence):

1. **Snapshot.** List the actions available now, in this state: buttons, inputs, text and chat boxes, links, menus, tabs, drawers, hover-only and keyboard paths — and what changed since the last step. A new screen, state or control (a result page, a chat box on a finished run, an error state) goes into the inventory at once.
2. **Choose** the next action on purpose, and write why: a snapshot row not tried yet, the highest user risk, or the run's goal.
3. **Predict.** Write the expected result: what renders, which request and status, what state or data changes, how long it takes, what the logs say.
4. **Act** in the real app.
5. **Measure** the actual: screenshot, network and console, backend logs or DB truth, timing. A mismatch is a finding — or a wrong expectation, which you correct and note. Never write "works" without the observation that proves it; a probe you cannot read is `unknown`, never a pass.

Log one row per action in the scratchpad `stress-log.md`: `inventory id | action | expected | actual | evidence path | verdict (match / mismatch / unknown) | issue link`.

The **inventory** (`inventory.md`) is the union of the snapshots, one row per affordance: `id | page | affordance | what it does | inputs | roles | preconditions | cost (paid?)`. Start it from the first snapshot of each page, then widen it from the route table, the API schema, the docs and the components: a route or control there that the UI never showed is itself a finding. After each deploy, diff it against the last one; new and changed rows go first.

## Phase 0 — Triage into a run list

Before the passes, take a first snapshot of each page you can reach, then turn the inventory so far into `run-list.md`: discrete, numbered things to try. Rows that later snapshots find join it at once.

- **Variations.** Give each item its minor variations of user behaviour: order, timing, value shape, role, device width, repeat, interrupt.
- **Order.** Sort by dependency and user risk: the gate (happy path) first, then what most users touch, then the rest.
- **Lanes.** Group the items into independent lanes that run in parallel (one subagent each). Give each lane its own project, account and session, so lanes do not collide. Give each paid lane a budget, and stop the lane at its budget.
- **Coverage.** Map every inventory row to at least one run-list item, or mark it `skipped because …`.

## Phase 1 — Reliability gate (1-3 passes)

Run the primary happy path end to end, up to 3 times. Detail and motivation: [reliability.md](reliability.md).

- **Pass** = each run completes, with the same result each time — no flakiness, silent retries, or console/network errors.
- **Fail** = stop. File per [findings.md](findings.md) and hold the run here — fix (or report and wait) before you continue.

If the happy path is already proven on this deploy (a fresh green e2e in CI, a just-completed reliability pass), one confirmation pass is enough.

## Phase 2 — Comb (1-3 passes)

Work the run list per [comb.md](comb.md): each item with its variations, wide teeth first, finer each pass.

## Phase 3 — Mischief (1-3 passes)

Attack every input and control in the inventory per [mischief.md](mischief.md). Aim first at what Phase 2 showed is load-bearing.

## Phase 4 — Bug hunt (last, or in parallel)

Code-first, per [bug-hunter.md](bug-hunter.md). It never touches the running app, so it can run in parallel (a subagent that reads code while you drive) or as the final sweep. Feed it what the earlier phases found: each knot and crack has a code address.

## Throughout

- **File findings as you go** per [findings.md](findings.md); never batch them to the end.
- **Mark each run-list item done** with the issue links it produced, so a crashed session can resume from the files.
- **Drive deliberately** per [driving.md](driving.md).

## End — coverage check

Check the run list against the inventory: every row tried, or skipped with a reason; a row with neither goes back on the run list. Count the log verdicts: predictions matched, falsified and unknown. Then report per **After the pass** in [findings.md](findings.md), which starts with these counts.

## When to deviate

- The user asked for one mode only → run that mode, still with the step loop.
- Time-boxed → keep the step loop and a coarse run list; one real pass per phase is better than three shallow ones or a skipped phase.
- Phase 1 keeps failing → the run ends early; a broken happy path *is* the headline finding.
