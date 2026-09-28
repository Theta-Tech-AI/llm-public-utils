# Interpretation: turning numbers into the next change

Measuring is half the discipline; the other half is reading the result well enough to decide what to change next — and then measuring *that* change rather than assuming it worked. This file is the diagnosis playbook: symptom → instrument → likely causes → the measurement that discriminates between them.

## Contents

- [The loop](#the-loop)
- [Symptom to cause](#symptom-to-cause)
- [A worked example](#a-worked-example)
- [Reading a trace's hottest-events list](#reading-a-traces-hottest-events-list)
- [Prove the instrument discriminates](#prove-the-instrument-discriminates)
- [When the numbers do not move](#when-the-numbers-do-not-move)
- [Turning a finding into a fix and an issue](#turning-a-finding-into-a-fix-and-an-issue)

## The loop

```
measure  ->  rank the costs  ->  form one falsifiable hypothesis  ->  measure the hypothesis
  ^                                                                              |
  +--------------------------- change one thing, re-measure ----------------------+
```

A profiler is not a diagnosis. Its output is an *ordering*: these are the expensive things, in this order. Pick the top of that list, state a hypothesis you could disprove ("the scroll handler forces synchronous layout because it reads `offsetHeight` after each write"), change one variable, and measure again. If the number did not move, the hypothesis was wrong — that is a result too, and it is cheaper than shipping a fix that never worked.

## Symptom to cause

| Symptom | Instrument | Likely causes | The discriminating measurement |
|---------|-----------|---------------|-------------------------------|
| Scroll stutters | trace `DroppedFrame`, effective FPS | Long main-thread tasks, forced synchronous layout, non-composited animations | Trace during a scripted scroll; compare `DroppedFrame` count before/after |
| High `LayoutDuration` relative to `TaskDuration` | `Performance.getMetrics` + trace | Layout thrash (read-write interleaving), animating `width`/`top`, enormous DOM | Count `Layout` events; test with the read moved out of the write loop |
| High `RecalcStyleDuration` | `Performance.getMetrics` | Broad selectors, class churn, style writes in a loop | Recalc count vs count of style mutations |
| High `ScriptDuration` | trace hottest events (`FireAnimationFrame`, `FunctionCall`) | Algorithmic cost, re-render churn, per-frame work that belongs on an event | Attribute `dur` by function/event name; the top entry is the target |
| Content jumps after load | CLS via `layout-shift` observer | Images/ads/banners without reserved space, late font swap | Per-shift `value` + the elements in `sources` |
| Slow first paint | LCP observer + network waterfall | Render-blocking CSS/JS, slow API for above-the-fold content, font blocking | LCP timestamp vs the network timings for the elements it needs |
| Endpoint slow, CPU low | logs (`db_ms`, outbound host, `cache`) | N+1 queries, chatty service calls, missing index, cold cache, lock contention | Split the request duration by span from the logs |
| Latency fine but errors/timeouts | logs by status + backlog | Pool exhaustion, queue backlog, retry storms | Concurrency vs pool size; queue depth over time |
| Regression after a deploy | deploy markers + metric timeline | The diff; also traffic shift, cold cache, new instance type | Same window length, same route, same filters, before vs after the marker |
| "It feels slower" with no metric | pick one user-visible outcome and instrument it | Unmeasured work added somewhere | Establish the baseline now; the next change can be measured against it |

## A worked example

A page with an animation loop, a 4000-row list, a button that turns on jank (300 forced layouts per frame plus a 60 ms busy-wait), and a banner injected 1.2 s after load to force a layout shift. Measured with `scripts/perf-cdp.mjs`, 6 s per run, headless, same host:

| Condition | Layout | Style recalc | Script | Effective FPS | Dropped | Long tasks (worst) | CLS |
|-----------|--------|--------------|--------|---------------|---------|--------------------|-----|
| idle page | 115 ms | 12 ms | 19 ms | 120.2 | 0 | 0 | 0.272 |
| jank button pressed | 174 ms | 3 ms | 6008 ms | 31.8 | 261 | 100 (232 ms) | 0.312 |

What the numbers say, in order:

1. **Script dominates** (6008 ms of a 6275 ms task total). This is not a layout or paint problem; the fix is in the loop, not the CSS.
2. The hottest events name the mechanism: `FireAnimationFrame` 5896 ms inside `ProxyMain::BeginMainFrame` 5975 ms — the rAF callback holds the main thread, so no frame can be presented.
3. **Script time is the cause, dropped frames the consequence**: 31.8 fps and 261 dropped frames follow from (2).
4. `LayoutDuration` rose only 59 ms while `LayoutCount` went 380 → 341 — the forced reflows are real but small next to the busy-wait. Had we "fixed" the layout thrash first, the page would still drop 261 frames. **The ranking is what saved the effort.**
5. CLS 0.272 is the late-injected banner and is unrelated to the jank — a second, independent finding with its own fix (reserve the space).

## Reading a trace's hottest-events list

Aggregate `dur` by event `name` and sort descending. How to read the top entries:

- **`ProxyMain::BeginMainFrame`** — the umbrella: total time the main thread took per frame. If this is near the whole run, the main thread is the bottleneck (as opposed to compositor/raster/GPU).
- **`FireAnimationFrame` / `FunctionCall` / `UpdateLayoutTree`** — JS work per frame. Sustained values over a few milliseconds per frame guarantee dropped frames at 60 Hz (16.7 ms budget).
- **`Layout` / `LocalFrameView::layout` / `PrePaint` / `Paint` / `RunCompositingInputsLifecyclePhase`** — the rendering pipeline. Large `Paint` totals point at paint area and invalidation; large `Layout` totals at reflow.
- **`Graphics.Pipeline` / raster events** — compositor side; if these dominate *and* main-thread totals are small, look at canvas/image costs and layer count rather than JS.
- **`TimerFire`** — timers and polling; a poll loop that re-renders is a common cause of background jank.

Judge per-frame cost, not just the total: milliseconds of main-thread work ÷ frames presented. A 300 ms total across 700 frames is healthy; 5975 ms across 191 frames is not.

## Prove the instrument discriminates

Before trusting a before/after pair, verify the instrument can see a difference at all. Make the condition deliberately worse — thrash layout in a rAF loop, add a busy-wait, remove an index — and confirm the numbers move in the expected direction and magnitude.

This catches the two failure modes that produce false confidence:

- **A blind instrument** — measuring the wrong target, a throttled page, or a metric that is cumulative and never diffed. A control run will show no difference between good and bad.
- **A noisy instrument** — run-to-run variance as large as the effect. A control with a known 10× effect that measures as 1.2× tells you the noise floor before you interpret a 1.2× "improvement" as real.

The control numbers belong in the report next to the result. "The instrument distinguishes a known-bad page by 3.8× in FPS and 261 dropped frames" is what makes the before/after pair trustworthy.

## When the numbers do not move

Possibilities, in the order worth checking:

1. **The effect is smaller than the noise.** Repeat and take the median; report the spread before claiming a win.
2. **The change is not in the measured path.** Confirm the new code actually ran (a log, a counter — but remember that confirming the mechanism is not the measurement).
3. **You measured the wrong metric.** A fix to first paint will not move scroll FPS; check you instrumented the outcome the user described.
4. **Something else compensated.** A faster query plus a new cache-miss penalty can net to zero; split the duration by span.
5. **The conditions changed.** Build mode, dataset, cache warmth, instance size, concurrent load.
6. **The fix targets a symptom ranked below the real cost.** Go back to the hottest-events list; the top entry is probably unchanged.

Any of these is a legitimate finding. "The change did not measurably improve the metric under these conditions" prevents a false claim from entering the record — which is worth more than an unverified win.

## Turning a finding into a fix and an issue

A measured finding is actionable and competable: it names the metric, the before value, the target, and the evidence. File it where work is tracked (an issue, not a chat message) with:

- the metric and unit, the current value, and how it was measured (tool, command, scenario, `n`);
- the suspected mechanism and the trace/log evidence that ranked it;
- the proposed change and the target value;
- how it will be re-measured to confirm — the same command, the same conditions.

State the *how*: a finding that cannot be re-measured by the next person becomes folklore.
