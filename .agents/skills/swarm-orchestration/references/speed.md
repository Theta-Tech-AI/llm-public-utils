# Speed: where the time goes, and the levers

Read this when the operator asks "why so slow" or "how do we go faster", and at every checkpoint where accepted
closures per hour fall. Speed is accepted outcomes per hour, not busy workers. Measure the clock first, then pull the
lever for the stage that holds the most time.

## Measure the item clock

For the items accepted in the last window, split each item's time into stages and report p50 and the largest:

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

Time the shared lanes separately (integration check run, deploy run, per step), from the CI or deploy system's own
timestamps, over at least five runs. One run is an anecdote. A lever is chosen from the largest measured stage, never
from a guess, and its effect is reported as predicted against measured on the next runs.

## Levers, in the order they usually pay

1. **Accept at the earliest point the owner's definition allows.** If done means "landed on the integration branch",
   close at push and name the live check that is left; a failed live check reopens the item. Waiting for every deploy
   to go green before closing added one deploy cycle to every item.
2. **Never block building on a shared deploy.** Workers prove on a local or private stack and hand over a branch; the
   live proof runs after landing and does not hold the next build. A worker that waits for a deploy is an idle slot.
3. **Push each batch the moment its combined checks pass.** A deploy queue that keeps one running run and the newest
   waiting run batches pushes for free; holding ready work "so deploys do not cancel" costs a full cycle.
4. **Scale the checks to the diff.** Docs, prompt and style-only batches run the fast gate, not the full suite. Run the
   full suite once per batch on the combined tree, never per branch on the coordinator. When the suite exceeds about
   five minutes, parallelise it (isolated database or schema per test worker) before it becomes the queue.
5. **Cut the deploy by its measured steps.** Skip a stage whose inputs did not change (input hash); move work that
   does not gate the verdict off the critical path; keep one standing worker on deploy speed whose every change is
   measured on the next runs. No paid shortcuts unless the operator asks for them.
6. **Keep risky shared-environment changes out of the integration lane.** A change that deliberately breaks the shared
   environment (a configuration rehearsal, an "off" direction) poisons every batch queued behind it. Rehearse it on a
   private environment, or push its repair in the same batch, and never queue unrelated batches behind a deploy you
   expect to fail.
7. **Spend the coordinator on the next landing slice.** Rank by remaining time to acceptance. Before spawning new
   work, review and integrate the branches that land next; a finished branch waiting for the coordinator is the most
   expensive queue. Delegate reports, charts and inventories to scripts or workers.
8. **Add workers only while integration keeps up.** Split by file ownership, not by issue; check overlap before
   dispatch and before each batch. Before dispatching item N, search commit messages on every remote branch for it
   (`git log --remotes --grep "#N"`) and read its latest comments; a hit means message the owner, never a second
   worker.
9. **Replace stuck workers fast.** A worker that ran out of context or repeats itself is replaced with a fresh one and a
   short verified handoff (branch, head, uncommitted files, checks run, decisions made); stop the old one first so the
   workspace has one owner.
10. **Decide reversible questions yourself.** A worker's "decision for you" that is reversible and has a clear
    recommendation is decided by the coordinator in the same turn; only money, production, security, irreversible data
    and regulatory choices go to the operator, batched as multiple choice.
11. **Allocate shared sequence numbers up front** (migrations, ports, container names). When a later number is ready
    first, swap the numbers; do not land placeholders.
12. **Expect inflow.** Test runs and panels file real defects; report opened and closed per hour separately and give
    each new defect a worker in the same turn, so the count falls after the next batch instead of drifting.

## Failure patterns

- **The open count stayed high while every branch was green.** — Closure waited for a deploy the owner's definition did
  not require. Lever 1. Evidence: items closed at push versus at deploy, minutes saved per item.
- **Two deploys in a row failed and three batches waited behind them.** — A deliberately breaking configuration
  rehearsal ran in the shared lane, and the next batch carried the same setting. Lever 6. Evidence: failed runs and the
  queue age behind them.
- **A second worker rebuilt an issue already on another branch.** — The duplicate check searched branch names, not
  commit messages. Lever 8. Evidence: overlapping files between the two branches.

---

Related: [measurement](measurement.md) · [planning and capacity](planning-and-capacity.md) · [validation and review](validation-and-review.md)
