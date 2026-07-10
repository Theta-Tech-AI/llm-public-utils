---
name: mischief
description: Act in ways the system does not expect — out-of-order clicks, half-done flows, chaos — to surface bugs before real users do.
---

# Mischief

Cause mischief: act in ways the system *does not expect*. Click out of order. Hit Back at the worst moment. Leave things half-done. Jump users mid-flow. Disrupt the happy path on purpose so the paranoid system — which hopes you always behave — has to cope.

## Why

Humans are excellent at breaking software by accident. Better that an agent finds those breaks first. Mischief hardens the app against strange, impatient, multi-tab, multi-user reality.

Know the happy path first (a short [comb](comb.md) pass helps). Mischief without a map is just noise.

## How to be most mischievous

1. **Look before you leap.** Observe the current layout and state. Guessing blind wastes probes.
2. **Pick the move that hurts most and you haven't tried yet.** Half-finished form → another section → different user → fail an async job. Stack disruptions.
3. **Challenge enabled/disabled controls.** Are the live buttons the ones that *should* be live? What happens if you force the "wrong" one via UI or API?
4. **Use the code.** Ugly workflows and confusing branches are a map of where to strike next.
5. **Go breadth-first on gross breaks**, then subtler races and state corruption — same axis as comb, opposite temper.

## Tools

- **Agent browser:** Primary weapon for webapps. Drive it like a chaotic user, not a script that only hits APIs.
- **API out of order:** Valid and useful — wrong sequence, stale tokens, double-submit, concurrent writers — but UI mischief catches what APIs miss (enabled buttons, nav traps, modal races).
- **Multi-actor:** Two sessions, two roles, one shared resource. Collaboration bugs love mischief.

Still cross-check before filing: UI + network/console + backend. Don't file deploy flakes or tool misses as product bugs.

## What to do with bugs

Default: file a **GitHub issue** per real bug and report hyperlinks to the user. No GitHub → markdown/HTML artifact.

If context clearly says auto-fix, fix as you go; otherwise shake the ground and surface bugs — filing is the point unless told otherwise.

## See also

- [comb.md](comb.md) — gentle happy-path grooming
- [bug-hunter.md](bug-hunter.md) — find bugs by reading code, not only by breaking flows
