---
name: deslop-architecture-separation-of-concerns
description: Deslop principle — Separation of Concerns: High cohesion, low coupling; one concern per part — judged by where a single change lands, not only by what one function does.
---

# Separation of Concerns

> "The separation of concerns, even if not perfectly possible, is yet the only available technique for effective ordering of one's thoughts."
> — Edsger Dijkstra

Decompose systems into distinct parts, each addressing one concern — any aspect of functionality, whether functional (authentication, payment), non-functional (performance, security), or cross-cutting (logging, caching). The two measures are high cohesion (related things together) and low coupling (unrelated things independent). Watch for DB queries in UI handlers, business rules in CSS, validation scattered across layers, or formatting logic baked into business classes — and for the structural smells they create: the god object that centralizes everything, divergent change (one class edited for many unrelated reasons), and shotgun surgery (one change rippling across many files). Separate where concerns genuinely differ, but don't fragment for its own sake.

```python
# ❌ Wrong - Mixed concerns: business logic + presentation + I/O
def process_order(order_id):
    order = db.query(f"SELECT * FROM orders WHERE id = {order_id}")
    if order.total > 100:
        order.discount = order.total * 0.1
    print(f"<div class='order'>Order #{order.id}: ${order.total}</div>")
    send_email(order.customer, "Your order is ready")

# ✅ Correct - Separated concerns
class OrderRepository:
    def get_by_id(self, order_id: int) -> Order:
        return self.db.query(Order).get(order_id)

class OrderService:
    def apply_discount(self, order: Order) -> Order:
        if order.total > 100:
            order.discount = order.total * 0.1
        return order

class OrderPresenter:
    def to_html(self, order: Order) -> str:
        return f"<div class='order'>Order #{order.id}: ${order.total}</div>"
```

## Reading the change set — the two smells, made decidable

Cohesion and coupling are verdicts, and a verdict needs evidence. The evidence is **where change lands**: a change-set
is what one logical change actually cost — the files its author had to touch. It fails in two opposite directions, and
only one of them is the finding in front of you.

**Shotgun surgery — one change, many files.** The code's *unit of change* does not match its *unit of layout*. The
cause is usually structural rather than an author's carelessness: a **layer-first** tree guarantees it, because a
feature's rule, query, DTO, route and validator were given five homes before the first feature existed.

```text
# ❌ layer-first — every feature is a five-folder change by construction
src/
  controllers/order_controller.py
  services/order_service.py
  repositories/order_repository.py
  models/order.py
  validators/order_validator.py
  serializers/order_serializer.py
# "orders can be partially refunded" edits all six, plus one test file per layer
```

```text
# ✅ feature-first — the concept owns its folder, and the change is one place
src/orders/
  __init__.py      # the only surface the rest of the app may import
  model.py
  store.py
  api.py
  refunds.py       # the new rule and its tests land beside the rest of orders
```

**Divergent change — many changes, one file.** The mirror image, and the god file is its usual body: a unit edited for
unrelated reasons, so unrelated owners queue on one path. The confession is normally in the name — `utils.py`,
`helpers.py`, `common.py`, `manager.py`.

```python
# ❌ utils.py — 1,900 lines, and the name is the admission
def parse_date(s): ...       # billing
def send_email(to, t): ...   # notifications
def calculate_tax(a, r): ... # pricing
def retry(fn, n): ...        # resilience — a second copy of one that already exists
```

```python
# ✅ each concept names its own home; utils.py is deleted, not shrunk
billing/tax.py           # calculate_tax, its rates table and its tests
notifications/email.py   # send_email and its template resolution
# resilience/retry.py    # already existed: the reverse test came first, so nothing was created
```

### The tests

1. **Change-set test** — `git log --name-only -5` over the last five capability commits. One logical change crossing
   four or more folders is shotgun surgery; that count is the design's price per feature.
2. **Layout test** — are the top-level folders named for a technical role (`controllers/`, `services/`, `models/`,
   `utils/`) or for a capability (`orders/`, `billing/`)? Role-named layout decides the scattering before any code exists.
3. **Mirror test** — `git log --name-only -- <file>`. A file whose history mixes unrelated changes is the other smell.
   **Report only the one the evidence supports**: their repairs are opposite, and a misread makes the fix worse.
4. **Owner test** — name the single component that owns the concern. If the answer is a list, the concern has no owner.
5. **Newcomer test** — what must a new engineer be told to add a feature? A list of five files is the cost, stated.
6. **Dead-copy test** (god files only) — before extracting anything, grep each function for an existing owner. The
   bucket file is where duplication hides, and deleting a copy beats moving it.

### The repairs

Shotgun surgery: **move the layout to the unit of change** — group by capability, expose one surface per group, move one
capability at a time, and let a crossing change be what review rejects. Divergent change: **split by reason to change,
never by line count**, extract to named homes, and delete the bucket file. For both, make the result enforceable: an
import rule that refuses "orders → billing internals" is what stops the new layout eroding
([Layering Violations](layering-violations.md)).

### Boundaries

Framework-mandated layouts (Django apps, Rails MVC) impose some crossing, and the finding is then domain policy living
in the framework's folders. A repo split by deployment target is not layer-first. Generated code, schemas and fixtures
are legitimately long, and a single-concept module may be large and correct — a split that only relocates lines
satisfies neither smell (see the counting rules in [a campaign](../../modes/campaign.md)).

### Prior art

| Term | Source | How it relates |
|---|---|---|
| Shotgun Surgery, Divergent Change | Martin Fowler, *Refactoring*; catalogued by Refactoring.Guru as "change preventers" | Name the two opposite smells this section instruments. |
| Large Class | Refactoring.Guru, "bloaters" | The class-level body of divergent change. |
| Package by feature / Screaming Architecture | Robert C. Martin; practitioner literature | The layout repair. |
| Big Ball of Mud | Foote & Yoder (1997) | The system-wide form of the same accumulation. |

**What is this library's own:** the change-set test — reading recent commits and counting the directories crossed — as a
decidable instrument, the rule to report only one of the two opposite smells, and divergent change applied at **file**
granularity, the repository's real unit of change.

---

In relation to other principles, separation of concerns:

| Principle | Relationship |
|-----------|--------------|
| [**Modularity**](modularity.md) | Modules are where separated concerns get packaged — and shallow modules are where a "seam" holds no concern |
| [**Single Level of Abstraction**](../clean-code/slap.md) | SLAP is separation within one function |
| [**SOLID**](solid.md) | SRP is separation of concerns at class granularity |
| [**One Logical Unit, One Home**](one-logical-unit-one-home.md) | The same scattering seen as a unit spread across packages |
| [**Layering Violations**](layering-violations.md) | The enforceable arrows that keep a feature-first layout from eroding |
| [**Enforce Invariants with Constraints**](../data-layer/invariant-constraints.md) | The data layer owns "the data is well-formed" |
