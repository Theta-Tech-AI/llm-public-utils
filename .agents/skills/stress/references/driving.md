---
name: driving
description: How to drive an app under stress — agent browser vs API vs hybrid — and when each surface finds different bugs.
---

# Driving: Browser vs API

Stress testing needs hands on the system. Two primary surfaces, different bugs:

| Surface | What it is | Bugs it catches well | Weak at |
|---------|------------|----------------------|---------|
| **Agent browser** (real UI) | Click/type like a user in the real SPA | Enabled/disabled controls, nav traps, modal races, labels, spinners, client-only state, "looks fine but feels broken" | Fast combinatorial sequences, auth-edge floods, pure contract bugs |
| **API** (`curl`, scripts, HTTP clients) | Talk to backends the way the frontend (or other services) would | Ordering, idempotency, authz, validation, concurrency, stale tokens, double-submit, schema drift, worker/queue failures | Visual/UX knots, wrong button affordances, layout/state that never hits the network |

Neither replaces the other. Prefer **hybrid**: use the API to set up state and probe contracts fast; use the browser to confirm what a human would actually experience.

**For a webapp the browser is not the "confirm" step, it is the product.** Users never see your `curl`; they see what renders, when, what it says and whether controls behave. Default your hands to the browser for any webapp. If your findings are all backend or contract defects, you skipped the front door; the UI is not clean.

---

## Agent browser

