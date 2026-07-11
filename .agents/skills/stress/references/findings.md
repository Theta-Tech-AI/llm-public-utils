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
- Good: `Authoring "Continue" stays enabled when SE gate is incomplete`
- Bad: `Bug from mischief pass 3`
- Bad: `Something weird on staging`

### Body template

Use this structure (adapt section names if the repo has an issue template — fill theirs, but keep this level of detail):

```markdown
## Summary
One or two sentences: what breaks, where, and why it matters.

## Why this is an issue
Justify impact. Who gets hurt? Data loss? Wrong decision? Security? Silent corruption?
Blocked workflow? Confusing UX that will generate support load?
Do not file "nice to have polish" as if it were a defect unless you say so explicitly.

## Environment
- App URL / environment: (local / staging / prod — never prod unless user asked)
- Commit / SHA / image tag / deploy id: (if known)
- Date/time (UTC):
- Account / role used: (throwaway id, not passwords)
- Browser vs API (or both):
- Agent / model that found it: (e.g. Cursor Grok, Claude Opus, …)

## Steps to reproduce (overly detailed)
Numbered steps a stranger can follow. Include:
- Exact URLs and navigation path
- Every click, field value, wait, and back-button
- For API: full method, path, query, headers (secrets redacted), body
- Timing / concurrency notes ("two tabs", "fire 10 parallel POSTs")
- Starting state (empty project, seeded fixture name, prior API setup)

1. …
2. …
3. …

## Expected
What should happen, and why (product rule, API contract, UI gate, security invariant).

## Actual
What happened instead — quote UI copy, status codes, response bodies, console errors.

## Evidence
Paste more than you think you need:
- Response snippets (trim only secrets)
- Console / network errors
- Screenshots or recording paths if available
- Log lines with timestamps
- **Code pointers** (see below)

## Suspected cause
Best guess with pointers into the code. Say if uncertain.

## Suggested fix
Concrete, actionable suggestions (even if wrong — they accelerate triage):
- Which function/handler/component to change
- Invariant to enforce (e.g. "DELETE must make subsequent PATCH return 404")
- Test to add (UI, API, or unit)
- Whether a quick guard is enough vs a deeper redesign

## Severity
One of: `severity:critical` | `severity:high` | `severity:medium` | `severity:low` | `severity:latent`
(Brief one-liner why this severity.)
```

### Repro quality bar

Write repros as if the reader has **never seen the app**:

- Prefer exact strings: button labels, toast text, field names — not "the blue button"
- Include waits ("wait until spinner clears / `networkidle` / status becomes `ready`")
- Include negative space: what you did *not* click, which optional fields you left empty
- For races: how many clients, which tokens/roles, approximate timing
- Re-run once before filing when cheap — note "reproduced twice" or "intermittent (1/3)"

### Code links and snippets (required when you can)

Point at code. Prefer **stable GitHub permalinks** over vague file names:

```bash
# Permalink to a line or range on the current commit (not floating branch HEAD)
gh browse path/to/file.py:42-58 --commit "$(git rev-parse HEAD)"
# Or construct: https://github.com/<owner>/<repo>/blob/<sha>/path/to/file.py#L42-L58
```

In the issue body:

1. **Permalink** to the relevant lines (blob URL with SHA + `#Lstart-Lend`)
2. **Short inline snippet** (5–30 lines) so the issue stays readable if the SHA ages
3. Call out the bad assumption ("swallows all exceptions and returns `None`", "UI disables the button but API has no check")

Example:

```markdown
## Evidence (code)

Permalink: https://github.com/org/repo/blob/a1b2c3d/services/orders.py#L88-L101

```python
# services/orders.py (a1b2c3d)
def update_order(order_id, body):
    try:
        return repo.save(order_id, body)
    except Exception:
        return None  # callers treat None as "no change" — masks deleted rows
```
```

If the bug is UI/API disagreement, link **both** sides (frontend gate + backend handler).

### Suggested fix + justification

Always include both:

| Section | Purpose |
|---------|---------|
| **Why this is an issue** | Persuade a busy maintainer it deserves attention |
| **Suggested fix** | Reduce time-to-first-patch; show you've thought past the symptom |

