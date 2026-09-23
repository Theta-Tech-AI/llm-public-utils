---
name: deslop-clean-code-cyclomatic-complexity
description: Deslop principle — Cyclomatic Complexity: a testability metric, read as a locator, never optimized as a target.
---

# Cyclomatic Complexity

> "…we were very aware that if we measure it, you will try to improve it."
> — SonarSource, *Cognitive Complexity, Because Testability != Understandability*

**The number has exactly one meaning, and it is not "hard to read".** Cyclomatic complexity (Thomas J.
McCabe, 1976) counts the **linearly independent paths** through a routine, taken from its control-flow
graph: `M = E − N + 2` for a single subroutine. For a structured routine that reduces to something anyone
can compute by eye — **decision points + 1** — with two riders that tools disagree about:

- **Each predicate variable counts.** `if a and b` is two decisions, not one, because at machine level it
  is `if a then if b then`. This is why the same function can score differently in different tools.
- **Each extra exit point subtracts.** With multiple exits the count is `π − s + 2`, which is why adding
  early returns *lowers* the score.

Because every independent path needs its own test, the metric is first a **testability** measure: basis-path
testing needs as many test cases as the routine's complexity.

## The same score, three different experiences

Measured with `radon` (`uvx radon cc -s`), all three of these score **4 — rank A, "low complexity"**:

```python
def flat(a, b, c):          # three sequential decisions
    if a: return 1
    if b: return 2
    if c: return 3
    return 0

def nested(a, b, c):        # the same three decisions, nested three deep
    if a:
        if b:
            if c:
                return 3
    return 0

def predicated(a, b, c):    # one `if`, three predicate variables
    if a and b and c: return 3
    return 0
```

One number, three reading experiences. The nested version is the one a reviewer will misread, and the
metric cannot see the difference — it counts each decision once regardless of depth. This is precisely what
SonarSource built **Cognitive Complexity** to repair: +1 for each break in the linear flow, +1 *more* for
each level of nesting, and nothing at all for shorthands that condense code readably.

## Blind spots

- **Nesting is invisible** (above). Three nested `if`s equal three sequential ones.
- **`switch`/`case` inflate it.** A 12-case dispatch reads easily and scores 13. Cognitive Complexity
  increments once for the whole structure, for exactly this reason.
- **Boolean shorthand inflates it.** `and`/`or` chains on one line add up; naming the intermediates reduces
  the score *and* improves the reading — one of the few places where the metric and taste agree.
- **It correlates with size.** Cyclomatic complexity tracks lines of code closely; Les Hatton's claim is
  that it predicts defects no better than LOC does, and studies that control for size are inconclusive. A CC
  reduction at constant LOC has to be explained — say what got more testable, don't just show the delta.
- **It moves for reasons unrelated to quality.** Early returns lower it; guard clauses are good practice;
  so a lower number may be a reshuffle rather than an improvement.
- **Above the routine it degrades.** The metric is defined per subroutine. Sums and averages over a module
  or a class are statistics about your codebase, not measurements of anything a reader experiences.

**Do not confuse it with essential complexity.** McCabe's other measure reduces the flow graph by
condensing every single-entry/single-exit subgraph, then takes the complexity of what cannot be reduced: 1
for any structured program, higher only where control flow is genuinely irreducible (`goto`, deep `break`,
`continue`). It measures *structuredness*, not size.

## Thresholds, and how to read them

McCabe recommended splitting routines that exceed **10**; NIST's *Structured Testing* methodology found the
figure of 10 substantially corroborated, while noting that relaxation is sometimes appropriate. McCabe's own
risk bands, from his DHS presentation, are 1–10 simple, 11–20 moderate, 21–50 complex and high risk, above
50 untestable.

Treat every one of these as **a threshold for looking, not for passing**. A table-driven parser with a
complexity of 30 may be perfectly clear; a routine of 9 that nobody can follow is not redeemed by the
number.

## How to use it in a pass

1. **Measure the distribution, not the average.** The mean hides the tail, and the tail is the work. Report
   both — a campaign figure such as "per-symbol mean 237 → 56" is only interpretable beside the distribution
   it came from.
2. **Compare like with like.** Same language, same tool, same version. Tool differences on boolean
   operators, `switch` and exit points make cross-tool numbers meaningless.
3. **Read the top of the list, not the score.** The deliverable of a CC pass is a short list of routines
   worth reading, plus a reason for each.
4. **Never target the number.** Standing a "reduce complexity by 30%" target invites splitting one routine
   per branch, which produces shallow functions and often *raises* the real reading cost. This is the exact
   failure the SonarSource paper describes: teams restructuring code to lower a score without making it
   easier to read.
5. **Pair it with the reader's metric.** Cyclomatic complexity for testability and triage; Cognitive
   Complexity or a human read for readability; LOC and file size for shape.

## In relation to other principles, cyclomatic complexity is the number the others are usually invoked to justify

| Principle | Relationship |
|-----------|--------------|
| [**Measuring a campaign**](../measuring.md) | The harness that produces the number, and the reporting discipline that keeps it honest |
| [**KISS**](kiss.md) | Lists "cyclomaticism" as a complexity tell — the metric is one input to that judgement, not the judgement |
| [**Cognitive Load**](cognitive-load.md) | What the metric cannot see: nested depth and working-memory cost |
| [**Small Functions**](small-functions.md) | The tempting-but-wrong response — splitting per branch buys the number and loses the reader |
| [**Guard Clauses**](guard-clauses.md) | Early exits lower the count by design; the improvement is real, the number is a side effect |
| [**Elegance**](elegance.md) | The judgement the number cannot replace: minimality without shallowness |

## Summary

1. **Cyclomatic complexity counts independent paths** — decision points + 1 in a structured routine, with
   predicate variables counted individually.
2. **It is a testability metric.** Basis-path testing needs as many cases as the number.
3. **It is blind to nesting, generous to `switch`, and correlated with LOC** — so it is not a readability
   score and not a quality gate.
4. **Read it as a locator**: distributions, the tail, like-for-like tooling, and a reason for each hot spot.
5. **Never optimize it directly.** A score that drops while the reading cost rises is the failure mode the
   metric's own critics named, and the reason Cognitive Complexity exists.
