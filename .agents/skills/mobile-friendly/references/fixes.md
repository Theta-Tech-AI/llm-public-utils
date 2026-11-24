# Fix patterns

**Why:** most phone faults have one cause and one fix that removes it; the tempting fix (hide the overflow, shrink the font, remove the element) hides the cause and breaks something else. Each pattern names the symptom, the cause to look for, and the fix at the cause.

## ↔️ The page scrolls sideways

- **Find the cause first.** The probe's `overflow` list names the outermost element past the right edge. Open its children: the culprit is usually one child that will not shrink.
- **Flex or grid child refuses to shrink.** A flex item's `min-width` is `auto` (its content's width), so a long word, a URL, an id or a `white-space: nowrap` label keeps it wide. Fix: `min-width: 0` on the flex/grid child (and `overflow-wrap: anywhere` on the text in it). This is the most common cause.
- **Fixed widths.** `width: 480px`, `min-width: 600px`, a grid with `grid-template-columns: 300px 1fr`. Fix: `max-width: 100%`, `minmax(0, 1fr)`, or one column under the breakpoint.
- **Long unbreakable strings.** ids, file names, hashes, emails. Fix: `overflow-wrap: anywhere` on that text, never on the whole page.
- **Media.** `img, video, canvas, svg { max-width: 100%; height: auto; }` where the app lacks it.
- **Tables.** See below; never let a table set the page width.
- **Not a fix:** `overflow-x: hidden` on `html`, `body` or the page wrapper. It also breaks `position: sticky` inside it.

## 📊 Table on a phone

