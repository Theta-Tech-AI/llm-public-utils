# The assignment and result record

The one record used at every stage: what each assignment states, what the result carries, and what survives a lost session.

## Assignment and result record

Use this compact record in a durable task tracker. Omit fields that do not apply. Put results next to the original acceptance criteria so a new session can see what remains.

```text
Task and intended outcome:
Primary task ID / current stage:
Acceptance rows, including live/release requirements:
Owner:
Independent reviewer:
Coordinator:
Workspace / real remote / branch / baseline revision:
Allowed paths or artifact boundary / excluded scope:
Dependencies / active descendants / shared resources:
Checkpoint bound and next checkpoint:

Final revision and changed paths:
Source composition: upstream revision + overlay revision + generated inputs:
Checks: command, working directory, tool version, result, durable evidence:
Review: reviewer identity, exact revision, findings, resolution:
Delivery: PR/artifact link, target, exact head, check state, merge revision:
Completed acceptance rows / remaining rows:
Blocker / next action / responsible owner:
Updated at:
```

A local path or “tests pass” alone is not a durable result. Store the useful result summary with an accessible artifact, commit, or task record. Exclude secrets and sensitive payloads from reports.

---

Related: [planning and capacity](planning-and-capacity.md) · [validation and review](validation-and-review.md) · [publication and acceptance](publication-and-acceptance.md)
