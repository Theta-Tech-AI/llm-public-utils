---
name: deslop-architecture-orthogonality
description: Deslop principle — Orthogonality: Unrelated things change independently.
---

# Orthogonality

> "Eliminate effects between unrelated things. Design self-contained components: independent, and with a single, well-defined purpose."
> — Andy Hunt & Dave Thomas

Two components are orthogonal when a change in one doesn't affect the other — like a helicopter with coupled controls, non-orthogonal code means fixing one bug pops up two more elsewhere. Coupling is viral: a little leads to more. Measure orthogonality by how many places must change when one requirement changes. The usual culprits are global state, business logic coupled to a specific database dialect, presentation mixed with computation, and objects that accrete unrelated responsibilities. Dependency injection, abstract interfaces, and avoiding global state all push toward independence.

---

In relation to other principles, orthogonality:

| Principle | Relationship |
|-----------|--------------|
| [**Separation of Concerns**](separation-of-concerns.md) | Orthogonality is separation measured by the blast radius of change |
| [**Modularity**](modularity.md) | Self-contained modules are the vehicle |
| [**Dependency Injection**](dependency-injection.md) | DI removes a whole axis of coupling |
| [**DRY**](dry.md) | Duplicated knowledge is non-orthogonal by definition — one change needs N edits |
