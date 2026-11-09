---
name: deslop-pattern-unnamed-decision
description: Deslop pattern — Unnamed Decision: a question never asked, answered per site; ask it, answer it once, name the answer.
---

# The decision nobody named

The code has to handle a situation nobody planned for. Nobody wrote down what should happen, so each programmer who ran into it made up an answer on the spot. The answers do not match.

## The structural tell

Take a search function with a `limit` argument: how many results to return. What should happen when the caller passes `limit = 0`? Nobody decided. So one search function raises an error, a second returns an empty list, and a third returns everything. Each author did something sensible. None of them knew there was a question to answer, and no function name, constant or comment says what the right behaviour is.

More questions of the same kind:

- A document has no "last modified" date. Does it count as old?
- A server sent back something that is not valid JSON. Is that an error, or is it the page text?
- An API key is a string of spaces. Is that a key, or no key?
- Ten items were sent together and one failed. Did the whole batch fail?

The answer usually hides in one small piece of code: `<` in one place and `<=` in another, an `or 0`, an early `return`, a `continue` inside an `except`.

Searching will not find these places, because they share no words. Find them this way:

1. Pick one such piece of code and say in one sentence what it decides: "if the limit is zero, return nothing".
2. Find every other place that does the same job. The usual pairs are the normal and the `async` version of a function, the function for one item and the function for many, the same feature built for two providers, the filter used when reading and the filter used when writing, and the check in the browser and the check on the server.
3. Ask each place the same sentence.

Two places that answer differently are a bug: report it. Places that all agree, with no name for the rule, are worth reporting too, because the next author will not know the rule exists.

## Why it arises

The author designed the normal case and met the odd case halfway through typing. They wrote the smallest thing that let the function finish. A reviewer sees one of these places at a time, and each one looks fine alone.

## Repair shape, owner first

1. **Write the question down and get it answered.** Do not assume one of the existing behaviours is the right one. The right answer may be a third one, or "reject this input". A person may have to decide.
2. **Give the answer a name**, in the module where that idea already lives: a small function, a named constant, or a type that cannot hold the undecided value.
3. **Make every place use that name**, and delete the scattered pieces of code that used to carry the answer, in the same change.

If you only make the pieces match and skip step 2, the next author will invent a new answer.

## Who owns the mechanism

File each instance under one of these principles. This pattern only groups them.

| Principle | What it covers | How this pattern relates |
|---|---|---|
| [decide-dont-cope](../principles/clean-code/decide-dont-cope.md) | one place that avoids making a decision | this pattern is the same thing happening in several places, with different results |
| [single-source-of-truth](../principles/architecture/single-source-of-truth.md) | one home for each rule | where the named answer goes once it exists |
| [least-surprise](../principles/clean-code/least-surprise.md) | similar functions should behave alike | what the caller sees when two of them disagree |
| [design-by-contract](../principles/reliability/design-by-contract.md) | a function states what input it accepts | use it when the answer is "reject this input" |

This is not [one-fact-many-owners](one-fact-many-owners.md). There, a known rule was copied and the copies drifted apart; you fix it by picking one copy as the owner. Here nobody copied anything and there never was a rule; you fix it by deciding the rule first.

## Caught by

Lenses `duplication` and `parsing`.

## Measured

No count yet. This pattern was added after the audit that produced the counts in [the index](../patterns.md).

## Example

```python
# ❌ "what does limit = 0 mean?" — never decided, so three functions give three answers
def search_web(query, limit):    return [] if limit <= 0 else fetch(query)[:limit]
def search_notes(query, limit):  return fetch_notes(query)[:limit or None]        # 0 means "no limit"
def search_files(query, limit):
    if limit <= 0: raise ValueError("limit must be positive")
    return fetch_files(query)[:limit]

# ✅ decided once, named, used by all three
def checked_limit(limit):
    if limit <= 0: raise ValueError("limit must be positive")
    return limit
```
