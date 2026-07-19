---
name: deslop-architecture-command-query-separation
description: Deslop principle — Command-Query Separation: Methods either do or answer, never both.
---

# Command-Query Separation

> "Asking a question should not change the answer."
> — Bertrand Meyer

A method should either return information (a query, no side effects) or change state (a command, returns nothing) — never both. Keeping them separate means queries are safe to call anywhere, cache, and parallelize without race conditions, while commands stay easy to reason about and test. Break the rule only for genuinely atomic operations that must do both — a stack `pop`, a thread-safe increment-and-get, database identity generation.

```python
# ❌ Wrong - Modifies AND returns
def get_or_create_user(self, email: str) -> User:
    user = self.db.find_by_email(email)
    if not user:
        user = User(email=email)
        self.db.save(user)  # Side effect!
    return user

# ✅ Correct - Separate operations
def find_user_by_email(self, email: str) -> User | None:
    """Query: Returns user or None, no side effects."""
    return self.db.find_by_email(email)

def create_user(self, email: str) -> None:
    """Command: Creates user, returns nothing."""
    self.db.save(User(email=email))
```

---

In relation to other principles, command-query separation:

| Principle | Relationship |
|-----------|--------------|
| [**Principle of Least Surprise**](../clean-code/least-surprise.md) | CQS eliminates the mutating-query surprise |
| [**Immutability**](immutability.md) | Queries on immutable data are always safe |
| [**Design by Contract**](../reliability/design-by-contract.md) | Both are Meyer's — contracts state what queries guarantee and commands effect |
| [**Idempotency**](idempotency.md) | Queries are idempotent for free; commands must be designed for it |
