---
name: deslop-pattern-declaration-vs-enforcement
description: Deslop pattern — Declaration vs Enforcement: a name, docstring, route or config key promises what the body never does; make the code carry the promise or delete the claim.
---

# Declaration vs enforcement

**Why this is slop:** a name, comment, route or config key promises what no line keeps, and nothing couples the promise to the code, so the reader's trust is spent on something untrue.

The declaration was written once and the code changed under it; nothing couples the two.

## The structural tell

A docstring, name, comment, route declaration or config key promises behaviour that no line enforces: a `validate_*` that only logs, a route marked admin-only whose handler never checks, an "idempotent" docstring over an append, a `timeout` setting nothing reads. Read the promise, then find the line that keeps it. No such line is the finding.

## Variant: kept on some routes

The rule is enforced, but only on the path its author was working on. The same data also travels another path, and nothing checks it there.

- An error message is hidden in the log, and sent unhidden in an event to the user interface.
- Private text is removed from the body of a message and left in its title.
- An admin right is given an expiry time, and the object that carries the right does not hold that time.
- A database guard runs on insert and update, and not on delete.
- Of two login checkers, one checks the token type and the other does not.

This is easy to miss because a search for the check finds it, so the code looks correct. List every path the protected thing can take and look at each one. Put the check at the one place all paths go through. When the paths are many members under one **authority** rule (a permission, a lock or lease), the mechanism is [complete-mediation](../principles/reliability/complete-mediation.md): the one door checks and returns the only writing handle. Other rules a population must obey (validation, idempotency, an audit record with its change) go to the owners the [population census](../readings/auditing.md#the-population-census) names.

## Why it arises

Declarations are cheap and unchecked. Middleware is unmounted, a refactor drops the guard, or the setting was wired to nothing from the start.

## Repair shape, owner first

Make the code carry the promise — a type, a guard inside the handler's own dependency, a constraint — or delete the claim. Never edit the comment to match a behaviour nobody chose.

## Who owns the mechanism

| Principle | Owns | Boundary with this pattern |
|---|---|---|
| [unclaimed-guarantee](../principles/clean-code/unclaimed-guarantee.md) | a promise nobody enforces | the mechanism; this pattern is its most common form |
| [design-by-contract](../principles/reliability/design-by-contract.md) | pre/postconditions that are checked | what an enforced promise looks like |
| [least-surprise](../principles/clean-code/least-surprise.md) | names that match behaviour | the reader's side of a false name |
| [complete-mediation](../principles/reliability/complete-mediation.md) | the one door checks under its lock and returns the only writing handle | the *kept on some routes* variant, when a population of members carries an authority rule (permission, lock or lease) |
| [documentation-discipline](../principles/clean-code/documentation-discipline.md) | what a comment may claim | the comment half; does not decide whether code or claim goes |

## Caught by

Lenses `guarantees` and `legibility`.

## Measured

785 findings, 64 high — the most frequent pattern, mostly medium severity. Heuristic classes; they overlap.

## Example

```typescript
// ❌ the route declares who may call it; the handler never looks
router.delete("/orders/:id", requireRole("admin"), (req) => remove(req.params.id)); // role middleware not mounted
// ✅ the guarantee lives in the handler's own dependency, so it cannot be skipped
router.delete("/orders/:id", (req) => remove(authorize(req, "admin"), req.params.id));
```
