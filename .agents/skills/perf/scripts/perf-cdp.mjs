#!/usr/bin/env node
/**
 * perf-cdp.mjs — measure frontend rendering performance over the Chrome DevTools
 * Protocol. Zero dependencies: Node >= 22 (global fetch + WebSocket), Chrome/Chromium.
 *
 * Measures, in one run:
 *   - rendering cost deltas   Performance.getMetrics(): LayoutDuration, RecalcStyleDuration,
 *                             ScriptDuration, TaskDuration, JSHeapUsedSize (+Nodes/Documents gauges)
 *   - frame health            Tracing: presented frames, dropped frames, worst frame, effective FPS
 *   - page vitals             PerformanceObserver in-page: LCP, CLS, long tasks, event latency
 *   - interaction cost        each scenario step is timed and attributed to a trace window
 *
 * Usage:
 *   node perf-cdp.mjs --url http://localhost:3000 --scenario steps.json --out report.json
 *   node perf-cdp.mjs --cdp http://127.0.0.1:9222 --url http://localhost:3000 --duration 5000
 *   node perf-cdp.mjs --url http://localhost:3000 --script "document.querySelector('#go').click()"
 *
 * Flags:
 *   --url <u>            page to open (repeatable: navigations are interleaved by scenario)
 *   --scenario <file>    JSON array of steps: {type:click|eval|wait|scroll|navigate|key, ...}
 *   --script <js>        shorthand for a single eval step (repeatable)
 *   --duration <ms>      keep measuring an idle page for this long after the steps (default 0)
 *   --cdp <ws|http url>  attach to a running browser instead of launching Chrome
 *   --out <file>         write the full JSON report (default: ./perf-report.json)
 *   --fps-overlay        show the visual FPS counter in the page (Overlay.setShowFPSCounter)
 *   --headful            launch a visible window instead of headless
 *   --json               print the report as JSON only (no human summary)
 *   --debug              progress log to stderr
 */

import { spawn, execSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

// ---------------------------------------------------------------- CDP client

class CDP {
  constructor(ws) {
    this.ws = ws;
    this.seq = 0;
    this.pending = new Map();
    this.listeners = [];
    ws.addEventListener('message', (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id !== undefined) {
        const p = this.pending.get(msg.id);
        if (!p) return;
        this.pending.delete(msg.id);
        msg.error ? p.reject(new Error(`${p.method}: ${msg.error.message}`)) : p.resolve(msg.result);
      } else {
        for (const l of this.listeners) l(msg);
      }
    });
  }

  static async connect(url) {
    const ws = new WebSocket(url);
    await new Promise((res, rej) => {
      ws.addEventListener('open', res, { once: true });
      ws.addEventListener('error', () => rej(new Error(`cannot connect to ${url}`)), { once: true });
    });
    return new CDP(ws);
  }

  send(method, params = {}, sessionId) {
    const id = ++this.seq;
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    this.ws.send(JSON.stringify(payload));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject, method });
      setTimeout(() => {
        if (this.pending.delete(id)) reject(new Error(`${method}: timed out`));
      }, 120_000);
    });
  }

  on(fn) { this.listeners.push(fn); return () => { this.listeners = this.listeners.filter((l) => l !== fn); }; }

  close() { try { this.ws.close(); } catch {} }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Progress to stderr only when --debug is set (stdout stays machine-readable).
let DEBUG = false;
const dbg = (...a) => { if (DEBUG) console.error(`[${new Date().toISOString().slice(11, 19)}]`, ...a); };

// ---------------------------------------------------------------- launch / attach

async function rpcJson(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url} -> HTTP ${r.status}`);
  return r.json();
}

async function waitForPort(port, ms = 15_000) {
  const deadline = Date.now() + ms;
  while (Date.now() < deadline) {
    try { return await rpcJson(`http://127.0.0.1:${port}/json/version`); } catch { await sleep(120); }
  }
  throw new Error(`Chrome did not expose a debugging port within ${ms}ms`);
}

