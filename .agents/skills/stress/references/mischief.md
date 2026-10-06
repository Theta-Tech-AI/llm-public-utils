---
name: mischief
description: Red-team the app on purpose — break staging with creative, context-derived, relentless attacks (UI and API) so users never hit those cracks. Use for mischief, chaos testing, hostile inputs, wrong-order flows, and hardening before release.
---

# Mischief

Act in ways the system *does not expect*. Wrong order. Wrong time. Twice. Under load. With garbage. Mid-abandon. While another tab mutates the step above. The paranoid system hopes you take the happy path — your job is to refuse. Shared how-to: [driving.md](driving.md) · [findings.md](findings.md). Know the happy path first ([comb.md](comb.md)) so attacks are aimed — then stop blessing it.

## Philosophy

Mischief has a purpose: every crack you find gets a fix and a regression anchor, and the surface that survives your worst is the one users can trust. Do not hold back the weird idea, the absurd ordering or the hostile input; a real user will find it. You are hunting bugs, not confirming it works. They hide under "works in the demo": the race that fires only on double-click, the gate that dead-ends after a refreeze, the 500 that appears when a dependency is down.

## Mission

Break staging early, on purpose, in private. **A found bug is the goal, never a setback.**

| Rule | Meaning |
|------|---------|
| Quiet ≠ whole | Escalate (load, concurrency, timing, malformed input, combine categories) until something gives. |
| Never done | Parallel agents change code; yesterday's green is not today's. Re-break continuously. |
| No ceiling | Catalogs are a floor. Invent new categories when you run dry. |
| Capture the bait | File per [findings.md](findings.md) with the **exact** click order / request — make it a regression anchor. |

## How to hunt

It is the step loop of [process.md](process.md) with a hostile choice: `recon (snapshot) → pick tier and hands → invent the attack this state invites (choose) → predict what a hardened app does → execute → cross-check (measure; the UI lies) → file if real → escalate or descend tier`.

### 1. Recon — re-map before you re-break

Your targets are the rows of the inventory ([process.md](process.md)): **every input and control in it gets attacked**, not only the ones the happy path uses. Other agents ship new routes, tabs and relabels constantly, and the freshest code is where state-machine bugs live. After every deploy, refresh the inventory, diff it against the last one, and hit **new and changed** rows first.

### 2. Prioritize — finish a tier before you descend

Gross first, all of it, across the whole app. Sweep **breadth until dry**, then drop one notch of subtlety and sweep again. Do **not** deep-dive one component six ways while order-of-operations bugs sit unfound elsewhere. Workflow confidence is **earned by driving illegal orderings**, not assumed from one happy-path pass. Say which tier you're on when you escalate (comb's wide-tooth-before-fine, opposite temper).

| Tier | Hunt |
|------|------|
| **1 — hard gross** | 500s / blank / dead-ends / data-bleed / lying gates |
| **2 — workflow gross** | stale-after-upstream / leaked pollers / non-terminal states / missing forward CTAs |
| **3 — interaction** | double-submit / control-state desync / lock-or-freeze granularity |
| **4 — deep subtle** | optimistic concurrency / validation-version binding / audit-chain races / idempotency-key scoping |

### 3. Pick your hands — browser, API, or both

Browser for the chaotic user (wrong-order clicks, Back, multi-tab, abandon mid-wizard); API for contracts, concurrency, illegal sequences and payload matrices; hybrid to discover in the UI and amplify by script, or to break the API and see whether the UI recovers or lies. Detail: [driving.md](driving.md).

### 4. Invent the attack *this* page invites (radio test in practice)

The catalog names the buttons; your job is the order of presses nobody tried. Absorb the screen, entity state, workflow stage, domain constraint and the code behind it, and ask what it is *assuming*. What impatient, confused or hostile thing could a user do right here? What assumption can I violate? What two features interact untested? Treat this page's inventory rows as raw material for illegal sequences, not a checklist. If quiet, escalate until it rattles or you have earned "held under fire" for this page at this tier. Blind generic payloads are weak; specific mischief is lethal.

### 5. Cross-check always — the UI lies by omission

A clean snapshot is **not** proof: SPAs swallow the 4xx/5xx that mischief triggers into "button does nothing." Measure every probe on UI, `console` + `network`, an API probe of the same resource, and logs if needed. Twin mischief (UI silent / API screaming, or UI blocked / API allowed) is this class.

### 6. Patterns that flush bugs

