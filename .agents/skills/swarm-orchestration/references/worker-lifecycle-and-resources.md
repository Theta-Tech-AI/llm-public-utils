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
- Compute overlapping paths across the selected issues before each wave, and serialize or give a single owner to any file two assignments would write; check whether a repair task is still needed before spending a worker on it. An add/add conflict costs two workers and a merge repair.
- Push each green slice as soon as it is green, and cap the number of concurrently test-running agents, so a host-level failure costs only the work not yet pushed rather than a whole wave.
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


## Failure patterns

- **A worker finished and nobody read its result.** — Completed child results are not always delivered automatically; the coordinator kept working instead of yielding and reading the roster. Rule above. Evidence: completed results left unread.
- **Hung external workers and a timed-out search were read as results.** — A hung child emits nothing and exits into an empty file, and a size-bounded search returns empty on timeout — indistinguishable from a true no-match unless the wording is read. Give every external agent a wall-clock timeout and a non-empty-output assertion; on a timed-out search, narrow the scope and re-run rather than concluding absence Evidence: zero-byte outputs and timeouts presented as findings.
- **A worker named after a model did not prove model identity.** — Labels were mistaken for runtime metadata. Rule above. Evidence: Runtime receipt, not agent self-report.
- **An idle worker never acted on a new message.** — The messaging operation did not restart a completed turn. Rule above. Evidence: Acknowledgment or active run.
- **Nested or CLI workers created hidden load.** — Only direct managed children were counted. Rule above. Evidence: Actual active count and resource usage.
- **Temporary builds filled the filesystem and stopped even cleanup commands.** — Retained compositions had no space budget or cleanup owner. Rule above. Evidence: Free space, free inodes, and retained build size.
- **A new patch landed in another task's delivery clone.** — Ownership and workspace were implicit. Rule above. Evidence: the procedure above.
- **A 16-agent campaign had only one agent running while the coordinator reported 16.** — Registered agents were counted after their turns completed; freed slots were not refilled. Query live states before each capacity report and after completions; assign bounded useful follow-up work and confirm the new turn is running. Report any shortfall when safe work is unavailable Evidence: Running count from the runtime, slot assignments, and accepted issue closures.
- **A credential helper and a container environment dump printed live secrets into internal tool output.** — Diagnostics requested whole secret-bearing payloads, and filtering after output missed values outside a `PASSWORD` pattern. Rule above. Evidence: the procedure above.
- **Every control-plane query failed while the worker kept working.** — An exhausted API quota or rate limit turned state queries into errors that the worker did not surface. Rule above. Evidence: work advanced while state was unreadable.
- **Sessions were killed by the kernel in the middle of a wave.** — Where memory exhaustion is the cause, the wave was sized against available slots rather than the host's memory. Rule above. Evidence: silent workers that never resume.
- **A permission denial halted a slice, and the work was retried or handed to a peer.** — A blocked call looked like a routing problem, so the natural workaround was to forward it rather than surface it. Treat a denial as terminal for that slice: report the evidence, hand the operator the one command, and never retry it verbatim or delegate around it — a peer's execution is not the operator's consent Evidence: a repeat attempt or a peer receiving the denied action.
- **One unbounded worker process took down the whole shared host.** — Concurrent agents shared a host and a multiplexer, and one runaway test grew until the kernel killed it along with every sibling session. Rule above. Evidence: a process that outlives its fix.
- **A worker that stopped was counted as a worker that finished.** — A turn ceiling, an exhausted budget, or the worker's own background jobs ended the run with partial output that read like a complete report. Rule above. Evidence: partial output entering a status report.
- **Two workers wrote the same file and produced an add/add conflict.** — The wave was planned by issue rather than by file ownership, so path collisions were invisible before dispatch. Rule above. Evidence: repeat collisions and obsolete repairs.
- **A campaign's decisions vanished into repeated compaction.** — Campaign state lived in the conversation, so each compaction forced the coordinator to re-derive ownership, agreements, and acceptance criteria. Write plan, ownership, decisions, and acceptance criteria to durable artifacts as they happen, and treat anything recoverable only from the message log as non-durable Evidence: state re-derived after a compaction.
- **A host crash erased uncommitted work in throwaway worktrees.** — Green slices sat unpushed in ephemeral checkouts, so a host-level failure cost the whole slice. Rule above. Evidence: green work left unpushed.
- **A worker was judged finished from an unscoped process listing.** — Processes are invisible across isolation boundaries — containers, namespaces, remote hosts, or a runtime that owns its workers — and silence was read as absence of work. Rule above. Evidence: duplicate dispatch of work that was already running.
- **Concurrent workers sharing one per-user tool profile retargeted each other.** — The client keeps active-identity state in a per-user config, so one unscoped switch is global rather than per-process, and it fails silently. Give each worker an isolated profile or a pinned exported identity, and forbid bare identity-switch commands in worker briefs Evidence: calls landing under the wrong identity.
- **A second worker silently renamed its branch instead of failing.** — A branch can be checked out in only one worktree, so handing the same branch name to two workers makes the second fail or divert without surfacing an error. Allocate a unique branch and worktree name per worker up front, and require workers to fail loudly rather than rename when the requested branch is taken Evidence: diverted branch names appearing in reports.
- **Two workers editing one submodule collided despite separate worktrees.** — A worktree isolates the superproject index only; submodule objects and checkouts remain shared. Treat submodules and shared caches as single-writer resources: serialize edits to them or clone them per worktree Evidence: submodule conflicts between parallel workers.
- **A background subsystem failed thousands of times in silence.** — Auxiliary work such as checkpointing degrades at warning level, which does not block the happy path and so is never acted on. Turn repeated non-fatal background failures into an actionable signal by count or threshold, so a broken recovery mechanism cannot be discovered only at the moment recovery is needed Evidence: the same warning repeating without an owner.
- **Architecture cleanup deleted a meaningful seam or introduced a broad translator.** — Line reduction replaced contract analysis. Check consumers, packaging, invariants, and ownership; prefer the narrow correct change, and confirm the actual duplication fell Evidence: Preserved behavior with less actual duplication.
- **A review approved a change whose tests nobody executed.** — The reviewer's environment lacked prerequisites, so approving on reported evidence was cheaper than running the suite. Make runnable prerequisites a precondition for review tasks, and mark a verdict resting on reported rather than reproduced evidence as provisional Evidence: approvals carrying no execution.
- **A gate reported a false pass and a false failure on the same change.** — Concurrent runs shared one hardcoded scratch tree and overwrote each other mid-build. Rule above. Evidence: gate results that contradict a clean re-run.
- **A partially executed run was reported as verified.** — A consent or permission gate blocked one step and the rest of the run continued, so the summary read as fully verified. Require every report to list steps skipped for denied consent or permission as an explicit unverified-gap section, and have the reviewer treat an unnamed skipped step as unverified Evidence: a verified claim that covers a step that did not execute.

---

Related: [planning and capacity](planning-and-capacity.md) · [the assignment record](assignment-and-handoff.md) · [validation and review](validation-and-review.md)
