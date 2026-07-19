---
name: deslop-architecture-idempotency
description: Deslop principle — Idempotency: Safe repetition; design for duplicate requests.
---

# Idempotency

> "An operation is idempotent if performing it multiple times has the same effect as performing it once."

An idempotent operation produces the same result whether run once or many times. Duplicate requests are inevitable in distributed systems — retries, at-least-once queues, impatient users — so design around them rather than assuming exactly-once delivery. The main techniques: idempotency keys, deterministic IDs derived from content, database upserts (`INSERT ... ON CONFLICT`), conditional writes with version numbers, and lease-based processing. Some operations are naturally idempotent (`GET`, `PUT`, `DELETE`, and assignment `x = 5`) while others are not (`x += 5`). The cheap test is to call it twice and confirm the state matches.

---

In relation to other principles, idempotency:

| Principle | Relationship |
|-----------|--------------|
| [**Generate Identity and Order in the Database**](../data-layer/database-identity.md) | The unique constraint IS the idempotency key |
| [**Resilience & Graceful Degradation**](../reliability/resilience.md) | Only idempotent operations are safe to retry |
| [**Command-Query Separation**](command-query-separation.md) | Queries are idempotent for free |
| [**Fail-Fast**](../reliability/fail-fast.md) | Deterministic failures should fail loudly, not be retried |
