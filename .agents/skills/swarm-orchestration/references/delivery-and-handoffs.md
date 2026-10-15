# Delivery and handoffs

## Assignment and result record

Use this compact record in a durable task tracker. Omit fields that do not apply. Put results next to the original acceptance criteria so a new session can see what remains.

```text
Task and intended outcome:
Primary task ID / current stage:
Acceptance rows, including live/release requirements:
Owner / independent reviewer / coordinator:
Workspace / real remote / branch / baseline revision:
Allowed paths or artifact boundary / excluded scope:
Dependencies / active descendants / shared resources:
Checkpoint bound and next checkpoint:

Final revision and changed paths:
Source composition: upstream revision + overlay revision + generated inputs:
Checks: command, working directory, tool version, result, durable evidence:
Review: exact revision, findings, resolution:
Delivery: PR/artifact link, target, exact head, check state, merge revision:
Completed acceptance rows / remaining rows:
Blocker / next action / responsible owner:
Updated at:
```

A local path or “tests pass” alone is not a durable result. Store the useful result summary with an accessible artifact, commit, or task record. Exclude secrets and sensitive payloads from reports.

## Validate the source you intend to deliver

For layered repositories, record the upstream commit, overlay commit, generated inputs, and composition procedure. Keep the upstream snapshot immutable. Apply overlays into a separate disposable tree. Copying overlays into a mirror changes the baseline and can make a deletion or duplicate check falsely pass.

Confirm changed paths match the reviewed revision. Do not validate an old build directory or a worker's unstated local changes. A failure is “pre-existing” only after reproduction on the appropriate pristine baseline with the same dependency and composition context. Preserve other workers' work while establishing that baseline.

Test the behavior the task changes. A page test that mocks the polling hook cannot establish polling cadence or terminal refresh behavior. A passing helper test cannot prove its production caller uses the helper. Check real callers, side effects, error paths, and meaningful acceptance boundaries.

Run the relevant project-wide type-check context, configuration, version, and dependency set when CI does so. Single-file inference can miss errors found when the complete project is analyzed. A shell gate can print informational type errors and still exit successfully; inspect the diagnostics and the gate's contract.

Read the required CI contract before planning publication. Run cheap applicable repository-wide checks, such as documentation links and policy checks, before spending time on remote CI. Focused behavior tests do not cover those contracts. If several items share a failing prerequisite, give the repair one owner and reuse its verified revision; validate each resulting composition separately. When a remote check fails, inspect its job steps and artifacts to distinguish an early gate failure, a test failure, and an infrastructure failure before editing the patch.

Do not widen error baselines, add ignores, or weaken assertions to make a regression disappear. Fix the cause or document a demonstrated intentional contract change. When a required check fails, isolate the failure once and assign one owner; avoid several workers repeating the same investigation.

After code changes, rerun affected checks and have the independent reviewer inspect the delta. Reuse evidence only when its source and assumptions still match. Do not rerun every expensive suite after a prose edit.

Use a fresh, empty composition for each candidate and amendment. Verify the exact base revision and every provider or overlay pin before testing. Run full base-to-head repository gates, not only checks for the final commit. Include the cheap checks that commonly run early in CI, such as policy, documentation, comment, and whitespace checks, before publication. Keep the composition manifest and check output with the task record so another coordinator can reproduce the result. A last-commit diff or focused test is insufficient when an earlier commit can still fail a gate; run the affected tests in the same project context as CI, never reuse a populated scratch tree as evidence, and verify that the recorded base revision, pins, generated inputs and final tree or commit ID match the revision under review.

## Composing a commit through a Git API

Use the exact remote parent and pass its **tree** SHA as `base_tree` — a commit SHA is not a tree SHA. Compare the new tree's changed paths with the intended manifest before updating any ref, and re-read the ref afterwards. Green CI proves automated checks passed, not that the change is right: keep an independent review of the behavior and data-flow invariant (for example, whether an audit transaction is actually committed) and require fresh review after any amendment. Because an approval pinned to an exact revision is voided by every amendment, batch small fixes into one revision before requesting review and cap the open fix-chains per branch, so the gate is not serialized behind an amend-then-re-review loop.

## Full scope and architectural judgment

Build an acceptance matrix from the complete task, not only the latest proposed patch. Mark each row as demonstrated, outstanding, or no longer applicable with a reason and evidence. A partial implementation can merge if authorized, but the task remains open until its required outcome is complete.

Audit scope against the exact delivered revision or pin. Compare file hashes for the named final tree, including unchanged files used to waive a scope row; a stale default build cannot support a scope verdict.

Do not treat every wrapper, empty package file, or small module as waste. Check dynamic imports, packaging behavior, stable boundaries, and real consumers before deletion. Do not replace a narrow problem with a generic framework or an incomplete schema translator. Keep tightly coupled contract changes together.

If a task's proposed implementation is obsolete but its outcome already holds, document the current evidence and let the coordinator decide within the existing scope. Do not invent a need for operator approval for routine architecture choices; ask only when a real product, safety, scope, or authorization decision is missing.

For upstream/downstream work, fix provider-neutral behavior in its owning source. Consume a published revision that retains the currently consumed ancestry or an explicitly justified equivalent history; a newer-looking commit can still omit deployed fixes. Verify both ancestry and required content, then test the final composition. A test-only repair on an integration branch may not belong in upstream if those tests do not exist there.

## Publication and acceptance

Refresh actual remote state before publication and again before merge. Verify repository identity, base branch, exact head, independent review, required checks, and current task state. A comment saying “merged” is weaker evidence than the hosting service's live merge record. Never merge while required checks are pending.

If transport fails, diagnose the tool error before changing the patch. Use another supported publication route only within the same permissions and authorization. For object-based Git APIs, verify every returned blob, tree, and commit ID against the locally reviewed objects; update only the intended feature ref, without force. Do not publish stale request files after an amendment or write a default-branch ref as a shortcut. Keep such a route exceptional; do not build a publication service for a one-off fault.

Repository merge, deployed revision, and live behavior are separate facts. Claim each only with matching evidence. Do not invent deployment or live-acceptance requirements for a task that does not need them. Read-only acceptance checks can proceed under existing authorization; deployment needs its own applicable authorization. An unreachable environment is a blocked acceptance check, not a pass. Keep useful independent work moving while recording the precise blocked step.

Before closure, reconcile every acceptance row against the live task and delivered revision. Confirm the hosting service reports the intended PR or artifact as merged or released, verify the exact merge or delivery revision, and check that no required acceptance row remains open. Post delivery links plus evidence in the task record, then refresh the campaign totals. Do not count partial slices, duplicate housekeeping closures, or unrelated contributors as this swarm's completed work.
