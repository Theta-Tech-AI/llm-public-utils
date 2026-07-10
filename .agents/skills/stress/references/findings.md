---
name: findings
description: What to do when stress testing finds a bug — GitHub issues by default, artifacts when needed, auto-fix only when asked. Over-document repros, evidence, fix suggestions, and labels (including severity and model).
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

## Artifacts (no GitHub)

If you cannot file issues, write `docs/stress-findings-YYYYMMDD.md` (or HTML) with the **same sections and detail bar**, including permalinks and suggested fixes. Commit when appropriate. Summarize with the file path.

## After the pass

Summarize for the user:

- Modes run (comb / mischief / bug hunter)
- Surfaces used (browser / API / hybrid)
- Links to every issue (or artifact path)
- Severity mix (counts per severity label)
- Ask which items to fix now if they haven't already said

## See also

- [driving.md](driving.md) · [comb.md](comb.md) · [mischief.md](mischief.md) · [bug-hunter.md](bug-hunter.md)
