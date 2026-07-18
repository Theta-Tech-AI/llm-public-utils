---
name: deslop-reliability
description: Deslop principles, Part III: Reliability — Fail-Fast, Design by Contract, Postel's Law, Resilience & Graceful Degradation, Least Privilege, Boy Scout Rule, Observability.
---

# Part III: Reliability

> *Building robust, maintainable systems. These principles govern how code handles errors, maintains itself over time, and operates in production.*

**Contents:**

- [Robustness & Safety](#robustness--safety)
  - [Fail-Fast & Defensive Programming](#fail-fast--defensive-programming)
  - [Design by Contract](#design-by-contract)
  - [Postel's Law (Robustness Principle)](#postels-law-robustness-principle)
  - [Resilience & Graceful Degradation](#resilience--graceful-degradation)
  - [Principle of Least Privilege](#principle-of-least-privilege)
- [Maintainability & Operations](#maintainability--operations)
  - [Boy Scout Rule](#boy-scout-rule)
  - [Observability & Transparency](#observability--transparency)

---

## Robustness & Safety

*How does code handle the unexpected? Fail-Fast detects errors early, Design by Contract makes expectations explicit, Postel's Law enables interoperability, Resilience keeps systems running despite failures, and Principle of Least Privilege limits damage from breaches.*

---

### Fail-Fast & Defensive Programming

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

### Design by Contract

> "A software system is not a bunch of components thrown together. It is a construction of interacting elements, connected by clear contracts."
> — Bertrand Meyer

A contract makes the agreement between caller and routine explicit: the function guarantees its results (**postconditions**) *provided* the caller meets its requirements (**preconditions**), and **invariants** hold throughout the object's lifetime. Assertions are these contracts made executable — they document and verify at once. Under inheritance (Liskov substitution), a subtype may only *weaken* preconditions and only *strengthen* postconditions and invariants. DbC complements defensive programming rather than replacing it: trust-but-verify with contracts across internal interfaces where the caller is responsible for preconditions, and trust-no-one defensive checks at external boundaries.

---

### Postel's Law (Robustness Principle)

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

### Resilience & Graceful Degradation

> "In complex systems, failure is the normal state. Success is the special case that requires explanation."
> — Richard Cook

In any non-trivial system, partial failure is the normal state — design to keep operating through it rather than assuming success. Three pillars carry most of the load: **retry** transient failures with exponential backoff and jitter (`delay = min(base * 2^attempt + jitter, max)`) to recover without a thundering herd; **fall back** to cached or default data to degrade gracefully; and **protect** against cascades with circuit breakers (CLOSED → OPEN → HALF-OPEN) and timeouts on every external call. Only retry *transient* errors — an auth failure should fail fast, not loop.

```python
# Cascading fallback: personalized → cached → popular
def get_recommendations(user_id: str) -> list[Product]:
    try:
        return recommendation_service.get_personalized(user_id)
    except ServiceUnavailableError:
        cached = cache.get(f"recommendations:{user_id}")
        if cached:
            return cached
        return get_popular_items()  # Final fallback
```

---

### Principle of Least Privilege

> "Every program and every user of the system should operate using the least set of privileges necessary to complete the job."
> — Jerome Saltzer, *Protection and the Control of Information Sharing in Multics* (1974)

Every component should run with the minimum permissions its job requires — nothing more. Fewer permissions mean fewer entry points (smaller attack surface) and less damage when a breach happens (smaller blast radius); most breaches start with a privileged credential being abused, as Equifax (permissive DB access, no segmentation) and Target (an over-privileged HVAC vendor) both showed. The principle applies at every level: a config-reading function shouldn't have write access, a read path shouldn't hold a connection with `DROP TABLE`, a payment service shouldn't reach user profiles, and an IAM policy shouldn't say `Action: "s3:*", Resource: "*"`.

```python
# ❌ Wrong - Function accepts overly broad context
def send_notification(user: User, db: DatabaseAdmin):
    email = db.query(f"SELECT email FROM users WHERE id = {user.id}")
    # db could delete the entire users table!

# ✅ Correct - Function receives only what it needs
def send_notification(email: str):
    send_email(email, "Your notification...")  # Cannot touch the database
```

Default to deny and grant explicitly, separate credentials by function (read vs. write), time-bound elevated access, and audit regularly — permissions accumulate as roles change and "temporary" access becomes permanent. Watch for the verbal tells: "just give it admin, it's easier," "we'll lock it down later," "it needs that for debugging." Least privilege partners with Zero Trust: Zero Trust authenticates *who* is making a request, PoLP limits what that authenticated identity can *do*.

---

## Maintainability & Operations

*Code is a living artifact. The Boy Scout Rule keeps code improving incrementally with every change, while Observability & Transparency ensure you can understand what your systems are doing in production.*

---

### Boy Scout Rule

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

### Observability & Transparency

> "Observability is the ability to understand the internal state of a system by examining its external outputs."
> — Charity Majors

Make system behavior visible through structured telemetry — in distributed systems, the logs, metrics, and traces you emit are your primary debugger, because you can't attach one in production. Structure logs for machine parsing (JSON, key-value pairs, semantic prefixes), match log levels to intent, propagate correlation IDs (request IDs, trace IDs) so one request reads as a single story across services, and return operational metadata in responses. The anti-patterns are the ones that leave you blind: silently swallowed exceptions, opaque generic error messages, missing request context, over-logging inside tight loops — and the one that's actively dangerous, logging secrets.
