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

1. **Done means accepted.** A merged slice is not a completed task while an acceptance row is open. Close only on evidence.
2. **Live state beats memory.** Refresh the remote, the task and the runtime roster before you assign, report or merge. A worker summary is a claim. Verify it against an artifact or live state.
3. **One bounded deliverable, one workspace, one owner per item.** Give the owner through review, integration and acceptance.
4. **Limit work in progress by the slowest stage.** Reserve capacity for review and integration. When review saturates, admit no new implementation. An idle slot can be correct.
5. **Rank by time to full acceptance.** Almost-finished work outranks new easy work. Re-rank at every stage change.
6. **Refill at every completion.** Before a CI wait or a status reply, refresh the roster and give each free slot a task or record its real limit.
7. **Review is independent and pinned to a revision.** Author and reviewer are different actors. An amendment voids the review.
8. **Validate the exact composed source** in the same context as CI. Never reuse a stale tree.
9. **Merged, deployed and live are three facts.** Claim each with its own evidence.
10. **Decide reversible choices yourself.** Send scope, money, production, security, irreversible and regulated-data choices to the operator, as one batched multiple-choice question after all unblocked work is dispatched.
11. **A permission denial ends the slice.** Report it and give the operator the one command. Do not retry it or pass it to a peer.
12. **Keep secrets out of output.** Ask for the specific non-secret fact.
13. **Write state to the durable task record** at each transition. Local paths and chat do not survive.
14. **A failed query is unknown, never zero.**

## Improve the skill

After a costly failure, add one lesson to the stage reference that owns it: observation, cause, rule, evidence. If you cannot state the evidence, do not add it. Delete obsolete and tooling-enforced rules. Keep generic guidance here and local commands in the owning project.
