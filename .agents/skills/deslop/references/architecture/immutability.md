---
name: deslop-architecture-immutability
description: Deslop principle — Immutability: Values fixed after creation; never mutate caller data.
---

# Immutability

> "Immutable types are safer from bugs, easier to understand, and more ready for change."
> — MIT 6.005 Software Construction

Once created, an immutable object's value is fixed; to "change" it you create a new one. Mutable shared state causes most concurrency and aliasing bugs, and immutability eliminates them by design — objects become safe to share between threads without locks or defensive copies, usable as hash keys, and easy to reason about because you only need to understand the creation site. The common violation is a function that quietly mutates its caller's data; return a new structure instead.

```python
# ❌ Wrong - Mutates caller's data
def normalize_scores(scores: list[float]) -> list[float]:
    for i in range(len(scores)):
        scores[i] /= max(scores)  # Mutates the input!
    return scores

# ✅ Correct - Returns new list
def normalize_scores(scores: list[float]) -> list[float]:
    max_score = max(scores)
    return [score / max_score for score in scores]
```

In Python, reach for `@dataclass(frozen=True)`, `tuple` instead of `list` for fixed data, and `frozenset` instead of `set`.

---

In relation to other principles, immutability:

| Principle | Relationship |
|-----------|--------------|
| [**Command-Query Separation**](command-query-separation.md) | Immutable objects make every query side-effect-free |
| [**Parse, Don't Validate**](parse-dont-validate.md) | Parsed types should be frozen values |
| [**Orthogonality**](orthogonality.md) | No shared mutable state, no hidden coupling |
| [**Idempotency**](idempotency.md) | Assignment to fresh values is naturally idempotent |
