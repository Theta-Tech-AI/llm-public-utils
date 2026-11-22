---
name: swarm-orchestration
description: "Coordinate multiple agents doing parallel work: capacity, ownership, independent review, integration, handoff recovery, and accepted delivery rates. Use for delegation, parallel backlogs, worker expansion, nested subagents, CLI agents, review queues, rework, or stalled multi-agent delivery. Do not load for ordinary solo implementation, application concurrency, or one isolated helper task without coordination needs."
---

# Swarm orchestration

Optimize the rate of accepted outcomes, not the number of busy agents. The coordinator owns scope, scheduling, integration and the delivery decision. Workers own bounded assignments. Reviewers give independent evidence. More workers help only while the later stages can accept their output.

This skill is portable. Use the agent runtime, task tracker, version control and checks that you have. Follow the user's model choices and the repository's rules. The skill does not grant permission to delegate, publish, merge, deploy or contact people. Use existing authorization. Do not build a scheduler or service when a task board and short records are enough.

## The pipeline

Each item moves through `ready → implementing → review → integrating → acceptance → done`, with a blocked reason when needed. Use only the stages that the task needs. Keep one record per item: owner, immutable revision, next action, evidence. Each stage has one reference. Each rule is stated once, in its stage.

| Stage | Read this when you... |
|---|---|
| 1. [Establish](references/establish.md) | start a campaign, size the pool, pick the first tasks, or a stage saturates |
| 2. [Assign](references/assign.md) | dispatch, brief, re-rank, refill a slot, or route a decision |
| 3. [Build](references/build.md) | start or expand workers, use CLI or nested agents, share a host or workspace |
| 4. [Review](references/review.md) | accept a handoff, approve a revision, or debug a failing check |
| 5. [Integrate and deliver](references/integrate-and-deliver.md) | push, merge, claim "live", or close an item |
| 6. [Measure](references/measure.md) | report rates, queues, the open set, or run a scheduling experiment |
| 7. [Speed](references/speed.md) | closures per hour fall, or the operator asks how to go faster |
| 8. [Recover](references/recover.md) | check the roster, a worker goes quiet or stops, or you hand off context |

Each reference ends with its failure patterns in the form symptom — cause — rule — evidence. Read the one that matches the stage you are diagnosing.

## Rules for every turn

Each rule has one owner stage. Read it there for the conditions.

1. **Done means accepted.** Close only on the recorded closure event, with evidence. [1](references/establish.md), [5](references/integrate-and-deliver.md)
2. **Live state beats memory.** A worker summary is a claim. Verify it against an artifact or live state. [2](references/assign.md)
3. **One deliverable, one workspace, one owner per item**, through acceptance. [2](references/assign.md), [3](references/build.md)
4. **The slowest stage limits work in progress.** Rank by time to full acceptance, and refill every free slot at each completion. [1](references/establish.md), [2](references/assign.md)
5. **Review is independent and pinned to one revision.** Validate the exact composed source as CI does. [4](references/review.md)
6. **Merged, deployed and live are three facts.** Claim each with its own evidence. [5](references/integrate-and-deliver.md)
7. **Use existing authorization and verify blockers.** Decide covered reversible choices yourself. Send only unresolved operator decisions, with the verified missing fact, as one batched question after unblocked work is dispatched. [2](references/assign.md)
8. **A permission denial ends the slice.** Report it. Do not retry it or pass it to a peer.
9. **Keep secrets out of output.** Ask for the specific non-secret fact.
10. **Write state to the durable task record** at each transition. A failed query is unknown, never zero. [8](references/recover.md)

## Improve the skill

After a costly failure, follow [8. Recover](references/recover.md#improve-the-skill-after-a-costly-failure).
