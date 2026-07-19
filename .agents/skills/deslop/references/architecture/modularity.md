---
name: deslop-architecture-modularity
description: Deslop principle — Modularity: Deep modules, each hiding one design decision.
---

# Modularity

> "Every module is characterized by its knowledge of a design decision which it hides from all others."
> — David Parnas

Divide software into independent components, each encapsulating one responsibility and hiding its implementation behind a well-defined interface. The Parnas principle is to decompose by **design decisions likely to change**, so each module hides one such decision. Aim for high cohesion (elements within a module belong together) and low coupling (modules depend only on each other's interfaces, not internals). Prefer **deep** modules — a simple interface hiding complex implementation — over **shallow** ones that expose a complex interface while hiding little. A "God module" that does everything encapsulates nothing.

---

In relation to other principles, modularity:

| Principle | Relationship |
|-----------|--------------|
| [**Separation of Concerns**](separation-of-concerns.md) | Decompose by concern, then package into modules |
| [**Encapsulation**](encapsulation.md) | Information hiding is what makes a module deep |
| [**Cognitive Load**](../clean-code/cognitive-load.md) | Deep modules lower load; shallow ones raise it |
| [**Small Functions**](../clean-code/small-functions.md) | Modularity at file granularity, small functions at logic granularity |
