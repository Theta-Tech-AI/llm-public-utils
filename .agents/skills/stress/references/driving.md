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

**But for a webapp, the browser is not the "confirm" step — it is the product.** The user never sees your `curl`; their entire experience is what renders, when it renders, what it says, and whether the controls behave. It is easy to slide into API/code hunting because it's fast and systematic — and then report a pile of backend defects while the bugs users actually hit (a stage you can reach too early, a value that flashes raw, a save that didn't save, a control a banner covers) sit untouched. **Default your hands to the browser for any webapp** and drive it deliberately with the playbook below. Treat "my findings are all backend/contract" as a symptom that you skipped the front door, not that the UI is clean.

---

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

If they decline, fall back to **API-only** driving (below) and say so.

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

### Brief usage (stress loop)

Core pattern: **open → snapshot → act → re-snapshot**. Refs go stale after DOM changes — always re-snapshot.

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

- `agent-browser batch "open …" "snapshot -i"` — chain when you don't need intermediate output
- `network requests` / `network request <id>` — pair with API asserts (hybrid)
- `network route "**/api/*" --abort` — mischief: break the frontend's dependencies
- Auth: prefer project token scripts or `--state ./auth.json` / `--session-name …` over typing prod passwords into the agent; see the CLI's auth docs via `agent-browser skills get core --full`
- If a click fails because something covers the target (banner/modal), dismiss the cover, re-snapshot, retry

For deeper command reference, prefer `agent-browser skills get core` over copying stale snippets from memory.

---

### Agent-browser gotchas while poking tools

- **Refs shift** after every click that re-renders. For repeated clicks, grab the ref **fresh** each iteration (`snapshot -i` again) — do not reuse `@e3` from three actions ago.
- **Read rendered document/content via snapshot** (or dedicated get-text on a scoped ref). Some layouts do not expose body text to a naive page `eval`; don't conclude "empty/missing" from a bad eval.
- **Wrap every `eval` body in an IIFE** — a bare `return` throws `Illegal return statement`. Prefer snapshot/get over eval when either works.

## Frontend driving playbook — be the user at the front door

Driving the UI well is a skill, not a screenshot. A whole class of real bugs exists *only* here — what renders, when, what it says, and how controls behave — and none of it shows up in an API response or a code read. Run these deliberately on **every** page you touch, not just the one you came to test. The list is roughly ordered from "do nothing" to "abuse it":

1. **Watch the first paint.** Land cold and *do nothing* for a few seconds. Note anything that flashes, a raw value (id/UUID) that appears then resolves to a name, a control that shows then hides, a "not ready"/empty state that self-corrects, or blank skeletons that read as "no data." First-visit races are invisible if you interact immediately — most of them only exist in the first second.

2. **Read every rendered string** as a real, non-expert user: headings, badges, toasts, status lines, timestamps, empty states, error and warning copy. Flag raw internal values (ids, enums, UTC, internal codes/jargon), wrong terms, and generic templated messages that should name the *actual* affected entity and current state. The words on screen are the product; read them, don't skim past them.

3. **Drive the async settle.** Trigger loads and long-running jobs and watch the loading→loaded transition end to end. Is progress loud enough for a blocking wait? Leftover or technical loading text? When several progress indicators run at once, is it clear which is the overall vs a sub-task? Then leave the page idle for a couple of poll intervals and watch for stale toasts or leaked pollers still firing.

4. **Exercise every affordance, not just the forward CTA.** Click every clickable thing and confirm it goes somewhere *real* — a badge, count, or link that references an entity must navigate or scroll to it, never open an empty panel or do nothing. Open every drawer/panel/modal and confirm it has a visible close. Check hover and focus states, not just the resting look — missing or inconsistent hover/focus affordances on sibling controls are real bugs.

5. **Reload to verify persistence — the single highest-yield frontend check.** After *any* change (select a row, toggle, inline-edit, autosave), hard-reload and confirm it actually stuck. This catches optimistic-UI lies, silent non-persistence (the click looked saved but no write happened), and 500s hidden behind a cheerful success toast. If a change the user expects to auto-save requires a non-obvious explicit "save," that's also a bug.

6. **Resize.** Drive the same flow at mobile, tablet, and desktop widths. Watch for overflow, overlapping elements, controls pushed off-screen or under other elements, and layouts that become unusable. "Works on my 1440px window" is not "works."

7. **Check occlusion.** Sticky headers, banners, toasts, and modals can *cover* interactive controls — a button present in the DOM but visually covered is unusable. If a click fails because something overlays the target, that is often a real user-facing bug, not merely a test annoyance to route around.

