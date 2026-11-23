# 4. Review and validate

Read before you accept a handoff, approve a revision, or diagnose a failing check.

## Keep author and reviewer apart

- Independent review means that the recorded reviewer identity differs from the recorded author. Use an actor identifier that the runtime or hosting service can tell apart. A role label is not an identity.
- A shared, missing or unestablishable identity leaves independent review outstanding. Disclosing a shared identity does not satisfy the rule. A finding marked unverifiable cannot contribute to a pass.
- Record both identities as structured fields that the delivery gate can compare.
- A review approves one exact revision. Every amendment voids it. Batch small fixes into one revision before you ask for review, and cap the open fix-chains per branch. After an amendment, validate the new revision, get a fresh review of the delta, and continue delivery without waiting for the campaign to end.
- Make runnable prerequisites a precondition for a review task. Mark a verdict that rests on reported, not reproduced, evidence as provisional.
- Require each report to list steps that were skipped for denied consent or permission, as an "unverified" section. Treat an unnamed skipped step as unverified.

## Validate the source you deliver

- For layered repositories, record the upstream commit, overlay commit, generated inputs and composition procedure. Keep the upstream snapshot immutable. Apply overlays into a separate disposable tree. Copying overlays into a mirror changes the baseline and can make a deletion or duplicate check pass falsely.
- Use a fresh, empty composition for each candidate and each amendment. Never use a populated scratch tree as evidence. Verify the base revision and every pin before you test.
- Confirm that the changed paths match the reviewed revision. Verify files with hashes (`git hash-object`) and compare tree and commit with the remote. Do not validate an old build directory or unstated local changes.
- A failure is "pre-existing" only after you reproduce it on a pristine baseline with the same dependencies and composition. Keep other workers' work intact while you do so.
- Run the checks in the same project-wide context as CI: type-check scope, configuration, tool version, dependencies. Single-file inference misses errors. A gate can print type errors and still exit 0; read the diagnostics and the gate contract.
- Run full base-to-head gates, not only checks for the last commit. Include the cheap early CI checks (policy, documentation links, comments, whitespace) before publication. Keep the manifest and check output with the task record.
- Test the behavior that the task changes. A page test that mocks the polling hook cannot show polling cadence. A helper test cannot show that production uses the helper. Check real callers, side effects and error paths. For generated artifacts, compare fresh generator output with the shipped artifact.
- Name the fixture that exercises each required outcome. If it is missing, create an authorized disposable fixture. Do not wait for a rare state to occur. A failure-path run or an empty error log cannot prove a success path. Read the required final artifact before you mark a row demonstrated.
- Do not widen error baselines, add ignores, or weaken assertions to hide a regression. Fix the cause, or document a demonstrated intentional contract change.
- After a code change, rerun the affected checks. Reuse evidence only when its source and assumptions still match. A green review does not survive a conflicting merge: rerun on the merged head. Do not rerun expensive suites after a prose edit.

## Diagnose a failing check

1. Read the failing job's artifact, step and log before you change code.
2. Decide which it is: an early gate, a test, or infrastructure. A skipped, pending or early gate says nothing about later tests.
3. Reproduce the gate on the exact composition.
4. Give one owner the smallest supported repair. When items share a failing prerequisite, one owner repairs it, and each resulting composition is validated separately.

## Judge scope and design

- Build the acceptance matrix from the whole task, not from the latest patch. A partial implementation may merge when authorized. The task stays open until its required outcome is complete.
- Audit scope against the exact delivered revision. Compare file hashes of the final tree, including unchanged files that waive a scope row.
- Before you delete a wrapper, empty package file or small module, check dynamic imports, packaging, stable boundaries and real consumers. A reviewer who removes a symbol first searches its importers and runtime entry points.
- Prefer the narrow correct change. Do not replace a narrow problem with a generic framework or schema translator. Keep tightly coupled contract changes together.
- If the proposed implementation is obsolete but the outcome already holds, record the current evidence and let the coordinator decide. Ask the operator only for a real product, safety, scope or authorization gap.
- Fix provider-neutral behavior in its owning source. Consume an upstream revision only when it keeps the ancestry you consume now, or an explicitly justified equivalent. A newer commit can omit deployed fixes. Check ancestry and required content, then test the final composition. A test-only repair on an integration branch may not belong upstream.
- Before you build an upstream extension, read that project's contribution rules and name the real consumer. Record producer and consumer changes together. For an adoption, list the removed or renamed public symbols and routes, changed signatures, schemas, configuration, generated artifacts and startup requirements, from the final producer diff. Give each consumer adaptation an owner and land coupled changes together. Run the consumer's real startup check on the composed revision.
- Debris from stress or test scripts can look like a bug or a data leak. Trace the write in the audit trail first. Archive the debris (reversible) and do not edit records. Then check whether it exposes a real missing guard.

## Failure patterns

- **Validation passed against the wrong source.** — Build directories were stale, or overlays contaminated the mirror. Rule: immutable inputs, a distinct composition per check. Evidence: file hashes, composition manifest.
- **A "pre-existing" failure disappeared after composition.** — The baseline was an old disposable build. Rule: pristine baseline. Evidence: same failing test, same context.
- **Focused tests passed but publication failed on cheap repository-wide checks.** — The plan omitted checks outside the module. Rule: read the CI contract early. Evidence: fewer failed publication attempts.
- **Tests passed while production bypassed the new abstraction.** — Tests used helpers or mocks. Rule: check production consumers. Evidence: a boundary test on the real path.
- **An "independent review" came from the actor that wrote the change.** — Independence was a role label, and one shared identity served every agent. Rule: structured author and reviewer fields. Evidence: a self-reviewed change whose record shows a reviewer.
- **A regeneration silently dropped a merged branch's hand edit.** — One lane edited a generated file by hand; another lane's merge regenerated it from the template. Rule: a generated file changes only through its generator; after any regeneration at integration, diff each generated file against every merged branch's version and move hand edits into the template. Evidence: a behaviour lost with all checks green.
- **A worker's premise came from a test report that misread the product.** — A coordinator routed an operator decision on "16 signatures" that the code showed was 2. Rule: check a reported defect against the code before turning it into a decision or a brief. Evidence: a decision asked and then withdrawn.
- **Every small fix voided an approval and serialized the gate.** — No batching. Rule: batch fixes; cap fix-chains. Evidence: successive approvals on one branch.
- **A partially executed run was reported as verified.** — A consent gate blocked one step and the run went on. Rule: explicit unverified-gap section. Evidence: a "verified" claim that covers a step that did not run.
- **An upstream update dropped previously consumed fixes.** — The candidate was newer but on divergent ancestry. Rule: ancestry plus content. Evidence: composed tests.
- **A provider refactor kept duplicate selection variables.** — Compatibility tests passed, but acceptance needed one observable value. Rule: record the observable contract before you split work. Evidence: one accepted value and tests for it.
- **Architecture cleanup deleted a meaningful seam or added a broad translator.** — Line count replaced contract analysis. Rule: check consumers and invariants. Evidence: behavior kept, duplication down.
- **A run reported success having produced almost nothing.** — The status vocabulary folds partial progress into warnings. Rule: assert produced against expected counts before you accept a success status. Evidence: completions with empty output.

Next: [5. Integrate and deliver](integrate-and-deliver.md)
