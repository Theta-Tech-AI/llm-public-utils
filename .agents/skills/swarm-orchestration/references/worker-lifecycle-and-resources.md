# Worker lifecycle and resources

Read when starting, restarting, or expanding workers: runtime evidence, workspace ownership, host limits, and the roster loop that recovers stopped or unreported work.

## Verify the runtime and model

- Honor explicit model choices. Do not infer a model from an agent name such as `fast-worker` or `small-model-review`.
- Distinguish requested configuration from runtime-reported identity. Prefer a spawn receipt or run metadata. Record agent ID, requested model, observed model, and evidence source. If identity is not exposed, report it as unverified.
- Read local version/configuration/help before changing settings. If documentation is needed, use the installed version and an authoritative source. Avoid publishing a guessed parameter as a working fix.
- Smoke-test one bounded worker before a large expansion: start it, observe a result, verify identity if possible, and confirm cleanup. A smoke test can be a harmless read-only task.
- A larger configured limit does not establish higher throughput. Observe live capacity and measure delivery after expansion.

The coordinator needs enough context to resolve design and acceptance disputes. Routine implementation and routine review can use the user's preferred worker profile. Escalate difficult diagnosis or review when its measured rework cost justifies another profile. Keep author and reviewer independent regardless of model; model size alone is not a review result.

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

## Diagnostic hygiene

Do not dump credential-helper results or whole process/container environments and try to redact them afterward. If a secret appears in tool output, stop that diagnostic path, report the exposure scope without repeating the value, and follow the operator's decision on continued use or rotation.

## The roster loop

Choose and record a roster-check cadence, and apply it between transitions as well as at them: check in with running workers rather than inferring from silence, and drain completed results at each checkpoint.

A finished worker is not a reporting worker: completed results are not always delivered to the coordinator, so read them back explicitly and treat an assigned child that is neither running nor reported as an outstanding result to resolve now, not as still running.

A worker that stopped is not a worker that finished: a turn ceiling, an exhausted budget, or the worker's own background jobs can end a run with partial output, so verify the artifact or revision and resume explicitly by task id instead of folding a partial report into campaign state.

Treat repeated control-plane failures (an exhausted API quota, a rate-limited or erroring state query) as a stop condition for the affected assignment: record the blocker and what establishes recovery, stop claiming verified progress, and continue only work that does not depend on the unreadable state.

---

Related: [planning and capacity](planning-and-capacity.md) · [the assignment record](assignment-and-handoff.md) · [validation and review](validation-and-review.md)
