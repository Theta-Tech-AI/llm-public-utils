# Frontend rendering measurement over the Chrome DevTools Protocol

Everything here was exercised against Chrome 151/152 on Linux; the raw protocol (not a wrapper library) is used so the same code works from any harness, in any language, with zero dependencies.

## Contents

- [Connecting](#connecting)
- [1. Rendering cost — `Performance.getMetrics`](#1-rendering-cost--performancegetmetrics)
- [2. Frame health — `Tracing`](#2-frame-health--tracing)
- [3. Visual FPS — `Overlay.setShowFPSCounter`](#3-visual-fps--overlaysetshowfpscounter)
- [4. Page vitals — `PerformanceObserver` in the page](#4-page-vitals--performanceobserver-in-the-page)
- [5. Driving interactions — `Input`](#5-driving-interactions--input)
- [Metric definitions](#metric-definitions)
- [Launching Chrome for measurement](#launching-chrome-for-measurement)
- [Pitfalls](#pitfalls)

## Connecting

Three ways in, in order of preference for measurement work:

| Route | When | How |
|-------|------|-----|
| Launch your own | Repeatable, isolated runs | `chrome --remote-debugging-port=0` and read `DevToolsActivePort` from the profile dir |
| Attach to an existing browser | The app under test is already open, or a harness owns the session | `--cdp <ws-url>` / `--cdp http://127.0.0.1:9222` |
| Attach from a test runner | Playwright/Puppeteer already drives the page | Playwright: `chromium.connectOverCDP(endpoint)`; Puppeteer: `puppeteer.connect({ browserURL })` — then go raw with `client.send(...)` if you want these exact metrics |

Useful endpoints on any running browser: `GET /json/version` (yields `webSocketDebuggerUrl` for the browser), `GET /json/list` (page targets). If a tool already launched a browser for you (`agent-browser get cdp-url` prints one) reuse it rather than launching a second instance.

A minimal raw client in Node ≥ 22 (global `WebSocket`, no npm packages):

```js
const ws = new WebSocket(browserWsUrl);
await new Promise((r) => ws.addEventListener('open', r, { once: true }));
let seq = 0; const pend = new Map();
ws.addEventListener('message', (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id !== undefined) pend.get(m.id)?.(m);          // command reply
  else handleEvent(m);                                   // Tracing.dataCollected, Page.loadEventFired, …
});
const send = (method, params = {}, sessionId) => new Promise((resolve, reject) => {
  const id = ++seq;
  pend.set(id, (m) => (m.error ? reject(new Error(`${method}: ${m.error.message}`)) : resolve(m.result)));
  ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
});

// one tab, addressed by sessionId for the rest of the run
const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
```

Then `Page.enable`, `Runtime.enable`, `Performance.enable` on `sessionId`.

## 1. Rendering cost — `Performance.getMetrics`

```js
await send('Performance.enable', {}, sessionId);
const { metrics } = await send('Performance.getMetrics', {}, sessionId);
const m = Object.fromEntries(metrics.map((x) => [x.name, x.value]));
```

Thirty-six metrics come back (Chrome 151). The ones worth recording, with their units — **seconds**:

| Metric | Kind | Meaning |
|--------|------|---------|
| `LayoutDuration` | cumulative | Time in layout (reflow). Grows with layout thrash and forced synchronous layout |
| `RecalcStyleDuration` | cumulative | Time recomputing styles |
| `ScriptDuration` | cumulative | Time executing JavaScript |
| `TaskDuration` | cumulative | Total main-thread task time — the ceiling the other three live under |
| `LayoutCount` / `RecalcStyleCount` | cumulative | Event counts; useful as a ratio against the durations |
| `JSHeapUsedSize` / `JSHeapTotalSize` | gauge | Memory |
| `Nodes` / `Documents` / `Frames` | gauge | DOM size and frame count |

**Duration and count metrics are cumulative for the page's lifetime**, so a measurement is the difference of two snapshots: take one after load, run the scenario, take another. Reporting the raw total after navigation measures page load, not the thing you changed. Millisecond conversion: `value * 1000`.

## 2. Frame health — `Tracing`

This is where dropped frames and rendering time per frame come from.

```js
await send('Tracing.start', {
  categories: 'devtools.timeline,disabled-by-default-devtools.timeline.frame,blink.user_timing,benchmark',
  options: 'record-until-full',
  transferMode: 'ReportEvents',
}, sessionId);

// …drive the page (click, scroll, type)…

const done = new Promise((res) => { /* resolve on Tracing.tracingComplete */ });
await send('Tracing.end', {}, sessionId);
await done;
```

Events arrive as `Tracing.dataCollected` notifications (`params.value` is an array of events) and always end with `Tracing.tracingComplete`. Parse them in memory — a few seconds of tracing is on the order of tens of thousands of events (44k for a 6-second heavily-janked run) and a few MB, so a one-off in-process pass is fine; for long traces use `transferMode: 'ReturnAsStream'` and read the stream.

Frame-relevant event names, with `ts` in microseconds and `dur` (when present) also microseconds:

| Event | Use |
|-------|-----|
| `DroppedFrame` | **The jank count.** Each one is a frame the compositor could not present in its budget |
| `DrawFrame` / `ActivateLayerTree` | Frames actually presented — count these and divide by the span for effective FPS |
| `BeginFrame` | Frame budget ticks; `BeginFrame - presented` approximates the drop rate |
| `FireAnimationFrame` | rAF callback execution — the usual suspect when script time is high |
| `Layout` / `LocalFrameView::layout` / `PrePaint` / `Paint` | Rendering pipeline; their totals say whether you are layout-bound or paint-bound |
| `RunTask` | Main-thread task envelope |
| `ProxyMain::BeginMainFrame` | Total time the main thread held the frame — the umbrella number |

Effective FPS from the trace:

```js
const presented = events.filter((e) => e.name === 'DrawFrame' || e.name === 'ActivateLayerTree');
const dropped   = events.filter((e) => e.name === 'DroppedFrame').length;
const ts = presented.map((e) => e.ts).sort((a, b) => a - b);
const fps = ts.length > 1 ? (ts.length - 1) / ((ts[ts.length - 1] - ts[0]) / 1e6) : 0;
```

Two more fields on every event are worth having: `name` and `args`. Aggregating `dur` by `name` and sorting descending produces the **hottest events by total time** — the single most useful output of a trace, because it names where the milliseconds went instead of leaving you to guess.

`disabled-by-default-devtools.timeline.frame` is required for the frame-scoped events; `devtools.timeline` alone gives you the pipeline but not the frame accounting. Categories are additive, and adding `v8` or `disabled-by-default-v8.cpu_profiler` costs buffer and performance — include them only when you are hunting a JS hotspot specifically.

## 3. Visual FPS — `Overlay.setShowFPSCounter`

For a human watching the screen (or a screenshot artifact to attach to a report):

```js
await send('DOM.enable', {}, sessionId);        // Overlay.enable fails without it:
                                               //   "DOM should be enabled first"
await send('Overlay.enable', {}, sessionId);
await send('Overlay.setShowFPSCounter', { show: true }, sessionId);
```

The HUD renders in the top-left corner showing frame rate, a frame-rate history graph, GPU raster status and GPU memory. Verified: `Frame Rate 60.0 fps`, green, frame graph pegged — captured with `Page.captureScreenshot` on a headless run, so it works without a display server.

## 4. Page vitals — `PerformanceObserver` in the page

CDP does not expose LCP, CLS or long tasks; the page can. Install the observer **before any page script runs** so buffered entries are not missed:

```js
await send('Page.addScriptToEvaluateOnNewDocument', { source: PROBE }, sessionId);
```

`PROBE` registers observers for these entry types (all with `buffered: true`):

| Entry type | Gives | Threshold that matters |
|------------|-------|------------------------|
| `largest-contentful-paint` | LCP — when the main content painted | > 2.5 s is "poor" |
| `layout-shift` | CLS — accumulated shift, skipping entries with `hadRecentInput` | > 0.1 is "poor" |
| `longtask` | Main-thread tasks ≥ 50 ms | any is a jank source |
| `event` | Interaction latency, per event name (`durationThreshold: 16`) | p98 > 200 ms is "poor" |

Read them back later with one `Runtime.evaluate` returning `JSON.stringify(...)`. LCP and CLS are meaningless in a warm page you navigated to minutes ago — measure them on a fresh load.

## 5. Driving interactions — `Input`

Metrics without a scenario measure an idle page. Drive real input rather than calling handlers directly, so the browser does hit-testing and event dispatch the way a user does:

```js
const box = await send('Runtime.evaluate', {
  expression: `(() => { const r = document.querySelector('#go').getBoundingClientRect();
    return JSON.stringify({x: r.left + r.width/2, y: r.top + r.height/2}); })()`,
  returnByValue: true,
}, sessionId);
const { x, y } = JSON.parse(box.result.value);
await send('Input.dispatchMouseEvent', { type: 'mousePressed',  x, y, button: 'left', clickCount: 1 }, sessionId);
await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 }, sessionId);
```

Keys: `Input.dispatchKeyEvent` (`keyDown`/`keyUp`). Scrolling: `Runtime.evaluate("window.scrollTo(0, y)")` for programmatic, or `Input.dispatchMouseEvent` with `type: 'mouseWheel'` when you want the real wheel path.

Time each step as wall-clock around the dispatch — a slow handler is otherwise invisible in a whole-run aggregate.

## Metric definitions

Reading a number without its definition invites wrong conclusions:

- **Effective FPS** — presented frames per second across the measured span. Compare against the display budget (60 fps ⇒ 16.7 ms per frame); sustained 30 fps means every other frame is late, not "half speed".
- **Dropped frames** — frames the compositor missed. The right metric for "does the scroll stutter".
- **`LayoutDuration`** — total layout time; high relative to `TaskDuration` means you are reflow-bound (forced synchronous layout, animating layout properties, huge DOM).
- **`RecalcStyleDuration`** — selector invalidation cost; check broad descendant selectors and class churn.
- **`ScriptDuration`** — JS execution; if this dominates, the answer is algorithmic, not CSS.
- **Long tasks** — anything ≥ 50 ms blocks input; count and *worst* matter more than total.
- **CLS** — layout shift; late-injected content without reserved space is the classic cause.
- **LCP** — when the main content painted; a render-blocking resource or a slow API is the usual cause.

## Launching Chrome for measurement

Flags that matter, with the reason:

```bash
--headless=new                                  # no display server needed; frames still produced
--remote-debugging-port=0                       # port written to <profile>/DevToolsActivePort
--user-data-dir=<fresh temp dir>                # isolation: one profile per run
--password-store=basic                          # REQUIRED on Linux with no running secret service
--disable-component-update --disable-sync       # no background network during a run
--disable-background-timer-throttling           # a hidden/occluded page is throttled — that is a wrong
--disable-backgrounding-occluded-windows        #   measurement, not a fast page
--disable-renderer-backgrounding
--window-size=1280,900
```

**The `--password-store=basic` flag is not optional on bare Linux hosts.** Without a running gnome-keyring/kwallet, Chrome's default password store blocks startup: `Target.createTarget` silently leaves the target on `about:blank`, `Page.navigate` never returns, and every subsequent CDP command on that session times out — which reads exactly like a broken client. Symptom signature: `data:` URLs navigate fine, `http(s)://` URLs never commit. Diagnosed by bisecting launch flags against a known-good browser instance; `--password-store=basic` alone fixes it (`--use-mock-keychain` does not).

## Pitfalls

- **Cumulative vs gauge metrics.** Diffing `LayoutDuration` is right; diffing `Nodes` or `JSHeapUsedSize` is not — those are snapshots.
- **Measuring in a background tab** gives throttled timers and near-zero frame activity. Keep the window visible, or pass the anti-throttling flags above.
- **`record-until-full` can overflow**; watch `Tracing.bufferUsage` and stop the trace when it approaches 1.
- **A trace of an idle page measures nothing.** Every claim about frames needs a scenario: scroll, click, type.
- **Frames do not present at all** on some attached/occluded targets (0 presented, 0 dropped) — that is a visibility artifact, not a perfect score. Confirm the target is foreground before trusting FPS.
- **Instrumentation changes what you measure** if your probe runs `setInterval` work in the measured page; keep the probe passive (observers only).
- **Do not trust a single run.** Frame accounting on a headless host varies run to run; repeat and report the median, or you will chase noise.
