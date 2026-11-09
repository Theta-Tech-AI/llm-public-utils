---
name: deslop-pattern-unnamed-decision
description: Deslop pattern — Unnamed Decision: a question never asked, answered per site; ask it, answer it once, name the answer.
---

# The decision nobody named

Nothing was copied and nothing drifted. The question was never asked, so each author answered it by accident, in the shape of whatever line they happened to write.

## The structural tell

An edge of the input space has no stated policy: what a zero or negative limit means, whether a record with no timestamp counts as old, whether a reply that fails to parse is content or an error, whether a blank credential is absent, which states count as "needs waking", whether a date with no zone is local, whether a per-item failure fails the batch. No function, constant, enum member or sentence anywhere names the question. The answer lives in an operator: `<` beside `<=`, `in {A, B}` beside `!= C`, `or 0`, an early `return`, a `continue` in an `except`.

Sites that answer it share no text and no vocabulary, so no clone scanner and no search by name finds them. Find them by the question: take one branch, say what it decides in one sentence, then open every other route to the same operation and ask each the same sentence. Routes worth opening side by side: the sync and the async method, the single call and the batch, one adapter per provider, the read filter and the write filter, the log line and the event built from one error, the client's guard and the server's.

Two different answers is the finding. One answer with no name is the finding one change early.

## Why it arises

The happy path was designed and the edge was met while typing. Each author closed it with the smallest thing that let the function finish, which is a local, reasonable, undocumented choice. Review sees one of them at a time and each one reads as fine.

## Repair shape, owner first

1. **Ask the question in words and get it answered.** Neither existing answer is presumed right; often the true answer is a third one, or "refuse". This is a design decision, so it may need a person.
2. **Name the answer** where its concept lives: a predicate, an enum member, a parsed type that cannot hold the undecided case.
3. Route every site through the name and delete the operators that used to carry it, in the same change.

Aligning the operators without step 2 leaves the next author to answer it a third way.

## Who owns the mechanism

| Principle | Owns | Boundary with this pattern |
|---|---|---|
| [decide-dont-cope](../principles/clean-code/decide-dont-cope.md) | a decision deferred into control flow at one site | the single-site form; this pattern is the same dodge met at several sites with different outcomes |
| [single-source-of-truth](../principles/architecture/single-source-of-truth.md) | one home for a fact | where the named answer goes once it exists |
| [least-surprise](../principles/clean-code/least-surprise.md) | siblings that behave alike | the caller's view of two routes that disagree |
| [design-by-contract](../principles/reliability/design-by-contract.md) | stated preconditions | "refuse" as the answer |

Sibling pattern: [one-fact-many-owners](one-fact-many-owners.md) starts from a known fact that was copied and drifted, and its repair picks an owner among the copies. Here there is no fact yet and no copy is the original; the repair starts by deciding.

## Caught by

Lenses `duplication` and `parsing`; `legibility` meets it as siblings that surprise.

## Measured

Not a class in the field run's counts. Added from a later pass, where it accounted for most findings in which two routes to one operation disagreed.

## Example

```python
# ❌ "is a document with no modified time old enough?" — never asked, answered twice
def page(docs, cutoff):   return [d for d in docs if d.modified is None or d.modified < cutoff]   # yes
def query(cutoff):        return Filter.by("modified").less_than(cutoff)                           # no: null never matches
# ✅ asked, answered, named; both routes use it
def is_stale(modified, cutoff): return modified is None or modified < cutoff
```
