---
name: deslop-reliability-boy-scout-rule
description: Deslop principle — Boy Scout Rule: Leave code better than you found it, scoped to what you touch.
---

# Boy Scout Rule

> "Always leave the code better than you found it."
> — Robert C. Martin (Uncle Bob), *Clean Code*

Leave the code slightly better than you found it with each commit. Continuous small improvements — renaming `o` to `order`, removing a dead import, extracting a magic number, simplifying a tangled conditional — compound and beat periodic "refactoring sprints," because each change is small enough to be low-risk and ride along with the feature you're already shipping. But clean the campground, not the forest: scope cleanup to the files you're already touching (a 350-file blank-line sweep makes review impossible), and file a ticket for anything larger.

```python
# ❌ Wrong - "Not my problem" attitude
def add_discount(order):
    o = order          # terrible name from legacy code
    d = o.total * 0.1  # magic number
    o.total = o.total - d
    return o

# ✅ Correct - cleaned up while adding the feature
def add_discount(order: Order) -> Order:
    DISCOUNT_RATE = 0.1
    discount = order.total * DISCOUNT_RATE
    order.total = order.total - discount
    return order
```

The excuses to distrust: "I'll clean it up later" (you won't), "that's not my code," "it works, don't touch it." The exceptions to respect: don't "improve" code you don't understand or that has no test coverage, and don't fold cleanup into a time-critical production fix. This is the antidote to broken windows — neglect invites more neglect, and a tidy file signals the code is cared for.

---

In relation to other principles, the boy scout rule:

| Principle | Relationship |
|-----------|--------------|
| [**Documentation Discipline**](../clean-code/documentation-discipline.md) | Delete rotting comments and dead code as you pass |
| [**DRY**](../architecture/dry.md) | Dedup the copies you touch, not the whole forest |
| [**Small Functions**](../clean-code/small-functions.md) | Extract-and-name is the commonest cleanup |
| [**KISS**](../clean-code/kiss.md) | Every cleanup is a small simplification |
