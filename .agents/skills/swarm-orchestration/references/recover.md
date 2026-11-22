# 8. Recover: roster, handoff and durable state

Read at every checkpoint, when a worker goes quiet, when a worker stops, and before a context handoff.

## The roster loop

Choose a check cadence and record it. Apply it between transitions as well as at them. Ask running workers for status. Do not infer progress from silence. Drain completed results at each checkpoint.

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

## Failure patterns

- **A worker finished and nobody read its result.** — The coordinator kept working and did not read the roster. Rule: outstanding-result state above. Evidence: completed results left unread.
- **A worker that stopped was counted as finished.** — A turn ceiling, budget or background job ended the run with partial output that read like a report. Rule: verify the artifact; resume by task id. Evidence: partial output in a status report.
- **An idle worker never acted on a new message.** — The message did not restart a completed turn. Rule: resume operation plus acknowledgment. Evidence: an active run.
- **A worker ran out of context while its background test run kept going.** — The turn ended with uncommitted edits and a live job. Rule: stop the old worker, hand off to a new one. Evidence: two workers writing one tree.
- **A worker was judged finished from an unscoped process listing.** — Silence was read as absence of work. Rule: lifecycle evidence. Evidence: duplicate dispatch of running work.
- **Every control-plane query failed while the worker kept working.** — A quota or rate limit turned state queries into errors that nobody surfaced. Rule: stop condition above. Evidence: work advanced while state was unreadable.
- **A campaign's decisions vanished into repeated compaction.** — State lived in the conversation. Rule: durable artifacts. Evidence: state re-derived after a compaction.
- **A background subsystem failed thousands of times in silence.** — Warning-level degradation blocked nothing, so nobody acted. Rule: threshold signal. Evidence: the same warning repeating without an owner.
- **Reports survived only in temporary paths.** — The recovery record was incomplete. Rule: durable record. Evidence: a new session resumes without chat or local files.

Related: [2. Assign](assign.md) · [3. Build](build.md)
