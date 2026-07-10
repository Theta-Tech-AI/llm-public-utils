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

**Default order:** clear **gross** bugs first (breadth across screens/flows), then go **subtle** on surfaces that already hold under fire. A quiet subtle hunt while the CTA is dead is wasted cleverness — same spirit as comb's wide-toothed-before-fine, opposite temper.

When you escalate on quiet, say which axis you're escalating on (more gross paths vs deeper subtle setup).

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
