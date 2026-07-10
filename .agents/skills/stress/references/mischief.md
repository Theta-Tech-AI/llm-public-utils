---
name: mischief
description: Red-team the app on purpose — break staging with creative, context-derived, relentless attacks (UI and API) so users never hit those cracks. Use for mischief, chaos testing, hostile inputs, wrong-order flows, and hardening before release.
---

# Mischief

Cause mischief: act in ways the system *does not expect*. Click out of order. Hit Back at the worst moment. Fire API calls in illegal sequences. Leave things half-done. Jump users mid-flow. Disrupt the happy path on purpose so the paranoid system — which hopes you always behave — has to cope.

Shared how-to: [driving.md](driving.md) · [findings.md](findings.md).

## Purpose (red team)

Your job is to **try to break staging** — so the user doesn't have to.

Break it early, on purpose, in private, so that by the time it reaches real hands it is smooth as butter and solid as a rock — it "just works." Every bug you flush out here is one a user never hits in real usage.

Be relentless: **actively try to break it**. Do not merely confirm it works. Hunt for the click order, the input, the timing, the concurrency, the load that makes it fall over.

A quiet run does **not** mean the system is whole — it means you weren't aggressive or creative enough. **Escalate** (add concurrency, add timing, add malformed input, combine categories) until something gives.

You are not here to bless the happy path. You are here to find where it cracks, before the user does. **Break it on purpose, here, now — that is the job. A found bug is the goal, never a setback.**

## Why we do this: mischief makes bugs unearth themselves

Mischief is not a checklist you complete — it is a **bug-hunting method**. Bugs don't announce themselves on the happy path; they sit buried under "works fine in the demo."

The way you flush them out is to **shake the system**: click at the wrong time, in the wrong order, twice, under load, with garbage input, while another agent (or tab, or token) mutates the step above. The more chaos you introduce, the more latent bugs scatter and surface on their own — a race that only fires under a double-click, a stale gate that only dead-ends after a refreeze, a 500 that only appears when a dependency is down.

You are not "testing to confirm it works." You are **hunting for delicious bugs**, and mischief is the bait that draws them out of hiding.

### Consequences of this framing — internalize them

1. **More mischief = more bugs surfaced.** A quiet run that finds nothing usually means you weren't creative or aggressive enough, not that the system is perfect. Escalate: add load, add concurrency, add timing, add malformed input, combine categories.
2. **The mischief is never done.** Parallel agents keep changing the code; every change can resurrect a bug a previous run buried. Re-run previously-passing mischief continuously — a green result from yesterday is not a green result today.
3. **There is no exhaustive set.** When you run out of ideas, invent new categories or ask the user / another agent for more. A system can always be broken in a more creative way; any catalog in this skill (or in the repo) is a **starting point, not a ceiling**.
4. **A surfaced bug is the goal, not a setback.** Every bug mischief drags into the light is one the real user never hits. Hunt them eagerly; report each one per [findings.md](findings.md) with the **exact click order / request** that flushed it out so it becomes a permanent regression anchor.

## The UI lies by omission — hunt the swallowed failure

The single most important driving habit — and it matters **more for mischief than for comb**: a clean snapshot is **not** proof.

Half of mischief's best bugs are failures the screen never shows. You are deliberately triggering 4xx/5xx constantly, and the SPA often eats them — a 403 with an HTML body gets swallowed as something like "Could not parse error response body (status 403)" while on screen it reads as "the button just does nothing."

Without looking at network/console/API truth, you log "button is a dead no-op" (wrong diagnosis) or miss the bug entirely. With it, you have the real knot: an ungraceful error the product hid.

The whole point of mischief — surface ungraceful errors before a real user hits them — depends on catching the error the UI hid. Always cross-check:

1. Agent-browser / UI observation
2. `console` + `network requests` (filter xhr/fetch, status 4xx/5xx)
3. Direct API probe of the same resource when unsure
4. Backend/worker logs if the request never left or never returned cleanly