**Poke every inventory row, not only the forward CTA.** Demo-untouched tools hide unguarded mutations (secondary checkers, attach/verify, version rails, per-row links, regenerate, review handshakes, advanced panels). Hostile-drive each: wrong time, twice, while a job is live, after delete, second token. **Human factor:** start mid-flight, navigate away, switch entity, return; interrupt with Back, tab close, a second session or a competing API call; watch for leaked pollers, orphaned leases, stranded modals, zombie drafts and cross-entity bleed. **Moves that hurt:** wrong order or time; create→delete→mutate; double-submit; stale token; two writers on one lock; force the "disabled" action via API (or the reverse); escalate on quiet.

### 7. API frontend-simulator (high-yield hands)

No browser required: reverse-engineer what the frontend would send, then break that conversation. Map mutations from SPA client / OpenAPI / HAR; create disposable scratch (superuser OK for *create* only); attack with normal user tokens; prefix `MISCHIEF-…` / `SCRATCH-…`; clean up. Blast each mutation: malformed, contradictory, **cross-resource IDs**, wrong order/time, unexpected concurrency. Often finds validation gaps, cross-tenant/project refs accepted, and audit/atomicity failures.

## Field-proven state-contradiction classes (bugs users hit first)

These classes reach a human first because they surface only when the *live UI* is driven into a specific state. Drive every staged or multi-step flow against all of them.

1. **Downstream stage reachable with an unmet upstream prerequisite.** A later step must be unreachable — by its nav control **and** by pasting its deep-link URL directly — until its upstream gate is genuinely satisfied. The classic root cause: the frontend derives "is this step available" from a source that can disagree with the backend's authoritative prerequisite state (e.g. "downstream data already exists in the store" gets treated as "the upstream gate passed"). Check every stage *both* ways (click the nav item, and paste the URL). A stage that renders — or half-renders, then throws an unclear "prerequisite not met" error — with an incomplete predecessor is a bug even if data appears. Verify the guard's *error copy* too: it must name what's missing and the next action, not emit a bare internal code.

2. **The inverse — a completed stage that hides its forward affordance.** Over-restriction is also a bug. When a step is already complete/locked, the "continue to next step" control must still be present (even if it no longer needs a re-run confirmation). A locked step with no way forward strands the user.

3. **Action enabled while its target is disabled (control-state contradiction).** A "Lock / Submit / Save selection" button is active while the very thing it acts on (the table, form, or selection it would lock) is greyed out and uneditable. The enable-state of an action and the enable-state of the data it operates on are derived independently and disagree. For every action control, confirm the thing it mutates is in a consistent, matching state.

4. **First-visit / transient wrong state that only self-corrects on manual refresh.** Arrive at a page *immediately* from the upstream action, before any poller settles, and watch the first render without touching anything. A page that shows "not ready" / stale / empty until you hit refresh — while the backend is actually ready — is a real bug. Common shape: arriving on a page should auto-start a job (the precondition is met), but the job only kicks off after a manual refresh or re-trigger. It must converge to the true state on its own.

5. **Return-to-in-flight-job orphaning.** Start a long-running job on a page, navigate away, then return (or refresh) while it's still running. The page must re-attach to the in-flight run and keep reporting progress (or offer cancel) — not silently orphan the run, prompt a conflicting "re-run" that could double-fire, or leave the user unsure whether work is happening in the background. Test every page that launches an async job this way.

These pair with the rendered-output knots in [comb.md](comb.md) and the statically-catchable roots in [bug-hunter.md](bug-hunter.md) — the same bug often has a comb symptom, a mischief trigger, and a bug-hunter root.

### Front-door chaos (the user's real environment, not yours)

Run the [driving.md](driving.md) playbook hostile and mid-flow: resize during a wizard, reload before a change settles, Back and cold deep-links in a fresh tab, a banner over the control. Then hit the app while the backend is rolling or down: the front door should show a maintenance state, not a raw 502 or a white screen (rule out a false alarm first — see [findings.md](findings.md)).

## Report

Per [findings.md](findings.md): search before filing, file early, over-document repro + evidence + labels. Filing *is* the point unless asked to auto-fix. Then keep hunting.

## See also

- [comb.md](comb.md) — gentle happy-path grooming (sibling, opposite temper)
- [bug-hunter.md](bug-hunter.md) — code-first hunt
- [driving.md](driving.md) · [findings.md](findings.md)
