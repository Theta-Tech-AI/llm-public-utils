# Validation and independent review

Read before accepting a handoff or approving a revision: proving the source, matching CI's context, judging scope, and keeping author and reviewer separate.

## Validate the source you intend to deliver

For layered repositories, record the upstream commit, overlay commit, generated inputs, and composition procedure. Keep the upstream snapshot immutable. Apply overlays into a separate disposable tree. Copying overlays into a mirror changes the baseline and can make a deletion or duplicate check falsely pass.

Confirm changed paths match the reviewed revision. Do not validate an old build directory or a worker's unstated local changes. A failure is “pre-existing” only after reproduction on the appropriate pristine baseline with the same dependency and composition context. Preserve other workers' work while establishing that baseline.

Test the behavior the task changes. A page test that mocks the polling hook cannot establish polling cadence or terminal refresh behavior. A passing helper test cannot prove its production caller uses the helper. Check real callers, side effects, error paths, and meaningful acceptance boundaries.

Run the relevant project-wide type-check context, configuration, version, and dependency set when CI does so. Single-file inference can miss errors found when the complete project is analyzed. A shell gate can print informational type errors and still exit successfully; inspect the diagnostics and the gate's contract.

Read the required CI contract before planning publication. Run cheap applicable repository-wide checks, such as documentation links and policy checks, before spending time on remote CI. Focused behavior tests do not cover those contracts. If several items share a failing prerequisite, give the repair one owner and reuse its verified revision; validate each resulting composition separately. When a remote check fails, inspect its job steps and artifacts to distinguish an early gate failure, a test failure, and an infrastructure failure before editing the patch.

Do not widen error baselines, add ignores, or weaken assertions to make a regression disappear. Fix the cause or document a demonstrated intentional contract change. When a required check fails, isolate the failure once and assign one owner; avoid several workers repeating the same investigation.

After code changes, rerun affected checks and have the independent reviewer inspect the delta. Reuse evidence only when its source and assumptions still match. Do not rerun every expensive suite after a prose edit.

Use a fresh, empty composition for each candidate and amendment. Verify the exact base revision and every provider or overlay pin before testing. Run full base-to-head repository gates, not only checks for the final commit. Include the cheap checks that commonly run early in CI, such as policy, documentation, comment, and whitespace checks, before publication. Keep the composition manifest and check output with the task record so another coordinator can reproduce the result. A last-commit diff or focused test is insufficient when an earlier commit can still fail a gate. Run the affected tests in the same project context as CI. Never reuse a populated scratch tree as evidence. Verify that the recorded base revision, pins, generated inputs, and final tree or commit ID match the revision under review.

## Full scope and architectural judgment

Build an acceptance matrix from the complete task, not only the latest proposed patch. Mark each row as demonstrated, outstanding, or no longer applicable with a reason and evidence. A partial implementation can merge if authorized, but the task remains open until its required outcome is complete.

Audit scope against the exact delivered revision or pin. Compare file hashes for the named final tree, including unchanged files used to waive a scope row; a stale default build cannot support a scope verdict.

Do not treat every wrapper, empty package file, or small module as waste. Check dynamic imports, packaging behavior, stable boundaries, and real consumers before deletion. Do not replace a narrow problem with a generic framework or an incomplete schema translator. Keep tightly coupled contract changes together.

If a task's proposed implementation is obsolete but its outcome already holds, document the current evidence and let the coordinator decide within the existing scope. Do not invent a need for operator approval for routine architecture choices; ask only when a real product, safety, scope, or authorization decision is missing.

For upstream/downstream work, fix provider-neutral behavior in its owning source. Consume a published revision that retains the currently consumed ancestry or an explicitly justified equivalent history; a newer-looking commit can still omit deployed fixes. Verify both ancestry and required content, then test the final composition. A test-only repair on an integration branch may not belong in upstream if those tests do not exist there.

Record separate author and reviewer identities, and treat a shared or unestablishable identity as leaving independent review outstanding — a finding marked unverifiable cannot contribute to a pass.

## Verify a handoff before accepting it

Verify the claimed revision and tree from the files (`git hash-object` for changed blobs; compare tree and commit with the remote) and build from the exact upstream pin the candidate recorded; a stale checkout or symlink makes missing imports and deletions look valid. A reviewer who removes a symbol or module must search its importers and runtime entry points first. Before merge, verify the PR base, exact head, required CI jobs and their artifacts; a green job from another revision, or an early gate, is not evidence for the candidate.


