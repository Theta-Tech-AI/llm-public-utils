---
name: deslop-clean-code-documentation-discipline
description: Deslop principle — Documentation Discipline: Where docs live; which comments earn their place.
---

# Documentation Discipline

> "Code tells you how, comments tell you why."
> — Jeff Atwood, Stack Overflow co-founder

Comments don't compile, can't be tested, and rot — yet sometimes they're essential for explaining *why*. The discipline is knowing the difference and moving documentation to the highest appropriate level.

| Layer | Audience | Purpose |
|-------|----------|---------|
| **README** | New users/devs | First contact, setup, overview |
| **API Docs** | Consumers | Contract, usage, edge cases |
| **Docstrings** | Callers | What it does, params, returns |
| **Inline Comments** | Maintainers | Why this specific implementation |

Comments earn their place when they explain business-rule rationale, justify a rejected alternative, document a workaround for an external constraint, attribute a borrowed algorithm, or warn about a non-obvious footgun. They don't earn it when they parrot what the code already says, journal who-changed-what (use git blame), pile up as a TODO graveyard, or preserve commented-out dead code (git has the history).

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Parrot comments** | `i += 1  # increment i` | Delete—code already says this |
| **Rotting comments** | Comment describes deleted code | Delete or update |
| **Journal comments** | `// Fixed by John, 3/15` | Use git blame instead |
| **Commented-out code** | Dead code polluting the file | Delete—git has history |
| **Mandated comments** | Boilerplate on every method | Comment only when valuable |
| **TODO graveyards** | `// TODO: fix this (2019)` | Create tickets or delete |

Comments drift from code silently, so keep them next to the code they describe, review them during code review, and delete rather than let them lie. Docstrings should document non-obvious behavior — business rules, edge cases, what gets raised — not restate a signature the reader can already see.

```python
# ✅ Documents non-obvious behavior
def calculate_shipping(order: Order) -> Decimal:
    """
    Calculate shipping cost with business rules.

    - Free shipping for orders over $100
    - Hawaii/Alaska adds flat $15 (no free shipping)

    Raises:
        InvalidAddressError: If shipping address is incomplete
    """
```

---

In relation to other principles, documentation discipline:

| Principle | Relationship |
|-----------|--------------|
| [**Self-Documenting Code**](self-documenting-code.md) | Name it well first; comment only the why |
| [**Boy Scout Rule**](../reliability/boy-scout-rule.md) | Delete rotting comments as you pass them |
| [**DRY**](../architecture/dry.md) | A comment restating code is duplicated knowledge that drifts |
| [**Cognitive Load**](cognitive-load.md) | Parrot comments cost reading effort and add no information |
