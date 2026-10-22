---
name: deslop-recipes
description: Five asks, five invocations — pick the shape of the pass before reading anything else.
---

# Recipes

Most passes are one of five shapes. Pick the shape from the ask, then read only what that shape needs. If the ask
fits none of them, it is a campaign or an extension — the last two rows.

| The ask sounds like | Shape | What to read, in order | What you owe the end |
|---|---|---|---|
| "is this PR/diff/file sloppy?", "review this" | **scoped pass** | `readings/auditing.md`, `readings/when-to-relax.md`, then the **one or two groups** the code is (a boundary question → `boundaries`; a parser → `parsing`), in full | a short findings list, verified at the line |
| "look at X specifically" — separation of concerns, coupling, duplication | **directed cell** | that group's index, then every file in the group, then the module whole | findings in that group's terms, with the declinations |
| "run a deslop pass over this directory", "we keep missing things" | **coverage pass** | `stages/planning.md` → plan cells and budget → one reading per cell (see *Mechanism*) → `stages/aggregation.md` → `stages/consolidation.md` → `stages/reporting.md` | the bucketed list, the rotation state, and what was left out |
| "massive simplification", "30% LOC", "get it all done" | **campaign** | `modes/campaign.md` (which names `library/measuring.md` before you start) | a PR or PR set with a measured before/after |
| "this rule is wrong / we need a principle for X" | **library extension** | `library/extending-the-library.md`, then `readings/detecting-slop.md` for the control | a new principle that fires, merged upstream |
| "we keep finding new slop in the same code" | **second round** | `stages/planning.md` §rounds — the next round is the complement of the last | the unread groups, named |

## Mechanism

The decomposition is fixed; the execution is not (§7 of `stages/planning.md`). You may run the cells as parallel
subagents, as a harness fan-out, as model tiers (a strong model for judgement-heavy groups, a cheap one for
mechanical sweeps), or one at a time in this context. What must hold in every case: **one cell per reading, whole
files, read-only, the prompt passed through verbatim, and never two groups merged to save an agent.**

```bash
# plan a coverage pass, then dispatch one cell per reading
python3 scripts/swarm_plan.py --repo <root> --target <dir> --out /tmp/plan --budget 24 \
    [--ledger .deslop-rounds.jsonl --round 2]
python3 scripts/swarm_lenses.py --emit /tmp/cells --target <slice> --only <group>
python3 scripts/swarm_merge.py /tmp/cells/findings-*.jsonl --assignments /tmp/cells --out /tmp/cells/merged.md
```

## The one-line rule

**Scope bounds the code you read, not the principles you apply.** The cheapest way to make a pass miss a real
defect is to let it decide for itself which principle files to open — measured, that is how Separation of Concerns
is never read at all. Index-only reconnaissance is allowed; it is a named mode, not the default.
