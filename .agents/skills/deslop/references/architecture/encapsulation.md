---
name: deslop-architecture-encapsulation
description: Deslop principle — Encapsulation: Tell, don't ask; hide state behind behavior.
---

# Encapsulation

> "Ask not what an object knows; ask what it can do for you."

Bundle related data with the behavior that operates on it, and hide internal state behind an interface so it can change without breaking callers. The core habit is **tell, don't ask**: rather than querying an object's state and making decisions for it externally, command it to act and let it enforce its own rules.

```python
# ❌ Wrong - Asking for state, making decisions externally
def process_order(order):
    if order.get_status() == "pending":
        if order.get_total() > 100:
            discount = order.get_total() * 0.1
            order.set_total(order.get_total() - discount)
        order.set_status("processed")

# ✅ Correct - Telling the object what to do
def process_order(order):
    order.process()  # Order knows its own business rules
```

The tells of broken encapsulation: anemic data classes that are just fields plus getters/setters, accessor pairs that add no validation or computation, methods that return mutable internal state for callers to corrupt, and feature envy (a method that uses another class's data more than its own).
