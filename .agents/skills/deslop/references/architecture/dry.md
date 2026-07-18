---
name: deslop-architecture-dry
description: Deslop principle — DRY: Don't Repeat Yourself: One authoritative representation per piece of knowledge; fix at the 2nd occurrence.
---

# DRY: Don't Repeat Yourself

> "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."
> — Andy Hunt & Dave Thomas, *The Pragmatic Programmer*

DRY is about **knowledge**, not code — avoid duplicating *meaning*, not syntax. Knowledge duplication (the same business rule living in multiple places) must always be fixed, starting at the SECOND occurrence — not the third. Incidental duplication (code that *looks* similar but represents *different* concepts that will evolve independently) should be left alone; merging it couples unrelated concerns. The distinguishing test is never the occurrence count, it's whether it's the same knowledge: see [Hunting Duplication — Beyond Token Scanners](../duplication.md) for how to tell the two apart and what to do about it once found.

> "Duplication is far cheaper than the wrong abstraction." — Sandi Metz

The wrong abstraction is the more expensive failure. One developer extracts it; the next needs it slightly different and adds a parameter; the next adds a conditional; eventually it's incomprehensible but no one deletes it because of sunk cost. When an abstraction starts accumulating parameters and conditionals to handle "just one more case," inline it back into its callers and start fresh — re-extracting is cheaper than maintaining the wrong abstraction.

| True Knowledge Duplication (FIX) | Incidental Similarity (LEAVE) |
|---------------------------------|------------------------------|
| Same business rule/concept | Different business concepts |
| Changes *must* affect all instances | Instances will evolve independently |
| 2+ occurrences of the SAME rule | Similar-looking code, different concepts |
| Abstraction simplifies | Abstraction requires conditionals |

```python
# ❌ Over-DRY: Merged with conditionals
def get_user_by_something(identifier, by_type):
    if by_type == "id": ...
    elif by_type == "email": ...

# ✅ Separate functions with clear responsibilities
def get_user_by_id(user_id: int) -> User: ...
def get_user_by_email(email: str) -> User: ...
```

DRY extends beyond code: define database constraints once in the schema, generate API contracts from code (FastAPI/Pydantic) rather than maintaining them separately, centralize config in one module, and keep a single authoritative source for documentation.

## Worked Example: Two Classes Repeating the Same 3 Lines

In coding, the D.R.Y. ("Don't Repeat Yourself") is one of the most important principles. If the same line(s) of code appear in more than one location, it should probably be abstracted away into a reusable function (or equivalent).

Consider two different classes each writing:

```python
user = authenticate_user(jwt_token)
groups = get_user_groups(user)
is_superuser = "superuser" in groups
```

If the code is sloppy, you'll find a bunch of classes and functions using those same 3 lines duplicated across the codebase. Deduplicate them into a shared `get_is_superuser(jwt_token)` function. Now you've reduced the lines of code (fewer lines of code is better in general), and made the code more readable and maintainable.

Some argue that for simple things, the overhead of the abstraction is not worth it. Benchmark first to see if you're really losing performance in modern systems due to overhead; usually you're not. Once two occurrences represent the same knowledge, deduplicate them; do not wait for a third copy.

**The deduplicated version — one shared helper, two callers:**

```python
from typing import Sequence


def get_is_superuser(jwt_token: str) -> bool:
    """Resolve whether the bearer of `jwt_token` holds the superuser role.

    Single authoritative implementation of the "authenticate -> list groups
    -> check superuser" chain so every caller resolves superuser status the
    same way. Fix the rule once here; every caller inherits the fix.
    """
    user = authenticate_user(jwt_token)
    groups = get_user_groups(user)
    return "superuser" in groups


class AuditExporter:
    """Exports audit events, redacting fields the caller may not read."""

    def __init__(self, jwt_token: str) -> None:
        self._is_superuser = get_is_superuser(jwt_token)

    def can_read(self, event) -> bool:
        return self._is_superuser or event.actor_id == "self"


class AdminConsole:
    """Gates admin-only operations behind the superuser check."""

    def __init__(self, jwt_token: str) -> None:
        self._is_superuser = get_is_superuser(jwt_token)

    def delete_project(self, project_id: str) -> None:
        if not self._is_superuser:
            raise PermissionError("superuser required")
        ...
```

The 3-line chain appeared in two classes; it now lives once in `get_is_superuser`. If the group lookup ever changes (e.g. switched to a Graph API call, or `"superuser"` renamed to `"system-administrator"`), there is one place to edit — not N. Feed this to your coding agents, have them make a skill for this, and have them scan your codebase for this slop violation — you'll be surprised how much this shows up.
