---
name: deslop-architecture-dependency-injection
description: Deslop principle — Dependency Injection: Inject dependencies; declare what, not how.
---

# Dependency Injection

> "The key benefit of Dependency Injection is that it removes the dependency that a class has on a concrete implementation."
> — Martin Fowler

Dependencies should be injected from outside rather than created internally — a class declares *what* it needs, not *how* to get it. Constructor injection is preferred (explicit, immutable, testable) over setter or interface injection. The primary payoff is testability: swap real dependencies for test doubles without touching the class. DI also makes SRP violations visible — a constructor demanding too many dependencies is a class doing too much.

```python
# ❌ Wrong - Hardcoded dependency
class MovieLister:
    def __init__(self):
        self._finder = ColonDelimitedMovieFinder("movies.txt")  # Coupled!

# ✅ Correct - Injected dependency
class MovieLister:
    def __init__(self, finder: MovieFinder):
        self._finder = finder
```
