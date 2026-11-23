# 0. The coordinator loop

The coordinator's main job is to run this loop. Run it:

- on a fixed cadence (default every 30 minutes), woken by a background checker, not by the operator's questions;
- before every status reply;
- whenever a worker hands back, finishes or stops.

Each step reads live state and writes the board. **A status is generated from the loop's output in the same turn, never from memory or from the dispatch record.** **"Has an owner" is not "is moving"**: an item moves only when its next event arrives by its expected time. **Liveness is not progress**: a worker in review round 20 answers a ping at once and still does not converge.

## The board

Keep one machine-readable board: a JSON file in a durable place, mirrored to the tracker at each milestone. It holds the state the coordinator would otherwise keep in context, so a context summary or a lost session costs nothing. `scripts/board_check.py` reads it, and `scripts/progress_chart.py --board` draws it. `tests/board_fixture.json` with `tests/status_fixture/` is a worked example.

| Key | Fields (required in bold) | Meaning |
|---|---|---|
| `updated` | ISO-8601 UTC | when the board was last refreshed from the tracker |
| `items[]` | **id, what, stage, owner, next_event, expected_by**, group, area, waits_on, live_check, live_check_owner, blocks | one row per open item, or per closed item with a live check left |
| `sweeps[]` | **id, what, owner**, next_event, expected_by | standing work: live-check sweeps, a promotion, a dependency bump, a verify-and-close pass |
| `workers[]` | **id, model**, pace_min, reported | every running worker; `id` names its status file and activity record |
| `pipelines[]` | **name, result, checked**, owner | the last run of every CI/CD workflow, not only the deploy |
| `environments[]` | **name, capacity, in_use** | shared capacity: test stacks, model quota, a signing path |
| `handbacks[]` | **worker, what, at**, answered | each hand-back to the coordinator and when it was answered |
| `fixtures[]` | **name, env, stage**, used_by | prepared test projects and the stage each has reached |
| `capacity` | **target**, idle_reason | the worker target, and the written reason when slots stay idle |
| `stages[]`, `groups[]` | name, always_show / name, color | order of operations and group colours, for the chart |

- `owner` is a worker id, a named person or an outside party, or a list. `null` is a finding.
- `waits_on` names ONE thing, the next one, not a chain. Use the item or sweep id when that thing is on the board. Leave it empty when the item waits only on its own owner's work.
- `next_event` + `expected_by` make lateness a comparison, not a judgement.
- `live_check` is the check left after closure; `live_check_owner` is set with it.

## The worker status file

