---
name: perf
description: "Measure performance before and after a change — never assume. Use when a change is claimed to be faster, a page or endpoint feels slow, a regression is suspected, or a performance budget or baseline needs establishing. Covers frontend rendering (layout, script, frames, FPS) over the Chrome DevTools Protocol, backend timing (perf_counter, timestamped logs, percentiles), deployment markers, and the compare-and-record loop that turns numbers into decisions."
---

# Perf: Measure, Never Assume

**A performance claim without a number is a guess.** Code that *looks* faster, a query that *should* be indexed, a bundle that *ought* to be smaller — none of it counts until an instrument says so. A change is an improvement only when a measurement taken under the same conditions moved in the right direction, and the raw numbers are recorded.

This skill is the discipline, not a single tool:

| Phase | Question | How |
|-------|----------|-----|
| 1. **Define** | What outcome does the user feel, and in what unit? | Name one metric with a target (ms, fps, %ile, rps) |
| 2. **Baseline** | What is it right now? | Measure the *unmodified* code, repeatably, and write the number down |
| 3. **Change** | One variable at a time | Make the change; do not bundle three optimizations into one run |
| 4. **Re-measure** | Did it move? | Same instrument, same conditions, same load |
| 5. **Compare** | Is the delta real or noise? | Repeat runs; report median and spread, not a single sample |
| 6. **Record** | What will the next person know? | One line in the perf ledger: metric, before, after, conditions |

Skip a phase and the numbers lie. The most common failure is not a bad instrument — it is a good instrument pointed at a question nobody asked, or a before/after pair taken under different conditions.

## Rule one: measure the outcome, not your mechanism

Verifying that your change *deployed*, your instrumentation *fired*, or your cache *is present* is not a measurement of the outcome. Instrumentation is an actor in a bigger system — a device routine, another service, a scheduler, an external provider can all produce (or mask) the effect you care about. Enumerate who else can move the metric, then measure the user-visible outcome itself, in its own units. If the request was "the page should stop jank ing while scrolling", the measurement is dropped frames during a scroll — not "the scroll handler is now debounced".

## Instrument map

Measure at the layer where the problem lives, and where the cost is incurred. Do not profile the frontend when the endpoint takes four seconds.

| Layer | Primary instrument | Reference |
|-------|-------------------|-----------|
| Browser rendering, frames, interactions | Chrome DevTools Protocol (`Performance.getMetrics`, `Tracing`, `Overlay`) | [references/frontend-cdp.md](references/frontend-cdp.md) |
| Application code, hot paths | `perf_counter()`, monotonic timers, spans | [references/backend-logs.md](references/backend-logs.md) |
| Requests, jobs, queues | percentiles from timestamped structured logs | [references/backend-logs.md](references/backend-logs.md) |
| Deploys, infra, restarts | timestamped deploy markers (`echo` with a UTC timestamp is a legitimate log) | [references/backend-logs.md](references/backend-logs.md) |
| Interpreting any of the above | the diagnosis playbook | [references/interpretation.md](references/interpretation.md) |
| Comparing runs, budgets, ledgers | the regression loop | [references/regression-loop.md](references/regression-loop.md) |

## Frontend: measure rendering for real

`scripts/perf-cdp.mjs` is a zero-dependency profiler (Node ≥ 22, any Chrome/Chromium/Edge). It drives a page over the DevTools Protocol and returns four things at once: **rendering cost** (layout, style recalculation, script), **frame health** (presented vs dropped frames, effective FPS), **page vitals** (LCP, CLS, long tasks, interaction latency), and **the hottest trace events by total time** — which is the part that points at the culprit.

```bash
# measure a page while driving it
node scripts/perf-cdp.mjs --url http://localhost:3000 --duration 5000 --out before.json

# drive it: click, scroll, type — then measure the interaction cost
node scripts/perf-cdp.mjs --url http://localhost:3000 --scenario steps.json --out after.json

# attach to a browser you already have open (Playwright/Puppeteer/agent-browser)
node scripts/perf-cdp.mjs --cdp http://127.0.0.1:9222 --url http://localhost:3000 --out after.json
```

Scenario files are a JSON array of steps — see [examples/scenario.example.json](examples/scenario.example.json):

