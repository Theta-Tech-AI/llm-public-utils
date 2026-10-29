---
name: deslop-architecture-layering-violations
description: Deslop principle — Layering Violations: a dependency that runs against the intended arrows, made invisible because no gate checks the direction.
---

# Layering Violations

> "No cycles on the application module level — the dependencies between modules have to form a directed acyclic
> graph. Efferent module access via API packages only."
> — Spring Modulith, *Verifying Application Module Structure*

Layers are a promise: a lower layer may be replaced without a higher one noticing, because **knowledge flows one
way**. A violation is a single import that runs against the arrows — the domain rule importing the HTTP request
object, the repository importing the serializer, a model importing the ORM session, one feature importing another's
internals. No individual line looks wrong; that is why the erosion succeeds. It accumulates until the "layer" is a
folder name, the swap it promised is impossible, and every test that touches the rule needs a web framework
installed. Two findings, always reported together: **the reversed dependency, and the absence of anything that would
have refused it.**

```python
# ❌ the rule knows the framework, the database and the wire format
# domain/order.py
from flask import request                      # HTTP into the domain
from infrastructure.db import Session          # persistence into the rule
from api.serializers import OrderJSON          # presentation into the rule

def apply_discount(order):
    order.discount = request.json["discount"]  # the arrow reversed, three times
    Session().merge(order)
    return OrderJSON.dump(order)
```

```python
# ✅ the domain knows itself; the edges translate in each direction
# domain/order.py
def apply_discount(order: Order, discount: Discount) -> Order: ...

# api/orders.py — the adapter: parse at the edge, call inward, serialise outward
def discount_route(order_id: str, payload: dict):
    discount = Discount.parse(payload)         # the edge does the untrusted work
    order = orders.apply(order_id, discount)   # one call inward, domain types only
    return to_json(order)                      # presentation stays at the edge
```

Making the arrows **enforceable** is part of the repair, not a nicety: an import-linter contract, an ArchUnit or
Spring Modulith rule, `dependency-cruiser`, or a hand-written check in CI. An architecture asserted only in a README
has already eroded; the gate is what keeps the tidy-up from being undone next sprint.

## What this adds over its neighbours

[Separation of Concerns](separation-of-concerns.md) says where code belongs; [Modularity](modularity.md) says how to
package it; [Dependency Injection](dependency-injection.md) says dependencies should be declared. None of them asks
the question this file asks: **which way does knowledge flow, and what refuses a violation?** The direction and its
enforcement are the missing third leg.

## The tests

1. **Arrow test** — write the intended arrows down in one sentence (`api → application → domain`; `infrastructure →
   domain`, never back). For each dependency that crosses a module line, does it point with an arrow?
2. **Cycle test** — the module graph must be acyclic. A cycle means two modules are one module in disguise, or the
   part they both need has no owner.
3. **Import-nothing test** — grep the lowest layer for imports of anything above it (framework, HTTP, DB session,
   serializer, logger). Zero is the only pass; each hit is a separate finding.
4. **Internal-access test** — does one module import another's internal file rather than its public surface? Cross
   through a seam, or the seam does not exist.
5. **Gate test** — is the direction checked by a machine on every push? "No" converts every finding above from an
   accident into a policy, and is filed as its own defect.

## The family: one disease, many costumes

| Artifact | The arrow it breaks | The owner that was missing |
|---|---|---|
| domain imports `flask.request` | presentation → domain, reversed | an adapter that parses the request |
| repository returns a serialised DTO | persistence → presentation | a mapper at the edge |
| migration imports an application service | infrastructure → application | a script at the composition root |
| `billing` imports `orders.internal.models` | module → module internals | orders' public surface |
| `a → b → a` between two packages | the acyclic rule | the shared concept has no home |

## The repair

**Move the knowledge to its owner, then let a machine hold the line.** The edge adapter does the translation in both
directions; shared lower-level value types live in their own dependency-free module; each module exposes one public
surface. Then add the gate — a contract file in CI — in the same change, because an unenforced arrow is a temporary
arrangement.

## Boundaries

A **shared kernel** of value types (money, identifiers, timestamps) is legitimate even though everyone imports it, as
long as it imports nothing of the app. Hexagonal, onion, clean and modulith styles differ in vocabulary, not in the
direction-plus-acyclic core; pick the vocabulary of the codebase. Prototypes, one-file scripts and a single-module
service have no layers to violate. And a violation inside one module's private files is usually just an untidy
module — the finding needs a module line to cross.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Information hiding | David Parnas (1972) | Why modules hide one design decision — the reason direction matters. |
| The Dependency Rule | Robert C. Martin, *Clean Architecture* | Dependencies point inward; stated as an invariant of the style. |
| Module verification | Spring Modulith; ArchUnit; jMolecules | Machine-checked arrows — the gate this file insists on. |
| Architecture erosion / cyclic dependency | Detecting and measuring layering violations (IEEE, 2006); *Architecture Anti-patterns: Automatically Detectable?* (TSE 2019) | The empirical case that violations accumulate and predict bug- and change-proneness. |

**What is this library's own:** pairing the reversed dependency with the missing gate as a single finding, so each
violation carries its own prevention.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Separation of Concerns**](separation-of-concerns.md) | Decides where code belongs; this decides what it may then see. |
| [**Modularity**](modularity.md) | Deep modules with one surface are what an arrow can be drawn to. |
| [**Dependency Injection**](dependency-injection.md) | How a module receives what it needs without reaching. |
| [**Shotgun Surgery**](shotgun-surgery.md) | Feature-first layout removes the crossings a layer-first tree creates. |
| [**Errors at the Boundary**](../reliability/errors-at-the-boundary.md) | Translation at a seam — the error-side instance of the same rule. |

## Summary

1. **Arrows are the architecture; folders are only labels.**
2. **Every reversed dependency is filed with the missing gate** — unenforced direction is a temporary arrangement.
3. **Cycles mean two modules are one, or a shared concept has no home.**
4. **Translating at the seam is how the edge stays outside** — parsing in, serialising out.
5. **A shared kernel is fine; it must import nothing of your own.**
