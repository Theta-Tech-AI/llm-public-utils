# 5. Integrate and deliver

Read before you push, merge, bump a dependency, close, or claim that something is live.

## Refresh before you publish or merge

- Refresh the remote before publication and again before merge: repository, base branch, exact head, independent review, required checks, task state.
- The hosting service's merge record outranks a comment that says "merged". Check the merge timestamp and revision.
- Never merge while a required check is pending. A green job from another revision is not evidence for the candidate. Green CI is not a review of the behavior.
- After every merge, fetch the target and read the changed files for conflict markers. A successful merge command says nothing about the result.

## Land in checked batches

**One integration owner lands, so the coordinator is not on every merge.** It can be a worker or a script. Authors hand it review-passed heads. It runs the batch below, pushes, and tells each author the pushed head, so that the author runs its own live check. Observation: workers could not land their own changes, so every "proven live" waited for the coordinator's push, the next deploy and a resume message. The batch:

1. Merge the integration branch and the named branches into one fresh tree. Stop at the first conflict.
2. Run the combined checks in order (tests, type-check and build, the deploy preflight when deploy files changed), one at a time on that tree.
3. Run the push gate. Push only on green. **Never push on a red gate, whatever its reason**: one gate failed on an uninitialised submodule, the push script did not call the gate, and a change went out on red. Fix the environment and rerun.
4. Print the pushed head; record it on the board.

Before you choose a cadence for a branch that triggers deploys, read the queue configuration and trace one running and one superseded run: what does a new push cancel? If only waiting runs are replaced, push each checked batch at once. If running runs are cancelled, batch by measured run time. Overlapping branches share one batch and one combined test run. Fetch and rebase just before a push, and re-read the head after the base moves. A peer that owns merges keeps them: do not push to its branches.

## Merged, deployed and live are three facts

Claim each with its own evidence. An unreachable environment is a blocked check, not a pass. A deploy needs its own authorization.

**Merged upstream is not live.** A fix reaches a consumer that pins the dependency only after the pin bump. Observation: three upstream merges waited about an hour, each worker assuming another session owned the bump. Rule: "merged upstream, waits dependency bump" is its own board stage, and the bump gets an owner the moment the first upstream merge lands.

A worker may not see deploys. When a task needs live proof, an observer gives the live revision with evidence, and the coordinator messages the acceptance owner with that revision. Without the message the proof never runs. Long acceptance runs go to a quiet promoted environment, not the integration environment that every batch rolls.

## Close on evidence

1. Refresh the task state and the delivered revision.
2. Verify the recorded closure event ([1](establish.md)) and every acceptance row required before it.
3. Close with the revision and evidence. If a live check is left, keep the board row with `live_check` and its owner ([0](coordinator-loop.md), step 7). A failed check reopens the item.

Deferral is a scope decision, not acceptance. Follow the operator's tracker convention.

**When the open count stays flat while workers finish**, delivered work is waiting for acceptance. Compare opened, closed, reopened and moved items. Then run a partitioned verify-and-close sweep. Each worker checks a slice of the open set against the integration branch, closes done items with evidence, merges duplicates into one survivor, and leaves one status line on the rest. Test workers search for an existing item before they file one.

## Publish when transport fails

Diagnose the tool error first. For an object-based Git API: use the exact remote parent and its tree SHA as `base_tree`; compare the new tree's changed paths with the intended manifest; verify every returned ID; update only the feature ref, without force. Keep this route exceptional.

## Failure patterns

- **A cadence was set from an assumed queue policy, twice in opposite directions.** Rule: trace the queue first; count only completed runs.
- **One HTTP 429 from the system's own rate limiter failed a deploy.** A preflight treated "slow down" as final. Rule: probes retry 429 like gateway errors.
- **Live tests kept being cut by the team's own deploys.** Twenty batches rolled the shared environment under long runs. Rule: long runs on a quiet promoted environment.

Next: [6. Measure](measure.md)