```json
[{"type": "click", "selector": "#load-more"},
 {"type": "wait", "ms": 500},
 {"type": "scroll", "y": 2000},
 {"type": "eval", "expression": "window.router.push('/reports')"},
 {"type": "navigate", "url": "http://localhost:3000/dashboard"}]
```

Read the report's `frames.hottestByTotalTime` first — it names where the milliseconds actually went (e.g. `FireAnimationFrame`, `Layout`, `Paint`, `RunTask`), which is what turns a number into an idea. Protocol-level recipes, event names, and metric definitions are in [references/frontend-cdp.md](references/frontend-cdp.md).

**Prove the instrument discriminates.** Before trusting a before/after pair, run a deliberate control: make something obviously worse (thrash layout in a `requestAnimationFrame` loop, add a 60 ms busy-wait) and confirm the numbers move — dropped frames up, `LayoutDuration` up. An instrument that cannot see a known-bad condition cannot be trusted to have seen your improvement. A measured control looks like this:

| Condition | layout | script | effective FPS | dropped frames | long tasks |
|-----------|--------|--------|---------------|----------------|------------|
| idle page | 115 ms | 19 ms | 120.2 | 0 | 0 |
| forced layout thrash + busy-wait | 174 ms | 6008 ms | 31.8 | 261 | 100 (worst 232 ms) |

## Backend and infra: always-on beats occasional

Cheap, always-on, timestamped measurements beat expensive profiling you run once. A `perf_counter()` around a hot path and a structured log line per request cost almost nothing and accumulate the history you need when something regresses a week later. Infra counts too: a deploy script's `echo "[$(date -u +%FT%TZ)] deploy start"` is a performance instrument — it is what lets you line a metric change up against a release. Patterns for timers, log-derived percentiles, and deploy markers: [references/backend-logs.md](references/backend-logs.md).

## Reporting

Report **percentiles, not averages**; report **conditions, not just numbers**; report **the spread** when the delta is small. A single sample is an anecdote.

```
p95 GET /reports   1840 ms -> 210 ms   (n=500 each, same dataset, same host, median of 3 runs)
LCP (cold, 4x CPU throttle)  3.4 s -> 1.2 s
dropped frames during scroll  41 -> 2
```

Never report "faster" without the unit, the before, the after, and the conditions. If the delta is inside the noise band, say so — an honest "no measurable change" is a result.

## Pitfalls

- **Averaging away the tail.** A mean latency of 200 ms can hide a p99 of 9 s. Percentiles or nothing.
- **Before/after under different conditions** — different machine, cache state, dataset, build mode (dev vs production), or network. The comparison is then meaningless, however precise the numbers.
- **Measuring a development build.** Unminified code, HMR sockets, source maps and dev overlays dominate production numbers. Measure the artifact you ship.
- **Micro-optimising what a profiler never ranked.** Read the hottest-events list before rewriting anything.
- **Single-shot runs.** Cold JIT, cold caches and a noisy neighbour move numbers by tens of percent. Repeat, take the median, and note the spread.
- **Measuring a throttled page.** Backgrounded or occluded tabs have timers and rAF throttled — FPS and long-task numbers from a hidden page are fiction. Keep the window visible (or headless with backgrounding disabled) while measuring frames.
- **Trusting the mechanism instead of the outcome** — see "Rule one". If your fix is confirmed present but the user-visible metric did not move, the fix did not work.
- **Chrome on Linux hanging on every navigation.** With no running secret service (gnome-keyring/kwallet) Chrome's default password store blocks startup, and navigations never commit — CDP commands then time out and it looks like a broken client. Launch with `--password-store=basic`. Diagnosed by bisecting launch flags against a known-good browser; if `data:` URLs navigate and `http://` ones do not, this is the cause.
- **A timing source that can go backwards.** Use a monotonic clock for durations (`perf_counter`, `performance.now`), wall-clock only for correlating across machines.

## Standing practice

What gets measured gets managed: re-measure on a schedule, not only when something breaks. Put a budget on the metrics that matter, keep the ledger, and let a regression trip an alert or a CI gate. See [references/regression-loop.md](references/regression-loop.md) for budgets, thresholds relative to run-to-run variance, and the ledger format.
