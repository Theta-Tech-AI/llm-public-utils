---
name: mischief
description: Red-team the app on purpose — break staging with creative, context-derived, relentless attacks (UI and API) so users never hit those cracks. Use for mischief, chaos testing, hostile inputs, wrong-order flows, and hardening before release.
---

# Mischief

Act in ways the system *does not expect*. Wrong order. Wrong time. Twice. Under load. With garbage. Mid-abandon. While another tab mutates the step above. The paranoid system hopes you take the happy path — your job is to refuse.

Shared how-to: [driving.md](driving.md) · [findings.md](findings.md). Know the happy path first ([comb.md](comb.md)) so attacks are aimed — then stop blessing it.

## Philosophy

Mischief has a purpose. The better you get at breaking it — the more creative, more devious, more relentless the attack — the more hardened the system becomes. Every crack you find gets a fix and a regression anchor; the surface that survives your worst is the surface the user can trust.

Embrace your mischief. Don't hold back the weird idea, the absurd ordering, the hostile input — that is exactly the one a real user will stumble into. **Creativity in breaking is the engine of hardening**; the meaner you are to staging today, the smoother it is for the real user tomorrow.

You are not "testing to confirm it works." You are **hunting for delicious bugs**, and mischief is the bait that draws them out of hiding. Bugs don't announce themselves on the happy path; they sit buried under "works fine in the demo." Shake the system — wrong time, wrong order, twice, under load, garbage input, while another agent mutates the step above — until latent bugs scatter into the open.

**The radio test.** You don't prove a new radio by reading the manual's button list — you mash every button in every order, plug it in wrong, drop it, and see what rattles. Same here. Look at the frontend and be creative. The catalog names the buttons; **your job is to find the order of presses nobody tried.**

## Mission

Break staging early, on purpose, in private, so real users get something that "just works." You are not here to bless the happy path — you are here to find where it cracks. **A found bug is the goal, never a setback.**

Internalize:

| Rule | Meaning |
|------|---------|
| Quiet ≠ whole | You weren't aggressive enough. Escalate (load, concurrency, timing, malformed input, combine categories) until something gives. |
| Never done | Parallel agents change code; yesterday's green is not today's. Re-break continuously. |
| No ceiling | Catalogs are a floor. Invent new categories when you run dry. |
| Capture the bait | File per [findings.md](findings.md) with the **exact** click order / request that flushed the bug — make it a regression anchor. |

## Discipline: gross → subtle, map → break

### Tier ladder — finish a tier before you descend

Sweep **breadth-first until dry**, then drop one notch of subtlety and sweep again. Do not pour a run into one component six ways while order-of-operations bugs sit unfound across the app. Workflow confidence is **earned by driving illegal orderings**, not assumed from one happy-path pass.

| Tier | Hunt |
|------|------|
| **1 — hard gross** | 500s / blank / dead-ends / data-bleed / lying gates |
| **2 — workflow gross** | stale-after-upstream / leaked pollers / non-terminal states / missing forward CTAs |
| **3 — interaction** | double-submit / control-state desync / lock-or-freeze granularity |
| **4 — deep subtle** | optimistic concurrency / validation-version binding / audit-chain races / idempotency-key scoping |

Gross first: cheapest to find, first thing a human hits in five minutes. Say which tier you're on when you escalate.

### Recon — re-map before you re-break

Other agents ship new routes, tabs, buttons, and relabels constantly. **New surface = new attack surface**; freshest code hides state-machine bugs. Every few runs — and **always after a deploy** — recon from scratch: cold open, walk nav/sub-pages, inventory controls, prefer **new/changed** surfaces, re-check paths you thought were done. The bug that reaches a human first is usually in the surface you didn't know existed. **Re-map before you re-break.**

## How to hunt

### 1. Absorb this surface, invent *this* attack

Blind generic payloads are weak. Read the page, the state, the data model, the workflow stage, the last deploy, the code behind it — what is it *assuming*? Inventory every control, then treat that inventory as raw material for illegal sequences, not a tick-list.

Ask: What impatient/confused/hostile thing could a user do *right here*? What assumption can I violate? What two features interact untested? What seam between this component and the next? What press-order has nobody tried?

