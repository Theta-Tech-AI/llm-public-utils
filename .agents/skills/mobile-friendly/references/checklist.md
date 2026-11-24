# What to look for on a phone

**Why this list:** a desktop page on a phone fails in the same dozen ways every time: it scrolls sideways, its targets are too small to hit, its text is too small to read, its frame eats the first screen, and its nested boxes eat the width. Each rule below names its threshold, the probe field that measures it (`📏`) or the screenshot look that shows it (`📸`), and its source. A project's own written rules win where they differ.

Phone layout = below the app's tablet/desktop breakpoint (often 768 px). The common phone range is 320 to 430 px wide.

## Rules

**M1. 🥇 Content first, one column.** The first screen shows the page title and the first real content (first card, row or field). Only the top bar and one primary action sit above it. Filters, stats, status lines and secondary actions go behind one control or below the content. 📸 *Is the first real item above the fold at 390 × 844?* — [web.dev: content first], [NN/g]

**M2. 📐 One side margin, one left edge.** One page margin (16 px is the Material compact margin) on every page, widened to the safe-area inset where the device has one: `padding-inline: max(16px, env(safe-area-inset-left))`. A nested group (section, panel, form block) adds no side padding of its own on a phone; a box around a single field or a single list is not needed. A card may keep one inset (12 px) that all its text shares. 📏 `edges` (a histogram: many distinct x values = nested padding), 📸 ruler down the page. — [Material 3: structure]

**M3. 👆 Tap targets 44 × 44 px, 8 px apart.** Pad the hit area; the icon may stay smaller. Inline links in a sentence are exempt. WCAG 2.5.8 (AA) asks 24 px; 2.5.5 (AAA) and Apple ask 44; Material asks 48 with 8 px spacing. Take 44 below the breakpoint unconditionally, 48 for the menu button and primary actions. Above the breakpoint, raise small targets under `@media (any-pointer: coarse)` (not `pointer`, which reports only the primary pointer). 📏 `targets`, `crowded`. — [web.dev: tap targets], [WCAG 2.5.8]

**M4. 🔤 Text 16 px body, 13 px secondary, 12 px floor; inputs 16 px.** iOS Safari zooms the page when it focuses an input under 16 px. Never shrink text to make a line fit. Never truncate a name: let it wrap to two lines. Use `rem` so the system text size scales it, and give text containers a minimum height, never a fixed one. 📏 `smallText`, `smallInputs`, `truncated`. — [Apple HIG: typography]

**M5. ☰ One menu button, one drawer, one way back.** One menu button top left (48 px). No second hamburger, no tab bar repeating the drawer. The drawer marks and scrolls to the current place; long lists show recent items first with a search field; deep trees drill down (tap replaces the list, with a back row) instead of indenting. The drawer is a modal `<dialog>` (focus trapped, Escape closes, focus returns to the button), at most 85 % of the width. The way back is one "‹ Parent" link above the title, not a full breadcrumb. 📸 open the drawer on the deepest page. — [NN/g: hamburger menus]

**M6. 🪧 The page header is one row.** Menu, title and the app's icons share one row (at least 56 px, grows when the title wraps). Page actions go in one row below the title, at most two visible, the rest behind "More". A status that is not an action goes into the content. Fixed or sticky bars together cover about 12 % of the height or less; on a short viewport (landscape, keyboard open) the bar scrolls with the page. Never two stacked sticky bars. 📏 `bars.share`, 📸 header rows.

**M7. 📊 No sideways scroll for primary content.** A table becomes stacked records (a card per row: name, then two or three key facts, label above value) or keeps priority columns (name + one status) with the rest behind a row tap. Content that truly needs two dimensions (a matrix, a comparison, a diagram, a map) scrolls inside its own region: `role="region"`, a name, `tabindex="0"`, first column frozen, a cut-off column visible as a cue. The page itself never scrolls sideways. 📏 `pageScrollsSideways`, `overflow`, `scrollRegions` (`named`, `focusable`). — [NN/g: mobile tables], [WCAG 1.4.10]

**M8. 📝 Forms and filters.** Labels above fields; one full-width field per row, at least 48 px high, with the right `type`, `inputmode` and `autocomplete`. Filters collapse behind one "Filter" button that shows a count ("Filter · 2") and opens a sheet with Apply. The search field stays visible. Submit is full width at the end. No search box over a list of fewer than about 8 items. 📸 — [web.dev: forms]

