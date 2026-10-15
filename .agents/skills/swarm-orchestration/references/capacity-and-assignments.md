# Capacity and assignments

## Choose work before choosing worker count

The useful pool is bounded by independent tasks, reviewer throughput, integration throughput and shared resources. Count active descendants and CLI processes, not only direct children: runtime limits can apply to the whole tree, and nesting is not proven extra capacity.

Start small and reserve reviewer capacity. Set explicit WIP limits for implementation, review, integration and acceptance, choosing the count from observed completion and review times rather than a sample pool size. Add implementation work only while completed items flow through review and integration without a growing wait — a saturated review queue means stopping new intake and moving qualified agents to independent review.

Give spare agents work that clears the current bottleneck: reproduce a CI failure, check full scope, prepare an acceptance fixture, inspect a dependency, review a ready change. Never speculative work to keep a dashboard busy.

Watch large tasks and the dependency path: an aging item or prerequisite outranks another easy closure when it unlocks more accepted work, and a task spanning three repositories with live acceptance can outlast a larger local change.

## Reassign at transitions

For each free agent ask which assignment most reduces time to the next accepted outcome, or unlocks several. Use current evidence, not the original estimate or time already spent; a nearly finished task is a poor next choice if its remaining acceptance is inaccessible.

Prefer, in order: ready work that can pass the final delivery step; small repairs that release reviewed work; reviews and acceptance checks for complete implementations; prerequisites unblocking several items; then new independent implementation. A whole issue close outranks a smaller patch that would leave acceptance rows or dependencies open. Re-order for aging, severity or a critical dependency, and preserve the user's stated priorities.

Re-rank when a worker finishes, a reviewer finds a defect, CI completes or access changes; never leave assignments fixed for the campaign. Estimate implementation, review, repair, integration and acceptance separately — the slowest available stage controls intake — and parallelise preparation around a serialised merge decision while keeping one owner for it.

At each completion, refresh the roster, record `running`, `completed` and `idle` separately with the next task for each reusable slot, and confirm a follow-up actually started a new turn. A one-shot status check is a completed task, never an active worker for the rest of a CI wait.

Monitor work already in progress as well as new candidates: if implementation outruns review, move qualified agents to reviews; if CI is simply running, prepare the next reviewed delivery instead of duplicating checks; if integration waits on a coordinator decision, supply a compact decision packet so it can be cleared promptly.

When a merge train leaves CI runs queued for old commits, compare each run's SHA with the current branch or PR head and cancel only superseded queued runs, preserving the head's required checks. An old green run is not evidence for the candidate.

## Verify the runtime and model

- Honour explicit model choices; never infer a model from an agent name such as `fast-worker` or `small-model-review`.
- Distinguish requested configuration from runtime-reported identity: prefer a spawn receipt or run metadata, record agent ID, requested and observed model and the evidence source, and report identity as unverified when it is not exposed.
- Read the installed version, configuration or help before changing settings; use an authoritative source for documentation, and never publish a guessed parameter as a working fix.
- Smoke-test one bounded worker before a large expansion — start it, observe a result, verify identity where possible, confirm cleanup. A harmless read-only task suffices.
- A larger configured limit does not establish higher throughput; observe live capacity and measure delivery after expansion.

The coordinator needs enough context to resolve design and acceptance disputes. Routine implementation and review can use the user's preferred worker profile; difficult diagnosis or review may escalate when its measured rework cost justifies another. Keep author and reviewer independent regardless of model — model size is not a review result.

## Assign a complete unit

The assignment states the outcome, artefact boundary, source baseline, excluded scope, acceptance checks, review destination and publication authority ([record template](delivery-and-handoffs.md)), and asks for a concrete next checkpoint rather than unlimited investigation.

Where two tasks touch one contract, one owner decides the contract first and independent callers or tests follow. Nested delegation suits a child with a concrete subtask while its parent still has useful independent work, and the parent owns reconciliation before reporting completion. Track descendants on the same board: no nested author starts an unrelated backlog, and a supervisor tree that only waits adds handoff delay without delivery value.

## Workspace and resource ownership

- One isolated checkout per delivery item. Worktrees isolate files but still share Git metadata such as stash, so use standalone clones when shared metadata is unsafe or read-only.
- Give the coordinator the path and the real remote before work starts; a clone made from a local repository may still have that local path as `origin`.
- Use an ignored repository scratch directory only after checking ignore behaviour and write access, otherwise an authorised temporary directory. A different path bypasses neither a sandbox nor a runtime slot limit.
- Never switch branches, pop a shared stash, reset another agent's tree or overwrite its report. Preserve mistaken edits and move the intended patch to its own clean checkout.
- Give each test composition, browser session, output file and log a unique owner, and do not rebuild a source tree while another worker tests it.
- Limit expensive suites by memory and environment capacity: respect the project's cap, serialise broad suites, and start no duplicate builds or live probes for the same evidence.
- Check free space and inodes before cloning or composing, leave room for tools and cleanup, and afterwards remove only owned disposable builds whose source revisions and evidence are recorded.

## CLI workers and lifecycle

Use CLI workers only where the tool exists, delegation is authorised and limits allow — never to evade an enforced limit — and inspect help for supported model and output flags rather than assuming syntax.

Record process or session ID, working directory, source revision, model evidence, log path and result path. Keep the detailed report separate from the CLI's final-output file so a short final message cannot overwrite it, and provide a steering channel the worker actually reads at checkpoints.

For an idle worker use the runtime's resume or follow-up operation — a queued message can steer a running agent but may not trigger a new turn after completion — and check acknowledgment or state change. Stop only the owned process; never a broad process-name kill that can reach other agents.
