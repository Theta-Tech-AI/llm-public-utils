# 6. Measure

Read when you report delivery: at campaign start, after each accepted closure, and at each checkpoint.

## Measures

Record timestamps in UTC. Name each window. Use one completion definition throughout a comparison.

| Measure | Definition and limits |
|---|---|
| Completion percentage | Completed items / current total items × 100. Report both counts and membership changes. |
| Completion rate | Accepted completion events / elapsed window hours. Report unique items and repeated closures apart. Report opened and closed per hour apart, so a flat open count is diagnosable. |
| Inter-completion gap | Time between consecutive events. Report the median and the largest gap. Use null when fewer than two events exist. |
| Current silence | Time since the last completion, at observation time. It exposes a stalled tail that the median hides. |
| Task lead time | Accepted completion minus task creation. It includes time before the swarm began. |
| Campaign cycle time | Accepted completion minus campaign claim. It needs a recorded start. Do not substitute issue age. |
| Review wait | Review start minus ready-for-review time. Also show the age of items still waiting. |
| Rework | Rejected handoffs and repair cycles, with time when recorded. Keep reopened work visible. |
| Work in progress | Items started but not accepted, by stage and age. A finished patch that waits for merge still counts. |

- With no events, report rate zero and last completion unknown. A window's length is a lower bound on silence, not an inter-completion gap. An API failure is unavailable data, never zero activity.
- Round completion percentages down. Report 100% only when the count is complete.

## Attribution and membership

- Show all backlog activity, and the subset that this campaign's delivery records support. Use task, PR and revision links. A shared account, a display name or a close timestamp does not identify the worker. Separate code completion from administrative closure of earlier work.
- Per-issue attribution or cost inferred from links is provisional. Record the primary task ID and stage in the assignment. Do not infer cost from worker names, filenames or old issue references.
- Current milestone membership is not historical membership. Save the member list at each observation, and report additions and removals next to percentages.
- Current `closed_at` values lose earlier close and reopen cycles. For an auditable rate, use timeline events. Report close events, unique issues closed, reopen events and net events apart. A reopened issue is rework. Do not count pull requests as issues.

## Tokens and worker time

- Count unique response IDs globally. Assign a record only to the thread that provably owns it. Report input, cached input, uncached input, output, reasoning output and total apart. Cached input is a subset of input. Reasoning output is a subset of output. Do not add subsets to the total. Treat cumulative snapshots as reference values. A window comparison needs a snapshot at the window start.
- For worker time, pair starts and completions by turn. Merge overlapping intervals per worker before you compute concurrency. Report closed intervals as measured. Report unfinished tasks as cutoff-clipped upper bounds. Report missing terminals and after-cutoff terminals apart. Never infer that an available slot was busy. Count a replacement or nested worker only when its ownership and scope are proven.

## Run a scheduling experiment

1. Capture the baseline window, task mix, pool, queue sizes and delays.
2. Change one factor: implementation limit, reviewer allocation, assignment size, or an early validation step.
3. Compare equal windows. Show raw counts and duration, not only a percentage.
4. Check quality: acceptance failures, reopenings, rework, queue age.
5. Keep the change only with evidence. Otherwise target the observed bottleneck and measure again.

One closure or two short windows cannot show that a larger pool caused a change. Task difficulty, outside contributors, batch closures, CI duration and work in progress also move the rate. A visibly growing review queue is enough reason to stop adding implementation work. Do not weaken acceptance or split issues to raise the count.

## Status report

Report rates per hour from completion timestamps. Group the open set by state (worked, blocked and by whom, epic, waiting). Call out anything unowned. Show last reported against now, as a table.

```text
As of <UTC>: <closed>/<total> (<percent>), scope change <added/removed>.
Window <start..end>: <events> closures, <unique> issues, <reopens> reopens,
<rate>/hour; median gap <value/unknown>; last closure <time/unknown>.
Campaign-attributed: <count> accepted outcomes with linked delivery evidence.
Queue: <implementation>, <review>, <integration>, <acceptance>; oldest <age>.
Bottleneck and scheduling change: <observation → action>.
```

## Draw the open set

When the operator asks for a chart of open work, send one image that answers "where is every open item, and what moves
it next": a pie on the left, and the same slices as horizontal bars on the right. Draw it with
`scripts/progress_chart.py INPUT.json OUTPUT.png` (the input format is in its header).

- **Chart the focus set the operator names, plus every open item with no milestone** (one "no milestone" slice, so
  untriaged work stays visible; name its count in the title even when it is 0). Leave other milestones out unless the
  operator asks for them; then each is one slice. Every open item in the chart sits in exactly one slice, from the item
  records, never from memory. With one focus group, the group goes in the title and the bars name only the stage.
- **Stages follow the order of operations for one item**, and the bars run in that order, top to bottom: waiting on the
  operator or an outside party, scheduled event, ready with no owner, finding the cause, coding, waits a deploy for its
  next step, final checks, in a batch (lands at push), proof running, after the release window. Never draw one big
  "being built" slice: split it into finding the cause, coding, waits a deploy and final checks, so the chart shows
  where work piles up.
- **Pie and bars share one fixed colour per stage**, the same in every chart, so two charts compare at a glance.
- **The bars carry the names; the pie carries the counts.** Only a large pie slice also shows its group name; no legend.
  An outsized non-focus bar is clipped with its true count, so it does not flatten the focus bars.
- **The title carries the totals and the change**: total open, each focus count, and each focus count at the last
  chart with its time ("release 1.1 = 20, was 24 at 5:37 PM").
- **Counts from a live query** at draw time. Give `total`; the script refuses slices that do not add up to it.
- **Follow it with a short table** of the focus slices that names what moves each one next.

## GitHub adapter (optional)

`scripts/closure_metrics.py --help` prints a read-only snapshot from an authenticated `gh` or a saved fixture. It reads current milestone members and their close and reopen timeline events. It does not change issues, infer model identity, rebuild historical membership, or measure review wait without stage timestamps. Its tests need no network: from the skill directory, run `python3 -m unittest discover -s tests`. Keep collected names, titles, identities and event data outside the skill package.

## Failure patterns

- **The open count stayed flat while workers finished.** — Delivered items waited for acceptance, and test runs filed duplicates. Rule: report opened and closed apart; run the sweep in [5](integrate-and-deliver.md). Evidence: closures per hour rose while the count did not fall.
- **A rate change was credited to a larger pool.** — One short window, a different task mix. Rule: equal windows, one factor. Evidence: raw counts per window.

Next: [7. Speed](speed.md)
