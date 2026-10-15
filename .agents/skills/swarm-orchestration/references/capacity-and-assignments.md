# Capacity and assignments

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

## Verify the runtime and model

- Honor explicit model choices. Do not infer a model from an agent name such as `fast-worker` or `small-model-review`.
- Distinguish requested configuration from runtime-reported identity. Prefer a spawn receipt or run metadata. Record agent ID, requested model, observed model, and evidence source. If identity is not exposed, report it as unverified.
- Read local version/configuration/help before changing settings. If documentation is needed, use the installed version and an authoritative source. Avoid publishing a guessed parameter as a working fix.
- Smoke-test one bounded worker before a large expansion: start it, observe a result, verify identity if possible, and confirm cleanup. A smoke test can be a harmless read-only task.
- A larger configured limit does not establish higher throughput. Observe live capacity and measure delivery after expansion.

The coordinator needs enough context to resolve design and acceptance disputes. Routine implementation and routine review can use the user's preferred worker profile. Escalate difficult diagnosis or review when its measured rework cost justifies another profile. Keep author and reviewer independent regardless of model; model size alone is not a review result.

## Assign a complete unit

The assignment should state the outcome, allowed files or artifact boundary, source baseline, excluded scope, acceptance checks, review destination, and publication authority. Ask for a concrete next checkpoint, not unlimited investigation.

For two tasks that touch the same contract, use one owner to decide the contract first. Delegate independent callers or tests after that decision is stable. Nested delegation is useful when a child has a concrete subtask and its parent can still do useful independent work. The parent owns reconciliation before reporting completion to the coordinator.

Track descendants in the same board. Do not let nested authors each start their own unrelated backlog. A tree of supervisors that only waits adds handoff delay without delivery value.

## Workspace and resource ownership

- Use one isolated checkout per delivery item. Worktrees isolate files but still share Git metadata such as stash; standalone clones provide stronger separation when shared metadata is unsafe or read-only.
- Give the coordinator the path and real remote before work starts. A clone made from a local repository may still have that local path as `origin`.
- Use an ignored repository scratch directory only after checking ignore behavior and write access. Otherwise use an authorized temporary directory. A different path does not bypass a sandbox or a runtime slot limit.
- Do not switch branches, pop a shared stash, reset another agent's tree, or overwrite its report. Preserve mistaken edits and move the intended patch to its own clean checkout.
- Give each test composition, browser session, output file, and log a unique owner. Do not rebuild a source tree while another worker tests it.
- Limit expensive suites by memory and environment capacity. Use the project's memory cap and serialize broad suites when needed. Do not start duplicate builds or live probes for the same evidence.
- Enforce a per-process time and memory cap on every heavy or possibly diverging command, and isolate it so one runaway test cannot exhaust the shared host and kill every sibling session. After replacing a runaway with a fix, confirm the offending process has actually terminated — editing the file does not stop a running loop.
- Compute overlapping paths across the selected issues before each wave, and serialize or give a single owner to any file two assignments would write. An add/add conflict costs two workers and a merge repair.
- Push each green slice as soon as it is green, and cap the number of concurrently test-running agents, so a host-level failure costs at most one slice.
- Check free space and inodes on the actual filesystem before cloning or composing. Leave room for tools and cleanup. After review, remove only owned disposable builds whose source revisions and evidence are recorded.

## CLI workers and lifecycle

Use CLI workers only when the tool exists, delegation is authorized, and they fit runtime/resource limits. They are not a way to evade an enforced limit. Inspect help for supported model and output flags rather than assuming syntax.

Record process/session ID, working directory, source revision, model evidence, log path, and result path. Keep the detailed report separate from the CLI's final-output file; otherwise a short final message can overwrite the report. Provide a steering channel the worker actually reads at checkpoints.

Use the runtime's resume/follow-up operation for an idle worker. A queued message can steer a running agent but may not trigger a new turn after completion. Check acknowledgment or state change. Stop only the owned process when cleanup is needed; never use a broad process-name kill that can terminate other agents.

Bound each assignment so it can finish inside one worker budget, and require a durable report written before or during the work, so a worker that dies mid-task still leaves a recoverable handoff instead of uncommitted half-work the successor must reverse-engineer.
