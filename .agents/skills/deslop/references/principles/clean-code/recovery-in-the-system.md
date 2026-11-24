---
name: deslop-clean-code-recovery-in-the-system
description: Deslop principle — Recovery in the System: a Retry button the system could replace; classify the case, and keep a control only where a person decides or must act.
---

# Recovery Belongs in the System, Not in a Button

> "Let some other process do the error recovery."
> — Joe Armstrong, *Making Reliable Distributed Systems in the Presence of Software Errors*, 2003

A report page generates a table with a slow job. Sometimes the job fails, so the page gets a **Retry** button. Then a retry runs while the first is still going, so the button learns to disable itself. Then a retry re-pays for a table that was fine, so the server learns to check a cache, and the cache key and the screen disagree about what "current" means. Each step is small and justified by a bug. Nobody decided that a person should be the retry loop.

A manual fallback control (Retry, Refresh, Draft again, Sync now, Re-run, Regenerate) added for a failure or a staleness the system could resolve itself is [patchwork](patchwork.md) at the interface layer. It ships a path the design never meant to have, and every incident adds a state to it.

## The test: name the human decision

For each such control, finish this sentence: "The person presses this to decide ___." If you can fill the blank, the control is a decision and stays. If you cannot, it compensates for missing recovery: delete it and build the recovery in its place.

## Classify at one owner

Put the classification in one place (the run, the job, the state machine), not in each screen. Four cases, and none of them is a Retry button.

| Case | Examples | What the system does |
|------|----------|----------------------|
| **Transient** | rate limit, outage, deploy or restart, timeout, lock | Bounded automatic recovery with a visible waiting state ("retrying at 14:05"). Never a button. After the bound, move to the next row. |
| **Needs a person** | missing input, refused content, a permission | Name the cause in plain words and offer the one action that fixes it. The control is labelled by that action ("Add the missing file"), not by "Retry". |
| **A decision** | regenerate signed or approved work, spend money, discard someone's edit | A decision control, labelled as the decision ("Replace the signed table"), with its cost shown. Never styled as a fallback. |
| **Unexpected** | an unclassified exception, a bug in our own code | Stop safely (no half-written result; the last good state stays), fail loud (full diagnostics with a correlation id, an alert to the owners), tell the person plainly that the fault is ours and their work is safe, and re-queue the stopped work by itself once a build with the fix is live. Then classify the error into one of the rows above, so it does not stay unknown: a rising count here means the classification is missing a row. A Retry button on a bug repeats the bug and its cost. |

## A control must not reach what the automatic path rules out

A "just in case" control often becomes a **second definition of the state**. If the system re-drafts work when its inputs change, then "current" already means "inputs unchanged". A manual re-draft that works on current items either redoes finished work or needs its own idea of current. The second idea drifts, and the user sees the two disagree.

```python
# ❌ A retry endpoint with its own idea of "current". The screen calls the table current;
#    this path adds the prompt version to the key, so a prompt change re-pays and replaces it.
def retry_table(table_id: str) -> Table:
    table = load(table_id)
    key = (table.inputs_hash, PROMPT_VERSION)           # a second definition of "current"
    if cache.get(key) is None:
        table = draft(table_id)                         # runs again, replaces what the expert sees
    return table

# ✅ One definition of current; the run recovers from transient errors itself.
def is_current(table: Table) -> bool:
    return table.drafted_from == table.inputs_hash      # the only owner of the question

def run_draft(table_id: str) -> None:
    table = load(table_id)
    if is_current(table):
        return
    try:
        save(draft(table))
    except TransientError as err:                       # rate limit, outage, restart, timeout
        attempts = record_attempt(table_id)             # persisted, so a restart keeps the count
        if attempts < MAX_ATTEMPTS:
            defer(table_id, retry_at=backoff(attempts), reason=str(err))     # shows "retrying at ..."
        else:
            block(table_id, cause="still unavailable after several tries", action=None)  # the next row
    except NeedsPerson as err:                          # missing input, refused content
        block(table_id, cause=err.plain_words, action=err.fix)               # one named action
    except Exception:                                   # unexpected: a bug or an unclassified error
        stop_and_report(table_id)                       # keeps the last good table, alerts, re-queues after the fix
        raise
```

On the screen the same split holds. The ❌ shows a "Draft again" button next to every table, always enabled. The ✅ shows nothing on a current table, "retrying at 14:05" on a deferred one, the cause with its one fix on a blocked one, "our error, reported (ref …); your table is unchanged" on a stopped one, and "Replace the signed table" only where a person decides.

## Worked example (anonymized)

In a regulatory-authoring product, generated comparison tables already re-drafted themselves when their inputs changed. A "Draft again" path still existed as a fallback. Its server side grew its own idea of "current": a cache key that included the prompt version. After a prompt change, a table the screen called current was paid for again and replaced under the expert who was reading it.

The repair was not a better guard on the button:

1. One definition of "current", read by the screen, the run and the retry path alike.
2. Automatic recovery for transient run failures, with a visible waiting state.
3. The button stays only where a person decides (a signed table) or must act (the cause is named).

## When not to apply

- **A deliberate refresh of external data the system cannot watch**: pull-to-refresh of a remote feed has a real decision behind it ("check now").
- **An expert's explicit regenerate of approved content**: that is the decision row above, labelled as such.
- **Offline-first apps where the person controls sync**: here the person owning sync is the design.

What keeps a control on this list is a person's authority to decide, not the system's inability to see: an offline app sees its pending changes and still lets the person choose when to sync. A control whose only reason is "the system did not recover" is not on this list.

## Finding and fixing it

1. List the controls whose label is a verb of repetition: Retry, Refresh, Again, Sync, Re-run, Regenerate.
2. For each, write the human decision. If the blank stays empty, mark it as compensation.
3. Find the server path behind it. If it holds its own cache key, freshness test or "already done" check, it is a second definition of the state: route it through the one owner.
4. Classify the failures it covers (transient, needs a person, decision) and build the matching recovery.
5. Delete the control, or relabel it as the decision or the one action.

In relation to other principles, this file:

| Principle | Relationship |
|-----------|--------------|
| [**Patchwork**](patchwork.md) | The parent diagnosis. Patchwork names compensating code in general; this is the form where the compensation is a control handed to a person. |
| [**Resilience & Graceful Degradation**](../reliability/resilience.md) | Owns the automatic recovery (bounded retries, backoff, breakers). A fallback *value* for degraded data is fine; a fallback *control* that asks a person to run the recovery is this principle. |
| [**A Special Case Is a Requirement the Design Never Accounted For**](special-cases.md) | A retry button is a special case: a path for one situation that the state model never named. |
| [**Single Source of Truth**](../architecture/single-source-of-truth.md) | "Current" must have one owner; a retry path with its own key is a second one. |
| [**Implicit State Machine**](../architecture/implicit-state-machine.md) | Transient, blocked and current are states; write them down instead of letting buttons imply them. |
| [**Idempotency**](../architecture/idempotency.md) | Automatic retry is safe only if the operation is idempotent; a manual retry that is not is a double charge waiting. |

## Summary

1. **Recovery is the system's job.** A control that asks a person to run the system's recovery is patchwork at the interface.
2. **Name the human decision.** No decision to name means delete the control and build the recovery.
3. **Classify at one owner:** transient gets bounded automatic recovery and a visible waiting state; needs-a-person gets the cause and the one fixing action; a decision gets a decision control.
4. **A control must not reach a state the automatic path rules out.** Otherwise it becomes a second definition of that state.
5. **Keep the control where a person really decides:** external data the system cannot watch, an expert's regenerate of approved work, a person-owned sync.
