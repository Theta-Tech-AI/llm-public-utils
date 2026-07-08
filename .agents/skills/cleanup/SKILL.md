---
name: cleanup
description: End-to-end repo housekeeping pass — branch sync, submodule hygiene, stuck-deploy recovery, doc triage, E2E smoke. Use at session start or when repo/deploy state is unclear. Reports surgically; only applies safe fixes.
---

# /cleanup — repository housekeeping pass

A single-command sweep that audits the repository, its deploy target, and
docs the way you would when you sit down and ask "what state are we
actually in?" Reports findings and applies safe fixes; surfaces
blast-radius decisions for explicit confirmation.

This is **not** an autonomous "fix everything" command. The doc backlog
is usually large; many followups are explicitly future PRs. The goal of
`/cleanup` is to bring the working state up to a known-good baseline,
identify what's actually pending, and prove the deployed environment is
alive — not to ship every queued change.

## What it checks, in order

Run each section. Report findings inline. Apply safe fixes; ask before
destructive ones.

### 1. Branch sync

```bash
git status --short
git branch -vv
git log --oneline -20
for b in main develop staging release; do
  git rev-parse --verify "$b" >/dev/null 2>&1 || continue
  echo "-- $b --"
  echo "ahead:"
  git log --oneline origin/$b..$b
  echo "behind:"
  git log --oneline $b..origin/$b
done
```

Report: any branch ahead/behind its remote, any uncommitted changes.

**Safe to auto-apply**: delete local branches that are fully an ancestor
of your integration branch (`git merge-base --is-ancestor <b> develop`).

### 2. Submodule hygiene

```bash
git submodule status
git -C <upstream-submodule-path> status --short | head -30
```

If untracked files exist in the upstream submodule, each should be
present in your overlay tree — they're stale build/sync artifacts whose
cleanup step (e.g. an `EXIT` trap) didn't fire. Verify no build is in
flight first (`ps -ef | grep -E 'build|deploy|sync' | grep -v grep`),
then `git -C <upstream-submodule-path> clean -fdx`. **NEVER edit upstream
submodule files directly** — only clean sync artifacts. Real changes
belong in your overlay tree or upstream.

### 3. Parallel-agent check

Before any heavyweight op, the ~20s "is someone else here?" check. Look
for:

```bash
ps -ef | grep -E 'deploy|build|sync|push' | grep -v grep
gh run list --branch staging --limit 3
gh run list --branch main --limit 3
git -C <your-canonical-upstream-checkout> status --short
```

A CI deploy in progress, an active remote build, or uncommitted upstream
working changes mean: don't touch the same surface area. Use
`git worktree` if the upstream change you'd make collides with theirs.

### 4. Deploy-target health

Probe the deployed environment and the deploy pipeline's last run.
Replace the URLs and CLI calls below with your cloud provider's
equivalents.

```bash
# App reachability — front door, liveness, API health.
curl -sk -o /dev/null -w "/=%{http_code} /health/live=%{http_code} /api/health=%{http_code}\n" \
  https://<your-staging-environment>/ \
  https://<your-staging-environment>/health/live \
  https://<your-staging-environment>/api/health

# Most recent deploy run + status (via gh CLI or your provider's CLI).
gh run list --branch staging --limit 5
```

Repeat for any other environment expected to be up (a per-dev sandbox, etc.).

**Wedge signatures** to watch for:
- A deploy/provisioning record stuck in a `Running`/`InProgress` state
  for far longer than a normal apply (> 30 min) → stuck.
- A host-agent / VM extension stuck "Updating" past its normal window →
  extension wedge blocking the next deploy.
- A CI run that failed with "deployment already active" / "another
  operation in progress" → blocked by the wedged deployment.
- The front door returning a reverse-proxy/gateway-shaped 500 while
  authenticated `/api/...` paths return 200 in your logs → the ingress
  /gateway layer is broken, not the backend.