8. **Stress navigation.** Back/forward/reload at each step; paste every route's deep-link URL directly (not only via the nav); move between stages in illegal orders. Confirm the page rebuilds correct state from a cold URL and that gates hold on direct entry as well as via the nav control.

9. **Keyboard.** Tab order, Enter-to-submit, Escape-to-close. A form you can't complete or a modal you can't dismiss from the keyboard is broken for many users.

10. **Feel the latency.** Time frequent, simple actions (lock, toggle, save). A multi-second wait on something that should feel instant, with no immediate feedback, reads as broken even when it eventually succeeds — file it as a perceived-performance bug, and consider optimistic feedback.

**Cross-check stays mandatory** (a clean render is not proof — see [findings.md](findings.md)): the browser is the source of truth for *what the user sees*; `console` + `network` + API/logs are the truth for *what actually happened*. Pair them — when they disagree (UI says success, network shows a 500; UI blocks, API allows), you've found something.

### Agent-browser mechanics for this playbook

- Resize via the CLI's viewport/window sizing before a mobile pass; re-`snapshot -i` after — layout refs move.
- **Reload-to-verify** is just `open <same url>` (or a reload) then re-`snapshot`/get-text and compare to the pre-reload state.
- To catch occlusion, don't only trust a ref click "succeeding" — screenshot and look, and check whether a banner/toast/modal is on top.
- Read rendered text via snapshot/get-text on a scoped ref, not a naive page `eval` (some layouts don't expose body text to eval).

## API driving

Talk to the backend the way a client would. This is not a lesser substitute for the browser — it finds a **different class** of bugs, often faster. On a webapp it is best used to *set up state, probe contracts, and amplify a UI-discovered suspicion* — not as the place you spend most of your time.

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

Minimal sketch (adapt to the app):

```bash
# Login / mint (example — use the project's real script when one exists)
TOKEN=$(curl -sS -X POST "$BASE/auth/token" -H 'content-type: application/json' \
  -d '{"user":"'"$STRESS_USER"'","password":"'"$STRESS_PASS"'"}' | jq -r .access_token)

# Happy path step
curl -sS -o /tmp/create.json -w "%{http_code}" -X POST "$BASE/api/items" \
  -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' \
  -d '{"name":"STRESS-comb-1"}'

# Mischief: delete then mutate
ID=$(jq -r .id /tmp/create.json)
curl -sS -X DELETE "$BASE/api/items/$ID" -H "authorization: Bearer $TOKEN"
curl -sS -X PATCH "$BASE/api/items/$ID" -H "authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' -d '{"name":"after-delete"}'   # expect 404, not 200/500

# Concurrency sketch: two writers
seq 1 20 | xargs -P 10 -I{} curl -sS -X POST "$BASE/api/items/$ID/lock" \
  -H "authorization: Bearer $TOKEN"
```

Record repros as **method + path + headers (secrets redacted) + body + expected vs actual**. That travels better than "I clicked around."

### When to lean API-first

- Many repetitions (50× variants) — browsers are slow; scripts are cheap
- Contracts, pagination, filters, webhooks, batch endpoints
- Concurrency and idempotency
- Auth is easier via tokens than full IdP UI
- Bug is behind the UI (worker, DB invariant, permission check)
- Surface is API-native (CLI, mobile, partner integrations)

---

## When to lean browser-first

- Product *is* a webapp and the user cares about **UX knots**
- Affordance bugs: wrong enabled buttons, bad CTAs, modal traps
- Client-only failure modes: stale chunks, optimistic UI lies, local cache vs server
- Still learning the happy path and need to *see* the app

---

## A large class of real bugs is browser-only — budget live passes

Code review and API probes systematically miss an entire population of bugs that real users report first, because these exist only in the rendered UI and its async timing:

- gate/nav state that disagrees with the backend's authoritative prerequisite state (a reachable stage with an unmet predecessor);
- first-visit / transient render races (stale "not ready" until a manual refresh; a control that flashes then auto-hides);
- flash of a raw internal value before a lookup resolves;
- loading-state and progress-indicator polish;
- error/status copy clarity;
- hide-vs-disable and dead-end panels.

**Diagnostic:** if your findings are dominated by backend/code defects and you have few or no UI knots, you are *under-driving the browser* — not out of bugs. Budget explicit live-browser passes that: load each page on **first visit** and watch the async settle without interacting; read **every** rendered string (badges, toasts, headers, timestamps); and reach each stage **both** via its nav control and by pasting its deep-link URL. The state-contradiction catalog is in [mischief.md](mischief.md); the rendered-output knots are in [comb.md](comb.md).

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
