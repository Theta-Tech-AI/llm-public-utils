---
name: deslop-architecture-modularity
description: Deslop principle — Modularity: Deep modules, each hiding one design decision — and a hop that adds no policy is a shallow module, not a seam.
---

# Modularity

> "Every module is characterized by its knowledge of a design decision which it hides from all others."
> — David Parnas

Divide software into independent components, each encapsulating one responsibility and hiding its implementation behind a well-defined interface. The Parnas principle is to decompose by **design decisions likely to change**, so each module hides one such decision. Aim for high cohesion (elements within a module belong together) and low coupling (modules depend only on each other's interfaces, not internals). Prefer **deep** modules — a simple interface hiding complex implementation — over **shallow** ones that expose a complex interface while hiding little. A "God module" that does everything encapsulates nothing.

## The shallow module, in practice: a hop with no policy

The shallow module has a body you can point at, and it is the commonest wrapper in real code: a method that forwards
its arguments unchanged, a service that only calls its repository, a module that re-exports a library, a middleware
that calls `next()` and does nothing else. It pays for itself with a name and returns nothing — the reader stops at the
hop looking for a decision that is not there, the real dependency is concealed one level down, and every parameter is
threaded twice. These are cheap to write, which is why they accumulate after every refactor that was not finished.

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

Where a hop **does** carry policy — authorisation, translation, a transaction boundary, retries, caching, metrics, a
port with two implementations — keep exactly one such hop and say what it adds. The defect is the hop that adds
nothing, or the same policy carried twice.

### The tests

1. **Policy test** — say in one sentence what the hop adds. "Nothing" is the finding; identical forwarding signatures
   are the fingerprint.
2. **Reverse test** — delete it and repair the call sites. If the repair is a rename, nothing was lost. If it is the
   same logic appearing at N call sites, the wrapper was hiding an ownerless rule.
3. **Double-carry test** — is another layer already doing it (a middleware, a decorator, the ORM's unit of work)?
   Then one of the two is redundant even though each looks justified alone.
4. **Path-length test** — count the hops from the entry point to the work; each must be nameable in a sentence. An
   unnamed hop is the finding, and the count is what the indirection costs the reader.

### Boundaries

**Proxy, Decorator, Adapter and Facade** create these layers deliberately, and a hop with a named policy is correct at
any count. A port that exists so a test can substitute a fake is carrying a policy — replaceability — and the question
is whether its interface is narrow enough to be specifiable. A thin public façade over internals is a stability
promise, and the composition root assembling collaborators is doing the work of the composition root. Note also that
[Law of Demeter](law-of-demeter.md) *manufactures* these wrappers when applied without limit — which is how most of
them appear.

### Prior art

| Term | Source | How it relates |
|---|---|---|
| Deep vs shallow modules | John Ousterhout, *A Philosophy of Software Design* | The structural form of the rule this section instruments. |
| Middle Man, Lazy Class | Refactoring.Guru (Fowler's catalogue) | Name the wrapper smell, the *Remove Middle Man* refactoring, and the legitimate exceptions. |
| Overzealous message-chain elimination | Refactoring.Guru, *Middle Man*, "reasons for the problem" | How the wrappers get created in the first place. |

**What is this library's own:** the policy test as a one-sentence decidable instrument, and the path-length count as
the measure of what an indirection costs.

---

In relation to other principles, modularity:

| Principle | Relationship |
|-----------|--------------|
| [**Separation of Concerns**](separation-of-concerns.md) | Decompose by concern, then package into modules |
| [**Encapsulation**](encapsulation.md) | Information hiding is what makes a module deep |
| [**Law of Demeter**](law-of-demeter.md) | Its over-application manufactures the shallow modules above |
| [**Dependency Injection**](dependency-injection.md) | Injection removes the wrappers that exist only to hide wiring |
| [**Cognitive Load**](../clean-code/cognitive-load.md) | Deep modules lower load; shallow ones raise it |
| [**Small Functions**](../clean-code/small-functions.md) | Modularity at file granularity, small functions at logic granularity |
