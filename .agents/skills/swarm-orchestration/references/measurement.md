# Measurement and experiments

## Measures

Record timestamps in UTC, name each window, and keep one completion definition throughout a comparison.

| Measure | Definition and limits |
|---|---|
| Completion percentage | Completed / current total × 100; report both counts and membership changes. |
| Completion rate | Accepted completion events / elapsed window hours; unique items and repeat closures separately. |
| Inter-completion gap | Time between consecutive events: median and largest; null when fewer than two exist. |
| Current silence | Time since the last completion, which exposes a stalled tail a median hides. |
| Task lead time | Accepted completion minus creation, including time before the swarm began. |
| Campaign cycle time | Accepted completion minus campaign claim or start; needs a recorded start — never substitute issue age. |
| Review wait | Review start minus ready-for-review, plus the age of still-waiting items. |
| Rework | Rejected handoffs or repair cycles with time spent where recorded; keep reopened work visible. |
| Work in progress | Items started but not accepted, by stage and age; finished patches awaiting merge still count. |

With no events, report zero rate and an unknown last completion. A window's duration is a lower bound on silence when the earlier event is unavailable, not a fabricated gap. API failure is unavailable data, never zero activity.

## Attribution and membership

Show all backlog activity and the subset the campaign's delivery records support, attributing by task, PR or revision link: a shared account, agent display name or close timestamp does not identify the delivering worker, and code completion differs from administrative closure of earlier work.

Single-issue attribution or cost labels inferred from observed links are provisional — not strict lower bounds or complete per-issue costs unless the measurement captures the whole work boundary. Record the primary task ID and stage in the assignment or handoff rather than inferring cost from worker names, filenames or historic references.

## Token and worker accounting

- With usage records, count unique response IDs globally and assign each record only to its proven thread. Report input, cached input, uncached input, output, reasoning output and total separately; cached input is a subset of input and reasoning output a subset of output, so add neither to total.
- Cumulative snapshots are reference values only: a window comparison needs a baseline at the window start, otherwise leave the difference unavailable.
- For worker time, pair starts and completions by turn, then merge overlapping intervals per worker before calculating concurrency. Report closed intervals as measured and keep unfinished tasks explicit.
- Cutoff-clipped durations are upper bounds — including completions after the cutoff — and missing and after-cutoff terminals are reported separately.
- Never infer that an available slot was busy, and count a replacement or nested worker only when its ownership and scope are proven.

## Membership and events

Current milestone membership is not historical membership: save the member list at each observation and report additions and removals beside percentages, since a query of today's milestone cannot reconstruct removed issues.

Current `closed_at` values lose earlier close/reopen cycles. For an auditable rate use task timeline events, reporting close events, unique issues closed, reopen events and net separately. A reopened issue is rework, not sustained progress, and pull requests are not issues.

## Run a small scheduling experiment

1. Capture the baseline window, task mix, active pool, queue sizes and review/integration delays.
2. Change one factor: implementation limit, reviewer allocation, assignment size, or an early validation step.
3. Compare equal elapsed windows, showing raw counts and duration, not only a percentage improvement.
4. Check quality and outstanding work: acceptance failures, reopenings, rework, queue age.
5. Keep the change only with evidence; otherwise target the observed bottleneck and measure again.

Never claim a pool-size effect from one closure or two short windows: difficulty, external contributors, batch closures, CI duration and in-flight work all explain differences. Larger samples improve confidence, but a visibly growing review queue is already reason to stop adding implementation work.

A simple status report suffices:

```text
As of <UTC>: <closed>/<total> (<percent>), scope change <added/removed>.
Window <start..end>: <events> closures, <unique> issues, <reopens> reopens,
<rate>/hour; median gap <value/unknown>; last closure <time/unknown>.
Campaign-attributed: <count> accepted outcomes with linked delivery evidence.
Queue: <implementation>, <review>, <integration>, <acceptance>; oldest <age>.
Bottleneck and scheduling change: <observation → action>.
```

## Optional GitHub adapter

`scripts/closure_metrics.py --help` gives a read-only snapshot from authenticated `gh` or a saved fixture: current milestone members and their close/reopen timeline events. It mutates nothing, infers no model identity, and cannot establish historical membership or review wait without stage timestamps. Its unit tests ship beside it and need no network or credentials — run `python3 -m unittest discover -s tests` from this skill's directory.

Keep collected repository names, titles, identities and event data outside the skill package: the reusable skill carries instructions and synthetic examples, not a private campaign's records.
