# 1. Establish the campaign

Read before the first dispatch and when a stage saturates. This stage fixes the scope, the definition of done, the baseline, and the size of the pool.

## Fix the scope and the definition of done

1. Read the project guidance and each selected task in full: comments, dependencies, claims, acceptance criteria.
2. Turn each task into an acceptance matrix. List every required behavior, test, review, integration, release and live check. Mark each row demonstrated, outstanding, or not applicable (with a reason and evidence).
3. Separate implementation, independent review, integration, release and live acceptance when they are distinct requirements. A merged slice is not a completed task while an acceptance row is open. Do not invent a deploy or live row for a task that does not need one.
4. Record the exact event that permits closure: checked push to the named branch, merge, release or live acceptance. Use the operator's definition. Add no later gate and drop no required one to cut the open count. If the operator changes it, update the item records, briefs and closing step together. Give every live check that follows closure an owner, a trigger and a failure action.
5. Refresh the provider remote and the task state before each assignment. A remote-tracking ref and a saved backlog are caches, not proof of current state.
6. Record a baseline: member list, completed and total counts, timestamp, recent completions, known outside contributors. Keep the denominator, so that a scope change cannot look like delivery.

## Choose work before choosing worker count

The useful pool has four limits: independent tasks, reviewer throughput, integration throughput, and shared resources.

- Count running workers, nested descendants and CLI processes from the runtime before each launch. Configured slots, created agents and active workers are three different counts. Resuming a finished worker takes a slot.
- A runtime can refuse launches silently at a fixed cap. When that happens, check first that concurrency is the real bottleneck. If the host has headroom (load, memory), the setting is supported, and you are authorized, raise the cap. Checkpoint the workers first if the change needs a restart.
- Start with a small delivery set. Reserve reviewer capacity. Set a WIP limit for each stage: implementation, review, integration, acceptance. When review saturates, admit no new implementation and move qualified agents to review. An idle slot can be correct.
- Choose the pool size from observed completion and review times, not from a sample size. Add implementation work only while finished items flow through review and integration without a growing wait.
- Nesting is not extra capacity. A tree of supervisors that only waits adds delay.
- When the operator sets a worker target, record each slot's state and next assignment. Query the runtime just before you report; report the number running now and the shortfall.

## Pick the first tasks

- Start with small, unblocked tasks that can be verified independently.
- Rank by expected time to full acceptance and by dependency value, not by code size. A task across three repositories with live acceptance can finish later than a larger local change.
- Re-check aging and critical-path items, so that easy items do not starve them.
- When two or more lanes stop on the same gap, open one investigation of that gap and rank it first. It unlocks more closures than any single lane.
- Before you fan out acceptance runs that share a user path, run one representative case through its prerequisites by the normal entry point. Record the fixture, roles, data, expected artifact and first blocking step. If several runs would stop there, give the blocker one owner and pause only the dependent runs.
- Give spare agents work that clears the current bottleneck: reproduce a CI failure, check the full scope of an issue, prepare an acceptance fixture, review a ready change. Do not invent work to keep a dashboard busy.

## Check the host first

- Confirm that the shared read-only source artifact exists before you dispatch work into exclusive clones.
- Check free space and inodes on the real filesystem before cloning or composing. If `/tmp` is a small tmpfs, use an ignored, disk-backed workspace. Record its owner and cleanup plan.
- Size parallel work against measured memory, not against free slots.

## Failure patterns

- **More authors produced more patches but fewer closures.** — Review, CI repair and publication were saturated. Rule: limit active delivery items and reserve reviewers. Evidence: closures per hour, review age, rework.
- **Many "easy" slices left the original tasks open.** — Assignments optimized patch size, not full acceptance. Rule: audit the whole task scope before selection and keep a per-row matrix. Evidence: remaining rows against actual closures.
- **A 16-agent campaign had one agent running while the coordinator reported 16.** — Agents were counted after their turns ended. Rule: query live state before each capacity report. Evidence: runtime running count against slot assignments.
- **Sessions died in the middle of a wave.** — The wave was sized by slots, not by host memory. Rule: size by measured memory; a killed session leaves no completion report, so confirm that a silent worker died and did not finish. Evidence: silent workers that never resume.
- **Temporary builds filled the filesystem and stopped even cleanup commands.** — Retained compositions had no space budget or owner. Rule: check space before expansion; retire owned builds after you record revisions and evidence. Evidence: free space, free inodes, retained size.

Next: [2. Assign](assign.md) · Pool sizing feeds [7. Speed](speed.md)
