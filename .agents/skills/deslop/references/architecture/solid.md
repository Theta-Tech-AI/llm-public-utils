---
name: deslop-architecture-solid
description: Deslop principle — SOLID Principles: SRP, OCP, LSP, ISP, DIP — with code smells.
---

# SOLID Principles

> "SOLID principles are the foundation of good software design—they make code more maintainable, flexible, and testable."
> — Robert C. Martin (Uncle Bob)

| Letter | Principle | Core Idea | Code Smells |
|--------|-----------|-----------|-------------|
| **S** | Single Responsibility | One reason to change | Class name has "And"/"Manager", mixed I/O and logic, methods don't use most attributes |
| **O** | Open/Closed | Open for extension, closed for modification | `if/elif`/`isinstance()` chains on type, modifying existing code for each new variant |
| **L** | Liskov Substitution | Subtypes substitutable for base types | Subclass raises `NotImplementedError`, empty `pass` overrides, type checks before calls |
| **I** | Interface Segregation | Many specific interfaces over one general | Fat interfaces (10+ methods), implementations that `raise NotImplementedError` |
| **D** | Dependency Inversion | Depend on abstractions, not concretions | Direct instantiation in constructors, concrete imports in business logic, can't mock |

SOLID earns its keep in code that must evolve, but it's overhead in simple scripts, prototypes, and performance-critical paths. Don't create an interface for a class that will only ever have one implementation — wait for real, concrete callers to reveal the actual shape before designing a flexible abstraction around a hypothetical one. (This is distinct from DRY's duplication question above: designing a speculative interface before it's needed is premature abstraction, not a duplication-count threshold — see [Hunting Duplication](../duplication.md) for when *duplication itself* should be fixed.)
