# Research: read the web before you design

**Why:** phone layout practice moves every year (new viewport units, keyboard APIs, container queries, the retreat of the navigation drawer), and the model's training data holds old patterns. A campaign that skips research re-invents fixes the platform already solved, or ships a pattern the guidance now advises against. So every campaign starts with a short, cited research pass, and every page agent searches again for its own page's main pattern before its first fix.

## 🌐 When

| Who | When | How much |
|-----|------|----------|
| Coordinator | before the inventory | 6–10 searches across the topics below; write the take-aways into the brief with URLs |
| Page agent | before its first fix | 2–4 searches on its page's main pattern (a data table, a filter form, an editor toolbar, a chart, a feed) |
| Anyone | when a fix feels invented | one search for the pattern by name before writing it |

## 🔎 How

- **Primary sources first:** web.dev and developer.chrome.com (including Chrome's *modern-web-guidance* guides), MDN, W3C/WCAG Understanding pages, NN/g, Baymard, Material, Apple HIG, Can I Use / Baseline for support. Vendor and agency blogs are leads to a primary source, not the source.
- **Query shape:** the user-visible pattern plus "mobile" and the year (`mobile data table pattern 2026`, `mobile filter bottom sheet UX`, `virtual keyboard form field visible`). One capability per query.
- **Chrome's guides from the command line**, where the agent may run `npx`: `npx -y modern-web-guidance@latest search "<2-5 word query>"`, then `retrieve <id>`. Where `npx` is blocked (sandboxed subagents), search the web for `developer.chrome.com/docs/modern-web-guidance <topic>`: the same guides are published there.
- **Check support** for anything newer than about two years (Baseline status, Can I Use) and write the fallback next to the technique.
- **Load the search tool first.** When web search is a deferred tool, the agent cannot call it until it is loaded (for example a tool search for "WebSearch"): the brief says how, and asks for cited sources plus what changed. Agents skip the step when this is missing.
- **Record:** the brief and each agent report carry a "🌐 Research" section: URL, the one thing taken from it, and whether it changed the fix. A search that changed nothing is still listed.

## 📚 Starting map (2026-11, re-check each campaign)

**Layout and units**
- Container queries let a component follow its slot, not the window; design components, not pages. — [web.dev: the new responsive](https://web.dev/articles/new-responsive), [container queries in action](https://web.dev/articles/baseline-in-action-container-queries)
- Use `dvh` or `svh` instead of `vh`: `svh` for things that must never jump (a drawer), `dvh` for app shells. `lvh` equals today's `vh` (the large viewport, behind expanded browser bars), so it is not a fix. — [Chrome guide: responsive design](https://developer.chrome.com/docs/modern-web-guidance/guides/css/responsive-design), [web.dev: viewport units](https://web.dev/blog/viewport-units)
- Edge-to-edge with `viewport-fit=cover` and `max(16px, env(safe-area-inset-*))` on bars. — [Chrome guide: form factor adaptation](https://developer.chrome.com/docs/modern-web-guidance/guides/user-experience/form-factor-adaptation.md.txt)
- `text-wrap: pretty` for paragraphs (no one-word last lines); `balance` only for short headings. — [Chrome: text-wrap pretty](https://developer.chrome.com/blog/css-text-wrap-pretty)
- `field-sizing: content` for inputs that grow with their text (keep a `min-width`).

**Keyboard**
- Since Chrome 108 on Android the keyboard resizes only the visual viewport (like iOS Safari); `<meta name="viewport" content="…, interactive-widget=resizes-content">` opts back into resizing the layout, which keeps a bottom bar above the keyboard. — [Chrome: viewport resize behavior](https://developer.chrome.com/blog/viewport-resize-behavior), [MDN: viewport meta](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Viewport_meta_element)
- The VirtualKeyboard API (`navigator.virtualKeyboard.overlaysContent`, `env(keyboard-inset-height)`) gives full control, Chromium only: progressive enhancement. — [MDN: VirtualKeyboard API](https://developer.mozilla.org/en-US/docs/Web/API/VirtualKeyboard_API), [Chrome: VirtualKeyboard](https://developer.chrome.com/docs/web-platform/virtual-keyboard)
- The right `type`/`inputmode`/`autocomplete` brings the right keyboard; many sites still miss it. Labels above fields on phones. — [Baymard: touch keyboards](https://baymard.com/research-articles/mobile-touch-keyboards), [Baymard: label position](https://baymard.com/research-articles/mobile-form-usability-label-position)

**Content and navigation**
- Every element on a phone pushes another below the fold: prioritise content, defer secondary content, cut harder than for desktop, keep chrome small. — [NN/g: mobile UX](https://www.nngroup.com/articles/mobile-ux/), [NN/g: condense mobile content](https://www.nngroup.com/articles/condense-mobile-content/)
- Hidden navigation is used less than visible navigation; keep primary destinations visible where possible and treat the hamburger as overflow. Material 3 Expressive deprecates the navigation drawer in favour of a navigation rail / bar. — [NN/g: hamburger menus](https://www.nngroup.com/articles/hamburger-menus/), [9to5Google on M3 Expressive](https://9to5google.com/?p=672452)
- Bottom sheets: full width on phones, a short modal sheet opens fully, a tall one never opens full screen (its top goes out of reach). — [Material: bottom sheets](https://material.io/components/sheets-bottom)
- Reach: Hoober's grip research is the root of "thumb zone" advice; newer views say people change grips, so put primary actions where they are easy, but do not design for one grip. — [Smashing: the thumb zone](https://www.smashingmagazine.com/2016/09/the-thumb-zone-designing-for-mobile-users), [Addy Osmani: touch-friendly design](https://addyosmani.com/blog/touch-friendly-design/)

**Tables, charts, empty states**
- Tables: stacked records or priority columns on phones; a matrix scrolls inside a named region. — [Chrome guide: responsive table](https://developer.chrome.com/docs/modern-web-guidance/guides/ui-atoms/responsive-table), [NN/g: mobile tables](https://www.nngroup.com/articles/mobile-tables/)
- Charts: simplify rather than shrink; lead with two or three headline numbers, then one glanceable chart. — [EU data viz guide: responsive](https://data.europa.eu/apps/data-visualisation-guide/responsive-data-visualisation-introduction), [Adobe Research: responsive visualizations](https://research.adobe.com/news/designing-responsive-visualizations/)
- Filters: one labelled button with a count, collapsed by default. — [Baymard: filter UI](https://baymard.com/blog/ecommerce-filter-ui)

**Testing**
- Emulators miss keyboard behaviour and grip; check portrait and landscape, and at least once on a real mid-range phone. — [clay.global: mobile practices](https://clay.global/blog/practices-for-mobile-web-design)
