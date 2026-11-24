// mobile-probe.js: measure the phone-layout faults a screenshot hides, on the page as it is rendered now.
// Run it in the page, for example:
//   agent-browser --session <s> eval "$(cat .agents/skills/mobile-friendly/scripts/mobile-probe.js)"
// It returns JSON: {viewport, counts, overflow, targets, crowded, smallText, smallInputs, edges, bars, truncated,
// vhRules, meta}. Each list holds the worst offenders (at most LIMIT); `counts` holds the full totals.
// A clean page has every count at 0 except `edges` (a histogram to read) and `bars` (read the height share).
// Thresholds follow WCAG 2.2 / Apple HIG / Material; change MIN_* only to match a project's own written rules.
(() => {
  const MIN_TARGET = 44; // px, each side of a tap target's hit area
  const MIN_GAP = 8; // px between neighbouring targets
  const MIN_TEXT = 12; // px, absolute minimum for any text
  const MIN_INPUT = 16; // px, below this iOS Safari zooms the page on focus
  const MAX_BARS_SHARE = 0.12; // share of viewport height that fixed or sticky bars may cover
  const LIMIT = 15;

  const W = window.innerWidth;
  const H = window.innerHeight;
  const doc = document.documentElement;
  const box = (e) => e.getBoundingClientRect();
  const style = (e) => getComputedStyle(e);
  const shown = (e) => {
    const r = box(e);
    const cs = style(e);
    // A 1 px box is a screen-reader-only element (a skip link), not something on screen.
    return r.width > 1 && r.height > 1 && cs.visibility !== "hidden" && cs.display !== "none" && parseFloat(cs.opacity) > 0;
  };
  const name = (e) => {
    const id = e.id ? `#${e.id}` : "";
    const cls = typeof e.className === "string" && e.className.trim() ? "." + e.className.trim().split(/\s+/).slice(0, 2).join(".") : "";
    const label = e.getAttribute("aria-label") || (e.innerText || e.value || "").trim().replace(/\s+/g, " ");
    return `${e.tagName.toLowerCase()}${id}${cls}${label ? ` "${label.slice(0, 32)}"` : ""}`;
  };
  const rect = (e) => {
    const r = box(e);
    return { x: Math.round(r.left), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height) };
  };
  const all = [...document.body.querySelectorAll("*")].filter((e) => !e.closest("svg") || e.tagName === "svg");

  // A region that scrolls sideways on purpose (a table, a diagram) may hold wide content; the page may not.
  const scrollsX = (e) => /(auto|scroll)/.test(style(e).overflowX) && e.scrollWidth > e.clientWidth + 1;
  const insideScroller = (e) => {
    for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) if (scrollsX(p)) return true;
    return false;
  };
  // Content clipped by an ancestor (overflow hidden or clip) is not on screen, so it cannot widen the page.
  const clipped = (e) => {
    for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) {
      const o = style(p).overflowX;
      if (o === "hidden" || o === "clip") return true;
    }
    return false;
  };
  const wide = all.filter((e) => shown(e) && style(e).position !== "fixed" && !insideScroller(e) && !clipped(e))
    .filter((e) => { const r = box(e); return r.right > W + 1 || r.left < -1; });
  // Report the outermost offenders: a child of a wide element is wide because of it.
  const overflow = wide.filter((e) => !wide.includes(e.parentElement))
    .map((e) => ({ el: name(e), ...rect(e), past: Math.round(Math.max(box(e).right - W, -box(e).left)) }));
  const scrollRegions = all.filter((e) => shown(e) && scrollsX(e) && e !== doc && e !== document.body)
    .map((e) => ({ el: name(e), named: e.hasAttribute("aria-label") || e.hasAttribute("aria-labelledby"), focusable: e.tabIndex >= 0 }));

  // Tap targets: a link inside running text is exempt (WCAG 2.5.8 inline exception).
  const TAPPABLE = "a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button], [role=link], [role=tab], [role=checkbox], [role=radio], [role=switch], [role=menuitem], [role=option], [tabindex]:not([tabindex='-1'])";
  const inline = (e) => e.tagName === "A" && style(e).display === "inline" && /\S/.test((e.parentElement?.innerText || "").replace(e.innerText, ""));
  const tappable = [...document.querySelectorAll(TAPPABLE)].filter((e) => shown(e) && !inline(e) && !e.disabled)
    // A label wrapping a small checkbox gives it its hit area; measure the label instead.
    .map((e) => (e.matches("input[type=checkbox], input[type=radio]") && e.closest("label") ? e.closest("label") : e))
    .filter((e, i, list) => list.indexOf(e) === i && !list.some((o) => o !== e && o.contains(e)));
  const targets = tappable.filter((e) => { const r = box(e); return r.width < MIN_TARGET || r.height < MIN_TARGET; })
    .map((e) => ({ el: name(e), ...rect(e) }));
  const crowded = [];
  for (let i = 0; i < tappable.length; i += 1) {
    for (let j = i + 1; j < tappable.length; j += 1) {
      const [a, b] = [box(tappable[i]), box(tappable[j])];
      const gx = Math.max(a.left, b.left) - Math.min(a.right, b.right);
      const gy = Math.max(a.top, b.top) - Math.min(a.bottom, b.bottom);
      const gap = Math.max(gx, gy);
      if (gap >= 0 && gap < MIN_GAP && (gx < 0 || gy < 0)) crowded.push({ a: name(tappable[i]), b: name(tappable[j]), gap: Math.round(gap) });
    }
  }

  // Text: every element that holds its own visible text.
  const ownText = (e) => [...e.childNodes].some((n) => n.nodeType === 3 && /\S/.test(n.textContent));
  const texty = all.filter((e) => ownText(e) && shown(e));
  const smallText = texty.filter((e) => parseFloat(style(e).fontSize) < MIN_TEXT)
    .map((e) => ({ el: name(e), px: parseFloat(style(e).fontSize) }));
  const smallInputs = [...document.querySelectorAll("input:not([type=checkbox]):not([type=radio]):not([type=range]):not([type=hidden]), select, textarea, [contenteditable=true]")]
    .filter((e) => shown(e) && parseFloat(style(e).fontSize) < MIN_INPUT)
    .map((e) => ({ el: name(e), px: parseFloat(style(e).fontSize) }));

  // Left edges: where each text line starts. Many distinct x values mean nested padding ate the width.
  const edgeCount = {};
  for (const e of texty) {
    const node = [...e.childNodes].find((n) => n.nodeType === 3 && /\S/.test(n.textContent));
    const range = document.createRange();
    range.selectNodeContents(node);
    const r = range.getClientRects()[0];
    if (!r || r.top > H * 3) continue;
    const x = Math.round(r.left);
    edgeCount[x] = (edgeCount[x] || 0) + 1;
  }
  const edges = Object.entries(edgeCount).map(([x, n]) => ({ x: Number(x), n })).sort((a, b) => b.n - a.n).slice(0, 8);

  // Fixed and sticky bars: together they may cover only a small share of the height.
  const barEls = all.filter((e) => shown(e) && /^(fixed|sticky)$/.test(style(e).position))
    .filter((e) => { const r = box(e); return r.width > W * 0.5 && r.height < H * 0.6; })
    .filter((e, i, list) => !list.some((o) => o !== e && o.contains(e)));
  const bars = barEls.map((e) => ({ el: name(e), position: style(e).position, h: Math.round(box(e).height), top: Math.round(box(e).top) }));
  const barsShare = Math.round((bars.reduce((s, b) => s + b.h, 0) / H) * 100) / 100;

  // Truncated text: an ellipsis or a clamp that actually cut something.
  const truncated = texty.filter((e) => {
    const cs = style(e);
    return (cs.textOverflow === "ellipsis" && e.scrollWidth > e.clientWidth + 1) || (cs.webkitLineClamp !== "none" && e.scrollHeight > e.clientHeight + 1);
  }).map((e) => ({ el: name(e) }));

  // 100vh on a phone ignores the browser toolbars; dvh/svh follow them. Same-origin sheets only.
  const vhRules = [];
  for (const sheet of document.styleSheets) {
    let rules;
    try { rules = sheet.cssRules; } catch { continue; }
    const walk = (list) => {
      for (const r of list) {
        if (r.cssRules) walk(r.cssRules);
        if (r.selectorText && /\b100vh\b/.test(r.cssText) && document.querySelector(r.selectorText.split(",")[0].replace(/::?[a-z-]+(\(.*\))?$/i, "") || "x-none")) vhRules.push(r.selectorText.slice(0, 60));
      }
    };
    walk(rules);
  }

  const viewportMeta = document.querySelector("meta[name=viewport]")?.content || "";
  const meta = {
    viewport: viewportMeta,
    zoomBlocked: /maximum-scale\s*=\s*1(\.0)?\b|user-scalable\s*=\s*(no|0)/.test(viewportMeta),
    fitCover: /viewport-fit\s*=\s*cover/.test(viewportMeta),
  };

  const counts = {
    pageScrollsSideways: doc.scrollWidth > W + 1 ? doc.scrollWidth - W : 0,
    overflow: overflow.length,
    unnamedScrollRegions: scrollRegions.filter((r) => !r.named || !r.focusable).length,
    smallTargets: targets.length,
    crowdedTargets: crowded.length,
    smallText: smallText.length,
    smallInputs: smallInputs.length,
    distinctEdges: Object.keys(edgeCount).length,
    barsOverShare: barsShare > MAX_BARS_SHARE ? barsShare : 0,
    truncated: truncated.length,
    vhRules: vhRules.length,
    zoomBlocked: meta.zoomBlocked ? 1 : 0,
  };
  const cap = (list) => list.slice(0, LIMIT);
  return JSON.stringify({
    viewport: { w: W, h: H, dpr: devicePixelRatio, coarse: matchMedia("(any-pointer: coarse)").matches },
    counts,
    overflow: cap(overflow),
    scrollRegions: cap(scrollRegions),
    targets: cap(targets),
    crowded: cap(crowded),
    smallText: cap(smallText),
    smallInputs: cap(smallInputs),
    edges,
    bars: { share: barsShare, list: cap(bars) },
    truncated: cap(truncated),
    vhRules: cap([...new Set(vhRules)]),
    meta,
  }, null, 1);
})();
