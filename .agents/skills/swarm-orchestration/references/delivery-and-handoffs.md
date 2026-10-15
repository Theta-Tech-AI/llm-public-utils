# Delivery and handoffs

## Assignment and result record

Keep one compact record in a durable tracker, omitting fields that do not apply, with results beside the original acceptance criteria so a new session can see what remains.

```text
Task and intended outcome / primary task ID / stage:
Acceptance rows, including live or release requirements:
Owner / independent reviewer / coordinator:
Workspace / real remote / branch / baseline revision:
Allowed paths or artefact boundary / excluded scope:
Dependencies / active descendants / shared resources:
Checkpoint bound / next checkpoint:

Final revision / changed paths:
Source composition: upstream revision + overlay revision + generated inputs:
Checks: command, working directory, tool version, result, durable evidence:
Review: exact revision, findings, resolution:
Delivery: PR or artefact link, target, exact head, check state, merge revision:
Completed acceptance rows / remaining rows:
Blocker / next action / owner / updated at:
```

A local path or "tests pass" alone is not a durable result: store the summary with an accessible artefact, commit or task record, and keep secrets and sensitive payloads out of it.

## Validate the source you intend to deliver

For layered repositories record the upstream commit, overlay commit, generated inputs and composition procedure; keep the upstream snapshot immutable and apply overlays into a separate disposable tree. Copying overlays into a mirror changes the baseline and can make a deletion or duplicate check falsely pass.

Confirm changed paths match the reviewed revision, never validate an old build directory or a worker's unstated local changes, and classify a failure "pre-existing" only after reproducing it on the appropriate pristine baseline with the same dependencies and composition context. Preserve other workers' work while establishing that baseline.

Test the behaviour the task changes. A page test that mocks the polling hook cannot establish polling cadence or terminal refresh; a passing helper test does not prove its production caller uses the helper. Check real callers, side effects, error paths and meaningful acceptance boundaries.

Run the project-wide type-check context, configuration, version and dependency set when CI does: single-file inference misses errors found in the complete project, and a shell gate can print type errors and still exit successfully — inspect the diagnostics and the gate's contract.

Read the required CI contract before planning publication and run the cheap repository-wide checks (documentation links, policy) before spending remote CI time; focused behaviour tests do not cover those contracts. When several items share a failing prerequisite, give one owner the repair and reuse its verified revision, validating each resulting composition. When a remote check fails, inspect its job steps and artefacts to separate an early gate failure, a test failure and an infrastructure failure before editing the patch.

Never widen error baselines, add ignores or weaken assertions to remove a regression: fix the cause or document a demonstrated intentional contract change. Isolate a required failure once and give it one owner rather than several workers repeating the investigation.

After code changes rerun the affected checks and have the independent reviewer inspect the delta, reusing evidence only while its source and assumptions still match; do not rerun every expensive suite after a prose edit.

Use a fresh empty composition for each candidate and amendment, verify the exact base revision and every provider or overlay pin before testing, and run full base-to-head gates rather than checks for the final commit alone — including the cheap policy, documentation, comment and whitespace checks that commonly run early in CI. A last-commit diff or a focused test is not enough when an earlier commit can still fail a gate. Keep the composition manifest and check output with the task record so another coordinator can reproduce the result, and verify that the recorded base revision, pins, generated inputs and final tree or commit ID match the revision under review.

## Composing a commit through a Git API

Use the exact remote parent for the new commit, and pass that commit's **tree** SHA as `base_tree` — a commit SHA is not a tree SHA. Compare the new tree's changed paths with the intended manifest before updating any ref, re-read the ref afterwards, and update only the intended feature ref: never force, and never write a default-branch ref as a shortcut. Verify every returned blob, tree and commit ID against the locally reviewed objects; never publish request files generated before a final amendment, so that each publication request describes the amended revision — republishing is not banned for objects that are still valid. Stay within the same permissions and authorisation, diagnose a transport failure before changing the patch, and treat the route as exceptional rather than building a publication service for a one-off fault.

Green CI proves the automated checks passed, not that the change is right. Keep independent review of the behaviour and data-flow invariant — for example, whether an audit transaction is actually committed — and require fresh review after any amendment.

## Full scope and architectural judgment

Build the acceptance matrix from the complete task, not the latest patch, marking each row demonstrated, outstanding or no longer applicable with a reason and evidence: a partial implementation may merge when authorised, but the task stays open until its required outcome is complete. Audit scope against the exact delivered revision or pin, comparing file hashes for the named final tree, including unchanged files used to waive a row — a stale default build cannot support a scope verdict.

Check dynamic imports, packaging behaviour, stable boundaries and real consumers before deleting a wrapper, empty package file or small module. Do not replace a narrow problem with a generic framework or an incomplete schema translator, and keep tightly coupled contract changes together. When a proposed implementation is obsolete but its outcome already holds, document the evidence and let the coordinator decide within existing scope; ask for operator approval only when a real product, safety, scope or authorisation decision is missing.

For upstream/downstream work, fix provider-neutral behaviour in its owning source and consume a published revision that retains the currently consumed ancestry or an explicitly justified equivalent, since a newer-looking commit can still omit deployed fixes. Verify ancestry and required content, then test the final composition; a test-only repair may not belong upstream where those tests do not exist.

## Publication and acceptance

Refresh actual remote state before publication and again before merge, verifying repository identity, base branch, exact head, independent review, required checks and current task state. A comment saying "merged" is weaker evidence than the hosting service's live merge record, and required checks must not be pending at merge. If transport fails, diagnose the tool error before changing the patch, and use another supported publication route only within the same permissions and authorisation.

Repository merge, deployed revision and live behaviour are separate facts, each claimable only with matching evidence. Do not invent deployment or live-acceptance requirements; read-only acceptance checks proceed under existing authorisation while deployment needs its own. An unreachable environment is a blocked acceptance check, not a pass — keep useful independent work moving while recording the precise blocked step.

Before closure reconcile every acceptance row against the live task and delivered revision: confirm the hosting service reports the intended PR or artefact merged or released, verify the exact merge or delivery revision, and check that no required row remains open. Post delivery links and evidence in the task record, refresh the campaign totals, and never count partial slices, duplicate housekeeping closures or unrelated contributors as this swarm's completed work.
