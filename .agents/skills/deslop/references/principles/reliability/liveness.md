---
name: deslop-reliability-liveness
description: Deslop principle — Liveness: every state leaves by itself or names who it waits for; an unowned state gets an owner by accident.
---

# Liveness: Every State Has an Owner That Moves It Forward

**Why this is slop:** a system that forbids the wrong states and never guarantees the right move forward stalls politely — every safety rule holds and the work still never finishes.

> Safety: nothing bad happens. Liveness: something good eventually happens.
> — the distinction, paraphrased, from Leslie Lamport, *Proving the Correctness of Multiprocess Programs* (1977), formalised by Alpern and Schneider, *Defining Liveness* (1985)

## Core Concept

Most reliability rules are **safety** rules: an illegal state cannot be stored, a write is checked, an error stops early. They say what must never happen. **Liveness** says what must eventually happen: every non-final state is eventually left, under stated assumptions (the service comes back, the person acts). A system can be perfectly safe and still stuck: nothing wrong is ever written, and nothing finishes. For the states the system owns, add an operational bound on top (attempts, a deadline, then escalation); for states that wait on a person, name the person, so the wait is visible rather than bounded.

The test is one question per state: **what moves it forward, and when?** Keep two words apart. The **owner** is the one place that holds the transition's policy (its guards, what "current" means, what happens on failure). A **trigger** is anything that asks the owner to run: a timer, an event, a person's control. Many triggers are fine; two owners are not. Valid owners are few:

| The owner | When | Example |
|---|---|---|
| **The system itself** | on a timer, an event, or a bounded retry | a run deferred by a rate limit resumes at 14:05 |
| **A named person, with the one action that unblocks it** | when they act; the state says who and what | "upload the missing test report" |
| **A named decision** | when a person decides; the control is labelled as the decision | "replace the signed table" |
| **The fix pipeline** (for an unexpected error) | when a build with the fix is live; the work is re-queued by itself | "our error, reported (ref …); your work is safe" |

Any other answer, a blank, or "whoever notices", is a **liveness gap**. A gap never stays empty: something fills it by accident.

## How an unowned state gets an owner by accident

- **A generic control for the user.** Retry, Refresh, Reload, Draft again, Sync now: the person becomes the scheduler. Each later incident adds a state to the control: it learns to disable itself during a run, it grows its own idea of "current", it can be pressed on finished work. This is [patchwork](../clean-code/patchwork.md) at the interface.
- **A runbook or a script for an operator.** "If runs stick in *queued*, re-run `requeue.sh`." The owner is whoever reads the runbook in time.
- **A guard in the next layer.** The consumer re-checks and repairs what the producer left half done ([A Special Case Is a Requirement](../clean-code/special-cases.md)).
- **A sweep that ends it the wrong way.** A cleanup job marks stuck work *failed* instead of resuming it: the state is left, but by the wrong exit.
- **Nothing.** The work waits until a person happens to look, often the user who already left.

## The cases are classified at one owner

Whether a failure is transient, needs a person, is a decision, or is unexpected is decided once, where the work runs (the job, the run lifecycle, the state machine), never per screen or per caller. Screens only render the state the owner set. A screen that decides recovery is a second owner, and two owners disagree.

```python
# ❌ The run ends "failed" for every cause; recovery is whoever presses Retry.
def run_job(job_id: str) -> None:
    try:
        do_work(load(job_id))
    except Exception as err:
        mark(job_id, "failed", str(err))          # stuck: the screen shows a Retry button

# ✅ Every exit names its owner; nothing waits for "whoever notices".
def run_job(job_id: str) -> None:
    try:                                          # one boundary, loading included
        job = load(job_id)
        if job.done:
            return
        do_work(job)
    except TransientError as err:                 # owner: the system, bounded
        attempts = record_attempt(job_id)         # persisted, so a restart keeps the count
        if attempts < MAX_ATTEMPTS:
            defer(job_id, retry_at=backoff(attempts), reason=str(err))
        else:
            escalate(job_id, cause=str(err))      # owner: the team; the screen says "unavailable"
    except NeedsPerson as err:                    # owner: a named person and action
        block(job_id, who=err.who, cause=err.plain_words, action=err.fix)
    except DecisionRequired as err:               # owner: a named decision
        await_decision(job_id, question=err.question, options=err.options)
    except Exception:                             # owner: the fix pipeline
        stop_and_report(job_id)                   # keeps the last good state, alerts, re-queues after the fix
        raise
```