Good justification names the failure mode: data integrity, authz hole, user-blocking workflow, incorrect clinical/business output, security, silent wrong answer, accessibility trap, etc.

Good fix suggestions are small and testable: "reject PATCH after DELETE with 404", "disable Continue when `workflow-state.se_complete` is false and match API", "add regression test X".

---

## Labels (use more, not fewer)

Apply **all** labels that fit. Sparse labeling makes triage worse. If a label is missing in the repo, **create it** (via `gh label create` or the UI) with a short description, then apply it — unless the user forbade creating labels.

### Severity (required)

Always set exactly one severity label:

| Label | Use when |
|-------|----------|
| `severity:critical` | Data loss, security breach, prod-down, wrong irreversible action |
| `severity:high` | User-blocking on a primary workflow; major incorrect output; authz failure |
| `severity:medium` | Real bug, workaround exists, or non-primary path |
| `severity:low` | Minor UX/copy/edge annoyance; low blast radius |
| `severity:latent` | Smell / landmine not yet user-visible but will bite (swallowed errors, missing checks) |

Mirror the same severity in the issue body.

### Model / agent identity (recommended)

Add a label for **who found it**, so humans can filter agent-filed noise and follow up with the right tool:

- Prefer a stable slug: `model:grok`, `model:claude-opus`, `model:gpt`, `model:composer`, etc.
- Or `agent:cursor`, `agent:claude-code` if the harness matters more than the model
- Create the label if missing; put the precise model name in the issue body Environment section either way

### Area / layer (apply all that apply)

Create and use specific labels rather than one vague `bug`:

| Label examples | Meaning |
|----------------|---------|
| `frontend` / `backend` / `infrastructure` | Layer |
| `api` / `ui` / `ux` / `user-experience` / `user-interface` | Surface |
| `workflow` / `logic` / `state-machine` | Behavioral class |
| `security` / `auth` / `authz` | Safety |
| `data` / `database` / `migrations` | Persistence |
| `testing` / `flaky` | Test harness issues |
| `performance` / `reliability` | Ops qualities |
| `docs` | Documentation-only |
| `comb` / `mischief` / `bug-hunter` | Which stress mode found it |
| `browser` / `api-repro` | Drive surface that demonstrated it |

Also use repo-existing labels (`bug`, `enhancement`, team names) when they fit — **in addition to**, not instead of, the specific ones above.

### Creating labels via CLI

```bash
gh label create "severity:high" --description "User-blocking or major incorrect output" --color E11D48
gh label create "model:grok" --description "Filed by Grok-family agent" --color 6E40C9
gh label create "workflow" --description "Multi-step workflow / state machine" --color 1D4ED8
# then on the issue:
gh issue create --title "…" --body-file /tmp/issue.md \
  --label "bug" --label "severity:high" --label "backend" --label "api" \
  --label "workflow" --label "mischief" --label "api-repro" --label "model:grok"
```

List first so you reuse existing names when close enough (`gh label list`), but **prefer adding a precise label** over overloading a vague one.

---

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
3. For each class, generalize it into a reusable check and add it to the right mode file: [comb.md](comb.md) for rendered-output/UX/copy knots, [mischief.md](mischief.md) for state-contradiction and timing, [bug-hunter.md](bug-hunter.md) for statically-catchable roots.
4. Re-run the sweep with the enriched catalog to find the **still-present** siblings of each human-found bug — the same class almost always has other live instances.

A human-found bug is a hole in the catalog; the durable fix is the generalized check, not just patching the one instance. These mode files are living documents — extend them whenever a bug slips past. (A recurring finding from this exercise: user-reported bugs skew heavily toward *browser-only* UX/state/timing/copy defects that backend-first sweeps never see — see the browser-only callout in [driving.md](driving.md).)

## After the pass

Summarize for the user:

- Modes run (comb / mischief / bug hunter)
- Surfaces used (browser / API / hybrid)
- Links to every issue (or artifact path)
- Severity mix (counts per severity label)
- Ask which items to fix now if they haven't already said

## See also

- [driving.md](driving.md) · [comb.md](comb.md) · [mischief.md](mischief.md) · [bug-hunter.md](bug-hunter.md)
