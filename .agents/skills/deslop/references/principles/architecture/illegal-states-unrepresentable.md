---
name: deslop-architecture-illegal-states-unrepresentable
description: Deslop principle — Illegal States Unrepresentable: a field whose validity depends on another field's value, so every reader must re-check the combination the domain forbids.
---

# Make Illegal States Unrepresentable

> "Make illegal states unrepresentable."
> — Yaron Minsky, *Effective ML Revisited* (Jane Street, 2011)

When a model carries a field that is meaningful only in one mode — `shipped_at` when `status == "shipped"`,
`session_id` when the connection is up, `is_admin` implying `is_user` — the type has admitted a state the domain
forbids. Nothing prevents constructing it, so every reader downstream must re-derive which fields are valid, and the
one that forgets produces the null that pages someone at 3 a.m. A validator is not the repair: it moves the same
check to a new place and leaves the type able to lie. **The repair is a shape in which the combination cannot be
built at all** — one variant per state, each holding exactly the fields that state has.

```python
# ❌ five optional fields, three of them guarded by a string
@dataclass
class Connection:
    state: str                          # "connecting" | "connected" | "disconnected"
    last_ping: tuple[Time, int] | None  # set iff connected
    session_id: str | None              # set iff connected
    when_disconnected: Time | None      # set iff disconnected
```

```python
# ✅ one variant per state; the discriminator is the type, not a string
@dataclass(frozen=True)
class Connecting:
    initiated: Time

@dataclass(frozen=True)
class Connected:
    session_id: str
    last_ping: tuple[Time, int] | None

@dataclass(frozen=True)
class Disconnected:
    at: Time

State = Connecting | Connected | Disconnected

@dataclass(frozen=True)
class Connection:
    server: InetAddr
    state: State
```

The second-order benefit is the part teams underrate: every `if state == "connected"` disappears, because a function
that takes `Connected` can only be handed a connected connection. The combinable subset of states is now a
compile-time fact rather than a convention each caller re-implements.

## What this adds over its neighbours

[Parse, Don't Validate](parse-dont-validate.md) is about **where a value enters** — the boundary, once. This file is
about **what the model permits** once it is inside, and it fires on data models that were never parsed at all: DTOs,
ORM results, message payloads, configuration objects. Its trigger is a field whose meaning depends on a sibling
field, which is a shape the boundary principle does not tell a reader to look for.
[No Silent Defaults](../reliability/no-silent-defaults.md) covers the same disease at read time — the `or ""` that
invents an absent value; this covers the write-side shape that made absence expressible.

## The tests

1. **Implication table** — list the optional fields of a model and, for each pair, write "X is set only when Y…". Any
   sentence that begins "must be" is a representable illegal state; the table is the finding, and it is two minutes'
   work.
2. **Discriminator test** — grep for the field that decides (`status`, `state`, `type`, `kind`). Each comparison is a
   place re-deriving which fields are valid; that count is the cost of the shape.
3. **Constructor test** — can an illegal instance be built without raising? Then the type is a suggestion and every
   consumer is on its own.
4. **Flag test** — two booleans that never co-occur or never differ (`is_admin` + `is_user`, `is_draft` +
   `is_published`) are the same disease in miniature.
5. **Reader test** — pick the one consumer that must handle the combination; ask what it does when given the
   impossible one. `pass`, `assert`, or `# shouldn't happen` is the confession.

## The family: one disease, many costumes

| Artifact | The impossible state admitted | The variant that removes it |
|---|---|---|
| `status: str` + `shipped_at: datetime \| None` | shipped with no timestamp | `Pending` / `Shipped(at)` / `Delivered(at)` |
| optional credentials on a "guest" user | a guest carrying a password hash | separate `Guest` and `Account` |
| `error: str \| None` + `result: T \| None` | both set, or neither | `Ok(result)` / `Err(error)` |
| `payment_method: str` + `card_last4: str \| None` | card fields on a wire transfer | one variant per method |
| `start: datetime` + `end: datetime \| None` | an interval that closed before it opened | `Ongoing(start)` / `Closed(start, end)` |

## The repair

**Introduce one type per state, each with exactly the fields that state has, and make construction the only door.**
Language support varies — sum types and pattern matching in one, a frozen class per variant plus a factory function
returning a tagged value in another — and the invariant matters, not the syntax. Persist the variants as
`(discriminator, nullable columns)` if the schema requires; the boundary does the mapping, and the interior stays
impossible.

## Boundaries

Not every optional field is illegal. Genuinely optional data (`middle_name`, a note) is optional in every state. A
nullable database column is correct where the row legitimately has no value; the mapping at the boundary is where the
variant appears. Single-purpose DTOs that live for one call and are never branched on need none of this. And a
data-driven shape — a configuration blob whose keys are validated against a schema — is often better served by a
schema than by a variant per combination.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Make illegal states unrepresentable | Yaron Minsky, *Effective ML Revisited* (2011); Daniel Beskin; functional-architecture.org | The principle and the canonical `connection_state` example. |
| Designing with types | Scott Wlaschin, *F# for Fun and Profit* | The same repair, with an F#/C# treatment of the constructor test. |
| Parse, don't validate | Alexis King (2019) | The boundary-side companion: prove the invariant once, carry the proof in the type. |

**What is this library's own:** the implication-table diagnostic — reading a model as a table of "X only when Y" —
and the flag test as its miniature, so the finding is decidable while reading a dataclass rather than while thinking
about type theory.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Parse, Don't Validate**](parse-dont-validate.md) | The boundary; this is the model. Same repair, different trigger. |
| [**No Silent Defaults**](../reliability/no-silent-defaults.md) | The read-side symptom this shape causes. |
| [**Design by Contract**](../reliability/design-by-contract.md) | Invariants as checks; this makes them unrepresentable instead. |
| [**Domain Constraints**](../data-layer/domain-constraints.md) | The same invariant at the database boundary. |
| [**Implicit Coupling**](implicit-coupling.md) | A discriminator string is a vocabulary several modules must agree on. |

## Summary

1. **A field valid only in one mode is an illegal state the type permits.**
2. **Read the implication table** — every "X is set only when Y" is a finding.
3. **A validator relocates the check; a variant deletes it.**
4. **Construction is the only door** — if an illegal instance can be built, the type is a suggestion.
5. **Optional-by-nature fields are exempt**; impossibility is what this hunts, not nullability.
