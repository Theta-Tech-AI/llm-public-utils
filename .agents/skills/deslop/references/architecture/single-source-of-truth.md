---
name: deslop-architecture-single-source-of-truth
description: Deslop principle — Single Source of Truth: One authoritative location per datum; other copies derive from it.
---

# Single Source of Truth

> "There should be one—and preferably only one—obvious way to store a piece of information."

Every piece of data should have exactly one authoritative location; all other references derive from it. Where DRY targets duplicated *code and logic* within a codebase, SSoT targets duplicated *data storage* across systems and databases. The diagnostic question is simply "which copy is correct?" — if you can't answer immediately, the design is broken. Typical violations are the same foreign key stored in multiple databases, user data copied across services, and derived data with no clear owner. Duplication is fine when it's deliberate and synchronization isn't required: TTL caches, CQRS read-model denormalization, computed values, and cross-region replicas.
