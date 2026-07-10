---
name: comb
description: Repeatedly walk the happy path of an app, gently teasing out subtle knots — like combing hair until it runs silky.
---

# Comb

Go through the happy path over and over, with slight deviations, until the app feels silky smooth. This is **grooming**, not sabotage (that's [mischief.md](mischief.md)) and not a code review (that's [bug-hunter.md](bug-hunter.md)). You are simulating a calm, competent user who keeps using the product the way it was meant to be used — then noticing every little snag.

## The combing metaphor

1. **Wide-toothed comb first.** Walk the happy path as expected. Don't try to break anything. Confirm the big strokes work: pages load, CTAs go where they should, gates tell the truth, primary outputs appear.
2. **Same path again.** Repeat with another state, another project, another account if available. Reproducibility matters — comb the same area until it stays smooth.
3. **Narrower teeth.** Tease out larger obvious knots (wrong labels, dead buttons, stale state, laggy spinners). Still gentle.
4. **Finer and finer.** Drift slightly off the happy path into less-expected but still reasonable choices. Subtler bugs appear only after the coarse layer is clear.
5. **Fine-toothed finish.** The path flows with almost no friction. That's the goal.

Start wide every time you hit a fresh surface or a new deploy. Breadth-first on gross tangles, then drill down. Polishing copy while a CTA points at the wrong page is wasted work.

## Specifics

- Stay close to the last path; move outward slowly so each knot is reproducible.
- On each screen, inventory buttons and actions *before* choosing the next move.
- Do not cause mischief. Use the system as expected; deviate only gradually.
- Cross-check layers before you believe a knot: UI snapshot + console/network + API/backend (and infra/deploy health if you have it). A scary screenshot is not a bug until two more layers agree. A clean screenshot is not proof either.
- Rule out false alarms: deploy/roll in flight, stale SPA chunks, your own earlier mutations, and tool limitations (e.g. undriveable custom widgets).
- Watch your footprint. Prefer throwaway data; note when a verify left side effects.
- Eventually the remaining knots look almost like mischief — that's fine; by then the hair is mostly smooth.
- This is an app-user behavior simulator, not a static code review.

## Tools

- **Agent browser (or equivalent):** Drive the real UI. Closest to a user wins. Prefer this for webapps.
- **API / scripts:** Replay the happy path with `curl` or small scripts — faster for backend confirmation, not a substitute for UI.
- **Infra CLIs / logs:** `az`, `aws`, `gh run list`, server logs, telemetry — confirm the happy path is healthy end-to-end, not just pretty on the frontend.

## What to do with knots

Default: **file a GitHub issue** per real knot and give the user the hyperlink. If there's no GitHub, write a markdown/HTML artifact.

If the user wants auto-fix: fix small, additive, tested knots as you go; leave large/load-bearing ones filed. Ask once if instructions are unclear.

## See also

- [mischief.md](mischief.md) — opposite temper: break expected flow on purpose
- [bug-hunter.md](bug-hunter.md) — code-first hunt across many dimensions
