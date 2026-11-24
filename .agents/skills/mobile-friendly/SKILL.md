---
name: mobile-friendly
description: "Make every page of a web app work on a phone: inventory the pages, give each page its own agent with a private preview server, render it at phone widths in an agent browser, measure it with a probe (sideways overflow, tap targets, text and input sizes, left edges, sticky bars), critique the screenshot, fix, re-shoot, and loop until clean, then fold what the campaign found back into this skill. Use when the user says mobile friendly, responsive, phone layout, small screen, it breaks on my phone, test on mobile, or asks to fan out over pages for a layout pass."
---

# Mobile friendly: design the phone layout on purpose

**A phone layout is a design, not a shrunken desktop.** On a phone the user comes for one thing per screen: the title and the first real content. Everything else (filters, stats, secondary actions, navigation) sits behind one control or below the content. A page passes when the probe finds nothing, the screenshot reads well at every phone width, and nothing on it needs a sideways scroll or a zoom.

Two instruments, used together on every iteration:

| Instrument | Catches | Misses |
|------------|---------|--------|
| 📸 **Screenshot** (agent browser, phone viewport) | first screen, hierarchy, crowding, awkward wraps, empty bands, things that look broken | a 40 px target that looks fine, an 11 px label, a 2 px overflow, a 15 px input that zooms on iOS |
| 📏 **Probe** ([`scripts/mobile-probe.js`](scripts/mobile-probe.js)) | sideways overflow and its outermost cause, targets under 44 px or closer than 8 px, text under 12 px, inputs under 16 px, distinct left edges, fixed bars over 12 % of the height, truncation, `100vh`, blocked zoom | anything about meaning, order or taste |

## 🔁 The campaign

| # | Step | Who | Done when |
|---|------|-----|-----------|
| 0 | **Inventory** the pages from the router, not from the menu ([fan-out.md](references/fan-out.md)) | coordinator | every route maps to one page owner or is a redirect |
| 1 | **Harness**: one private preview server per agent, proxied to the shared backend ([harness.md](references/harness.md)) | coordinator | one page renders signed in at 390 px, with real data, and an edit shows up without a rebuild |
| 2 | **Shell first**: the frame every page shares (top bar, menu drawer, page header) gets its own owner | shell agent | the frame passes on an empty page |
| 3 | **One agent per page** runs [the loop](references/loop.md): shoot → probe → critique → fix → re-shoot | page agents | probe clean or every remaining count justified, critique all yes at every width |
| 4 | **Integrate**: merge the branches, typecheck, re-run the probe on every page at 390 px | coordinator | one table, every page, every count |
| 5 | **Fold back**: each agent's findings go into [findings.md](references/findings.md); a class seen twice becomes a [checklist](references/checklist.md) rule, a [fix recipe](references/fixes.md) or a probe change | coordinator | this skill knows what the campaign learned |

Step 2 runs alongside step 3 only when page agents are told: *do not touch the shell; report shell faults to the coordinator*. Otherwise every page agent "fixes" the top bar and the branches collide.

## 🎯 When is an agent happy?

All of these, at **320, 390 and 767 px** wide (844 px high), and once at **768 px** to confirm the desktop layout starts:

1. 📏 Probe: `pageScrollsSideways`, `overflow`, `smallInputs`, `zoomBlocked` are 0. `smallTargets`, `crowdedTargets`, `smallText`, `truncated`, `vhRules` are 0 or each remaining item is named in the report with the reason it stays (an inline link in a sentence; a third-party widget).
2. 📸 Critique: every question in [checklist.md § critique](references/checklist.md#-critique-questions) is a yes, in both themes if the app has two.
3. 🔁 The last two iterations changed nothing the critique cares about. Three iterations without progress on the same fault means the fault is structural: stop and report it, do not keep nudging pixels.

## 📚 References

| File | Read it when |
|------|--------------|
| [references/checklist.md](references/checklist.md) | **What to look for**: the phone rules with thresholds and sources, and the critique questions |
| [references/loop.md](references/loop.md) | **Per-page agent**: the exact shoot → probe → critique → fix loop, states to cover, file names |
| [references/harness.md](references/harness.md) | Setting up private preview servers so many agents iterate at once without rebuilding a shared bundle |
| [references/fan-out.md](references/fan-out.md) | **Coordinator**: page inventory, ownership, the agent brief, capacity, integration |
| [references/fixes.md](references/fixes.md) | A probe or screenshot fault and the CSS/markup pattern that fixes it at the cause |
| [references/findings.md](references/findings.md) | **The ledger**: what past campaigns found, newest first. Read before you start; add to it when you finish |

## 🧭 Project rules win

When the project has its own written phone rules (a design-principles file, a breakpoints doc), read them first: they win over [checklist.md](references/checklist.md) where they differ, and the critique uses their numbers. The app's own breakpoint is the phone/desktop line; do not invent a new one. If the project has no phone rules, the checklist is the starting set, and the campaign's findings are the first draft of the project's rules.
