# Planning and capacity

Read before dispatch, and again when a stage saturates: choosing the delivery set, sizing the pool, and re-ranking as work completes.

## Choose work before choosing worker count

The useful pool is bounded by independent tasks, reviewer throughput, integration throughput, and shared resources. Count active descendants and CLI processes as well as direct managed children. Runtime limits can apply to the whole tree; nesting is not proof of extra capacity.

Start with a small delivery set and reserve reviewer capacity. Set explicit WIP limits for implementation, review, integration, and acceptance. Choose the count from observed completion and review times, not a sample pool size. Increase implementation work only while completed items flow through review and integration without a growing wait. A saturated review queue is a reason to stop new implementation intake and reassign available qualified agents to independent review.

Give spare agents work that clears the current bottleneck: reproduce a CI failure, check full issue scope, prepare an acceptance fixture, inspect a dependency, or review a ready change. Do not create speculative work to keep the dashboard busy.

Watch large tasks and the dependency path. Schedule an aging item or a prerequisite when it unlocks more accepted work than another easy closure. A task with three repositories and live acceptance can be slower to finish than a larger local change.

## Reassign at transitions

For each free agent, ask which assignment most reduces remaining time to the next accepted outcome or unlocks several outcomes. Use current evidence, not the task's original estimate or time already spent. A nearly finished task can still be a poor next choice if its remaining acceptance is inaccessible.

Prefer, in order, ready work that can pass the final delivery step; small repairs that release reviewed work; reviews and acceptance checks for complete implementations; prerequisites that unblock several items; then new independent implementation. A whole issue close outranks a smaller patch when the patch would leave required acceptance rows or dependencies open. Change this order when aging, severity, or a critical dependency justifies it. Preserve the user's stated priorities.

Re-rank when a worker finishes, a reviewer finds a defect, CI completes, or access changes. Do not leave the original assignments fixed for the whole campaign. Estimate implementation, review, repair, integration, and acceptance separately; the slowest available stage controls useful intake. Parallelize preparation around a serialized merge decision, while keeping one owner for that final decision.

At each completion notice, refresh the runtime roster and replace finished assignments that still have useful independent work. Record `running`, `completed`, and `idle` separately with the next task for each reusable slot. A follow-up task must trigger a new turn and its running state must be checked. Count a one-shot status check as a completed task, never as an active worker for the rest of a CI wait.

Monitor aging work already in progress as well as new candidates. If implementation finishes faster than review, move qualified independent agents to reviews. If required CI is simply running, prepare the next reviewed delivery instead of launching duplicate checks. If integration depends on a coordinator decision, supply a compact decision packet so the coordinator can clear it promptly.

When a merge train leaves CI runs queued for old branch commits, compare each run SHA with the current branch or PR head before canceling it. Cancel only superseded queued runs; preserve the current head's required checks. This frees runner capacity without treating an old green run as evidence for the candidate.

## Assign a complete unit

The assignment should state the outcome, allowed files or artifact boundary, source baseline, excluded scope, acceptance checks, review destination, and publication authority. Ask for a concrete next checkpoint, not unlimited investigation.

For two tasks that touch the same contract, use one owner to decide the contract first. Delegate independent callers or tests after that decision is stable. Nested delegation is useful when a child has a concrete subtask and its parent can still do useful independent work. The parent owns reconciliation before reporting completion to the coordinator.

Track descendants in the same board. Do not let nested authors each start their own unrelated backlog. A tree of supervisors that only waits adds handoff delay without delivery value.

## Refill at each completion

At each worker completion, before a CI/deploy wait, and before a status reply, refresh the live roster and ready work, then re-rank remaining acceptance and independent tasks. For each freed reusable slot, record its next useful bounded assignment or the specific resource limit, full downstream WIP stage, or lack of safe work. Start and verify useful independent work while it remains; a CI/deploy wait alone does not block unrelated review, repair, or acceptance. Keep reviewer, integration, and acceptance WIP limits and one owner per live browser/session; do not create busywork to preserve a worker count. A queued message may not restart a completed worker; use the runtime's follow-up or spawn operation and verify that it is running.


## Failure patterns

- **More authors produced more patches but fewer closures.** — Review, CI repair, and publication were saturated. Limit active delivery items; reserve reviewers; clear the ready queue before starting more code. Evidence: Closures/hour, review age, accepted work, rework.
- **The coordinator kept planning improvements while ready work waited.** — Process work had no delivery bound. Make one small improvement aimed at the current bottleneck, apply it to the next item, and resume delivery. Delegate preparation around the coordinator's final decision, and measure the improvement by shorter queue age and more accepted outcomes rather than more process artifacts
- **All three workers completed while review and acceptance work remained, and refill was deferred during CI/deploy waiting.** — The coordinator had no checkpoint to re-plan before waiting or sending status. Rule above. Evidence: Live roster, next assignment or constraint per freed slot, and movement in review or acceptance.
- **A local pass was reported as live acceptance.** — Implementation, integration, deployment, and acceptance were collapsed. Track and prove each required stage separately. Evidence: Deployed revision and real acceptance artifact.

---

Related: [worker lifecycle](worker-lifecycle-and-resources.md) · [the assignment record](assignment-and-handoff.md) · [measurement](measurement.md)
