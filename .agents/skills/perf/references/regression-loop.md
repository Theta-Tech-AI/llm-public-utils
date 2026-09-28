# The regression loop: budgets, comparison, ledger

Measuring once answers "how fast is it now". The loop below answers the question that actually protects users: **did it get worse, and will we know when it does?**

## Contents

- [Budgets](#budgets)
- [Comparing two runs honestly](#comparing-two-runs-honestly)
- [Thresholds](#thresholds)
- [The perf ledger](#the-perf-ledger)
- [Standing measurement](#standing-measurement)
- [CI gates](#ci-gates)
- [Pitfalls](#pitfalls)

## Budgets

A budget converts a measurement into a decision: a number with a consequence attached. Pick the few metrics a user can feel, and write the number down where the work happens.

| Area | Metric | Example budget |
|------|--------|----------------|
| Frontend | LCP (mobile, throttled) | ≤ 2.5 s |
| Frontend | CLS | ≤ 0.1 |
| Frontend | Long tasks during an interaction | none > 200 ms |
| Frontend | Dropped frames during a scripted scroll | ≤ 5 % of presented |
| Frontend | Initial JS transferred | ≤ 300 kB gzipped |
| Backend | p95 latency for a route | ≤ 500 ms |
| Backend | p99 latency | ≤ 2 s |
| Backend | Error rate | ≤ 0.1 % |
| Backend | Job backlog age | ≤ 60 s |
| Infra | Deploy-to-ready duration | ≤ 5 min |

Budgets without an owner and a check are decoration. The two enforcement points that work in practice: a CI gate for what can be measured deterministically, and a scheduled re-measurement for what cannot (production latency, real-device rendering).

## Comparing two runs honestly

The comparison is only as good as the conditions. Hold constant, or state the difference:

- **Same machine and load** — including background work; a busy host inflates everything.
- **Same artifact** — production build, minified, same flags. Never compare a dev server to a previous production run.
- **Same scenario** — same steps, same dataset, same viewport, same time budget.
- **Same warmth** — cold JIT, cold caches and cold connection pools are a different workload. Measure both if both matter, but compare like with like.
- **Same measurement path** — the same instrument, the same metric definition.

Repeat and take the median. Run-to-run variance on a shared CI host easily reaches 10–20 % for a single sample; three runs and a median is the cheapest defence against chasing noise. Record the spread (min–max, or the median absolute deviation) beside the number whenever the delta is small:

```
p95 GET /reports   1840 ms -> 210 ms   (n=500, median of 3 runs, spread ±15 ms)
scroll dropped      41 → 2             (median of 5 runs, spread 0–4)
```

## Thresholds

A regression is a **change larger than the noise band**. Establish the band from a control: repeat the *unmodified* measurement N times and take the spread. Then:

| Condition | Action |
|-----------|--------|
| ∆ within the measured spread | Noise. Report "no measurable change" — do not claim a win |
| ∆ beyond the spread, same direction across repeats | Real. Record it; if it is a regression, file it |
| ∆ in the wrong direction beyond 10–20 % | Block the merge / alert |
| ∆ in the right direction but under the spread | Re-measure with more repeats before claiming it |

Two softenings worth building in: **a budget floor** (a 3 ms → 5 ms change is 66 % but meaningless; gate on both absolute and relative movement) and **a minimum effect size** (require the change to exceed both the noise band and a meaningful absolute delta).

## The perf ledger

Keep a one-line-per-change record near the code or in the repo's docs. It is the only artifact that makes trends visible without re-running history.

```
| date       | change                      | metric                | before   | after    | conditions            |
|------------|-----------------------------|-----------------------|----------|----------|-----------------------|
| 2026-09-14 | virtualised report list     | scroll dropped frames | 41       | 2        | headless, 4x CPU      |
| 2026-09-21 | index on reports.tenant_id  | p95 GET /reports      | 1840 ms  | 210 ms   | n=500, prod replica   |
| 2026-09-28 | removed per-frame re-render | effective FPS (scroll)| 31.8     | 58.9     | median of 3 runs      |
```

Rules that keep the ledger useful: one row per change (not per session), the unit always present, the conditions always present, and **the row written on the same day** — a ledger reconstructed from memory is fiction. When a number was measured with an instrument that later changed, note it; the trend line silently breaks otherwise.

## Standing measurement

What gets measured gets managed, and management is periodic:

- **Per change** — the metric the change targets, before and after, in the ledger.
- **Daily** — production latency percentiles and error rates from logs, plus deploy markers; alert on budget breach, not on a single slow sample.
- **Weekly** — re-run the frontend script against the main journeys to catch slow creep that no single PR caused.
- **Per release** — a fixed benchmark suite, so "release N+1 is 8 % slower" is known before users report it.

Slow creep is the failure mode periodic measurement exists for: ten changes of +2 % each never trip a per-PR gate, and a quarter later the page is 20 % heavier.

## CI gates

Gate on metrics that are deterministic on a CI runner: bundle size, type-check and build times, unit-level benchmarks, page weight, request counts. Percentile latency on a shared runner is not deterministic; use a trend check against the last N runs, or measure it in a fixed environment instead. A gate that flaps is disabled within a month, and a disabled gate protects nothing.

Prefer a gate that fails loudly with the number and the delta, and a documented way to re-baseline deliberately:

```
FAIL perf budget: LCP 3.4s > 2.5s budget (+0.9s vs baseline 2.5s, run 3 of 3, median of 5)
```

Re-baselining is a decision with a name and a reviewer — never a silent update of a stored baseline to make CI green.

## Pitfalls

- **Gating on a single sample.** The most common cause of a disabled gate.
- **Silently re-baselining.** It converts a regression into a permanent baseline. Re-baseline explicitly, in a committed change, with the reason in the message.
- **Comparing across environments.** CI numbers and production numbers belong in separate tables.
- **Recording only wins.** The ledger is a record of measurements, not a highlight reel; the regressions you chose not to fix are the most valuable rows.
- **Measuring at a cadence nobody reads.** A weekly report with no owner decays into an unread file — attach it to a person and a decision.
- **Optimising to the metric instead of the outcome.** A synthetic benchmark can be made faster while the application gets slower (caching the benchmark's exact input, special-casing the test route). Keep one measurement anchored in a realistic journey.
