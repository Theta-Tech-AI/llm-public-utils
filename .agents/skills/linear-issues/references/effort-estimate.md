---
name: effort-estimate
description: Measure each issue's effort — estimate before, actual after, and the time taken across pauses.
---

# Effort Estimate and Time

Every issue carries two numbers and a clock: an estimate before the work, an actual after it, and the time the work actually took. Recorded at the moment it happens, in comments — never reconstructed at close.

## Asking: a question with fixed options, never free text

Both ends of the measurement are put to the user as a **multiple choice selection**, never as free-form input — the rule [orient.md](orient.md) already sets for projects and issues. Propose the bands yourself from the issue you have just read, mark the one you judge right as the recommended option, and let the tool's own "other" row carry the rare exception. Never infer an answer from silence or from your own reading: an unanswered question is `unestimated`, not consent.

One question at the moment it is needed — the before question when work begins, the closing question before the status moves. Not batched, not merged into a status update.

**Before the work** ([start-linear-issue.md](start-linear-issue.md)):

> How much effort will this take?
> - ½ day or less — small, well-understood change *(recommended)*
> - About 1 day
> - 2–3 days
> - More than 3 days — needs splitting before it starts

That ladder is the default; shift it to suit the issue (an hour-scale fix wants hours, a multi-week feature wants days or weeks) and record which scale was used. The option chosen is the baseline, recorded with who set it:

- **Estimate:** the chosen band, the one thing driving it, and the scale used.
- **Started at:** timestamp in the user's local zone.

An estimate written after the work has begun is not an estimate. If the issue was picked up without one, mark it `unestimated` and say so; never back-fill.

**On resume** ([continue-linear-issue.md](continue-linear-issue.md)) — ask only when what you found changes the picture:

> The estimate was *about 1 day*. Does it still hold?
> - Holds — continue on it *(recommended)*
> - Raise it one band
> - Lower it one band
> - Something changed — I will explain

**After the work** ([close-linear-issue.md](close-linear-issue.md)) — the actual, confirmed before the status flips:

> Work took about *6 h* against an estimate of *about 1 day*. Record it that way?
> - Yes, as measured *(recommended)*
> - Under-ran — propose a shorter actual
> - Over-ran — propose a longer actual
> - Do not record an actual

## The clock

The clock runs only while someone is working. Stopping ([stop-linear-issue.md](stop-linear-issue.md)) closes a segment: **Worked:** `started` → `stopped`, elapsed, plus a partial actual. Continuing opens the next one. Total effort is the sum of segments — not the wall-clock span from first start, which would count the night in between.

The closing comment carries, alongside the evidence:

- **Actual:** hours worked (sum of segments) and the elapsed span.
- **Estimate vs actual:** the before band, the delta and ratio, and one sentence on why it moved — scope found, blocker, review rounds.

## Why this is tracked

Two numbers per issue turn sizing from a guess into a series. After a handful of issues the actual-to-estimated ratio for a class of work is knowable, and the story-point size can be anchored to that ratio instead of re-guessed each time.

## Rules

- Ask at both ends, as a multiple choice selection — before the work and after it. An unasked estimate is a missed measurement, not a saved minute.
- The user's choice wins over your reading, every time; record who set the figure.
- Hours are the unit of effort; the Linear `estimate` (story points) field stays the sizing field and is not a substitute.
- Never silently round the actual down, and never report the elapsed span as the effort.
- Report times in the user's local zone; raw UTC belongs in the record, not in the sentence spoken to them.
- A pause is not a close: partial actuals live in stop comments, the final one in the close.