See [driving.md](driving.md) and [findings.md](findings.md). Twin mischief (UI blocked vs API allowed, or UI silent vs API screaming) is often exactly this class.

## Poke every tool on the page — not just the happy-path button

Each route is a **workbench**. Knots and unguarded mutations hide in the tools the demo never touches — secondary checkers, attach/verify flows, version rails, per-row links, regenerate, review/comment handshakes, "advanced" panels, anything that isn't the big forward CTA.

For every page you land on:

1. `agent-browser snapshot -i` — enumerate **all** interactive controls, not just the primary button.
2. Drive **each** control in a hostile way: wrong time in the workflow, twice, while a run/job is live, after delete, under a second tab/token.
3. Cross-check **console + network + a backend probe** every time (see swallowed failures above).
4. Prefer attacking obscure tools first once tier-1 gross paths on that page are dry — they're least demo-hardened.

### Agent-browser gotchas while poking tools

- **Refs shift** after every click that re-renders. For repeated clicks, grab the ref **fresh** each iteration (`snapshot -i` again) — do not reuse `@e3` from three actions ago.
- **Read rendered document/content via snapshot** (or dedicated get-text on a scoped ref). Some layouts do not expose body text to a naive page `eval`; don't conclude "empty/missing" from a bad eval.
- **Wrap every `eval` body in an IIFE** — a bare `return` throws `Illegal return statement`. Prefer snapshot/get over eval when either works.

## Philosophy

Mischief has a purpose. The better you get at breaking it — the more creative, more devious, more relentless the attack — the more hardened the system becomes. Every crack you find gets a fix and a regression anchor; the surface that survives your worst is the surface the user can trust.

Embrace your mischief. Don't hold back the weird idea, the absurd ordering, the hostile input — that is exactly the one a real user will stumble into. **Creativity in breaking is the engine of hardening**; the meaner you are to staging today, the smoother it is for the real user tomorrow.

**The radio test.** You don't prove a new radio by reading the manual's button list — you mash every button in every order, plug it in wrong, drop it, and see what rattles. Same here. Look at the frontend in front of you and be creative with what mischief you can cause. The catalog (docs, snapshots, route lists) names the buttons; **your job is to find the order of presses nobody tried** — and the wrong plug, the drop, the rattle.

Know the happy path first (a short [comb](comb.md) pass helps) so your attacks are aimed — but do not stop at "it worked once."

## Absorb context, then invent *this* attack

Mischief is most lethal when it is **specific to what you're looking at**, not a generic payload fired blind.

1. **Absorb the bigger picture first.** Look at the actual frontend in front of you — this screen, this project's (or tenant's) state, this data model, this workflow stage, this domain constraint, what just changed in the last deploy. Read the page, read the code behind it, understand what it's trying to do and what it's *assuming*. Inventory every control you can see — then refuse to treat that inventory as a checklist to tick; treat it as raw material for illegal sequences.
2. **Invent the attack this surface invites.** Ask:
   - Given everything I now understand, what weird / hostile / impatient / confused thing could a real user do *right here* that the authors probably didn't think about?
   - What assumption is this screen (or endpoint) making that I can violate?
   - What two features interact in a way nobody tested?
   - What happens at the seam between this component and the next?
   - What order of presses (clicks, tabs, API calls) has nobody tried on *this* screen?
3. That **context-derived attack** — the one no catalog entry names — is worth more than ten generic ones. Derive it from the details + the big picture; don't wait to be told. Mash, mis-order, mis-plug; listen for the rattle.

Then escalate: if the clever attack fails quietly, combine it with concurrency, timing, malformed input, or a second actor until the crack shows — or you've earned a hard-won "held under fire" for *this* surface.

## Two axes: gross vs subtle (pick deliberately)

Mischief lives on two axes. **Consciously choose** where you're spending effort — don't drift into subtle land while gross cracks are still open.

