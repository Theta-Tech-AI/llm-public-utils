# The per-page loop

**Why a loop:** one screenshot and one fix almost never finish a page. A fix at 390 px breaks 320 px; a wrapped title pushes the first card below the fold; a padded button crowds its neighbour. The loop re-measures everything after every change, so each iteration either removes a fault or shows the fix was wrong. It only works when the time from edit to screenshot is about a second, which is why it runs on a local hot-reload preview, never on a deploy.

One agent owns one page. It works in its own worktree and its own preview server ([harness.md](harness.md)), and it edits only its page's files.

## 0. 🔧 Set up (once)

Run each step as its own command, each under a timeout: a cold dev server on a loaded machine can take a minute or more for the first page, and a combined command times out half-way.

```bash
<preview> start <port>                       # private dev server, hot reload
<preview> login <s> <port> <page-path>       # sign in, open the page
agent-browser --session <s> set viewport 390 844 2   # AFTER login: opening a page can reset the viewport
agent-browser --session <s> get url          # the page may have redirected; the probe would measure the wrong page
```

Then **wait for real content**: a screenshot of loading skeletons or a spinner judges nothing. Wait for a CSS selector of the loaded page (`agent-browser --session <s> wait "<selector>"`); text selectors and fixed sleeps are unreliable. A first paint that shows a load error after a cold start ("failed to fetch dynamically imported module") is the dev server still compiling: reload once.

