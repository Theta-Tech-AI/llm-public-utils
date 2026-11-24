// mobile-probe.js: measure the phone-layout faults a screenshot hides, on the page as it is rendered now.
// Run it in the page, for example:
//   agent-browser --session <s> eval "$(cat .agents/skills/mobile-friendly/scripts/mobile-probe.js)"
// To judge one page and not the shared frame, set a root first (it limits targets, text, edges, overlaps, clipped;
// page sideways scroll, overflow, bars and vhRules stay global; set it to '' to clear it):
//   agent-browser --session <s> eval "window.__mobileProbeRoot='main'; $(cat .agents/skills/mobile-friendly/scripts/mobile-probe.js)"
// It returns JSON with these keys. Each list holds the worst offenders (at most LIMIT); `counts` holds the full totals.
//   viewport        {w, h, dpr, coarse}
//   root            {selector, found}: the scope in use
//   counts          one number per fault below, 0 is clean (distinctEdges and barsOverShare are a count and a share)
//   overflow        outermost elements wider than a page scroller (the document or an app-shell scroll container)
//   clipped         elements cut by an overflow hidden/clip ancestor (content the user cannot reach; judge each one)
//   scrollers       every scroll container found; page:true marks the ones that carry the page. Scroll the inner
//                   page scroller to shoot below the fold: a full-page screenshot only shows its first screen
//   scrollRegions   narrower regions that scroll sideways on purpose (they need a name and keyboard focus)
//   targets         tap targets under MIN_TARGET px
//   crowded         target pairs closer than MIN_GAP px (overlap counts as distance 0)
//   overlaps        text over a control it is not inside, or two controls that intersect
//   smallText       text under MIN_TEXT px
//   smallBody       running text under MIN_BODY px: text in a p/li/dd/td/blockquote/figcaption whose whole text is over
//                   40 characters, or any other element whose own text is over 40 characters
//   smallSecondary  short text (labels, captions) from MIN_TEXT up to MIN_SECONDARY px
//   textSizes       histogram {px: number of text elements}
//   smallInputs     form fields under MIN_INPUT px (iOS Safari zooms on focus)
//   edges           histogram of where text lines start (many distinct x means nested padding ate the width)
//   bars            fixed/sticky bars: share = union of the viewport height they cover, list = each bar
//   truncated       text cut by an ellipsis, a line clamp, or an overflow-hidden box of its own (even with no ellipsis)
//   offscreenFixed  fixed or stuck elements that cross the viewport edge (they never widen the page, so overflow misses them)
//   vhRules         CSS rules that use 100vh without a dvh/svh/lvh twin, on elements that exist now
//   meta            {viewport, zoomBlocked, fitCover}
// Heuristics that cannot be exact have a hook (set it in the same eval, before the file):
//   window.__mobileProbePageScroller = '<selector list>'  the scroll containers that carry the page (replaces the guess)
//   [data-scroll-region] or role=region with a name        an intentional sideways scroll region (never a page scroller)
// Without the hook, a page scroller is a scroll container that holds the main landmark or the h1; only if none does,
// a container at least 90 % of the viewport wide and half as tall. A modal <dialog> limits targets, crowded and
// overlaps to the top-most open one (root.modal names it). A custom modal that is not a <dialog> needs __mobileProbeRoot.
// A clean page has every count at 0 except `edges` (a histogram to read) and `bars` (read the share).
// Thresholds follow WCAG 2.2 / Apple HIG / Material; change MIN_* only to match a project's own written rules.
(() => {
  const MIN_TARGET = 44; // px, each side of a tap target's hit area
  const MIN_GAP = 8; // px between neighbouring targets
  const MIN_TEXT = 12; // px, absolute minimum for any text
  const MIN_BODY = 16; // px, running text on a phone
  const MIN_SECONDARY = 13; // px, short labels and captions
  const MIN_INPUT = 16; // px, below this iOS Safari zooms the page on focus
  const MAX_BARS_SHARE = 0.12; // share of viewport height that fixed or sticky bars may cover
  const LIMIT = 15;

  const W = window.innerWidth;
  const H = window.innerHeight;
  const doc = document.documentElement;
  const box = (e) => e.getBoundingClientRect();
  // One getComputedStyle per element: the same ancestors are read for every descendant.
  const styles = new Map();
  const style = (e) => { let s = styles.get(e); if (!s) styles.set(e, (s = getComputedStyle(e))); return s; };
  const shownCache = new Map();
  const isShown = (e) => {
    const r = box(e);
    // A 1 px box is a screen-reader-only element (a skip link), not something on screen.
    if (r.width <= 1 || r.height <= 1) return false;
    if (e.checkVisibility) {
      // Also covers an ancestor with display none, visibility hidden or opacity 0 (a closed drawer).
      if (!e.checkVisibility({ opacityProperty: true, visibilityProperty: true })) return false;
    } else {
      for (let p = e; p; p = p.parentElement) {
        const cs = style(p);
        if (cs.display === "none" || cs.visibility === "hidden" || parseFloat(cs.opacity) === 0) return false;
      }
    }
    // Inert content cannot be used; aria-hidden with no size is a hidden holder (aria-hidden alone may still paint).
    if (e.closest("[inert]")) return false;
    for (let p = e.closest("[aria-hidden=true]"); p; p = p.parentElement?.closest("[aria-hidden=true]")) {
      const pr = box(p);
      if (pr.width <= 1 || pr.height <= 1) return false;
    }
    return true;
  };
  const shown = (e) => { let v = shownCache.get(e); if (v === undefined) shownCache.set(e, (v = isShown(e))); return v; };
  const name = (e) => {
    const id = e.id ? `#${e.id}` : "";
    const cls = typeof e.className === "string" && e.className.trim() ? "." + e.className.trim().split(/\s+/).slice(0, 2).join(".") : "";
    // <progress> and <meter> have a numeric value, so coerce before trimming.
    const label = String(e.getAttribute("aria-label") || e.innerText || e.value || "").trim().replace(/\s+/g, " ");
    return `${e.tagName.toLowerCase()}${id}${cls}${label ? ` "${label.slice(0, 32)}"` : ""}`;
  };
  const rect = (e) => {
    const r = box(e);
    return { x: Math.round(r.left), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height) };
  };
  const all = [...document.body.querySelectorAll("*")].filter((e) => !e.closest("svg") || e.tagName === "svg");

  // Scope: a root narrows the per-element checks; page scroll and bars always look at the whole page.
  const rootSelector = String(window.__mobileProbeRoot || "");
  let rootEl = document.body;
  let rootFound = true;
  if (rootSelector) {
    try { rootEl = document.querySelector(rootSelector); } catch { rootEl = null; }
    if (!rootEl) { rootEl = document.body; rootFound = false; }
  }
  const scoped = rootEl === document.body ? all : all.filter((e) => rootEl.contains(e));

  // Scrollers. An app often scrolls inside one container, not the document, so that container carries the page.
  const scrollsX = (e) => /(auto|scroll)/.test(style(e).overflowX) && e.scrollWidth > e.clientWidth + 1;
  const scrollsY = (e) => /(auto|scroll)/.test(style(e).overflowY) && e.scrollHeight > e.clientHeight + 1;
  const REGION = "[data-scroll-region], [role=region][aria-label], [role=region][aria-labelledby]";
  const scrollable = all.filter((e) => /(auto|scroll)/.test(style(e).overflowY) && shown(e) && !e.matches(REGION));
  let hook = [];
  try { hook = window.__mobileProbePageScroller ? [...document.querySelectorAll(window.__mobileProbePageScroller)] : []; } catch { /* bad selector: use the guess */ }
  let pageList = hook.length ? hook : scrollable.filter((e) => e.matches("main, [role=main]") || e.querySelector("main, [role=main], h1"));
  if (!pageList.length) {
    // No landmark inside any scroller: fall back to size, which cannot tell a tall wide table from an app shell.
    pageList = scrollable.filter((e) => { const r = box(e); return r.width >= W * 0.9 && r.height >= H * 0.5; });
  }
  const pageScrollers = new Set(pageList);
  const sideways = (s) => (s === doc
    ? Math.max(0, doc.scrollWidth - W)
    : /(auto|scroll)/.test(style(s).overflowX) ? Math.max(0, s.scrollWidth - s.clientWidth) : 0);
  const pageSideways = Math.max(0, ...[doc, ...pageScrollers].map((s) => (sideways(s) > 1 ? sideways(s) : 0)));
  const scrollers = [
    ...(doc.scrollHeight > doc.clientHeight + 1 || sideways(doc) > 1 ? [{ el: doc, page: true, scrollWidth: doc.scrollWidth, clientWidth: doc.clientWidth, scrollHeight: doc.scrollHeight, clientHeight: doc.clientHeight }] : []),
    ...all.filter((e) => shown(e) && (scrollsX(e) || scrollsY(e)))
      .map((e) => ({ el: e, page: pageScrollers.has(e), scrollWidth: e.scrollWidth, clientWidth: e.clientWidth, scrollHeight: e.scrollHeight, clientHeight: e.clientHeight })),
  ].sort((a, b) => Number(b.page) - Number(a.page));
  // A narrower region that scrolls sideways on purpose (a table, a diagram) may hold wide content; the page may not.
  const scrollRegions = all.filter((e) => shown(e) && scrollsX(e) && !pageScrollers.has(e))
    .map((e) => ({ el: name(e), named: e.hasAttribute("aria-label") || e.hasAttribute("aria-labelledby"), focusable: e.tabIndex >= 0 }));

  // Sideways overflow: for each element find its page scroller, and whether a region or a clipping ancestor decides.
  const classify = (e) => { // region:true means skip the element (a deliberate scroll region or a hidden holder)
    const r = box(e);
    let cut = null;
    for (let p = e.parentElement; p && p !== doc; p = p.parentElement) {
      if (p === document.body) break; // body overflow-x hidden is the hack to hide a wide child, not a clip to trust
      const ox = style(p).overflowX;
      if (!cut && (ox === "hidden" || ox === "clip")) {
        const pr = box(p);
        // A 1 px clipper is a screen-reader-only holder: what is inside is not on screen at all.
        if (pr.width <= 1 || pr.height <= 1) return { region: true };
        if (r.right > pr.right + 1 || r.left < pr.left - 1) cut = p;
      }
      if (pageScrollers.has(p)) return { home: p, cut };
      if (scrollsX(p)) return { region: true };
    }
    return { home: doc, cut };
  };
  const wide = [];
  const clippedSet = [];
  for (const e of all) {
    if (!shown(e) || style(e).position === "fixed") continue;
    const r = box(e);
    const c = classify(e);
    if (c.region) continue;
    const inRoot = scoped === all || rootEl.contains(e);
    if (c.cut) { if (inRoot) clippedSet.push({ e, by: c.cut }); continue; }
    let past = 0;
    if (c.home === doc) past = Math.max(r.right - W, -r.left);
    else { const x = r.left - box(c.home).left + c.home.scrollLeft; past = Math.max(x + r.width - c.home.clientWidth, -x); }
    if (past > 1) wide.push({ e, past, home: c.home });
  }
  // Report the outermost offenders: a child of a wide element is wide because of it.
  const outermost = (list) => { const set = new Set(list.map((o) => o.e)); return list.filter((o) => { for (let p = o.e.parentElement; p; p = p.parentElement) if (set.has(p)) return false; return true; }); };
  const overflow = outermost(wide).sort((a, b) => b.past - a.past)
    .map((o) => ({ el: o.e, ...rect(o.e), past: Math.round(o.past), ...(o.home === doc ? {} : { scroller: o.home }) }));
  const clipped = outermost(clippedSet).map((o) => ({ el: o.e, ...rect(o.e), by: o.by }));

  // Tap targets: a link inside running text is exempt (WCAG 2.5.8 inline exception).
  const TAPPABLE = "a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button], [role=link], [role=tab], [role=checkbox], [role=radio], [role=switch], [role=menuitem], [role=option], [tabindex]:not([tabindex='-1'])";
  // An outer element of this kind activates the same thing as the control inside it; a plain tabindex region does not.
  const CONTROL = "a[href], button, summary, label, [role=button], [role=link], [role=tab], [role=checkbox], [role=radio], [role=switch], [role=menuitem], [role=option]";
  // Inline only counts as prose when the parent holds real text besides its links, not a row of sibling links.
  const inline = (e) => {
    if (e.tagName !== "A" || style(e).display !== "inline" || !e.parentElement) return false;
    let text = e.parentElement.textContent;
    for (const a of e.parentElement.querySelectorAll("a")) text = text.replace(a.textContent, "");
    return text.replace(/\s+/g, " ").trim().length >= 20;
  };
  // A native modal dialog makes everything behind it inert, so only the top-most one is judged.
  let modal = null;
  try { modal = [...document.querySelectorAll("dialog:modal")].pop() || null; } catch { /* no :modal support */ }
  const tapScope = modal || rootEl;
  // A hidden native checkbox gives its hit area to the label around it (or the label[for]), which is what is measured.
  const hitArea = (e) => (e.matches("input[type=checkbox], input[type=radio]")
    ? e.closest("label") || (e.id ? document.querySelector(`label[for="${CSS.escape(e.id)}"]`) : null) || e : e);
  const tappable = [...tapScope.querySelectorAll(TAPPABLE)].filter((e) => !e.disabled).map(hitArea)
    .filter((e, i, list) => shown(e) && !inline(e) && list.indexOf(e) === i && !list.some((o) => o !== e && o.contains(e) && o.matches(CONTROL)));
  const targets = tappable.filter((e) => { const r = box(e); return r.width < MIN_TARGET || r.height < MIN_TARGET; })
    .map((e) => ({ el: e, ...rect(e) }));
  // Rectangle distance: 0 when the boxes touch or overlap, diagonal neighbours included.
  const dist = (a, b) => Math.hypot(Math.max(a.left - b.right, b.left - a.right, 0), Math.max(a.top - b.bottom, b.top - a.bottom, 0));
  // Only the part of a box that its clipping ancestors leave visible can overlap (a chip scrolled half out of its row does not).
  const visibleRect = (e, t, from = e) => {
    let [l, tp, r, b] = [t.left, t.top, t.right, t.bottom];
    for (let p = from; p && p !== document.body; p = p.parentElement) {
      const cs = style(p);
      if (cs.overflowX === "visible" && cs.overflowY === "visible") continue;
      const pr = box(p);
      [l, tp, r, b] = [Math.max(l, pr.left), Math.max(tp, pr.top), Math.min(r, pr.right), Math.min(b, pr.bottom)];
    }
    return r - l > 1 && b - tp > 1 ? { left: l, top: tp, right: r, bottom: b } : null;
  };
  const crowded = [];
  const overlaps = [];
  // A fixed or sticky bar slides over the content when it scrolls; only pairs inside the same layer are a fault.
  const layer = (e) => { for (let p = e; p && p !== doc; p = p.parentElement) if (/^(fixed|sticky)$/.test(style(p).position)) return true; return false; };
  for (let i = 0; i < tappable.length; i += 1) {
    for (let j = i + 1; j < tappable.length; j += 1) {
      const [x, y] = [tappable[i], tappable[j]];
      if (x.contains(y) || y.contains(x)) continue;
      const [a, b] = [box(x), box(y)];
      const d = dist(a, b);
      if (d >= MIN_GAP) continue;
      crowded.push({ a: x, b: y, gap: Math.round(d) });
      const [va, vb] = [visibleRect(x, a, x.parentElement), visibleRect(y, b, y.parentElement)];
      if (!va || !vb) continue;
      const ix = Math.min(va.right, vb.right) - Math.max(va.left, vb.left);
      const iy = Math.min(va.bottom, vb.bottom) - Math.max(va.top, vb.top);
      if (ix > 2 && iy > 2 && layer(x) === layer(y)) overlaps.push({ a: x, b: y, w: Math.round(ix), h: Math.round(iy) });
    }
  }

  // Text: every element that holds its own visible text.
  const ownNodes = (e) => [...e.childNodes].filter((n) => n.nodeType === 3 && /\S/.test(n.textContent));
  const texty = scoped.filter((e) => ownNodes(e).length && shown(e));
  const textRects = new Map(); // line boxes of the element's own text, not of its (wider) block box
  for (const e of texty) {
    const rects = [];
    for (const n of ownNodes(e)) {
      const range = document.createRange();
      range.selectNodeContents(n);
      for (const r of range.getClientRects()) if (r.width > 1 && r.height > 1) rects.push(r);
    }
    textRects.set(e, rects);
  }
  // Text running under a control it is not part of: the title that slides below a button at 320 px.
  const controlRects = tappable.map((c) => visibleRect(c, box(c), c.parentElement));
  // The label of a control that already overlaps another control is the same fault, not a second one.
  const hot = new Set(overlaps.flatMap((o) => [o.a, o.b]));
  for (const e of modal ? texty.filter((t) => modal.contains(t)) : texty) {
    for (let k = 0; k < tappable.length; k += 1) {
      const [c, cr] = [tappable[k], controlRects[k]];
      if (!cr || cr.right <= 0 || cr.left >= W || c.contains(e) || e.contains(c) || tappable.some((o) => hot.has(o) && o.contains(e))) continue;
      const hit = textRects.get(e).map((t) => visibleRect(e, t)).find((t) => t && t.right > 0 && t.left < W
        && Math.min(t.right, cr.right) - Math.max(t.left, cr.left) > 2 && Math.min(t.bottom, cr.bottom) - Math.max(t.top, cr.top) > 4);
      if (!hit || layer(e) !== layer(c)) continue;
      overlaps.push({ a: e, b: c, w: Math.round(Math.min(hit.right, cr.right) - Math.max(hit.left, cr.left)), h: Math.round(Math.min(hit.bottom, cr.bottom) - Math.max(hit.top, cr.top)) });
    }
  }

  const px = (e) => parseFloat(style(e).fontSize);
  const smallText = texty.filter((e) => px(e) < MIN_TEXT).map((e) => ({ el: e, px: px(e) }));
  const sizeCount = {};
  for (const e of texty) { const k = String(Math.round(px(e) * 10) / 10); sizeCount[k] = (sizeCount[k] || 0) + 1; }
  const textSizes = Object.fromEntries(Object.entries(sizeCount).sort((a, b) => a[0] - b[0]));
  // Running text is what people read for more than a glance. Its owner is the paragraph-like block, so a span inside a
  // long <p> counts by the paragraph; a short label or caption is secondary text with its own lower floor.
  const textLen = (e) => e.textContent.replace(/\s+/g, " ").trim().length;
  const BLOCK = "p, li, dd, td, blockquote, figcaption";
  const smallBody = [];
  const smallSecondary = [];
  const seenBlocks = new Set();
  for (const e of texty) {
    const size = px(e);
    if (size >= MIN_BODY) continue;
    const block = e.closest(BLOCK);
    if (block ? textLen(block) > 40 : textLen(e) > 40) {
      if (block && seenBlocks.has(block)) continue;
      if (block) seenBlocks.add(block);
      smallBody.push({ el: e, px: size });
    } else if (size >= MIN_TEXT && size < MIN_SECONDARY) smallSecondary.push({ el: e, px: size });
  }
  const smallInputs = [...rootEl.querySelectorAll("input:not([type=checkbox]):not([type=radio]):not([type=range]):not([type=hidden]), select, textarea, [contenteditable=true]")]
    .filter((e) => shown(e) && px(e) < MIN_INPUT)
    .map((e) => ({ el: e, px: px(e) }));

  // Left edges: where each text line starts. Many distinct x values mean nested padding ate the width.
  const edgeCount = {};
  for (const e of texty) {
    const r = textRects.get(e)[0];
    if (!r || r.top > H * 3) continue;
    const x = Math.round(r.left);
    edgeCount[x] = (edgeCount[x] || 0) + 1;
  }
  const edges = Object.entries(edgeCount).map(([x, n]) => ({ x: Number(x), n })).sort((a, b) => b.n - a.n).slice(0, 8);

  // Fixed and sticky bars: together they may cover only a small share of the height (the union, not the sum).
  const stuck = (e, cs) => {
    if (cs.position === "fixed") return true;
    // A sticky box covers content only while it sits on the edge it sticks to.
    let bound = { top: 0, bottom: H };
    for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) if (style(p).overflowY !== "visible") { bound = box(p); break; }
    const [t, b, r] = [parseFloat(cs.top), parseFloat(cs.bottom), box(e)];
    return (!isNaN(t) && Math.abs(r.top - (bound.top + t)) <= 1) || (!isNaN(b) && Math.abs(bound.bottom - b - r.bottom) <= 1);
  };
  const barEls = all.filter((e) => shown(e) && /^(fixed|sticky)$/.test(style(e).position) && stuck(e, style(e)))
    .map((e) => { const r = box(e); return { e, w: Math.min(r.right, W) - Math.max(r.left, 0), top: Math.max(r.top, 0), bottom: Math.min(r.bottom, H) }; })
    // A box covering the whole screen is an app shell or a backdrop, not a bar.
    .filter((b) => b.w > W * 0.5 && b.bottom - b.top > 1 && b.bottom - b.top <= H * 0.9);
  let covered = 0;
  let edge = 0;
  for (const b of [...barEls].sort((x, y) => x.top - y.top)) {
    covered += Math.max(0, b.bottom - Math.max(b.top, edge));
    edge = Math.max(edge, b.bottom);
  }
  const bars = barEls.map((b) => ({ el: b.e, position: style(b.e).position, h: Math.round(b.bottom - b.top), top: Math.round(b.top) }));
  const barsShare = Math.round((covered / H) * 100) / 100;

  // A fixed or stuck element is positioned against the viewport, so it can cross the edge without widening the page.
  const vw = window.visualViewport?.width || W;
  const vh = window.visualViewport?.height || H;
  const offscreen = all.filter((e) => shown(e) && /^(fixed|sticky)$/.test(style(e).position) && stuck(e, style(e)))
    .map((e) => ({ e, r: box(e) }))
    // Wholly outside is a closed drawer; crossing the edge is the fault.
    .filter(({ r }) => r.right > 0 && r.left < vw && r.bottom > 0 && r.top < vh && (r.right > vw + 1 || r.left < -1 || r.bottom > vh + 1 || r.top < -1))
    .map(({ e, r }) => ({ e, past: Math.max(r.right - vw, -r.left, r.bottom - vh, -r.top) }));
  const offscreenFixed = outermost(offscreen).map((o) => ({ el: o.e, ...rect(o.e), past: Math.round(o.past) }));

  // Truncated text: an ellipsis or a clamp that actually cut something.
  const truncated = texty.filter((e) => {
    const cs = style(e);
    // overflow hidden on a box that holds the text cuts it with or without an ellipsis
    return (/^(hidden|clip)$/.test(cs.overflowX) && e.scrollWidth > e.clientWidth + 1) || (cs.webkitLineClamp !== "none" && e.scrollHeight > e.clientHeight + 1);
  }).map((e) => ({ el: e }));

  // 100vh on a phone ignores the browser toolbars; dvh/svh follow them. Same-origin sheets only.
  const vhRules = [];
  const topLevelParts = (sel) => { // a comma inside :is(...) or [...] does not split the list
    const parts = [];
    let depth = 0;
    let cur = "";
    for (const ch of sel) {
      if ("([".includes(ch)) depth += 1;
      else if (")]".includes(ch)) depth -= 1;
      if (ch === "," && depth === 0) { parts.push(cur); cur = ""; } else cur += ch;
    }
    return [...parts, cur];
  };
  const matchesNow = (sel) => topLevelParts(sel).some((part) => {
    try { return !!document.querySelector(part.replace(/::[a-z-]+(\(.*\))?\s*$/i, "").trim() || "x-none"); } catch { return false; }
  });
  // Last declaration wins per selector and property: a later dvh/svh rule is the fix, a later vh rule brings the fault back.
  const vhState = new Map();
  const walk = (list) => {
    for (const r of list) {
      try {
        // A rule inside a media or supports block that does not match now never applies.
        if (r.media && !matchMedia(r.media.mediaText).matches) continue;
        if (r.conditionText !== undefined && r.constructor.name === "CSSSupportsRule" && !CSS.supports(r.conditionText)) continue;
        if (r.selectorText && r.style) {
          for (const prop of r.style) {
            const v = r.style.getPropertyValue(prop);
            if (/\d[ds]vh\b/.test(v)) vhState.set(`${r.selectorText}|${prop}`, false);
            else if (/\b100l?vh\b/.test(v)) vhState.set(`${r.selectorText}|${prop}`, true); // lvh is vh: both ignore the toolbars
          }
        }
        if (r.cssRules) walk(r.cssRules);
      } catch { /* one odd rule must not hide the rest */ }
    }
  };
  for (const sheet of [...document.styleSheets, ...(document.adoptedStyleSheets || [])]) {
    try { if (!sheet.disabled && (!sheet.media?.mediaText || matchMedia(sheet.media.mediaText).matches)) walk(sheet.cssRules); } catch { /* cross-origin sheet */ }
  }

  for (const [key, fault] of vhState) {
    const sel = key.slice(0, key.lastIndexOf("|"));
    if (fault && matchesNow(sel)) vhRules.push(sel.slice(0, 60));
  }

  const viewportMeta = document.querySelector("meta[name=viewport]")?.content || "";
  const directives = {};
  for (const part of viewportMeta.split(/[,;]/)) {
    const [k, ...v] = part.split("=");
    if (k.trim() && v.length) directives[k.trim().toLowerCase()] = v.join("=").trim().toLowerCase();
  }
  const meta = {
    viewport: viewportMeta,
    // Zoom is blocked by user-scalable=no/0 or by a maximum scale under 2 (WCAG 1.4.4 needs 200 %).
    zoomBlocked: ["no", "0"].includes(directives["user-scalable"]) || parseFloat(directives["maximum-scale"]) < 2,
    fitCover: directives["viewport-fit"] === "cover",
  };

  const counts = {
    pageScrollsSideways: Math.round(pageSideways),
    overflow: overflow.length,
    clipped: clipped.length,
    unnamedScrollRegions: scrollRegions.filter((r) => !r.named || !r.focusable).length,
    smallTargets: targets.length,
    crowdedTargets: crowded.length,
    overlaps: overlaps.length,
    smallText: smallText.length,
    smallBody: smallBody.length,
    smallSecondary: smallSecondary.length,
    offscreenFixed: offscreenFixed.length,
    smallInputs: smallInputs.length,
    distinctEdges: Object.keys(edgeCount).length,
    barsOverShare: barsShare > MAX_BARS_SHARE ? barsShare : 0,
    truncated: truncated.length,
    vhRules: new Set(vhRules).size,
    zoomBlocked: meta.zoomBlocked ? 1 : 0,
  };
  // Elements become readable names only for the lists that are printed.
  const named = (list) => list.slice(0, LIMIT).map((o) => Object.fromEntries(Object.entries(o).map(([k, v]) => [k, v instanceof Element ? name(v) : v])));
  return JSON.stringify({
    viewport: { w: W, h: H, dpr: devicePixelRatio, coarse: matchMedia("(any-pointer: coarse)").matches },
    root: { selector: rootSelector, found: rootFound, modal: modal ? name(modal) : null },
    counts,
    overflow: named(overflow),
    clipped: named(clipped),
    scrollers: named(scrollers),
    scrollRegions: scrollRegions.slice(0, LIMIT),
    targets: named(targets),
    crowded: named(crowded),
    overlaps: named(overlaps),
    smallText: named(smallText),
    smallBody: named(smallBody),
    smallSecondary: named(smallSecondary),
    offscreenFixed: named(offscreenFixed),
    textSizes,
    smallInputs: named(smallInputs),
    edges,
    bars: { share: barsShare, list: named(bars) },
    truncated: named(truncated),
    vhRules: [...new Set(vhRules)].slice(0, LIMIT),
    meta,
  }, null, 1);
})();
