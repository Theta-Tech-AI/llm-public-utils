---
name: mischief
description: Red-team the app on purpose — break staging with creative, context-derived, relentless attacks (UI and API) so users never hit those cracks. Use for mischief, chaos testing, hostile inputs, wrong-order flows, and hardening before release.
---

# Mischief

Act in ways the system *does not expect*. Wrong order. Wrong time. Twice. Under load. With garbage. Mid-abandon. While another tab mutates the step above. The paranoid system hopes you take the happy path — your job is to refuse. Shared how-to: [driving.md](driving.md) · [findings.md](findings.md). Know the happy path first ([comb.md](comb.md)) so attacks are aimed — then stop blessing it.

## Philosophy

Mischief has a purpose. The better you get at breaking it — the more creative, more devious, more relentless the attack — the more hardened the system becomes. Every crack you find gets a fix and a regression anchor; the surface that survives your worst is the surface the user can trust. Embrace your mischief. Don't hold back the weird idea, the absurd ordering, the hostile input — that is exactly the one a real user will stumble into. **Creativity in breaking is the engine of hardening**; the meaner you are to staging today, the smoother it is for the real user tomorrow. You are not "testing to confirm it works." You are **hunting for delicious bugs**, and mischief is the bait that draws them out of hiding. Bugs sit buried under "works fine in the demo." Shake the system until they scatter into the open: the race that only fires on double-click, the gate that only dead-ends after a refreeze, the 500 that only appears when a dependency is down.

## Mission

Break staging early, on purpose, in private, so real users get something that "just works." You are not here to bless the happy path — you are here to find where it cracks. **A found bug is the goal, never a setback.**

| Rule | Meaning |
|------|---------|
| Quiet ≠ whole | Escalate (load, concurrency, timing, malformed input, combine categories) until something gives. |
| Never done | Parallel agents change code; yesterday's green is not today's. Re-break continuously. |
| No ceiling | Catalogs are a floor. Invent new categories when you run dry. |
| Capture the bait | File per [findings.md](findings.md) with the **exact** click order / request — make it a regression anchor. |

## How to hunt

One loop — stay in it: `recon → pick tier → pick hands (browser / API / both) → invent the attack this page invites → execute → cross-check (UI lies) → file if real → escalate or descend tier`.

### 1. Recon — re-map before you re-break

Other agents ship new routes, tabs, buttons, and relabels constantly. **New UI/API area = new place bugs hide** — and the freshest, least-hardened code is exactly where state-machine bugs live. The bug that reaches a human first is usually in the place you didn't know existed yet. Every few runs — and **always after a deploy** — recon from scratch: (1) cold-open and walk primary nav plus every reachable tab/sub-page; (2) `snapshot -i` / inventory controls anew; (3) diff against your last map; (4) prefer **new and changed** areas first at your current tier; (5) re-check gates and order-of-operations on paths you thought were done. **Re-map before you re-break.** A catalog from yesterday is not a map of today's app.

### 2. Prioritize — finish a tier before you descend

Gross first, all of it, across the whole app. Sweep **breadth until dry**, then drop one notch of subtlety and sweep again. Do **not** deep-dive one component six ways while order-of-operations bugs sit unfound elsewhere. Workflow confidence is **earned by driving illegal orderings**, not assumed from one happy-path pass. Say which tier you're on when you escalate (comb's wide-tooth-before-fine, opposite temper).

| Tier | Hunt |
|------|------|
| **1 — hard gross** | 500s / blank / dead-ends / data-bleed / lying gates |
| **2 — workflow gross** | stale-after-upstream / leaked pollers / non-terminal states / missing forward CTAs |
| **3 — interaction** | double-submit / control-state desync / lock-or-freeze granularity |
| **4 — deep subtle** | optimistic concurrency / validation-version binding / audit-chain races / idempotency-key scoping |

### 3. Pick your hands — browser, API, or both

These are **how you touch the app**, not "attack surfaces" (that's the page/route/API you're targeting after recon). Full install/usage and API technique tables: [driving.md](driving.md). Ask consent before installing agent-browser.

| Hands | Best for |
|-------|----------|
| **Browser** | Chaotic user: wrong-order clicks, Back, multi-tab, abandon mid-wizard, every workbench control |
| **API** | Contracts, concurrency, illegal sequences, payload matrices — fast and systematic |
| **Both (hybrid)** | Discover in UI → amplify with scripts; or break API → see if UI recovers or lies |

### 4. Invent the attack *this* page invites (radio test in practice)

You don't prove a radio by reading the button list — you mash every button in every order, plug it in wrong, drop it, and see what rattles. **The catalog names the buttons; your job is the order of presses nobody tried.** Absorb this screen, entity state, data model, workflow stage, domain constraint, last deploy, and the code behind it — what is it *assuming*? Inventory every control, then treat that list as raw material for illegal sequences, not a checklist. Ask: What impatient/confused/hostile thing could a user do *right here*? What assumption can I violate? What two features interact untested? What seam with the next step? What press-order has nobody tried? Execute that context-derived attack; if quiet, escalate until it rattles — or you've earned "held under fire" for *this* page at *this* tier. Blind generic payloads are weak; specific mischief is lethal.

### 5. Cross-check always — the UI lies by omission

A clean snapshot is **not** proof. Mischief triggers 4xx/5xx constantly; SPAs swallow them into "button does nothing." Half the best bugs never appear on screen. Every probe: UI → `console` + `network` (xhr/fetch, 4xx/5xx) → API probe of the same resource → logs if needed. Twin mischief (UI silent / API screaming, or UI blocked / API allowed) is this class.

