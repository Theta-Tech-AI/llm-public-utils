---
name: deslop-campaign-mode
description: Deslop campaign mode — run a whole-codebase simplification program against a measured LOC/legibility target, split across god files and unified helpers, delivered as a PR or PR set without waiting for per-step decisions.
---

# Campaign mode

A normal deslop pass is scoped to a file, a directory, or a diff. **Campaign mode is scoped to the
codebase, runs to completion, and carries a measurable target.** It is what the user means when they
say any of:

- "massive simplification", "simplification across the board", "simplify the whole repo"
- "I want LOC to drop dramatically", "minimum 30%", "cut the bloat"
- "break up the god files", "unify the helpers", "less if-if-if-else routing"
- "raise legibility", "make the codebase easier to understand", "make it elegant"
- "**get it all done**", "**no excuses**", "**don't wait for my decisions**"
- "present me a PR / a set of PRs when you're done"

Any of the last group **is the mode answer** — see [auditing.md](auditing.md#the-autonomy-rule).
Do not open a campaign with a mode question.

## Why campaigns fail

They fail in three predictable ways, and every rule below exists to prevent one of them:

| Failure | What it looks like | Defense |
|---|---|---|
| **Target theatre** | LOC drops 30% because a 900-line file was split into nine 100-line files that together do the same thing, or because lines were moved, not removed | §2 — measure *what kind* of line changed, not just the count |
| **Silent breakage** | A 4,000-line refactor lands green because the tests never covered the cut paths | §4 — every behavior-adjacent cut needs a test that was red before it |
| **Unreviewable delivery** | One 20,000-line PR that no human can read, so it gets rubber-stamped or sits forever | §5 — deliberate split, per-PR proof |

## 1. Baseline before you cut

**Never state a target without a measured baseline.** The full harness — four tools, the unbiased task
corpus, the metrics that actually carry the story, and the reporting skeleton — is in
[**measuring.md**](measuring.md). **Read it before you start; it defines both the baseline you take
now and the numbers you owe at the end.**

The short version:

```bash
# Production LOC per language, excluding vendored/generated/lockfiles — state your exclusions
tokei --exclude vendor --exclude '*.lock' --exclude node_modules .   # or cloc / pygount

# The shape of the problem: the biggest files are the campaign's first targets
find . -name '*.py' -not -path './vendor/*' | xargs wc -l | sort -rn | head -30

# Test count — the invariant you must not reduce
pytest --collect-only -q | tail -1

# Branch density: conditionals per function is a better slop signal than LOC alone
rg -c '\b(if|elif|else if|switch|case)\b' --glob '!vendor/**' .
```

Record: **total LOC, per-file top-N, test count, branch count.** The baseline is what the target is
measured against, and it is what makes the final claim checkable rather than rhetorical.

**Take the baseline on a frozen, named commit.** Every later comparison is against that commit, and a
failure discovered while integrating is checked against it to determine whether it is pre-existing —
the same discipline as *"repro on `origin/main` HEAD in a clean env to see whether the failure is
already there."*

**And measure more than LOC.** In the reference campaign, LOC fell 31–36% while **max nesting depth
fell 90% (99 → 10), the longest `elif` chain fell 90% (92 → 9), and functions over 300 lines fell 99%
(192 → 2)**. Those are what "less if-if-if-else routing" and "elegance" mean when made measurable —
and they are far harder to game than a line count.

## 2. What "30% LOC reduction" actually means

The user's number is a *proxy for complexity removed*. Honor the number, but honor what it is proxying:

- **Counted:** deleted dead code, deleted duplication, deleted indirection (pass-through wrappers,
  one-caller helpers, redundant DTO↔model mappings), collapsed conditional chains, removed
  commented-out blocks, inlined single-use abstractions, merged near-identical functions.
- **NOT counted (say so explicitly if it dominates):** lines moved between files, code split out to
  satisfy a size rule, vendored/generated/lockfile churn, and reformatting. **A split that relocates
  900 lines into nine files with no net deletion is not a simplification** — it may still be worth
  doing, but it does not count toward the number and must not be reported as if it did.
- **Report the split.** "LOC −34%: −21% deletion, −13% consolidation" is a credible claim. A bare
  "−34%" invites the suspicion that the target came first and the measurement justified it.

**If the honest number falls short of the target, report the shortfall with the reason.** A truthful
22% with a named cause is worth more than a 30% that only holds because the measurement was
generous. Say which files resisted and why.

## 3. The five sweeps

Run in this order — each one shrinks the surface the next has to read.

### Sweep 1 — God-file decomposition
Any file past the house threshold (~400 LOC backend, ~250 frontend/TS) or mixing several
responsibilities. **Delegate the mechanics to the [`shatter`](../../shatter/SKILL.md) skill** rather
than improvising a split — it owns the thresholds and the responsibility-boundary analysis. What
campaign mode adds: do the splits **after** the deletion sweeps below, or you will split code you are
about to delete.

### Sweep 2 — Duplication and helper unification
The highest-yield sweep. Two shapes:

- **Token-level duplication** — the same block in N places. Extract once, call N times.
- **Conceptual duplication** — N functions doing the same *job* under different names
  (`format_date` / `to_display_date` / `render_date`), or a helper that reimplements a stdlib/library
  call, or a local utility that shadows a shared one. **Search the whole codebase for each helper's
  job before keeping it** — the point of unification is that the codebase ends with *one* way to do
  each thing.
- **Indirection with one caller** — a wrapper, adapter, or interface with exactly one implementation
  and one call site. Inline it unless it marks a genuine seam (test double, vendor boundary, planned
  second implementation).

See [duplication.md](duplication.md) for the sweep mechanics and
[architecture/dry.md](architecture/dry.md) for where to stop.

### Sweep 3 — Branch-density reduction
"Less if-if-if-if-if-else routing" is a *measurable* goal, not a vibe. Targets:

- **Type/state ladders** (`if kind == 'a' … elif kind == 'b' …` ×7) → a dict/registry dispatch, a
  polymorphic method, or a `match`. Decide the type once at the boundary —
  [decide-dont-cope.md](clean-code/decide-dont-cope.md).
- **Nested pyramids** → guard clauses and early returns — [guard-clauses.md](clean-code/guard-clauses.md).
- **Flag-parameter branching** (`if with_cache: … else: …`) → two functions, or a strategy passed in.
- **Boolean ceremony** (`if cond: return True else: return False` → `return cond`).
- **Dead branches** — conditions that can no longer be false because of an earlier guard.

Re-count branch density at the end. **Fewer branches per function is a better elegance signal than
fewer lines**, and it is the one the user's phrasing is actually asking for.

### Sweep 4 — Bloat and dead weight
YAGNI violations (unused config knobs, speculative extension points, "just in case" parameters),
unused exports and imports, commented-out code, abandoned feature flags, vestigial models, duplicated
docs, and defensive checks on already-validated inputs. Always grep for a symbol before deleting —
tool reports miss dynamic/string/reflection use (see the pitfalls in [SKILL.md](../SKILL.md)).

### Sweep 5 — Legibility and connection
The sweep most often skipped, and the one the user named explicitly ("interpretability of the
codebase and how things connect to each other"). See
[legibility.md](clean-code/legibility.md). In a campaign the typical deliverable is a small number of
**connection artifacts**: a module map, a documented call path for the two or three core flows, and
the removal of the naming lies that make navigation guesswork.

## 4. Verification at campaign scale

Campaign mode changes a great deal at once, so the discipline is stricter, not looser:

- **Tests are the invariant.** The test count from §1 must not fall. Deleting a test is a stop —
  unless the test covered code you deleted, in which case say so in the PR body with the file and the
  reason.
- **Pin behavior-adjacent cuts with a test that was red first.**
  [loop-until-dry.md](loop-until-dry.md) states it for a pass; it applies harder here: *a refactor
  with no failing-test proof is a hope, not a fix.*
- **Verify in slices, not at the end.** Run the suite after each sweep and each split. A campaign that
  discovers a breakage 15,000 lines in cannot attribute it.
- **Respect [when-to-relax.md](when-to-relax.md).** Tests, DTOs, generated code, hot paths, security
  boundaries, and legitimate compat seams are not slop. Cutting them is churn, and it *inflates* the
  LOC number while making the codebase worse — the exact failure the target invites.
- **A second model's independent pass** before delivery, per [loop-until-dry.md](loop-until-dry.md).

## 5. Running it at scale

A campaign is large enough that the *process* is the deliverable. From the reference campaign
(19 active hours, 1,652 subagent tasks, 111,352 tool calls, +432,726 / −782,630 lines):

- **The orchestrator does not edit source.** It measures the codebase, splits it into
  **non-overlapping groups** (36 in the reference run), writes the assignments, reads the reports,
  integrates the branches, and runs the checks. Coordination and editing in the same agent is where
  campaigns fall apart.
- **One working copy per worker — a `git worktree`, not a shared checkout.** Workers that write the
  same tree clobber each other; disjoint files are not enough, because the *tree* is shared state.
- **Disjoint by file, and sequenced by file.** Two workers touching one file must be one worker or one
  prompt — parallel agents on a shared file collide and clobber each other, and file-level disjointness
  is the only thing that makes a parallel wave safe.
- **Briefs state three things:** the code to simplify, the **interfaces to preserve**, and the checks
  required before committing. A brief missing the second one produces regressions that look like
  progress.
- **Workers commit after each verified step.** This is not tidiness — it is what makes the run
  recoverable. The reference run **died mid-flight when the provider's auth token expired**, and the
  workers' commits and briefs were the only reason it could be resumed and finished.
- **Verify interfaces mechanically, not by reading the diff.** In the reference run, a tool's JSON
  schema had to remain identical and a CLI command's `--help` output was compared **byte for byte**.
  Pick the cheapest stable contract for your project and diff it.
- **Expect resource exhaustion from parallelism.** ~30 worktrees each started their own language server
  and consumed ~8.7 GB. Plan for shared services (one language server for all worktrees, with a
  liveness check), or budget the RAM.
- **Nested delegation is normal** — 1,328 of those 111,352 tool calls were themselves
  `delegate_task`. Allow the tree to go a few levels deep, and make each level's brief self-contained.

**Failure to plan for:** deleting a symbol because the in-repo call graph says nothing calls it. If the
repo publishes anything — a plugin API, a CLI, an importable module — an externally-used name has no
internal caller. **Flag removed public names for review**; the reference campaign added exactly this
check after shipping the regression.

## 6. Delivery — the PR or PR set

The user asked for a PR. Give them one that can actually be reviewed.

**Split when a single PR would be unreviewable** — roughly, when it exceeds a few thousand changed
lines or spans independent subsystems. A good split is **by sweep, by subsystem, or by change kind**
(pure deletion / helper unification / file decomposition / legibility), not by arbitrary line count.
Each PR must stand alone: independently green, independently revertable.

**Every PR body carries:**

1. **Measured before/after** — LOC and branch count for the scope it touches, with the deletion vs
   relocation split from §2. Use the reporting skeleton in [measuring.md](measuring.md#reporting-skeleton)
   so the numbers are comparable across PRs.
2. **The proof** — test command and its real result. Not "tests pass" but the command and the count.
   If tests could not be run, say "not run" and why; never imply a pass that did not happen.
3. **What was deliberately not cut**, and why (the `when-to-relax` list, plus anything that survived
   the meta-principle).
4. **The shortfall, if any** — the honest version of the number and the named cause.
5. **Risk tiering** from [auditing.md](auditing.md) — which changes are SAFE / CAREFUL / RISKY, so a
   reviewer knows where to spend attention.

## 7. Guardrails

- **The metric is the symptom, not the goal.** Elegance, legibility, and behavior-preservation are
  the goal; LOC is how you tell whether you moved. A campaign that hits −30% and makes the code
  harder to understand has failed, whatever the diffstat says.
- **Do not remove a boundary to win a number.** Compat shims, staged migrations, vendor isolation,
  and validation at trust boundaries look like bloat and are not — check `git blame` and the
  surrounding comment before cutting, per the Chesterton's Fence rule in [SKILL.md](../SKILL.md).
- **"No excuses" is not "no judgment."** The mandate is to proceed without asking permission for each
  step — not to skip the checks that make the result trustworthy. Autonomy covers *when to act*, never
  *what to verify*.
- **When a "violation" survives scrutiny** because fixing it makes the code worse, record why and move
  on — the [meta-principle](when-to-relax.md#the-meta-principle).
