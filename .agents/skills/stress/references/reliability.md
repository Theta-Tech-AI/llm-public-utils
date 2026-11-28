---
name: reliability
description: Confirm the app works reliably before anything fancier — re-run the happy path until it consistently completes, because reliability is what earns user trust. Use as the gate at the start of any stress run, in the browser or by API.
---

# Reliability

The gate before [comb.md](comb.md) and [mischief.md](mischief.md) — the first driving phase of the standard run in [process.md](process.md), after setup (environments, access, drive modes).

## Philosophy
It doesn't matter if it produces shit - if it produces shit reliably and consistently, well maybe a mushroom which eats shit will come to depend on it, and perhaps even spark an intellectual revolution via its hallucinogenic properties.

You never know what value others may derive from something unexpectedly, outside of what you thought they care about. And oftentimes, you only discover that by building something so reliable that people are able use it repeatedly, trusting that it will "just work" and not break.

When a system is not reliable, and obscure or unexpected bugs occur, people develop a general anxiety right before using it, and never get to the point where they can extract the true value from it for themselves.

Being reliable, consistently working, is what enables a sense of relief or trust in a system which makes usage sticky.

When you put the video game into the system, you never have to worry that the menu will be glitchy. You don't expect weird user behavior bugs. Those things lose the immersiveness of the game. The same applies to software systems.

## The gate

Run the primary happy path end to end. Then again, up to three times in all.

- **Pass** = the run completes successfully, with the same result each time — no flakiness, silent retries, or console, network or log errors along the way.
- **Fail** = stop. File per [findings.md](findings.md) and hold the run here. There is no point in finding issues with the system unless the happy path is consistently functional — fix (or report and wait) before continuing.
- **Already proven** (a fresh green end-to-end run in CI, or a just-completed reliability pass on this deploy) → a single confirmation pass suffices.
- **A single requested app-driving phase** ("just cause mischief") still starts with that confirmation pass on the happy path it stands on, or with the evidence that it is already proven; say which in the report.
- **A new build** serving the environment reopens the gate.

**By API**, the gate is one fresh end-to-end flow from a new object to the final deliverable, driven as the real roles ([api.md](api.md#4-flows-and-fixtures)). **No test writes until the gate passes**, in the browser or by API: the gate's own flow on its own fresh object is the only exception. Until then every other tester and lane may map, read code, read state and prepare drivers — but creates no scratch data, starts no paid or metered work, and mutates no seed. A read with a known write effect (an audited download, a read that appends an audit record) counts as a write and waits too. Time each stage: a stage that takes hours, needs an administrator's workaround, or contradicts its own state is a finding. Open the final deliverable and read its content, not only its status ([api.md → Record](api.md#6-oracles-one-property-across-everything)).
