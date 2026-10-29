---
name: deslop-architecture-pass-through-wrappers
description: Deslop principle — Pass-Through Wrappers: an indirection that adds a name to the call path and no policy, hiding where the decision actually lives.
---

# Pass-Through Wrappers

> "If a class performs only one action, delegating work to another class, why does it exist at all?"
> — Refactoring.Guru, *Middle Man*

Every hop in a call path must pay for itself. A **pass-through wrapper** — a method that forwards its arguments
unchanged, a service that only calls its repository, a module that re-exports a library, a middleware that calls
`next()` and does nothing else — pays with a name and returns nothing. That is not harmless tidiness: the reader
stops at the hop looking for the decision, the real dependency is concealed one level down, and every parameter must
be threaded twice, so a change to the callee's signature is a change to the wrapper as well. Wrappers are the
cheapest code to write, which is why they accumulate after every refactor that was not finished.

```python
# ❌ three hops, and no decision anywhere among them
class OrderRepository:
    def __init__(self, session): self._s = session
    def get(self, order_id): return self._s.get(Order, order_id)      # forwards, unchanged

class OrderService:
    def __init__(self, repo): self._repo = repo
    def get_order(self, order_id): return self._repo.get(order_id)    # forwards, unchanged

def route(order_id):
    return OrderService(OrderRepository(Session())).get_order(order_id)  # builds what it was given
```

```python
# ✅ one seam that names the decision, and no empty hop
class OrderStore:                       # the real seam: a store, not a session
    def __init__(self, session): self._s = session
    def get(self, order_id: OrderId) -> Order | None:
        return self._s.get(Order, order_id)      # the only place a session is touched

def route(order_id: str):
    order = OrderStore(Session()).get(OrderId.parse(order_id))
    return to_json(order)               # the edge's own policy, stated once
```

Where a hop **does** carry policy — authorisation, translation, a transaction boundary, retries, caching, metrics —
keep exactly one such hop and say what it adds. The defect is the hop that adds nothing, or the same policy carried
twice.

## What this adds over its neighbours

[Modularity](modularity.md) prefers deep modules over shallow ones, which is the theory.
[Law of Demeter](law-of-demeter.md) *creates* these wrappers when applied without limit — which is precisely how most
of them appear. This file supplies the decidable test that separates a legitimate seam from an empty one: **name the
policy.**

## The tests

1. **Policy test** — say in one sentence what the wrapper adds (a check, a translation, a choice, a guarantee, a
   measurement). "Nothing" is the finding; "it is what the interface requires" is a finding of a different kind.
2. **Signature test** — are its parameters the wrapped call's parameters, in the same order, unchanged? Identical
   forwarding is the fingerprint.
3. **Reverse test** — delete it and repair the call sites. If the repair is a rename, nothing was lost and the file
   should go. If the repair is the same logic appearing at N call sites, the wrapper was hiding an ownerless rule.
4. **Double-carry test** — is another layer already doing this (a middleware, a decorator, the ORM's unit of work)?
   Then one of the two is redundant even though each looks justified alone.
5. **Path-length test** — count the hops from the entry point to the work. Each one must be named in a sentence; an
   unnamed hop is the finding, and the count is the cost.

## The family: one disease, many costumes

| Artifact | The policy it should have carried | What to do instead |
|---|---|---|
| `class XService` wrapping one repository call | none | inject the repository at the edge, delete the service |
| module that re-exports a library (`from pkg import *`) | none | import the library at the use site |
| `middleware` calling `next()` after logging only | the log line, not the call | keep it, and let the log be its only job |
| DTO ↔ model mapper with same-named fields | none | map at the seam where the shapes genuinely differ |
| `get_foo()` returning `self.foo` | none | expose the value, or make the field the interface |

## The repair

**Either give the hop a policy or delete it.** Deleting is usually right: inline the forwarding call at its call
sites, let the dependency be injected where it is needed, and remove the wrapper from the module's public surface in
the same change. Where a hop must remain — a port with two implementations, a boundary that translates — state its
policy in one line so the next reader does not repeat this investigation.

## Boundaries

Do not confuse a seam with a middle man. **Proxy, Decorator, Adapter and Facade** create these layers deliberately
(Refactoring.Guru says so explicitly), and a hop with a named policy is correct at any count. A port that exists so a
test can substitute a fake is carrying a policy — replaceability — and the question is whether its interface is
narrow enough to be specifiable. A public library's thin façade over internals is a stability promise. And when the
"wrapper" is the composition root assembling its collaborators, it is doing the work of the composition root.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Middle Man, Lazy Class | Refactoring.Guru (Fowler's catalogue) | Names the smell, the *Remove Middle Man* refactoring, and the legitimate exceptions. |
| Shallow module | John Ousterhout, *A Philosophy of Software Design* | The structural version: interface complexity not paid for by hidden complexity. |
| Overzealous message-chain elimination | Refactoring.Guru, *Middle Man*, "reasons for the problem" | How the wrappers get created in the first place. |

**What is this library's own:** the policy test as a one-sentence decidable instrument, and the path-length count as
the measure of what the indirection costs.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Modularity**](modularity.md) | Deep vs shallow modules — the theory this file operationalises. |
| [**Law of Demeter**](law-of-demeter.md) | Its over-application manufactures these wrappers. |
| [**Dependency Injection**](dependency-injection.md) | Injection removes the need for constructing wrappers that hide wiring. |
| [**One Logical Unit, One Home**](one-logical-unit-one-home.md) | A wrapper often hides that the unit lives elsewhere already. |
| [**Layering Violations**](layering-violations.md) | A legitimate seam must be enforced by direction, not by proximity. |

## Summary

1. **Every hop must name its policy** — a sentence, or it goes.
2. **Identical forwarding signatures are the fingerprint.**
3. **Deleting a wrapper converts hidden reliance into a visible call site.**
4. **Proxy, Decorator, Adapter and port seams are legitimate** — decide with the policy test, not with a rule.
5. **Count the path to the work** — that count is what the indirection costs the reader.
