---
name: deslop-recipes
description: Pick the shape of a deslop pass before reading anything else. A file, directory, module or repository gets a coverage pass by default; a scoped pass is only for a diff or PR, or an explicit quick look.
---

# Recipes

Pick the shape from the ask, then read only what that shape needs. A target that is not a diff or PR gets a
**coverage pass**. The other rows are for narrower asks, or for work that is not a pass at all.

| The ask sounds like | Shape | What to read, in order | What you owe the end |
|---|---|---|---|
| "deslop this directory", "review this module", "we keep missing things", or any file, package, subsystem or repository that is not a diff | **coverage pass** (the default) | `readings/auditing.md`, `readings/when-to-relax.md`, then **every group** in `lenses.json`: its index, then every principle file in it, in full (see *The default*) → `stages/aggregation.md` → `stages/consolidation.md` → `stages/reporting.md` | the bucketed list and the **coverage receipt**: each group read or not read, with a files-read manifest per cell. A pass that did not read every group is **partial coverage** |
| "review this PR", "is this diff sloppy?", or an explicit "quick look" / "narrow look" | **scoped pass** | `readings/auditing.md`, `readings/when-to-relax.md`, `patterns.md` and the pattern files of those groups, then the **one or two groups** the code is (a boundary question → `boundaries`; a parser → `parsing`), in full | a short findings list, verified at the line, and the groups it did not read |
| "look at X specifically" — separation of concerns, coupling, duplication | **directed cell** | that group's index, then every file in the group, then the module whole | findings in that group's terms, with the declinations |
| "massive simplification", "30% LOC", "get it all done" | **campaign** | `modes/campaign.md` (which names `library/measuring.md` before you start) | a PR or PR set with a measured before/after |
| "this rule is wrong / we need a principle for X" | **library extension** | `library/extending-the-library.md`, then `readings/detecting-slop.md` for the control | a new principle that fires, merged upstream |
| "we keep finding new slop in the same code" | **second round** | `stages/planning.md` §8 — the next round is the complement of the last | the unread groups, named |

## The default: a coverage pass

A plain "deslop this" is a coverage pass. A scoped reading chooses for itself which principle files to open. In the
recorded control (`library/evaluation.md`, 2026-10-21), one monolithic reading touched 9 principles; eight group
readings touched 25, and 17 of those were never touched by the monolith. Giving every group its reading removes that
choice.

- **Every group.** One reading per group in `lenses.json` — all nine today. A reading covers one group. No group is
  merged into another or dropped to save budget.
- **The reading list, in order.** Each reading opens its group's category index first (the `indexes` the group
  names in `lenses.json`), then `readings/auditing.md`, `readings/when-to-relax.md`, then any protocol the group
  names (the duplication group also opens `readings/duplication.md`), then **every principle file in the group, in
  full**, then `patterns.md` and the group's pattern files (the `patterns` list in `lenses.json`; a group with none skips the index).
- **The mechanism.** If the harness can spawn subagents, dispatch one per group in parallel: read-only, whole files,
  the cell prompt passed verbatim. If it cannot, run the same cells one after another in this context, each with
  its own reading list and its own manifest. The execution changes; the cells do not.
- **Large targets are sliced, not thinned.** When one reading cannot hold the whole target, cut the target into
  slices — by module, or by a cross-folder concept cluster with `--file-list` — as `stages/planning.md` §3
  describes. Every group still runs at least once over the whole target. The budget buys slices; it never buys a
  missing group.
- **Not the scripted plan's selection.** `scripts/swarm_plan.py` selects cells under a budget, and it always orients
  only five of the nine groups, so it can leave a group unread. A coverage pass emits every group with
  `scripts/swarm_lenses.py --emit`.
- **The receipt.** Each cell writes `files-read-<cell>.txt`, the manifest that aggregation checks against the
  assignment. The report carries the per-group receipt that `stages/reporting.md` defines.

## Mechanism

The decomposition is fixed; the execution is not (§7 of `stages/planning.md`). Parallel subagents, a harness
fan-out, or one cell at a time in this context all satisfy the protocol. Model tiers are a choice inside the
mechanism, never a way to skip a file: the manifest shows what each cell opened. What must hold in every case:
**one cell per reading, whole files, read-only, the prompt passed through verbatim, and never two groups merged to
save an agent.**

```bash
python3 scripts/swarm_lenses.py --check                                              # the partition is exact
python3 scripts/swarm_lenses.py --emit /tmp/cells --repo <root> --target <dir>       # one prompt per group, all nine
python3 scripts/swarm_lenses.py --emit /tmp/cells --repo <root> --target <module> --label <module>   # one slice, all nine
python3 scripts/swarm_merge.py /tmp/cells/findings-*.jsonl --assignments /tmp/cells --out /tmp/cells/merged.md
```

## The one-line rule

**Scope bounds the code you read, not the principles you apply.** The cheapest way to make a pass miss a real
defect is to let it decide for itself which principle files to open — measured, that is how Separation of Concerns
is never read at all. Index-only reconnaissance is allowed; it is a named mode, not the default.
