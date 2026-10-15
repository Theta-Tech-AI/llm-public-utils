---
name: swarm-orchestration
description: "Coordinate multiple agents doing parallel work: capacity, ownership, independent review, integration, handoff recovery, and accepted delivery rates. Use for delegation, parallel backlogs, worker expansion, or stalled multi-agent delivery. Do not load for ordinary solo implementation, application concurrency, or one isolated helper task without coordination needs."
---

# Swarm orchestration

Optimize the rate of accepted outcomes, not the number of busy agents. The coordinator owns scope, scheduling, integration, and the final delivery decision. Workers own bounded assignments. Reviewers provide independent evidence. More workers help only while downstream stages can accept their output.

This skill is portable. Use the available agent runtime, task tracker, version control, and checks. Follow the user's model choices and the repository's rules. The skill does not grant permission to delegate, publish, merge, deploy, or contact other people; use existing authorization. Do not add a new scheduler or service when a task board and short records are enough.

This applies when fanning out a backlog or milestone, adding workers, using nested subagents or CLI agents, allocating authors and reviewers, recovering agent handoffs, or diagnosing stalled closures, growing review queues, and rework.

## Establish the campaign

1. Read current project guidance and the complete selected tasks, including comments, dependencies, and acceptance criteria. Turn each selected issue into an acceptance matrix before dispatch: required behavior, tests, review, integration, release, and live checks. Refresh the provider remote before assignment: a local remote-tracking ref is a cache, not proof of current state. A saved backlog is a planning aid, not proof that an issue is still open.
2. Define what counts as done. Separate implementation, independent review, integration, release, and live acceptance when they are distinct requirements. A merged slice is not a completed task if acceptance remains.
3. Record a baseline: backlog membership, completed and total items, timestamp, recent completion events, and known external contributors. Preserve the denominator so scope changes cannot look like delivery.
4. Inspect actual capacity: running agents, nested descendants, runtime limits, CPU/RAM, test environments, review capacity, and integration capacity. Configured slots, created agents, and active workers are different counts.
   When the operator sets an active-worker target, record each slot's current state and next useful assignment. Query the runtime immediately before reporting capacity; report the number running now and any shortfall, not the number ever created.
5. Confirm the shared read-only source artifact exists and is usable before dispatching work into exclusive clones.
6. Check the filesystem before creating compositions, clones, or test output. If `/tmp` is a full or constrained tmpfs, use an ignored, disk-backed workspace inside the repository (or another authorized disk-backed path), record its owner and cleanup plan, and remove only owned disposable output after preserving the evidence. Do not let scratch allocation become the campaign blocker.
7. Start with small, unblocked, independently verifiable tasks. Rank by likely time to full acceptance and dependency value, not code size alone. Reassess aging or critical-path work so easy items do not starve it.

Read [capacity and assignments](references/capacity-and-assignments.md) before a large fan-out, model verification, CLI workers, or nested delegation.

## Run a bounded pipeline

Track each item as `ready → implementing → review → integrating → acceptance → done`, with an explicit blocked reason when needed. Use only the stages the task needs. Keep one record per item with owner, immutable revision, next action, and evidence.

