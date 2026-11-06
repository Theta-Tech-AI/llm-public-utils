---
name: effort-estimate
description: Measure each issue's effort — estimate before, actual after, and the time taken across pauses.
---

# Effort Estimate and Time

Every issue carries two numbers and a clock: an estimate before the work, an actual after it, and the time the work actually took. Recorded at the moment it happens, in comments — never reconstructed from memory at close.

## Before work starts — the estimate

Before writing code, in the **Started** comment ([start-linear-issue.md](start-linear-issue.md)):
- **Estimate:** hours, as a point or an honest range (`~3 h`, `2–5 h`), plus the one thing driving the uncertainty (unknown API, flaky suite, a review round expected). Hours are the unit; the story-point `estimate` field stays the sizing field and is not a substitute.
- **Started at:** timestamp in the user's local zone.
- **Ask:** put the estimate to the user — "I read this as ~3 h; correct me if that's off." One line in the same reply, not a blocking question. If they revise it, the revised figure is the baseline and the comment records who set it.

An estimate written after the work has begun is not an estimate. If the issue was picked up without one, mark it `unestimated` and say so; never back-fill.

## While the clock is paused

The clock runs only while someone is working. Stopping ([stop-linear-issue.md](stop-linear-issue.md)) closes a segment: **Worked:** `started` → `stopped`, elapsed, plus a partial actual. Continuing ([continue-linear-issue.md](continue-linear-issue.md)) opens the next one. Total effort is the sum of segments — not the wall-clock span from first start, which would count the night in between.

## After the work — the actual

In the closing comment ([close-linear-issue.md](close-linear-issue.md)):
- **Actual:** hours worked (sum of segments) and the elapsed span.
- **Estimate vs actual:** the before figure, the delta and ratio, and one sentence on why it moved — scope found, blocker, review rounds.
- **Ask:** whether the recorded actual matches the user's sense of it; correct it before flipping the status if not.

## Why this is tracked

Two numbers per issue turn sizing from a guess into a series. After a handful of issues the actual-to-estimated ratio for a class of work is knowable, and the story-point size can be anchored to that ratio instead of re-guessed each time.

## Rules

- Ask at both ends — before the work and after it. An unasked estimate is a missed measurement, not a saved minute.
- Never silently round the actual down, and never report the elapsed span as the effort.
- Report times in the user's local zone; raw UTC belongs in the record, not in the sentence spoken to them.
- A pause is not a close: partial actuals live in stop comments, the final one in the close.
