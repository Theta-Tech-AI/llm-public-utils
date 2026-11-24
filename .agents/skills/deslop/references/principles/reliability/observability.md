---
name: deslop-reliability-observability
description: Deslop principle — Observability & Transparency: structured, correlated telemetry as the production debugger; a failure is understood from the logs alone.
---

# Observability & Transparency

**Why this is slop:** behaviour nobody can see is behaviour nobody can defend, and without telemetry every production incident is a guess made from memory.

> "Observability is the ability to understand the internal state of a system by examining its external outputs."
> — Charity Majors

Make system behavior visible through structured telemetry — in distributed systems, the logs, metrics, and traces you emit are your primary debugger, because you can't attach one in production. Structure logs for machine parsing (JSON, key-value pairs, semantic prefixes), match log levels to intent, propagate correlation IDs (request IDs, trace IDs) so one request reads as a single story across services, and return operational metadata in responses. The anti-patterns are the ones that leave you blind: silently swallowed exceptions, opaque generic error messages, missing request context, over-logging inside tight loops — and the one that's actively dangerous, logging secrets.

---

In relation to other principles, observability:

| Principle | Relationship |
|-----------|--------------|
| [**Fail-Fast**](fail-fast.md) | Loud errors need somewhere to be heard |
| [**Resilience & Graceful Degradation**](resilience.md) | Fallbacks must be visible to be trusted |
| [**Principle of Least Privilege**](least-privilege.md) | The one active danger — logging secrets |
| [**Self-Documenting Code**](../clean-code/self-documenting-code.md) | Structured logs document runtime behavior |
| [**Every Request Has a Round-Trip Budget**](../data-layer/round-trips-per-request.md) | Two fields a request's line owes: its statement count, and a remainder so that the timed parts sum to the total |
