# 2. Assign the work

Read when you dispatch, re-rank, brief workers, or decide who owns what.

## The assignment and result record

Keep one record per item in a durable task tracker. Omit fields that do not apply. The owner and reviewer identity fields are required when the work is reviewed. Put results next to the original acceptance criteria, so that a new session can see what remains.

```text
Task and intended outcome:
Primary task ID / current stage:
Acceptance rows, including live/release requirements:
Owner / independent reviewer / coordinator:
Workspace / real remote / branch / baseline revision:
Allowed paths or artifact boundary / excluded scope:
Dependencies / active descendants / shared resources:
Checkpoint bound and next checkpoint:

Final revision and changed paths:
Source composition: upstream revision + overlay revision + generated inputs:
Checks: command, working directory, tool version, result, durable evidence:
Review: reviewer identity, exact revision, findings, resolution:
Delivery: PR/artifact link, target, exact head, check state, merge revision:
Completed acceptance rows / remaining rows:
Blocker / next action / responsible owner:
Updated at:
```

A local path or "tests pass" is not a durable result. Store the summary with an artifact, commit or task record. Keep secrets and sensitive payloads out of reports.

## Rules for each assignment

- Give each worker one bounded deliverable that can finish inside one worker budget. Name the outcome, allowed paths, baseline revision, exclusions, acceptance checks, reviewer, and publication authority. Ask for a concrete next checkpoint, not open investigation.
- Require a durable report before or during the work. A worker that dies then leaves a handoff, not half-done edits.
- Give each worker its own workspace, and a unique branch and worktree name. Tell the worker to fail loudly, never to rename, when the name is taken.
- The item owner stays responsible through review, integration and acceptance. Delegate bounded finishing steps, but keep one owner for the rest of the path.
- Split work by independent concern and by file ownership, not by issue. Keep tightly coupled interfaces under one owner. For two tasks on one contract, decide the contract first, then delegate callers and tests. Use another agent for tests or review, never for a competing implementation.
- Nested children use the same budget. The parent reconciles before it reports. Do not let nested authors start their own backlogs.
- Give every worker the same written brief: method, checks, report format, and the kill rule in [3. Build](build.md). To change a rule, edit the brief atomically and message the running workers. Name the repository's shared parallel test runner in the brief; a worker's private serial script cost about three times as long and ran three times.
- Assign by role where the runtime and the operator allow. Cheaper models build and trial. The strongest model reviews and decides. A separate model does the final real run. Model size alone is not a review result.
- A checkpoint limit ends one assignment attempt, not the user's task. Record the evidence, replan, and continue. Do not retry the same failed approach silently.

## Prevent duplicates and collisions

- Before you dispatch item N, run `git log --remotes --oneline --grep "#N"` and read the latest comments for a claim. A hit means message the owner. Never start a second worker. Search commit messages, not branch names.
- Compute file overlap at dispatch: planned paths and reserved names across assignments, plus `git diff --name-only <base>...<branch>` for every open branch. Compute it again for every integration batch. Give any file that two assignments would write to one owner, or sequence the second assignment after the first lands. Overlapping branches share one batch and one combined test run, or the later one rebases first.
- Treat a scope or owner change as a handoff. Tell the old owner to stop and reconcile its descendants. Read back its commits, closures and comments. Record the new boundary. The new owner waits for acknowledgment before it changes the same item or paths. With no acknowledgment, stop the old run and verify its side effects. Other items continue.
- Allocate sequence-numbered names (migration numbers, ports, container names, id ranges) before work starts. Check the integration branch for collisions at merge. When a later number is ready first, swap the numbers. Do not land placeholders.

## Rank and refill

Rank by remaining effort to full acceptance, with review, repair, integration and live rows included. Estimate each stage separately. The slowest stage controls intake.

For each free agent, choose in this order, unless aging, severity or a critical dependency says otherwise:

