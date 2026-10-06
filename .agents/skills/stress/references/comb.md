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

- **Work the run list, not memory.** Each pass takes the next items from `run-list.md` ([process.md](process.md)) with their variations: order, timing, value shape, role, device width, repeat, interrupt. Run the step loop at each step; a calm user's expectation is the prediction, and a variation you invent mid-pass goes into the run list first.
- Stay close to the last path; move outward slowly so each knot is reproducible.
- Do not cause mischief. Use the system as expected; deviate only gradually.
- Cross-check layers before you believe a knot — see [findings.md](findings.md).
- Watch your footprint. Prefer throwaway data; note when a verify left side effects.
- Eventually the remaining knots look almost like mischief — that's fine; by then the hair is mostly smooth.

## Field-proven knots (read the rendered output, not just the flow)

The calmest, highest-value comb pass is to *read every user-facing string and the generated output itself*, as a real user would. These knots reach users first because a flow-only pass (does the button work?) never stops to read what's on screen:

1. **Leaked internal representation.** A surface shows a raw UUID, enum constant, internal project code or jargon, ISO/UTC timestamp or raw ratio. Walk every badge, toast, header, status line and label. **Flash of raw value:** the raw id shows for a moment, then swaps to the name; resolve first, render once. (Also grep-able: [bug-hunter.md](bug-hunter.md).)

2. **Copy that isn't written for the reader.** Trigger each error, warning, and empty state and read it cold. Flag: jargon the user can't act on; a warning that doesn't say *which* entity, *why*, or *what to do*; the wrong term for a concept (e.g. an "admin" vs "superuser" mismatch); and the same condition worded differently in different places. Good status/error copy states what happened, why, and the next action — in plain language, naming the specific entities involved.

3. **Non-cumulative aggregate metric.** A number meant to summarize across many contributors instead flips to whatever sub-source reported last (a running error/progress count that jumps 13 → 157 → 6 as different workers report in). A user-facing aggregate must be cumulative across all contributors, not last-writer-wins.

4. **Loading-state polish.** Watch every async surface through its loading→loaded transition. Flag: a blocking wait with a too-subtle or missing progress indicator (make long blocking loads loud and obvious); leftover or overly technical loading text ("releasing stale locks and refreshing…"); and unclear hierarchy when several progress indicators run at once (which card is the overall vs a sub-task?).

5. **Hide vs disable, and dead-end panels.** If a control is unusable for the entire duration of a state, prefer hiding it over showing it disabled (rows/tabs/buttons that can't be used until a batch job finishes are noise). And every panel/drawer/modal you can open needs a visible way to close it.

6. **Sibling-control inconsistency.** Two controls that do the same kind of thing should look and behave the same (same style, same hover/affordance). Inconsistent siblings read as unfinished.

7. **Read the generated artifact itself.** When the product produces an output document/report/export, open it and read it — structure, ordering, and every value — not just the flow that made it. Thin, duplicated, mis-ordered, or scaffold-leaking output is invisible to a flow-only pass. (Deeper failure modes and the code-first version live in [bug-hunter.md](bug-hunter.md).)

8. **Blank vs loading.** A surface that renders empty/blank while data is still loading reads as "there is no data." Distinguish the two: show a real (loud, unmistakable, even blocking) loading indicator with granular status where possible, and an explicit empty state *only* once loading has truly finished with nothing to show. A blank card mid-load is a knot.

9. **Generic where it should be contextual.** A warning, error, or status that shows a templated message without interpolating the *actual* affected entities and current situation forces the user to guess. Name which items are affected, what state they're in, and what to do next — written for a non-expert who just wants to know what happened and what to do.

10. **Generated content too thin for its slot.** When the product generates prose/content into a structured slot, check depth and shape against what that slot expects — a one-sentence stub where a full paragraph belongs is a quality bug even though "content appeared." (Pairs with item 7 — read the artifact.)

11. **Activity/telemetry that shows a reference, not verifiable substance.** A "what the system did" surface (tool-call log, activity feed, result preview) that shows only a bare reference — a file path, an id, a "success" — without enough to confirm the operation was actually *correct* invites silent wrong behavior. Prefer showing (or letting the user open) the real substance, and separately confirm the underlying operation did the right thing, not merely that it ran.

## Sweep surface by surface, not path by path

Walking the path again and again is the right shape for reliability, but as a comb it skims: each surface gets a glance on the way to the next. Go **depth-first per surface, breadth across surfaces**:

1. **Park on one surface** and work every inventory row on it, every label, empty state, number, transition, and the second instance of anything repeatable. Move on when the surface stops yielding, not when the path lets you.
2. **File everything, fix nothing.** Stopping to fix loses the state you built and lets the surface go cold. Fixes run behind you as a separate pipeline; come back to confirm them later.

The per-surface backlog is the deliverable, not a pass/fail verdict. Expect it to be slow: one surface can yield a dozen real issues, and a pass that "covered every page" in an hour skimmed. If you move on because a surface *worked*, you are path-combing again.

## Time-dependent knots (a settled snapshot cannot see them)

`open` → wait → `snapshot` observes the settled state by construction. Anything that exists only during a transition, after idling or across two views is unreachable that way: a control that shows for a second while the page loads and then vanishes (clickable by mistake, which matters when the action is destructive or costs money); a session-expiry warning that fires only when you return to an idle tab; a summary figure that changes when you switch tabs with nothing spent between; an error toast from navigating during a long job. Drive for time:

1. **Sample during load.** Snapshot immediately on navigation and a beat later, then diff. Present early and absent later is a flash. A trigger control that flashes and then hides because the job auto-started must pick one behaviour: auto-start and never show it, or require the click.
2. **Idle deliberately** past a session, lease or token lifetime, then return.
3. **Diff one widget across navigations.** A count, cost or status that changes without an action is wrong.
4. **Act during async work:** switch tabs, navigate away and back, open sibling views while a job is live.
5. **Watch the console for the whole pass.** Repeated 4xx/5xx from background polls never show in the DOM and are often the first sign of a doomed request.

## Comparison knots (one path, walked once, can never find these)

A comb pass traverses. These knots exist only in the *difference* between two
things, so no single traversal — however careful the reading — surfaces them.
You have to create a second instance, or hold two surfaces side by side.

### Plurality: exercise the SECOND one

The primary instance is exercised constantly; the second often runs different code (another data source, a fallback, an aggregate written when only one existed). Typical shapes: a secondary record shows a raw id where the primary shows a name because an untested fallback fired; a "selected items" list shows only the active group; a header total summarises only the active tab; a second concurrent job hits a lock the first never contended for.

- Seed at least **two** of every repeatable entity and drive the second, ideally a deliberately **sparser** one (no optional fields, no enrichment): fallbacks live there, and leaked internals with them.
- Verify any summarising figure **aggregates** rather than reporting the selected context.

### Cross-surface: the same concept, rendered twice

A value shown in two places must agree and look the same (shared component in one surface, raw in another). When you meet a count, cost, status or entity name, find its other rendering and compare formatting, units, rounding and wording; a mismatch is a knot even when both read fine alone.

The interaction-level checks — persistence-by-reload, responsive resize, occlusion, hover/keyboard, and every-clickable-goes-somewhere — live in the frontend driving playbook in [driving.md](driving.md); run them alongside these reading-level knots. Comb reads the front door; the playbook drives it.

## See also

- [mischief.md](mischief.md) — opposite temper: break expected flow on purpose
- [bug-hunter.md](bug-hunter.md) — code-first hunt across many dimensions
- [driving.md](driving.md) · [findings.md](findings.md) — knots are filed per findings; auto-fix only small tested knots when asked