Every worker appends one JSON line to `<status dir>/<worker id>.jsonl` at every step change, as its brief requires ([2](assign.md#the-brief)): `at, step, waiting_on, expected_end, last_result, round, finding_class`, and `unsent` when a message to the coordinator failed. **The status file is the primary signal because it needs no message channel.** Observation: three workers' replies to liveness polls failed ("recipient not reachable"). They looked silent, and their words arrived only in the final hand-back.

Transcript or output modification time is a fallback only. It gives false alarms (one long tool call writes nothing) and misses (a finished worker writes nothing). **Fix the signal; never widen the threshold.** One coordinator answered false alarms by raising the quiet threshold from 15 to 75 minutes, until the watcher was blind.

## The heartbeat

Start the checker in the background at the start of the campaign, and again after every loop:

```text
python3 scripts/board_check.py BOARD.json --status-dir DIR --watch 10 --deadline-min 240
```

It exits at the first finding, which wakes the coordinator, or with 0 at its deadline. Then the coordinator runs the loop. Without the heartbeat, checks run only when the operator asks. Operator questions and merges then take every coordinator turn.

## The loop

Run the steps in order. Write what changed to the board before the next step.

1. **Answer hand-backs first.** A worker waiting on a decision or a merge is the most expensive queue. Answer each within 10 minutes; `board_check.py` prints the measured coordinator latency. Record `answered`.
2. **Refresh the board from the tracker.** Read open and new items, closures and comments. Add, remove and restage rows. Set `updated`.
3. **Capacity.** Read the host load, free memory, the runtime's count of running workers, and each environment's `in_use` against its `capacity`. Cap concurrent proofs to the environment: 17 proof runs on one small environment once gave 40 min of rate-limit refusals and made every run 5–9 times slower.
4. **Progress and liveness.** Run `board_check.py BOARD --status-dir DIR`. It flags a worker that is late past its expected end, has no step or round change for an hour, loops on one finding class for three rounds, writes no status, or failed to reach you. For a late worker, send one line: "what are you doing, what do you wait on, expected end". Read what the runtime says the send did. A runtime notice that a worker "finished" or "waits on its own background work" is evidence, not noise: one such notice was a worker that had stopped for good. No answer within one step (about 15 minutes): list its processes, then hand the lane over ([2](assign.md#hand-a-lane-over)).
5. **Every pipeline's last run.** Read the last run of every workflow: tests, deploys, scheduled jobs, infrastructure applies, advisory jobs. A red run that "blocks nothing" still gets an owner: an advisory job red for hours hides the next real failure.
6. **One wait per item.** Each item names the ONE thing it waits on, and its next event with an expected time. Ask the owner of a late item why, and replan.
7. **Shared blockers become items.** When two or more items wait on the same thing, that thing becomes an item with its own owner at once. No worker routes around a shared blocker on its own: a workaround for a signature, an approval or audit evidence can write false evidence.
8. **Every live check has an owner.** Usually one sweep worker takes logs and infrastructure, and one takes the UI.
9. **Fill idle capacity.** For each free slot, take the first useful item:
   1. an unowned or late live check;
   2. a shared blocker without a worker;
   3. a fixture that two or more proofs need (build it once from ground truth; list it in `fixtures[]`);
   4. a verify-and-close sweep over items done on the integration branch but still open ([5](integrate-and-deliver.md));
   5. a split: one queue that two items share gets one worker per item, when they own different files;
   6. the dependency bump for fixes merged upstream;
   7. a deslop pass over what just landed;
   8. review of a ready branch ([4](review.md)).

   A slot stays idle only with a written `idle_reason`.
10. **Re-ask decisions whose premise changed.** Example: "promote after the exports finish" became circular when the exports needed the promotion. Before you ask the operator to re-scope an item, verify its premise in the code or in one real file.

Run `board_check.py` again until it exits 0, or until each finding has a written next action. Restart the heartbeat. Draw any chart with `progress_chart.py --board` ([6](measure.md)).

## Status from the loop

A status reply holds the stage counts, the findings and what you did about each, late items with their new time, and the operator's decisions as multiple choice, all from the board. Never write "every item has a worker", "nothing is stalled" or "all moving" without this loop's output from the same turn. Name the time of the check.

## Failure patterns

- **Asked "are they all moving?", the coordinator twice answered "all alive". A check minutes later found load 4 of 32 cores, 6 workers for 14 items and 4 workers quiet 46–57 min. It also found a dead workflow, an unowned dependency bump, 13 live checks with no owner and six items on one unowned blocker.** Cause: the answer came from the dispatch record and a blind watcher. There was no scheduled probe, no expected times, and only the deploy was watched. Rule: the heartbeat, this loop, and a status from its output.
- **Chart counts were typed from memory and were wrong three times.** Rule: draw from the board.
- **Workers waited 20–60 min for hand-backs while the coordinator answered the operator and merged.** The coordinator was the narrowest stage and did not measure itself. Rule: step 1; an integration owner lands batches ([5](integrate-and-deliver.md)); briefs pre-authorize the recommended option.
- **An accidental interrupt stopped every worker, and none could be resumed.** Restart worked because branches and tracker comments held the state. Rule: the board and the tracker are the state.

Next: [1. Establish](establish.md) · End of day: [8. Recover](recover.md#retro-at-the-end-of-each-day)
