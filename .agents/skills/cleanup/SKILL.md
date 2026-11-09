---
name: cleanup
description: Repo cleanup and consolidation — close every loop (PRs, issues, branches, worktrees, stale tests, leftover gates, dead code after a consolidation, stray browsers and containers) and the housekeeping audit (branch sync, submodules, deploy health, docs). Use on a cleanup day or when told to consolidate, clean up, prune, deslop, "too many issues/PRs/tests", or at session start when repo state is unclear.
---

# /cleanup — repository housekeeping pass

A sweep that audits the repository, its deploy target, and docs the way
you would when you sit down and ask "what state are we actually in?"
Reports findings and applies safe fixes; surfaces blast-radius decisions
for explicit confirmation. On a cleanup day, run the close-every-loop
checklist first, then the audit.

This is **not** an autonomous "fix everything" command. The doc backlog
is usually large; many followups are explicitly future PRs. The goal of
`/cleanup` is to bring the working state up to a known-good baseline,
identify what's actually pending, and prove the deployed environment is
alive — not to ship every queued change.

## Cleanup day — close every loop

Teams that run many agents in parallel open work faster than anyone finishes it. Words like "consolidate", "clean up", "prune" and "deslop" are the signal for a cleanup day. Each ask on such a day is one room of the same clean: name the intent, then run the whole checklist, not only the ask.

### Checklist

0. **Count first.** Run `python3 .agents/skills/cleanup/inventory.py --detail` (`--help` lists the optional inputs: code roots, frozen-docs prefix, CI baseline files, guidance file, review label, a test tree for the collected case count; every missing input drops its row instead of failing). It reports tests, comment and code lines, TODO markers, Python shape, **excess complexity** (sum of complexity above 10 per function), markdown files and tokens, open issues, PRs, worktrees, branches, stashes, containers, and **running agent-browser daemons and agent-browser Chrome processes** (these leak when agents crash). Steer by excess complexity and by hotspots (excess x commits in the last 60 days), never by the mean, which splitting lowers and deleting wrappers raises. Report at the start, after each merge batch and at the end **as a table**: one row per metric, columns "last reported", "now", "change", every row (flat or unflattering ones too). Compare with the last numbers you gave, not the start of the day, and post each report on the day's cleanup issue; the snapshot file is only this machine's last run. Tests near code lines mean test noise; worktrees, branches, containers and browsers above live work are leftovers.
1. **Plan before you cut.** Between the count and the first change, turn the counts into ranked targets and post the plan where the team will see it.
   - **One lever list per metric.** For each metric, name the few actions that move it most and the command that finds them: test lines (folders with the highest tests/code ratio; noise classes such as source-text pins and mock choreography), code lines (the same fact decided in several places, then dead code), complexity (excess in hotspots; a file with several hotspots is one decision re-derived), open issues (verify-and-close sweep first, then small bugs, then epics by the consolidations that close them), markdown (largest folders, the same topic in several docs, history in always-read files), baseline lines (entries already below their pin), worktrees/branches/containers/browsers (only those you can prove are stale, see the rules).
   - **Estimate before acting:** expected change, confidence, cost, risk. Rank by change x confidence / cost. Risk to security, data, compliance or product quality becomes one multiple-choice decision for the owner.
   - **Form waves by files.** Candidates sharing no files run in parallel (one worktree each); overlapping ones run in sequence.
   - **Steer by numbers that resist gaming:** not mean complexity, raw test count, issue count by closing without work, or lines moved between files. Report deletion and consolidation separately.
   - **Predict, then compare.** After each batch, post predicted versus measured change and the cause of each miss; use the misses to re-rank the next wave.
