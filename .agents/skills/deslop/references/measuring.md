---
name: deslop-measuring
description: How to measure a deslop campaign — the four harnesses (static shape, runtime, navigability, lookup sim), the honest before/after tables from a real 34% reduction, the metrics that matter (nesting depth, elif chains, CC), and the caveats that keep the number truthful.
---

# Measuring a deslop campaign

> **A campaign that cannot be measured cannot be claimed.** LOC alone is the weakest signal in this
> file; the strongest is *what an agent pays to read the code*.

This reference exists because a real campaign was measured end-to-end, and the measurement is what
made it credible. Source: Nous Research, *Refactoring Hermes with 1,393 agents* — PR
`NousResearch/hermes-agent#102117`, baseline `main` @ `63279301bcb`, PR @ `a0be177aac0`. All numbers
below are that campaign's actual figures, quoted so you can see the shape of a result and the shape of
an honest caveat. Reproduce with your own harnesses; do not copy the numbers.

## The four harnesses

Run all four. Each answers a question the others cannot.

| Harness | Answers | Produces |
|---|---|---|
| **`static_metrics.py`** | What shape is the code? | LOC split, size/function distributions, `elif`/nesting depth, radon cyclomatic complexity + maintainability index (see [Cyclomatic Complexity](clean-code/cyclomatic-complexity.md)), import graph + SCC cycles |
| **`runtime_bench.py`** | Did we make it slower? | Fresh-interpreter import time, module count, RSS; CLI end-to-end; hot paths; `pytest --collect-only`; bytecode |
| **`bench.py`** | What does it cost to find a symbol? | Per-"show me X" token cost over ~19k tasks derived from the test suite |
| **`lookup_sim.py`** | What does *our tooling* pay per lookup? | Paired grep+read simulation over a few thousand common symbols |

**Always take two independent runtime passes** and report both — a single pass cannot distinguish a
real regression from machine noise.

## The unbiased task corpus (the best idea in the campaign)

`bench.py`'s workload is derived mechanically:

> every `from <module> import <Name>` in `tests/`, resolved to the module that *defines* the name.

The reasoning, in the author's words: **"Nobody picked these; they're the symbols the test suite
actually reaches for."** This is the fix for the usual problem with performance sampling — you cannot
bias the sample toward files you already suspect, because you did not choose it. If the repo has a
test suite, it has a ready-made, non-cherry-picked map of which symbols matter.

**Use this.** It is cheap to run, impossible to game, and it directly measures the thing a campaign is
supposed to improve.

## What actually moved (the real before/after)

### Shape

| Metric | Before | After | Δ |
|---|---|---|---|
| physical lines (first-party, no tests) | 1,018,446 | 651,589 | **−36%** |
| code lines (no blanks/comments/docstrings) | 660,534 | 452,572 | **−31%** |
| files > 5,000 lines | 37 | 6 | −84% |
| files > 2,000 lines | 103 | 41 | −60% |
| functions > 300 lines | 192 | 2 | **−99%** |
| functions > 100 lines | 1,338 | 139 | −90% |
| longest function (lines) | 7,310 | 566 | −92% |
| **`if`/`elif` chains ≥ 8 branches** | 224 | 7 | **−97%** |
| **longest `elif` chain** | 92 | 9 | −90% |
| **max nesting depth** | 99 | 10 | **−90%** |
| functions nested ≥ 5 deep | 964 | 369 | −62% |
| radon mean cyclomatic complexity | 6.73 | 4.88 | −27% |
| blocks with CC > 50 | 219 | 4 | −98% |
| worst function CC | 1,075 | 84 | −92% |

**Note which metrics carry the story.** Not "lines deleted" — **nesting depth, `elif` chain length,
and cyclomatic complexity**. Those are what "less if-if-if-if-else routing" and "elegance" actually
mean when you make them measurable, and they moved far more (90–99%) than LOC did (31–36%). **A
campaign judged only on LOC understates itself and can be gamed; a campaign judged on these cannot.**

### What an agent pays to read the code

| Per "show me X" task | Before | After | Δ |
|---|---|---|---|
| tokens of the defining file (median) | 30,762 | 10,333 | **−66%** |
| tokens of the defining file (p90) | 114,456 | 52,547 | −54% |
| tokens of the defining file (max) | 330,028 | 85,075 | −74% |
| overhead beyond the symbol itself (median) | 24,867 | 9,403 | −62% |
| **tasks whose file does not fit a 128k context** | **1,589** | **0** | −100% |
| 2,000-line read windows to scan the file (mean) | 3.26 | 1.43 | −56% |
| cyclomatic complexity of the symbol (mean) | 236.99 | 55.83 | **−76%** |

The headline is not the percentage: **1,589 lookups landed in a file no 128k-context model could load
at all; after, zero.** That is the difference between "expensive to read" and "cannot be read."