1. Ready work that can pass the final delivery step.
2. Small repairs that release reviewed work.
3. Reviews and acceptance checks for complete implementations.
4. Prerequisites that unblock several items.
5. New independent implementation.

Preserve the user's stated priorities.

At each worker completion, before a CI or deploy wait, and before a status reply:

1. Refresh the live roster and the ready work, and re-rank.
2. Record `running`, `completed` and `idle` separately.
3. Give each reusable slot its next bounded task, or record its actual limit: a resource, a full downstream WIP stage, or no safe work.
4. Start the task and check that it is running. A queued message may not restart a finished worker. Use the runtime's resume or spawn operation.

A CI or deploy wait does not block unrelated review, repair or acceptance work. A one-shot status check is a completed task, not an active worker. Saturation rules: [1](establish.md). When the coordinator holds a decision, supply a compact decision packet so it clears fast.

## Route decisions

- Before you ask for a decision or call work externally blocked, check the governing requirement, the code, the configuration and the recorded authorization for the non-secret facts you need. Do not turn another party's operating policy into a project requirement.
- Decide reversible choices within existing authorization in the same turn, and say so. Ask only about unresolved scope, new spending, an uncovered production or security action, irreversible or regulated data, or another choice reserved to the operator. State the exact missing fact. Send the choices as one batched multiple-choice question after all unblocked work is dispatched. Say where a requested input comes from and how the operator can supply it.
- A permission or policy denial ends that slice. Report the evidence and hand the operator the one command to run. Never retry the denied action. Never pass it to another worker: a peer that runs it is not the operator's consent.
- Treat worker summaries as claims. "Tests pass", "merged", "available model" and "complete" each need an artifact or live state. Check a claim about running-system state (a stuck queue, a livelock) against logs or data before you relay it.
- Separate the symptom from its proposed cause. Before you prescribe a repair, ask for the smallest probe that can disprove the cause. Check what counters, timestamps, retries and revision numbers mean at their owner. Give the worker the observation and the competing explanations, not a required diagnosis. When a claim is disproved, correct the task record and every active brief that used it.

## Iterate a skill or prompt

Write it. Get a cold-read critique from a reader with no context. Run a trial with a friction log. Revise with a new worker. Trial again. In a blind trial, keep expected answers, synonyms, answer-shaped examples and earlier findings out of the text, the brief and the inherited context. An evaluator holds the expected cases apart. Record any steering. A disclosed answer voids that case. Judge coverage against independent sources and new findings, not only recovery of the known example. A trial that finds the answer unaided is the pass signal.

## Failure patterns

- **Long acceptance runs were briefed as UI click-throughs while the repository held a driver for the same artifact.** — Nobody searched the drive and test scripts first. Rule: before briefing an end-to-end proof, search the repository for an existing driver or API path to the artifact; use the UI only for what must be seen in the UI. Evidence: hours of clicking for minutes of work.
- **A second worker rebuilt an issue that was already on another branch.** — The duplicate check searched branch names. Rule: search commit messages and comments. Evidence: overlapping files between the two branches.
- **Two workers wrote the same file and produced an add/add conflict.** — The wave was planned by issue, so path collisions were invisible. Rule: plan by file ownership. Evidence: repeat collisions and obsolete repairs.
- **Several ready items waited on the same prerequisite repair.** — Each path treated the shared blocker as separate work. Rule: one owner, one verified revision, reused. Evidence: fewer duplicate investigations.
- **The coordinator kept planning improvements while ready work waited.** — Process work had no delivery bound. Rule: make one small improvement aimed at the current bottleneck, apply it to the next item, and resume delivery. Evidence: shorter queue age, not more process artifacts.
- **Workers confidently reported a stuck queue and a livelock that logs disproved.** — The queue was empty, and the revisions came from one global sequence. Rule: check state claims against logs before relaying. Evidence: log lines that match the claim.

Next: [3. Build](build.md) · Related: [recover](recover.md)
