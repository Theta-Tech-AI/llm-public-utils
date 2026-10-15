# Lessons: execution and coordination

These rules come from observed multi-agent delivery failures. They are portable causes and corrections, not a claim that every campaign needs the same pool or tools.

Failures in how work is chosen, dispatched, staffed, and kept running.

Each row is one failure: the observation, its cause, the correction, and the evidence to watch.

| Observation | Cause | Correction |
|---|---|---|
| More authors produced more patches but fewer closures. | Review, CI repair, and publication were saturated. | Limit active delivery items; reserve reviewers; clear the ready queue before starting more code. Evidence to watch: Closures/hour, review age, accepted work, rework. |
| The coordinator kept planning improvements while ready work waited. | Process work had no delivery bound. | Make one small improvement aimed at the current bottleneck, apply it to the next item, and resume delivery. Delegate preparation around the coordinator's final decision, and measure the improvement by shorter queue age and more accepted outcomes rather than more process artifacts. |
| Many “easy” slices left the original tasks open. | Assignments optimized patch size instead of full acceptance. | Audit complete issue scope before selection; keep a per-row acceptance matrix. Evidence to watch: Remaining rows and actual task closures. |
| A worker started an issue that was already closed. | Assignment used an old backlog snapshot. | Refresh task state, comments, claims, and linked work at assignment time. Evidence to watch: No duplicate implementation. |
| A worker finished and nobody read its result. | Completed child results are not always delivered automatically; the coordinator kept working instead of yielding and reading the roster. | Read the live roster on a recorded cadence and at each checkpoint, recover undelivered results explicitly, and treat an assigned child that is neither running nor reported as an outstanding result to resolve rather than as still running. Watch for completed results left unread. |
| Hung external workers and a timed-out search were read as results. | A hung child emits nothing and exits into an empty file, and a size-bounded search returns empty on timeout — indistinguishable from a true no-match unless the wording is read. | Give every external agent a wall-clock timeout and a non-empty-output assertion; on a timed-out search, narrow the scope and re-run rather than concluding absence. Watch for zero-byte outputs and timeouts presented as findings. |
| Cancelled workers had already pushed their effects. | Cancelling stops the process but does not roll back committed side effects, so "cancelled" was assumed to mean "did nothing". | Treat cancellation as non-idempotent: re-read the target's real state before re-dispatching, and make delegated actions checksum-guarded so a re-run is safe. Watch for duplicate or racing work after a cancel. |

---

## Turn experience into an improvement

After a costly failure, identify the first missing fact that would have prevented the wasted work. Put that fact in the assignment, log, check, or handoff closest to the decision. Measure whether the change reduced rework or wait on the next items.

Write a narrow rule supported by the failure. Do not convert a temporary environment fault into a permanent product workaround, an example pool size into a universal limit, or a single campaign into a claimed speedup. Keep the entrypoint short; add details here only when they change future decisions. Periodically remove rules that are obsolete or already enforced by tooling.

Each table row is one lesson: the observation, its cause, and the correction. The evidence that the rule helped belongs in the correction when it changes a future decision — as a measured outcome or a failure to watch for — rather than in a separate cell. A lesson whose evidence cannot be stated is not yet supported; do not add it.

---

Related: [lessons: workers and resources](lessons-workers-and-resources.md) · [lessons: delivery](lessons-delivery.md) · [planning and capacity](planning-and-capacity.md)