async function launchChrome({ headful }) {
  const profile = mkdtempSync(join(tmpdir(), 'perf-cdp-'));
  const bin = ['google-chrome-stable', 'google-chrome', 'chromium', 'chromium-browser', 'msedge']
    .find((c) => spawnSyncWhich(c));
  if (!bin) throw new Error('no Chrome/Chromium/Edge binary found on PATH');
  const args = [
    '--remote-debugging-port=0',
    `--user-data-dir=${profile}`,
    '--no-first-run', '--no-default-browser-check',
    // REQUIRED on Linux hosts with no running secret service (gnome-keyring/kwallet):
    // Chrome's default password store blocks startup and every navigation never commits.
    '--password-store=basic',
    '--disable-component-update',
    '--disable-sync',
    '--disable-background-timer-throttling',      // do not let a hidden page be throttled
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--window-size=1280,900',
  ];
  if (headful) args.push('--new-window');
  else args.push('--headless=new');
  args.push('about:blank');

  const proc = spawn(bin, args, { stdio: 'ignore', detached: false });
  const portFile = join(profile, 'DevToolsActivePort');
  const deadline = Date.now() + 15_000;
  let port;
  while (Date.now() < deadline) {
    if (existsSync(portFile)) {
      const first = readFileSync(portFile, 'utf8').split('\n')[0].trim();
      if (first) { port = Number(first); break; }
    }
    await sleep(100);
  }
  if (!port) { proc.kill(); throw new Error('Chrome never wrote DevToolsActivePort'); }
  const version = await waitForPort(port);
  return { proc, port, browserWsUrl: version.webSocketDebuggerUrl, bin };
}

function spawnSyncWhich(cmd) {
  try { execSync(`command -v ${cmd}`, { stdio: 'ignore' }); return true; } catch { return false; }
}

// ---------------------------------------------------------------- page-side probe

// Injected before any page script runs; collects the metrics CDP does not expose.
const VITALS_PROBE = `(() => {
  if (window.__perfProbe) return;
  const p = window.__perfProbe = { lcp: 0, cls: 0, longTasks: [], shifts: [], events: [], marks: [] };
  try {
    new PerformanceObserver((l) => { for (const e of l.getEntries()) p.lcp = Math.max(p.lcp, e.startTime); })
      .observe({ type: 'largest-contentful-paint', buffered: true });
  } catch {}
  try {
    new PerformanceObserver((l) => {
      for (const e of l.getEntries()) {
        if (e.hadRecentInput) continue;
        p.cls += e.value;
        p.shifts.push({ value: e.value, startTime: e.startTime });
      }
    }).observe({ type: 'layout-shift', buffered: true });
  } catch {}
  try {
    new PerformanceObserver((l) => {
      for (const e of l.getEntries()) p.longTasks.push({ startTime: e.startTime, duration: e.duration });
    }).observe({ type: 'longtask', buffered: true });
  } catch {}
  try {
    new PerformanceObserver((l) => {
      for (const e of l.getEntries()) p.events.push({ name: e.name, duration: e.duration, startTime: e.startTime });
    }).observe({ type: 'event', buffered: true, durationThreshold: 16 });
  } catch {}
  const t0 = performance.now();
  setInterval(() => { p.marks.push({ t: performance.now() - t0, heap: (performance.memory||{}).usedJSHeapSize || 0 }); }, 250);
})();`;

// ---------------------------------------------------------------- main

function parseArgs(argv) {
  const out = { urls: [], steps: [], scripts: [], duration: 0, out: 'perf-report.json', fpsOverlay: false, headful: false, json: false, cdp: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => argv[++i];
    if (a === '--url') out.urls.push(next());
    else if (a === '--scenario') out.steps.push(...JSON.parse(readFileSync(next(), 'utf8')));
    else if (a === '--script') out.scripts.push(next());
    else if (a === '--duration') out.duration = Number(next());
    else if (a === '--out') out.out = next();
    else if (a === '--cdp') out.cdp = next();
    else if (a === '--fps-overlay') out.fpsOverlay = true;
    else if (a === '--headful') out.headful = true;
    else if (a === '--json') out.json = true;
    else if (a === '--debug') out.debug = true;
    else if (a === '-h' || a === '--help') { console.log(readFileSync(new URL(import.meta.url)).toString().split('*/')[0]); process.exit(0); }
    else throw new Error(`unknown flag: ${a}`);
  }
  for (const s of out.scripts) out.steps.push({ type: 'eval', expression: s });
  return out;
}

// Performance.getMetrics names worth diffing across the run.
const DELTA_METRICS = [
  'LayoutDuration', 'RecalcStyleDuration', 'ScriptDuration', 'TaskDuration',
  'LayoutCount', 'RecalcStyleCount', 'JSHeapUsedSize', 'Nodes', 'Documents',
];
const GAUGE_METRICS = ['Nodes', 'Documents', 'JSHeapUsedSize', 'JSHeapTotalSize', 'Frames'];

