---
name: swarm-orchestration
description: "Use when fanning out to multiple agents or workers — finishing a backlog or milestone in parallel, adding workers, nested subagents or CLI agents — even if nobody says 'swarm'; also for coordinating concurrent changes, allocating authors and reviewers, recovering handoffs, or diagnosing stalled closures, review queues and rework. Optimize the rate of accepted outcomes, not the number of busy agents. Not for solo implementation or one isolated task."
---

# Swarm orchestration

Optimize the rate of accepted outcomes, not the number of busy agents. The coordinator owns scope, scheduling, integration and the final delivery decision; workers own bounded assignments; reviewers provide independent evidence. More workers help only while downstream stages can accept their output.

This skill is portable: use the runtime, tracker, version control and checks that exist, follow the repository's rules and the user's model choices, and take no permission from it to delegate, publish, merge, deploy or contact others. Do not add a scheduler or service when a task board and short records suffice.

## Establish the campaign

1. Read current project guidance and the selected tasks **as they stand now** — comments, dependencies, acceptance criteria. Refresh the provider remote before assignment: a remote-tracking ref is a cache, not proof of current state, and a saved backlog is a planning aid, not proof an issue is open. Turn each item into an acceptance matrix: behaviour, tests, review, integration, release, live checks.
2. Define done, separating implementation, independent review, integration, release and live acceptance. A merged slice with acceptance outstanding is not complete.
3. Record a baseline — membership, completed and total, timestamp, recent completions, known external contributors — and preserve the denominator so scope changes cannot masquerade as delivery.
4. Inspect real capacity: running agents, descendants, runtime limits, CPU/RAM, test, review and integration capacity. Configured slots, created agents and active workers are different counts. When the operator sets a worker target, record each slot's state and next assignment, then query the runtime immediately before reporting: give the number running now and any shortfall, never the number ever created.
5. Confirm the shared read-only source artefact exists and is usable before dispatching into exclusive clones.
6. Check the filesystem before creating compositions, clones or test output. If `/tmp` is constrained, use an ignored disk-backed workspace inside the repository, record its owner and cleanup plan, and remove only owned disposable output after preserving evidence — scratch allocation must not become the campaign blocker.
7. Start with small, unblocked, independently verifiable items, ranked by likely time to full acceptance and dependency value rather than code size; reassess aging and critical-path work so easy items do not starve it.

Read [capacity and assignments](references/capacity-and-assignments.md) before a large fan-out, model verification, CLI workers or nested delegation.

## Run a bounded pipeline

Track each item as `ready → implementing → review → integrating → acceptance → done`, using only the stages the task needs, with an explicit blocked reason where needed and one record per item carrying owner, immutable revision, next action and evidence.

- Set work-in-progress limits from the slowest stage and reserve capacity for review and integration: sixteen free slots do not mean sixteen simultaneous implementations. When review saturates, admit no new implementation, finish and checkpoint what exists, keep a visible WIP limit per stage, and move capacity to the oldest or closest-to-closure item — a full implementation pool with an empty acceptance lane is slower progress. An idle slot can be the correct choice.
- Schedule by remaining effort to full acceptance, re-ranking after every stage transition or blocker change and including unresolved review, checks, integration and live requirements.
- One bounded deliverable and one exclusive workspace per worker; name allowed paths, baseline revision, acceptance checks, exclusions, reviewer and handoff destination ([handoff template](references/delivery-and-handoffs.md)).
- The item's owner stays responsible through review, integration and acceptance. Delegate bounded finishing steps, but keep one owner for the remaining acceptance path and its evidence.
- Split by independent concern: keep tightly coupled interfaces under one owner, and use a second agent for tests or review rather than a competing implementation. Nested children consume the same budget.
- Review small complete changes as soon as they are ready; if reviewed work accumulates, stop new intake and move capacity to diagnosis, review, acceptance or integration.
- A checkpoint limit ends an attempt, not the task: record the evidence, replan, continue useful authorised work, and avoid silent retries of a failed approach.
- Treat worker summaries as claims: "tests pass", "merged", "available model" and "complete" each need a matching artefact or live state.
- Keep credentials out of diagnostic output: ask for the specific non-secret fact needed rather than dumping credential-helper results or whole environments; if a secret does surface, stop that path, report the exposure scope without repeating the value, and follow the operator's decision on use or rotation.
- At each completion, before a CI/deploy wait and before a status reply, refresh the live roster and ready work, then re-rank: give every freed slot its next bounded assignment or record the actual constraint (resource limit, full downstream stage, no safe work). A CI/deploy wait does not block unrelated review, repair or acceptance; do not manufacture busywork to hold a worker count; keep one owner per live browser session. A queued message may not restart a finished worker — use the runtime's follow-up or spawn operation and verify it runs.

## Review and deliver the exact result

Read [delivery and handoffs](references/delivery-and-handoffs.md) before validation, publication, integration or recovery.

Require independent review of the final revision plus acceptance evidence; the coordinator resolves findings and decides, and approval is not an automatic merge instruction. Treat feedback as a small checkpoint amendment: validate the amended revision, take fresh review, and publish only with a revision receipt when authorised — without waiting for the campaign to end, and without inventing a framework or duplicating guidance to process routine feedback.

For code, validate the composed source in the project-wide check context, keep the source immutable while testing, rerun affected checks after a change and review the delta instead of reusing approval for an older revision. Avoid broad repeated suites without changed risk or an unresolved failure.

Before delivery, refresh task state, target branch, remote, required checks and exact head; apply repository rules and existing authorisation; close only when every required acceptance row has evidence, keeping partial progress visible without counting it as completion. Validate the exact base-to-head range against the repository's cheap gates and the affected tests in CI's own context, from a fresh empty composition per branch or amendment — never a reused scratch tree — recording base revision, pins, generated inputs and the final tree or commit ID. Verify a handoff's claimed revision and tree from the files (`git hash-object`; compare tree and commit with the remote) and build from the pin it recorded — a stale checkout or symlink makes missing imports and deletions look valid. A reviewer removing a symbol or module must first search its importers and runtime entry points. When CI fails, read the failing job's artefact, step and log before editing, reproduce the gate on the exact composition, and give one owner the smallest supported repair: a skipped, pending or early gate says nothing about later tests.

## Measure and adapt

[Measurement and experiments](references/measurement.md) defines the measures, attribution and the optional read-only GitHub adapter.

Report completed/total and percentage from a live query, completions per hour over a stated UTC window, time between completions and time since the last, plus review-queue age, rework, blocked time and each stage's WIP — at campaign start, after each accepted closure and at checkpoints, separating campaign-attributed outcomes from all repository activity. Compare equal windows before and after a scheduling change; small samples, differing difficulty, batch closures and other contributors all limit causal claims. If more workers do not improve delivery, identify the slowest stage and change one scheduling factor — never weaken acceptance or split issues to inflate the count.

## Leave a recoverable system

At every transition and checkpoint, persist revision, evidence summary, acceptance rows done and remaining, scope, blocker, owner and next action in the durable task record; local reports support it, but temporary paths do not survive a lost machine. At checkpoints report active workers and descendants, review and integration queue age, pending checks and next action. Before a context handoff, refresh the board and record what is running, what is idle and how to resume each — a message to an idle worker may not restart it.

Read [lessons and failure patterns](references/lessons.md) when diagnosing coordination waste. After a costly failure add the smallest supported improvement — observation → cause → rule → evidence the rule helped — keeping generic guidance here and project commands in the owning repository, and removing obsolete rules instead of accumulating incident folklore.
