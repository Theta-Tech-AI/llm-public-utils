# The per-page loop

**Why a loop:** one screenshot and one fix almost never finish a page. A fix at 390 px breaks 320 px; a wrapped title pushes the first card below the fold; a padded button crowds its neighbour. The loop re-measures everything after every change, so each iteration either removes a fault or shows the fix was wrong.

One agent owns one page. It works in its own worktree and its own preview server ([harness.md](harness.md)), and it edits only its page's files.

## 0. 🔧 Set up (once)

```bash
# Start your private preview server, sign in, set a phone viewport (names are examples).
<preview> start <port>
agent-browser --session <s> set viewport 390 844 2
<preview> login <s> <port> <page-path>
```

Then **wait for real content**: a screenshot of loading skeletons judges nothing. Wait until a known element of the loaded page exists (`agent-browser --session <s> wait "<selector>"`, or poll `eval` for it), never a bare sleep. If the page needs a record (a project, an item), pick one with realistic data: long names, many rows, an empty state too.

## 1. 📸 Shoot

For each width **320, 390, 767** (height 844), and once at **768** (the desktop layout must start there):

```bash
agent-browser --session <s> set viewport <w> 844 2
agent-browser --session <s> screenshot <dir>/<page>-<w>-<theme>-i<n>.png          # first screen
agent-browser --session <s> screenshot --full <dir>/<page>-<w>-<theme>-i<n>-full.png
```

Read every image (open the PNG). One state per image: never a collage. Cover the states a phone user meets on this page: loaded, empty, long names, an open dialog or sheet, the menu drawer open, a form with the keyboard field focused. Both themes when the app has two (`agent-browser set media dark|light`, or the app's own toggle).

## 2. 📏 Probe

```bash
agent-browser --session <s> eval "$(cat <skill>/scripts/mobile-probe.js)"
```

Run it at each width, after the content loaded. Read `counts` first; then the lists. `overflow` names the **outermost** wide element: that element (or a child that refuses to shrink) is the cause, not the page. `edges` is a histogram of text start positions: the two or three biggest bars should be the page margin and the card inset; a long tail of x values means nested padding.

The probe does not see touch emulation: `agent-browser set device` sets the user agent and pixel ratio but not touch, so `(any-pointer: coarse)` is false. Below the breakpoint that does not matter if the app applies phone rules by width.

## 3. 🔍 Critique

Write the answers to [the critique questions](checklist.md#-critique-questions) for each width, plus the probe counts. Name each fault with its rule (M1–M11 or the project's own rule number), what you see, and the element. Rank: sideways scroll and unreachable controls first, then the first screen, then targets and text, then alignment and polish.

## 4. 🛠️ Fix

Fix at the cause, in the page's own files ([fixes.md](fixes.md) has the patterns):

- Scope phone changes to the phone breakpoint (`@media (max-width: <bp - 1>px)` or the app's helper) so the desktop layout does not move. Check 1280 px once at the end.
- Use the app's existing tokens, spacing scale and breakpoint helpers. Search for how another page already solved the same fault before you write a new pattern.
- Never `overflow-x: hidden` on `html`, `body` or a page wrapper to hide a wide child. Never shrink text below the floor to make a line fit. Never `display: none` real content on a phone without a way to reach it.
- A fault in the shared frame (top bar, drawer, shared component used on many pages) is not yours: write it down for the coordinator and move on.

Sync the edit into the preview (`<preview> sync`), let it hot-reload, and go back to step 1.

## 5. 🛑 Stop

Stop when [the happy test](../SKILL.md#-when-is-an-agent-happy) holds at every width. Stop and report when three iterations on one fault made no progress: the fault is structural (a component designed only for wide screens, a shared frame fault, a data shape) and needs a decision, not more nudging.

## 6. 📦 Report

Commit your page's files on your branch. Then return, in this order:

1. **Result table**: one row per width, the probe counts before and after.
2. **Screenshots**: the before and after paths at 390 px (and any width that changed most).
3. **Faults fixed**: rule, what it was, the fix, the file.
4. **Faults left**: rule, element, why it stays or who owns it (shell / shared component / backend data).
5. **Findings for the skill**: anything that was hard to see, a probe false positive or miss, a fix pattern that worked, a trap in the harness. One line each: *class — symptom — cause — fix — caught by (probe field / screenshot / neither)*.
