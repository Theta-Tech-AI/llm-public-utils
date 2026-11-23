---
name: swarm-orchestration
description: "Coordinate multiple agents doing parallel work: capacity, ownership, independent review, integration, handoff recovery, and accepted delivery rates. Use for delegation, parallel backlogs, worker expansion, nested subagents, CLI agents, review queues, rework, or stalled multi-agent delivery. Do not load for ordinary solo implementation, application concurrency, or one isolated helper task without coordination needs."
---

# Swarm orchestration

Optimize the rate of accepted outcomes, not the number of busy agents. The coordinator owns scope, scheduling, integration and the delivery decision. Workers own bounded assignments. Reviewers give independent evidence.

This skill is portable. Use the available agent runtime, task tracker, version control and checks. Follow the user's model choices and the repository's rules. The skill grants no permission to delegate, publish, merge, deploy or contact people.

## Start here: the coordinator loop

Read [0. The coordinator loop](references/coordinator-loop.md) first. Run it every 30 minutes, before every status reply, and whenever a worker hands back. Every worker appends a status line at each step change ([the brief](references/assign.md#the-brief)). The coordinator keeps a machine-readable board. Two scripts read them:

- `python3 scripts/board_check.py BOARD.json --status-dir DIR [--watch 10]` lists what needs the coordinator: late, stuck or looping workers, failed replies, unowned items, shared blockers and live checks, late items, red pipelines, full environments, waiting hand-backs, idle capacity. With `--watch` it runs in the background and wakes you at the first finding.
- `python3 scripts/progress_chart.py --board BOARD.json --focus-group NAME OUT.png` draws the open set from the same board.

A status comes from the loop's output in the same turn, never from memory. "Has an owner" is not "is moving". Fix a weak signal; never widen its threshold.

## The stages

Each item moves through `ready → implementing → review → integrating → acceptance → done`. Use only the stages that the task needs. Each rule lives in one stage reference.

| Stage | Read this when you... |
|---|---|
| 0. [Coordinator loop](references/coordinator-loop.md) | run the cadence, answer "is everything moving?", or write a status |
| 1. [Establish](references/establish.md) | start a campaign, size the pool, pick first tasks, prepare fixtures |
| 2. [Assign](references/assign.md) | dispatch, choose a model, hand a lane over, or route a decision |
| 3. [Build](references/build.md) | start workers, use CLI or nested agents, share a host or workspace |
| 4. [Review](references/review.md) | accept a handoff, approve a revision, cap a review loop |
| 5. [Integrate and deliver](references/integrate-and-deliver.md) | push, merge, bump a dependency, claim "live", or close an item |
| 6. [Measure](references/measure.md) | report rates, queues or the open set, or draw the chart |
| 7. [Speed](references/speed.md) | closures per hour fall, or the operator asks how to go faster |
| 8. [Recover](references/recover.md) | a worker goes quiet or stops, you hand off context, or the day ends (retro) |

## Rules for every turn

1. **Done means accepted.** Close only on the recorded closure event, with evidence. [1](references/establish.md), [5](references/integrate-and-deliver.md)
2. **Live state beats memory.** A worker summary is a claim. Verify it against an artifact or live state. [0](references/coordinator-loop.md), [2](references/assign.md)
3. **One deliverable, one workspace, one owner per item**, through acceptance. [2](references/assign.md)
4. **Review is independent and pinned to one revision.** After three rounds of the same class of finding, stop patching and escalate. [4](references/review.md)
5. **Merged, deployed and live are three facts.** Claim each with its own evidence. [5](references/integrate-and-deliver.md)
6. **Decide covered reversible choices yourself.** Send the operator only unresolved decisions, with the verified premise, as one batched multiple-choice question. [2](references/assign.md)
7. **A permission denial ends the slice.** Report it. Do not retry it or pass it to a peer.
8. **Keep secrets out of output.** Ask for the specific non-secret fact.
9. **The board and the tracker are the state.** A failed query is unknown, never zero. [8](references/recover.md)

## Improve the skill

After a costly failure, follow [8. Recover](references/recover.md#improve-the-skill-after-a-costly-failure).
