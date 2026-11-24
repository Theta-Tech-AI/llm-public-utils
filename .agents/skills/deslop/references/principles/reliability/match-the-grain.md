---
name: deslop-reliability-match-the-grain
description: Deslop principle — Match the Grain: every mechanism around work acts per unit of work; one unit's failure, edit or event never spreads to its siblings.
---

# Match the Grain

**Why this is slop:** When a mechanism acts on a bigger piece than the work, one unit's event becomes every unit's event: one bad answer loses the whole run, one edit re-checks every section, one lock makes everything stale.

> "Use bulkhead architectures to limit scope of impact."
> — AWS Well-Architected Framework, Reliability Pillar

Most jobs are a set of independent units: the questions of a form, the documents of a batch, the rows of a table, the sections of a report, the steps of a simulation. A unit is independent when its result does not depend on the results of its siblings. Several mechanisms surround every unit of work, and each one has a *grain*: the size of the piece it acts on.

| Mechanism | At the grain of the job (slop) | At the grain of the unit |
|---|---|---|
| Failure | one unit's error fails the job | that unit ends `unavailable` with its reason; the others finish |
| Retry | the whole job runs again | the failed unit runs again, a bounded number of times, with a short backoff |
| Saving | results are written once, at the end | each unit's result is written when it finishes; a resume skips finished units |
| Status | one status for the job | one outcome per unit; the job's status is derived from them by one rule |
| Caching | one entry for the batch | one entry per unit, keyed on what that unit read |
| Staleness | one event or time anywhere marks every unit stale | a unit is stale only when its own inputs changed ([Freshness From Inputs](../architecture/freshness-from-inputs.md)) |
| Concurrency | independent units in one serial loop | a bounded parallel map |

Nobody chooses the coarse grain. A loop gives it by default: `for unit in units:` inside one `try`, then one `save()`. Every mechanism then inherits the loop's grain, and the cost of one failure grows with the size of the job.

## One mechanism, not one fix per job

Put the grain in the runner, once: a map over units that, for each unit, retries, records the outcome, saves the result and skips work already done. Every job gets the grain by using the map. The other way is patchwork. Each job adds its own `try`/`except` around the cause that failed last time (a refused value, a timeout), and the next new cause fails the whole job again. The specific cause still needs a fix, as an ordinary bug. That fix does not limit the damage; the grain does.

A retry fixes a transient failure: a timeout, a rate limit, a malformed model answer. A deterministic failure, such as a value the validator always refuses, fails again on every retry. Isolation keeps it to its one unit.

## Example

A job asks a model to suggest an answer for each question of a form, then saves the suggestions.

```python
# ❌ The job's grain: one refused value loses every suggestion, after all of them were paid for
def suggest_all(form, model):
    suggestions = {}
    for question in form.questions:
        suggestions[question.id] = model.suggest(question)
    store.save_all(form.id, suggestions)   # validates every value; one refusal raises and nothing is kept

# ✅ The unit's grain: one generic runner owns retry, outcome, saving and resume
def suggest_one(question, model):
    return Suggestion.parse(question, model.suggest(question))   # refused here, for this question only

outcomes = run_units(form.questions, suggest_one, key=lambda q: q.id,
                     retries=2, backoff_s=2.0, save=store.save_one, skip_done=True)
# {question_id: Done(suggestion) | Unavailable(reason)}; the job's status is derived from these
```

## How to find it

1. **Name the unit of work** of every job: the smallest piece whose result does not depend on its siblings.
2. **Find the grain of each mechanism in the table.** Read the loop, the `try`, the save, the status field, the cache key and the staleness test.
3. **A mechanism coarser than the unit is a finding.** Tells: a loop over independent items inside one `try`, or followed by one save; a job status with no outcome per item; "run the job again" as the only recovery; one cache entry or key over a batch; a project-wide time or event that decides each item's staleness; a serial loop of independent remote calls.
4. **Count the damage.** For one real failure, count the units lost against the units that actually failed. "One refused value lost 28 answers and 24 minutes of paid work" is the severity of the finding.

## How to fix it

1. Write the unit function. It takes one unit and returns its result, or raises.
2. Run every unit through one runner that owns the grain: bounded retry with backoff, an outcome per unit (`done`, `unavailable(reason)`), a save per finished unit, skip-done on resume, bounded parallelism.
3. Derive the job's status from the unit outcomes and the job's own steps (a final publish, for example) by one rule that also says which units are required.
4. Show the person the outcome per unit ("no suggestion for this question"), not a failed job.
5. Delete the per-job `try`/`except` blocks and leave-out lists that the runner replaces.

## When a coarser grain is right

- **Atomic work.** Work that must be all or nothing, such as a signature over a set, a transfer or a migration step. The set is then the unit.
- **Dependent units.** A later item reads an earlier item's result. The chain is then the unit.
- **Cost per unit.** When the overhead per unit is larger than the work (one network call per tiny item), batch the calls, but keep the outcome, the save and the cache entry per unit.

---

In relation to other principles, match the grain:

| Principle | Relationship |
|-----------|--------------|
| [**Resilience & Graceful Degradation**](resilience.md) | Resilience owns how to retry, time out and degrade; this decides which unit those wrap |
| [**Liveness**](liveness.md) | A failure at the job's grain leaves every unit without an owner that moves it on |
| [**Freshness From Inputs**](../architecture/freshness-from-inputs.md) | Freshness decides how staleness is tested; this decides the grain of the test |
| [**Idempotency**](../architecture/idempotency.md) | Retry and resume per unit are safe only when each unit is idempotent |
| [**Orthogonality**](../architecture/orthogonality.md) | Independent units that share one fate are welded; the coarse mechanism is the weld |
| [**One fact, many owners**](../../patterns/one-fact-many-owners.md) | A job status beside per-unit errors is its status-and-message variant |

## Summary

1. **Find the unit of work**: the smallest piece whose result does not depend on its siblings.
2. **Every mechanism acts at that grain**: failure, retry, saving, status, caching, staleness and concurrency.
3. **One runner owns the grain.** Do not add a `try`/`except` per job for the last cause that failed.
4. **A retry fixes transient failures; isolation contains deterministic ones.**
5. **Count the damage**: units lost against units that failed.
