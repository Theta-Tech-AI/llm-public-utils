# Findings ledger

**Why a ledger:** the checklist says what good looks like; this file says what real campaigns actually found, so the next campaign looks there first. Every campaign adds a dated section, newest first, with one line per finding: *class — symptom — cause — fix — caught by (probe field / screenshot / neither)*. When a class shows up in two campaigns or on two pages, promote it (a checklist rule, a fix pattern, a probe change) and mark the line `→ promoted to <file>`.

Keep entries provider-neutral: the framework and the fault, not the product or its domain.

## 2026-11 · React + Vite SPA, about 15 pages, dark-first design system

Harness and method (found while setting up, before the page agents ran):

- **Loading skeletons** — the first screenshot showed eight grey bars and no data — screenshot taken before the list query answered — wait for a known loaded element, never a fixed sleep — screenshot → promoted to [loop.md § 0](loop.md#0--set-up-once)
- **Device emulation without touch** — `set device "iPhone 14"` left `(any-pointer: coarse)` false and `maxTouchPoints` 0 — the browser driver sets user agent and pixel ratio only — test phone rules by width; test touch-only CSS another way — probe `viewport.coarse` → promoted to [harness.md](harness.md#viewport-and-device)
- **Token mint over a local certificate** — `curl` to the local HTTPS backend failed (`unable to get local issuer certificate`) while the browser trusted it — the system store and the browser store differ — mint the token through the preview's own proxy, which trusts the local root through `NODE_EXTRA_CA_CERTS` — neither → promoted to [harness.md](harness.md#shape)
- **Back link as a target** — a "‹ Parent" link above the title was 47 × 14 px — styled as a caption, not as a control — pad its hit area to 44 px — probe `targets`
- **Wide side margin** — page text started at x = 24 on a 390 px screen, not 16 — desktop page padding kept under the breakpoint — set the page margin once under the breakpoint — probe `edges`, screenshot