- Set work-in-progress limits from the slowest stage. Reserve capacity for review and integration. Sixteen available slots do not imply sixteen simultaneous implementations.
- Schedule by remaining effort to full acceptance. A nearly finished item usually outranks a new easy item; include unresolved review, checks, integration, and live requirements in that estimate. Re-rank after each stage transition or blocker change.
- Give each worker one bounded deliverable and one exclusive workspace. Name the allowed paths, baseline revision, acceptance checks, exclusions, reviewer, and handoff destination. Use the [assignment record](references/assignment-and-handoff.md).
- The item owner remains responsible through review, integration, and acceptance. Delegate bounded finishing steps when useful, but keep one owner for the remaining acceptance path and evidence.
- Split across independent concerns. Keep tightly coupled interfaces under one owner; use another agent for tests or review instead of two competing implementations. Nested children consume the same resource budget.
- Review small complete changes as soon as they are ready. If reviewed work accumulates, stop new intake and move capacity to diagnosis, review, acceptance, or integration. An idle slot can be the correct choice.
- When review is saturated, admit no new implementation until review capacity or queue age improves. Finish and checkpoint existing work; do not discard it to meet a count.
- Keep a visible WIP limit for implementation, review, integration, and acceptance. Reassign capacity to the oldest or closest-to-closure item when a stage reaches its limit; a full implementation pool with an empty acceptance lane is slower progress.
- A checkpoint limit ends an assignment attempt, not the user's overall task. Record the evidence, replan, and continue useful authorized work. Avoid silent retries of the same failed approach.
- Treat worker summaries as claims to verify. “Tests pass,” “merged,” “available model,” and “complete” each need a matching artifact or live state.
- Keep credentials out of diagnostic output: ask workers for the specific non-secret fact needed, and never dump credential-helper results or whole environments. The exposure handling rule is in [worker lifecycle and resources](references/worker-lifecycle-and-resources.md).
- At each worker completion, before a CI/deploy wait, and before a status reply, refresh the live roster and ready work and re-rank remaining acceptance; give each freed slot useful independent work or record its actual constraint. The full refill procedure is in [planning and capacity](references/planning-and-capacity.md).
- Run the roster loop between transitions and at each checkpoint, and treat a worker that is neither running nor reported as an outstanding result rather than as still working. The cadence, result recovery, stop-versus-finish distinction, and control-plane failure handling are in [worker lifecycle and resources](references/worker-lifecycle-and-resources.md).
- Treat a permission or policy denial as terminal for that slice: report the evidence and hand the operator the one command to run. Never retry the denied action verbatim and never route it to another worker — a peer executing it is not the operator's consent.

## Review and deliver the exact result

Read [validation and independent review](references/validation-and-review.md) before accepting a handoff, and [publication and acceptance](references/publication-and-acceptance.md) before publishing, merging, or closing.

Require independent review of the final revision and relevant acceptance evidence. The coordinator resolves review findings and makes the final decision. Review approval is not an automatic merge instruction.

Treat feedback as a small checkpoint amendment: validate the amended revision, obtain fresh review, and publish only with a revision receipt when authorized. The procedure is in [validation and independent review](references/validation-and-review.md).

For code, validate the actual composed source and the relevant full-project check context. Keep the source immutable during testing. After a change, rerun the affected checks and review the delta; do not reuse approval for an older revision. Avoid broad repeated suites without a changed risk or unresolved failure.

Before delivery, refresh the task state, target branch, remote, and required checks, and close only on acceptance evidence. The receipts are in [publication and acceptance](references/publication-and-acceptance.md).

Before accepting a handoff, verify the claimed revision and tree, and before merge verify the PR base, exact head, and required CI jobs. The commands and the failure modes are in [validation and independent review](references/validation-and-review.md).

When CI fails, read the failing job's artifact, step and log before changing code, and give one owner the smallest supported repair. The procedure is in [validation and independent review](references/validation-and-review.md).

For a branch or composed tree, use [validation and independent review](references/validation-and-review.md) for the base-to-head validation and what green CI does and does not prove, and [publication and acceptance](references/publication-and-acceptance.md) for the exact remote parent, the `base_tree` rule, and the delivery receipts.

## Measure and adapt

Use [measurement and experiments](references/measurement.md) for definitions, attribution, and the optional read-only GitHub adapter.

Report completed/total and percentage from a live task query, the accepted rate over a stated window, and each stage's WIP, at campaign start, after each accepted closure, and at regular checkpoints. The full metric set, its definitions, and the causal limits are in [measurement and experiments](references/measurement.md).

## Leave a recoverable system

At each meaningful transition and regular campaign checkpoint, persist the revision, evidence summary, acceptance rows completed and remaining, remaining scope, blocker, owner, and next action in the durable task record. Local reports support that record; temporary paths alone do not survive a lost machine.

At campaign checkpoints, report active workers and descendants, review/integration queue age, pending checks, and the next action. Before a context handoff, refresh the board and record which agents are running, which are idle, and how to resume each. A message to an idle worker may not restart it; check the runtime's actual behavior.

Read [lessons: execution](references/lessons-execution.md) and [lessons: delivery](references/lessons-delivery.md) when diagnosing coordination waste. After a costly failure, add the smallest supported improvement: observation → cause → rule → the evidence that would show the rule helped. Keep generic guidance in this skill and local commands in the owning project. Remove obsolete rules instead of accumulating incident folklore.
