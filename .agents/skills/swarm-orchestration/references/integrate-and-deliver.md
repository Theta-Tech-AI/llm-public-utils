# 5. Integrate and deliver

Read before you push, merge, close, or claim that something is live.

## Refresh before you publish or merge

- Refresh the actual remote state before publication and again before merge. Verify repository, base branch, exact head, independent review, required checks and current task state. Check a PR's base branch before you merge.
- The hosting service's merge record outranks a comment that says "merged". Check the merge timestamp and merge revision.
- Never merge while a required check is pending. A green job from another revision, or an early gate, is not evidence for the candidate.
- Green CI shows that automated checks passed. It does not show that the change is right. Keep an independent review of the behavior and data-flow invariant (for example, whether an audit transaction commits).
- After every merge, fetch the target ref and read the changed files for conflict markers. A successful merge command says nothing about the merge result.
- These rules apply to every route: a CLI push, a branch, a composed commit through an API.

## Push and batch

- Push each green slice to its own branch at once.
- Before you choose a cadence for a shared integration branch that triggers deploys, read the queue configuration and trace one running and one superseded run. Record what a new push cancels: running work, waiting work, both or neither. If the running run survives and only the newest waiting head remains, push each checked batch at once, and verify that the newest head holds the earlier changes. If pushes cancel running work, merge in bounded batches sized from measured run time. A rehearsal that needs two deployed states reserves both runs. Run one combined test run per batch on the composed tree.
- Fetch and rebase just before a push. Push with force-with-lease only to your own branch. Exclude agent-owned branches from bulk refresh sweeps. Re-read the head after the base moves.
- A peer gate session that owns merges keeps them. Never push to its branches. Answer its questions explicitly, and cite the operator's decision where one exists. Move a slow item to the next bump. Do not hold a bump for it.
- Cancel a queued CI run only when its SHA is superseded by the current head. Keep the current head's required checks.

## Publish when transport fails

Diagnose the tool error before you change the patch. Use another publication route only within the same permissions. For object-based Git APIs:

- Use the exact remote parent. Pass its tree SHA as `base_tree`. A commit SHA is not a tree SHA.
- Compare the new tree's changed paths with the intended manifest before you update any ref. Re-read the ref afterwards.
- Verify every returned blob, tree and commit ID against the locally reviewed objects.
- Update only the intended feature ref, without force. Never write a default-branch ref as a shortcut. Regenerate request files after every amendment.
- Keep this route exceptional. Do not build a publication service for one fault.

## Merged, deployed and live are three facts

Claim each one only with its own evidence. Read-only acceptance checks run under existing authorization. A deploy needs its own authorization. An unreachable environment is a blocked check, not a pass. Keep independent work moving, and record the precise blocked step.

Merged upstream is not live: a fix reaches the product only after the dependency pin bump. Track "merged upstream, waits pin bump" as its own stage. Give the pin bump an owner when the first upstream merge lands; otherwise each worker assumes another session owns it and merges wait.

A worker may not see deploys. When a task needs live proof, have an authorized observer give the live revision with its evidence. Then resume the acceptance owner with a message that names the revision and the access its checks need. Without that message the proof never runs.

## Close on evidence

1. Refresh the task state and the exact delivered revision.
2. Verify the item's recorded closure event ([1](establish.md)) on the branch, the hosting service, the release record or the live environment.
3. Verify every acceptance row required before that event. Do not substitute a nearby test or an unread artifact.
4. Close with the revision and evidence. Link the checks that follow closure, with their owners and triggers. Reopen on a failed check when the recorded policy says so.
5. Refresh the campaign totals.

Partial slices, duplicate housekeeping closures and unrelated contributors do not count as this swarm's completed work.

Deferral is a scope decision, not acceptance. Follow the operator's tracker convention. Unless told otherwise, leave deferred work open, move it to its agreed scope with the reason and a deferral label, and keep the links to finished slices.

When the open count stays flat while workers finish, compare opened, closed, reopened and moved items first. If delivered work waits for closure, run a partitioned verify-and-close sweep. Each worker reads the full task and acceptance record, then checks the delivered revision. For an item that has an active owner, reconcile with the owner's latest findings before you close it. A disagreement leaves the item open with one named next action. Do not waive a row, move scope or defer to improve the count. A duplicate closure names the survivor and keeps its remaining rows. Comment on a remaining item only when the evidence or next action changed. Tell test workers to search for an existing item before they file one.

## Failure patterns

- **"Merged" appeared in a report while the PR was open.** — Narrative status was trusted. Rule: check the hosting service. Evidence: merge timestamp and revision.
- **Two writers raced on one shared integration branch.** — Rebase-then-push has no per-branch reservation, and each merge invalidates the others. Rule: fetch, rebase, force-with-lease, re-read. Evidence: repeat non-fast-forward rejections.
- **A merge landed with conflict markers that nobody read.** — Approval checked the source branch and the command's success, not the result. Rule: read the result back. Evidence: merges never read back.
- **A local pass was reported as live acceptance.** — Implementation, integration, deploy and acceptance were collapsed. Rule: prove each stage. Evidence: deployed revision and a real acceptance artifact.
- **A cadence was set from an assumed queue policy.** — One run held pushes for a belief that pushes cancel deploys, and the queue did not. Another run pushed every lane into a queue that did cancel. Rule: trace the queue first; count only completed, uncancelled runs; re-baseline after a change. Evidence: completed runs per hour.

- **Live tests on the shared environment kept being cut by the team's own deploys.** — Twenty batches in an evening each rolled the environment while long end-to-end runs and samplers were in flight. Rule: run long acceptance runs on a quiet promoted environment (a release candidate), and keep the busy integration environment for quick proofs. Evidence: runs restarted or abandoned under update overlays.
- **One transient answer from the system's own rate limiter failed a deploy.** — A pre-flight probe treated HTTP 429 as final. Rule: a probe retries "slow down" answers like gateway errors; only a real refusal is final. Evidence: a deploy that failed with the application healthy.

- **A change went out on a red gate because the push script did not run the gate itself.** — The gate failed on the environment (an uninitialised submodule), and the push went ahead. Rule: never push on a red gate, whatever its reason; fix the environment and rerun; push scripts call the gate. Evidence: a push after a red gate.

Next: [6. Measure](measure.md) · Related: [4. Review](review.md)
