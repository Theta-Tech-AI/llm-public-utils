---
name: findings
description: What to do when stress testing finds a bug — search before filing, file early, over-document repros/evidence/fixes/labels, Fixes/Closes on PRs, subagents must file issues not only final messages.
---

# Findings: What To Do With Bugs

Shared policy for comb, mischief, and bug hunter. Modes decide *how* to hunt; this file decides *what happens when you catch something*.

## Defaults

| Situation | Do this |
|-----------|---------|
| Repo has GitHub and you can file issues | **One issue per distinct real finding**; give the user hyperlinks when you summarize |
| No GitHub / no permission | Write a **markdown or HTML artifact** (preferably in-repo so it can be committed) |
| User asked to auto-fix | Fix **small, additive, tested** knots as you go; still **file** large or load-bearing ones |
| Unclear | Ask once, then proceed with filing |

**GitHub smoke test:** before a batch of real issues, create a throwaway issue and delete it to prove permissions.

### File early — durability over polish

File or update a GitHub issue **as soon as a real bug or scoped follow-up is confirmed**. Do this **before or alongside** the fix — not after the deploy — so the finding survives if the session ends, the agent crashes, or context is lost.

A final-message-only finding is **not durable**. Comments can always be added later to flesh out repro, evidence, or fix notes. Prefer: confirm → search → file/comment → then fix/deploy → comment again with verification.

### Subagents must file too

If you spawn subagents, their prompt must **explicitly require** GitHub issue creation or commenting for every confirmed finding (same detail bar as this doc). Do not let a subagent return bugs only in its final message to the parent — that dies with the session. The parent should verify issue URLs exist before treating the hunt as done.

## What counts as a "real" finding

Do **not** file from a single flaky signal. Cross-check before filing:

1. UI / agent-browser observation (if relevant)
2. Console / network
3. API or backend truth
4. Infra/deploy state when symptoms look like 502, blank page, or stale chunks

A scary screenshot is not a bug until another layer agrees. A clean screenshot is not proof the backend is healthy.

Rule out false alarms: deploy/roll in flight, stale SPA, your own earlier mutations, tool limitations. See [driving.md](driving.md).

One distinct bug per issue. Don't dump a whole session into a single ticket.

---

## Search before filing (avoid duplicates)

Before opening a new issue, search existing ones (open **and** closed):

```bash
gh issue list --state all --limit 50 --search "keyword1 keyword2"
# Examples:
gh issue list --state all --search "double submit order"
gh issue list --state all --search "workflow-state Continue enabled"
```

| Result | Action |
|--------|--------|
| **Close match exists** | **Comment** on that issue with the new evidence, environment, repro delta, and links — do **not** open a duplicate |
| **Related but distinct** | Open a new issue; link the related one (`Related to #N`) and explain the difference |
| **Nothing close** | Create a new issue with the full template below |

When commenting on an existing issue, still be overly detailed: what you tried, what differed from the original report, new permalinks, whether it still reproduces on current SHA.

---

## How to file a GitHub issue (be overly detailed)

Err on the side of **too much detail**. Future you (or another agent/human) should be able to reproduce and fix from the issue alone — without the chat transcript.

### Title

Name the **failure**, not the session:

- Good: `POST /api/orders after DELETE returns 200 and resurrects the row`
- Good: `"Continue" stays enabled while the review gate is incomplete`
- Bad: `Bug from mischief pass 3`
- Bad: `Something weird on staging`

### Body template

Adapt to the repo's issue template if it has one; keep this detail level. Sections, in order:

- **Summary** — what breaks, where, why it matters.
- **Why this is an issue** — impact: data loss, wrong decision, security, silent corruption, blocked workflow. Do not file polish as a defect unless you say so.
- **Environment** — app URL and environment (never prod unless asked), commit / image tag, UTC time, throwaway account and role, browser vs API, finding agent and model.
- **Steps to reproduce** — numbered, exact URLs, clicks, field values, waits, headers and bodies (secrets redacted), concurrency notes, starting state.
- **Expected** and **Actual** — quote UI copy, status codes, response bodies, console errors; say which rule makes "expected" true.
- **Evidence** — response snippets, console / network errors, screenshots, timestamped log lines, code pointers.
- **Suspected cause** — best guess with code pointers; say if uncertain.
- **Suggested fix** — function or invariant to change, and the test to add.
- **Severity** — one severity label and one line why.

### Repro quality bar

Write repros as if the reader has **never seen the app**:

- Prefer exact strings: button labels, toast text, field names — not "the blue button"
- Include waits ("wait until spinner clears / `networkidle` / status becomes `ready`")
- Include negative space: what you did *not* click, which optional fields you left empty
- For races: how many clients, which tokens/roles, approximate timing
- Re-run once before filing when cheap — note "reproduced twice" or "intermittent (1/3)"