### 6. Patterns that flush bugs

**Poke every tool, not only the forward CTA.** Each route is a workbench — demo-untouched tools hide unguarded mutations (secondary checkers, attach/verify, version rails, per-row links, regenerate, review handshakes, advanced panels). Hostile-drive each: wrong time, twice, while a job is live, after delete, second token. Once tier-1 on the page is dry, prefer obscure tools. **Agent-browser:** refs go stale after re-renders — re-`snapshot -i` before each repeated click; read content via snapshot/get-text; wrap `eval` in an IIFE ([driving.md](driving.md)). **Human factor:** start mid-flight → navigate away → other entity → return; interrupt with Back, tab close, second session, competing API; watch for leaked pollers, orphaned leases/locks, stranded modals, lost/zombie drafts, cross-entity data bleed (tier 1–2). **Moves that hurt:** wrong order/time; create→delete→mutate; double-submit; stale token; two writers on one lock; multi-actor; force the "disabled" action via API (or reverse); use ugly code as a map of where to strike; escalate on quiet.

### 7. API frontend-simulator (high-yield hands)

No browser required: reverse-engineer what the frontend would send, then break that conversation. Map mutations from SPA client / OpenAPI / HAR; create disposable scratch (superuser OK for *create* only); attack with normal user tokens; prefix `MISCHIEF-…` / `SCRATCH-…`; clean up. Blast each mutation: malformed, contradictory, **cross-resource IDs**, wrong order/time, unexpected concurrency. Often finds validation gaps, cross-tenant/project refs accepted, and audit/atomicity failures.

```bash
SCRATCH=$(curl -sS -X POST "$BASE/api/projects" -H "authorization: Bearer $SUPERUSER_TOKEN" \
  -H 'content-type: application/json' -d '{"name":"MISCHIEF-scratch-1"}' | jq -r .id)
curl -sS -X PATCH "$BASE/api/projects/$SCRATCH/items/$OTHER_PROJECT_ITEM_ID" \
  -H "authorization: Bearer $USER_TOKEN" -H 'content-type: application/json' \
  -d '{"project_id":"'"$SCRATCH"'"}'
seq 1 10 | xargs -P 10 -I{} curl -sS -o /dev/null -w "%{http_code}\n" -X POST \
  "$BASE/api/projects/$SCRATCH/submit" -H "authorization: Bearer $USER_TOKEN"
```

## Field-proven state-contradiction classes (bugs users hit first)

These classes repeatedly reach a human before a sweep catches them, because they only surface when you drive the *live UI* into a specific real state — code review and API probes miss them. Each is a mischief target with a concrete check. Drive every staged/wizard/multi-step flow against all of them.

1. **Downstream stage reachable with an unmet upstream prerequisite.** A later step must be unreachable — by its nav control **and** by pasting its deep-link URL directly — until its upstream gate is genuinely satisfied. The classic root cause: the frontend derives "is this step available" from a source that can disagree with the backend's authoritative prerequisite state (e.g. "downstream data already exists in the store" gets treated as "the upstream gate passed"). Check every stage *both* ways (click the nav item, and paste the URL). A stage that renders — or half-renders, then throws an unclear "prerequisite not met" error — with an incomplete predecessor is a bug even if data appears. Verify the guard's *error copy* too: it must name what's missing and the next action, not emit a bare internal code.

2. **The inverse — a completed stage that hides its forward affordance.** Over-restriction is also a bug. When a step is already complete/locked, the "continue to next step" control must still be present (even if it no longer needs a re-run confirmation). A locked step with no way forward strands the user.

3. **Action enabled while its target is disabled (control-state contradiction).** A "Lock / Submit / Save selection" button is active while the very thing it acts on (the table, form, or selection it would lock) is greyed out and uneditable. The enable-state of an action and the enable-state of the data it operates on are derived independently and disagree. For every action control, confirm the thing it mutates is in a consistent, matching state.

4. **First-visit / transient wrong state that only self-corrects on manual refresh.** Arrive at a page *immediately* from the upstream action, before any poller settles, and watch the first render without touching anything. A page that shows "not ready" / stale / empty until you hit refresh — while the backend is actually ready — is a real bug. Common shape: arriving on a page should auto-start a job (the precondition is met), but the job only kicks off after a manual refresh or re-trigger. It must converge to the true state on its own.

5. **Flash of a control that then disappears.** On first load a page briefly shows a "trigger / generate" control, then auto-starts and hides it. Pick one behavior and commit — either auto-start (and never show the manual trigger) or require the click. A control that appears then vanishes reads as a missed click and a flicker.

6. **Return-to-in-flight-job orphaning.** Start a long-running job on a page, navigate away, then return (or refresh) while it's still running. The page must re-attach to the in-flight run and keep reporting progress (or offer cancel) — not silently orphan the run, prompt a conflicting "re-run" that could double-fire, or leave the user unsure whether work is happening in the background. Test every page that launches an async job this way.

These pair with the rendered-output knots in [comb.md](comb.md) and the statically-catchable roots in [bug-hunter.md](bug-hunter.md) — the same bug often has a comb symptom, a mischief trigger, and a bug-hunter root.

## Report

Per [findings.md](findings.md): search before filing, file early, over-document repro + evidence + labels. Filing *is* the point unless asked to auto-fix. Then keep hunting.

## See also

- [comb.md](comb.md) — gentle happy-path grooming (sibling, opposite temper)
- [bug-hunter.md](bug-hunter.md) — code-first hunt
- [driving.md](driving.md) · [findings.md](findings.md)
