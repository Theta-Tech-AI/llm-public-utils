---
name: deslop-architecture
description: Deslop principles, Part II: Architecture — DRY, Single Source of Truth, Separation of Concerns, Modularity, Encapsulation, Demeter, Orthogonality, DI, Composition, SOLID, CQS, Reusability, Parse Don't Validate, Immutability, Idempotency.
---

# Part II: Architecture

> *Structuring and designing systems. These principles govern how code is organized, how components relate, and how systems are designed for change.*

Each principle is a self-contained file; read every file when auditing this layer.

## Organization & Structure

*Where does this code belong? DRY and Single Source of Truth ensure knowledge lives in one place, Separation of Concerns defines boundaries between responsibilities, and Modularity packages those boundaries into self-contained units.*

| Principle | What it says |
|-------------|----------------|
| [DRY: Don't Repeat Yourself](architecture/dry.md) | One authoritative representation per piece of knowledge; fix at the 2nd occurrence |
| [Single Source of Truth](architecture/single-source-of-truth.md) | One authoritative location per datum; other copies derive from it |
| [Separation of Concerns](architecture/separation-of-concerns.md) | High cohesion, low coupling; one concern per part |
| [Modularity](architecture/modularity.md) | Deep modules, each hiding one design decision |

## Coupling & Dependencies

*How do components relate to each other? These principles minimize unhealthy dependencies. Encapsulation hides internal state, Law of Demeter limits knowledge of other objects, Orthogonality ensures independent change, Dependency Injection makes dependencies explicit, and Composition Over Inheritance favors flexible composition.*

| Principle | What it says |
|-------------|----------------|
| [Encapsulation](architecture/encapsulation.md) | Tell, don't ask; hide state behind behavior |
| [Law of Demeter](architecture/law-of-demeter.md) | Talk only to immediate friends; the one-dot rule |
| [Orthogonality](architecture/orthogonality.md) | Unrelated things change independently |
| [Dependency Injection](architecture/dependency-injection.md) | Inject dependencies; declare what, not how |
| [Composition Over Inheritance](architecture/composition-over-inheritance.md) | Has-a over is-a; black-box composition |

## Design Patterns & Conventions

*Proven approaches to common problems. SOLID provides five foundational OO principles, Convention Over Configuration reduces boilerplate through sensible defaults, Command-Query Separation distinguishes actions from queries, and Code Reusability addresses when and how to make code reusable.*

| Principle | What it says |
|-------------|----------------|
| [SOLID Principles](architecture/solid.md) | SRP, OCP, LSP, ISP, DIP — with code smells |
| [Convention Over Configuration](architecture/convention-over-configuration.md) | Sensible defaults with escape hatches |
| [Command-Query Separation](architecture/command-query-separation.md) | Methods either do or answer, never both |
| [Code Reusability](architecture/code-reusability.md) | Earn reuse from real callers; don't speculate on interfaces |

## Data & State

*How should data flow and behave? Parse Don't Validate transforms unstructured input into typed domain objects at boundaries. Immutability eliminates bugs by preventing state changes after creation. Idempotency ensures operations can be safely repeated.*

| Principle | What it says |
|-------------|----------------|
| [Parse, Don't Validate](architecture/parse-dont-validate.md) | Convert input to precise types once at the boundary |
| [Immutability](architecture/immutability.md) | Values fixed after creation; never mutate caller data |
| [Idempotency](architecture/idempotency.md) | Safe repetition; design for duplicate requests |
