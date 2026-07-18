---
name: deslop-reliability-resilience
description: Deslop principle — Resilience & Graceful Degradation: Retry, fall back, circuit-break; design for partial failure.
---

# Resilience & Graceful Degradation

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