### What a lookup costs with real tooling

Policy: `grep -n` the definition, `read_file` a 60-line window at the hit, page forward in 2,000-line
windows only while the definition keeps going.

| Per lookup | Before | After | Δ |
|---|---|---|---|
| tokens returned (mean) | 2,218 | 993 | **−55%** |
| lookups needing >1 read window | 628 | 184 | **−71%** |
| exact tokens of the definition itself (mean) | 410 | 249 | −39% |
| median file the symbol lives in (lines) | 2,130 | 686 | −68% |

## The caveats — copy these habits, not just the numbers

An honest campaign reports what got **worse**. This one did:

- **The median lookup moved the other way: 564 → 680 tokens (~20% worse).** Cause: with comments and
  docstrings stripped, a line of code is 11.6 tokens instead of 9.0, so a **fixed 60-line window costs
  more even though the definitions inside it got 39% shorter.** The mean fell only because the enormous
  tail collapsed. **If you only reported the mean, you would have missed that the typical case got
  worse.**
- **Module count and import dependencies rose** — 109 → 176 first-party modules on the gateway path,
  and import time on split entry points went up (`run_agent` 270 → 292 ms, `gateway.run` 154 → 196 ms).
  Recoverable by making large facades lazy; a known, non-blocking cost.
- **Six files still exceeded 5,000 lines.** Not a clean sweep — say so.
- **Coupling was not resolved.** "The refactor made individual pieces easier to read without resolving
  all the coupling between them." Splitting files reduces reading cost, not architectural debt — do not
  claim otherwise.
- **Runtime was unchanged**, as expected for Python. Report it as *unchanged within noise*, with the
  noise, rather than claiming an improvement.

**The rule this demonstrates:** report the median and the tail, report what regressed, and name the
mechanism. A campaign that reports only improvements has either not measured carefully or is not
telling you everything.

## Scale and process (what a campaign actually takes)

From the live transcripts, Sep 2 10:18 → Sep 3 21:52:

- **478 delegation batches, 1,652 subagent tasks, 111,352 tool calls** (70,046 terminal · 14,223
  read_file · 9,224 execute_code · 8,631 write_file · 5,042 patch · **1,328 nested `delegate_task`**)
- 4,257 commits across 2,601 files; **+432,726 / −782,630** lines
- ~110 agents concurrent on average; peak 218
- median task 39 min; p90 3.2 h

**Division of labour that worked:** the orchestrator never edited source. It measured the codebase,
split it into **36 non-overlapping groups**, wrote the assignments, read the reports, integrated the
branches, and ran the checks. Workers used **git worktrees** — separate checkouts so they could not
clobber each other — and **committed after each verified step**, which is why the run was recoverable.

**Interface preservation, checked mechanically:** a tool's JSON schema had to remain identical; a CLI
command's `--help` output was compared **byte for byte**. A **frozen baseline** was established and
every integration failure was checked against it — the same discipline as *"repro on `origin/main`
HEAD in a clean env to determine whether the failure is pre-existing."*

## Failure modes to expect

- **The run died mid-flight** when the provider's auth token expired (~50 min in). Workers' commits and
  briefs survived; a separate session diagnosed it and prepared a handoff for the resumed run.
  **Commit after every verified step, or a dead run loses everything.**
- **Removed public names that had no callers inside the repo but that external plugins import.**
  Lesson: a symbol with no in-repo caller is **not** dead — it may be a published contract. They added
  a check that flags removed public names for review. **This is the single most likely campaign
  regression: deletion based on internal call-graph evidence.**
- **A mechanical rewrite changed exception handling at ~65 call sites** and the existing tests missed
  it — caught by review, not by CI. Mechanical sweeps need their own verification, not just a green
  suite.
- **Resource exhaustion from parallelism:** ~30 worktrees each started their own Pyright, consuming
  ~8.7 GB; fixed by sharing one language server with a liveness check.

## Reporting skeleton

```
Scope:            <dirs> — exclusions: vendor, generated, lockfiles
Baseline:         <commit>  ·  Head: <commit>
Shape:            LOC <a>→<b> (−X%)   code-LOC <a>→<b> (−Y%)
                  files>5k <a>→<b>   funcs>300 <a>→<b>
                  longest elif chain <a>→<b>   max nesting <a>→<b>
                  mean CC <a>→<b>
Navigability:     median tokens/file <a>→<b>   files over 128k ctx <a>→<b>
Lookup sim:       mean tokens <a>→<b>   median tokens <a>→<b>
                  lookups needing >1 window <a>→<b>
Runtime:          2 passes, within noise / regressed by <x> — cause: <…>
Regression:       <what got worse, and why>
Tests:            <command> → <real result>
Not cut:          <what survived the meta-principle, and why>
```

**Subtract nothing and omit nothing.** The credibility of the whole campaign rests on this table being
the one a hostile reviewer would have produced.
