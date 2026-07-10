---
name: mischief
description: Act in ways the system does not expect — out-of-order clicks, illegal API sequences, half-done flows, chaos — to surface bugs before real users do.
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

## Driving while causing mischief

Read [driving.md](driving.md). Short version for mischief:

- **Browser:** chaotic user — out-of-order clicks, Back, multi-tab, abandon mid-wizard.
- **API:** often *stronger* for concurrency, idempotency, authz bypass attempts, illegal state transitions, and flooding a flow with variants. Scripts make "do the wrong thing 100 ways" tractable; browsers make "do the wrong thing the way a human would" tractable.
- **Hybrid:** discover a suspicious sequence in the UI, then amplify it with parallel API clients; or break the contract via API and see whether the UI recovers or lies.

Multi-actor (two sessions / two tokens / two roles, one shared resource) loves mischief on both surfaces.

## Bugs

Handle per [findings.md](findings.md). Default: file issues and report links — filing *is* the point unless the user asked to auto-fix.

## See also

- [comb.md](comb.md) — gentle happy-path grooming
- [bug-hunter.md](bug-hunter.md) — find bugs by reading code, not only by breaking flows
- [driving.md](driving.md) · [findings.md](findings.md)
