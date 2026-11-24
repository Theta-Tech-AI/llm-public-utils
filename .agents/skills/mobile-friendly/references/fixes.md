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

- **Stacked records:** under the breakpoint, render each row as a card: the name as the card title, then two or three key facts as label-above-value pairs, the rest behind a tap. In CSS-only form: `tr { display: grid }`, `td::before { content: attr(data-label) }`, `thead { display: none }` (keep the header text reachable by `data-label`).
- **Priority columns:** keep name + one status, hide the rest under the breakpoint, show them on row tap or in a detail view.
- **A matrix that must stay a table:** wrap it in `<div role="region" aria-label="…" tabindex="0" style="overflow-x:auto">`, freeze the first column (`position: sticky; left: 0` on the first cell, with a background), and let a cut-off column show as the cue.

## 🥇 The first screen is all frame

- Stats rows, filter forms, help text and status banners above the content: move them below the content or behind one control (a "Filter · 2" button that opens a sheet; a disclosure for stats).
- A page header in three rows: one row for menu + title + icons; page actions in one row below, two visible, the rest behind "More"; status into the content.
- Two sticky bars: keep one, or make the second scroll with the page.

## 👆 Small or crowded targets

- Pad the hit area, not the icon: `min-width: 44px; min-height: 44px; display: inline-grid; place-items: center` on the button.
- A visual that must stay small (a chip, a dense list row): extend the hit area with a pseudo-element (`position: relative` on the control; `::after { content: ""; position: absolute; inset: -10px; }`), and keep neighbours 8 px apart so the extended areas do not overlap.
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