**Recovery** (ask before applying — these are blast-radius actions):
```bash
# Cancel a stuck deploy (provider-specific).
# Restart the host/VM if its agent is wedged; the app re-pulls its image on boot.
```

Then re-trigger the deploy: `gh workflow run <deploy-workflow>.yml --ref staging`.

### 5. Logs — pull a slice for the most recent 5-15 min

Query your log aggregator for the recent window. If you prefix log lines
with category emojis, filter by category:

```bash
<your-log-query-tool> app 15m '❌'                  # active errors
<your-log-query-tool> all 5m | head -50             # broad sweep across all services
<your-log-query-tool> app 10m 'ingest\|writing\|LLM'  # key pipeline activity
```

Report any new error category. Cross-check against the "falling back to
X" smell — if you see a fallback log line, find the service that
*caused* the fallback, don't filter-grep just the one that handled it.

### 6. Followup-doc triage + stale-content cleanup

Walk **every** `docs/*.md` file — not just followup docs. For each:

#### 6a. Followup / findings docs (`*followup*`, `*findings*`, `*stress*`, `*deferred*`)

For each finding/action item, grep the live code to confirm whether
it's:

- ✅ **Implemented** (cite the commit SHA via `git log --grep` or
  inspect the live file) — strike from the followup doc.
- 🔧 **Still actionable** — leave in place.

Delete the followup doc only when every item is implemented or marked
explicitly stale. Otherwise rewrite to remove only the closed items.

#### 6b. All markdown files — stale content sweep

For every `docs/*.md`:

- **Time-boxed items** past their date → prune (keep only items still
  actionable regardless of the date).
- **"Awaiting deploy" / "shipped, pending next deploy"** items → check
  if the deploy landed; if so, update status to ✅ deployed.
- **References to "in flight" upstream work** → check if the upstream
  PR merged; if so, update status.
- **Risk/followup items that reference fixed commits** → close them.
- **Stale counts in index docs** (`OPEN-FOLLOWUPS.md` or equivalent) →
  recount and update the table.

#### 6c. Update the open-followups index

After triaging all docs, update your canonical open-items doc (e.g.
`docs/OPEN-FOLLOWUPS.md`):
- Refresh the open-item count per doc.
- Add any newly-closed items to the "Recently closed" section.
- Remove rows for docs that have been fully closed and deleted.

This is the canonical "what's still open" view. It must match reality
after every cleanup pass.

#### 6d. Routing

**Upstream routing** for any framework-agnostic followup (caching,
storage abstraction, shared validation, etc.): move the fix into the
shared framework submodule, not into your overlay tree.

**Before duplicating an upstream PR/branch**: `git -C
<your-canonical-upstream-checkout> log --grep "<keyword>" --all` to catch
a parallel contributor's existing work. If they've already pushed the
fix, drop your branch.

### 7. Feature-parity audit (post-CI; needs an authenticated session)

Beyond the happy-path E2E drive in §7.5, walk each user-facing feature
the product promises and verify the actual UX. User-visible regressions
hide here because the happy-path drive doesn't enumerate every clickable
thing or every state transition ("click every clickable thing").

For each row: drive in the browser → cross-reference logs + DB → mark
verdict. File a fresh dated followup doc if anything regresses.

