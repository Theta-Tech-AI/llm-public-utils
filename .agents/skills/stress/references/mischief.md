---
name: mischief
description: Act in ways the system does not expect — out-of-order clicks, illegal API sequences, API frontend-simulator blasts, half-done flows, chaos — to surface bugs before real users do.
---

# Mischief

Cause mischief: act in ways the system *does not expect*. Click out of order. Hit Back at the worst moment. Fire API calls in illegal sequences. Leave things half-done. Jump users mid-flow. Disrupt the happy path on purpose so the paranoid system — which hopes you always behave — has to cope.

Shared how-to: [driving.md](driving.md) · [findings.md](findings.md).

## Why

Humans (and buggy clients) are excellent at breaking software by accident. Better that an agent finds those breaks first. Mischief hardens the app against strange, impatient, multi-tab, multi-user, and multi-request reality.

Know the happy path first (a short [comb](comb.md) pass helps). Mischief without a map is just noise.

## How to be most mischievous

1. **Look before you leap.** Observe current UI state *or* resource/API state. Guessing blind wastes probes.
2. **Pick the move that hurts most and you haven't tried yet.** Half-finished form → another section → different user → fail an async job. Or: create → delete → mutate; double-submit; replay with a stale token; two writers on one lock.
3. **Challenge gates.** Are the live buttons / allowed methods the ones that *should* be live? What happens if you force the "wrong" action via UI **or** API? UI-blocked but API-allowed (or the reverse) is a classic bug class — see twin mischief in [driving.md](driving.md).
4. **Use the code.** Ugly workflows and confusing branches are a map of where to strike next.
5. **Go breadth-first on gross breaks**, then subtler races and state corruption — same axis as comb, opposite temper.

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

This is not random noise — it is a **hostile simulator of the frontend's API usage**, then the same calls in illegal sequences and shapes. Pair with [driving.md](driving.md) API techniques; file per [findings.md](findings.md) as soon as something confirms.

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

Handle per [findings.md](findings.md). Default: file issues and report links — filing *is* the point unless the user asked to auto-fix.

## See also

- [comb.md](comb.md) — gentle happy-path grooming
- [bug-hunter.md](bug-hunter.md) — find bugs by reading code, not only by breaking flows
- [driving.md](driving.md) · [findings.md](findings.md)
