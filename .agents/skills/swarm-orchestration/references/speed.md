# 7. Speed: where the time goes

Read when the operator asks "why so slow" or "how do we go faster", and when accepted closures per hour fall. Speed is accepted outcomes per hour, not busy workers. Measure the item clock first. Then pull the lever for the stage that holds the most time.

## Measure the item clock

For the items accepted in the last window, split each item's time into stages. Report p50 and the largest.

| Stage | Starts | Ends |
|---|---|---|
| Wait for an owner | item ready | worker assigned |
| Build | assigned | branch head with the worker's checks green |
| Coordinator latency | a hand-back (decision, ready to land) | the coordinator's answer or merge; target under 10 min |
| Review | head ready | independent review passes on that head |
| Integration checks | branch picked for a batch | combined checks green |
| Landing wait | checks green | pushed to the integration branch |
| Deploy queue and deploy | pushed | deployed and healthy |
| Live proof | deployed | acceptance evidence recorded |
| Inflow | — | items opened in the window (test runs, panels, reviewers) |

Time the shared lanes (integration check run, deploy run, each step) from the CI or deploy system's own timestamps, over at least five runs. One run is an anecdote. Choose a lever from the largest measured stage, never from a guess. After the change, report predicted against measured on the next runs.

## Levers, in the order they usually pay

1. **Close at the recorded closure event ([1](establish.md)).** If that is "landed on the integration branch", close at push and name the live check that is left. A failed live check reopens the item. Waiting for every deploy added one deploy cycle to every item.
2. **Never block building on a wait.** Workers prove on a local or private stack and hand over a branch; live proof runs after landing. Long checks run in the background while the worker takes the next piece of its lane. A worker that waits for a deploy, a test run or a review round is an idle slot.
3. **Push when the verified queue policy allows.** Use the policy recorded in [5](integrate-and-deliver.md). Do not hold a checked batch because another deploy runs.
4. **Scale the checks to the changed behavior.** Run the full suite once per batch on the combined tree when its contracts are affected. A prompt-only change may skip unrelated code tests but needs a representative behavioral trial. Compare output, tool use, cost and elapsed time with the previous prompt. A fast code gate cannot supply that evidence. A prose or style edit needs only the checks for what it can change. If checks dominate the next landing, try bounded parallel shards with isolated test state. Compare elapsed time under the same host load. Keep the split only if it shortens the blocking check without more failures or starving another landing.
5. **Cut the deploy by its measured steps.** Skip a stage whose inputs did not change (input hash). Move work that does not gate the verdict off the critical path. Keep one standing worker on deploy speed, and measure each change on the next runs. Offer paid shortcuts only if the operator asks.
6. **Keep risky shared-environment changes out of the integration lane.** A change that deliberately breaks the shared environment (a configuration rehearsal, an "off" direction) poisons every batch behind it. Rehearse it on a private environment, or push its repair in the same batch. Never queue unrelated batches behind a deploy that you expect to fail.
7. **Take the coordinator off the critical path.** Answer hand-backs first, pre-authorize recommended options in briefs ([2](assign.md#the-brief)), and give landing to an integration owner ([5](integrate-and-deliver.md)). Give reports, charts and inventories to scripts. `board_check.py` prints the measured coordinator latency.
8. **Add workers only while integration keeps up.** Sizing: [1](establish.md). Split by file ownership: [2](assign.md).
9. **Expect inflow.** Test runs and panels file real defects. Report opened and closed per hour apart. Give each new defect a worker in the same turn, so that the count falls after the next batch.

## Failure patterns

- **The coordinator explained a slow stage before it was measured, and was wrong.** — It inferred from a long input list that script edits re-ran the whole infrastructure apply; the measurement showed the apply already skipped itself and most runs had real template changes. Rule: answer "why is it slow" with the measured table, or say "measuring" and send the worker first. Evidence: a retracted explanation.

- **The open count stayed high while every branch was green.** — Closure waited for a deploy that the owner's definition did not require. Lever 1. Evidence: items closed at push against at deploy, minutes saved per item.
- **Two deploys in a row failed and three batches waited behind them.** — A deliberately breaking rehearsal ran in the shared lane, and the next batch carried the same setting. Lever 6. Evidence: failed runs and queue age behind them.

Next: [8. Recover](recover.md) · Related: [6. Measure](measure.md)
