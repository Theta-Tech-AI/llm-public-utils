// mobile-probe.js: measure the phone-layout faults a screenshot hides, on the page as it is rendered now.
// Run it in the page, for example:
//   agent-browser --session <s> eval "$(cat .agents/skills/mobile-friendly/scripts/mobile-probe.js)"
// The default root is the whole body, so the frame's own controls (the header) are judged. To judge one page and not the
// shared frame, set a root first (it limits targets, text, edges, overlaps, escapes, clipped and the checks below;
// page sideways scroll, overflow, bars and vhRules stay global; set it to '' to clear it). Run both: a page root such as
// `main` hides the header's own crowding.
//   agent-browser --session <s> eval "window.__mobileProbeRoot='main'; $(cat .agents/skills/mobile-friendly/scripts/mobile-probe.js)"
// It returns JSON with these keys. Each list holds the worst offenders (at most LIMIT); `counts` holds the full totals.
//   viewport        {w, h, dpr, coarse}
//   root            {selector, found}: the scope in use
//   counts          one number per fault below, 0 is clean (distinctEdges and barsOverShare are a count and a share)
//   overflow        outermost elements wider than a page scroller (the document or an app-shell scroll container)
//   clipped         elements cut by an overflow hidden/clip ancestor (content the user cannot reach; judge each one).
//                   Not judged: aria-hidden decoration, pan regions (touch-action: none)
//   scrollers       every scroll container found; page:true marks the ones that carry the page. Scroll the inner
//                   page scroller to shoot below the fold: a full-page screenshot only shows its first screen
//   scrollRegions   narrower regions that scroll sideways on purpose (they need a name and keyboard focus)
//   targets         controls whose real hit area (see Method) is under MIN_TARGET px; hitW/hitH is the measured size.
//                   A control is a real action: button, a[href], input, select, textarea, summary or a role (button, link,
//                   tab, checkbox, radio, switch, menuitem, option). A tabindex alone (a tooltip trigger) is not one.
//   sampling        {controls, sampled, covered, unsampled, points, incomplete, unsampledList}: which controls could be asked;
//                   unsampledList is {above, below, side, budget, partial}; partial = cut by its scroller's edge or under a
//                   fixed/sticky bar at this stop (it is asked at the stop where it is whole); incomplete names checks the deadline cut
//   crowded         controls whose hit areas come closer than MIN_GAP px (gap under 7.5 px, unrounded; overlap counts as 0),
//                   or where a tap in the MIN_TARGET square around one control's centre reaches the other. A pair where
//                   one box holds the other, or exactly one has a fixed or sticky ancestor, is not judged
//   overlaps        text over a control it is not inside, or two controls whose boxes cross (same exemptions as crowded)
//   escapes         text or a box that runs past the card or panel around it (a border, background or shadow) by over 2 px, any
//                   side. Not judged: visually hidden or aria-hidden elements, content inside a scroller or role=region,
//                   an element that is its own container
//   smallText       text under MIN_TEXT px
//   smallBody       running text under MIN_BODY px: text in a p/li/dd/td/blockquote/figcaption whose whole text is over
//                   40 characters, or a div whose own text is over 40 characters. A pill or badge label from 13 px up is not body
//   smallSecondary  short text (labels, captions) from MIN_TEXT up to MIN_SECONDARY px
//   textSizes       histogram {px: number of text elements}
//   smallInputs     form fields under MIN_INPUT px (iOS Safari zooms on focus)
//   letterColumn    text over 5 lines tall whose lines are all under 2 characters wide (a value broken one letter per line)
//   splitWords      table cells that break a word of up to 24 characters across lines ("Standar/d")
//   unnamedControls controls with no accessible name (an icon-only button whose label is hidden on phones)
//   repeatedHeading the same heading text twice on the first screen (page title and card heading)
//   squeezedScroller a vertical scroller under 40 % of the screen height with much more content, while the document does not scroll
//   edges           histogram of where text lines start (many distinct x means nested padding ate the width)
//   bars            fixed/sticky bars: share = union of the viewport height they cover, list = each bar
//   truncated       text cut by an ellipsis, a line clamp, or an overflow-hidden box of its own (even with no ellipsis)
//   offscreenFixed  fixed or stuck elements that cross the viewport edge (they never widen the page, so overflow misses them)
//   vhRules         CSS rules that use 100vh without a dvh/svh/lvh twin, on elements that exist now
//   meta            {viewport, zoomBlocked, fitCover}
//   scroller        the page scroller whose metrics follow: the innermost page scroller that really scrolls, or "document"
//   coverage        {controls, seen, unseen, unseenList} over ALL controls in scope, across runs: each run adds the controls it
//                   sampled to window.__mobileProbeSeen (a WeakSet); set it to null to reset. Scroll, run, repeat until
//                   scrollTop + clientHeight >= scrollHeight; then coverage.unseen holds only budget, side and covered cases
//   scrollTop, scrollHeight, clientHeight   of that scroller: accumulate coverage across scroll stops until the bottom
//   ms              run time of the probe in milliseconds
// Method: tap size, crowding and overlaps are MEASURED, not read from boxes. For each control that touches the viewport
// the probe calls document.elementFromPoint on a grid (GRID px, out to REACH px beyond each edge) and keeps the points
// where the top element is the control or one of its descendants; the hit area is their bounding box, with each edge
// refined to the pixel. So a hit pad (::after) counts, a pad clipped by overflow does not, and a control that a sticky
// bar or a modal covers (under half of its box reachable) is skipped and counted in sampling.covered. A text line
// overlaps a control only when a tap inside the line's visible rect, over the control's painted box, reaches the
// control. Containment compares Range rects (text) and boxes with the nearest container ancestor (border, background
// or shadow); an ancestor with its own overflow, an out-of-flow element, or a region that scrolls sideways on purpose
// is not judged (clipped and scrollRegions own those). Works at any width, desktop included.
// Limits: only the viewport can be asked, so controls below the fold are listed in sampling.unsampledList and not
// counted: scroll the page scroller and run again. Probe at scroll top: text that scrolled under a sticky bar's
// control is reported as an overlap. A stretched link (a pad over a whole card) is crowded with its neighbours.
// Hit sampling ends after BUDGET_MS; the remaining controls are unsampled. Target sizes carry 1 px of slack.
// Heuristics that cannot be exact have a hook (set it in the same eval, before the file):
//   window.__mobileProbePageScroller = '<selector list>'  the scroll containers that carry the page (replaces the guess)
//   [data-scroll-region] or role=region with a name        an intentional sideways scroll region (never a page scroller)
// There is no hook for targets: the browser decides what a tap reaches.
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
  const GRID = 4; // px between hit samples
  const REACH = 22; // px sampled beyond each edge of a control: a hit pad can grow a target that far
  const BUDGET_MS = 1000; // after it, sampling stops and the cut checks are named in sampling.incomplete
  const LIMIT = 15;

  const t0 = performance.now();
  const late = () => performance.now() - t0 > BUDGET_MS; // one deadline for sampling, crowding and overlaps
  const incomplete = new Set(); // the checks the deadline cut short

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
  const all = [...document.body.querySelectorAll("*")];
  const decor = (e) => !!e.closest("[aria-hidden=true]"); // aria-hidden decoration is not content to judge
  const pinnedCache = new Map();
  const pinned = (e) => { // the element or an ancestor is fixed or sticky
    if (!e || e === document.body) return false;
    let v = pinnedCache.get(e);
    if (v === undefined) { v = /^(fixed|sticky)$/.test(style(e).position) || pinned(e.parentElement); pinnedCache.set(e, v); }
    return v;
  };

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
  // A pan viewport (a map, a graph canvas) moves its content on purpose: touch-action none on the clipper or below it.
  const panned = (e, by) => { for (let p = e; p; p = p.parentElement) { if (style(p).touchAction === "none") return true; if (p === by) break; } return false; };
  const wide = [];
  const clippedSet = [];
  for (const e of all) {
    if (!shown(e) || style(e).position === "fixed") continue;
    const r = box(e);
    const c = classify(e);
    if (c.region) continue;
    const inRoot = scoped === all || rootEl.contains(e);
    if (c.cut) { if (inRoot && !decor(e) && !panned(e, c.cut)) clippedSet.push({ e, by: c.cut }); continue; }
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
  const TAPPABLE = "a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button], [role=link], [role=tab], [role=checkbox], [role=radio], [role=switch], [role=menuitem], [role=option]";
  // An outer element of this kind activates the same thing as the control inside it.
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
  // Only the part of a box that its clipping ancestors leave visible can be seen or tapped.
  const visibleRect = (e, t) => {
    let [l, tp, r, b] = [t.left, t.top, t.right, t.bottom];
    for (let p = e; p && p !== document.body; p = p.parentElement) {
      const cs = style(p);
      if (cs.overflowX === "visible" && cs.overflowY === "visible") continue;
      const pr = box(p);
      [l, tp, r, b] = [Math.max(l, pr.left), Math.max(tp, pr.top), Math.min(r, pr.right), Math.min(b, pr.bottom)];
    }
    return r - l > 1 && b - tp > 1 ? { left: l, top: tp, right: r, bottom: b } : null;
  };

  // Real hit areas: ask the browser which element a tap at a point reaches. That counts hit pads, and it ignores a
  // control that a sticky bar or a modal covers, with no guess about boxes. Only the viewport can be asked.
  const tapIndex = new Set(tappable);
  const hitCache = new Map();
  let samples = 0;
  const hitAt = (x, y) => {
    x = Math.round(x); y = Math.round(y);
    if (x < 0 || y < 0 || x >= W || y >= H) return null;
    const k = x * 8192 + y;
    let h = hitCache.get(k);
    if (h === undefined) { samples += 1; h = document.elementFromPoint(x, y); hitCache.set(k, h); }
    return h;
  };
  const ownerCache = new Map();
  const ownerOf = (h) => { // the control a tap on h activates, or null
    if (!h) return null;
    let o = ownerCache.get(h);
    if (o === undefined) {
      o = null;
      for (let p = h.matches("input[type=checkbox], input[type=radio]") ? hitArea(h) : h; p; p = p.parentElement) if (tapIndex.has(p)) { o = p; break; }
      ownerCache.set(h, o);
    }
    return o;
  };
  // Sample coordinates along one axis: 1 px inside each edge, every GRID px out to REACH beyond it, coarser across a long span.
  const axis = (a, b) => {
    const out = [];
    for (let v = a - 1; v >= a - REACH; v -= GRID) out.push(v);
    const step = Math.max(GRID, (b - a) / 10);
    for (let v = a + 1; v < b - 1; v += step) out.push(v);
    out.push(b - 1);
    for (let v = b + 1; v <= b + REACH; v += GRID) out.push(v);
    return [...new Set(out.map(Math.round))].sort((p, q) => p - q);
  };
  // Binary search for the exact pixel where the control's hit area ends, between a hit and the miss next to it.
  const refine = (hit, miss, isHit) => {
    while (Math.abs(hit - miss) > 1) { const mid = Math.round((hit + miss) / 2); if (isHit(mid)) hit = mid; else miss = mid; }
    return hit;
  };
  // Returns {eff, near} for a control, or {state} when it cannot be judged: "offscreen" or "covered".
  const measure = (c, r) => {
    const xs = axis(r.left, r.right);
    const ys = axis(r.top, r.bottom);
    const cx = (r.left + r.right) / 2;
    const cy = (r.top + r.bottom) / 2;
    const ext = { l: null, r: null, t: null, b: null };
    const near = new Set(); // other controls a tap in the 44 px square around the centre reaches
    let inside = 0;
    let insideHits = 0;
    for (const y of ys) {
      for (const x of xs) {
        const h = hitAt(x, y);
        if (!h) continue;
        const inBox = x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
        if (inBox) inside += 1;
        const o = ownerOf(h);
        if (o === c) {
          if (inBox) insideHits += 1;
          if (!ext.l || x < ext.l.x) ext.l = { x, y };
          if (!ext.r || x > ext.r.x) ext.r = { x, y };
          if (!ext.t || y < ext.t.y) ext.t = { x, y };
          if (!ext.b || y > ext.b.y) ext.b = { x, y };
        } else if (o && Math.abs(x - cx) <= MIN_TARGET / 2 && Math.abs(y - cy) <= MIN_TARGET / 2 && !o.contains(c) && !c.contains(o)) near.add(o);
      }
    }
    if (!inside) return { state: "offscreen" };
    if (insideHits / inside < 0.5) return { state: "covered" };
    const isOwn = (x, y) => ownerOf(hitAt(x, y)) === c;
    const edge = (list, p, dir, horizontal) => { // dir -1 looks outward on the low side, +1 on the high side
      const v = horizontal ? p.x : p.y;
      const next = list[list.indexOf(v) + dir];
      if (next === undefined) return v; // the sample sits on the viewport edge
      return refine(v, next, (m) => (horizontal ? isOwn(m, p.y) : isOwn(p.x, m)));
    };
    const eff = {
      left: edge(xs, ext.l, -1, true), right: edge(xs, ext.r, 1, true) + 1,
      top: edge(ys, ext.t, -1, false), bottom: edge(ys, ext.b, 1, false) + 1,
    };
    // A side that leaves the viewport cannot be asked: take the box there.
    if (r.left < 0) eff.left = r.left;
    if (r.right > W) eff.right = r.right;
    if (r.top < 0) eff.top = r.top;
    if (r.bottom > H) eff.bottom = r.bottom;
    return { eff: { ...eff, width: eff.right - eff.left, height: eff.bottom - eff.top }, near };
  };
  const partial = (c, r) => {
    const v = visibleRect(c, r);
    if (!v || v.right - v.left < r.width - 1 || v.bottom - v.top < r.height - 1) return true;
    if (pinned(c)) return false;
    return barEls.some((b) => {
      if (b.e.contains(c)) return false;
      const br = box(b.e);
      return Math.min(r.right, br.right) - Math.max(r.left, br.left) > r.width * 0.5 && Math.min(r.bottom, br.bottom) - Math.max(r.top, br.top) > 1;
    });
  };
  const unsampled = [];
  const coveredList = [];
  const hit = []; // {c, r, eff, near}: the controls that could be asked
  for (const c of tappable) {
    const r = box(c);
    // above / below / side: outside the viewport (scroll and run again); budget: in view, cut by the deadline
    const where = r.bottom <= 0 ? "above" : r.top >= H ? "below" : r.right <= 0 || r.left >= W ? "side" : "";
    if (where) { unsampled.push({ el: c, ...rect(c), where }); continue; }
    if (late()) { unsampled.push({ el: c, ...rect(c), where: "budget" }); incomplete.add("targets"); continue; }
    // A control cut by its scroller's edge or half under a bar shows a hit area smaller than its own: it is asked at the stop where it is whole.
    if (partial(c, r)) { unsampled.push({ el: c, ...rect(c), where: "partial" }); continue; }
    const m = measure(c, r);
    if (m.state === "covered") coveredList.push({ el: c, ...rect(c) });
    else if (m.state) unsampled.push({ el: c, ...rect(c), where: "below" });
    else hit.push({ c, r, ...m });
  }
  // 1 px of slack: the sampling edge is a pixel, a box edge may be fractional.
  const targets = hit.filter((o) => o.eff.width < MIN_TARGET - 1 || o.eff.height < MIN_TARGET - 1)
    .map((o) => ({ el: o.c, ...rect(o.c), hitW: Math.round(o.eff.width), hitH: Math.round(o.eff.height) }));
  // Rectangle distance: 0 when the areas touch or overlap, diagonal neighbours included.
  // The sampled edge is a whole pixel: where it is within 1 px of the control's own box, use the box, so an 8.0 px gap stays 8.0.
  const snap = (o) => {
    const near = (v, w) => (Math.abs(v - w) <= 1 ? w : v);
    return { left: near(o.eff.left, o.r.left), right: near(o.eff.right, o.r.right), top: near(o.eff.top, o.r.top), bottom: near(o.eff.bottom, o.r.bottom) };
  };
  const inside = (a, b) => a.left >= b.left - 1 && a.right <= b.right + 1 && a.top >= b.top - 1 && a.bottom <= b.bottom + 1;
  const dist = (a, b) => Math.hypot(Math.max(a.left - b.right, b.left - a.right, 0), Math.max(a.top - b.bottom, b.top - a.bottom, 0));
  const crowded = [];
  const overlaps = [];
  for (let i = 0; i < hit.length; i += 1) {
    for (let j = i + 1; j < hit.length; j += 1) {
      const [x, y] = [hit[i], hit[j]];
      if (x.c.contains(y.c) || y.c.contains(x.c)) continue;
      // One box inside the other is a part of one widget (an icon in its own input); one control under a sticky or fixed
      // bar and the other not is scrolled content under the bar, judged at the stop where it is clear.
      if (inside(x.r, y.r) || inside(y.r, x.r) || pinned(x.c) !== pinned(y.c)) continue;
      const d = dist(snap(x), snap(y));
      if (d >= MIN_GAP - 0.5 && !x.near.has(y.c) && !y.near.has(x.c)) continue;
      crowded.push({ a: x.c, b: y.c, gap: Math.round(d * 10) / 10 });
      // Two painted boxes that cross: a tap inside the crossing reaches one of them (not a bar or a modal on top).
      const [lx, rx] = [Math.max(x.r.left, y.r.left), Math.min(x.r.right, y.r.right)];
      const [ty, by] = [Math.max(x.r.top, y.r.top), Math.min(x.r.bottom, y.r.bottom)];
      if (rx - lx <= 2 || by - ty <= 2) continue;
      if (late()) { incomplete.add("overlaps"); continue; }
      let seen = false;
      for (const fx of [0.2, 0.5, 0.8]) for (const fy of [0.2, 0.5, 0.8]) {
        const o = ownerOf(hitAt(lx + (rx - lx) * fx, ty + (by - ty) * fy));
        if (o === x.c || o === y.c) seen = true;
      }
      if (seen) overlaps.push({ a: x.c, b: y.c, w: Math.round(rx - lx), h: Math.round(by - ty) });
    }
  }

  // Text: every element that holds its own visible text.
  const ownNodes = (e) => [...e.childNodes].filter((n) => n.nodeType === 3 && /\S/.test(n.textContent));
  // A modal dialog can sit outside the root; its text must be judged against its own controls.
  const textPool = modal ? [...new Set([...scoped, ...all.filter((e) => modal.contains(e))])] : scoped;
  const texty = textPool.filter((e) => ownNodes(e).length && shown(e));
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
  // Text under a control it is not part of: the title that slides below a button at 320 px. A text line overlaps a
  // control only when a tap inside the visible line, over the control's painted box, reaches the control.
  // The label of a control that already overlaps another control is the same fault, not a second one.
  const hot = new Set(overlaps.flatMap((o) => [o.a, o.b]));
  for (const e of modal ? texty.filter((t) => modal.contains(t)) : texty) {
    for (const t of textRects.get(e)) {
      if (t.bottom <= 0 || t.top >= H || t.right <= 0 || t.left >= W) continue;
      const vt = visibleRect(e, t);
      if (!vt) continue;
      for (const { c, r } of hit) {
        if (late()) { incomplete.add("overlaps"); break; }
        if (c.contains(e) || e.contains(c) || pinned(e) !== pinned(c) || [...hot].some((o) => o.contains(e))) continue;
        const [l, rt] = [Math.max(vt.left, r.left), Math.min(vt.right, r.right)];
        const [tp, bt] = [Math.max(vt.top, r.top), Math.min(vt.bottom, r.bottom)];
        if (rt - l <= 2 || bt - tp <= 4) continue;
        let n = 0;
        for (let x = l + 1; x < rt; x += GRID) for (const f of [0.25, 0.5, 0.75]) if (ownerOf(hitAt(x, tp + (bt - tp) * f)) === c) n += 1;
        if (n >= 2) overlaps.push({ a: e, b: c, w: Math.round(rt - l), h: Math.round(bt - tp) });
      }
    }
  }

  // Containment: painted text or a box that runs past the card or panel around it. A container is the nearest
  // ancestor with a visible border, background or shadow; an ancestor with its own overflow decides first (a clip
  // is `clipped`, a scroll is on purpose), and so does an out-of-flow box (a badge, a tooltip).
  const clear = (c) => c === "transparent" || /(rgba|hsla)\(.*,\s*0\)$/.test(c) || /\/\s*0(\.0+)?\)$/.test(c);
  const chrome = (cs) => cs.boxShadow !== "none" || cs.backgroundImage !== "none" || !clear(cs.backgroundColor)
    || ["Top", "Right", "Bottom", "Left"].some((s) => parseFloat(cs[`border${s}Width`]) > 0 && cs[`border${s}Style`] !== "none" && !clear(cs[`border${s}Color`]));
  const selfHolder = (e) => { const cs = style(e); return cs.overflowX === "visible" && cs.overflowY === "visible" && chrome(cs); };
  const holders = new Map();
  const holderOf = (e) => {
    let h = holders.get(e);
    if (h !== undefined) return h;
    const p = e.parentElement;
    if (!p || p === document.body || p === doc) h = false;
    else {
      const cs = style(p);
      if (cs.overflowX !== "visible" || cs.overflowY !== "visible") h = false;
      else if (chrome(cs)) h = p;
      else if (/^(absolute|fixed)$/.test(cs.position)) h = false;
      else h = holderOf(p);
    }
    holders.set(e, h);
    return h;
  };
  const regions = new Map();
  const inRegion = (e) => { // below a region that scrolls sideways on purpose
    if (!e || e === doc) return false;
    let v = regions.get(e);
    if (v === undefined) { v = (scrollsX(e) && !pageScrollers.has(e)) || inRegion(e.parentElement); regions.set(e, v); }
    return v;
  };
  // Content inside a scroller (or a named region) is reached by scrolling, so it does not spill; the page scrollers are not such regions.
  const inScroll = (e) => { for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) if (!pageScrollers.has(p) && (/(auto|scroll)/.test(style(p).overflowX + style(p).overflowY) || p.getAttribute("role") === "region")) return true; return false; };
  const hiddenVisually = (e) => { const cs = style(e); const r = box(e); return /inset\(50%\)/.test(cs.clipPath) || (cs.clip && cs.clip !== "auto" && r.width <= 1) || (r.width <= 1 && r.height <= 1); };
  const escaping = [];
  for (const e of scoped) {
    if (!shown(e) || /^(absolute|fixed)$/.test(style(e).position)) continue;
    if (inRegion(e.parentElement) || inScroll(e) || decor(e) || hiddenVisually(e)) continue;
    // Text is judged against the element itself when it is the painted container, else against the one around it.
    const outer = holderOf(e);
    const own = textRects.has(e) ? (selfHolder(e) ? e : outer) : null;
    for (const [c, rs] of [[own, textRects.get(e)], [outer, [box(e)]]]) {
      if (!c || !rs || c === e) continue; // a box is not its own container
      const cr = box(c);
      const past = Math.max(0, ...rs.map((r) => Math.max(r.right - cr.right, cr.left - r.left, r.bottom - cr.bottom, cr.top - r.top)));
      const prev = escaping.find((o) => o.e === e);
      // Up to 2 px is glyph overhang (negative letter-spacing, gradient text), not a spill.
      if (past > 2 && !prev) escaping.push({ e, past, c });
      else if (past > 2 && past > prev.past) Object.assign(prev, { past, c });
    }
  }
  const escapes = outermost(escaping).sort((a, b) => b.past - a.past)
    .map((o) => ({ el: o.e, ...rect(o.e), past: Math.round(o.past), container: o.c }));

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
    // Body is a text block, or the own text of a plain div; a pill or a badge label from 13 px up is a label, not body.
    const plain = e.tagName === "DIV" && !(size >= MIN_SECONDARY && chrome(style(e)));
    if (block ? textLen(block) > 40 : plain && textLen(e) > 40) {
      if (block && seenBlocks.has(block)) continue;
      if (block) seenBlocks.add(block);
      smallBody.push({ el: e, px: size });
    } else if (size >= MIN_TEXT && size < MIN_SECONDARY) smallSecondary.push({ el: e, px: size });
  }
  const smallInputs = [...rootEl.querySelectorAll("input:not([type=checkbox]):not([type=radio]):not([type=range]):not([type=hidden]), select, textarea, [contenteditable=true]")]
    .filter((e) => shown(e) && px(e) < MIN_INPUT)
    .map((e) => ({ el: e, px: px(e) }));

  // A value broken one letter per line: more than 5 lines, none wider than 2 characters of its font size.
  const letterColumn = texty.filter((e) => {
    const rs = textRects.get(e);
    return rs.length > 5 && Math.max(...rs.map((r) => r.width)) < 2 * px(e);
  }).map((e) => ({ el: e, ...rect(e) }));
  // A table cell that breaks inside a word (an `overflow-wrap: anywhere` cell shrinks to one letter): a word of up to 24
  // characters whose range has more than one line box. A longer token (a hash, a URL) is broken on purpose.
  const splitWords = [];
  for (const cell of scoped.filter((e) => /^(TD|TH)$/.test(e.tagName) && shown(e))) {
    const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
    let split = null;
    for (let n = walker.nextNode(); n && !split; n = walker.nextNode()) {
      for (const m of n.textContent.matchAll(/\S{2,24}/g)) {
        const range = document.createRange();
        range.setStart(n, m.index);
        range.setEnd(n, m.index + m[0].length);
        if (new Set([...range.getClientRects()].filter((r) => r.width > 1).map((r) => Math.round(r.top))).size > 1) { split = m[0]; break; }
      }
    }
    if (split) splitWords.push({ el: cell, word: split, wrap: style(cell).overflowWrap });
  }
  // A control with no accessible name: no label, no visible text (innerText skips a label hidden on phones), no title, no image alt.
  const nameOf = (e) => {
    const ids = (e.getAttribute("aria-labelledby") || "").split(/\s+/).map((id) => document.getElementById(id)?.textContent || "").join(" ");
    const labels = e.labels ? [...e.labels].map((l) => l.innerText).join(" ") : "";
    const alt = [...e.querySelectorAll("img[alt], svg title")].map((i) => i.getAttribute("alt") || i.textContent).join(" ");
    return [e.getAttribute("aria-label"), ids, e.innerText, labels, e.title, alt, e.matches("input[type=button], input[type=submit]") ? e.value : ""].join(" ").trim();
  };
  const unnamedControls = tappable.filter((c) => !nameOf(c.matches("label") ? (c.querySelector("input") || c) : c)).map((c) => ({ el: c, ...rect(c) }));
  // The same heading text twice on the first screen (a page title and the card heading under it).
  const headingCount = {};
  const repeatedHeading = [];
  for (const e of scoped.filter((x) => x.matches("h1, h2, h3, h4, h5, h6, [role=heading]") && shown(x))) {
    const r = box(e);
    if (r.bottom <= 0 || r.top >= H) continue;
    const k = (e.innerText || "").replace(/\s+/g, " ").trim().toLowerCase();
    if (!k) continue;
    headingCount[k] = (headingCount[k] || 0) + 1;
    if (headingCount[k] === 2) repeatedHeading.push({ el: e, text: k.slice(0, 40) });
  }
  // A vertical scroller under 40 % of the screen height with much more content, while the document itself does not scroll
  // (a list squeezed under a hero or a fixed header).
  const squeezedScroller = doc.scrollHeight > doc.clientHeight + 1 ? [] : all.filter((e) => {
    if (!shown(e) || !scrollsY(e) || e.matches("textarea, select, pre")) return false;
    const r = box(e);
    return r.top < H && r.bottom > 0 && e.clientWidth >= W * 0.5 && e.clientHeight < H * 0.4 && e.scrollHeight > e.clientHeight * 1.5;
  }).map((e) => ({ el: e, ...rect(e), clientHeight: e.clientHeight, scrollHeight: e.scrollHeight }));

  // Left edges: where each text line starts. Many distinct x values mean nested padding ate the width.
  const edgeCount = {};
  for (const e of texty) {
    const r = textRects.get(e)[0];
    if (!r || r.top > H * 3) continue;
    const x = Math.round(r.left);
    edgeCount[x] = (edgeCount[x] || 0) + 1;
  }
  const edges = Object.entries(edgeCount).map(([x, n]) => ({ x: Number(x), n })).sort((a, b) => b.n - a.n).slice(0, 8);

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
  // Last declaration wins per selector and property: any later non-vh value (dvh, svh, auto) is the fix, a later vh brings the fault back.
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
            const important = r.style.getPropertyPriority(prop) === "important";
            const key = `${r.selectorText}|${prop}`;
            // A later normal declaration cannot replace an !important one.
            if (vhState.get(key)?.important && !important) continue;
            if (/\b100l?vh\b/.test(v) && !/\d[ds]vh\b/.test(v)) vhState.set(key, { fault: true, important }); // lvh is vh: both ignore the toolbars
            else if (vhState.has(key) || /\d[ds]vh\b/.test(v)) vhState.set(key, { fault: false, important }); // any later non-vh value replaces it
          }
        }
        if (r.cssRules) walk(r.cssRules);
      } catch { /* one odd rule must not hide the rest */ }
    }
  };
  for (const sheet of [...document.styleSheets, ...(document.adoptedStyleSheets || [])]) {
    try { if (!sheet.disabled && (!sheet.media?.mediaText || matchMedia(sheet.media.mediaText).matches)) walk(sheet.cssRules); } catch { /* cross-origin sheet */ }
  }

  for (const [key, { fault }] of vhState) {
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
    escapes: escapes.length,
    smallText: smallText.length,
    smallBody: smallBody.length,
    smallSecondary: smallSecondary.length,
    offscreenFixed: offscreenFixed.length,
    smallInputs: smallInputs.length,
    letterColumn: letterColumn.length,
    splitWords: splitWords.length,
    unnamedControls: unnamedControls.length,
    repeatedHeading: repeatedHeading.length,
    squeezedScroller: squeezedScroller.length,
    distinctEdges: Object.keys(edgeCount).length,
    barsOverShare: barsShare > MAX_BARS_SHARE ? barsShare : 0,
    truncated: truncated.length,
    vhRules: new Set(vhRules).size,
    zoomBlocked: meta.zoomBlocked ? 1 : 0,
  };
  // Elements become readable names only for the lists that are printed.
  const named = (list) => list.slice(0, LIMIT).map((o) => Object.fromEntries(Object.entries(o).map(([k, v]) => [k, v instanceof Element ? name(v) : v])));
  // The page scroller is the innermost candidate that really scrolls (an outer shell that does not overflow says nothing
  // about the bottom); one that holds the root or sits inside it wins. Every scroll metric reads this one element.
  const scrolling = [...pageScrollers].filter((e) => e.scrollHeight > e.clientHeight + 1);
  const depth = (e) => { let n = 0; for (let p = e; p; p = p.parentElement) n += 1; return n; };
  const related = scrolling.filter((e) => e.contains(rootEl) || rootEl.contains(e));
  const pageEl = (related.length ? related : scrolling).sort((a, b) => depth(b) - depth(a))[0] || document.scrollingElement || doc;
  // Coverage across scroll stops: each run adds the controls it sampled to a set kept on the window.
  if (!(window.__mobileProbeSeen instanceof WeakSet)) window.__mobileProbeSeen = new WeakSet();
  for (const o of hit) window.__mobileProbeSeen.add(o.c);
  const unseen = tappable.filter((c) => !window.__mobileProbeSeen.has(c));
  return JSON.stringify({
    ms: Math.round(performance.now() - t0),
    viewport: { w: W, h: H, dpr: devicePixelRatio, coarse: matchMedia("(any-pointer: coarse)").matches },
    root: { selector: rootSelector, found: rootFound, modal: modal ? name(modal) : null },
    counts,
    overflow: named(overflow),
    clipped: named(clipped),
    scrollers: named(scrollers),
    scrollRegions: scrollRegions.slice(0, LIMIT),
    targets: named(targets),
    sampling: { controls: tappable.length, sampled: hit.length, covered: coveredList.length, unsampled: unsampled.length, points: samples, incomplete: [...incomplete], unsampledList: Object.fromEntries(["above", "below", "side", "budget", "partial"].map((w) => [w, named(unsampled.filter((u) => u.where === w))])) },
    scroller: pageEl === doc || pageEl === document.scrollingElement ? "document" : name(pageEl).replace(/ ".*$/, ""),
    coverage: { controls: tappable.length, seen: tappable.length - unseen.length, unseen: unseen.length, unseenList: named(unseen.map((c) => ({ el: c, ...rect(c) }))) },
    scrollTop: Math.round(pageEl.scrollTop), scrollHeight: pageEl.scrollHeight, clientHeight: pageEl.clientHeight,
    crowded: named(crowded),
    overlaps: named(overlaps),
    escapes: named(escapes),
    smallText: named(smallText),
    smallBody: named(smallBody),
    smallSecondary: named(smallSecondary),
    offscreenFixed: named(offscreenFixed),
    textSizes,
    smallInputs: named(smallInputs),
    letterColumn: named(letterColumn),
    splitWords: named(splitWords),
    unnamedControls: named(unnamedControls),
    repeatedHeading: named(repeatedHeading),
    squeezedScroller: named(squeezedScroller),
    edges,
    bars: { share: barsShare, list: named(bars) },
    truncated: named(truncated),
    vhRules: [...new Set(vhRules)].slice(0, LIMIT),
    meta,
  }, null, 1);
})();