## A control must not reach what the automatic path rules out

When the system already moves a state forward, a manual control for the same move is safe only as a **trigger** of the owner's transition. It becomes a **second owner** the moment it carries its own policy: its own freshness test, cache key or guard. That copy drifts. In one case a "draft again" path judged a table by a cache key the automatic path did not use; after a prompt change, a table the screen called current was paid for again and replaced. Route the control through the one owner: that fixes the liveness defect. A second, separate rule then decides whether the control stays at all, and it is deliberate: **a control needs a decision behind it**. A trigger with a real decision ("check now" on data the system cannot watch, an expert's regenerate, a person-owned sync) stays, labelled as that decision. A trigger with none ("Retry now" on a wait the system already owns) is not a correctness bug, but it is removed anyway: it adds a path no one needs, and the next fix to it is how a second owner grows back.

## When a control is right

A person's **authority to decide** keeps a control, not the system's inability to observe. Pull-to-refresh of a remote feed the system cannot watch is a decision ("check now"). An expert regenerating approved work is a decision. An offline app sees its pending changes and still lets the person choose when to sync. Keep these, labelled as the decision.

## Finding and fixing it

1. **List the states** of a flow (from the status column, the run table, or the screens), not only the happy ones: queued, running, deferred, blocked, failed, stale.
2. **Write the owner and the triggers next to each.** A finding is a state with no owner (a blank, "whoever notices", "a sweep fails it"), or a state whose only way forward is a person or an operator although the system could own it (the Retry button, the runbook). A person's control that triggers the owner's transition for a real decision, an unwatchable refresh or a person-owned sync is not a finding.
3. **Find the second owners:** controls, scripts and guards that carry their own transition policy (their own freshness test, cache key or guard) for a state the system already moves. Make them triggers of the one owner, or delete them.
4. **Bound every automatic owner** (attempts, time) and say where it escalates when the bound runs out.
5. **Make every wait visible:** the state names its owner and its next time ("retrying at 14:05", "waiting for Ana to upload the report").

In relation to other principles:

| Principle | Relationship |
|-----------|--------------|
| [**Illegal States Unrepresentable**](../architecture/illegal-states-unrepresentable.md) | The safety half: what a state may never be. Liveness is the other half: no legal state may be a dead end. |
| [**A State Machine Nobody Wrote Down**](../architecture/implicit-state-machine.md) | Write the transitions down; liveness adds an owner and a trigger to each. |
| [**Resilience & Graceful Degradation**](resilience.md) | The mechanics of the system-owned case: bounded retry, backoff, breakers. A fallback *value* is resilience; a fallback *control* that hands the move to a person is a liveness gap. |
| [**Patchwork**](../clean-code/patchwork.md) | What an unowned state turns into over time, one justified fix at a time. |
| [**Idempotency**](../architecture/idempotency.md) | An automatic owner retries; only idempotent moves are safe to retry. |
| [**Observability & Transparency**](observability.md) | A wait the logs and the screen cannot explain is unowned in practice. |

## Summary

1. **Safety says nothing bad happens; liveness says something good eventually happens.** Check both.
2. **Every state names its owner and its triggers:** the system (bounded in operation), a named person and action, a named decision, or the fix pipeline. Many triggers are fine; one owner.
3. **An unowned state gets an owner by accident:** a Retry button, a runbook, a repairing guard, a sweep that fails it, or nothing.
4. **Classify at the one place the work runs;** screens render the state, never decide recovery.
5. **One owner per transition; then a decision behind every control.** A control that carries its own policy is a second owner (a defect). A control that only triggers the owner is safe, and it stays when a person has a real decision to make; without one it is clutter, removed by design choice, not as a defect.