| Axis | What it is | Examples | Why it matters |
|------|------------|----------|----------------|
| **GROSS** | Obvious, immediate breakage a user hits on a normal-ish path | 500 / blank page / dead-end; gate that won't open (or opens too early); forward CTA that never appears; nav that lies; one project's data on another's page; stale "ready" after an upstream change; action silently lost | Cheap to trigger, expensive to ship — a human finds them in the first five minutes of real use |
| **SUBTLE** | Deep edge cases inside one component or invariant | Validation keyed to id-not-version; audit hash-chain race; optimistic-concurrency gap; idempotency-key scoping | Real, but need deliberate setup and a narrow trigger |

### Tier ladder — finish a tier before you descend

The order is **GROSS first, all of it, across the whole app** — and only once you genuinely cannot find any more breakage at the current tier do you drop a level into the next tier of subtlety, work that tier to exhaustion, and so on down.

Don't jump straight to clever optimistic-concurrency races while a page still 500s or dead-ends somewhere. Each level: **sweep it broad until dry**, then refine the resolution one notch and sweep again.

Gross bugs first because they're the ones a user hits in five minutes **and** they're the cheapest to find — spending a subtle-bug budget while gross bugs remain is mis-prioritized effort.

Practical ladder:

1. **Tier 1 — hard gross:** 500s / blank / dead-ends / data-bleed / lying gates
2. **Tier 2 — workflow gross:** stale-after-upstream-change / leaked pollers / non-terminal states / missing forward CTAs
3. **Tier 3 — interaction:** double-submit / control-state desync / freeze (or lock) granularity
4. **Tier 4 — deep subtle:** optimistic-concurrency / validation-version binding / audit-chain races / idempotency-key scoping

**Finish a tier before you descend.** Same spirit as comb's wide-toothed-before-fine, opposite temper.

Do **not** pour a whole run into stress-testing one component six ways while gross order-of-operations bugs sit unfound across the rest of the app. We do **not** actually know the workflow "just works" under various orders of operations at each stage — that confidence has to be **earned by driving it**, not assumed because the happy path passed once. Sweep stages and illegal orderings breadth-first; only then deep-dive a single component.

When you escalate on quiet, say which **tier** you're on and whether you're still sweeping breadth or ready to descend.

### Recon — don't attack from a stale map

Other agents (and humans) continuously ship new routes, sub-pages, tabs, and buttons, and relabel/move existing controls. **New surface = new attack surface** — and the freshest, least-hardened code is exactly where state-machine bugs hide.

So don't attack from a stale map. **Every few runs (and always after a fresh deploy lands), do a from-scratch recon:**

1. Open the app cold (or hard-refresh); walk primary nav and every tab/sub-page you can reach in the current workflow stage.
2. Snapshot or inventory controls anew — names, enabled/disabled, new CTAs, moved buttons.
3. Diff mentally (or in notes) against your last map: what appeared, disappeared, or changed meaning?
4. Prefer attacking **new and changed** surfaces first at the current tier — they're the least battle-tested.
5. Re-check gates and order-of-operations on paths you thought were "done"; a merge can reintroduce gross breakage.

A catalog from yesterday is not a map of today's app. The bug that reaches a human first is usually in the surface you didn't know existed yet. **Re-map before you re-break.**

## How to be most mischievous

1. **Look before you leap.** Observe current UI state *or* resource/API state. Guessing blind wastes probes.
2. **Pick the move that hurts most and you haven't tried yet.** Half-finished form → another section → different user → fail an async job. Or: create → delete → mutate; double-submit; replay with a stale token; two writers on one lock.
3. **Challenge gates.** Are the live buttons / allowed methods the ones that *should* be live? What happens if you force the "wrong" action via UI **or** API? UI-blocked but API-allowed (or the reverse) is a classic bug class — see twin mischief in [driving.md](driving.md).
4. **Use the code.** Ugly workflows and confusing branches are a map of where to strike next.
5. **Go breadth-first on gross breaks**, then subtler races and state corruption — same axis as comb, opposite temper.
6. **Escalate on quiet.** No bug yet → add concurrency, timing, malformed input, cross-resource refs, multi-actor; combine categories. Quiet ≠ done.

## High-yield: API frontend-simulator

