---
name: process
description: The standard stress run — lay of the land, an inventory of every way to use the app, a triaged run list in parallel lanes, then 1-3 reliability, 1-3 comb and 1-3 mischief passes and the code-first bug hunt, ending with a coverage report. Use as the default shape of a full stress engagement.
---

# Process: The Standard Stress Run

A full run has a default shape. User intent and what you find always win. The phases, their order and their parallel rule are in the table in [SKILL.md](../SKILL.md); this file says how to run each one. Each phase hands context to the next: the inventory says what exists, reliability proves the path works, comb maps where it is rough, mischief attacks what is load-bearing, and the bug hunt finds the code address of each knot and crack.

## Before you start — deployment

Know which environments exist (localhost, cloud dev, staging, prod), which one you may stress, and how each one deploys. Read the CI/CD yaml; ask if it is not clear. **Never touch prod unless explicitly instructed, and confirm any prod change with the user before acting.** Detail: [reliability.md](reliability.md).

## Phase 0 — Inventory first, then triage

**Principle: map every way to use the app before you use it.** A run that drives only the flows it remembers misses whole affordances. The typical miss: a chat box that shows only on a finished result, so no pass ever asks it for a change. Memory gives you the main flows; only an inventory gives you all of them.

### 1. Inventory

Before any pass, write `inventory.md` in your scratchpad: **every way a user can use the app**.

Walk every route and page. List every affordance on it: buttons, links, inputs, text and chat boxes, menus, tabs, drawers, toggles, drag targets, uploads, downloads, keyboard paths, hover-only controls; empty, loading and error states; per-role differences; multi-user and multi-tab paths; and controls that show only after an action completes. Take rows from all of these sources, and compare them:

1. **The UI** — crawl it: `snapshot -i` on every page, in every state you can reach.
2. **The route table** — every route, also the ones no nav item links to.
3. **The API schema** — every mutation the UI can send.
4. **The docs** — what the product says a user can do.
5. **The code's components** — controls that render only in rare states.

A row that one source has and the UI does not is itself a finding.

One row per affordance: `page | affordance | what it does | inputs it accepts | roles | preconditions | cost (paid?)`.

After each deploy, refresh the inventory and diff it against the last one. New and changed rows go first: the newest code is the least hardened.

### 2. Triage into a run list

Turn the inventory into `run-list.md`: discrete, numbered things to try.

- **Variations.** Give each item its minor variations of user behaviour: order, timing, value shape, role, device width, repeat, interrupt.
- **Order.** Sort by dependency and user risk: the gate (happy path) first, then what most users touch, then the rest.
- **Lanes.** Group the items into independent lanes that run in parallel (one subagent each). Give each lane its own project, account and session, so lanes do not collide. Give each paid lane a budget, and stop the lane at its budget.
- **Coverage.** Map every inventory row to at least one run-list item, or mark it `skipped because …`. A row with neither is a gap in the run.

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
- **Mark each run-list item done** with the issue links it produced, so a crashed session can resume from the file.
- **Drive deliberately** per [driving.md](driving.md).

## End — coverage check

Check the run list against the inventory: every row tried, or skipped with a reason. A row with neither goes back on the run list. Then report per **After the pass** in [findings.md](findings.md), which starts with this coverage.

## When to deviate

- The user asked for one mode only → run that mode, but still from the inventory rows it touches.
- Time-boxed → a coarse inventory (pages and their controls) is still the first step; one real pass per phase is better than three shallow ones or a skipped phase.
- Phase 1 keeps failing → the run ends early; a broken happy path *is* the headline finding.
