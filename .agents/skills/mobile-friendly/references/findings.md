# Findings ledger

**Why a ledger:** the checklist says what good looks like; this file says what real campaigns actually found, so the next campaign looks there first. Every campaign adds a dated section, newest first, with one line per finding: *class — symptom — cause — fix — caught by (probe field / screenshot / neither)*. When a class shows up in two campaigns or on two pages, promote it (a checklist rule, a fix pattern, a probe change) and mark the line `→ promoted to <file>`.

Keep entries provider-neutral: the framework and the fault, not the product or its domain.

## 2026-11 · React + Vite + Tailwind SPA, 20 routes, dark-first design system, 19 page agents

### Campaign shape

- **The frame dominated** — every page agent reported the same four faults: page header in two or three rows with the title running under a "Next" button at 320 px, a 24 px side margin (an 8 px panel padding on top of a 16 px page padding), a "‹ Parent" back link 14 px high, `100vh` on a shell element — they belong to the shared frame — run the shell agent first → promoted to [SKILL.md](../SKILL.md#-the-campaign), [fan-out.md § ownership](fan-out.md#1--ownership)
- **Nothing to fix** — three of the first six reports were "no change": routes that only redirect or render a title plus a shared empty-state panel — classify routes before assigning → promoted to [fan-out.md § inventory](fan-out.md#0--inventory-every-page-the-app-serves)
- **Stale inventory** — a page file named in the brief did not exist, five served routes were missing (one from an upstream package, one from the menu only), and one page file had no route at all (dead code) — the inventory was read from an old checkout and from one route file — inventory from the branch tree, reconcile router and menu → promoted to [fan-out.md](fan-out.md#0--inventory-every-page-the-app-serves)
- **Empty records hide row faults** — a page's document rows were never rendered because the chosen project had none — pick a record with data per page → promoted to [loop.md § 0](loop.md#0--set-up-once)
- **Locked records hide forms** — a locked project showed no editable step, so input sizes and the keyboard rule went unchecked — name an unlocked record for form pages
- **Read-only rules hide editors** — the section editor's toolbar was never opened because the shared data must not change — give the agent a throwaway record it may edit, or check editors against a disposable environment
- **Research skipped under pressure** — one agent of the twelve that got the research instruction skipped it — make research a numbered loop step, not an add-on → promoted to [loop.md § 1](loop.md#1--research-before-your-first-fix)

### Harness and method

- **Loading skeletons** — the first screenshot showed grey bars — taken before the list query answered — wait for a loaded element's CSS selector → promoted to [loop.md § 0](loop.md#0--set-up-once)
- **Device emulation without touch** — `set device` left `(any-pointer: coarse)` false — the driver sets user agent and pixel ratio only — test phone rules by width → promoted to [harness.md](harness.md#driver-traps-agent-browser-027)
- **Token mint over a local certificate** — `curl` to the local HTTPS backend failed while the browser trusted it — system and browser trust stores differ — mint through the preview's proxy → promoted to [harness.md](harness.md#shape)
- **Leaked preview servers** — `stop` reported success but the server kept its port — the pid file held `$!` of a backgrounded list — start the server as a simple command → promoted to [harness.md](harness.md#shape)
- **Cold start under load** — 16 dev servers compiling at once took a 32-core machine to load 34; first loads took over a minute and tool calls timed out — warm the base's dependency prebundle before cloning; run start, login and viewport as separate calls → promoted to [harness.md](harness.md#shape)
- **"Could not start" on first paint** — a failed dynamic import right after a cold start or an edit — the dev server was still compiling — reload once → promoted to [loop.md § 0](loop.md#0--set-up-once)
- **Viewport reset** — the first probe measured 1280 px — opening the page reset the viewport — set the viewport after login; read `viewport.w` → promoted to [harness.md](harness.md#driver-traps-agent-browser-027)
- **Older shared backend** — a page crashed on a missing API field — the local backend was built from an older branch than the worktree — rebuild the backend from the same branch; never patch the page around it → promoted to [harness.md](harness.md#shape)
- **Inner scroll container** — full-page screenshots showed only the first screen — the app scrolls in its own container — scroll the container and shoot in steps → promoted to [loop.md § 2](loop.md#2--shoot)
- **Blocked tools in sandboxed agents** — `sleep` and `npx -y <pkg>@latest` were denied — use the driver's `wait` and the web versions of the guides → promoted to [harness.md](harness.md#driver-traps-agent-browser-027)
- **Text selectors** — `wait "text=…"` and `click "text=…"` missed elements on screen — use CSS selectors or snapshot refs → promoted to [harness.md](harness.md#driver-traps-agent-browser-027)
- **Two agents on one preview tree** — a helper agent started and stopped a preview from the coordinator's worktree; the shared pid file then pointed at the wrong server and a start reported "port in use" — one preview per worktree, one owner
- **Dev auth host name** — local e-signing fell through to the real identity provider in the preview — the app enables its fake signing only for `localhost`, and the preview ran on `127.0.0.1` — serve and open the preview on `localhost` → promoted to [harness.md](harness.md#shape)
- **Half-built base published** — a failed dependency install still left a base directory that later starts reused — `set -e` does not apply inside `$(...)` without `inherit_errexit` — enable it, publish by rename only after success → promoted to [harness.md](harness.md#shape)
- **Hot reload crash** — a CSS update in the middle of a context-heavy panel threw a provider error — hot reload remounted part of the tree — reload; not a real fault

### Probe

- **Overflow in the app's scroll container** — a visible horizontal scrollbar while `pageScrollsSideways` was 0 — the probe treated the page's own scroll container as an intentional region — measure page scrollers (about viewport-wide, vertical) as the page — screenshot → probe changed
- **Overlap** — a header title ran under a button at 320 px; nothing flagged it — the probe had no overlap check — `overlaps` → probe changed
- **Body text at 14 px passed** — only text under 12 px was flagged — add `smallBody` and a `textSizes` histogram → probe changed
- **Shell noise** — `smallTargets`, `truncated` and `vhRules` reported the same frame items on every page — add a page root (`window.__mobileProbeRoot`) → probe changed
- **Crashes** — a numeric `value` and a selector list split at a comma inside `:is()` aborted the whole probe — guard both → probe changed
- **Transient crowding** — a crowded pair while the page loaded, or after `scrollIntoView` put content under a sticky header — probe at scroll top after the content selector is present → promoted to [loop.md § 3](loop.md#3--probe)
- **First-screen blindness** — tall stat tiles and a rail of cards pushed the main chart two screens down with every count at 0 — the probe has no notion of "first real content" — screenshot only; critique question 1
- **Popovers** — a status popover clipped at the right edge was invisible to the probe while closed — shoot every popover open → critique question 12

- **Touch-only target rules** — 175 small targets on a page that already had 44 px rules — the rules sat under `@media (pointer: coarse)`, which a headless phone viewport never matches — apply phone target sizes by width too: `@media (any-pointer: coarse), (max-width: <bp - 1>px)`; on real phones the original rule did apply, so read such counts with `viewport.coarse` in mind — probe `targets` + `viewport.coarse` → promoted to [fixes.md](fixes.md#-small-or-crowded-targets)
- **Modal false positives** — crowded pairs reported for page elements behind an open modal — the probe measured the inert page too — check the dialog screenshot; set the page root to the dialog while it is open
- **One wrapper, many targets** — 45 small targets on one step came from one focusable tooltip wrapper around a status pill — group the list by component before counting causes
- **12 px meta text** — after the pass, the home cards still carried 77 lines at 12 px (allowed as the floor, under the 13 px secondary size) — `smallSecondary` reports them; a project decides whether its meta lines move to 13 px
- **Capped lists** — `targets` listed 15 of 175 — the probe caps each list — group the full list by tag and size when a count is large

- **Probe review rounds** — three second-model rounds on the probe found 19, then 14, then fewer edge cases (page-scroller guesses, invisible or clipped boxes, native modals, label-wrapped inputs, viewport-unit overrides) — a geometric heuristic never ends in a perfect rule — add explicit hooks (`__mobileProbeRoot`, `__mobileProbePageScroller`, `[data-scroll-region]`), state each limit in the header, and cap the review rounds
- **Desktop leaks** — three page fixes changed the desktop look (unprefixed `!shrink`, `min-h-11`, state-coloured borders) — fixes written without a phone prefix — review every class a phone fix adds for a breakpoint prefix; compare the 1280 px screenshot — second-model review

- **Localhost could not show five states** (editor in edit mode, document rows, a long lineage graph, an editable intake, a simulation report) — the local stack had no record with that data — borrow one record from the development environment through the app's APIs (capture → import), sign in as its roster editor by id; four states became checkable locally, the simulation report stays a named gap (append-only run tables) → promoted to [harness.md § borrow](harness.md#borrow-data-never-move-the-loop)
- **Frame redesign in parallel** — a header overflow built on the old header conflicted with another session's frame move — the frame had two owners for an hour — ask the frame owner first and hand the rule over → promoted to [fan-out.md § ownership](fan-out.md#1--ownership)
- **Probe false positives on rich pages** — SVG edge paths of a graph counted as overlaps (42–69 on one page); a sticky toolbar over scrolled text counted as overlaps and crowded; an `::after` hit pad made its control count as truncated and as a small target; a `role=toolbar` scroll row with a label counted as an unnamed region — read the lists, not only the counts

### Page faults (fix patterns in [fixes.md § patterns](fixes.md#-patterns-from-the-first-campaign))

- **Sentence in a pill** — page scrolled sideways — `shrink-0` + no-wrap — wrap and shrink — screenshot
- **Unscoped desktop padding** — second and third text edges (x=48 on a 390 px screen) — `p-6`, `px-7`, four nested paddings — scope to desktop, zero nested layers — probe `edges`, screenshot
- **Card around one list** — text one card inset inside the margin, 25 characters per line — card chrome only on desktop — probe `edges`
- **Breakpoint prefix** — phone rules stopped at 640 px — `sm:` instead of `md:` — use the prefix that matches the app's breakpoint — neither
- **Rail of repeated cards** — six tall cards before the main chart — grid auto-fit stacked them — snap strip — screenshot
- **Stacked table rows** — a 6-cell row became ~900 px of label blocks; sorting vanished with the header — generic stack rule — grid card per row; sort select in the filter panel — screenshot
- **Three filter fields before content** — first record below the fold — filters always open — one "Filter · n" button beside the search — screenshot
- **Header actions in three rows** — two export buttons and a "Next" stacked, ~300 px of header — no phone rule for the actions slot — one row, two visible, the rest behind "More" — screenshot
- **Small inputs** — 14 px search and textarea — a shared field class sized for desktop — `max(16px, 1rem)` on phones — probe `smallInputs`
- **`em`-sized superscripts** — citation numbers at 9.9 px — `0.62em` of body text — `max(0.62em, 0.75rem)` — probe `smallText`
- **Hidden grid item kept its track** — name pushed to x=100 — fixed `grid-template-columns` — reset the template and the child's column — screenshot
- **Segmented control scrolling sideways** — 15 unnamed scroll regions — no-wrap fixed-width options — wrap and grow — probe `unnamedScrollRegions`
- **Mid-word breaks** — "Develo/pment", "SUPE/RUSER" — four columns squeezing the name; caps letter-spacing — three columns; less letter-spacing — screenshot
- **Ellipsis on names everywhere** — many `truncate` classes on names and labels — one-line row designs — `md:truncate` with `overflow-wrap: anywhere` on phones; fix a shared chip once at its owner — probe `truncated`
- **One owner, many small labels** — 10–11 px marks on every card from one chip component — fix the size once in the owner, not at seven call sites — probe `smallText`
- **Container cannot style itself** — a wrapper's frame rule inside its own `@container` query did nothing — container queries style descendants — use a media query for the wrapper — screenshot + computed style
