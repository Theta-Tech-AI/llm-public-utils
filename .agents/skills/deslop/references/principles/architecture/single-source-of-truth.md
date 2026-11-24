---
name: deslop-architecture-single-source-of-truth
description: Deslop principle — Single Source of Truth: One authoritative location per datum; other copies derive from it.
---

# Single Source of Truth

**Why this is slop:** a datum stored in more than one place cannot say which copy is authoritative, so the copies diverge quietly and the bug appears wherever the stale one is read.

> "There should be one—and preferably only one—obvious way to store a piece of information."

Every piece of data should have exactly one authoritative location; all other references derive from it. Where DRY targets duplicated *code and logic* within a codebase, SSoT targets duplicated *data storage* across systems and databases. The diagnostic question is simply "which copy is correct?" — if you can't answer immediately, the design is broken. Typical violations are the same foreign key stored in multiple databases, user data copied across services, and derived data with no clear owner. **Check disagreement, not resemblance:** two owners that already give different answers on one input (a threshold, a status mapping, a default) are a bug ([one fact, many owners](../../patterns/one-fact-many-owners.md)). Name the one owner before fixing any copy. Duplication is fine when it's deliberate and synchronization isn't required: TTL caches, CQRS read-model denormalization, computed values, and cross-region replicas.

---

In relation to other principles, single source of truth:

| Principle | Relationship |
|-----------|--------------|
| [**DRY**](dry.md) | DRY targets duplicated logic; SSoT targets duplicated data storage |
| [**Normalize to a Single Source of Truth**](../data-layer/normalization.md) | SSoT applied to schema |
| [**Immutability**](immutability.md) | Derived copies are safe only when deliberately unsynced, never hand-maintained |
| [**Every Request Has a Round-Trip Budget**](../data-layer/round-trips-per-request.md) | One owner is not one read: when every function asks the owner for itself, one request reads the same row many times |