| Area | What to verify | Where the assertion lives |
|---|---|---|
| Record/resource locks | Lock badge shows a human identity (email/name), not a raw UUID. Self-lock shows "(you)". | List-item component fields; upstream PR if the backend doesn't return the identity. |
| Page-progression gating | Can't reach a downstream page before its prerequisite is complete; can't approve before draft; can't finalize with unapproved items. | Route guard + empty-state component. Drive each gate. |
| Search thoroughness | Results come from the live data store (not a stale cache), each result is grounded in real source data, any cost/metering field renders a real value. Click every result row — links should NOT point at a deprecated backend (a leftover from a prior storage provider). | Results page render; 404 handling; row link href. |
| Background ingest freshness | The ingest job has run within its expected window, new items landed in object storage, new partitions/tenants get populated. | Ingest job logs (filter by the ingest emoji); object-store item count vs a week ago. |
| Live-progress UI | Lists render with names + counts; "Generate"/action buttons work; any WebSocket subscription shows progress live, not a stale poll. | Page component; the WebSocket/SSE path. |
| Edit / version / approve flow | Create / edit / version / approve / reject end-to-end; single-user lease respected; version sidebar updates without reload. | Editor components; lease module. |
| Validation + checkers | Trigger a check → results render → audit event emitted. Reject a result → re-trigger works. | Checker runner's audit-log call. |
| Layout polish | Sidebar collapse persists across reload, no awkward padding/spacing, no horizontal scroll at common widths, sticky elements survive scroll. | Visual review against your style guide. |
| Markdown docs | `docs/*.md` — any new content unimplemented in code? Any doc tracking an item that already landed? | Walk per §6 above. |

For each "open" / regression: create or extend a dated followup doc
(`docs/<area>-followups-YYYY-MM-DD.md`). Don't bury user-visible
regressions in prose.

### 7.5. End-to-end smoke (optional — needs interactive auth)

Check whether a saved authenticated browser session exists and is fresh:

```bash
ls -la <your-browser-session-state-file>
```

If the session state is older than the refresh-token lifetime (commonly
~24h), the tokens are dead. Either:

- **Path A**: re-export the session state from a signed-in browser tab.
- **Path B**: run your token-acquisition script (e.g. a device-code
  flow) in the background; surface the device-code URL + code inline;
  inject the resulting token into the browser session.

Then drive at minimum:
- The primary happy path end to end (landing → create → core flow).
- Each visited page: snapshot interactive elements, click every
  non-destructive link; flag any link pointing at a deprecated backend.
- Cross-reference UI state + a log slice + a DB invariant query
  (the three-layer rule: UI, logs, and DB must all agree before you
  call it verified).

### 8. Report

Output a punch-list:

- Branches synced / not synced.
- Submodule state.
- Deploy-target health (each URL, host, deploy run).
- Docs: per-doc verdict (delete / trim / keep).
- E2E: ran / blocked / skipped.
- Open items: what's still pending, with file:line where actionable.
- Decisions surfaced: anything that needed operator confirmation.

## What `/cleanup` MUST NOT do without operator consent

Blast-radius actions:

- Cancel an in-progress deployment.
- Restart the host/VM.
- Push to a shared branch (staging / release / main).
- Delete a remote branch.
- Re-trigger CI (`gh workflow run`).
- `git -C <upstream-submodule-path> reset --hard` (clobbers a parallel
  contributor's sync).
- Force-push anything.

For each, present the proposed action with the live evidence (e.g.
"deployment Running 45 min, host agent Updating") and ask before doing.

## What `/cleanup` MUST NOT do at all

- **Fire a serializing remote-exec command against a host while a CI
  deploy is mid-roll.** Many host-side remote-exec mechanisms serialize
  per-host: a diagnostic probe and a CI roll arriving within seconds of
  each other deadlock — CI fails with "another operation in progress",
  the probe wedges for many minutes, and the host agent flips to
  "Updating" as collateral. Use log queries instead — they never queue.
  If a host-side mutation is genuinely needed, wait for CI to reach its
  last step (the post-deploy health probe) before issuing the command.

## When to invoke

- Start of a session where the working state is unclear ("did anyone
  push since I left?").
- After receiving "what's broken on staging?" with no specific lead.
- Before a release-gate verification pass — confirm the baseline before
  testing the gate.
- After a parallel-agent / multi-contributor session ended ambiguously —
  confirm no artifacts were left behind.

## When NOT to invoke

- You already know the scope (e.g. "fix the cost-display bug" — go
  straight at it).
- An active deploy or CI run that you started is in progress — the
  notification will wake you; polling now wastes context.
- The operator gave a specific task; `/cleanup` is a sweep, not a detour.