### Code links and snippets (required when you can)

Give a **permalink** at the current commit (`gh browse path/to/file.py:42-58 --commit "$(git rev-parse HEAD)"`), a short inline snippet (5–30 lines) so the issue stays readable when the SHA ages, and the bad assumption ("swallows all exceptions and returns `None`"). For a UI/API disagreement, link both sides (frontend gate and backend handler).

### Suggested fix + justification

Always include both: **Why this is an issue** persuades a busy maintainer (name the failure mode: data integrity, authz hole, blocked workflow, wrong output, security, silent wrong answer, accessibility trap); **Suggested fix** cuts time-to-first-patch with something small and testable ("reject PATCH after DELETE with 404", "add regression test X").

---

## Labels

Follow the repo's own label rules first (`AGENTS.md`, `CONTRIBUTING.md`, issue docs). Apply every label that fits: kind, severity, every area that applies. Run `gh label list` first and reuse names; create a missing label only when none fits.

Stress-specific additions:

- **Severity** (exactly one): `severity:critical` (data loss, security breach, prod-down), `severity:high` (primary workflow blocked, wrong output, authz failure), `severity:medium` (workaround exists), `severity:low` (minor UX), `severity:latent` (landmine not yet user-visible). Repeat it in the body.
- **Mode**: `comb`, `mischief` or `bug-hunter`.
- **Finder**: a `model:<slug>` label for the model that found it, with the precise name in the body's Environment section.
- **Drive surface**: `browser` or `api-repro` when it demonstrated the bug.

## Fixing and closing issues

When you implement a fix:

1. **Reference the issue from the commit and/or PR** so GitHub auto-closes it on merge:

   ```text
   Fixes #123
   Closes #123
   ```

   Put `Fixes #N` / `Closes #N` in the PR body (and/or the merge commit message). Use `Refs #N` when the PR only partially addresses the issue.

2. **File/update the issue before the fix lands** if it is not already filed (see File early above).

3. **If the fix is committed but not live-verified**, comment on the issue with the **exact staging (or target-env) verification still required** — URL, account, steps, expected signal that proves the fix. Do not imply "done" until that verification has been run (or the user waives it).

4. After live verification, comment with the result (SHA/deploy id, steps run, pass/fail). If it failed, reopen or leave open and say so.

```bash
gh issue comment 123 --body "$(cat <<'EOF'
## Fix landed — live verify still required

- PR: https://github.com/org/repo/pull/456
- Commit: abcdef0
- Not yet verified on staging.

### Staging verification checklist
1. Deploy/promote includes abcdef0
2. As user X on https://staging.example.com/...
3. Repro steps from issue body — expect <new behavior>
4. Confirm API: `curl …` returns <expected>
EOF
)"
```

---

## Artifacts (no GitHub)

If you cannot file issues, write `docs/stress-findings-YYYYMMDD.md` (or HTML) with the **same sections and detail bar**, including permalinks and suggested fixes. Commit when appropriate. Summarize with the file path.

## Learn from bugs users found first

The point of stressing is that a bug should never reach a human before your sweep does. So treat the bugs that *did* reach a human — user reports, issues originating from human feedback, anything a real person filed that your passes missed — as a map of your blind spots.

Periodically:

1. Pull the closed **and** open bugs that originated from human/user feedback (e.g. a `human-feedback` label, or issues filed by real users rather than agents).
2. Cluster them by *class*, not instance — ask "what kind of check would have caught each?"
3. For each class, generalize it into a reusable check and add it to the right mode file: [process.md](process.md) for an affordance the inventory missed, [comb.md](comb.md) for rendered-output/UX/copy knots, [mischief.md](mischief.md) for state-contradiction and timing, [bug-hunter.md](bug-hunter.md) for statically-catchable roots.
4. Re-run the sweep with the enriched catalog to find the **still-present** siblings of each human-found bug — the same class almost always has other live instances.

A human-found bug is a hole in the catalog; the durable fix is the generalized check, not just patching the one instance. These mode files are living documents — extend them whenever a bug slips past. (A recurring finding from this exercise: user-reported bugs skew heavily toward *browser-only* UX/state/timing/copy defects that backend-first sweeps never see — see the browser-only callout in [driving.md](driving.md).)

## After the pass

Summarize for the user:

- **Coverage** — inventory rows tried and skipped (with the reason), and predictions matched / falsified / unknown, from the run list and log in [process.md](process.md)
- **Findings per lane** — links to every issue (or the artifact path)
- Modes run (comb / mischief / bug hunter)
- Surfaces used (browser / API / hybrid)
- Severity mix (counts per severity label)
- Ask which items to fix now if they haven't already said

## See also

- [driving.md](driving.md) · [comb.md](comb.md) · [mischief.md](mischief.md) · [bug-hunter.md](bug-hunter.md)
