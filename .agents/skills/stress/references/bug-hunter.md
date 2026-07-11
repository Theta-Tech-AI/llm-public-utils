---
name: bug-hunter
description: Hunt bugs in code from many angles — layers, workflows, data models, error handling — before users feel them.
---

# Bug Hunter

Sniff out bugs. They're subtle, but they're always there, just in the distance.

You are a hunter. Over-engineered brush hides obscure, rare bugs. Obsess over the *proper* way to do a thing, then compare it to how the code actually behaves. Catch-all `except` that returns `None`? Juicy. Silent fallbacks that paper over real failures? Prey.

Shared how-to when you need live proof: [driving.md](driving.md) · reporting: [findings.md](findings.md).

## Holistic view

The best hunts see the forest for the trees. Bugs hide in coupling, folder layout, and seams between services — places a single-file glance never reaches.

Slice the system across many dimensions and hunt in each corner:

- by layer (UI, API, worker, DB)
- by service / package boundary
- by user role and permission
- by workflow / state machine
- by abstraction level
- by class or module
- by information / domain model
- by schema and migrations
- by maintainability smells that *become* runtime bugs

The bugs that make hunters squeal are the ones that only appear from a *new* angle — rare by definition.

## Purpose

Find bugs before the user feels anything negative. Put aside bias: elegance and complexity can both hide defects.

Balance:

- **High-impact, user-touching bugs** that move the needle today
- **Subtle deferred bombs** that get swept under the rug until the worst moment

Unearth both. Don't only chase clever edge cases while ignoring the broken primary button — and don't only file obvious nits while ignoring the landmine in error handling.

## Method

1. Skim architecture and entrypoints; name the critical workflows.
2. Pick 2–3 dimensions from the list above and go deep, not every dimension at once.
3. Prefer bugs you can *demonstrate* (repro steps, failing assumption, bad invariant) over vibes.
4. When a code smell suggests a runtime failure, confirm via the cheapest honest surface — often an **API probe** or focused test; use the browser when the defect is UI-shaped. See [driving.md](driving.md).
5. Pair with [comb.md](comb.md) / [mischief.md](mischief.md) when a static finding needs a full live pass.

## Field-proven code-first classes

These classes have each burned a real user, and each is catchable statically or with a focused probe — hunt them explicitly:

1. **Two derived views of one entity, from two sources, that can disagree.** A summary and its detail are computed independently: a red "N problems" badge whose click opens an empty panel; a "Locked / Complete" banner beside a list that still shows unconfirmed items; an expand affordance shown for one item but not its identically-shaped sibling. Grep for a count/badge/status derived from a *different* source than the list/detail it summarizes. The summary and the detail must flow from one source of truth.

2. **Generated content falsely reports a missing input that exists elsewhere.** A generator/agent/pipeline that composes output from a primary source store falsely reports "insufficient input" / "no data" for a field whose value actually lives in a *different* part of the system — a form the user already filled, frozen configuration, or an upstream stage's output — that the generator has no tool or code path to reach. For every input a generator can flag as missing, verify it has a retrieval path to *every* place that input can legitimately live, not just the primary store. Related: cross-stage ordering where a later step needs an earlier step's output must be enforced so the later step isn't starved of data that already exists.

3. **Humanization gaps (static grep).** Search the view layer for rendering a raw identifier, enum, timestamp, or internal code directly into user-facing text without a formatter / label-map / name-lookup. This is the code-first counterpart to the comb "leaked internal representation" knot ([comb.md](comb.md)) and catches most instances without a browser.

4. **Counter / ratio invariants.** A progress counter rendered as `X/Y` must guarantee `X ≤ Y` and a sane, same-source denominator — a nonsensical value like `2/1` means "completed" and "total" are computed from different (or stale) sources. Check every `done/total` render for a shared source and a bound.

5. **Telemetry wired but not surfaced.** If the system already tracks a quantity (tokens, cost, timing, counts), verify it's actually surfaced where the user expects it — per-item *and* cumulative, live. "Cost: Pending" while the underlying tokens are already known is a wiring gap, not a missing feature. And attach a metric to the step it describes, not as its own confusing pseudo-step.

## Bugs

Handle per [findings.md](findings.md). Default: one GitHub issue per distinct bug with repro or reasoning; summarize with links and ask what to fix now.

## See also

- [comb.md](comb.md) — live happy-path grooming
- [mischief.md](mischief.md) — live adversarial probing
- [driving.md](driving.md) · [findings.md](findings.md)