- **Stacked records:** under the breakpoint, render each row as a card: the name as the card title, then two or three key facts as label-above-value pairs, the rest behind a tap. In CSS-only form: `tr { display: grid }`, `td::before { content: attr(data-label) }` as a small muted label above the value (13 px, secondary colour, no colon). Keep the header row in the accessibility tree: hide it visually (a visually-hidden class), not with `display: none`, which drops the header-to-cell association ([WAI: tables](https://www.w3.org/WAI/tutorials/tables/tips/)). Better still, render real records (a list of cards with their own labels) on phones.
- **Shape the card, not only the stack:** a generic stack rule gives one label block per cell (a 6-cell row became ~900 px). Put the row on a grid (`tr { display: grid; grid-template-columns: repeat(6, 1fr) }`), the name across all columns, three short figures spanning 2 each, two dates spanning 3 each: one compact card.
- **Sorting dies with the header row:** when column headers hide on phones, move sort into the filter panel as one `Sort` select (key and direction).
- **Priority columns:** keep name + one status, hide the rest under the breakpoint, show them on row tap or in a detail view.
- **A matrix that must stay a table:** wrap it in `<div role="region" aria-label="…" tabindex="0" style="overflow-x:auto">`, freeze the first column (`position: sticky; left: 0` on the first cell, with a background), and let a cut-off column show as the cue.

## 🥇 The first screen is all frame

- Stats rows, filter forms, help text and status banners above the content: move them below the content or behind one control (a "Filter · 2" button that opens a sheet; a disclosure for stats).
- A page header in three rows: one row for menu + title + icons; page actions in one row below, two visible, the rest behind "More"; status into the content.
- Two sticky bars: keep one, or make the second scroll with the page.

## 👆 Small or crowded targets

- **Rules gated on `(pointer: coarse)` only** do not apply in a headless phone viewport and miss touch laptops' small windows: gate phone target sizes by width as well, `@media (pointer: coarse), (max-width: <bp - 1>px)`.
- Pad the hit area, not the icon: `min-width: 44px; min-height: 44px; display: inline-grid; place-items: center` on the button.
- A visual that must stay small (a chip, a back link styled as a caption): extend the hit area with a pseudo-element (`position: relative` on the control; `::after { content: ""; position: absolute; inset: -10px; }`), and keep neighbours 8 px apart so the extended areas do not overlap. The probe measures the element's own box, so it still reports such a control: note it in the report as an extended hit area, or prefer padding (`min-height: 44px; display: inline-flex; align-items: center`) where the layout allows.
- A row of a full-width disclosure line plus a sibling link ("Section (6) … Go to") is crowded by construction: put `gap: 0.5rem` on the flex parent, not margins on the children.
- Raising targets to 44 px makes rows taller: look at the screenshot after, and take back wasted height from padding around the row, not from the target.
- A row of icon buttons: `gap: 8px` and 44 px each; if they do not fit, move the extras behind "More".
- A checkbox: make the whole label row the target (`<label>` wraps the input and the text, `min-height: 44px`).

## 🔤 Text and inputs

- Inputs, selects and textareas at `font-size: max(16px, 1rem)` under the breakpoint (stops iOS zoom on focus). Do not prevent zoom with the viewport meta instead.
- Labels and captions at 12 px or more; caps sub-labels are the usual offenders (10–11 px with letter-spacing).
- Truncated names: replace `white-space: nowrap; text-overflow: ellipsis` with wrapping (`overflow-wrap: anywhere`, two-line clamp only where a list needs a fixed rhythm and the full name is one tap away).

## 📐 Nested padding eats the width

- A panel inside a section inside a page, each with 16–24 px padding, leaves 300 px of a 390 px screen. Under the breakpoint, set nested groups' side padding to 0 and let the page margin be the only one; a card keeps one inset.
- Use the safe-area-aware page margin once, on the page container: `padding-inline: max(16px, env(safe-area-inset-left)) max(16px, env(safe-area-inset-right))`.

## 🧱 Side-by-side layouts

- Two-pane layouts (list + detail, editor + side panel): one pane at a time under the breakpoint; the list opens the detail, a back link returns. The side panel becomes a sheet or a section below.
- Components used both in a wide main column and a narrow side slot: use container queries (`container-type: inline-size` on the slot, `@container (max-width: …)` in the component) so the component reacts to its slot, not to the window.

## 📱 Height and keyboard

- `100vh` shells: `min-height: 100dvh` (or `100svh` for a drawer that must not jump).
- Bottom bars: `padding-bottom: env(safe-area-inset-bottom)`; with a form, `scroll-padding-bottom` equal to the bar height so the focused field is not under it.

## 🧩 Patterns from the first campaign

- **Breakpoint prefix:** utility frameworks name breakpoints by their own scale. Tailwind's `sm:` is 640 px; if the app's phone layout runs to 767 px, phone rules use the `md:` split (`p-3 md:p-6`, `text-base md:text-sm`).
- **Desktop padding never scoped:** `p-6`, `px-7` on a nested panel adds a second text edge on phones. Fix: `p-3 md:p-6` (one card inset) or `md:px-7` (no inset).
- **A card around one list:** apply the card's border and padding only from the desktop breakpoint; on a phone the list sits flat at the page margin with full-width dividers.
- **A pill or badge holding a sentence:** `flex-shrink: 0` plus `white-space: nowrap` pushes the page sideways. Let it wrap and shrink on phones (`white-space: normal`, `min-width: 0`, a rounder-rect radius once it is two lines).
- **A rail of repeated cards ahead of the main content** (lens pickers, model chips, stat tiles): stack them and the main chart starts two screens down. Turn the rail into a horizontal snap strip (`display: flex; overflow-x: auto; scroll-snap-type: x mandatory; flex: 0 0 min(15rem, 72%)` per card) in a named, focusable region, or move it below the content with `order` on a flex column.
- **Headline numbers:** one full-width tile for the main number, the next two side by side (`grid-cols-2`, first `col-span-2`), smaller padding, decorative icons dropped so 200 % text still fits.
- **A list row with fixed side columns** (icon | name | share | amount): at 320 px the name gets a few characters and breaks mid-word. Use three columns (icon | name | fixed-width figure) and move the secondary cells to a second line. A fixed figure column also keeps value bars comparable from row to row.
- **Caps labels with letter-spacing** break mid-word in half-width tiles: reduce the letter-spacing on phones, not the font size.
- **A hidden grid item still holds its track:** `display: none` on an emblem left a fixed first column, pushing the name to x=100. Reset `grid-template-columns` (with at least the original selector's specificity) and the remaining child's `grid-column`.
- **Superscripts and chips sized in `em`** fall under the 12 px floor (`0.62em` of 16 px = 9.9 px): `font-size: max(0.62em, 0.75rem)`.
- **Utility class loses to a component rule:** a `max-md:grid` on a table row did nothing because the table's component CSS set `display: block` with higher specificity. Fix the component rule for phones, or raise the utility (`!grid`) only in the page's own file.
- **A container cannot restyle itself from its own container query:** `@container` rules apply to descendants. A change to the wrapper's own frame goes in a media query.
- **Container query vs media query:** a page that switches on its own container width (`@container page (max-width: 30rem)`) can sit wider than the phone breakpoint at 767 px; a gap fix written only inside the container query is missing there. Fix spacing at the flex parent for every width.
- **A segmented control with many options:** fixed-width, no-wrap options scroll sideways in an unnamed region. Let options wrap and grow (`flex: 1 1 auto`) or use a select on phones.
- **Overflowing popovers:** a popover anchored to a header control sticks out past the right edge: `max-width: calc(100vw - 2 * <page margin>)` and keep its inline position inside the viewport. Shoot every popover open; the probe sees it only while it is open.
- **Scroll regions for code and logs:** a `<pre>` that scrolls needs `role="region"`, an `aria-label` and `tabindex="0"` so keyboard users can scroll it, at every width.
- **Filters on a live-filtering page:** one "Filter · n" button beside the always-visible search, opening an inline panel (one field per row) is enough; a sheet with Apply only where filters are applied in a batch.
