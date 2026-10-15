# Lessons and failure patterns

Observed multi-agent delivery failures: portable causes and corrections, not a claim that every campaign needs the same pool or tools.

| Observation | Cause | Correction |
|---|---|---|
| More authors, more patches, fewer closures. | Review, CI repair and publication saturated. | Limit active items; reserve reviewers; clear the ready queue before adding code. |
| The coordinator kept planning improvements while ready work waited. | Process work had no delivery bound. | Make one small improvement against the current bottleneck, apply it to the next item, resume delivery; delegate preparation around the coordinator's decision. |
| Easy slices left the original tasks open. | Assignments optimised patch size, not full acceptance. | Audit complete scope before selection; keep a per-row acceptance matrix. |
| A worker started an already-closed issue. | Assignment used an old backlog snapshot. | Refresh task state, comments, claims and linked work at assignment time. |
| A local branch looked current but omitted a provider-side update. | A remote-tracking ref was treated as live state. | Refresh and verify the provider remote before calling a ref current. |
| A worker named after a model did not prove model identity. | Labels were mistaken for runtime metadata. | Record requested and observed identity, or mark it unverified. |
| An idle worker never acted on a new message. | The messaging operation did not restart a finished turn. | Use the runtime's follow-up or resume operation and confirm the state change. |
| Nested or CLI workers created hidden load. | Only direct children were counted. | Track descendants, processes, memory and shared environments in one capacity budget. |
| Temporary builds filled the filesystem and stopped even cleanup. | No space budget or cleanup owner. | Check the filesystem before expansion; retire owned disposable builds once revisions and evidence are recorded. |
| A patch landed in another task's clone. | Ownership and workspace were implicit. | Put path, branch, baseline and allowed scope in every assignment; isolate the mistaken patch. |
| Validation passed against the wrong source. | Stale build directories, or overlays contaminating the mirror. | Use immutable inputs and a distinct composition per check, recording revisions; compare fresh generator output with the shipped artefact. |
| A "pre-existing" failure vanished after composition. | The baseline used an old disposable build. | Reproduce on fresh pristine inputs before classifying it. |
| Local typing passed; CI rejected the same file. | Single-file inference and local settings differed from CI. | Match project-wide scope, config, tool version and dependencies; confirm imports resolve, and reproduce the known CI failure on the old revision before trusting a repair. |
| Focused tests passed; publication failed on cheap repository-wide checks. | The plan omitted checks outside the changed module. | Read the CI contract early and run its cheap applicable checks before publication; fix violations without weakening checks. |
| Several items waited on one prerequisite repair. | Each path treated the shared blocker as separate work. | One repair owner, then reuse the verified revision; recheck each composition. |
| A gate printed PASS despite new type errors. | Typing was informational inside a broader gate. | Read the gate contract and its diagnostics; wait for the required checks. |
| Tests passed while the production path bypassed the new abstraction. | Tests exercised helpers or mocked the changed behaviour. | Trace real callers; verify the changed observable behaviour. |
| Review approved an old revision. | Amendments were not coupled to review records. | Record the exact head; review the final delta and rerun affected checks. |
| An upstream update dropped previously consumed fixes. | The candidate was newer but on divergent ancestry. | Preserve consumed history and validate the final composed tree. |
| "Merged" appeared in a report while the PR was open. | Narrative status trusted without a fresh remote check. | Verify hosting-service state before reporting or closing. |
| A publication retry used a stale object manifest. | Requests were generated before the final amendment. | Regenerate from the final revision and verify the returned IDs. |
| Architecture cleanup deleted a meaningful seam or added a broad translator. | Line reduction replaced contract analysis. | Check consumers, packaging, invariants and ownership; prefer the narrow correct change. |
| A provider refactor kept duplicate selection variables. | Compatibility tests passed but acceptance required one observable value. | Record the observable contract before splitting resolver and writer; allocate both sides against that contract, and do not call symbol centralisation a migration. |
| A local pass was reported as live acceptance. | Implementation, integration, deployment and acceptance were collapsed. | Track and prove each required stage separately. |
| Reports survived only in temporary paths. | The recovery record was incomplete. | Persist decision, revision, evidence, remaining scope and next owner in the tracker. |
| A "16-agent" campaign had one agent running. | Registered agents were counted after their turns ended; freed slots were not refilled. | Query live states before each capacity report and after completions; assign and verify useful follow-up, or report the shortfall. |
| All three workers finished while review and acceptance remained. | No checkpoint to replan before waiting or reporting. | At completion, before CI waits and before status replies, refresh capacity and ready work; give each freed slot an independent task or record its constraint. |
| A credential helper and an environment dump printed live secrets. | Diagnostics requested whole secret-bearing payloads; post-hoc filtering missed values. | Request only the non-secret metadata needed and filter before output; after exposure report the scope without repeating the value and follow the operator's decision on rotation. |

## Turn experience into an improvement

After a costly failure, find the first missing fact that would have prevented the wasted work and put it in the assignment, log, check or handoff closest to the decision; then measure whether it reduced rework or wait.

Write a narrow rule supported by the failure. Never turn a temporary environment fault into a product workaround, an example pool size into a universal limit, or a single campaign into a claimed speedup. Keep the entry point short, add detail here only when it changes future decisions, and periodically remove rules that are obsolete or already enforced by tooling.
