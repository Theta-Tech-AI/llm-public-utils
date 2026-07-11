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

## Field-proven knots (read the rendered output, not just the flow)

The calmest, highest-value comb pass is to *read every user-facing string and the generated output itself*, as a real user would. These knots reach users first because a flow-only pass (does the button work?) never stops to read what's on screen:

1. **Leaked internal representation.** A surface shows an internal value instead of a human one: a raw UUID/id instead of a name, a raw enum/status constant, an internal project code or jargon (ticket/spec/phase identifiers meant for the team, not the user), an ISO/UTC timestamp instead of localized time, or a raw ratio/counter. Walk every badge, toast, header, status line, and label — each raw internal value is a knot. **Special case — flash of raw value:** a field shows the raw id for a fraction of a second, then swaps to the resolved name once a lookup returns. Resolve first, render once; never paint the placeholder id. (Also grep-able — see [bug-hunter.md](bug-hunter.md).)

2. **Copy that isn't written for the reader.** Trigger each error, warning, and empty state and read it cold. Flag: jargon the user can't act on; a warning that doesn't say *which* entity, *why*, or *what to do*; the wrong term for a concept (e.g. an "admin" vs "superuser" mismatch); and the same condition worded differently in different places. Good status/error copy states what happened, why, and the next action — in plain language, naming the specific entities involved.

3. **Non-cumulative aggregate metric.** A number meant to summarize across many contributors instead flips to whatever sub-source reported last (a running error/progress count that jumps 13 → 157 → 6 as different workers report in). A user-facing aggregate must be cumulative across all contributors, not last-writer-wins.

4. **Loading-state polish.** Watch every async surface through its loading→loaded transition. Flag: a blocking wait with a too-subtle or missing progress indicator (make long blocking loads loud and obvious); leftover or overly technical loading text ("releasing stale locks and refreshing…"); and unclear hierarchy when several progress indicators run at once (which card is the overall vs a sub-task?).

5. **Hide vs disable, and dead-end panels.** If a control is unusable for the entire duration of a state, prefer hiding it over showing it disabled (rows/tabs/buttons that can't be used until a batch job finishes are noise). And every panel/drawer/modal you can open needs a visible way to close it.

6. **Sibling-control inconsistency.** Two controls that do the same kind of thing should look and behave the same (same style, same hover/affordance). Inconsistent siblings read as unfinished.

7. **Read the generated artifact itself.** When the product produces an output document/report/export, open it and read it — structure, ordering, and every value — not just the flow that made it. Thin, duplicated, mis-ordered, or scaffold-leaking output is invisible to a flow-only pass. (Deeper failure modes and the code-first version live in [bug-hunter.md](bug-hunter.md).)

## Knots

Handle per [findings.md](findings.md). Default: file GitHub issues with links; auto-fix only small tested knots if the user asked.

## See also

- [mischief.md](mischief.md) — opposite temper: break expected flow on purpose
- [bug-hunter.md](bug-hunter.md) — code-first hunt across many dimensions
- [driving.md](driving.md) · [findings.md](findings.md)
