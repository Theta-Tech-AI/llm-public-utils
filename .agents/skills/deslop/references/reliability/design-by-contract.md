---
name: deslop-reliability-design-by-contract
description: Deslop principle — Design by Contract: Explicit preconditions, postconditions, invariants.
---

# Design by Contract

> "A software system is not a bunch of components thrown together. It is a construction of interacting elements, connected by clear contracts."
> — Bertrand Meyer

A contract makes the agreement between caller and routine explicit: the function guarantees its results (**postconditions**) *provided* the caller meets its requirements (**preconditions**), and **invariants** hold throughout the object's lifetime. Assertions are these contracts made executable — they document and verify at once. Under inheritance (Liskov substitution), a subtype may only *weaken* preconditions and only *strengthen* postconditions and invariants. DbC complements defensive programming rather than replacing it: trust-but-verify with contracts across internal interfaces where the caller is responsible for preconditions, and trust-no-one defensive checks at external boundaries.
