---
name: deslop-architecture
description: Deslop principles, Part II: Architecture — DRY, Single Source of Truth, Separation of Concerns, Modularity, Encapsulation, Demeter, Orthogonality, DI, Composition, SOLID, CQS, Reusability, Parse Don't Validate, Immutability, Idempotency.
---

# Part II: Architecture

> *Structuring and designing systems. These principles govern how code is organized, how components relate, and how systems are designed for change.*

**Contents:**

- [Organization & Structure](#organization--structure)
  - [DRY: Don't Repeat Yourself](#dry-dont-repeat-yourself)
  - [Single Source of Truth](#single-source-of-truth)
  - [Separation of Concerns](#separation-of-concerns)
  - [Modularity](#modularity)
- [Coupling & Dependencies](#coupling--dependencies)
  - [Encapsulation](#encapsulation)
  - [Law of Demeter](#law-of-demeter)
  - [Orthogonality](#orthogonality)
  - [Dependency Injection](#dependency-injection)
  - [Composition Over Inheritance](#composition-over-inheritance)
- [Design Patterns & Conventions](#design-patterns--conventions)
  - [SOLID Principles](#solid-principles)
  - [Convention Over Configuration](#convention-over-configuration)
  - [Command-Query Separation](#command-query-separation)
  - [Code Reusability](#code-reusability)
- [Data & State](#data--state)
  - [Parse, Don't Validate](#parse-dont-validate)
  - [Immutability](#immutability)
  - [Idempotency](#idempotency)

---

## Organization & Structure

*Where does this code belong? DRY and Single Source of Truth ensure knowledge lives in one place, Separation of Concerns defines boundaries between responsibilities, and Modularity packages those boundaries into self-contained units.*

---

### DRY: Don't Repeat Yourself

> "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."
> — Andy Hunt & Dave Thomas, *The Pragmatic Programmer*

DRY is about **knowledge**, not code — avoid duplicating *meaning*, not syntax. Knowledge duplication (the same business rule living in multiple places) must always be fixed, starting at the SECOND occurrence — not the third. Incidental duplication (code that *looks* similar but represents *different* concepts that will evolve independently) should be left alone; merging it couples unrelated concerns. The distinguishing test is never the occurrence count, it's whether it's the same knowledge: see [Hunting Duplication — Beyond Token Scanners](duplication.md) for how to tell the two apart and what to do about it once found.

> "Duplication is far cheaper than the wrong abstraction." — Sandi Metz

The wrong abstraction is the more expensive failure. One developer extracts it; the next needs it slightly different and adds a parameter; the next adds a conditional; eventually it's incomprehensible but no one deletes it because of sunk cost. When an abstraction starts accumulating parameters and conditionals to handle "just one more case," inline it back into its callers and start fresh — re-extracting is cheaper than maintaining the wrong abstraction.

| True Knowledge Duplication (FIX) | Incidental Similarity (LEAVE) |
|---------------------------------|------------------------------|
| Same business rule/concept | Different business concepts |
| Changes *must* affect all instances | Instances will evolve independently |
| 2+ occurrences of the SAME rule | Similar-looking code, different concepts |
| Abstraction simplifies | Abstraction requires conditionals |

```python
# ❌ Over-DRY: Merged with conditionals
def get_user_by_something(identifier, by_type):
    if by_type == "id": ...
    elif by_type == "email": ...

# ✅ Separate functions with clear responsibilities
def get_user_by_id(user_id: int) -> User: ...
def get_user_by_email(email: str) -> User: ...
```

DRY extends beyond code: define database constraints once in the schema, generate API contracts from code (FastAPI/Pydantic) rather than maintaining them separately, centralize config in one module, and keep a single authoritative source for documentation.

#### Worked Example: Two Classes Repeating the Same 3 Lines

In coding, the D.R.Y. ("Don't Repeat Yourself") is one of the most important principles. If the same line(s) of code appear in more than one location, it should probably be abstracted away into a reusable function (or equivalent).

Consider two different classes each writing:

```python
user = authenticate_user(jwt_token)
groups = get_user_groups(user)
is_superuser = "superuser" in groups
```

If the code is sloppy, you'll find a bunch of classes and functions using those same 3 lines duplicated across the codebase. Deduplicate them into a shared `get_is_superuser(jwt_token)` function. Now you've reduced the lines of code (fewer lines of code is better in general), and made the code more readable and maintainable.

Some argue that for simple things, the overhead of the abstraction is not worth it. Benchmark first to see if you're really losing performance in modern systems due to overhead; usually you're not. Once two occurrences represent the same knowledge, deduplicate them; do not wait for a third copy.

**The deduplicated version — one shared helper, two callers:**

```python
from typing import Sequence


def get_is_superuser(jwt_token: str) -> bool:
    """Resolve whether the bearer of `jwt_token` holds the superuser role.

    Single authoritative implementation of the "authenticate -> list groups
    -> check superuser" chain so every caller resolves superuser status the
    same way. Fix the rule once here; every caller inherits the fix.
    """
    user = authenticate_user(jwt_token)
    groups = get_user_groups(user)
    return "superuser" in groups


class AuditExporter:
    """Exports audit events, redacting fields the caller may not read."""

    def __init__(self, jwt_token: str) -> None:
        self._is_superuser = get_is_superuser(jwt_token)

    def can_read(self, event) -> bool:
        return self._is_superuser or event.actor_id == "self"


class AdminConsole:
    """Gates admin-only operations behind the superuser check."""

    def __init__(self, jwt_token: str) -> None:
        self._is_superuser = get_is_superuser(jwt_token)

    def delete_project(self, project_id: str) -> None:
        if not self._is_superuser:
            raise PermissionError("superuser required")
        ...
```

The 3-line chain appeared in two classes; it now lives once in `get_is_superuser`. If the group lookup ever changes (e.g. switched to a Graph API call, or `"superuser"` renamed to `"system-administrator"`), there is one place to edit — not N. Feed this to your coding agents, have them make a skill for this, and have them scan your codebase for this slop violation — you'll be surprised how much this shows up.

---

### Single Source of Truth

> "There should be one—and preferably only one—obvious way to store a piece of information."

Every piece of data should have exactly one authoritative location; all other references derive from it. Where DRY targets duplicated *code and logic* within a codebase, SSoT targets duplicated *data storage* across systems and databases. The diagnostic question is simply "which copy is correct?" — if you can't answer immediately, the design is broken. Typical violations are the same foreign key stored in multiple databases, user data copied across services, and derived data with no clear owner. Duplication is fine when it's deliberate and synchronization isn't required: TTL caches, CQRS read-model denormalization, computed values, and cross-region replicas.

---

### Separation of Concerns

> "The separation of concerns, even if not perfectly possible, is yet the only available technique for effective ordering of one's thoughts."
> — Edsger W. Dijkstra

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

---

### Modularity

> "Every module is characterized by its knowledge of a design decision which it hides from all others."
> — David Parnas

Divide software into independent components, each encapsulating one responsibility and hiding its implementation behind a well-defined interface. The Parnas principle is to decompose by **design decisions likely to change**, so each module hides one such decision. Aim for high cohesion (elements within a module belong together) and low coupling (modules depend only on each other's interfaces, not internals). Prefer **deep** modules — a simple interface hiding complex implementation — over **shallow** ones that expose a complex interface while hiding little. A "God module" that does everything encapsulates nothing.

---

## Coupling & Dependencies

*How do components relate to each other? These principles minimize unhealthy dependencies. Encapsulation hides internal state, Law of Demeter limits knowledge of other objects, Orthogonality ensures independent change, Dependency Injection makes dependencies explicit, and Composition Over Inheritance favors flexible composition.*

---

### Encapsulation

> "Ask not what an object knows; ask what it can do for you."

Bundle related data with the behavior that operates on it, and hide internal state behind an interface so it can change without breaking callers. The core habit is **tell, don't ask**: rather than querying an object's state and making decisions for it externally, command it to act and let it enforce its own rules.

```python
# ❌ Wrong - Asking for state, making decisions externally
def process_order(order):
    if order.get_status() == "pending":
        if order.get_total() > 100:
            discount = order.get_total() * 0.1
            order.set_total(order.get_total() - discount)
        order.set_status("processed")

# ✅ Correct - Telling the object what to do
def process_order(order):
    order.process()  # Order knows its own business rules
```

The tells of broken encapsulation: anemic data classes that are just fields plus getters/setters, accessor pairs that add no validation or computation, methods that return mutable internal state for callers to corrupt, and feature envy (a method that uses another class's data more than its own).

---

### Law of Demeter

> "Each unit should have only limited knowledge about other units: only talk to your immediate friends; don't talk to strangers."
> — Ian Holland

Limit how much one object knows about another's structure: only talk to immediate friends, never reach *through* them. Formally, a method may invoke methods on its own object, its parameters, objects it creates, and its object's direct attributes — but not on objects *returned* by other calls. In practice this is the "one dot" rule: `a.b()` is fine, `a.b().c().d()` is a train wreck.

```python
# ❌ Wrong - Multiple dots (train wreck)
customer.get_wallet().get_credit_card().charge(amount)

# ✅ Correct - One dot
customer.charge(amount)  # Customer knows how to charge itself
```

Chaining is fine where there's no structure being traversed: builders and fluent interfaces that return `self`, DTOs with no behavior to encapsulate, and standard-library value operations like `"hello".strip().upper()`. And as Fowler warns, don't become a "getter eradicator" — objects sometimes collaborate by *providing* information, and the point is co-locating behavior with data, not banning every accessor.

---

### Orthogonality

> "Eliminate effects between unrelated things. Design self-contained components: independent, and with a single, well-defined purpose."
> — Andy Hunt & Dave Thomas

Two components are orthogonal when a change in one doesn't affect the other — like a helicopter with coupled controls, non-orthogonal code means fixing one bug pops up two more elsewhere. Coupling is viral: a little leads to more. Measure orthogonality by how many places must change when one requirement changes. The usual culprits are global state, business logic coupled to a specific database dialect, presentation mixed with computation, and objects that accrete unrelated responsibilities. Dependency injection, abstract interfaces, and avoiding global state all push toward independence.

---

### Dependency Injection

> "The key benefit of Dependency Injection is that it removes the dependency that a class has on a concrete implementation."
> — Martin Fowler

Dependencies should be injected from outside rather than created internally — a class declares *what* it needs, not *how* to get it. Constructor injection is preferred (explicit, immutable, testable) over setter or interface injection. The primary payoff is testability: swap real dependencies for test doubles without touching the class. DI also makes SRP violations visible — a constructor demanding too many dependencies is a class doing too much.

```python
# ❌ Wrong - Hardcoded dependency
class MovieLister:
    def __init__(self):
        self._finder = ColonDelimitedMovieFinder("movies.txt")  # Coupled!

# ✅ Correct - Injected dependency
class MovieLister:
    def __init__(self, finder: MovieFinder):
        self._finder = finder
```

---

### Composition Over Inheritance

> "Favor object composition over class inheritance."
> — Gang of Four, *Design Patterns*

Build complex behavior by combining objects ("has-a") rather than extending classes ("is-a"). Inheritance is white-box — the subclass sees and depends on parent internals, so changes cascade unpredictably and combinations breed a class explosion (`FileLoggerWithEncryptionAndCompression`). Composition is black-box — components interact through interfaces, stay loosely coupled, and can be mixed and swapped at runtime.

```python
# ❌ Wrong - Class explosion via inheritance
class FileLogger: ...
class FileLoggerWithEncryption(FileLogger): ...
class FileLoggerWithCompression(FileLogger): ...
# Combinatorial explosion!

# ✅ Correct - Composition
class Logger:
    def __init__(self, writer: Writer, filters: list[Filter]):
        self.writer = writer
        self.filters = filters

logger = Logger(FileWriter(), [EncryptionFilter(), CompressionFilter()])
```

---

## Design Patterns & Conventions

*Proven approaches to common problems. SOLID provides five foundational OO principles, Convention Over Configuration reduces boilerplate through sensible defaults, Command-Query Separation distinguishes actions from queries, and Code Reusability addresses when and how to make code reusable.*

---

### SOLID Principles

> "SOLID principles are the foundation of good software design—they make code more maintainable, flexible, and testable."
> — Robert C. Martin (Uncle Bob)

| Letter | Principle | Core Idea | Code Smells |
|--------|-----------|-----------|-------------|
| **S** | Single Responsibility | One reason to change | Class name has "And"/"Manager", mixed I/O and logic, methods don't use most attributes |
| **O** | Open/Closed | Open for extension, closed for modification | `if/elif`/`isinstance()` chains on type, modifying existing code for each new variant |
| **L** | Liskov Substitution | Subtypes substitutable for base types | Subclass raises `NotImplementedError`, empty `pass` overrides, type checks before calls |
| **I** | Interface Segregation | Many specific interfaces over one general | Fat interfaces (10+ methods), implementations that `raise NotImplementedError` |
| **D** | Dependency Inversion | Depend on abstractions, not concretions | Direct instantiation in constructors, concrete imports in business logic, can't mock |

SOLID earns its keep in code that must evolve, but it's overhead in simple scripts, prototypes, and performance-critical paths. Don't create an interface for a class that will only ever have one implementation — wait for real, concrete callers to reveal the actual shape before designing a flexible abstraction around a hypothetical one. (This is distinct from DRY's duplication question above: designing a speculative interface before it's needed is premature abstraction, not a duplication-count threshold — see [Hunting Duplication](duplication.md) for when *duplication itself* should be fixed.)

---

### Convention Over Configuration

> "You're not a beautiful and unique snowflake. By giving up vain individuality, you can leapfrog the toils of mundane decisions, and make faster progress in areas that really matter."
> — David Heinemeier Hansson, The Rails Doctrine

Provide sensible defaults that work out of the box, and require explicit configuration only when deviating from the norm. Most decisions aren't worth making — if 90% use `id` as the primary key, don't force everyone to specify it. Rails turns a `User` class into a `users` table with a `user_id` foreign key automatically; Django, Spring Boot, Next.js routing, and pytest test discovery all work the same way, each with an escape hatch (`self.table_name = "legacy_accounts"`) for the cases that differ.

```python
# ❌ Wrong - Forcing configuration for obvious defaults
service = UserService(
    table_name="users",
    id_column="id",
    created_at_column="created_at",
    updated_at_column="updated_at",
)

# ✅ Correct - Sensible defaults with escape hatches
class UserService:
    def __init__(self, table_name: str = "users", id_column: str = "id"):
        self.table_name = table_name
        self.id_column = id_column

service = UserService()                              # Zero config for the common case
legacy = UserService(table_name="legacy_accounts")  # Override only what differs
```

The cost is hidden magic: implicit behavior is harder to debug, you must learn the convention before you can deviate, and convention-optimized common cases can fight you at the edges (a legacy DB named `tbl_usr_accounts` means fighting the framework). This is why Python prizes "explicit over implicit" — the resolution is that conventions must be *discoverable* and well documented. Convention serves you until it doesn't; then configure explicitly.

---

### Command-Query Separation

> "Asking a question should not change the answer."
> — Bertrand Meyer

A method should either return information (a query, no side effects) or change state (a command, returns nothing) — never both. Keeping them separate means queries are safe to call anywhere, cache, and parallelize without race conditions, while commands stay easy to reason about and test. Break the rule only for genuinely atomic operations that must do both — a stack `pop`, a thread-safe increment-and-get, database identity generation.

```python
# ❌ Wrong - Modifies AND returns
def get_or_create_user(self, email: str) -> User:
    user = self.db.find_by_email(email)
    if not user:
        user = User(email=email)
        self.db.save(user)  # Side effect!
    return user

# ✅ Correct - Separate operations
def find_user_by_email(self, email: str) -> User | None:
    """Query: Returns user or None, no side effects."""
    return self.db.find_by_email(email)

def create_user(self, email: str) -> None:
    """Command: Creates user, returns nothing."""
    self.db.save(User(email=email))
```

---

### Code Reusability

> "A little copying is better than a little dependency."
> — Rob Pike

Reusability is forward-looking — code usable in multiple contexts without modification — where DRY is about eliminating duplication that already exists. It's earned, not designed up front: reusable components cost 3-10x more to build, and that cost only pays off with *actual* reuse. Designing for reuse before the need is proven is a YAGNI violation that buys complexity with no payoff (the `GenericDataProcessor` that takes a parser, transformer, validator, and serializer to handle "any" format). Wait for real, concrete callers to reveal the actual shape needed, then generalize — this is about not speculating on a future interface, not about how many times duplicated *knowledge* must appear before it's fixed (that's the DRY question — see [Hunting Duplication](duplication.md)).

```python
# ❌ Wrong - Premature reusability (YAGNI violation)
class GenericDataProcessor:
    def __init__(self, parser, transformer, validator, serializer): ...
    def process(self, data, options=None): ...  # endless option plumbing

# ✅ Correct - Start specific, generalize when needed
def parse_user_csv(csv_data: str) -> list[dict]:
    rows = csv_data.strip().split('\n')
    headers = rows[0].split(',')
    return [dict(zip(headers, row.split(','))) for row in rows[1:]]
```

When reuse *is* warranted, minimize dependencies (a little copying beats a little dependency), accept abstract inputs (a `Protocol`, not a concrete class), provide sensible defaults, and keep the public interface stable. But remember reuse cuts both ways: isolated, duplicated code keeps bugs and changes contained, where a "reusable" component becomes a coupling point across every system that depends on it. Rewriting 50 obvious lines often beats understanding 500 lines of someone's framework.

---

## Data & State

*How should data flow and behave? Parse Don't Validate transforms unstructured input into typed domain objects at boundaries. Immutability eliminates bugs by preventing state changes after creation. Idempotency ensures operations can be safely repeated.*

---

### Parse, Don't Validate

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

### Immutability

> "Immutable types are safer from bugs, easier to understand, and more ready for change."
> — MIT 6.005 Software Construction

Once created, an immutable object's value is fixed; to "change" it you create a new one. Mutable shared state causes most concurrency and aliasing bugs, and immutability eliminates them by design — objects become safe to share between threads without locks or defensive copies, usable as hash keys, and easy to reason about because you only need to understand the creation site. The common violation is a function that quietly mutates its caller's data; return a new structure instead.

```python
# ❌ Wrong - Mutates caller's data
def normalize_scores(scores: list[float]) -> list[float]:
    for i in range(len(scores)):
        scores[i] /= max(scores)  # Mutates the input!
    return scores

# ✅ Correct - Returns new list
def normalize_scores(scores: list[float]) -> list[float]:
    max_score = max(scores)
    return [score / max_score for score in scores]
```

In Python, reach for `@dataclass(frozen=True)`, `tuple` instead of `list` for fixed data, and `frozenset` instead of `set`.

---

### Idempotency

> "An operation is idempotent if performing it multiple times has the same effect as performing it once."

An idempotent operation produces the same result whether run once or many times. Duplicate requests are inevitable in distributed systems — retries, at-least-once queues, impatient users — so design around them rather than assuming exactly-once delivery. The main techniques: idempotency keys, deterministic IDs derived from content, database upserts (`INSERT ... ON CONFLICT`), conditional writes with version numbers, and lease-based processing. Some operations are naturally idempotent (`GET`, `PUT`, `DELETE`, and assignment `x = 5`) while others are not (`x += 5`). The cheap test is to call it twice and confirm the state matches.
