---
name: deslop-architecture-parse-dont-validate
description: Deslop principle — Parse, Don't Validate: Convert input to precise types once at the boundary.
---

# Parse, Don't Validate

> "A parser is just a function that consumes less-structured input and produces more-structured output."
> — Alexis King

Validation checks data and then forgets what it learned; parsing checks data and *remembers* the result in the type system. A validator returns nothing, so every downstream caller must trust that the check happened; a parser returns a more precise type that *proves* the check happened, so callers need no trust. Parse once at the boundary, convert external data into domain types immediately, and design those types so illegal states can't even be represented.

```python
# ❌ Validation: checks then discards the knowledge
def validate_non_empty(items: list) -> None:
    if not items:
        raise ValueError("List cannot be empty")

def process(items: list) -> None:
    validate_non_empty(items)
    first = items[0]  # Caller must trust validation happened

# ✅ Parsing: checks and returns proof in the type
NonEmptyList = NewType('NonEmptyList', list)

def parse_non_empty(items: list[T]) -> NonEmptyList[T]:
    if not items:
        raise ValueError("List cannot be empty")
    return NonEmptyList(items)

def process(items: NonEmptyList[T]) -> None:
    first = items[0]  # Type guarantees safety—no trust needed
```

The opposite is "shotgun parsing" — the same `if not user_id` check scattered across every function, easy to miss and prone to leaving half-processed invalid data behind. It pairs with primitive obsession, where domain concepts ride around as raw `str`/`int`/`dict` (`create_order(customer_id: str, product_id: str, ...)` invites swapping arguments and allows negative quantities). Encode the constraints in the type instead, and make impossible combinations unrepresentable rather than guarding against them everywhere:

```python
# ❌ Invalid states representable
@dataclass
class Order:
    status: str                  # "pending" | "shipped" | "delivered"
    shipped_at: datetime | None  # Bug: can be None when status == "shipped"

# ✅ Invalid states unrepresentable
@dataclass
class ShippedOrder:
    items: list[Item]
    shipped_at: datetime  # Required—impossible to forget

Order = PendingOrder | ShippedOrder | DeliveredOrder
```

Choose the parsing depth to fit: `NewType` for a zero-overhead marker, a frozen dataclass for richer invariants, Pydantic when you want full coercion and validation at the edge. For quick scripts, prototypes, and simple CRUD, not every field needs its own type.

---

In relation to other principles, parse, don't validate:

| Principle | Relationship |
|-----------|--------------|
| [**Decide, Don't Cope**](../clean-code/decide-dont-cope.md) | Parsing is the boundary decision that ends coping |
| [**Fail-Fast**](../reliability/fail-fast.md) | Illegal states fail at the boundary, not three layers in |
| [**Constrain the Domain in the Schema**](../data-layer/domain-constraints.md) | Parse-don't-validate for data at rest |
| [**Immutability**](immutability.md) | Parsed domain types are best made immutable |
