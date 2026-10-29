---
name: deslop-reliability-errors-at-the-boundary
description: Deslop principle — Errors at the Boundary: validation belongs where untrusted input enters, translation at each abstraction seam, and the decision where it can be acted on.
---

# Errors at the Boundary

> "Higher layers should catch lower-level exceptions and, in their place, throw exceptions that can be explained in
> terms of the higher-level abstraction."
> — Joshua Bloch, *Effective Java*, Item 73 (exception translation)

An error has three moments — **detection, translation, decision** — and each belongs to a particular place.
Detection belongs where untrusted data enters. Translation belongs at every abstraction seam, so a caller never
catches a driver's exception to decide an HTTP status. The decision (retry, fall back, return 409, page someone)
belongs where the context to make it exists. Slop is the misplacement of any of the three: a handler four layers
above the code that raised `psycopg2.errors.UniqueViolation` and branches on `str(exc)`; a validator called from
every leaf because the value was never made safe where it entered; a `except Exception` whose only action is to log
and continue. **The finding is a decision located where it cannot be made correctly, and the missing seam that
would have placed it.**

```python
# ❌ detection at the edge, decision nowhere near the knowledge
def register(payload):                       # the edge trusts everything
    return db.insert(payload)                # an UNIQUE violation escapes upward

# controller, three layers away
try:
    register(payload)
except Exception as e:                       # catches the driver to build a 400
    if "duplicate key" in str(e):            # string-matching someone else's error
        return 400
    raise
```

```python
# ✅ parse at the edge, translate at the seam, decide where the context lives
@dataclass(frozen=True)
class NewUser:
    email: Email
    name: str

def parse_new_user(payload: Mapping) -> NewUser | Invalid:   # one validator, at the edge

class DuplicateUser(Exception):              # the store's own vocabulary
    ...

class UserStore:
    def insert(self, user: NewUser) -> None:
        try:
            self._session.add(...)
        except IntegrityError as e:
            raise DuplicateUser(user.email) from e      # translation at the seam, cause chained

# the controller decides, in its own vocabulary
try:
    users.insert(parse_new_user(payload))
except DuplicateUser:
    return conflict("email already registered")
```

## What this adds over its neighbours

[Parse, Don't Validate](../architecture/parse-dont-validate.md) covers the *detection* moment and
[Fail-Fast](fail-fast.md) covers *when* to fail. Neither asks the question this file asks of every `catch`: **what
decision does this handler make, and is this the layer that can make it?** [Design by Contract](design-by-contract.md)
states the preconditions; this places their enforcement and the handling of what follows.
[Layering Violations](../architecture/layering-violations.md) is the same rule read as dependency direction.

## The tests

1. **Who-can-act test** — for each `except`, name the decision the catcher makes. "Log and continue", "re-raise
   unchanged", "return None" with no decision is a misplacement, not handling.
2. **Leapfrog test** — count the seams between the throw and the catch. A driver, framework or socket exception
   caught more than one abstraction boundary above it means nobody translated it.
3. **String-match test** — any handler branching on `str(exc)`, `exc.args[0]`, or a message substring is coupled to
   an implementation nobody promised; that is a missing error type at the seam.
4. **Entry test** — for each external input (request body, query, file, environment, third-party response), where is
   it validated? Anything validated *after* it has been used downstream is shotgun validation: one rule, many sites.
5. **Swallow test** — does the handler lose the cause (`raise X()` without `from`, `except: pass`, a bare `log`
   followed by a plausible default)? That is [no silent defaults](no-silent-defaults.md) arriving through the error
   path.
6. **Reach test** — does a lower layer's error type appear in a public signature above it? The abstraction just
   leaked; the caller is now coupled to `sqlalchemy` by accident.

## The family: one disease, many costumes

| Artifact | The misplaced moment | Where it belonged |
|---|---|---|
| `except Exception: log(e)` in a service | no decision at all | let it propagate to the boundary that decides |
| `if "duplicate key" in str(e)` at the controller | decision without translation | a `DuplicateUser` at the store seam |
| `validate(payload)` called in twelve leaves | detection detached from entry | one parse at the edge |
| `raise ValueError("not found")` from a repository | translation skipped | a domain error the caller can act on |
| HTTP 500 for a validation failure | decision with no vocabulary | a parse result at the edge, mapped at the edge |

## The repair

**Parse at the edge, translate at each seam, decide at the handler that holds the context, and always chain the
cause.** Each abstraction publishes its own failure vocabulary; the seam converts into it with `from e`; the handler
that knows what the caller wanted turns it into a status, a retry, or a page. Delete the deep validators and the
string-matched branches in the same change — their disappearance is the measure.

## Boundaries

Internal module boundaries may pass a domain error unchanged; translation is required where the *vocabulary* changes,
not at every function call. A top-level catch-all handler is correct for the genuinely unhandled case, provided it is
one, at the edge, and logs with the trace. Parsing at the edge is compatible with
[Postel's Law](postels-law.md) — tolerant at the edge means tolerating formats, not deferring validation into the
interior. And in a single-file script the edge *is* the whole program: this file's separation earns nothing there.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Exception translation | Joshua Bloch, *Effective Java*, Item 73 | The seam rule, stated as an API obligation. |
| Pass-through exceptions | Practitioner literature on smelly exceptions | Naming the deferred handler as the smell. |
| Parse, don't validate | Alexis King (2019) | Why the edge must produce a type rather than a boolean. |
| Untrusted input at the boundary | Michaël Grégoire, "On Validation vs. Error Checking"; OWASP input-validation guidance | Validation is a boundary activity by definition. |

**What is this library's own:** the three-moment split — detect, translate, decide — as the reading instrument, and
the leapfrog and string-match tests as the way to locate the misplaced one.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Parse, Don't Validate**](../architecture/parse-dont-validate.md) | The detection moment; this file places the other two. |
| [**Fail-Fast**](fail-fast.md) | When to fail; this is where the failure is turned into a decision. |
| [**No Silent Defaults**](no-silent-defaults.md) | The swallow test's target. |
| [**Design by Contract**](design-by-contract.md) | Preconditions stated; this enforces and handles them. |
| [**Layering Violations**](../architecture/layering-violations.md) | The dependency-direction reading of the same seam. |

## Summary

1. **Detect at the edge, translate at the seam, decide where the context is.**
2. **A handler that makes no decision is a misplacement**, not error handling.
3. **String-matching an exception means a missing error type** at the seam below.
4. **Always chain the cause** — an error without its origin is a rumour.
5. **Validation after use is shotgun validation**: one rule, many sites, no owner.