That context-derived attack beats ten catalog entries. If it fails quietly, escalate until it rattles — or you've earned "held under fire" for *this* surface at *this* tier.

### 2. Cross-check always — the UI lies by omission

A clean snapshot is **not** proof. Mischief triggers 4xx/5xx constantly; SPAs swallow them into "button does nothing." Half the best bugs never appear on screen.

Every probe: UI observation → `console` + `network` (xhr/fetch, 4xx/5xx) → API probe of the same resource → logs if needed. Twin mischief (UI silent / API screaming, or UI blocked / API allowed) is this class. See [driving.md](driving.md).

### 3. Poke every tool — not only the forward CTA

Each route is a **workbench**. Demo-untouched tools hide unguarded mutations: secondary checkers, attach/verify, version rails, per-row links, regenerate, review handshakes, advanced panels.

`snapshot -i` → hostile-drive **each** control (wrong time, twice, while a job is live, after delete, second token) → cross-check every time. Once tier-1 on the page is dry, prefer obscure tools.

**Agent-browser:** refs go stale after re-renders — re-`snapshot -i` before each repeated click. Read content via snapshot/get-text, not a naive eval. Wrap `eval` bodies in an IIFE (`return` at top level throws).

### 4. Human factor — abandon, wander, change your mind

Real users start, bail, jump elsewhere, wander back. Practice it: start mid-flight → navigate away → other entity → return. Interrupt with Back, tab close, second session, competing API.

Watch for: leaked pollers, orphaned leases/locks, stranded modals, lost or zombie drafts, cross-project/tenant data bleed. Classic tier-1/2.

### 5. Moves that hurt

- Wrong order / wrong time; create → delete → mutate; approve before submit
- Double-submit; stale token; two writers on one lock; multi-actor / multi-tab
- Force the "disabled" action via API (or the reverse) — gate lies
- Use ugly code paths as a map of where to strike next
- Escalate on quiet — quiet ≠ done

## Surfaces

| Surface | Use when |
|---------|----------|
| **Browser** | Chaotic user: out-of-order clicks, Back, multi-tab, abandon mid-wizard, every workbench tool |
| **API frontend-simulator** | Systematic, no-browser: map what the UI would send, then break it |
| **Hybrid** | Discover in UI → amplify with scripts; or break API → see if UI recovers or lies |

### API frontend-simulator (high yield)

1. Map mutations from SPA client / OpenAPI / HAR (`POST`/`PUT`/`PATCH`/`DELETE` + usual order).
2. Create a disposable scratch resource (superuser token OK for *create* only); attack with normal user tokens; prefix `MISCHIEF-…` / `SCRATCH-…`; clean up.
3. Blast each mutation: malformed, contradictory, **cross-resource IDs**, wrong order/time, unexpected concurrency.
4. Bug classes this repeatedly finds: validation gaps, cross-tenant/project refs accepted, audit/atomicity failures.

```bash
SCRATCH=$(curl -sS -X POST "$BASE/api/projects" -H "authorization: Bearer $SUPERUSER_TOKEN" \
  -H 'content-type: application/json' -d '{"name":"MISCHIEF-scratch-1"}' | jq -r .id)

curl -sS -X PATCH "$BASE/api/projects/$SCRATCH/items/$OTHER_PROJECT_ITEM_ID" \
  -H "authorization: Bearer $USER_TOKEN" -H 'content-type: application/json' \
  -d '{"project_id":"'"$SCRATCH"'"}'

seq 1 10 | xargs -P 10 -I{} curl -sS -o /dev/null -w "%{http_code}\n" -X POST \
  "$BASE/api/projects/$SCRATCH/submit" -H "authorization: Bearer $USER_TOKEN"
```

More API patterns: [driving.md](driving.md).

## Report

Per [findings.md](findings.md): search before filing, file early, over-document repro + evidence + labels. Filing *is* the point unless asked to auto-fix. Then keep hunting.

## See also

- [comb.md](comb.md) — gentle happy-path grooming (sibling, opposite temper)
- [bug-hunter.md](bug-hunter.md) — code-first hunt
- [driving.md](driving.md) · [findings.md](findings.md)
