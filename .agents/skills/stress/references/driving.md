---
name: driving
description: How to drive an app under stress — agent browser vs API vs hybrid — and when each surface finds different bugs.
---

# Driving: Browser vs API

Stress testing needs hands on the system. Two primary surfaces, different bugs:

| Surface | What it is | Bugs it catches well | Weak at |
|---------|------------|----------------------|---------|
| **Agent browser** (headless UI) | Click/type like a user in the real SPA | Enabled/disabled controls, nav traps, modal races, labels, spinners, client-only state, "looks fine but feels broken" | Fast combinatorial sequences, auth-edge floods, pure contract bugs |
| **API** (`curl`, scripts, HTTP clients) | Talk to backends the way the frontend (or other services) would | Ordering, idempotency, authz, validation, concurrency, stale tokens, double-submit, schema drift, worker/queue failures | Visual/UX knots, wrong button affordances, layout/state that never hits the network |

Neither replaces the other. Prefer **hybrid**: use the API to set up state and probe contracts fast; use the browser to confirm what a human would actually experience.

## When to lean API-first

- You need **many repetitions** (same flow 50× with different payloads) — browsers are slow; scripts are cheap.
- You are testing **contracts**: status codes, error bodies, pagination, filtering, webhooks, batch endpoints.
- You need **concurrency**: parallel writers, two users on one resource, race on "lock" / "submit".
- Auth is easier via tokens/headers than through a full IdP UI (or you already have a token mint script).
- The bug is suspected **behind** the UI (worker, DB invariant, permission check) and the UI only obscures it.
- Comb/mischief on a surface that is **API-native** (CLI consumers, integrations, mobile clients, partner webhooks).

## When to lean browser-first

- The product *is* a webapp and the user cares about **UX knots**.
- Affordance bugs: button enabled when it shouldn't be, CTA to the wrong step, modal that traps focus.
- Client-only failure modes: stale chunk after deploy, optimistic UI that lies, local cache vs server.
- You are still learning the happy path and need to *see* the app.

## Hybrid patterns (high leverage)

1. **API setup → browser verify.** Create/seed entities via API; comb or mischief only the UI that matters.
2. **Browser discover → API amplify.** Find a suspicious sequence in the UI; replay it as a script with variations and concurrency.
3. **API assert while browser drives.** During a UI pass, watch network + optionally `curl` the same resources to confirm backend truth (cross-check layers).
4. **Twin mischief.** Break ordering in the UI *and* fire the same illegal sequence via API — UI might block a button the API still accepts (or vice versa). That gap is a real bug class.

## Practical notes

- Record repros with the surface that found them: UI steps *or* exact request sequence (method, path, headers stripped of secrets, body, expected vs actual).
- Prefer throwaway accounts/data for destructive API probes.
- Don't conclude "missing/broken" from a tool miss (undriveable widget, gzipped asset grep, flaky headless). Confirm with a second surface when unsure.
- Infra CLIs and logs (`gh run`, cloud logs, worker tails) are a third surface for "is this a product bug or a deploy/roll?" — see [findings.md](findings.md).

## See also

- [comb.md](comb.md) · [mischief.md](mischief.md) · [bug-hunter.md](bug-hunter.md) · [findings.md](findings.md)
