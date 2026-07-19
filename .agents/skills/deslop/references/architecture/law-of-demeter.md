---
name: deslop-architecture-law-of-demeter
description: Deslop principle — Law of Demeter: Talk only to immediate friends; the one-dot rule.
---

# Law of Demeter

> "Each unit should have only limited knowledge about other units: only talk to your immediate friends; don't talk to strangers."
> — Ian Holland

Limit how much one object knows about another's structure: only talk to immediate friends, never reach *through* them. Formally, a method may invoke methods on its own object, its parameters, objects it creates, and its object's direct attributes — but not on objects *returned* by other calls. In practice this is the "one dot" rule: `a.b()` is fine, `a.b().c().d()` is a train wreck.

```python
# ❌ Wrong - Multiple dots (train wreck)
customer.get_wallet().get_credit_card().charge(amount)

# ✅ Correct - One dot
customer.charge(amount)  # Customer knows how to charge itself
```

Chaining is fine where there's no structure being traversed: builders and fluent interfaces that return `self`, DTOs with no behavior to encapsulate, and standard-library value operations like `"hello".strip().upper()`. And as Fowler warns, don't become a "getter eradicator" — objects sometimes collaborate by *providing* information, and the point is co-locating behavior with data, not banning every accessor.

---

In relation to other principles, the law of Demeter:

| Principle | Relationship |
|-----------|--------------|
| [**Encapsulation**](encapsulation.md) | A train wreck signals behavior lives away from its data |
| [**Cognitive Load**](../clean-code/cognitive-load.md) | Long chains force readers to know distant structure |
| [**Principle of Least Surprise**](../clean-code/least-surprise.md) | Reaching through objects is spooky action at a distance |
