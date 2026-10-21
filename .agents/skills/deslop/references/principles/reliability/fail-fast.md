---
name: deslop-reliability-fail-fast
description: Deslop principle — Fail-Fast & Defensive Programming: Detect and report errors at the earliest possible moment.
---

# Fail-Fast & Defensive Programming

> "The best debugging is the debugging you never have to do because you found the problem immediately."
> — Jim Shore

Detect and report errors at the earliest possible moment, and never let invalid state propagate. Fail-fast means checking inputs at function entry and config at startup, then raising loudly — a clear error at the boundary beats silent corruption three layers downstream. Match the response to the error type: raise immediately on precondition violations, retry transient failures with backoff, fail permanently on deterministic ones, and assert invariants that should never be false. Once data has been validated at a boundary, trust it — don't re-validate inside.

```python
# ✅ Guard clauses - fail fast at entry
def process_order(order):
    if order is None:
        raise ValueError("order required")
    if not order.items:
        raise ValueError("items required")

# ✅ Config validation at startup
def __init__(self):
    self.key = os.getenv("API_KEY")
    if not self.key:
        raise ConfigError("API_KEY required")
```

---

In relation to other principles, fail-fast:

| Principle | Relationship |
|-----------|--------------|
| [**Guard Clauses**](../clean-code/guard-clauses.md) | Guard clauses are fail-fast at function entry |
| [**Design by Contract**](design-by-contract.md) | Contracts define what to check; fail-fast defines when |
| [**Decide, Don't Cope**](../clean-code/decide-dont-cope.md) | Rejecting at the boundary beats coping in the interior |
| [**Postel's Law**](postels-law.md) | Strict on required fields, tolerant of unknown ones |
