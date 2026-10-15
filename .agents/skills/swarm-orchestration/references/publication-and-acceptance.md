# Publication and acceptance

Read before pushing, merging, or closing: remote receipts, the distinction between merged, deployed and live, and the closure reconciliation.

## Publication and acceptance

Refresh actual remote state before publication and again before merge. Verify repository identity, base branch, exact head, independent review, required checks, and current task state. Independent review means the recorded reviewer identity differs from the recorded author — the identity is whatever actor identifier the runtime or hosting service can actually distinguish, not a role label. A shared, missing, or unestablishable identity leaves independent review outstanding, and a finding marked unverifiable cannot contribute to a pass. A comment saying “merged” is weaker evidence than the hosting service's live merge record. Never merge while required checks are pending.

These acceptance rules apply to every delivery route — a CLI push, a branch, or a composed commit through an API — not only to API composition. Green CI proves automated checks passed, not that the change is right: keep an independent review of the behavior and data-flow invariant (for example, whether an audit transaction is actually committed). Because an approval pinned to an exact revision is voided by every amendment, batch small fixes into one revision before requesting review, cap the open fix-chains per branch, and require fresh review after any amendment, so the gate is not serialized behind an amend-then-re-review loop.

If transport fails, diagnose the tool error before changing the patch. Use another supported publication route only within the same permissions and authorization. For object-based Git APIs, verify every returned blob, tree, and commit ID against the locally reviewed objects; update only the intended feature ref, without force. Do not publish stale request files after an amendment or write a default-branch ref as a shortcut. Keep such a route exceptional; do not build a publication service for a one-off fault.

Repository merge, deployed revision, and live behavior are separate facts. Claim each only with matching evidence. Do not invent deployment or live-acceptance requirements for a task that does not need them. Read-only acceptance checks can proceed under existing authorization; deployment needs its own applicable authorization. An unreachable environment is a blocked acceptance check, not a pass. Keep useful independent work moving while recording the precise blocked step.

Before closure, reconcile every acceptance row against the live task and delivered revision. Confirm the hosting service reports the intended PR or artifact as merged or released, verify the exact merge or delivery revision, and check that no required acceptance row remains open. Post delivery links plus evidence in the task record, then refresh the campaign totals. Do not count partial slices, duplicate housekeeping closures, or unrelated contributors as this swarm's completed work.

## Composing a commit through a Git API

Use the exact remote parent and pass its **tree** SHA as `base_tree` — a commit SHA is not a tree SHA. Compare the new tree's changed paths with the intended manifest before updating any ref, and re-read the ref afterwards.


## Failure patterns

- **“Merged” appeared in a report while the PR remained open.** — Narrative status was trusted without a fresh remote check. Verify hosting-service state before reporting or closing — check the merge timestamp and merge revision. Evidence: the procedure above.
- **A publication retry used a stale object manifest.** — Requests were generated before the final amendment. Regenerate from the final revision and verify returned object IDs Evidence: Exact final tree/commit and intended feature ref.
- **An "independent review" returned a verdict from the same actor that wrote the change.** — Independence was treated as a role label rather than a property of the artefact, and one shared identity puppets every agent, so "reviewer" carried no distinguishing identifier. Require an independent reviewing actor and record who authored and who reviewed, as structured fields the delivery gate can compare. If the identity is shared, or independence cannot be established, record that limitation and leave independent review outstanding — disclosing a shared identity does not satisfy the requirement, and a finding marked unverifiable must not contribute to a pass Evidence: a self-reviewed change whose record nonetheless shows a reviewer.
- **Every small fix voided an approval and serialized the gate.** — Reviews were pinned to an exact revision behind an amend-then-re-review loop with no batching. Rule above. Evidence: successive approvals on one branch.
- **Two concurrent writers raced on one shared integration branch.** — Rebase-then-push against a mutable shared target has no per-branch reservation, and each accepted merge invalidates every other branch at once. Fetch and rebase immediately before push, push only with force-with-lease, exclude agent-owned branches from bulk refresh sweeps, and re-read the head after the base moves Evidence: repeat non-fast-forward rejections.
- **A merge landed carrying conflict-marker text that nobody inspected.** — Approval verified the source branch and the success of the merge command, never the content of the merge result on the target ref. After every merge, fetch the target ref and check the changed files for conflict markers before treating the merge as delivered. Evidence: merges whose result was never read back.

---

Related: [validation and review](validation-and-review.md) · [the assignment record](assignment-and-handoff.md) · [measurement](measurement.md)

## Receipts before delivery

Before delivery, refresh the task state, target branch, remote, required checks, and exact head. Apply repository rules and existing user authorization. Close the task only when every required acceptance row has evidence. Keep partial progress visible without counting it as completion.
