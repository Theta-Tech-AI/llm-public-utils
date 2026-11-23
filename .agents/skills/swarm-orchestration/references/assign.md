# 2. Assign the work

Read when you dispatch, choose a model, brief workers, hand a lane over, or route a decision.

## The assignment record

Keep one record per item in the durable tracker, next to its acceptance criteria. Its board row ([0](coordinator-loop.md)) points to it. Omit fields that do not apply.

```text
Task and intended outcome / acceptance rows, including live rows:
Owner (model) / independent reviewer / coordinator:
Workspace / real remote / branch / baseline revision:
Allowed paths / excluded scope / shared resources:
Next event and expected time:

Final revision and changed paths / composition (upstream + overlay + generated inputs):
Checks: command, directory, tool version, result, durable evidence:
Review: reviewer identity, exact revision, findings, resolution, round count:
Delivery: link, target, exact head, merge revision / remaining rows:
Blocker / next action / owner / updated at:
```

A local path or "tests pass" is not a durable result.

## Rules for each assignment

- Give each worker one bounded deliverable that fits one worker budget: outcome, allowed paths, baseline, exclusions, checks, reviewer, publication authority, and the next checkpoint with an expected time.
- Each worker gets its own workspace and a unique branch name. If the name is taken, the worker fails loudly and does not rename.
- The item owner stays responsible through review, integration and acceptance.
- Split by independent concern and by file ownership, not by issue. Keep tightly coupled interfaces under one owner. Use another agent for tests or review, never for a competing implementation.
- Every worker gets the same brief ([below](#the-brief)). To change a rule, edit the brief and message the running workers.
- **A helper that signs, approves or writes audit evidence is checked by the coordinator before any worker uses it.** One helper recorded a re-authentication that never happened. When in doubt, the worker stops at the signature and reports. A worker that refuses is right.
- A checkpoint limit ends one attempt, not the task. Record the evidence, replan, continue.

## The brief

Every brief carries these lines. Adapt the wording; keep each contract.

```text
Deliverable: <one outcome>; paths <allowed>; baseline <revision>; not in scope: <...>.
Done when: <checks + evidence>; reviewer: <identity>; you may push to <branch> / hand to <integration owner>.
Status: at every step change append one JSON line to <status dir>/<your id>.jsonl:
  {"at", "step", "waiting_on", "expected_end", "last_result", "round", "finding_class"}.
  When a review round returns, write its finding_class on that line ("none" for a clean round).
  If a message to the coordinator fails, write it there as "unsent" and carry on.
Reply address: <exact address that was tested at dispatch>, or "none: write your status file only".
Never idle-wait: start long checks (tests, a second-model review) in the background and do the next piece
  of the lane meanwhile (its live check, docs, a deslop pass on your own diff). Batch findings per round.
Reversible choices: if <A or B>, take your recommendation, say so in the status line, and continue.
Stop and report only for: <scope change, spending, production, security, signatures or audit evidence>.
Same finding class in three review rounds: stop patching; write the invariants (review.md).
Use the shared test runner <command>. Stop only processes you started, by exact PID.
```

- **Verify the reply channel at dispatch.** Send the worker a test line and see its answer, or tell it to rely on its status file only. Three workers once tried to answer liveness polls, and the sends failed with "recipient not reachable".
- **Pre-authorize the recommended option** for reversible choices, so that a worker does not stop to ask. A hand-back that waits on the coordinator costs the whole lane.
- **Never idle-wait.** One review round takes 10–20 min, and a test run 2–7 min. Run in the foreground over 5–27 rounds, that is hours of idle wall time per lane.

## Choose the model

Follow the operator's model choices. Where you choose:

| Work | Model |
|---|---|
| Routine building, fixes with a known cause, sweeps, fixtures | the routine (cheaper) model |
| Security or compliance design; anything that writes audit or signature evidence | the strongest model from the start |
| Diagnosis with no known cause | the strongest model from the start |
| Skill, prompt or process design | the strongest model from the start |
| Review and the delivery decision | the coordinator, or the strongest available reviewer |

Two review loops of 12 and 27 rounds ran on a mid-tier model, with the same class of finding each round. Escalation rule: [4](review.md#cap-the-review-loop). Handover: [below](#hand-a-lane-over).

## Hand a lane over

Hand over on a model change, a scope change, a review loop past its cap, or an owner that does not answer a liveness poll within one step (about 15 minutes). A compliance lane once sat 65 minutes quiet, after three failed review rounds, before it moved.

1. The old owner pushes its head and writes a state note on the item: every review finding so far, what was tried, what is open. Then it stops. If it does not answer, the coordinator stops it and reads its pushed head and status file.
2. The coordinator confirms that the old owner and its descendants ended, and reads back its commits and comments.
3. The new owner starts from the pushed head and the note, nothing else. The board's `owner` changes.

## Prevent duplicates and collisions

- Before you dispatch item N, run `git log --remotes --oneline --grep "#N"` and read the latest comments for a claim. A hit means resume or message the owner. Search commit messages, not branch names: a duplicate once overlapped 18 files of a differently named branch.
- Compute file overlap at dispatch (`git diff --name-only <base>...<branch>` for every open branch) and again for each integration batch. One owner per file, or sequence the second lane after the first lands.
- Allocate sequence-numbered names (migration numbers, ports, id ranges) before work starts. Check for collisions at merge.

## Rank and refill

Rank by remaining effort to full acceptance, including review, repair, integration and live rows. The slowest stage controls intake. Order for a free agent, unless aging or a critical dependency says otherwise:

1. ready work that can pass the final delivery step;
2. small repairs that release reviewed work;
3. reviews and acceptance checks;
4. prerequisites that unblock several items;
5. new independent implementation.

When a slot frees, the loop's step 9 ([0](coordinator-loop.md)) fills it. Start the next task and confirm that it runs: a queued message may not restart a finished worker. A CI or deploy wait does not block unrelated work.

## Route decisions

- Before you ask for a decision or call work blocked, check the requirement, the code, the configuration and the recorded authorization. **Verify an item's premise before you ask the operator to re-scope on it.** Two re-scope questions in one evening rested on guesses ("the feature is missing", "the files are scanned"). Ten minutes of reading would have withdrawn them.
- Decide reversible choices within existing authorization in the same turn, and say so. Ask only about scope, new spending, uncovered production or security actions, irreversible or regulated data, or a choice reserved to the operator. Send one batched multiple-choice question after all unblocked work is dispatched.
- A permission or policy denial ends that slice. Hand the operator the one command. A peer that runs it is not the operator's consent.
- Worker summaries are claims. Check a claim about running-system state (a stuck queue, a livelock) against logs or data before you relay it. Give workers the observation and the competing causes, not a required diagnosis. When a claim is disproved, correct every brief that used it.

## Iterate a skill or prompt

Write it, get a cold-read critique, trial it with a friction log, revise with a new worker, trial again. Keep expected answers and earlier findings out of a blind trial's text and context. A trial that finds the answer unaided is the pass signal.

## Failure patterns

- **The coordinator kept planning improvements while ready work waited.** Process work had no bound. Rule: make one improvement aimed at the current bottleneck, apply it, and resume delivery.
- **Several workers shared one issue queue, and an issue waited.** Rule: when the issues are independent and own different files, give each issue its own worker (the loop's step 9).

Next: [3. Build](build.md)