## Failure patterns

- **Many “easy” slices left the original tasks open.** — Assignments optimized patch size instead of full acceptance. Audit complete issue scope before selection; keep a per-row acceptance matrix. Evidence: Remaining rows and actual task closures.
- **Several ready items waited on the same prerequisite repair.** — Each delivery path treated the shared blocker as separate work. Rule above. Evidence: One repair, fewer duplicate investigations, and reduced blocked time.
- **A local branch appeared current but omitted a provider-side update.** — A remote-tracking ref was treated as live state. Refresh and verify the provider remote before calling a ref current. Evidence: Provider-side head and local ref agree.
- **Validation passed against the wrong source.** — Build directories were stale, or overlays contaminated the mirror. Use immutable inputs and a distinct composition per check; record source revisions. For generated artifacts, compare fresh generator output with the shipped artifact, rather than loading the same artifact twice. Evidence: File hashes, composition manifest, reproducible checks.
- **A “pre-existing” test failure disappeared after composition.** — Baseline used an old disposable build. Rule above. Evidence: Same failing test and same context on baseline.
- **Local typing passed but CI rejected the same test file.** — Single-file inference and local settings differed from CI. Match project-wide check scope, config, tool version, and dependencies. Confirm imports resolve and reproduce the known CI failure on the old revision before trusting a repaired local result. Evidence: Changed-file diagnostics in the full context.
- **Focused tests passed, but publication failed on cheap repository-wide checks.** — The delivery plan omitted checks outside the changed module. Read the required CI contract early; run its cheap applicable checks before publication, and watch whether failed publication attempts fall. Fix new violations without weakening checks Evidence: Fewer failed publication attempts and less CI repair time.
- **A gate printed PASS despite new type errors.** — Typing was informational inside a broader gate. Read the gate contract and its diagnostics; wait for required CI checks. Evidence: Explicit type result and final required-check state.
- **Tests passed while the production path bypassed the new abstraction.** — Tests exercised only helpers or mocked the changed behavior. Rule above. Evidence: Production consumer and relevant boundary test.
- **Review approved an old revision.** — Amendments were not coupled to review records. Rule above. Evidence: Reviewed revision equals delivered revision.
- **An upstream update dropped previously consumed fixes.** — The candidate was newer but on divergent ancestry. Rule above. Evidence: Ancestry, required content, composed tests.
- **A provider refactor retained duplicate selection variables.** — Compatibility tests passed, but acceptance required one observable selection value. Record the observable configuration contract before splitting resolver and config-writer work; allocate both sides against that contract, and do not call symbol centralization a full migration Evidence: One accepted selection value and tests for the contract.

- **A review approved a change whose tests nobody executed.** — The reviewer's environment lacked prerequisites, so approving on reported evidence was cheaper than running the suite. Make runnable prerequisites a precondition for review tasks, and mark a verdict resting on reported rather than reproduced evidence as provisional Evidence: approvals carrying no execution.
- **A partially executed run was reported as verified.** — A consent or permission gate blocked one step and the rest of the run continued, so the summary read as fully verified. Require every report to list steps skipped for denied consent or permission as an explicit unverified-gap section, and have the reviewer treat an unnamed skipped step as unverified Evidence: a verified claim that covers a step that did not execute.
- **Architecture cleanup deleted a meaningful seam or introduced a broad translator.** — Line reduction replaced contract analysis. Check consumers, packaging, invariants, and ownership; prefer the narrow correct change, and confirm the actual duplication fell Evidence: Preserved behavior with less actual duplication.
---

Related: [the assignment record](assignment-and-handoff.md) · [publication and acceptance](publication-and-acceptance.md) · [worker lifecycle](worker-lifecycle-and-resources.md)

## Handle an amendment

Treat feedback as a small checkpoint amendment: validate the amended revision, obtain fresh review, and publish only with a revision receipt when authorized. Continue the delivery path without waiting for the campaign to end. Do not create a new framework or duplicate guidance to process routine feedback.

## Diagnose a CI failure

When CI fails, read the failing job's artifact, step and log before changing code, reproduce the gate on the exact composition, and give one owner the smallest supported repair. A skipped, pending or early gate says nothing about later tests.
