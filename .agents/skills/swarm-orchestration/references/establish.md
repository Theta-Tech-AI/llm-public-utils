# 1. Establish the campaign

Read before the first dispatch and when a stage saturates. This stage fixes the scope, the definition of done, the baseline, the pool size and the proof setup.

## Fix the scope and the definition of done

1. Read the project guidance and each selected task in full: comments, dependencies, claims, acceptance criteria.
2. Turn each task into an acceptance matrix. List every required behavior, test, review, integration, release and live check. Mark each row demonstrated, outstanding, or not applicable (with reason and evidence).
3. A merged slice is not a completed task while an acceptance row is open. Do not invent a deploy or live row for a task that does not need one.
4. Record the exact event that permits closure: checked push to the named branch, merge, release or live acceptance. Use the operator's definition. Add no later gate, and drop no required one to cut the open count. Every live check that follows closure goes on the board with an owner ([0](coordinator-loop.md)).
5. Refresh the remote and the tracker before each assignment. A remote-tracking ref and a saved backlog are caches.
6. Record a baseline: member list, completed and total counts, timestamp, known outside contributors. Keep the denominator, so that a scope change cannot look like delivery.

## Size the pool

The useful pool has four limits: independent tasks, reviewer throughput, integration throughput, and shared resources (memory, disk, service quotas).

- Count running workers, nested descendants and CLI processes from the runtime before each launch. Configured slots, created agents and running workers are three different counts.
- A runtime can refuse launches silently at a fixed cap. If the host has headroom and you are authorized, raise the cap. Checkpoint workers first if the change needs a restart.
- Set a WIP limit for each stage. When review saturates, admit no new implementation and move agents to review. An idle slot can be correct; the board then records why.
- Add implementation only while finished items flow through review and integration without a growing wait. Nesting is not extra capacity.
- Size parallel work against measured memory and free disk, not against free slots. If `/tmp` is a small tmpfs, use a disk-backed ignored workspace with an owner and a cleanup plan.

## Pick the first tasks

- Start with small, unblocked tasks that can be verified independently.
- Rank by expected time to full acceptance and by dependency value, not by code size. Re-check aging and critical-path items so that easy items do not starve them.

## Proof is work

- **Build each fixture once and reuse it.** A fixture is a test project or environment at a given stage. Keep a maintained driver to each pipeline stage, and list prepared fixtures and their stage in the board's `fixtures[]`. Four workers once each spent 1–2 h bringing a project to the same stage by hand.
- **Inputs come from ground truth, or the worker stops.** Guessed defaults in demo or acceptance inputs caused most of one night's review findings. Synthetic data is fine only for a disposable test fixture.
- Before you fan out acceptance runs that share a path, run one representative case through its prerequisites. If several runs would stop at the same step, that step becomes a board item with an owner ([0](coordinator-loop.md), step 6).
- Before you brief a long UI run, search the repository for an existing driver or API path to the same artifact. Use the UI only for what must be seen in the UI.

## Failure patterns

- **More authors produced more patches but fewer closures.** Review and integration were saturated. Rule: WIP limits and reserved reviewers.
- **Many "easy" slices left the original tasks open.** Assignments optimized patch size, not acceptance. Rule: the acceptance matrix per task.
- **Sessions died in the middle of a wave, and temporary builds filled the disk.** The wave was sized by slots, and builds had no space budget. Rule: size by measured memory and disk; retire owned builds after you record their evidence.

Next: [2. Assign](assign.md)