**[agent-browser](https://github.com/vercel-labs/agent-browser)** (Vercel Labs CLI): `open → snapshot -i → act → re-snapshot`; refs go stale after DOM changes. Install with `npm install -g agent-browser && agent-browser install`; for commands run `agent-browser skills get core`. If the repo documents its own browser auth (token scripts, test accounts), use that.

Ask the user before installing or driving a real browser at a live app, and never commit auth state files. If they decline, drive by API only.

Useful under stress:

- `agent-browser batch "open …" "snapshot -i"` chains steps when you do not need intermediate output.
- `network requests` / `network request <id>` pair with API asserts (hybrid).
- `network route "**/api/*" --abort` breaks the frontend's dependencies (mischief).

### Gotchas

- Refs shift after every re-render: take a fresh `snapshot -i` per iteration.
- Read rendered content via snapshot or get-text on a scoped ref, not a page `eval`; some layouts hide body text from `eval`, so an empty result proves nothing.
- Wrap every `eval` body in an IIFE (a bare `return` throws).

## Frontend driving playbook — be the user at the front door

A whole class of real bugs exists only in the rendered UI and its async timing (gate state that disagrees with the backend, first-visit races, a raw id flashing before a lookup resolves, loading and error copy, hide-vs-disable dead ends). Code review and API probes miss them. Run these on **every** page you touch, roughly from "do nothing" to "abuse it":

1. **Watch the first paint.** Land cold and *do nothing* for a few seconds. Note anything that flashes, a raw value (id/UUID) that appears then resolves to a name, a control that shows then hides, a "not ready"/empty state that self-corrects, or blank skeletons that read as "no data." First-visit races are invisible if you interact immediately — most of them only exist in the first second.

2. **Read every rendered string** as a real, non-expert user: headings, badges, toasts, status lines, timestamps, empty states, error and warning copy. Flag raw internal values (ids, enums, UTC, internal codes/jargon), wrong terms, and generic templated messages that should name the *actual* affected entity and current state. The words on screen are the product; read them, don't skim past them.

3. **Drive the async settle.** Trigger loads and long-running jobs and watch the loading→loaded transition end to end. Is progress loud enough for a blocking wait? Leftover or technical loading text? When several progress indicators run at once, is it clear which is the overall vs a sub-task? Then leave the page idle for a couple of poll intervals and watch for stale toasts or leaked pollers still firing.

4. **Exercise every inventory row on the page, not just the forward CTA** ([process.md](process.md)). Click every clickable thing and confirm it goes somewhere *real* — a badge, count, or link that references an entity must navigate or scroll to it, never open an empty panel or do nothing. Open every drawer/panel/modal and confirm it has a visible close. Check hover and focus states, not just the resting look — missing or inconsistent hover/focus affordances on sibling controls are real bugs.

5. **Reload to verify persistence — the single highest-yield frontend check.** After *any* change (select a row, toggle, inline-edit, autosave), hard-reload and confirm it actually stuck. This catches optimistic-UI lies, silent non-persistence (the click looked saved but no write happened), and 500s hidden behind a cheerful success toast. If a change the user expects to auto-save requires a non-obvious explicit "save," that's also a bug.

6. **Resize.** Drive the same flow at mobile, tablet, and desktop widths. Watch for overflow, overlapping elements, controls pushed off-screen or under other elements, and layouts that become unusable. "Works on my 1440px window" is not "works."

7. **Check occlusion.** Sticky headers, banners, toasts, and modals can *cover* interactive controls — a button present in the DOM but visually covered is unusable. If a click fails because something overlays the target, that is often a real user-facing bug, not merely a test annoyance to route around.

8. **Stress navigation.** Back/forward/reload at each step; paste every route's deep-link URL directly (not only via the nav); move between stages in illegal orders. Confirm the page rebuilds correct state from a cold URL and that gates hold on direct entry as well as via the nav control.

9. **Keyboard.** Tab order, Enter-to-submit, Escape-to-close. A form you can't complete or a modal you can't dismiss from the keyboard is broken for many users.

10. **Feel the latency.** Time frequent, simple actions (lock, toggle, save). A multi-second wait on something that should feel instant, with no immediate feedback, reads as broken even when it eventually succeeds — file it as a perceived-performance bug, and consider optimistic feedback.

**Cross-check stays mandatory** (a clean render is not proof — see [findings.md](findings.md)): the browser is the source of truth for *what the user sees*; `console` + `network` + API/logs are the truth for *what actually happened*. Pair them — when they disagree (UI says success, network shows a 500; UI blocks, API allows), you've found something.

Mechanics: resize via the CLI viewport before a mobile pass and re-snapshot; reload-to-verify is `open <same url>` then compare with the pre-reload state; for occlusion, screenshot rather than trust a ref click that "succeeded".

## API driving

Talk to the backend the way a client would. It finds a different and equally real class of bugs, often faster: authz/IDOR, concurrency and lost updates, idempotency, validation gaps, state-machine holes, data-integrity and audit failures. Lead with the browser on a webapp, but do not skip this. Use it to set up state, probe contracts, amplify a UI-found suspicion and hunt what the browser cannot reach.

### Setup

1. Find the contract: OpenAPI/Swagger, frontend API client, gateway routes, or HAR from a browser pass (`agent-browser network har start` / `… stop ./capture.har`).
2. Get auth the cheap way: env token, service principal, or a small mint script — same throwaway accounts as UI.
3. Prefer idempotent or clearly prefixed throwaway resources (`STRESS-…`, `COMB-…`).

### Concrete techniques

| Technique | How | What it finds |
|-----------|-----|----------------|
| **Happy-path script** | Ordered `curl`/httpx/fetch calls mirroring the UI flow; assert status + key body fields each step | Regressions, broken gates, wrong payloads |
| **Payload matrix** | Same endpoint, many *valid* variants (optional fields, empty strings, unicode, large bodies, boundary IDs) | Validation gaps, 500s on weird-but-legal input |
| **Illegal transitions** | Skip steps, call later endpoints first, reuse IDs after delete, replay create | State-machine holes the UI never exposes |
| **Idempotency / double-submit** | Same POST twice (same key or none); parallel identical writes | Duplicate rows, double charges, non-idempotent "create" |
| **Concurrency** | `xargs -P`, GNU parallel, or a short async script — two tokens, one resource | Lost updates, lock races, last-write-wins corruption |
| **Authz** | Token A creates; token B reads/writes/deletes; anonymous hits | IDOR, missing checks, role confusion |
| **Stale credentials** | Expired/revoked token, wrong `Authorization` scheme, CSRF-less cookie-only routes | Auth middleware bugs |
| **Contract drift** | Compare response shape to OpenAPI or to what the SPA expects | Field renames, null vs missing, pagination surprises |
| **Worker/async** | Trigger job via API; poll status; kill/retry mid-flight if you can | Stuck jobs, duplicate processing, silent failure |

Record repros as **method + path + headers (secrets redacted) + body + expected vs actual**. That travels better than "I clicked around."

## Which surface first

API-first: many repetitions, contracts, pagination, webhooks, batch endpoints, concurrency, idempotency, token auth easier than the IdP UI, bugs behind the UI, API-native surfaces. Browser-first: the product is a webapp and UX knots matter (wrong enabled buttons, modal traps, stale chunks, optimistic-UI lies, local cache vs server), or you still need to see the happy path. The state-contradiction catalog is in [mischief.md](mischief.md); rendered-output knots are in [comb.md](comb.md).

## Hybrid patterns (high leverage)

1. **API setup → browser verify.** Seed entities via API; comb/mischief only the UI that matters.
2. **Browser discover → API amplify.** Suspicious UI sequence → script it with variants and concurrency.
3. **API assert while browser drives.** During a UI pass, `network requests` + `curl` the same resources.
4. **Twin mischief.** Illegal order in UI *and* via API — UI blocked but API allowed (or reverse) is a real bug class.
5. **HAR bridge.** Capture HAR in the browser, turn hot paths into API stress scripts.

---

## Practical notes

- Prefer throwaway accounts/data for destructive probes.
- Don't conclude "missing/broken" from a tool miss (undriveable widget, gzipped asset grep, flaky headless). Confirm with a second surface.
- Infra CLIs and logs (`gh run`, cloud logs, worker tails) are a third surface for deploy/roll false alarms — see [findings.md](findings.md).
- Reporting policy (issues vs fix vs artifacts) lives in [findings.md](findings.md).

## See also

- [comb.md](comb.md) · [mischief.md](mischief.md) · [bug-hunter.md](bug-hunter.md) · [findings.md](findings.md)
