# Measurement

How to state delivery: completed against total, accepted rate over a stated window, queue age, WIP, and attribution limits.

## Measure outcomes and the queue

Record timestamps in UTC and name each window. Use the same completion definition throughout a comparison.

| Measure | Definition and limits |
|---|---|
| Completion percentage | Currently completed items / current total items × 100. Report both counts and membership changes. |
| Completion rate | Accepted completion events / elapsed window hours. Report unique items and repeated closures separately. |
| Inter-completion gap | Time between consecutive events. Report median and largest gap; use null when fewer than two events exist. |
| Current silence | Time since the last completion as of the observation time. This exposes a stalled tail that an internal median hides. |
| Task lead time | Accepted completion minus task creation. This includes time before the swarm began. |
| Campaign cycle time | Accepted completion minus campaign claim/start. This needs a recorded start; do not substitute issue age. |
| Review wait | Review start minus ready-for-review time. Also show the age of still-waiting items. |
| Rework | Rejected handoffs or repair cycles, with time spent when recorded. Keep reopened work visible. |
| Work in progress | Items started but not accepted, grouped by stage and age. Finished patches awaiting merge still count. |

If no events exist, report zero rate and an unknown last-completion timestamp. A window's duration is a lower bound on silence when the earlier event is unavailable, not a fabricated inter-completion gap. API failure is unavailable data, never zero activity.

## Attribution and membership

Show all backlog activity and the subset supported by this campaign's delivery records. Use task/PR/revision links for attribution. A shared account, agent display name, or close timestamp does not identify which worker delivered the work. Distinguish code completion from administrative closure of work done earlier.

Single-issue attribution or cost labels inferred from observed links are provisional evidence. They are not strict lower bounds or complete per-issue costs unless the measurement captures the full work boundary.

For usage attribution, record the primary task ID and current stage in the assignment or handoff. Do not infer per-task cost from worker names, filenames, or historic issue references.

## Token and worker accounting

When usage records are available, count unique response IDs globally and assign a record only to its proven owning thread. Report input, cached input, uncached input, output, reasoning output, and total separately. Cached input is a subset of input, and reasoning output is a subset of output; do not add either subset to total. Treat cumulative token snapshots as reference values. A window comparison needs a snapshot baseline at the window start; without one, leave snapshot differences unavailable.

For worker time, pair task starts and completions by turn, then merge overlapping intervals per worker before calculating concurrency. Report closed intervals as measured. Keep unfinished tasks explicit and report their cutoff-clipped duration as an upper bound. Completions after the cutoff are also clipped for that upper bound. Report missing terminals and after-cutoff terminals separately. Never infer that an available slot was busy, and do not count a replacement or nested worker unless its ownership and scope are proven.

Current milestone membership is not historical membership. Save the member list at each observation. Report additions and removals alongside percentages. Historical membership analysis needs membership events or a fixed initial cohort; a query of today's milestone cannot reconstruct removed issues.

Current `closed_at` values give a quick snapshot but lose earlier close/reopen cycles. For an auditable rate, use task timeline events. Report close events, unique issues closed, reopen events, and net events separately. A completed issue that reopens is rework, not sustained progress. Do not count pull requests as issues accidentally.

## Run a small scheduling experiment

1. Capture the baseline window, task mix, active pool, queue sizes, and review/integration delays.
2. Change one factor: implementation limit, reviewer allocation, assignment size, or an early validation step.
3. Compare equal elapsed windows. Show raw event counts and duration, not just a percentage improvement.
4. Check quality and outstanding work: acceptance failures, reopenings, rework, and queue age.
5. Keep the change only with evidence; otherwise target the observed bottleneck and measure again.

Do not claim that a larger pool caused a rate change from one closure or two short windows. Difficulty, external contributors, batch closures, CI duration, and work already in progress can explain the difference. Larger samples improve confidence, but a visibly growing review queue is already enough reason to stop adding implementation work.

A simple status report is sufficient:

```text
As of <UTC>: <closed>/<total> (<percent>), scope change <added/removed>.
Window <start..end>: <events> closures, <unique> issues, <reopens> reopens,
<rate>/hour; median gap <value/unknown>; last closure <time/unknown>.
Campaign-attributed: <count> accepted outcomes with linked delivery evidence.
Queue: <implementation>, <review>, <integration>, <acceptance>; oldest <age>.
Bottleneck and scheduling change: <observation → action>.
```

## Report the measures

Report completed/total and percentage from a live task query, completions per hour over a stated UTC window, time between completions, and time since the last completion. Also track review queue age, rework, blocked time, and each stage's WIP. Give these measures at campaign start, after each accepted closure, and at regular checkpoints; separate campaign-attributed outcomes from all repository activity.

## Causal limits on a scheduling change

Compare equal windows before and after a scheduling change. Small samples, different task difficulty, batch closure, and other contributors limit causal claims. If more workers do not improve delivery, identify the slowest stage and change one scheduling factor. Do not weaken acceptance or split issues merely to inflate the count.

---

Related: [the assignment record](assignment-and-handoff.md) · [planning and capacity](planning-and-capacity.md) · [GitHub closure metrics](github-closure-metrics.md)
