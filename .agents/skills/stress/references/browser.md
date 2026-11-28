---
name: browser
description: Browser mode — drive a webapp's real UI with agent browser like a person at the front door. Consent and install, the open → snapshot → act loop and its gotchas, and the frontend driving playbook (first paint, every string, async settle, every affordance, reload-to-verify, resize, occlusion, navigation, keyboard, latency). Use for every webapp stress pass that must see what renders.
---

# Browser mode: be the user at the front door

Why this mode matters, what only it finds and how it duels with API mode: [driving.md](driving.md). This file is how to do it.

## Agent browser

**[agent-browser](https://github.com/vercel-labs/agent-browser)** (Vercel Labs) is a browser automation CLI built for AI agents — open pages, snapshot interactive elements as `@refs`, click/fill, screenshot, and inspect network. Docs and releases:

| Resource | URL |
|----------|-----|
| GitHub | https://github.com/vercel-labs/agent-browser |
| npm | https://www.npmjs.com/package/agent-browser |
| Site / changelog | https://agent-browser.dev/changelog |
| Skills directory | https://skills.sh/vercel-labs/agent-browser |
| Built-in dogfood skill (exploratory QA) | `agent-browser skills get dogfood` after install |

### Consent first

Before installing or driving a real browser against a target app:

1. **Ask the user** for explicit consent to install/use agent-browser (it downloads a Chrome for Testing binary and can interact with live apps, including login flows).
2. Confirm the **target URL / environment** (local, staging, prod) and that throwaway accounts/data are OK.
3. Do **not** store secrets in chat logs or commit auth state files; add `auth.json` / session dumps to `.gitignore` and delete when done.

If they decline, fall back to **API-only** driving ([api.md](api.md)) and say so in the report.

### Install

After consent:

```bash
# CLI (recommended)
npm install -g agent-browser
agent-browser install                 # Chrome for Testing (first time)
# Linux if system libs are missing:
agent-browser install --with-deps

# Optional: Homebrew (macOS) or Cargo
# brew install agent-browser && agent-browser install
# cargo install agent-browser && agent-browser install

agent-browser doctor                  # sanity-check install
agent-browser upgrade                 # later updates
```

Also install the **agent skill** so coding agents know the workflow (version-matched content lives in the CLI):

```bash
npx skills add vercel-labs/agent-browser -y
# After CLI install, load current instructions:
agent-browser skills get core         # snapshot/ref/act loop + troubleshooting
agent-browser skills get core --full  # full command reference
agent-browser skills get dogfood      # exploratory testing / bug-hunt patterns
```

For deeper command reference, prefer `agent-browser skills get core` over copying stale snippets from memory.

### The loop: open → snapshot → act → re-snapshot

```bash
agent-browser open https://staging.example.com
agent-browser snapshot -i             # interactive elements → @e1, @e2, ...
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password"
agent-browser click @e3
agent-browser wait --load networkidle # use sparingly; prefer wait --text / wait @ref
agent-browser snapshot -i             # fresh refs after navigation
agent-browser screenshot --full
agent-browser network requests --type xhr,fetch   # cross-check what the UI actually called
agent-browser close
```

Useful under stress:

- `agent-browser batch "open …" "snapshot -i"` — chain when you don't need intermediate output.
- `network requests` / `network request <id>` — pair with API reads of the same resource.
- `network route "**/api/*" --abort` — mischief: break the frontend's dependencies.
- `network har start` / `network har stop ./capture.har` — the HAR bridge to API scripts ([driving.md](driving.md#how-to-duel-them)).
- Auth: prefer project token scripts or `--state ./auth.json` / `--session-name …` over typing passwords into the agent; see `agent-browser skills get core --full`.

### Gotchas

- **Refs shift** after every click that re-renders. For repeated clicks, grab the ref **fresh** each time (`snapshot -i` again); do not reuse `@e3` from three actions ago. Resizing moves refs too.
- **Read rendered text via snapshot** (or get-text on a scoped ref), not a naive page `eval`: some layouts do not expose body text to eval, so don't conclude "empty/missing" from a bad eval.
- **Wrap every `eval` body in an IIFE** — a bare `return` throws `Illegal return statement`. Prefer snapshot/get over eval when either works.
- **A ref click that "succeeded" proves nothing about occlusion**: screenshot and look whether a banner, toast or modal is on top. If a click fails because something covers the target, dismiss the cover, re-snapshot, retry — and file the cover when a real user would hit it ([playbook item 7](#the-frontend-driving-playbook)).

## The frontend driving playbook

Driving the UI well is a skill, not a screenshot. Run these deliberately on **every** page you touch, not just the one you came to test. The list runs roughly from "do nothing" to "abuse it":

1. **Watch the first paint.** Land cold and *do nothing* for a few seconds. Note anything that flashes, a raw value (id/UUID) that appears then resolves to a name, a control that shows then hides, a "not ready"/empty state that self-corrects, or blank skeletons that read as "no data." First-visit races are invisible if you interact immediately — most of them only exist in the first second.

2. **Read every rendered string** as a real, non-expert user: headings, badges, toasts, status lines, timestamps, empty states, error and warning copy. Flag raw internal values (ids, enums, UTC, internal codes/jargon), wrong terms, and generic templated messages that should name the *actual* affected entity and current state. The words on screen are the product; read them, don't skim past them. (The full catalog of rendered-output knots: [comb.md](comb.md).)

3. **Drive the async settle.** Trigger loads and long-running jobs and watch the loading→loaded transition end to end. Is progress loud enough for a blocking wait? Leftover or technical loading text? When several progress indicators run at once, is it clear which is the overall vs a sub-task? Then leave the page idle for a couple of poll intervals and watch for stale toasts or leaked pollers still firing.

4. **Exercise every affordance, not just the forward CTA.** Click every clickable thing and confirm it goes somewhere *real* — a badge, count, or link that references an entity must navigate or scroll to it, never open an empty panel or do nothing. Open every drawer/panel/modal and confirm it has a visible close. Check hover and focus states, not just the resting look — missing or inconsistent hover/focus affordances on sibling controls are real bugs.

5. **Reload to verify persistence — the single highest-yield frontend check.** After *any* change (select a row, toggle, inline-edit, autosave), hard-reload and confirm it actually stuck — once after it settles, and once *before* it visually settles. This catches optimistic-UI lies, silent non-persistence (the click looked saved but no write happened), and 500s hidden behind a cheerful success toast. If a change the user expects to auto-save requires a non-obvious explicit "save," that's also a bug.

6. **Resize.** Drive the same flow at mobile, tablet, half-width and desktop sizes, and shrink the window in the middle of a wizard and keep going. Watch for overflow, clipping, overlapping elements, controls pushed off-screen or under other elements, layout shift on a tab or device switch, and layouts that become unusable. "Works on my 1440px window" is not "works."

7. **Check occlusion.** Sticky headers, banners, toasts, and modals can *cover* interactive controls — a button present in the DOM but visually covered is unusable. If a click fails because something overlays the target, that is often a real user-facing bug, not merely a test annoyance to route around.

8. **Stress navigation.** Back/forward/reload at each step; paste every route's deep-link URL directly in a fresh tab (not only via the nav); move between stages in illegal orders. Confirm the page rebuilds correct state from a cold URL, that the URL keeps its state on Back, and that gates hold on direct entry as well as via the nav control.

9. **Keyboard** (cite the project's written design standard when it has one). Tab order, Enter-to-submit, Escape-to-close. A form you can't complete or a modal you can't dismiss from the keyboard is broken for many users.

10. **Feel the latency.** Time frequent, simple actions (lock, toggle, save). A multi-second wait on something that should feel instant, with no immediate feedback, reads as broken even when it eventually succeeds — file it as a perceived-performance bug, and consider optimistic feedback.

## Drive for time, not only for path

The playbook above still observes mostly **settled** states, because an agent normally drives `open` → wait for the page to settle → `snapshot`. Anything that exists only *during* a transition, *after* idling, or *across* two views is unreachable to that rhythm — a control that appears for a second while the page loads and then vanishes as its work starts by itself; an expiry warning that fires only when you come back to a tab left open; a summary figure that changes when you switch tabs with nothing saved in between; an error toast from navigating *during* a long job. All of these reach real users.

1. **Sample during load, not after it.** Snapshot immediately on navigation and again a beat later, before the settle, and diff them. Anything present early and absent later is a flash — and a control that flashes is a control a user can click by mistake, which matters far more than cosmetics when the action is destructive or costs money.
2. **Idle deliberately.** Leave a page open past a session, lease, or token lifetime and return to it. Anything that fires on return is invisible to a pass that never stops moving.
3. **Diff one widget across navigations.** Note a count, cost, or status; go elsewhere; come back or switch tabs; compare. A figure that changes without a corresponding action is wrong even when each view looks right on its own.
4. **Act during async work, not after it.** Long-running work is exactly when real users click elsewhere. Switch tabs, navigate away and back, and open sibling views *while* a job is live, rather than waiting for it to finish.
5. **Watch the console for the whole pass.** Repeated 4xx/5xx from background polls and auto-started work never appear in the DOM, and are often the first evidence of a doomed request the UI is quietly retrying.

A knot that exists for two seconds still reached a user.

## Cross-check

**Cross-check stays mandatory** (a clean render is not proof — see [findings.md](findings.md#what-counts-as-a-real-finding)): the browser is the source of truth for *what the user sees*; `console` + `network` + API reads + logs are the truth for *what actually happened*. When they disagree (UI says success, network shows a 500; UI blocks, API allows), you've found something.

**Budget explicit passes for the browser-only class** ([driving.md](driving.md#browser-mode-what-the-person-actually-experiences)): load each page on first visit and watch it settle without touching it, read every rendered string, and reach each stage both via its nav control and by its pasted deep link. The state-contradiction catalog is in [mischief.md](mischief.md); the rendered-output knots are in [comb.md](comb.md).
