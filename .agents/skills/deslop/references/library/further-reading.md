---
name: deslop-further-reading
description: Bibliography for the deslop principles — foundational texts, seminal articles, online resources, and concept attribution.
---

# References

## Foundational Texts

Essential books that shaped modern software design thinking.

| Book | Author(s) | Key Contribution |
|------|-----------|------------------|
| *The Pragmatic Programmer* | Andy Hunt & Dave Thomas | Practical heuristics including DRY, orthogonality, tracer bullets, and "Tell Don't Ask" |
| *Clean Code* | Robert C. Martin | Function size, naming, and the Single Responsibility Principle |
| *A Philosophy of Software Design* | John Ousterhout | Deep vs. shallow modules, complexity as the root problem, strategic vs. tactical programming |
| *Design Patterns* | Gang of Four (Gamma, Helm, Johnson, Vlissides) | 23 reusable OO patterns; established patterns vocabulary |
| *Object-Oriented Software Construction* | Bertrand Meyer | Design by Contract, Command-Query Separation, Open-Closed Principle |
| *Refactoring* | Martin Fowler | Systematic code improvement techniques; code smells catalog |
| *Working Effectively with Legacy Code* | Michael Feathers | Seams, characterization tests, safely changing untested code |
| *Domain-Driven Design* | Eric Evans | Ubiquitous language, bounded contexts, strategic design |

## Seminal Articles & Essays

Influential writings that introduced or crystallized important concepts.

| Article | Author | Year | Key Idea |
|---------|--------|------|----------|
| [Parse, Don't Validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) | Alexis King | 2019 | Transform unstructured data into types that prove validity; let the type system enforce invariants |
| [Boolean blindness](https://shreevatsa.wordpress.com/2015/01/31/boolean-blindness/) | Dan Licata, recorded by Robert Harper | 2013–2015 | A Boolean carries no information beyond its value — using it means remembering the provenance you already erased |
| [Stringly typed](https://github.com/SteveDunn/StringlyTyped#readme) | folk usage, paired with Fowler's primitive obsession | 2010s | Carrying a domain concept as `str` — the primitive-obsession pejorative |
| [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) | Sandi Metz | 2016 | "Duplication is far cheaper than the wrong abstraction"; prefer inline code over premature DRY |
| [Cognitive Load is What Matters](https://github.com/zakirullin/cognitive-load) | Artem Zakirullin | 2023 | Minimize mental effort required to understand code; endorsed by Rob Pike, Andrej Karpathy |
| [Tell Don't Ask](https://martinfowler.com/bliki/TellDontAsk.html) | Martin Fowler | 2013 | Tell objects what to do rather than asking for data and acting on it |
| [Four Rules of Simple Design](https://martinfowler.com/bliki/BeckDesignRules.html) | Kent Beck | ~1990s | (1) Passes tests, (2) Reveals intention, (3) No duplication, (4) Fewest elements |
| [Law of Demeter](https://www2.ccs.neu.edu/research/demeter/papers/law-of-demeter/oopsla88-law-of-demeter.pdf) | Karl Lieberherr et al. | 1987 | Only talk to your immediate friends; minimize coupling chains |

## Online Resources

Living references for patterns, principles, and refactoring techniques.

- [Martin Fowler's Bliki](https://martinfowler.com/bliki/) — Authoritative essays on patterns, refactoring, and architecture
- [Refactoring Guru](https://refactoring.guru/) — Visual catalog of design patterns and refactoring techniques
- [DevIQ Principles](https://deviq.com/principles/) — Concise summaries of software development principles
- [c2 Wiki (Cunningham & Cunningham)](http://wiki.c2.com/) — The original patterns wiki; historical discussions on OO design
- [Source Making](https://sourcemaking.com/) — Design patterns, anti-patterns, and refactoring catalog

## Concept Attribution

Origins of specific principles referenced in this document.

| Concept | Origin |
|---------|--------|
| **KISS** | U.S. Navy, 1960s; popularized by Kelly Johnson (Lockheed Skunk Works) |
| **YAGNI** | Extreme Programming (Kent Beck, Ron Jeffries), late 1990s |
| **DRY** | *The Pragmatic Programmer* (Hunt & Thomas), 1999 |
| **SOLID** | Robert C. Martin, early 2000s (acronym coined by Michael Feathers) |
| **Separation of Concerns** | Edsger Dijkstra, 1974 |
| **Design by Contract** | Bertrand Meyer, 1986 (Eiffel language) |
| **Postel's Law** | Jon Postel, RFC 761 (TCP), 1980 |
| **Deep Modules** | John Ousterhout, *A Philosophy of Software Design*, 2018 |
| **Cognitive Load** | Psychology (John Sweller, 1988); applied to code by Zakirullin, 2023 |
| **Boolean blindness** | Dan Licata, CMU (as a PhD student); recorded by Robert Harper; catalogued as a smell by Jerzyk, 2022 |
| **Primitive obsession / stringly typed** | Martin Fowler, *Refactoring*, 1999; "stringly typed" as the pejorative for the string case |
| **A Helper That Must Exist Is an Architecture Finding** | This library (2026) — the architectural framing, the six-test audit, and the owner-before-type ordering; the type-level smells are the named concepts above |
| **Normalization / Normal Forms** | Edgar F. Codd, 1970 (relational model) |

## The data layer

The principles under [data-layer/](data-layer/) rest on four sources, and each file cites the one it leans on:

- **PostgreSQL manual** — [*Constraints*](https://www.postgresql.org/docs/current/ddl-constraints.html) (§5.5,
  including `NOT VALID` / `VALIDATE CONSTRAINT`), [*Indexes*](https://www.postgresql.org/docs/current/indexes.html)
  (multicolumn, ORDER BY, partial, index-only scans, examining usage),
  [*Generated Columns*](https://www.postgresql.org/docs/current/ddl-generated-columns.html), and
  [*Performance Tips*](https://www.postgresql.org/docs/current/performance-tips.html).
- **Markus Winand, *Use The Index, Luke*** — <https://use-the-index-luke.com/> — the join algorithms
  (nested loops / hash / sort-merge and what each wants from an index), the right column order in multi-column
  indexes, and the N+1 pattern as a nested loop run in the client.
- **Laurenz Albe, *Foreign key indexing and performance in PostgreSQL*** —
  <https://www.cybertec-postgresql.com/en/index-your-foreign-key/> — the target side is auto-indexed, the
  referencing side is not, and a parent-side delete scans the child table without one.
- **E. F. Codd** — *A Relational Model of Data for Large Shared Data Banks* (1970) and *Further Normalization of
  the Data Base Relational Model* (1971), summarized at
  <https://en.wikipedia.org/wiki/Database_normalization> — the normal forms and the insert / update / delete
  anomalies they prevent.
