# 8. Recover: worker states, handoff, durable state and the retro

Read when a worker goes quiet or stops, before a context handoff, and at the end of each campaign day. The periodic roster check is the loop's step 4 ([0](coordinator-loop.md)).

## Worker states

Keep these states apart, per worker:

| State | Meaning | Action |
|---|---|---|
| Running | the runtime reports it active | the loop reads its status file |
| Reported | final report read and verified | accept or reject the artifact; mark `reported` on the board |
| Interim | stopped while its own background job runs | track the job; message the worker when a "finished" notice has no new report |
| Outstanding | neither running nor reported | resolve now; read the result back |
| Stopped | turn ceiling, budget or a kill ended the run | verify the pushed revision; resume by task id, or hand over |

- **A finished worker is not a reporting worker.** A worker that finished writes nothing more, so quiet-time alone misses it. `board_check.py --activity-dir` flags an end of turn with no report.
- **A stopped worker is not a finished worker.** Partial output must not enter campaign state. Confirm completion from lifecycle evidence (exit status, terminal receipt). A process listing of unknown scope proves nothing across containers or hosts.
- **Quiet is a question.** One long tool call (a test run, a review round) writes nothing until it returns. Before you stop a worker, list its own processes (by its worktree path) and read its status file. Stopping two mid-step workers once lost their work.
- A queued message can steer a running worker. It may not start a new turn after completion. Use the runtime's resume operation and check for a state change.
- An accidental interrupt can stop every worker at once, and some runtimes cannot resume. Check whether resume works. Either way, keep each worker's state in pushed branches, its status file and tracker comments, so that a fresh worker restarts in minutes.
- While polling, read the process table for orphaned browser daemons of stopped workers. Run the repository's reaper or kill by a mapped dead worker's PID, never by binary name.

## Replace a stuck worker

A worker that ran out of context, repeats itself or does not answer is replaced by the handover in [2](assign.md#hand-a-lane-over). Stop the old worker first, so that the workspace has one owner.

## Stop on control-plane failure

Repeated control-plane failures (an exhausted quota, an erroring state query) stop the affected assignment. Record the blocker and what shows recovery. Stop claiming verified progress. A failed query is unavailable data, never zero activity. Repeated non-fatal background failures raise a signal by count; a warning nobody owns hides a broken path until you need it.

## Keep state durable

At each transition, write to the tracker: revision, evidence, acceptance rows done and remaining, blocker, owner, next action. Anything only in the message log or a temporary path is not durable. Before a context handoff, run the loop and leave the board, the heartbeat command and how to resume each worker.

## Retro at the end of each day

The skill improves by iteration. At the end of each campaign day:

1. **Coordinator misses first.** List each statement the coordinator made to the operator that a probe would have contradicted ("all moving", "every item has a worker", "nothing is stalled"), with the time and the probe that would have caught it.
2. **Stall minutes by cause.** For each lane, add up the minutes it did not move, by cause:
   - serial waiting on its own check;
   - coordinator latency;
   - an unowned shared blocker;
   - no right to land;
   - fixture setup;
   - environment quota;
   - a review loop without a cap;
   - a failed reply channel.

   Use status files, hand-back times and the board's history, not memory.
3. **The one rule.** Change the ONE rule or script check that would have saved the most minutes. Write it as observation → cause → rule, and measure it the next day.

## Improve the skill after a costly failure

Add one lesson at a time: observation, cause, rule, and the evidence that the rule helped. Put the first missing fact that would have prevented the waste next to the decision it informs, in the stage that owns it. Prefer a script check over a written rule, and delete rules that a script now enforces. Keep generic guidance here and local commands in the owning project. Do not turn one campaign's numbers into a universal limit.

For a shared skill, edit its canonical source and read the consumer's update instructions. Publish under existing authorization. Update the consumer through its supported install path. Verify the pinned revision, the lock record and the package contents. Load the installed revision before you claim that the new rules are in use.

Related: [0. Coordinator loop](coordinator-loop.md) · [2. Assign](assign.md)
