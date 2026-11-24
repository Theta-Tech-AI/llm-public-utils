---
name: mobile-friendly
description: "Make every page of a web app work on a phone: research current mobile practice on the web, inventory the pages, give each page its own agent with a private local preview server (edit to screen in about a second), render it at phone widths in an agent browser, measure it with a probe (sideways overflow, overlaps, tap targets, text and input sizes, left edges, sticky bars), critique the screenshot, fix, re-shoot and loop until clean, send the user every screenshot as it is taken, then fold what the campaign found back into this skill. Use when the user says mobile friendly, responsive, phone layout, small screen, it breaks on my phone, test on mobile, or asks to fan out over pages for a layout pass."
---

# Mobile friendly: design the phone layout on purpose

**A phone layout is a design, not a shrunken desktop.** On a phone the user comes for one thing per screen: the title and the first real content. Everything else (filters, stats, secondary actions, navigation) sits behind one control or below the content. A page passes when the probe finds nothing, the screenshot reads well at every phone width, and nothing on it needs a sideways scroll or a zoom.

Two instruments, used together on every iteration:

| Instrument | Catches | Misses |
|------------|---------|--------|
| 📸 **Screenshot** (agent browser, phone viewport) | first screen, hierarchy, crowding, awkward wraps, empty bands, a fold that hides the main content | a 40 px target that looks fine, an 11 px label, a 2 px overflow, a 15 px input that zooms on iOS |
| 📏 **Probe** ([`scripts/mobile-probe.js`](scripts/mobile-probe.js)) | sideways overflow (document and the app's own scroll container) and its outermost cause, overlapping boxes, targets under 44 px or closer than 8 px, text under 12 px, body text under 16 px, inputs under 16 px, left-edge histogram, fixed/sticky bar share, truncation, `100vh`, blocked zoom | anything about meaning, order or taste; what is below the fold of a page that scrolls inside a container |

## 🔁 The campaign

| # | Step | Who | Done when |
|---|------|-----|-----------|
| 0 | 🌐 **Research** current mobile practice on the web ([research.md](references/research.md)) | coordinator, then every page agent for its own pattern | the brief carries cited take-aways; each report has a "🌐 Research" section |
| 1 | 📋 **Inventory** every page the app serves, from a tree at the branch the agents will use ([fan-out.md](references/fan-out.md)) | coordinator | every route maps to an owner, a redirect, or dead code; every page has a record with real data |
| 2 | 🔧 **Harness**: one private local preview per agent, hot reload, proxied to the shared local backend ([harness.md](references/harness.md)) | coordinator | one page renders signed in at 390 px with real data, and an edit shows on screen in about a second |
| 3 | 🧱 **Shell first**: the frame every page shares (top bar, page header, side margin, drawer, shared primitives) | shell agent | the frame passes on three pages; then the page agents start |
| 4 | 👥 **One agent per page** runs [the loop](references/loop.md): shoot → probe → critique → fix → re-shoot | page agents | the happy test below |
| 5 | 📸 **Show the user** every screenshot as it lands, in the chat, as images ([loop.md § show](references/loop.md#-show-the-user)) | coordinator | the user has seen each page's before, each iteration, and its after |
| 6 | 🔗 **Integrate** on localhost: merge, typecheck, re-probe every page | coordinator | one table, every page, every count, before → after |
| 7 | ☁️ **Parity check** on the deployed environment: same pages, same widths, same probe | coordinator | cloud matches localhost; any difference is a finding |
| 8 | 📒 **Fold back** findings into [findings.md](references/findings.md), then promote ([fan-out.md § fold back](references/fan-out.md#5--fold-back)) | coordinator | the skill knows what the campaign learned |

**Localhost is where the work happens; the cloud only confirms.** The loop needs the time from edit to screenshot to be milliseconds, at worst a few seconds: a hot-reload dev server on the same machine. A deploy takes minutes to an hour, so it is never part of the loop; it is the last step, to prove the deployed app looks the same.

**Why shell first:** in the first campaign every page agent reported the same four frame faults (header row, side margin, back-link target, `100vh`), and pages that are only a title plus a shared panel had nothing of their own to fix. Run the shell agent's first round before the page agents, or tell page agents to report frame faults and never fix them.

## 🎯 When is an agent happy?

All of these, at **320 px, 390 px and the widest phone width** (one pixel under the app's phone/desktop breakpoint), 844 px high, and once **at the breakpoint** to confirm the desktop layout starts there:

1. 📏 Probe, page scope (`window.__mobileProbeRoot` set to the page's own container): `pageScrollsSideways`, `overflow`, `overlaps`, `smallInputs`, `zoomBlocked` are 0. `smallTargets`, `crowdedTargets`, `smallText`, `smallBody`, `truncated`, `clipped`, `unnamedScrollRegions`, `barsOverShare`, `vhRules` are 0, or each remaining item is named in the report with the reason it stays (an inline link in a sentence; a third-party widget; a frame fault owned by the shell).
2. 📸 Critique: every question in [checklist.md § critique](references/checklist.md#-critique-questions) has its expected answer, in both themes if the app has two.
3. 🔁 The last two iterations changed nothing the critique cares about. Three iterations without progress on one fault mean the fault is structural: stop and report it, do not keep nudging pixels.

## 📚 References

| File | Read it when |
|------|--------------|
| [references/research.md](references/research.md) | **Before anything**: how to research, which sources, and the current starting map of techniques |
| [references/checklist.md](references/checklist.md) | **What to look for**: the phone rules with thresholds and sources, and the critique questions |
| [references/loop.md](references/loop.md) | **Per-page agent**: the exact shoot → probe → critique → fix loop, states, file names, showing the user |
| [references/harness.md](references/harness.md) | Setting up private local preview servers so many agents iterate at once; the driver's traps |
| [references/fan-out.md](references/fan-out.md) | **Coordinator**: inventory, ownership, the brief, capacity, integration, parity check, fold back |
| [references/fixes.md](references/fixes.md) | A probe or screenshot fault and the CSS/markup pattern that fixes it at the cause |
| [references/findings.md](references/findings.md) | **The ledger**: what past campaigns found, newest first. Read before you start; add to it when you finish |

## 🧭 Project rules win

When the project has its own written phone rules (a design-principles file, a breakpoints doc), read them first: they win over [checklist.md](references/checklist.md) where they differ, and the critique uses their numbers. The app's own breakpoint is the phone/desktop line; do not invent a new one, and read the widths above from it. If the project has no phone rules, the checklist is the starting set, and the campaign's findings are the first draft of the project's rules.
