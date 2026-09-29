---
name: deslop-architecture-one-logical-unit-one-home
description: Deslop principle — One Logical Unit, One Home: parts of one unit spread across packages, or one shape re-implemented per feature, is a finding — consolidate to one module per responsibility.
---

# One Logical Unit, One Home

> "You found things that are one logical unit spread across multiple packages — your next immediate
> thought should have been: hey, this is slop."
> — the review that motivated this principle

A logical unit is one thing the system does: resolve a job's lifecycle, record an activity event, hold a
lock, run a step. When its parts are scattered — the lease in one package, the heartbeat in a second, the
stop-request in a third, the schema in all four — the code has nowhere that unit can be read. Every piece
works. Each was written beside the feature that needed it first. Nothing is duplicated line-for-line,
nothing is dead, and no tool reports it.

The same disease has a second face: **one shape re-implemented per feature**. Three step runners, each with
its own `jobs.py`. Five lock implementations. Six activity sinks. Every one an instance of the same shape,
none aware of the others. Individually defensible; jointly, a design nobody chose.

The obligation this principle names is immediate, and it is the point of the file: **the moment you notice
a unit spread across boundaries, that *is* the finding.** Name the unit, name the module that should own it,
propose the consolidation — in the pass, as an actionable item. Reporting the observation ("this looks
similar to X") and moving on is the failure: the next reader must re-notice it, re-scope it, and re-decide
it, for free, on your behalf.

## Why it happens

1. A general implementation already exists — a run-control service, a lock repository, an activity table.
2. A new feature needs *most* of it, but not all, and its author is working in another package with its own
   conventions and its own reviewers.
3. Copying is local, reviewable, and safe today. Importing the general one means editing it and its owners.
   The copy wins.
4. The copy diverges: fields tuned to the special case, capabilities added that only the special case
   wanted. Now there are two, and neither is the general one.

No bad commit is made at any step. Every step is a local optimum.

## The tells

Cheap views first — these are the checks that automated analysis cannot perform for you:

1. **The same file name in three or more packages** (`jobs.py`, `activity.py`, `runtime.py`, `config.py`):
   one design copied per package.
   ```bash
   find <src> -name '*.py' -not -path '*/tests/*' | sed 's#.*/##' | sort | uniq -c | sort -rn | awk '$1>=3'
   ```
2. **Two files whose def and class lists line up.** The strongest single signal — different folders, same
   design. Names that align across two files that are not each other's twin mean one of them is a fork.
   ```bash
   grep -hE '^(async )?def |^class ' a.py b.py | sort | uniq -c | sort -rn | head -30
   ```
3. **A facade with no boundary** — the module whose job is to re-export its own siblings, so a reader opens
   three files to see one unit. A third layer where two would do.
4. **The specialist beside the general** — two modules doing one job, where the specialist carries capability
   its own goal never names (a citation pipeline inside a runtime, voting rounds inside a job runner).
5. **N partial implementations of one mechanism.** Count them: locking, activity, streams, configuration,
   telemetry. One is a question; more than two is a finding.
6. **The reader's tell**, the weakest and most reliable: you opened three files to answer one question about
   one behaviour.

## Diagnostics

1. **Name the unit in one sentence** — "this is the job lifecycle of a step run." If you cannot, you have
   found a folder, not a unit. Stop.
2. **List the pieces and their packages.** Any piece whose only reason for living outside the unit is *where
   it was first needed* is a consolidation candidate.
3. **Count the lines that exist only because the unit is split**: the facade's re-exports, an import-cycle
   detour, a schema/envelope/status helper duplicated per copy, the adapter translating one copy's shape
   into the other's.
4. **Name the capability the goal does not require.** For each special feature in the fork, ask which stated
   goal needs it. If none does, deleting it is not a judgement call — it is the
   [YAGNI](../clean-code/yagni.md) answer.
5. **Count the survivors.** What would remain if the unit had one home? The remainder is the real payload.

## The repair

One module per logical separation of responsibility, and each feature reduced to the variation it genuinely
has.

- **Consolidate into one module**, keeping each feature's genuine hooks — its prompt, its domain fields, its
  policy — as parameters or subclasses, never as a parallel copy.
- **Delete the specialist's unneeded capability in the same change.** A fork's extra features are not
  inherited by the consolidated module; each must re-justify itself.
- **Drop the facade** unless it is a real seam (a published import path, a cycle break). Re-exporting your
  own submodules is not a boundary.
- **Sequence the PRs by concern** so each is independently green and revertable: the shared owner first
  (activity and events), then configuration and constants, then the runtime and wiring. One 5,000-line
  consolidation cannot be reviewed; five that stand alone can.
- **Prove parity on behaviour, not on the diff.** Regenerate the real artifacts and compare them, then delete
  the states the new shape cannot produce — the same discipline as
  [patchwork](../clean-code/patchwork.md).
- **Do not merge deliberate symmetry.** Parallel domain packages built to a common scaffold, framework DI
  idioms and per-model configuration lines all look like this and are not — they are meant to evolve
  independently. See the false-positive list in [hunting duplication](../duplication.md).

## The shape, before and after

```python
# ❌ One unit, four homes: the lease in the runner, the heartbeat in the progress module,
#    the stop-request in the status API, the schema in three packages. Every piece is correct.
#    No file shows the lifecycle, and each new runner copies all four again.
runner.py     lease(...)          heartbeat(...)
progress.py   mark_running(...)   sweep_stale(...)
status.py     request_stop(...)   clear_stop(...)
schema.py     jobs_ddl()          activity_ddl()
```

```python
# ✅ One owner, and each feature supplies only its variation.
run_control.py     claim(...)  heartbeat(...)  request_stop(...)  sweep_stale(...)  finalize(...)
features/step.py   CONTROL = RunControl(policy=StepPolicy(...), telemetry=StepTelemetry(...))
```

The second version is not smaller by coincidence: the duplicated lease/heartbeat/expiry logic, the
status-message plumbing, the per-feature schema helpers and the translator between the two copies all leave
with it.

In relation to other principles, one logical unit, one home is the audit's side of a rule its neighbours
state as a design aim:

| Principle | Relationship |
|-----------|--------------|
| [**Separation of Concerns**](separation-of-concerns.md) | States the aim — one concern per part. This is the tell that the aim was missed, and what the audit owes when it sees it. |
| [**Modularity**](modularity.md) | A deep module hides one decision. A unit split across packages hides its decision in four places and is shallow in each. |
| [**DRY**](dry.md) | DRY fixes the same knowledge written twice. This fixes ONE unit never given a place — its pieces are different lines, so no clone tool sees it. |
| [**Single Source of Truth**](single-source-of-truth.md) | SSoT asks "which copy is correct?" of a datum. This asks the same question of behaviour and shape. |
| [**YAGNI**](../clean-code/yagni.md) | Supplies the permission to delete the specialist's capability: no stated goal requires it. |
| [**Code Reusability**](code-reusability.md) | Says do not generalise before real callers exist. Here the callers already exist — as copies — which is exactly when to generalise. |
| [**Hunting Duplication**](../duplication.md) | The sweep that usually finds this; this file is the finding type and its repair. |
| [**Patchwork**](../clean-code/patchwork.md) | Patchwork is one file that cannot be simplified by deleting. This is several files that should not exist separately. |

## Summary

1. **A unit's parts spread across packages, or one shape re-implemented per feature, is a finding — not an
   observation.** Name it in the pass, with the owning module proposed.
2. **No tool reports it.** Cyclomatic complexity counts decisions inside a function; clone scanners compare
   text. A design copied with different names and control flow is invisible to both.
3. **The tells are cheap**: the same file name in three or more packages, two files whose def lists line up,
   a facade with no boundary, N copies of one mechanism.
4. **The repair is one module per responsibility**, with each feature reduced to its genuine hooks — in the
   same change that deletes the specialist capability nobody needs.
5. **Sequence the consolidation by concern** so every PR stands alone, and prove parity on behaviour rather
   than on the diff.
