---
name: deslop-patterns-index
description: Index of the recurring diagnostic patterns a very large audit measured, and the rule that separates a pattern from a principle.
---

# Patterns: index

Read this index before the pattern files your lens lists, the way a reading opens a category index before its principles. Each pattern has its own file under `patterns/`.

## Pattern versus principle

- A **principle** is a normative rule about **one mechanism with one owner**. A finding is charged under exactly one principle, and each principle belongs to exactly one lens.
- A **pattern** is a **recurring diagnostic shape** seen across many findings. It spans several principles and several lenses, names the repair shape, and points at the principle that owns each mechanism. It is **never charged by itself**: file each instance under the owning principle.
- A reader uses a pattern as a **tell while reading** ("this is one fact with a second owner — name the owner"). Consolidation uses it as the **L1 axis** next to the L2 axis (the fact) to cluster concerns into themes with one owner: see [consolidation](stages/consolidation.md#5-classify-then-theme-the-cross-concerns).
- Every pattern's repair has the same order: **name the owner first, route every consumer through it, delete the copies in the same change.** Two copies that cannot disagree (generated code, a deliberately independent module) are a guardrail case: see [when-to-relax](readings/when-to-relax.md).

## The patterns

**Measured on** a coverage pass over a ~236k-line web application (Python API, TypeScript SPA overlaid on an upstream framework, ops scripts): 332 read-only cells produced 9,407 findings; verification dropped 32%; the rest collapsed into 2,136 concerns (1,023 local, 582 **cross** — the right fix needs one owner across modules or layers — and 531 design or migration changes). Counts are heuristic text classes over the quoted evidence and **overlap**; never add them. "High" is the verified high-severity count.

| Pattern | Essence | Caught most by | Findings / high |
|---|---|---|---|
| [one-fact-many-owners](patterns/one-fact-many-owners.md) | two places decide one thing and already disagree | duplication, boundaries | 705 / 171 (40% of all high) |
| [declaration-vs-enforcement](patterns/declaration-vs-enforcement.md) | a name, comment or route promises what no line keeps | guarantees, legibility | 785 / 64 |
| [consumer-redecides-producer](patterns/consumer-redecides-producer.md) | a client re-derives what the producer already decided | parsing | 736 / 54 |
| [vocabulary-drift](patterns/vocabulary-drift.md) | one closed set spelled in several layers, members differing | coupling, data-integrity | 584 / 47 |
| [absence-equals-failure](patterns/absence-equals-failure.md) | one value for "nothing there" and "the read failed" | parsing, guarantees | 433 / 33 |
| [grammar-without-owner](patterns/grammar-without-owner.md) | one input format (identifier, config value) taken apart by several parsers | parsing | 427 / 37, plus 114 / 12 for the config variant |
| [fork-instead-of-extension](patterns/fork-instead-of-extension.md) | a downstream copy of an upstream module drifts | duplication | 211 / 40 |
| [one-sided-contract](patterns/one-sided-contract.md) | one end of an agreement has no partner | parsing, guarantees | 123 / 16 |
| [unnamed-decision](patterns/unnamed-decision.md) | a question the design never asked, answered differently wherever the code met it | duplication, parsing | not counted in the field run |

The `shape` and query lenses carry no pattern: the field data showed none that they catch most.

## Why these and not more

A pattern gets its own file only when **both** its structural tell **and** its repair shape differ from every sibling pattern's and from the principle that owns its mechanism. Two shapes in the original catalogue failed that bar:

- **Config parsed twice with different rules** — folded into [grammar-without-owner](patterns/grammar-without-owner.md) as a variant. Its tell (one input, several parsers that disagree) and its repair (one parser, typed output) are the identifier case with an environment value as the input. Its numbers stay with the variant.
- **Lifecycle in a column** (a nullable self-reference or flag written from many modules) — dropped as a pattern. Its tell (count the writers and readers) and repair (named states, one transition, a constraint) are already the content of [implicit-state-machine](principles/architecture/implicit-state-machine.md); the principle now carries the prevalence (181 findings, 23 high) and the pattern file would only restate it.

One shape was added after the field run and passes the same bar: [unnamed-decision](patterns/unnamed-decision.md). Its tell differs from *one fact, many owners* (no copied text or shared name to search for; the sites are found by asking one question of every route) and so does its repair (decide first, because no existing answer is the original).
