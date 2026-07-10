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

## API driving

Talk to the backend the way a client would. This is not a lesser substitute for the browser — it finds a **different class** of bugs, often faster.

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
