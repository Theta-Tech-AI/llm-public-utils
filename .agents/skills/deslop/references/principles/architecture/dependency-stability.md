---
name: deslop-architecture-dependency-stability
description: Deslop principle — Depend in the Direction of Stability: a unit that changes rarely importing one that changes often, so every change to the volatile side forces work in the stable side.
---

# Depend in the Direction of Stability

A dependency is a promise to be disturbed. The question worth asking of every import edge is not only
*which layer* it points to but **how often the far end moves**: a unit that changes yearly and depends on
one that changes weekly has handed its own stability to the other side. Every release of the volatile unit
becomes a candidate change in the stable one, for reasons that are the volatile unit's alone.

This is a different defect from a layering violation, and it survives in a codebase whose layers are
otherwise clean. The arrows can point the right *way* — domain does not import the HTTP layer — while still
pointing at things that move at the wrong **rate**: the business rule importing the vendor SDK, the pricing
policy importing the current endpoint schema, the long-lived core importing a feature-toggle reader that a
product team rewrites every sprint.

```python
# ❌ the most stable rule in the system imports the most volatile thing in it
from integrations.exchange_rate_v2 import fetch_rate        # vendor API shape, retried weekly

def convert(amount, currency, on):
    rate = fetch_rate(currency, on)                          # domain rule now tracks a vendor schema
    return amount * rate
```

```python
# ✅ the stable side declares what it needs; the volatile side satisfies it at the edge
class RateSource(Protocol):                                  # domain's own vocabulary, no vendor in it
    def rate(self, currency: str, on: date) -> Decimal: ...

def convert(amount: Decimal, currency: str, on: date, source: RateSource) -> Decimal:
    return amount * source.rate(currency, on)

# integrations/rates.py — the only file that knows the vendor, and the only one a vendor bump touches
```

The cost is cumulative rather than visible: each individual import is reasonable when it is written, the
vendor version moves, and the domain file acquires an edit "just for the upgrade" — the first of many. Two
or three such edges turn a stable module into a file that changes for other people's reasons, which is what
[Orthogonality](orthogonality.md) counts as a reason to change.

## What this adds over its neighbours

[Layering Violations](layering-violations.md) judges the **direction of the arrows** — an HTTP context in a
domain rule, a feature reaching another's internals. This judges the **rate at each end**, which no layering
diagram shows: both files can sit in the correct layer and still be wired against stability.
[Dependency Injection](dependency-injection.md) is the *mechanism* by which the inversion is done, and says
nothing about which edges deserve it. SOLID's dependency inversion says *depend on abstractions* — a shape,
not a rate: an abstraction owned by the volatile unit gives you none of the benefit.
[Separation of Concerns](separation-of-concerns.md) reads where one change lands across folders; this reads
where change arrives from outside and which files it drags with it.

## The tests

1. **Reason test** — the criterion, and it needs no tooling. Enumerate the far end's reasons to change for
   its *own* purposes (a vendor version, a wire format, an endpoint shape, a product experiment). If any of
   them obliges the near end to change, the edge is wrong regardless of how tidy the import looks.
2. **Change-rate test** — evidence for ranking, not the criterion. Compare how often the two files moved over
   the last N commits (`git log --oneline -- <path> | wc -l`, and `git log --name-only` to see them move
   together); an edge from low churn to high churn with no port between them is a candidate. Report the
   counts, and let the reason test decide.
3. **Fan-in test** — how many modules import the volatile unit. A volatile unit with high fan-in is a
   multiplier: one vendor bump, N edits. The number is the blast radius, not the finding.
4. **Bypass test** — does a port already exist for this volatile unit? Then the finding is the importer that
   reached past it, and that is a live defect rather than a design smell.
5. **Ownership test** — for a stable unit importing a volatile one, name the file whose job it is to track the
   vendor. "Every file that uses it" means nobody owns it.
6. **Reverse test** — delete the import and repair the call sites. If the repair is copying the volatile
   side's constants or error types inward, the port was missing; if it is one interface at the composition
   edge, the direction is fixed.

## The family: one disease, many costumes

| Import edge | Why the far end is volatile | The port that was missing |
|---|---|---|
| business rule → vendor SDK client | vendor version, auth flow, error taxonomy | a protocol in the domain's vocabulary, satisfied at the edge |
| core module → endpoint/DTO schema | the wire format changes with the remote service | a domain value type plus a mapper at the boundary |
| long-lived service → feature-toggle reader | product changes flags continuously | a decision passed in as configuration at start-up |
| domain → logging/metrics vendor | the observability stack is replaced every few years | one thin seam owned by the application |

## The repair

**Put a port where the rate changes, and only there.** The stable side names what it needs in its own
vocabulary (a protocol, a callable, a small interface — the narrowest thing that answers the reason test);
the volatile side implements it; one composition point wires them. Then delete the direct import in the same
change. Do not abstract a stable-to-stable edge: an interface over two files that change together adds a hop
and no policy, which is the [shallow module](modularity.md) finding.

## Boundaries

Not every vendor import is a finding. A thin adapter **is** the port — reaching a vendor from `integrations/`
is the job. Code that is genuinely throwaway (a script, a notebook, a spike) has no stability to protect. A
single-call-site integration with no reason to move is not worth an interface; YAGNI applies to abstracting
as much as to building. And a vendor boundary already owned by a framework (an ORM's dialect layer, a cloud
SDK's client) is not worth re-inventing — the finding there is the module that bypassed it.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Stable Dependencies Principle; Stable Abstractions Principle | Robert C. Martin, *Agile Software Development* (2002) | The formal statement: depend in the direction of stability, and let abstractness track instability |
| The Dependency Rule | Robert C. Martin, *Clean Architecture* (2017) | Source-code dependencies point inward, toward the policy that changes least |
| Dependency Inversion Principle | Martin, *SOLID*; Gamma et al., *Design Patterns* (1994) | The mechanism: both sides depend on an abstraction owned by the stable side |

**What is this library's own:** the **reason test** as the decidable criterion (the far end's own reasons,
not a metric), churn reported as *evidence for ranking* rather than as proof, and the **fan-in multiplier**
as the blast-radius measure. The SDP states the property; the diagnostics here are what make it chargeable
at a line of code.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Layering Violations**](layering-violations.md) | The direction of the arrows. This is the rate at each end; either can fail alone. |
| [**Dependency Injection**](dependency-injection.md) | How a port is satisfied. This decides which edges earn one. |
| [**Orthogonality**](orthogonality.md) | A stable unit changing for a vendor's reasons is one more reason to change in its census. |
| [**Modularity**](modularity.md) | A port with one implementation that adds no policy is a shallow module; the reason test is what tells them apart. |
| [**Single Source of Truth**](single-source-of-truth.md) | The vendor's schema copied inward is a second home for someone else's truth. |

## Summary

1. **A dependency is a promise to be disturbed; the far end's change rate decides what it costs.**
2. **The reason test is the criterion** — if the far end's own reasons force the near end to change, the edge is wrong.
3. **Churn is evidence, not proof** — report the counts, rank the cells, let the reason test charge the finding.
4. **Put the port where the rate changes**, in the stable side's vocabulary, and delete the direct import as the measure.
5. **Never abstract a stable-to-stable edge** — that buys a hop and no policy.
