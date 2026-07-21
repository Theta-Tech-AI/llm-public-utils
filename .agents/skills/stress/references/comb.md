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

8. **Blank vs loading.** A surface that renders empty/blank while data is still loading reads as "there is no data." Distinguish the two: show a real (loud, unmistakable, even blocking) loading indicator with granular status where possible, and an explicit empty state *only* once loading has truly finished with nothing to show. A blank card mid-load is a knot.

9. **Generic where it should be contextual.** A warning, error, or status that shows a templated message without interpolating the *actual* affected entities and current situation forces the user to guess. Name which items are affected, what state they're in, and what to do next — written for a non-expert who just wants to know what happened and what to do.

10. **Generated content too thin for its slot.** When the product generates prose/content into a structured slot, check depth and shape against what that slot expects — a one-sentence stub where a full paragraph belongs is a quality bug even though "content appeared." (Pairs with item 7 — read the artifact.)

11. **Activity/telemetry that shows a reference, not verifiable substance.** A "what the system did" surface (tool-call log, activity feed, result preview) that shows only a bare reference — a file path, an id, a "success" — without enough to confirm the operation was actually *correct* invites silent wrong behavior. Prefer showing (or letting the user open) the real substance, and separately confirm the underlying operation did the right thing, not merely that it ran.

## Sweep surface-by-surface, not path-by-path

The passes above describe walking the happy path repeatedly. That is the right
shape for *reliability*, but as a comb structure it skims: each surface is
touched briefly on the way to the next, so only knots big enough to interrupt
the path get noticed.

The higher-yield structure is the opposite — **depth-first per surface, breadth
across surfaces**:

1. **Park on ONE surface** and interrogate everything about it: every control,
   label, empty state, number, transition, and the second instance of anything
   repeatable. Do not advance because the path allows you to advance; advance
   when that surface has stopped yielding.
2. **File everything, fix nothing.** Each finding becomes an issue with enough
   detail that someone else can work it. Stopping to fix collapses the sweep —
   you lose the state you built up, and the surface you were on goes cold.
3. **Advance while fixes proceed behind you.** The backlog for surface N is
   being worked while you are combing surface N+1. Combing and fixing are
   different activities that contend for the same attention; run them as
   separate pipelines.
4. **Return later to confirm**, once fixes land, rather than blocking on them.

The per-surface backlog IS the deliverable, not a pass/fail verdict for the run.

**Expect this to be slow, and do not treat that as failure.** A single surface
can yield a dozen genuine issues, and a real sweep of a multi-surface product
does not finish in one sitting. A pass that "covered every page" in an hour
almost certainly skimmed. If you find yourself moving on because a surface
*worked*, you are path-combing again — working is the precondition for combing
it, not the conclusion.

## Time-dependent knots (the ones a settled snapshot cannot see)

The reading-level knots above assume you can look at the screen. Several whole
classes are invisible to the way an agent normally drives: `open` → wait for the
page to settle → `snapshot`. That rhythm observes the **settled** state by
construction, so anything that exists only *during* a transition, *after*
idling, or *across* two views is structurally unreachable — the checklist above
can ask for it and you will still never see it.

Typical misses, all of which reach real users:

- a control that appears for a second or two while the page loads and then
  vanishes as the work it offered starts by itself — gone before the first
  snapshot exists, yet long enough for a user to click it
- a session/token expiry warning that only fires when you come back to a tab
  left open — needs idling
- a summary figure that changes when you switch tabs, with nothing spent or
  saved in between — needs comparing one widget across two views
- an error toast produced by navigating *during* a long-running job — needs
  acting while async work is in flight

### Drive for time, not just for path

1. **Sample during load, not after it.** Snapshot immediately on navigation and
   again a beat later, before the settle, and diff them. Anything present early
   and absent later is a flash — and a control that flashes is a control a user
   can click by mistake, which matters far more than cosmetics when the action
   is destructive or costs money.
2. **Idle deliberately.** Leave a page open past a session, lease, or token
   lifetime and return to it. Anything that fires on return is invisible to a
   pass that never stops moving.
3. **Diff one widget across navigations.** Note a count, cost, or status; go
   elsewhere; come back or switch tabs; compare. A figure that changes without a
   corresponding action is wrong even when each view looks right on its own.
4. **Act during async work, not after it.** Long-running work is exactly when
   real users click elsewhere. Switch tabs, navigate away and back, and open
   sibling views *while* a job is live, rather than waiting for it to finish.
5. **Watch the console for the whole pass.** Repeated 4xx/5xx from background
   polls and auto-started work never appear in the DOM, and are often the first
   evidence of a doomed request the UI is quietly retrying.

This is a second axis over the reading-level pass, not a replacement. A knot
that exists for two seconds still reached a user.

## Comparison knots (one path, walked once, can never find these)

A comb pass traverses. These knots exist only in the *difference* between two
things, so no single traversal — however careful the reading — surfaces them.
You have to create a second instance, or hold two surfaces side by side.

### Plurality: exercise the SECOND one

Paths for "the first / primary / default" are exercised constantly. The second
instance often runs different code — another data source, a fallback, an
aggregate written when only one existed. A pass that creates one account, one
workspace, one document, one member never touches it. Typical shapes:

- a secondary record renders a raw internal id where the primary renders a
  human name, because the secondary lacks the enrichment the primary happened
  to have and an untested fallback fires
- a list labelled "selected items" shows only the currently-active group rather
  than all of them
- a header total summarises only the active tab, so it moves when you switch
- a second concurrent job hits a lock the first never contended for, failing in
  a way the single-job path never exposes

Rules:
- Seed at least **two** of every repeatable entity, and drive the second.
- Prefer a second instance that is deliberately **sparser** — missing optional
  fields, no upstream enrichment. Fallbacks live there, and fallbacks are where
  leaked internals appear.
- For any figure claiming to summarise, verify it **aggregates** rather than
  reporting whichever context is selected.

### Cross-surface: the same concept, rendered twice

A value shown in two places must agree and look the same. Divergence is
invisible while you look at either alone: a quantity formatted with the shared
component in one surface and raw in another; the same information presented two
different ways on two screens that could share a component.

Rule: when you meet a value that appears elsewhere — a count, a cost, a status,
an entity name — go find its other rendering and compare formatting, units,
rounding and wording. Decide which is canonical; a mismatch is a knot even when
both are individually readable.

The interaction-level checks — persistence-by-reload, responsive resize, occlusion, hover/keyboard, and every-clickable-goes-somewhere — live in the frontend driving playbook in [driving.md](driving.md); run them alongside these reading-level knots. Comb reads the front door; the playbook drives it.

## Knots

Handle per [findings.md](findings.md). Default: file GitHub issues with links; auto-fix only small tested knots if the user asked.

## See also

- [mischief.md](mischief.md) — opposite temper: break expected flow on purpose
- [bug-hunter.md](bug-hunter.md) — code-first hunt across many dimensions
- [driving.md](driving.md) · [findings.md](findings.md)
