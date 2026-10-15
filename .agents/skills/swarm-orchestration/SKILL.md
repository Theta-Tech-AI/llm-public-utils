---
name: swarm-orchestration
description: "Use when asked to fan out, delegate across multiple agents or workers, finish a backlog or milestone in parallel, add more workers, use nested subagents or CLI agents, or improve multi-agent delivery speed—even if nobody says 'swarm'. Also use when coordinating concurrent agent changes, allocating authors and reviewers, recovering agent handoffs, or diagnosing stalled closures, growing review queues, and rework in parallel execution. Guides capacity, ownership, independent review, integration, and completion-rate measurement. Do not load for ordinary solo implementation, application concurrency, or one isolated helper task without coordination needs."
---

# Swarm orchestration

Optimize the rate of accepted outcomes, not the number of busy agents. The coordinator owns scope, scheduling, integration, and the final delivery decision. Workers own bounded assignments. Reviewers provide independent evidence. More workers help only while downstream stages can accept their output.

This skill is portable. Use the available agent runtime, task tracker, version control, and checks. Follow the user's model choices and the repository's rules. The skill does not grant permission to delegate, publish, merge, deploy, or contact other people; use existing authorization. Do not add a new scheduler or service when a task board and short records are enough.

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
- Give each worker one bounded deliverable and one exclusive workspace. Name the allowed paths, baseline revision, acceptance checks, exclusions, reviewer, and handoff destination. Use the [handoff template](references/delivery-and-handoffs.md).
- The item owner remains responsible through review, integration, and acceptance. Delegate bounded finishing steps when useful, but keep one owner for the remaining acceptance path and evidence.
- Split across independent concerns. Keep tightly coupled interfaces under one owner; use another agent for tests or review instead of two competing implementations. Nested children consume the same resource budget.
- Review small complete changes as soon as they are ready. If reviewed work accumulates, stop new intake and move capacity to diagnosis, review, acceptance, or integration. An idle slot can be the correct choice.
- When review is saturated, admit no new implementation until review capacity or queue age improves. Finish and checkpoint existing work; do not discard it to meet a count.
- Keep a visible WIP limit for implementation, review, integration, and acceptance. Reassign capacity to the oldest or closest-to-closure item when a stage reaches its limit; a full implementation pool with an empty acceptance lane is slower progress.
- A checkpoint limit ends an assignment attempt, not the user's overall task. Record the evidence, replan, and continue useful authorized work. Avoid silent retries of the same failed approach.
- Treat worker summaries as claims to verify. “Tests pass,” “merged,” “available model,” and “complete” each need a matching artifact or live state.
- Keep credentials out of diagnostic output. Ask workers for the specific non-secret fact needed; do not dump credential-helper results or whole process/container environments and try to redact them afterward. If a secret appears in tool output, stop that diagnostic path, report the exposure scope without repeating the value, and follow the operator's decision on continued use or rotation.
- At each worker completion, before a CI/deploy wait, and before a status reply, refresh the live roster and ready work, then re-rank remaining acceptance and independent tasks. For each freed reusable slot, record its next useful bounded assignment or the specific resource limit, full downstream WIP stage, or lack of safe work. Start and verify useful independent work while it remains; a CI/deploy wait alone does not block unrelated review, repair, or acceptance. Keep reviewer, integration, and acceptance WIP limits and one owner per live browser/session; do not create busywork to preserve a worker count. A queued message may not restart a completed worker; use the runtime's follow-up or spawn operation and verify that it is running.

## Review and deliver the exact result

Read [delivery and handoffs](references/delivery-and-handoffs.md) before validation, publication, integration, or recovery.

Require independent review of the final revision and relevant acceptance evidence. The coordinator resolves review findings and makes the final decision. Review approval is not an automatic merge instruction.

Treat feedback as a small checkpoint amendment: validate the amended revision, obtain fresh review, and publish only with a revision receipt when authorized. Continue the delivery path without waiting for the campaign to end. Do not create a new framework or duplicate guidance to process routine feedback.

For code, validate the actual composed source and the relevant full-project check context. Keep the source immutable during testing. After a change, rerun the affected checks and review the delta; do not reuse approval for an older revision. Avoid broad repeated suites without a changed risk or unresolved failure.

Before delivery, refresh the task state, target branch, remote, required checks, and exact head. Apply repository rules and existing user authorization. Close the task only when every required acceptance row has evidence. Keep partial progress visible without counting it as completion.

Before accepting a handoff, verify the claimed revision and tree from the files (`git hash-object` for changed blobs; compare tree and commit with the remote) and build from the exact upstream pin the candidate recorded; a stale checkout or symlink makes missing imports and deletions look valid. A reviewer who removes a symbol or module must search its importers and runtime entry points first. Before merge, verify the PR base, exact head, required CI jobs and their artifacts; a green job from another revision, or an early gate, is not evidence for the candidate.

When CI fails, read the failing job's artifact, step and log before changing code, reproduce the gate on the exact composition, and give one owner the smallest supported repair. A skipped, pending or early gate says nothing about later tests.

For a branch or composed tree and for composing a commit through a Git API, use [delivery and handoffs](references/delivery-and-handoffs.md): it carries the base-to-head validation, the exact remote parent and `base_tree` rule, and what green CI does and does not prove.

## Measure and adapt

Use [measurement and experiments](references/measurement.md) for definitions, attribution, and the optional read-only GitHub adapter.

Report completed/total and percentage from a live task query, completions per hour over a stated UTC window, time between completions, and time since the last completion. Also track review queue age, rework, blocked time, and each stage's WIP. Give these measures at campaign start, after each accepted closure, and at regular checkpoints; separate campaign-attributed outcomes from all repository activity.

Compare equal windows before and after a scheduling change. Small samples, different task difficulty, batch closure, and other contributors limit causal claims. If more workers do not improve delivery, identify the slowest stage and change one scheduling factor. Do not weaken acceptance or split issues merely to inflate the count.

## Leave a recoverable system

At each meaningful transition and regular campaign checkpoint, persist the revision, evidence summary, acceptance rows completed and remaining, remaining scope, blocker, owner, and next action in the durable task record. Local reports support that record; temporary paths alone do not survive a lost machine.

At campaign checkpoints, report active workers and descendants, review/integration queue age, pending checks, and the next action. Before a context handoff, refresh the board and record which agents are running, which are idle, and how to resume each. A message to an idle worker may not restart it; check the runtime's actual behavior.

Read [lessons and failure patterns](references/lessons.md) when diagnosing coordination waste. After a costly failure, add the smallest supported improvement: observation → cause → rule → evidence that the rule helped. Keep generic guidance in this skill and local commands in the owning project. Remove obsolete rules instead of accumulating incident folklore.