**Pick a record with data.** An empty project, list or account hides every row-level fault. If the page needs a record, use one with long names, many rows and every optional part filled; check an empty state too. **When the local stack has no such record, borrow one** from a deployed environment onto localhost ([harness.md § borrow](harness.md#borrow-data-never-move-the-loop)); never move the loop to the cloud. Sign in as the record's own roster user (by id) when a state needs edit rights.

## 1. 🌐 Research (before your first fix)

Search the web for your page's main pattern ([research.md](research.md)): 2–4 queries, primary sources first. Write what you took from each URL into your report, including searches that changed nothing.

## 2. 📸 Shoot

Widths: **320**, **390**, and **the widest phone width** (one pixel under the app's phone/desktop breakpoint, 767 when it is 768), height 844, and once **at the breakpoint** (the desktop layout must start there) and once at a common desktop width (1280: your change must not move it).

```bash
agent-browser --session <s> set viewport <w> 844 2
agent-browser --session <s> screenshot <dir>/<page>-<w>-<theme>-i<n>.png
```

- **Name every shot in order** (`i0` before, `i1` after the first fix, …) and keep every one: the user watches them.
- Read every image (open the PNG). One state per image: never a collage.
- **Below the fold:** only the viewport can be hit-tested. Walk the page from the top: set `window.__mobileProbeSeen = null`, probe, scroll the probe's `scroller` down by one screen minus 64 px minus the height of the fixed bars (the stops overlap, so a control cut at one edge is whole at the next), probe again, and stop when its `scrollTop + clientHeight` reaches `scrollHeight`. The probe keeps the coverage across runs in the page: `coverage.unseen` must then hold only controls cut by the time budget (`sampling.incomplete`, `sampling.unsampledList.budget`) or off to the side; re-probe those with the page root narrowed to their section.
- Cover the states a phone user meets: loaded, empty, long names, an open dialog or sheet, the menu drawer open, a form field focused. Both themes when the app has two (`agent-browser set media dark|light`, or the app's own toggle).
- After a style change, give the dev server a second before the shot; the first shot can still show the old layout.

## 3. 📏 Probe

```bash
agent-browser --session <s> eval "window.__mobileProbeRoot='<page container selector>'; $(cat <skill>/scripts/mobile-probe.js)"
```

The probe measures what a finger gets, not what the CSS boxes imply: it samples `elementFromPoint` on a grid over and around each control, so a padded `::after` hit area counts, a control under a sticky bar or a modal is skipped (`sampling.covered`), and a neighbour that steals a tap shows as `crowded`. It also reports content that **escapes its container** (`escapes`: text or a box past its card, at any width, desktop included).

- **Probe at scroll top, after the content loaded.** A sticky bar over scrolled text reads as an overlap, and a probe during loading reports transient crowding.
- **Below the fold:** only the viewport can be hit-tested. Walk the page from the top: probe, scroll the page scroller down by one screen minus 64 px minus the fixed bars (overlapping stops: a control under a bar or cut by the edge is `sampling.unsampledList.partial` and is whole at the next stop), probe again, and stop when the probe's `scrollTop + clientHeight` reaches its `scrollHeight` (the page scroller's, read by the probe). Keep the union of the controls sampled at each stop; a control counts as covered once any stop sampled it (`sampling.unsampledList.above` / `.below` / `.side` are only outside this stop's view). Controls cut by the time budget (`sampling.unsampledList.budget`, and `sampling.incomplete`) are a separate list: re-probe that stop with the page root narrowed to their section.
- Set `__mobileProbeRoot` to the page's own container so the shared frame's faults do not show on every page; run it once with the root `body` (the default) to see the frame: a root such as `main` hides the header's own controls and their crowding.

Read `counts` first, then the lists:

- `overflow` names the **outermost** wide element: it, or a child that refuses to shrink, is the cause.
- `escapes` names text or boxes that run past their card: the containment base rule is missing or bypassed ([checklist M12](checklist.md)).
- `targets` carry `hitW`/`hitH`, the measured tap area; `crowded` pairs share or nearly share one.
- `overlaps` names text under a control or two controls on top of each other: always a fault at scroll top.
- `edges` is a histogram of text start positions: the two or three biggest bars should be the page margin and the card inset; a long tail means nested padding.
- `textSizes` shows the spread: body text under 16 px is `smallBody`.
- `sampling.unsampledList.partial` lists a control not whole at this stop, with its reason (`clipped-by-<ancestor>`, `under-bar`, `pan-region`). The probe does not judge it: the walk does. A control still listed at the last stop is `clipped`: fix it. A map or graph canvas that pans on purpose carries `data-pan-viewport` on its viewport, so its own clip is not judged; `touch-action: none` alone exempts nothing.
- `letterColumn`, `splitWords`, `unnamedControls`, `repeatedHeading`, `squeezedScroller` name faults a screenshot shows but the older checks missed; judge each one.
- `ms` is the run time; sampling stops after a budget (about 1 s) on very heavy pages.

The probe cannot see touch emulation: `agent-browser set device` sets the user agent and pixel ratio but not touch, so `(any-pointer: coarse)` is false.

## 4. 🔍 Critique

Write the answers to [the critique questions](checklist.md#-critique-questions) for each width, plus the probe counts. Name each fault with its rule (M1–M11 or the project's own rule number), what you see, and the element. Rank: sideways scroll, overlaps and unreachable controls first, then the first screen, then targets and text, then alignment and polish.

## 5. 🛠️ Fix

Fix at the cause, in the page's own files ([fixes.md](fixes.md) has the patterns):

- Scope phone changes to the phone breakpoint so the desktop layout does not move. With a utility framework, check which prefix matches the app's breakpoint (Tailwind's `sm:` is 640 px; a 768 px breakpoint is `md:`).
- Use the app's existing tokens, spacing scale and breakpoint helpers. Search for how another page already solved the same fault before you write a new pattern.
- Never `overflow-x: hidden` on `html`, `body` or a page wrapper to hide a wide child. Never shrink text below the floor to make a line fit. Never `display: none` real content on a phone without a way to reach it.
- A fault in the shared frame (top bar, drawer, a shared component used on many pages) is not yours: write it down for the coordinator and move on.
- A page that already passes needs no edit. Do not invent changes.

Sync the edit into the preview, let it hot-reload, and go back to step 2.

## 6. 🛑 Stop

Stop when [the happy test](../SKILL.md#-when-is-an-agent-happy) holds at every width. Stop and report when three iterations on one fault made no progress: the fault is structural (a component designed only for wide screens, a shared frame fault, a data shape) and needs a decision, not more nudging.

## 7. 📦 Report

Commit your page's files on your branch. Then return, in this order:

1. **Result table**: one row per width, the probe counts before and after.
2. **Screenshots**: every path, in order; mark the before and the final at 390 px.
3. **Faults fixed**: rule, what it was, the fix, the file.
4. **Faults left**: rule, element, why it stays or who owns it (shell / shared component / backend data).
5. **🌐 Research**: URL — what you took — did it change the fix.
6. **Findings for the skill**: one line each, *class — symptom — cause — fix — caught by (probe field / screenshot / neither)*. Include probe false positives and misses, and harness traps.

## 📣 Show the user

The user wants to watch the work, not read about it. **Send every new screenshot to the user in the chat, as images, as soon as it exists** — the before of each page, each iteration, and the after — with a one-line caption (page, width, what changed). Page agents save every shot in order into one folder per page; the coordinator watches the folder and sends each new batch (a page's before → after pair at least, and every iteration when the user asked for more). More often is better than tidier: a stream of small batches beats one gallery at the end.
