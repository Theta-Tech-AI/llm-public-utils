---
name: deslop-reliability-postels-law
description: Deslop principle — Postel's Law (Robustness Principle): Strict output, tolerant input; paranoid at security boundaries.
---

# Postel's Law (Robustness Principle)

> "Be conservative in what you send, be liberal in what you accept."
> — Jon Postel, RFC 793 (1981)

Be conservative in what you send and liberal in what you accept: generate strictly conformant output, but accept non-conformant input when the meaning is clear. This "tolerant reader" stance — ignore unknown fields rather than rejecting them — is what lets old clients keep working as servers evolve, and it powered the explosive growth of HTML, Unix pipes, SMTP, and JSON APIs.

```python
# ❌ Wrong - Strict parsing breaks when the API adds fields
def parse_user(data: dict) -> User:
    if set(data.keys()) != {"id", "name", "email"}:
        raise ValueError("Unexpected fields in response")
    return User(id=data["id"], name=data["name"], email=data["email"])

# ✅ Correct - Tolerant reader: require what you need, ignore the rest
def parse_user(data: dict) -> User:
    return User(id=data["id"], name=data["name"], email=data["email"])
```

But it has a dark side: liberal receivers mask sender bugs, "incorrect" behavior calcifies into a de facto standard (specification rot), and "reasonable" input can be crafted to exploit edge cases. The modern balance is to validate *required* fields strictly (fail-fast) while tolerantly ignoring unknown ones — and to be paranoid, not liberal, at security boundaries.

---

In relation to other principles, Postel's law:

| Principle | Relationship |
|-----------|--------------|
| [**Fail-Fast**](fail-fast.md) | Validate required fields strictly, tolerate unknown ones |
| [**Parse, Don't Validate**](../architecture/parse-dont-validate.md) | Tolerant reading is parsing that ignores what it doesn't need |
| [**Resilience & Graceful Degradation**](resilience.md) | Both keep systems working through an unreliable world |
| [**Principle of Least Privilege**](least-privilege.md) | At security boundaries, be paranoid, not liberal |
