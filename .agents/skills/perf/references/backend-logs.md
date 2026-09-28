# Backend, jobs and infra: timestamped measurement that is always on

Frontend profiling is a deliberate act. Backend measurement should be a habit: cheap, always-on, timestamped lines that accumulate the history you need when something regresses a week later. **A `perf_counter()` around a hot path and one structured log line per request cost almost nothing and answer questions you have not thought to ask yet.**

## Contents

- [Time the right clock](#time-the-right-clock)
- [Timing code](#timing-code)
- [Timestamped structured logs](#timestamped-structured-logs)
- [Percentiles from logs](#percentiles-from-logs)
- [Deploy and infra markers](#deploy-and-infra-markers)
- [Correlating a change with a metric](#correlating-a-change-with-a-metric)
- [What to instrument, and what not to](#what-to-instrument-and-what-not-to)
- [Pitfalls](#pitfalls)

## Time the right clock

| Clock | Use for | Never use for |
|-------|---------|---------------|
| `perf_counter()` (Python), `performance.now()` (JS/Node), `clock_gettime(CLOCK_MONOTONIC)` | Durations — monotonic, immune to NTP steps and DST | Correlating across machines |
| `time.time()` / `Date.now()` (wall clock) | Log timestamps, correlating events across services | Measuring elapsed time |

A wall-clock duration can be negative or inflated by an NTP correction mid-measurement. Log wall-clock, measure monotonic.

## Timing code

Python — a context manager that logs and never lies about which branch ran:

```python
import time, logging
from contextlib import contextmanager

log = logging.getLogger(__name__)

@contextmanager
def timed(event: str, **fields):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        ms = (time.perf_counter() - t0) * 1000
        log.info("%s %.1fms %s", event, ms, " ".join(f"{k}={v}" for k, v in fields.items()),
                 extra={"event": event, "duration_ms": round(ms, 1), **fields})

with timed("report.render", report_id=r.id, rows=len(rows)):
    html = render(r)
```

The `finally` matters: a slow path that raised is exactly the path you want in the log.

Node:

```js
const t0 = performance.now();
try { await handler(req); }
finally { logger.info({ event: 'handler', route: req.route, duration_ms: performance.now() - t0 }); }
```

Instrument the boundaries you can name — request handler, DB query, outbound call, job execution, cache lookup. Naming the boundary is what makes the numbers comparable between runs; "elapsed" alone is not a measurement anyone can act on.

## Timestamped structured logs

A log line is an instrument only if it can be aggregated. What makes one usable:

```json
{"ts":"2026-09-28T12:41:07.238Z","level":"info","event":"http.request","route":"GET /reports",
 "status":200,"duration_ms":184.2,"db_ms":121.7,"db_queries":7,"cache":"miss","bytes":48120}
```

- **UTC timestamp with milliseconds**, ISO-8601 — correlating with a deploy or another service depends on it.
- **A stable `event` name** — the key you group by.
- **`duration_ms` as a number**, not embedded in prose. `took 184ms` cannot be aggregated; `duration_ms=184.2` can.
- **Dimensions that split the data**: route, status, job name, tenant, cache hit/miss, row count, queue name.
- **Units in the field name** (`duration_ms`, `bytes`, `rows`) — unit confusion silently ruins aggregates.

Use the language's structured logging (JSON handler, `structlog`, `pino`, `zap`) rather than f-strings so the fields stay machine-readable.

## Percentiles from logs

Percentiles, never averages. From JSON logs with `jq`:

```bash
# p50/p95/p99 of a route over the last hour
jq -r 'select(.event=="http.request" and .route=="GET /reports") | .duration_ms' app.log \
  | sort -n \
  | awk '{v[NR]=$1} END {if (NR==0) {print "no samples"; exit}
         printf "n=%d  p50=%.1fms  p95=%.1fms  p99=%.1fms  max=%.1fms\n",
         NR, v[int(NR*0.50)], v[int(NR*0.95)], v[int(NR*0.99)], v[NR]}'
```

Plain-text logs work if the field is delimited — `awk` the duration out, then the same sort-and-index. Report `n` alongside the percentiles: a p99 from twelve samples is an anecdote with a decimal point.

Ratio metrics fall out of the same lines and catch what latency hides:

```bash
# route names contain spaces — emit tab-separated and split on the tab, not on whitespace
jq -r 'select(.event=="http.request") | [.route, (.db_queries // 0)] | @tsv' app.log \
  | awk -F'\t' '{c[$1]++; q[$1]+=$2} END {for (r in c) printf "%-30s n=%-6d avg_queries=%.1f\n", r, c[r], q[r]/c[r]}'
# GET /health   n=20   avg_queries=0.0
# GET /reports  n=500  avg_queries=4.8
```

A rising average query count per request is an N+1 forming — visible in logs long before it is visible in latency.

## Deploy and infra markers

Deployment is an event in the same timeline as your metrics, so it must be timestamped like one. An `echo` is a legitimate instrument:

```bash
echo "[$(date -u +%FT%TZ)] deploy start sha=$GIT_SHA env=$ENV"
# … deploy steps …
echo "[$(date -u +%FT%TZ)] deploy done sha=$GIT_SHA env=$ENV status=ok duration_s=$SECONDS"
```

Print the same marker around restarts, migrations, cache flushes and scaling events. Without markers, a latency graph that steps at 14:03 is a mystery; with them, it is a changelog entry. Log the commit SHA so a metric shift can be tied to a diff, not to a time window you have to reconstruct by hand.

## Correlating a change with a metric

1. Note the metric's before-value (from the logs or a saved baseline), the exact time, and the conditions (dataset, instance size, load).
2. Deploy; the marker lands in the timeline.
3. Compare the same window length, same route, same traffic mix, before vs after.
4. If other deploys or traffic shifts share the window, say so — an unattributed step is not evidence.
5. Record the result.

Log aggregation queries that carry their own caveats beat dashboards nobody annotates: write the window, the filters and the sample count next to the number.

## What to instrument, and what not to

| Always | Sometimes | Never |
|--------|-----------|-------|
| Request/route duration + status | Per-query timing on slow paths | Timing inside a per-iteration loop |
| Outbound call duration (with host) | Memory/cache size gauges | Logging every function entry/exit |
| Job/queue execution time + backlog | Sampled spans (1–10 %) | High-cardinality identifiers as metric labels |
| Cache hit/miss | GC pauses | Anything whose log volume exceeds the workload's own cost |
| Deploy/restart/migration markers | Thread/connection pool saturation | |

Sample when volume is the problem: 1 in N, or only when a duration crosses a threshold (`if ms > 100: log(...)`). Sampled data answers "is it slow", not "how many" — say which one your number is.

## Pitfalls

- **Averages as a summary.** Means hide the tail that users feel. Percentiles plus `max` plus `n`.
- **Wall-clock durations.** Use a monotonic source, or NTP will eventually invent a regression.
- **Logging the duration but not the unit.** `duration=184` is unusable six months later.
- **Timing inside the loop.** The instrument's overhead becomes the bottleneck; time the loop, then bisect if needed.
- **Measuring a warm cache only.** Cold and warm are different workloads; state which you measured.
- **Self-timed payloads on the client.** Client-reported durations include the network and the user's device — useful, but label them as end-to-end, not server time.
- **Unlabelled environment.** Development, CI and production numbers in one aggregate produce nonsense. Filter by environment, always.
- **Missing `n`.** A percentile without its sample count cannot be judged.
- **Deploy markers in local time.** Use UTC in logs; convert only for the human reading the report.
