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
- Batch only the merges into a shared integration branch that triggers deploys. If pushes there cancel one another's deploys, leave nothing verified, or hide a slow step, merge in bounded batches (about 30 minutes). Run one combined test run per batch on the composed tree.
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

A worker may not see deploys. When a task needs live proof, have an authorized observer give the live revision with its evidence. Then resume the acceptance owner with a message that names the revision and the access its checks need. Without that message the proof never runs.

## Close on evidence

1. Refresh task state, target branch, required checks and exact head.
2. Check every acceptance row against the live task and the delivered revision.
3. Confirm that the hosting service reports the PR or artifact as merged or released.
4. Close only when each required row has evidence. Post delivery links and evidence in the task record.
5. Refresh the campaign totals.

Partial slices, duplicate housekeeping closures and unrelated contributors do not count as this swarm's completed work.

When the open count stays flat while workers finish, compare opened, closed and reopened counts. If delivered items pile up unclosed, acceptance is the bottleneck. Run a verify-and-close sweep, partitioned across workers. Each worker takes a slice, verifies each item against the integration branch, closes done items with evidence, merges duplicates into one survivor, and leaves a status line on the rest. Tell test workers to search for an existing item and comment on it, not to file a duplicate.

## Failure patterns

- **"Merged" appeared in a report while the PR was open.** — Narrative status was trusted. Rule: check the hosting service. Evidence: merge timestamp and revision.
- **A publication retry used a stale object manifest.** — Requests predated the final amendment. Rule: regenerate from the final revision. Evidence: exact final tree and ref.
- **Two writers raced on one shared integration branch.** — Rebase-then-push has no per-branch reservation, and each merge invalidates the others. Rule: fetch, rebase, force-with-lease, re-read. Evidence: repeat non-fast-forward rejections.
- **A merge landed with conflict markers that nobody read.** — Approval checked the source branch and the command's success, not the result. Rule: read the result back. Evidence: merges never read back.
- **A local pass was reported as live acceptance.** — Implementation, integration, deploy and acceptance were collapsed. Rule: prove each stage. Evidence: deployed revision and a real acceptance artifact.
- **Pushing after every lane made deploys cancel each other.** — Newest wins in the queue, so nothing was verified, and a slow step stayed hidden. Rule: bounded batches; count only completed, uncancelled runs; re-baseline after a cadence change. Evidence: completed runs per hour.

Next: [6. Measure](measure.md) · Related: [4. Review](review.md)
