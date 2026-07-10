---
name: comb
description: Repeatedly walk the happy path of an app, gently teasing out subtle knots — like combing hair until it runs silky.
---

# Comb

Go through the happy path over and over, with slight deviations, until the app feels silky smooth. This is **grooming**, not sabotage (that's [mischief.md](mischief.md)) and not a code review (that's [bug-hunter.md](bug-hunter.md)). You are simulating a calm, competent user — or a well-behaved API client — who keeps using the product as intended, then noticing every little snag.

Shared how-to: [driving.md](driving.md) (browser vs API) · [findings.md](findings.md) (what to do with knots).

## The combing metaphor

1. **Wide-toothed comb first.** Walk the happy path as expected. Don't try to break anything. Confirm the big strokes work: pages load / endpoints succeed, CTAs or next-steps go where they should, gates tell the truth, primary outputs appear.
2. **Same path again.** Repeat with another state, project, account, or payload. Reproducibility matters — comb the same area until it stays smooth.
3. **Narrower teeth.** Tease out larger obvious knots (wrong labels, dead buttons, stale state, 4xx/5xx on the happy path, laggy spinners). Still gentle.
4. **Finer and finer.** Drift slightly off the happy path into less-expected but still reasonable choices. Subtler bugs appear only after the coarse layer is clear.
5. **Fine-toothed finish.** The path flows with almost no friction. That's the goal.

Start wide every time you hit a fresh surface or a new deploy. Breadth-first on gross tangles, then drill down. Polishing copy while a CTA (or "success" API) points at the wrong outcome is wasted work.

## Specifics

- Stay close to the last path; move outward slowly so each knot is reproducible.
- On each screen (or each step in an API sequence), inventory available actions *before* choosing the next move.
- Do not cause mischief. Use the system as expected; deviate only gradually.
- Cross-check layers before you believe a knot — see [findings.md](findings.md).
- Watch your footprint. Prefer throwaway data; note when a verify left side effects.
- Eventually the remaining knots look almost like mischief — that's fine; by then the hair is mostly smooth.

## Driving while combing

Read [driving.md](driving.md). Short version for comb:

- **Browser-heavy** when grooming a webapp's UX (labels, CTAs, spinners, client state).
- **API-heavy** when the happy path is a sequence of calls (integrations, backend workflows) or you need many gentle repetitions with varied valid payloads.
- **Hybrid (preferred for webapps):** API to seed/reset state and assert backend truth; browser to confirm the human path still feels silky. After a UI pass, optionally replay the same happy path as a script so regressions are cheap to re-check.

## Knots

Handle per [findings.md](findings.md). Default: file GitHub issues with links; auto-fix only small tested knots if the user asked.

## See also

- [mischief.md](mischief.md) — opposite temper: break expected flow on purpose
- [bug-hunter.md](bug-hunter.md) — code-first hunt across many dimensions
- [driving.md](driving.md) · [findings.md](findings.md)
