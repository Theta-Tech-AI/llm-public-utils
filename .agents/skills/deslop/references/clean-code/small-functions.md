---
name: deslop-clean-code-small-functions
description: Deslop principle — Small Functions: Short, focused functions that do one thing (~15 lines).
---

# Small Functions

> "The first rule of functions is that they should be small. The second rule of functions is that they should be smaller than that."
> — Robert C. Martin (Uncle Bob), *Clean Code*

Small Functions is the principle that **functions should be short, focused, and do one thing well**. Decompose logic into small, named units that can be understood at a glance, preferably under 15 lines long. Prefer many smaller functions over fewer big functions. Any time you notice yourself figuring out what a few lines of code does, extract it into a small, tight function which is named after that "what". Long functions are a code smell. Large functions are hard to name, do too many things with too many levels of abstraction, and are difficult to test in isolation. Claiming everything is related and needs to go in the same function is simply lazy thinking, and comments do not take the place of well-defined specific functions. Refactor now, not later.

The "Stepdown" rule says functions should read like a top-down narrative of what's going on, descending one level of abstraction at a time. For instance:

```python
def process_order(order: Order) -> Receipt:
    # Reads like a story:
    validate_order(order)
    apply_discounts(order)
    charge_payment(order)
    send_confirmation(order)
    return create_receipt(order)
```

Some code smells to watch out for are:
- 30+ lines long
- Comments separating sections inside the function
- Deeply nested conditionals (3+ levels)
- Functions with "And" in the name (e.g. `validateAndSave`)

Sometimes, larger functions are the better choice if too many files is increasing cognitive load, or the overhead of calling other functions is significantly degrading performance.

```python
# ❌ Too shallow - interface complexity exceeds implementation
def is_empty(collection): return len(collection) == 0
def is_not_empty(collection): return len(collection) > 0

# ✅ Better - meaningful abstraction hiding complexity
def get_active_users(user_ids: list[int]) -> list[User]:
    """Fetches users, filters inactive, sorts by last_active."""
    users = fetch_users_batch(user_ids)
    active = [u for u in users if u.is_active]
    return sorted(active, key=lambda u: u.last_active, reverse=True)
```

The "small function" principle is related to several other principles:

| Principle | Connection |
|-----------|------------|
| **Single Responsibility** | Small Functions is the *how*, SRP is the *what* |
| **Separation of Concerns** | Decompose by concern, then make each piece small |
| **DRY** | Extract duplicated code into small reusable functions |
| **Self-Documenting Code** | Function names replace comments when functions are small |
| **KISS** | Small functions are simpler to understand |