A fast, systematic, **no-browser** mischief mode: reverse-engineer what the frontend would send to the backend, then deliberately break that conversation.

1. **Map the client contract.** From the SPA/API client, OpenAPI, or a HAR of a happy path, list every mutation the UI can make (`POST` / `PUT` / `PATCH` / `DELETE`) and the usual order/payloads.
2. **Spin up a disposable scratch resource** (project, tenant, workspace — whatever the app's unit of isolation is). Prefer a **superuser / admin token** only to *create* throwaway scratch data quickly; then attack with normal user tokens too. Prefix names (`MISCHIEF-…`, `SCRATCH-…`) and delete when done.
3. **Blast every mutation endpoint** you can find against that scratch world. For each route, try:
   - **Malformed** bodies (wrong types, missing required fields, extra unknown fields, huge strings, null vs omit)
   - **Contradictory** payloads (field A says X while field B implies not-X; status + content that can't both be true)
   - **Cross-referencing** IDs from *another* project/user/resource (classic cross-tenant / cross-project reference bugs)
   - **Wrong order / wrong time** — call step 4 before step 1; mutate after delete; approve before submit; freeze then edit
   - **Unexpected concurrency** — parallel identical writes, two roles on one lock, overlapping submits
4. **Watch for real bug classes this method repeatedly finds:** input validation gaps, cross-project (or cross-tenant) references accepted, audit/atomicity failures (partial writes, missing audit rows, success response with rolled-back state).

This is not random noise — it is a **hostile simulator of the frontend's API usage**, then the same calls in illegal sequences and shapes. Still prefer **context-derived** variants once you know *this* screen's assumptions. Pair with [driving.md](driving.md) API techniques; file per [findings.md](findings.md) as soon as something confirms.

Sketch:

```bash
# 1) Create scratch (superuser) → 2) attack with user token
SCRATCH=$(curl -sS -X POST "$BASE/api/projects" -H "authorization: Bearer $SUPERUSER_TOKEN" \
  -H 'content-type: application/json' -d '{"name":"MISCHIEF-scratch-1"}' | jq -r .id)

# Happy-path-shaped call, then wrong-order / cross-ref variants
curl -sS -X PATCH "$BASE/api/projects/$SCRATCH/items/not-a-real-id" \
  -H "authorization: Bearer $USER_TOKEN" -H 'content-type: application/json' \
  -d '{"status":"approved","content":null}'

curl -sS -X PATCH "$BASE/api/projects/$SCRATCH/items/$OTHER_PROJECT_ITEM_ID" \
  -H "authorization: Bearer $USER_TOKEN" -H 'content-type: application/json' \
  -d '{"project_id":"'"$SCRATCH"'"}'   # cross-project reference probe

# Concurrency: double-submit the same mutation
seq 1 10 | xargs -P 10 -I{} curl -sS -o /dev/null -w "%{http_code}\n" -X POST \
  "$BASE/api/projects/$SCRATCH/submit" -H "authorization: Bearer $USER_TOKEN"
```

## Driving while causing mischief

Read [driving.md](driving.md). Short version for mischief:

- **Browser:** chaotic user — out-of-order clicks, Back, multi-tab, abandon mid-wizard.
- **API:** often *stronger* for concurrency, idempotency, authz bypass attempts, illegal state transitions, and flooding a flow with variants. Prefer the **API frontend-simulator** above when you want systematic coverage without a browser.
- **Hybrid:** discover a suspicious sequence in the UI, then amplify it with parallel API clients; or break the contract via API and see whether the UI recovers or lies.

Multi-actor (two sessions / two tokens / two roles, one shared resource) loves mischief on both surfaces.

## Bugs

Handle per [findings.md](findings.md). Default: file issues and report links — filing *is* the point unless the user asked to auto-fix. A found bug is success: capture it durably, then keep hunting.

## See also

- [comb.md](comb.md) — gentle happy-path grooming
- [bug-hunter.md](bug-hunter.md) — find bugs by reading code, not only by breaking flows
- [driving.md](driving.md) · [findings.md](findings.md)