async function getMetrics(cdp, session) {
  const { metrics } = await cdp.send('Performance.getMetrics', {}, session);
  return Object.fromEntries(metrics.map((m) => [m.name, m.value]));
}

// Trace analysis: frames presented vs dropped, and the worst offenders by category.
function analyseTrace(events) {
  const byName = new Map();
  for (const e of events) byName.set(e.name, (byName.get(e.name) || 0) + 1);

  const presented = events.filter((e) => e.name === 'DrawFrame' || e.name === 'ActivateLayerTree');
  const dropped = events.filter((e) => e.name === 'DroppedFrame');
  const beginFrames = events.filter((e) => e.name === 'BeginFrame');

  const times = presented.map((e) => e.ts).filter(Boolean).sort((a, b) => a - b);
  const spanMs = times.length > 1 ? (times[times.length - 1] - times[0]) / 1000 : 0;
  const fps = spanMs > 0 ? (times.length - 1) / (spanMs / 1000) : 0;

  // Longest complete events (dur is in microseconds), by name — reveals what ate the budget.
  const dur = events.filter((e) => typeof e.dur === 'number' && e.dur > 0);
  const totalUsByName = new Map();
  for (const e of dur) totalUsByName.set(e.name, (totalUsByName.get(e.name) || 0) + e.dur);
  const hottest = [...totalUsByName.entries()]
    .map(([name, us]) => ({ name, totalMs: +(us / 1000).toFixed(1) }))
    .sort((a, b) => b.totalMs - a.totalMs).slice(0, 15);

  return {
    droppedFrames: dropped.length,
    presentedFrames: presented.length,
    beginFrames: beginFrames.length,
    effectiveFps: +fps.toFixed(1),
    measuredSpanMs: +spanMs.toFixed(0),
    frameEventNames: {
      DrawFrame: byName.get('DrawFrame') || 0,
      ActivateLayerTree: byName.get('ActivateLayerTree') || 0,
      BeginFrame: byName.get('BeginFrame') || 0,
      DroppedFrame: byName.get('DroppedFrame') || 0,
    },
    hottestByTotalTime: hottest,
    droppedFrameSamples: dropped.slice(0, 20).map((e) => ({ ts: e.ts, args: e.args })),
    topLevelEventCount: byName.get('RunTask') || 0,
  };
}

async function runScenario(cdp, session, steps) {
  const results = [];
  for (const step of steps) {
    const t0 = Date.now();
    let note = '';
    switch (step.type) {
      case 'navigate': {
        await navigateAndWait(cdp, session, step.url, step.timeoutMs || 30_000);
        note = step.url;
        break;
      }
      case 'click': {
        const box = await cdp.send('Runtime.evaluate', {
          expression: `(() => { const el = document.querySelector(${JSON.stringify(step.selector)});
            if (!el) return null; const r = el.getBoundingClientRect();
            return JSON.stringify({x: r.left + r.width/2, y: r.top + r.height/2}); })()`,
          returnByValue: true,
        }, session);
        if (!box.result.value) throw new Error(`click: selector not found: ${step.selector}`);
        const { x, y } = JSON.parse(box.result.value);
        await cdp.send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 }, session);
        await cdp.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 }, session);
        note = step.selector;
        break;
      }
      case 'eval': {
        const r = await cdp.send('Runtime.evaluate', { expression: step.expression, awaitPromise: !!step.awaitPromise, returnByValue: true }, session);
        if (r.exceptionDetails) throw new Error(`eval failed: ${r.exceptionDetails.text} ${r.exceptionDetails.exception?.description || ''}`);
        note = JSON.stringify(r.result.value ?? null).slice(0, 120);
        break;
      }
      case 'wait': await sleep(step.ms || 1000); note = `${step.ms || 1000}ms`; break;
      case 'scroll': {
        const y = step.y ?? 500;
        await cdp.send('Runtime.evaluate', { expression: `window.scrollTo(0, ${y})` }, session);
        note = `y=${y}`;
        break;
      }
      case 'key': {
        await cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', key: step.key }, session);
        await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', key: step.key }, session);
        note = step.key;
        break;
      }
      default: throw new Error(`unknown step type: ${step.type}`);
    }
    results.push({ step: step.type, target: note || step.label || '', wallMs: Date.now() - t0 });
  }
  return results;
}

