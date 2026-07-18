---
name: deslop-reliability-observability
description: Deslop principle — Observability & Transparency: Structured telemetry as your production debugger.
---

# Observability & Transparency

> "Observability is the ability to understand the internal state of a system by examining its external outputs."
> — Charity Majors

Make system behavior visible through structured telemetry — in distributed systems, the logs, metrics, and traces you emit are your primary debugger, because you can't attach one in production. Structure logs for machine parsing (JSON, key-value pairs, semantic prefixes), match log levels to intent, propagate correlation IDs (request IDs, trace IDs) so one request reads as a single story across services, and return operational metadata in responses. The anti-patterns are the ones that leave you blind: silently swallowed exceptions, opaque generic error messages, missing request context, over-logging inside tight loops — and the one that's actively dangerous, logging secrets.
