# 7. Speed: where the time goes

Read when the operator asks "why so slow" or "how do we go faster", and when accepted closures per hour fall. Speed is accepted outcomes per hour, not busy workers. Measure the item clock first. Then pull the lever for the stage that holds the most time.

## Measure the item clock

For the items accepted in the last window, split each item's time into stages. Report p50 and the largest.

| Stage | Starts | Ends |
|---|---|---|
| Wait for an owner | item ready | worker assigned |
| Build | assigned | branch head with the worker's checks green |
| Review | head ready | independent review passes on that head |
| Integration checks | branch picked for a batch | combined checks green |
| Landing wait | checks green | pushed to the integration branch |
| Deploy queue and deploy | pushed | deployed and healthy |
| Live proof | deployed | acceptance evidence recorded |
| Inflow | — | items opened in the window (test runs, panels, reviewers) |

Time the shared lanes (integration check run, deploy run, each step) from the CI or deploy system's own timestamps, over at least five runs. One run is an anecdote. Choose a lever from the largest measured stage, never from a guess. After the change, report predicted against measured on the next runs.

## Levers, in the order they usually pay

1. **Accept at the earliest point the owner's definition allows.** If done means "landed on the integration branch", close at push and name the live check that is left. A failed live check reopens the item. Waiting for every deploy added one deploy cycle to every item.
2. **Never block building on a shared deploy.** Workers prove on a local or private stack and hand over a branch. Live proof runs after landing and does not hold the next build. A worker that waits for a deploy is an idle slot.
3. **Push each batch when its combined checks pass.** A deploy queue that keeps one running run and the newest waiting run batches pushes for free. Holding ready work "so deploys do not cancel" costs a full cycle. Batching rules: [5](integrate-and-deliver.md).
4. **Scale the checks to the diff.** Docs, prompt and style-only batches run the fast gate. Run the full suite once per batch on the combined tree, never per branch on the coordinator. If the suite takes more than about five minutes, parallelise it (an isolated database or schema per test worker) before it becomes the queue.
5. **Cut the deploy by its measured steps.** Skip a stage whose inputs did not change (input hash). Move work that does not gate the verdict off the critical path. Keep one standing worker on deploy speed, and measure each change on the next runs. Offer paid shortcuts only if the operator asks.
6. **Keep risky shared-environment changes out of the integration lane.** A change that deliberately breaks the shared environment (a configuration rehearsal, an "off" direction) poisons every batch behind it. Rehearse it on a private environment, or push its repair in the same batch. Never queue unrelated batches behind a deploy that you expect to fail.
7. **Spend the coordinator on the next landing slice.** Before you spawn new work, review and integrate the branches that land next. A finished branch that waits for the coordinator is the most expensive queue. Give reports, charts and inventories to scripts or workers.
8. **Add workers only while integration keeps up.** Split by file ownership: [2](assign.md).
9. **Expect inflow.** Test runs and panels file real defects. Report opened and closed per hour apart. Give each new defect a worker in the same turn, so that the count falls after the next batch.

## Failure patterns

- **The open count stayed high while every branch was green.** — Closure waited for a deploy that the owner's definition did not require. Lever 1. Evidence: items closed at push against at deploy, minutes saved per item.
- **Two deploys in a row failed and three batches waited behind them.** — A deliberately breaking rehearsal ran in the shared lane, and the next batch carried the same setting. Lever 6. Evidence: failed runs and queue age behind them.

Next: [8. Recover](recover.md) · Related: [6. Measure](measure.md)