// Listen before navigating: the load event can fire before a listener registered afterwards.
async function navigateAndWait(cdp, session, url, timeoutMs) {
  const loaded = new Promise((resolve) => {
    const off = cdp.on((msg) => {
      if (msg.method === 'Page.loadEventFired') { off(); clearTimeout(to); resolve('load'); }
    });
    const to = setTimeout(() => { off(); resolve('timeout'); }, timeoutMs);
  });
  await cdp.send('Page.navigate', { url }, session);
  const how = await loaded;
  if (how === 'timeout') console.error(`! ${url} did not finish loading within ${timeoutMs}ms — measuring anyway`);
  return how;
}

function summarise(report) {
  const L = [];
  const c = report.rendering.cost;
  L.push(`rendering cost (${report.duration.wallMs}ms wall, ${report.duration.measuredMs}ms measured)`);
  L.push(`  layout      ${(c.LayoutDuration * 1000).toFixed(0)}ms  (${c.LayoutCount} re-layouts)`);
  L.push(`  style recalc ${(c.RecalcStyleDuration * 1000).toFixed(0)}ms  (${c.RecalcStyleCount} recalcs)`);
  L.push(`  script      ${(c.ScriptDuration * 1000).toFixed(0)}ms ${c.ScriptDuration > 0.2 ? '  <- script-bound' : ''}`);
  L.push(`  task total  ${(c.TaskDuration * 1000).toFixed(0)}ms`);
  L.push(`frames: ${report.frames.effectiveFps} fps effective, ${report.frames.presentedFrames} presented, ${report.frames.droppedFrames} dropped`);
  L.push(`vitals: LCP ${report.vitals.lcpMs.toFixed(0)}ms, CLS ${report.vitals.cls.toFixed(3)}, long tasks ${report.vitals.longTasks.count} (worst ${report.vitals.longTasks.worstMs.toFixed(0)}ms), worst interaction ${report.vitals.worstInteractionMs.toFixed(0)}ms`);
  if (report.frames.hottestByTotalTime.length) {
    L.push('hottest trace events by total time:');
    for (const h of report.frames.hottestByTotalTime.slice(0, 6)) L.push(`  ${h.totalMs}ms  ${h.name}`);
  }
  if (report.steps.length) {
    L.push('scenario steps:');
    for (const s of report.steps) L.push(`  ${s.step} ${s.target} — ${s.wallMs}ms`);
  }
  return L.join('\n');
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  DEBUG = !!args.debug;
  dbg('args', JSON.stringify(args));
  if (!args.urls.length && !args.steps.some((s) => s.type === 'navigate')) {
    throw new Error('nothing to measure: pass --url or a scenario with a navigate step');
  }
  const target = args.urls[0] || args.steps.find((s) => s.type === 'navigate').url;

  let chrome = null, browserWs = args.cdp, bin = null;
  if (args.cdp && args.cdp.startsWith('ws')) {
    browserWs = args.cdp;
  } else if (args.cdp) {
    const v = await rpcJson(args.cdp.replace(/\/$/, '') + '/json/version');
    browserWs = v.webSocketDebuggerUrl;
  } else {
    chrome = await launchChrome({ headful: args.headful });
    browserWs = chrome.browserWsUrl;
    bin = chrome.bin;
  }

  const cdp = await CDP.connect(browserWs);
  const { targetId } = await cdp.send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await cdp.send('Target.attachToTarget', { targetId, flatten: true });

  await cdp.send('Page.enable', {}, sessionId);
  await cdp.send('Runtime.enable', {}, sessionId);
  await cdp.send('Performance.enable', {}, sessionId);

  // Collect every console error — a perf run that broke the page is not a perf run.
  const consoleErrors = [];
  cdp.on((m) => {
    if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') consoleErrors.push(m.params.entry.text);
    if (m.method === 'Runtime.exceptionThrown') consoleErrors.push(m.params.exceptionDetails.text);
  });
  await cdp.send('Log.enable', {}, sessionId);

  // Probe must be installed before the page's own scripts run.
  await cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: VITALS_PROBE }, sessionId);

  if (args.fpsOverlay) {
    try {
      await cdp.send('DOM.enable', {}, sessionId);      // Overlay.enable refuses without it
      await cdp.send('Overlay.enable', {}, sessionId);
      await cdp.send('Overlay.setShowFPSCounter', { show: true }, sessionId);
      dbg('FPS counter overlay on');
    }
    catch (e) { console.error(`! FPS overlay unavailable: ${e.message}`); }
  }

  // ---- baseline: load the page, let it settle, snapshot cumulative metrics
  dbg('navigating to', target);
  await navigateAndWait(cdp, sessionId, target, 30_000);
  await sleep(500);
  const before = await getMetrics(cdp, sessionId);
  dbg('baseline metrics captured');
  const wallStart = Date.now();

  const TRACE_CATEGORIES = [
    'devtools.timeline',
    'disabled-by-default-devtools.timeline.frame',
    'blink.user_timing',
    'benchmark',
  ].join(',');

  const traceEvents = [];
  const offTrace = cdp.on((m) => {
    if (m.method === 'Tracing.dataCollected') traceEvents.push(...m.params.value);
    if (m.method === 'Tracing.bufferUsage' && m.params.value > 0.9) console.error('! trace buffer nearly full');
  });
  await cdp.send('Tracing.start', {
    categories: TRACE_CATEGORIES,
    options: 'record-until-full',
    transferMode: 'ReportEvents',
  }, sessionId);

  const measured0 = Date.now();
  const steps = args.steps;
  dbg('running', steps.length, 'scenario steps');
  const stepResults = await runScenario(cdp, sessionId, steps);
  if (args.duration > 0) await sleep(args.duration);
  const measuredMs = Date.now() - measured0;
  dbg('steps done in', measuredMs, 'ms');

  const tracingDone = new Promise((res) => {
    const off = cdp.on((m) => { if (m.method === 'Tracing.tracingComplete') { off(); res('complete'); } });
    setTimeout(() => { off(); res('timeout'); }, 30_000);   // never hang the run on a trace
  });
  await cdp.send('Tracing.end', {}, sessionId);
  dbg('trace end ->', await tracingDone, 'events', traceEvents.length);
  offTrace();

  const after = await getMetrics(cdp, sessionId);
  const wallMs = Date.now() - wallStart;

  const probe = await cdp.send('Runtime.evaluate', {
    expression: `JSON.stringify(window.__perfProbe ? {
      lcp: __perfProbe.lcp, cls: __perfProbe.cls,
      longTasks: __perfProbe.longTasks, shifts: __perfProbe.shifts,
      events: __perfProbe.events, marks: __perfProbe.marks
    } : null)`,
    returnByValue: true,
  }, sessionId);
  const raw = probe.result.value ? JSON.parse(probe.result.value) : null;

  const cost = {};
  for (const k of DELTA_METRICS) {
    if (before[k] !== undefined && after[k] !== undefined) {
      // Durations/counters are cumulative; Nodes/Documents/JSHeapUsedSize are gauges.
      cost[k] = GAUGE_METRICS.includes(k) ? after[k] : +(after[k] - before[k]).toFixed(4);
    }
  }

  const longTasks = (raw?.longTasks || []).filter((t) => t.duration >= 50);
  const report = {
    tool: 'perf-cdp',
    when: new Date().toISOString(),
    target,
    browser: bin || 'attached',
    attachedTo: args.cdp || null,
    duration: { wallMs, measuredMs },
    scenario: { steps: steps.map((s) => s.type), idleAfterStepsMs: args.duration },
    rendering: { cost, gauges: Object.fromEntries(GAUGE_METRICS.filter((k) => after[k] !== undefined).map((k) => [k, after[k]])) },
    frames: analyseTrace(traceEvents),
    vitals: {
      lcpMs: +(raw?.lcp || 0).toFixed(1),
      cls: +(raw?.cls || 0).toFixed(4),
      longTasks: {
        count: longTasks.length,
        worstMs: +(longTasks.reduce((m, t) => Math.max(m, t.duration), 0)).toFixed(1),
        totalMs: +(longTasks.reduce((s, t) => s + t.duration, 0)).toFixed(1),
        top: longTasks.slice(0, 10).map((t) => ({ startMs: +t.startTime.toFixed(0), durationMs: +t.duration.toFixed(0) })),
      },
      worstInteractionMs: +((raw?.events || []).reduce((m, e) => Math.max(m, e.duration), 0)).toFixed(1),
      interactions: (raw?.events || []).slice(0, 20).map((e) => ({ name: e.name, durationMs: +e.duration.toFixed(1) })),
      layoutShifts: (raw?.shifts || []).slice(0, 20),
    },
    steps: stepResults,
    consoleErrors,
    traceEventCount: traceEvents.length,
  };

  writeFileSync(args.out, JSON.stringify(report, null, 2));
  console.log(args.json ? JSON.stringify(report, null, 2) : summarise(report));
  if (!args.json) console.log(`\nfull report -> ${args.out}`);

  cdp.close();
  if (chrome?.proc) chrome.proc.kill();
}

main().catch((e) => { console.error(`perf-cdp: ${e.message}`); process.exit(1); });
