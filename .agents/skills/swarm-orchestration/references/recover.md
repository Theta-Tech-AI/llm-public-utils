# 8. Recover: roster, handoff and durable state

Read at every checkpoint, when a worker goes quiet, when a worker stops, and before a context handoff.

## The roster loop

Choose a check cadence and record it. Apply it between transitions as well as at them. Ask running workers for status. Do not infer progress from silence. Drain completed results at each checkpoint.

Watch every worker by its own activity record (the runtime's per-task output or event log), not by repository
changes: a worker that drives a browser or an API has no worktree, so a worktree watcher never sees it. Give each worker
an expected pace when you dispatch it (the time its next stage should take). Quiet past that pace is a question, not a
verdict: ask the worker for its stage and wait one bounded reply window; stop and replace it only when no answer comes or
its own record shows no progress. A long single step writes nothing until it ends. Brief long-running workers to send a
one-line stage update at each stage, so a long step is never mistaken for a stall. Before you ask or stop, list the
worker's own processes (by its worktree path): a running test run or review round is evidence of a long step, not proof of
progress, so keep the bounded status question and its deadline.

Before you expand the pool, verify how a silent stall will reach you: runtime notices plus bounded roster checks when no watcher exists. Enroll each new or resumed worker at once. Record its last checkpoint, expected next event and check deadline. Verify that monitoring survives a restart or handoff. A background job counts as activity only when its owner and expected completion are known.
A watcher flags both ends: a worker that went quiet, and a worker that FINISHED without reporting (its last record is an end of turn and nothing follows). An accidental operator interrupt can stop every worker at once, and some runtimes cannot resume a stopped worker. Check whether resume works, and either way keep each worker's state in pushed branches and issue comments, so a fresh worker restarts from them in minutes.


Keep these states apart, per worker:

| State | Meaning | Action |
|---|---|---|
| Running | runtime reports it active | check at the cadence |
| Reported | final report read and verified | accept or reject the artifact |
| Interim | stopped while its own background job runs | track the job; message the worker when a "finished" notice has no new report |
| Outstanding | neither running nor reported | resolve now; read the result back explicitly |
| Stopped | turn ceiling, exhausted budget or a kill ended the run | verify the artifact or revision; resume by task id |

A finished worker is not a reporting worker. Completed results are not always delivered, so read them back. A stopped worker is not a finished worker: partial output must not enter campaign state. Confirm completion from authoritative lifecycle evidence, such as the exit status or terminal receipt of the run that launched it. A process listing whose scope you have not established proves nothing: processes are invisible across containers, namespaces and remote hosts.

Use the runtime's resume or follow-up operation for an idle worker. A queued message can steer a running agent. It may not start a new turn after completion. Check for acknowledgment or a state change.

## Replace a stuck worker

A worker that ran out of context or repeats itself gets replaced. Stop the old worker first, so that the workspace has one owner. Give the new worker a short verified handoff: branch, head, uncommitted files, checks run, decisions made.

## Stop on control-plane failure

Repeated control-plane failures (an exhausted API quota, a rate-limited or erroring state query) stop the affected assignment. Record the blocker and what establishes recovery. Stop claiming verified progress. Continue only work that does not depend on the unreadable state. Check the quota information the runtime exposes before dispatch. A failed query is unavailable data, never zero activity.

## Keep state durable

At each transition and checkpoint, write to the task record: revision, evidence summary, acceptance rows done and remaining, blocker, owner, next action. Write the plan, ownership, decisions and acceptance criteria as they happen. Anything that exists only in the message log is not durable. Temporary paths and local reports do not survive a lost machine.

At a checkpoint, report active workers and descendants, review and integration queue age, pending checks, and the next action. Before a context handoff, refresh the board. Record which agents run, which are idle, and how to resume each.

Make repeated non-fatal background failures (checkpointing, auxiliary jobs) raise a signal by count or threshold. A warning that nobody owns hides a broken recovery path until you need it.

## Improve the skill after a costly failure

Add one lesson at a time: observation, cause, rule, evidence that the rule helped. If you cannot state the evidence, do not add the lesson. Put the first missing fact that would have prevented the waste next to the decision it informs. Do not turn a temporary fault into a permanent workaround, an example pool size into a universal limit, or one campaign into a claimed speedup. Keep generic guidance here and local commands in the owning project. Delete obsolete and tooling-enforced rules.

For a shared skill, find its canonical source and read the consumer's update instructions before you edit an installed copy. Publish the source change under existing authorization. Update the consumer through its supported install path. Verify the pinned revision, lock record, complete package contents, removed files and links to renamed references. Load the installed revision before you claim that the new rules are in use. Record an intentional local patch apart.

## Failure patterns

- **A worker that stopped was counted as finished.** — A turn ceiling, budget or background job ended the run with partial output that read like a report. Rule: verify the artifact; resume by task id. Evidence: partial output in a status report.
- **A worker ran out of context while its background test run kept going.** — The turn ended with uncommitted edits and a live job. Rule: stop the old worker, hand off to a new one. Evidence: two workers writing one tree.
- **A worker was judged finished from an unscoped process listing.** — Silence was read as absence of work. Rule: lifecycle evidence. Evidence: duplicate dispatch of running work.
- **Every control-plane query failed while the worker kept working.** — A quota or rate limit turned state queries into errors that nobody surfaced. Rule: stop condition above. Evidence: work advanced while state was unreadable.
- **A campaign's decisions vanished into repeated compaction.** — State lived in the conversation. Rule: durable artifacts. Evidence: state re-derived after a compaction.
- **A background subsystem failed thousands of times in silence.** — Warning-level degradation blocked nothing, so nobody acted. Rule: threshold signal. Evidence: the same warning repeating without an owner.
- **A stall alert fired on a worker that had finished.** — The watcher checked a worktree whose branch had just landed. Rule: drop landed workers from the watch list at each batch; a watcher that ends green means every watched worker committed clean work. Evidence: alerts on worktrees already merged.
- **Queued runs were never claimed while the test load saturated a shared worker pool.** — Proof runs waited behind dozens of other agents' runs. Rule: check queue depth before declaring a live proof blocked; move the proof to a quiet environment rather than waiting. Evidence: runs queued with no claim line.
- **Three workers sat 20 minutes without the coordinator noticing, until the operator asked.** — The stall watcher only watched worktrees, and these workers drove a browser with no worktree; nobody had set an expected pace. Rule: watch every worker by its activity record and its expected pace. Evidence: a stall the operator found first.
- **The coordinator then stopped two workers that were mid-step.** — It read "no output for 20 minutes" as a stall, but one long step writes nothing until it ends. Rule: ask first, with a bounded reply window; stop only on no answer or no progress. Evidence: a stopped worker whose last line shows work in progress.
- **A worker looked stalled for 38 minutes while its second-model review and test run were running.** — One long tool call writes nothing to the transcript. Rule: check the worker's processes before stopping, and still ask for status with a deadline. Evidence: live processes under its worktree.
- **Reports survived only in temporary paths.** — The recovery record was incomplete. Rule: durable record. Evidence: a new session resumes without chat or local files.
- **A worker finished and nobody noticed.** — The watcher flagged only quiet workers. Rule: also flag a last record that is an end of turn with nothing after it. Evidence: a finished branch that waited for the next batch.
- **One operator interrupt stopped every worker, and none could be resumed.** — State lived in the sessions. Rule: keep state in pushed branches and issue comments. Evidence: fresh workers restarted from them in minutes.

Related: [2. Assign](assign.md) · [3. Build](build.md)