2. **Open PRs.** Read each PR and its issue with comments, then finish it, merge it, or close it with one line of evidence (superseded, folded, decided against). Merge ready PRs in reviewed batches: combine locally, run the tests once, push once (each push may queue a deploy).
3. **Issues.** Read each issue *with its comments* and verify the claim on the current integration branch before triage. Close what is fixed and verified, with evidence. Never close unfinished work without the owner's explicit permission, quoted in the closing comment. Comment what is left on partial ones; triage the rest (group, verified severity, size, decision needed). Fan out by number range and keep one record per issue.
4. **Branches, worktrees, stashes, scratch.** Local and remote. Delete branches of merged or closed PRs, and branches whose own commits are all on the integration branch. Keep the long-lived branches, release branches and open-PR heads; retire a release branch only when a tag or kept branch fully contains it and the owner confirms. Never delete tags. See the stale-worktree test below before removing any worktree.
5. **Processes and containers.** Count agent-browser daemons, agent-browser Chrome processes and containers; stop only the stale ones (see the rules).
6. **Tests.** Consolidate under a budget: fold per-bug files into the module's behaviour file; delete duplicates, source-text greps, AST or digest pins, mock choreography, CSS-text asserts and tests of dead code. Keep compliance and security contracts, migration tests and the last refusal test per route and role.
7. **Recently consolidated code.** Run the `deslop` skill on it (frontend and backend separately): merged pages and flows leave dead routes, second paths to one fact and parallel types. Delete gates and markers together with the design they served.
8. **Sibling subsystems.** Run the `dup-hunt` behaviour-first hunt, which compares what code does, never what it is called. Two packages that solve one problem are a consolidation target that complexity scores and clone scanners miss. Apply the specialisation test: every feature only the specialised sibling has must name the goal it serves, else delete it.
9. **Inventory.** End with the `inventory.py` numbers and their change since the start, not a claim.

### Rules for the cleanup

- **Read the code yourself, tools second.** Before consolidating an area, read every file in it and write a short map (file, what it owns, where it overlaps). Duplicate and dead-code tools only cross-check afterwards; they find copy-paste, not duplicated ideas.
- **Aggressive on reversible work** (branches, PRs, issues, tests, gates, dead code): go to the end state first; a timid first cut costs a second round. **Careful where the owner is careful:** tags, production, compliance evidence.
- **No backups.** Pushed history, tags and PR refs are the backup. Check that anything worth keeping is pushed, then delete.
- **Verify every subagent claim** ("pre-existing failure", "already fixed", pin state) before acting on it.
- **Call a failure pre-existing only after a run in the CI layout** (same build tree, submodules checked out for real, a freshly provisioned database).
- **Stale-worktree test.** Remove a worktree only when all four hold: no process has its working directory inside it, it has no tracked changes, its HEAD is contained in the integration branch, and it has been untouched for 24 hours or more. "Merged" or "already on the integration branch" alone is not enough: a running agent's fresh worktree matches that. A merged PR from the branch is the best proof.
- **Worktrees with submodules.** `git worktree remove` refuses a worktree that contains submodules. Check that it is clean and merged, then `rm -r` the folder and run `git worktree prune`, then `git branch -d` the branch. Never `--force`.
- **Deletes go out as individual commands, not a shell loop.** A command analyzer may refuse a loop before any permission check. Read the batch back afterwards (`git worktree list`, `git branch --list`, `git ls-remote --heads origin`), not a scrollback of N success lines.
- **Bulk deletes and permission blocks.** When the permission check blocks an agent, never route around it. Write one script that re-checks every condition for every item itself, run it read-only first and show the counts (how many items, how many would be deleted, how many skipped and why), and hand the operator the single command that runs it for real. An approval given in chat does not pass to a subagent.
- **Count browsers, kill only stale ones.** Agents that crash leave browser daemons and Chrome processes behind, and they grow unnoticed. Count them every cleanup (`inventory.py` does). Kill only browsers older than the longest legitimate run, with a reaper (`inventory.py --reap-browsers-older-than HOURS` lists them; add `--yes` to terminate), never another agent's live session and never by a broad `pkill`.
- **End-of-session cleanup.** Before you close, remove what you created: worktrees, branches, scratch trees, containers, and cloud resources tagged for throwaway work. Hand everything unfinished to the next owner through the issue tracker (a comment with state, next step and blockers), since local notes do not survive. Stop your own agents and background jobs before the session closes.
- **Status in a few lines;** the inventory numbers are always a table.

## Housekeeping audit — what it checks, in order

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
- Delete a remote `release/*` branch or a tag (branches of merged or
  closed PRs are fine).
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