**M9. 🃏 Cards: one per row, one fact once.** Full width inside the margin, gap about 12 px. Name first, then one status, then one number. A fact shows once per card (no "0 %" beside "0 of 8 steps"). A disabled card keeps 4.5:1 text contrast and says why (icon + label), not by fading the text. 📸

**M10. 📱 Safe areas, viewport, keyboard.** `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`; never `maximum-scale=1` or `user-scalable=no`. Use `dvh`/`svh`, never `100vh`, for full-height shells. Pad edge-anchored bars with `env(safe-area-inset-*)`. When the keyboard opens, the focused field stays visible and Submit stays reachable by scrolling (`scroll-padding-bottom`; `interactive-widget=resizes-content` where a bottom bar needs it). Do not lock orientation. 📏 `meta`, `vhRules`. — [web.dev: viewport units], [WCAG 1.3.4]

**M11. 🌀 Reflow and motion.** At 320 px nothing is clipped and nothing scrolls sideways except a named two-dimensional region. Never hide a fault with `overflow-x: hidden` on `html`/`body`: find the wide element and fix it. Drawers and sheets appear without sliding under `prefers-reduced-motion`. Hover is never the only way to reach something. 📏 `overflow` (the outermost wide element is the cause). — [WCAG 1.4.10], [WCAG 2.3.3]

## 🔍 Critique questions

Answer each in writing, per width, before you call a page done:

1. 🥇 What is on the first screen? Is the first real content visible without scrolling?
2. 👁️ Where does the eye land first? Is that the page's main thing?
3. 🪧 Is the header one row, with page actions in one row below it (two at most)?
4. 📐 Do all texts outside cards start at one x? Inside each card, at one x?
5. 👆 Is every control big enough to hit with a thumb, and apart from its neighbour?
6. 🔤 Is every text readable without zoom? Does any name end in "…"?
7. ↔️ Does anything scroll sideways, or sit cut off at the right edge?
8. 🧱 Is there a box inside a box, or a band of empty space with no job?
9. 🔁 Is any fact shown twice?
10. 🌗 Does it hold in both themes? Does the 768 px render switch to the desktop layout?
11. 🧭 With the drawer open on this page, is the current place visible and marked?

## Sources

- [Material 3: structure (compact windows, 16 dp margins, 48 dp targets, 8 dp spacing)](https://m3.material.io/foundations/designing/structure)
- [Apple HIG: layout](https://developer.apple.com/design/human-interface-guidelines/layout), [typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- WCAG 2.2: [2.5.8 target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [1.4.10 reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html), [1.3.4 orientation](https://www.w3.org/WAI/WCAG22/Understanding/orientation.html), [2.3.3 animation](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)
- web.dev: [accessible tap targets](https://web.dev/articles/accessible-tap-targets), [viewport units](https://web.dev/blog/viewport-units), [forms](https://web.dev/learn/forms)
- NN/g: [hamburger menus](https://www.nngroup.com/articles/hamburger-menus/), [mobile tables](https://www.nngroup.com/articles/mobile-tables/)
- [Chrome modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance) guides `form-factor-adaptation`, `responsive-table`, `navigation-drawer`, `content-first-noise-reduction` (`npx -y modern-web-guidance@latest search "<query>"`)
- iOS input zoom: [West Wind](https://weblog.west-wind.com/posts/2023/Apr/17/Preventing-iOS-Textbox-Auto-Zooming-and-ViewPort-Sizing)

[web.dev: content first]: https://github.com/GoogleChrome/modern-web-guidance
[NN/g]: https://www.nngroup.com/articles/mobile-tables/
[Material 3: structure]: https://m3.material.io/foundations/designing/structure
[web.dev: tap targets]: https://web.dev/articles/accessible-tap-targets
[WCAG 2.5.8]: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
[Apple HIG: typography]: https://developer.apple.com/design/human-interface-guidelines/typography
[NN/g: hamburger menus]: https://www.nngroup.com/articles/hamburger-menus/
[NN/g: mobile tables]: https://www.nngroup.com/articles/mobile-tables/
[WCAG 1.4.10]: https://www.w3.org/WAI/WCAG22/Understanding/reflow.html
[web.dev: forms]: https://web.dev/learn/forms
[web.dev: viewport units]: https://web.dev/blog/viewport-units
[WCAG 1.3.4]: https://www.w3.org/WAI/WCAG22/Understanding/orientation.html
[WCAG 2.3.3]: https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html
