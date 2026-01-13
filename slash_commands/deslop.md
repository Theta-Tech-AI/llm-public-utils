# Deslop: Code Quality Analysis Command

> A comprehensive Claude Code slash command for identifying and fixing "slop" in your codebase. Drop this file into your `.claude/commands/` folder to use `/deslop` to analyze code for violations of established coding principles and get concrete, actionable improvements.

This command combines a code analysis workflow with an extensive library of coding principles. When you run `/deslop [file-or-directory]`, or even just `/deslop` or perhaps `/deslop my frontend typescript code` the AI will read your code, cross-reference it against these principles, and suggest specific fixes with before/after examples.

---

## Table of Contents

1. [The Deslop Command](#the-deslop-command)
2. [Coding Principles Reference](#coding-principles-reference)
   - [Core Principles](#core-principles)
     - [DRY: Don't Repeat Yourself](#dry-dont-repeat-yourself)
     - [KISS: Keep It Simple, Stupid](#kiss-keep-it-simple-stupid)
     - [YAGNI: You Aren't Gonna Need It](#yagni-you-arent-gonna-need-it)
     - [Self-Documenting Code](#self-documenting-code)
     - [Separation of Concerns](#separation-of-concerns)
   - [Object-Oriented Design](#object-oriented-design)
     - [SOLID Principles](#solid-principles)
     - [Composition Over Inheritance](#composition-over-inheritance)
     - [Encapsulation](#encapsulation)
     - [Law of Demeter](#law-of-demeter)
   - [Data & State Management](#data--state-management)
     - [Single Source of Truth](#single-source-of-truth)
     - [Immutability](#immutability)
     - [Idempotency](#idempotency)
   - [Architecture & Design](#architecture--design)
     - [Modularity](#modularity)
     - [Orthogonality](#orthogonality)
     - [Dependency Injection](#dependency-injection)
     - [Command-Query Separation](#command-query-separation)
   - [Reliability & Operations](#reliability--operations)
     - [Fail-Fast & Defensive Programming](#fail-fast--defensive-programming)
     - [Design by Contract](#design-by-contract)
     - [Resilience & Graceful Degradation](#resilience--graceful-degradation)
     - [Observability & Transparency](#observability--transparency)
   - [User Experience](#user-experience)
     - [Principle of Least Surprise](#principle-of-least-surprise)
     - [Elegance](#elegance)

---

## The Deslop Command

You are a code quality analyzer. Your task is to identify "slop" - code that violates established coding principles - and suggest concrete improvements.

At the end, figure out what you should actually change in the code and ask the user if you should make the changes. Then make the changes if the user affirms.

### Target

Analyze: $ARGUMENTS

If no argument provided, operate on the current folder or current code base.

### Process

1. **Read all coding principles** from this document to understand what good code looks like.
2. **Read the target file(s)** using the Read tool
3. **Reread relevant coding principles** based on what violations you observe
4. **Identify violations** organized by principle
5. **Suggest concrete fixes** with before/after examples

### Output Format

#### Summary

Brief overview of code health (1-2 sentences).

#### Violations Found

For each violation:

```
##### [Principle Name] - [Specific Issue]

**Location**: `file.py:line_number`

**Problem**: [Description of what's wrong]

**Before**:
```python
# problematic code
```

**After**:
```python
# improved code
```

**Why**: [Brief explanation referencing the principle]
```

#### Recommendations

Prioritized list of changes, most impactful first.

Then, ask the user if they'd like to implement some or all of the changes.

### Important Notes

- **Don't over-engineer**: Suggesting abstractions for single-use code violates YAGNI/KISS
- **Context matters**: Test code has different standards (DAMP over DRY)
- **Rule of Three**: Don't suggest abstracting until pattern proven with 3+ occurrences
- **Incidental similarity is not duplication**: Don't merge code that happens to look similar but represents different concepts
- **Be specific**: Reference exact line numbers and provide concrete before/after code

### Example Output

#### Summary

The module has good structure but contains several DRY violations and magic numbers that reduce maintainability.

#### Violations Found

##### Self-Documenting Code - Magic Numbers

**Location**: `processor.py:45-48`

**Problem**: Hardcoded numeric values without explanation

**Before**:
```python
if retry_count > 3:
    time.sleep(0.5)
```

**After**:
```python
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 0.5

if retry_count > MAX_RETRIES:
    time.sleep(RETRY_DELAY_SECONDS)
```

**Why**: Named constants are self-documenting and centralize configuration.

##### DRY - Duplicated Validation Logic

**Location**: `api.py:23-28` and `api.py:67-72`

**Problem**: Same email validation logic in two places

**Before**:
```python
# In create_user():
if not email or '@' not in email:
    raise ValueError("Invalid email")

# In update_user():
if not email or '@' not in email:
    raise ValueError("Invalid email")
```

**After**:
```python
def validate_email(email: str) -> None:
    if not email or '@' not in email:
        raise ValueError("Invalid email")

# In both functions:
validate_email(email)
```

**Why**: Same business rule duplicated - if validation changes, both must update.

#### Recommendations

1. Extract `validate_email()` helper (DRY - affects 2 locations)
2. Replace magic numbers with named constants (Self-Documenting - affects 4 locations)
3. Consider splitting `UserManager` into `UserService` and `UserRepository` (SRP - optional, low priority)

---

## Coding Principles Reference

---

# Core Principles

---

## DRY: Don't Repeat Yourself

> "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."
> — Andy Hunt & Dave Thomas, *The Pragmatic Programmer*

### Core Concept

DRY is about **knowledge**, not necessarily code. Avoid duplication of *meaning and intent*, not just syntax. Two identical-looking code blocks may represent different business concepts—merging them creates harmful coupling.

**Two types of "duplication":**
1. **Knowledge Duplication** — Same business rule/concept in multiple places. **Always a code smell. Always fix.**
2. **Incidental Duplication** — Code that *looks* similar but represents *different* concepts. **Not true duplication.** Merging it creates harmful coupling.

**Critical insight**: If two code blocks look identical but encode *different* business concepts, they are not necessarily duplicates—they may be coincidentally similar. Forcing them into one abstraction couples unrelated concerns.

### The Rule of Three

> **First time**: Just write it. **Second time**: Note it. **Third time**: Abstract it.

This is **not** permission to tolerate knowledge duplication—it's patience to find the *right* abstraction. With only two occurrences, you can't distinguish true knowledge duplication from incidental similarity. Three examples reveal the actual pattern.

Sometimes it makes sense to deduplicate after two, and always after three.

### Recognizing True vs. Incidental Duplication

| True Knowledge Duplication (FIX) | Incidental Similarity (LEAVE) |
|---------------------------------|------------------------------|
| Same business rule/concept | Different business concepts |
| Changes *must* affect all instances | Instances will evolve independently |
| 3+ occurrences confirm the pattern | 1-2 occurrences—pattern unclear |
| Abstraction simplifies | Abstraction requires conditionals |
| Single source of truth needed | Coupling would be harmful |

### Common Violations

**Obvious**: Copy-pasted functions, duplicated validation, repeated magic numbers

**Hidden**: Inconsistent business rules across apps, divergent type definitions, scattered config, parallel data structures (DB columns in SQL strings AND ORM models)

### Anti-Patterns

```python
# ❌ Over-DRY: Merged with conditionals
def get_user_by_something(identifier, by_type):
    if by_type == "id": ...
    elif by_type == "email": ...

# ✅ Separate functions with clear responsibilities
def get_user_by_id(user_id: int) -> User: ...
def get_user_by_email(email: str) -> User: ...
```

```python
# ❌ Premature abstraction (Student/Teacher trap)
class Person:
    def get_full_name(self): return f"{self.first} {self.last}"
class Student(Person): pass
class Teacher(Person): pass  # Later needs middle name—abstraction wasted

# ✅ Keep separate until pattern proven
class Student:
    def get_full_name(self): return f"{self.first} {self.last}"
class Teacher:
    def get_full_name(self): return f"{self.first} {self.middle} {self.last}"
```

### Refactoring Techniques

| Technique | When to Use |
|-----------|-------------|
| **Extract Method** | Duplicated logic in same class |
| **Extract Class** | Duplication spans multiple methods |
| **Extract Superclass** | Multiple classes share behavior (Template Method) |
| **Parameterize Method** | Methods differ only in values |
| **Composition** | Complex inheritance hierarchies |

### DRY Beyond Code

- **Database**: Define constraints once in schema, not duplicated in app
- **API**: Generate OpenAPI from code (FastAPI/Pydantic), don't maintain separately
- **Config**: Centralize in one module, import everywhere
- **Docs**: Single source of truth, reference elsewhere
- **Infrastructure**: Similar infrastructure components may warrant deduplication.

### Summary

1. **Knowledge duplication is always a code smell**—always fix it
2. **Incidental similarity is not duplication**—don't merge different concepts
3. **Rule of Three**: Patience to find the *right* abstraction, not permission to ignore duplication
4. **Wrong abstractions**: Delete and start over—they merged incidental similarity
5. **Beyond code**: Databases, APIs, config, documentation—single source of truth everywhere

---

## KISS: Keep It Simple, Stupid

> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."
> — Antoine de Saint-Exupéry

### Core Concept

KISS is the discipline of **avoiding unnecessary complexity**. Coined by Kelly Johnson at Lockheed Skunk Works (1960), the principle states systems work best when kept simple.

**Two sins of complexity:**
1. **Too many parts** in the system
2. **Too many interconnected parts** coupling the system together

**Simple ≠ Easy:** Simple systems have few interconnected parts. Easy tasks require little effort.

### Measuring Complexity

| Metric | Measures | Threshold | Use Case |
|--------|----------|-----------|----------|
| **Cyclomatic Complexity** | Independent paths through code | ≤10/function | Test planning |
| **Cognitive Complexity** | Mental effort to understand | ≤15/function | Readability |

### Common Violations

**Code Smells**: Single-implementation interfaces, factories of factories, deep inheritance, "clever" one-liners.

**Verbal Cues**: "This pattern will be useful when...", "Let me make this more flexible...", "This is the proper enterprise way..."

### Four Classes of Violations

| Class | Example |
|-------|---------|
| **Cleverness Over Clarity** | Nested ternaries, regex golf |
| **Premature Optimization** | Caching before profiling |
| **Unnecessary Abstraction** | Interface for single implementation |
| **Speculative Generality** | Calculator with plugin architecture |

### Anti-Patterns

```python
# ❌ Wrong - Over-engineered calculator
class OperationInterface(ABC):
    @abstractmethod
    def execute(self, a: float, b: float) -> float: ...

class AddOperation(OperationInterface):
    def execute(self, a, b): return a + b

class OperationFactory:
    def create(self, op: str) -> OperationInterface: ...

# ✅ Correct - Direct solution
def calculate(a: float, b: float, op: str) -> float:
    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/': return a / b
    raise ValueError(f"Unknown operation: {op}")
```

### The Simplicity Test

Before adding complexity: **Can a junior understand this?** — **Does it solve a problem we have today?** — **Am I trying to impress or communicate?**

### Summary

1. **Fewer parts, fewer connections** — complexity kills maintainability
2. **Simple ≠ Easy** — simple systems may require skill to build
3. **Junior-readable code** — if they can't understand it, it's too complex
4. **Hardcode first** — add configurability when proven necessary
5. **Measure complexity** — cyclomatic ≤10, cognitive ≤15 per function
6. **Simplest sufficient code** — not incomplete, not over-engineered

---

## YAGNI: You Aren't Gonna Need It

> "Always implement things when you actually need them, never when you just foresee that you need them."
> — Ron Jeffries, XP co-founder

### Core Concept

YAGNI is the discipline of **not building functionality until it's required**. Every feature has costs: development, testing, maintenance, cognitive load. Features you don't need yet carry these costs without delivering value.

**The trap**: "While I'm here, I'll just add..." — **The reality**: ⅔ of speculative features fail to improve their target metrics.

### Four Costs of YAGNI Violations

| Cost | Description |
|------|-------------|
| **Build** | Time developing, testing, debugging unused code |
| **Delay** | Value lost by not building needed features instead |
| **Carry** | Complexity slowing all future development |
| **Repair** | Fixing when requirements differ from predictions |

### When YAGNI Applies

| Apply YAGNI | Don't Apply YAGNI |
|-------------|-------------------|
| Speculative features | Security (build in from start) |
| "Just in case" abstractions | Logging/observability |
| Unused configuration options | API versioning (public APIs) |
| Premature optimization | CI/CD and testing infrastructure |
| Generic frameworks for single use | Data migration paths |

### Common Violations

**Code Smells**: Config options no one uses, ABC with one implementation, extensibility points never extended, commented "future" code, unused API endpoints.

**Verbal Cues**: "We might need this later", "Just in case", "While we have the hood open...", "For future flexibility..."

### Anti-Patterns

```python
# ❌ Wrong - Speculative abstraction
class DataExporter(ABC):
    @abstractmethod
    def export(self, data): ...

class JSONExporter(DataExporter):
    def export(self, data): return json.dumps(data)
# CSVExporter, XMLExporter never built...

# ✅ Correct - Build what you need
def export_to_json(data):
    return json.dumps(data)
# Add abstraction when second exporter is needed
```

### The Delete Test

Before adding code: **Who needs this today?** (not "might need") — **What breaks without it?** (if nothing, skip it) — **Can we add it later?** (usually yes, with better understanding)

### Summary

1. **Build only what's needed now** — ⅔ of speculative features fail
2. **Delete speculative code** — git has history
3. **Hardcode first** — configure when needed
4. **Concrete over abstract** — until third occurrence
5. **Keep code malleable** — YAGNI requires easy-to-change code

---

## Self-Documenting Code

> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand."
> — Martin Fowler

### Core Concept

Self-documenting code **naturally conveys its purpose** through human-readable names, clear structure, and logical organization—without relying on comments.

**Reveals:** What the code does, how it works (through naming and structure)
**Cannot reveal:** Why decisions were made, rejected alternatives, system context (requires comments/docs)

### The Three Pillars

#### 1. Intention-Revealing Names

Names express purpose, not implementation. **Spell words out completely**—abbreviations force mental translation.

```python
# ❌ Wrong
def proc(d, w):
    return d * w * 8

# ✅ Correct
def calculate_billable_hours(days_worked: int, weeks: int) -> int:
    hours_per_day = 8
    return days_worked * weeks * hours_per_day
```

#### 2. Eliminate Magic Values

Replace hardcoded numbers with named constants.

```python
# ❌ Wrong                    # ✅ Correct
if retry_count > 3:           MAX_RETRIES = 3
    time.sleep(0.5)           RETRY_DELAY_SECONDS = 0.5
                              if retry_count > MAX_RETRIES:
                                  time.sleep(RETRY_DELAY_SECONDS)
```

#### 3. Structured Organization

Each function has one clear purpose. Structure tells the story.

### Naming Conventions

| Element | Convention | Examples |
|---------|------------|----------|
| **Variables** | Nouns, fully spelled out | `user_count`, `retry_delay_seconds` |
| **Functions** | Verbs/verb phrases | `calculate_total()`, `validate_input()` |
| **Predicates** | `is_`, `has_`, `can_` prefix | `is_active`, `has_permission` |
| **Classes** | Nouns, PascalCase | `UserAccount`, `OrderProcessor` |
| **Constants** | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |

### Common Violations

**Code Smells:** Abbreviations (`usr`, `cnt`), single-letter variables outside tiny scopes, boolean parameters without names, vague function names (`process`, `handle`, `do`).

### The Comment Balance

Self-documenting handles **what/how**. Comments handle **why/why not**.

```python
# ✅ Correct - Comment explains why
# Exponential backoff: upstream API rate-limits during peak hours (ISSUE-1234)
for attempt in range(MAX_RETRIES):
    time.sleep(2 ** attempt)
```

### Summary

1. **Spell out names completely** — `user_count` not `usr_cnt`
2. **Eliminate magic values** — named constants explain meaning
3. **Structure tells story** — one function, one purpose
4. **Code shows what/how** — comments explain why/why not

---

## Separation of Concerns

> "The separation of concerns, even if not perfectly possible, is yet the only available technique for effective ordering of one's thoughts."
> — Edsger W. Dijkstra

### Core Concept

Separation of Concerns (SoC) is the discipline of **decomposing a system into distinct parts, each addressing a single concern**. A "concern" is any aspect of functionality—business logic, persistence, UI, error handling, etc.

**Two measures of good separation:**
1. **High cohesion** — related things grouped together
2. **Low coupling** — unrelated things minimally dependent

### Types of Concerns

| Type | Examples |
|------|----------|
| **Functional** | Authentication, data processing, payment |
| **Non-functional** | Performance, security, scalability |
| **Cross-cutting** | Logging, error handling, caching |

### Common Violations

**Code Smells**: DB queries in UI handlers, business rules in CSS, validation scattered across layers, formatting in business classes.

**SoC-Specific Anti-Patterns:**

| Anti-Pattern | Description | Fix |
|--------------|-------------|-----|
| **Blob/God Object** | One class centralizes most functionality | Split into single-purpose classes |
| **Divergent Change** | One class changes for multiple reasons | Extract class per reason |
| **Shotgun Surgery** | One change modifies many places | Consolidate related logic |

### Anti-Patterns

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

### Summary

1. **One concern per component** — functions, classes, modules, layers
2. **High cohesion, low coupling** — related together, unrelated separate
3. **Natural boundaries** — separate where concerns genuinely differ
4. **Avoid over-separation** — don't fragment for its own sake

---

# Object-Oriented Design

---

## SOLID Principles

> "SOLID principles are the foundation of good software design—they make code more maintainable, flexible, and testable."
> — Robert C. Martin (Uncle Bob)

### Overview

| Letter | Principle | Core Idea |
|--------|-----------|-----------|
| **S** | Single Responsibility | One reason to change |
| **O** | Open/Closed | Open for extension, closed for modification |
| **L** | Liskov Substitution | Subtypes must be substitutable for base types |
| **I** | Interface Segregation | Many specific interfaces over one general |
| **D** | Dependency Inversion | Depend on abstractions, not concretions |

### S — Single Responsibility Principle

> "A class should have one, and only one, reason to change."

**Violations**: Mixed I/O and logic, persistence in domain objects, god classes, class names with "And" or "Manager"

### O — Open/Closed Principle

> "Software entities should be open for extension but closed for modification."

**Violations**: `if/elif` chains checking types, `isinstance()` checks, modifying existing code for new variants

### L — Liskov Substitution Principle

> "Subtypes must be substitutable for their base types."

**Violations**: Subclass raises `NotImplementedError`, empty `pass` overrides, type checks before method calls

### I — Interface Segregation Principle

> "Clients should not be forced to depend on interfaces they do not use."

**Violations**: Fat interfaces (20+ methods), `raise NotImplementedError` in implementations

### D — Dependency Inversion Principle

> "High-level modules should not depend on low-level modules. Both should depend on abstractions."

**Violations**: Direct instantiation in constructors, concrete imports in business logic, can't mock for testing

### When NOT to Apply SOLID

1. **Simple scripts**: Overhead outweighs benefits
2. **Prototyping**: Flexibility over structure
3. **Performance-critical paths**: Abstractions add indirection
4. **Single implementations**: Don't create interfaces for classes that won't have alternatives
5. **Early development**: Wait for patterns to emerge (Rule of Three)

### Detection Checklist

| Principle | Code Smells |
|-----------|-------------|
| **SRP** | Class name has "And"/"Manager", methods don't use most attributes |
| **OCP** | Adding features requires modifying existing classes, `isinstance()` chains |
| **LSP** | Subclass raises `NotImplementedError`, empty overrides, type checks |
| **ISP** | Interfaces with 10+ methods, classes implement unused methods |
| **DIP** | Direct instantiation in constructors, can't mock for testing |

---

## Composition Over Inheritance

> "Favor object composition over class inheritance."
> — Gang of Four, *Design Patterns*

### Core Concept

Composition Over Inheritance is the principle of **building complex behavior by combining objects rather than extending classes**.

**The key distinction:**
- **Inheritance** ("is-a"): White-box reuse — subclass sees parent internals
- **Composition** ("has-a"): Black-box reuse — objects interact via interfaces only

### Why Composition Is Preferred

| Inheritance Problem | Composition Solution |
|---------------------|---------------------|
| Tight coupling to parent | Loose coupling via interfaces |
| Changes cascade to subclasses | Changes isolated to components |
| Hierarchy fixed at compile-time | Components swappable at runtime |
| Class explosion for combinations | Mix components as needed |
| Fragile base class problem | No inherited implementation details |

### Anti-Patterns

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

### Summary

1. **Composition = "has-a"**, Inheritance = "is-a" — choose appropriately
2. **Inheritance breaks encapsulation** — changes cascade unpredictably
3. **Class explosion** — composition avoids combinatorial hierarchies
4. **Runtime flexibility** — swap components without recompiling

---

## Encapsulation

> "Ask not what an object knows; ask what it can do for you."

### Core Concept

Encapsulation is the principle of **bundling data and the methods that operate on that data into a single unit, while hiding internal implementation details behind a well-defined interface**.

**Two aspects:**
1. **Bundling**: Grouping related data and behavior together
2. **Information Hiding**: Restricting direct access to internal state

### Tell, Don't Ask

Instead of querying an object's state and making decisions externally, tell the object what to do and let it use its own state.

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

### Common Violations

- **Data Classes Without Behavior**: A "data class" that only contains fields and getters/setters
- **Getter/Setter Pairs That Add No Value**: Accessors without validation or computation
- **Returning Mutable Internal State**: Allowing callers to corrupt object invariants
- **Feature Envy**: Methods that use more data from another class than their own

### Summary

1. **Bundle data with behavior** — Objects should do things, not just hold data
2. **Hide implementation details** — Internals can change without affecting callers
3. **Tell, don't ask** — Command objects to act rather than querying their state
4. **Protect invariants** — Use access control to enforce object validity

---

## Law of Demeter

> "Each unit should have only limited knowledge about other units: only talk to your immediate friends; don't talk to strangers."
> — Ian Holland

### Core Concept

The Law of Demeter (LoD) is the discipline of **limiting an object's knowledge of other objects' internal structure**. An object should only interact with its immediate dependencies, not reach through them.

### The "One Dot" Rule

```python
# ❌ Wrong - Multiple dots (train wreck)
customer.get_wallet().get_credit_card().charge(amount)

# ✅ Correct - One dot
customer.charge(amount)  # Customer knows how to charge itself
```

### Formal Definition

A method `m` of object `a` may only invoke methods of:
- `a` itself
- `m`'s parameters
- Objects created within `m`
- `a`'s direct attributes
- Global/module-level objects

**Forbidden**: Methods of objects returned by other method calls.

### Exceptions: When Chaining Is Acceptable

| Pattern | Why It's OK |
|---------|-------------|
| **Builder pattern** | Same object returned; configures self |
| **Fluent interfaces** | Designed for chaining; returns `self` |
| **Data Transfer Objects** | No behavior to encapsulate |
| **Standard library** | `"hello".strip().upper()` — string ops |

### Summary

1. **Only talk to immediate friends** — don't reach through objects
2. **One dot rule** — `a.b()` good, `a.b().c()` suspect
3. **Tell, don't ask** — command objects, don't interrogate
4. **Exceptions exist** — builders, fluent APIs, DTOs are fine

---

# Data & State Management

---

## Single Source of Truth

> "There should be one—and preferably only one—obvious way to store a piece of information."

### Core Concept

Single Source of Truth (SSoT) is a data management principle: **every piece of data should have exactly one authoritative location**. All other references should derive from or point to that single source.

**The fundamental problem**: When data exists in multiple places, which one is correct when they disagree?

### SSoT vs. DRY

| Aspect | DRY | SSoT |
|--------|-----|------|
| **Focus** | Code and logic duplication | Data storage duplication |
| **Scope** | Within a codebase | Across systems and databases |
| **Violation** | Copy-pasted functions | Same field in multiple tables |
| **Fix** | Extract to shared function | Designate authoritative source |

### Common Violations

1. **Storing Foreign Keys in Multiple Databases**
2. **Duplicating User Data Across Services**
3. **Storing Derived Data Without Clear Ownership**

### When Duplication Is Acceptable

1. **Intentional Caching** with TTL
2. **Read Model Denormalization** (CQRS)
3. **Computed/Derived Values**
4. **Cross-Region Replication**

### Summary

1. **Every piece of data needs exactly one authoritative source**
2. **Other systems should reference, not duplicate** authoritative data
3. **Derived/computed values are acceptable** — they don't need synchronization
4. **Ask "which is correct?"** — if you can't answer immediately, fix the design

---

## Immutability

> "Immutable types are safer from bugs, easier to understand, and more ready for change."
> — MIT 6.005 Software Construction

### Core Concept

Immutability is the principle that **once an object is created, its state cannot be modified**. Instead of changing existing data, you create new data structures with the desired changes.

**The key insight**: Mutable shared state is the root cause of most concurrency bugs and many aliasing bugs. Immutability eliminates these problems by design.

### Benefits

- **Thread Safety Without Locks**: Immutable objects can be freely shared between threads
- **Eliminates Defensive Copying**: Immutable objects can be shared directly
- **Simpler Reasoning**: Only understand where an object was created
- **Safe Hash Keys**: Immutable objects can safely be dictionary keys
- **Enables Caching**: Cached results remain valid indefinitely

### Common Violations

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

### Python Implementation

```python
from dataclasses import dataclass

# ✅ Immutable dataclass
@dataclass(frozen=True)
class Document:
    gdrive_id: str
    file_name: str
    content_hash: str

# ✅ Use tuple instead of list for fixed data
SUPPORTED_EXTENSIONS: tuple[str, ...] = (".pdf", ".docx", ".txt")

# ✅ Use frozenset instead of set
VALID_STATUSES: frozenset[str] = frozenset({"pending", "done", "failed"})
```

### Summary

1. **Immutable objects can't change** — once created, their value is fixed
2. **Aliasing is safe** with immutable objects
3. **Thread safety is free** — no locks needed
4. **Prefer immutability** — use frozen dataclasses, tuples, frozensets

---

## Idempotency

> "An operation is idempotent if performing it multiple times has the same effect as performing it once."

### Core Concept

Idempotency is the property where executing an operation multiple times produces the same result as executing it once. In distributed systems, network failures, retries, and message redelivery make idempotency essential.

**The key insight**: Duplicate requests are not bugs to eliminate—they are inevitable realities to design around.

### Implementation Strategies

1. **Idempotency Keys**: Attach unique identifier to each request
2. **Deterministic IDs**: Generate IDs from content itself
3. **Database Upserts**: Use `INSERT ... ON CONFLICT`
4. **Conditional Writes**: Use version numbers (optimistic locking)
5. **Lease-Based Processing**: Acquire exclusive access before processing

### Naturally Idempotent Operations

| Operation | Why Idempotent |
|-----------|----------------|
| `GET /resource` | Reads don't change state |
| `PUT /resource` | Full replacement, same result |
| `DELETE /resource` | Deleting twice = still deleted |
| Setting a value | `x = 5` is idempotent; `x += 5` is not |

### Summary

1. **Duplicates are inevitable** in distributed systems—design for them
2. **Use deterministic IDs** derived from content when possible
3. **Prefer upserts** over inserts for database operations
4. **Track processed messages** in queue consumers
5. **Test by calling twice** and verifying same result

---

# Architecture & Design

---

## Modularity

> "Every module is characterized by its knowledge of a design decision which it hides from all others."
> — David Parnas

### Core Concept

Modularity is **dividing software into independent components** where each module encapsulates a specific responsibility and hides implementation details behind a well-defined interface.

**The Parnas Principle**: Decompose systems by **design decisions likely to change**. Each module hides one decision.

**Two measures:**
1. **Cohesion** — How strongly elements within a module belong together (aim: high)
2. **Coupling** — How much modules depend on each other's internals (aim: low)

### Deep vs. Shallow Modules

| Type | Characteristics |
|------|-----------------|
| **Deep** | Simple interface, complex implementation |
| **Shallow** | Complex interface, little hidden |

**Aim for depth**: Hide significant complexity behind minimal APIs.

### Common Violations

**Code Smells**: God Class, Feature Envy, Shotgun Surgery, Utilities junk drawer

### Summary

1. **Hide design decisions** — Each module encapsulates one decision likely to change
2. **High cohesion** — Elements within a module belong together
3. **Low coupling** — Modules depend only on interfaces
4. **Deep over shallow** — Simple interface, complex implementation
5. **No God modules** — If it does "everything," it encapsulates nothing

---

## Orthogonality

> "Eliminate effects between unrelated things. Design self-contained components: independent, and with a single, well-defined purpose."
> — Andy Hunt & Dave Thomas

### Core Concept

Two components are **orthogonal** if changes in one do not affect the other. Just as moving along the X-axis doesn't change your Y position, modifying an orthogonal component shouldn't ripple into unrelated parts.

### The Helicopter Problem

A helicopter's controls are all coupled—lowering the collective causes dip and turn, requiring compensating adjustments. This is precisely what happens in non-orthogonal code: fix a bug in one place, two more pop up elsewhere.

### Common Violations

- **Global State**: Becomes a coupling point between different parts
- **Database-Coupled Business Logic**: SQL dialects leak into business logic
- **Presentation Mixed with Logic**: Changing display requires changing computation
- **Feature Creep in Objects**: Objects accumulate responsibilities

### Summary

1. **Two components are orthogonal if changes in one don't affect the other**
2. **Coupling is viral** — a little leads to more
3. **Measure orthogonality** by how many places change when one requirement changes
4. **Techniques that help**: dependency injection, abstract interfaces, avoiding global state

---

## Dependency Injection

> "The key benefit of Dependency Injection is that it removes the dependency that a class has on a concrete implementation."
> — Martin Fowler

### Core Concept

Dependency Injection (DI) is a technique where dependencies are "injected" from the outside rather than created internally. A class should declare what it needs, not how to get it.

### Three Forms of Injection

1. **Constructor Injection** (Preferred): Dependencies through constructor
2. **Setter Injection**: Dependencies through setter methods after construction
3. **Interface Injection**: Dependency provides an injector method

### Anti-Patterns

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

### Service Lifetimes

| Lifetime | Instance Created | Use Case |
|----------|------------------|----------|
| **Transient** | Every time requested | Lightweight, stateless services |
| **Scoped** | Once per scope/request | Request-specific state |
| **Singleton** | Once for application lifetime | Expensive to create, shared state |

### Summary

1. **DI decouples classes from dependencies** — clients declare needs, not solutions
2. **Constructor injection is preferred** — explicit, immutable, testable
3. **Too many dependencies = SRP violation** — DI makes this visible
4. **Testability is the primary benefit** — swap real dependencies for test doubles

---

## Command-Query Separation

> "Asking a question should not change the answer."
> — Bertrand Meyer

### Core Concept

Command-Query Separation divides methods into two categories:

| Type | Purpose | Return Value | Side Effects |
|------|---------|--------------|--------------|
| **Query** | Return information | Yes | None |
| **Command** | Change state | None (void) | Yes |

**The insight**: Methods that return values should not change observable state. Methods that change state should not return values.

### Why CQS Matters

1. **Reasoning Confidence**: Queries are safe to call anywhere
2. **Testing Simplicity**: Queries tested in isolation
3. **Caching Safety**: Queries can be cached
4. **Parallelization**: Queries run concurrently without race conditions

### Anti-Patterns

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

### Pragmatic Exceptions

- Stack pop operation (atomic)
- Thread-safe increment-and-get
- Database identity generation

### Summary

1. **Separate queries from commands** — Return value OR change state, not both
2. **Queries are safe** — Call them anywhere, cache them, parallelize them
3. **Commands need care** — Order matters, test state changes explicitly
4. **Break CQS pragmatically** — Atomic operations sometimes require both

---

# Reliability & Operations

---

## Fail-Fast & Defensive Programming

> "The best debugging is the debugging you never have to do because you found the problem immediately."
> — Jim Shore

### Core Concept

Fail-fast is the discipline of **detecting and reporting errors at the earliest possible moment**. Rather than allowing invalid state to propagate, fail-fast code validates assumptions immediately and fails loudly.

**Two complementary practices:**
1. **Fail-Fast** — Detect errors early, fail immediately with clear diagnostics
2. **Defensive Programming** — Anticipate misuse, validate at boundaries

### Design by Contract

| Contract | Responsibility | Example |
|----------|---------------|---------|
| **Preconditions** | Caller must satisfy before calling | `assert user_id is not None` |
| **Postconditions** | Method must satisfy before returning | `assert result.is_valid()` |
| **Invariants** | Must hold throughout object lifetime | `assert self.balance >= 0` |

### Common Patterns

```python
# ✅ Guard Clauses - Fail fast at entry
def process_order(order):
    if order is None:
        raise ValueError("order required")
    if not order.items:
        raise ValueError("items required")

# ✅ Config Validation at Startup
def __init__(self):
    self.key = os.getenv("API_KEY")
    if not self.key:
        raise ConfigError("API_KEY required")
```

### Error Handling Strategies

| Error Type | Strategy |
|------------|----------|
| **Precondition violation** | Raise immediately |
| **Transient failure** | Retry with backoff |
| **Deterministic failure** | Fail permanently |
| **Invariant violation** | Assert (crash in dev) |

### Summary

1. **Validate early** — Check inputs at function entry, config at startup
2. **Fail loudly** — Clear error messages beat silent corruption
3. **Distinguish error types** — Transient (retry) vs. deterministic (fail) vs. bug (crash)
4. **Use assertions for invariants** — Things that should never be false
5. **Trust validated data** — Don't re-validate inside trusted boundaries

---

## Design by Contract

> "A software system is not a bunch of components thrown together. It is a construction of interacting elements, connected by clear contracts."
> — Bertrand Meyer

### Core Concept

Design by Contract (DbC) treats software construction as a series of agreements between clients (callers) and suppliers (routines). Every function has a contract: it promises to deliver certain results (postconditions) **if and only if** the caller meets requirements (preconditions).

### The Three Pillars

| Element | Definition | Who Benefits | Who Obligates |
|---------|------------|--------------|---------------|
| **Precondition** | What must be true before | Supplier | Client |
| **Postcondition** | What the routine guarantees | Client | Supplier |
| **Invariant** | What must always be true | Both | Supplier |

### Inheritance Rules (Liskov Substitution)

| Contract Element | Subtype Rule |
|------------------|--------------|
| **Preconditions** | Can only be **weakened** |
| **Postconditions** | Can only be **strengthened** |
| **Invariants** | Can only be **strengthened** |

### DbC vs. Defensive Programming

| Aspect | Design by Contract | Defensive Programming |
|--------|-------------------|----------------------|
| **Philosophy** | Trust but verify at boundaries | Trust no one |
| **Responsibility** | Caller ensures preconditions | Callee handles all cases |
| **When to use** | Internal interfaces | External interfaces |

### Summary

1. **Contracts make responsibilities explicit** — Caller ensures preconditions; supplier ensures postconditions
2. **Invariants define valid object state** — Must hold after construction and every public method
3. **Assertions are executable contracts** — Document and verify simultaneously
4. **DbC complements defensive programming** — Use DbC internally, defensive at boundaries

---

## Resilience & Graceful Degradation

> "In complex systems, failure is the normal state. Success is the special case that requires explanation."
> — Richard Cook

### Core Concept

Resilience is the ability of a system to **continue operating despite partial failures**. Resilient systems anticipate failure, implement recovery strategies, and degrade gracefully.

### The Three Pillars

| Pillar | Purpose | Mechanism |
|--------|---------|-----------|
| **Retry** | Recover from transient failures | Exponential backoff with jitter |
| **Fallback** | Provide degraded service | Cached data, default values |
| **Protect** | Prevent cascade failures | Circuit breakers, timeouts |

### Pattern 1: Exponential Backoff with Jitter

```python
delay = min(base_delay * 2^attempt + random_jitter, max_delay)
```

### Pattern 2: Circuit Breaker

Three states: CLOSED (normal) → OPEN (fail fast) → HALF-OPEN (test recovery)

### Pattern 3: Graceful Degradation

```python
# Cascading fallback strategy
def get_recommendations(user_id: str) -> list[Product]:
    try:
        return recommendation_service.get_personalized(user_id)
    except ServiceUnavailableError:
        cached = cache.get(f"recommendations:{user_id}")
        if cached:
            return cached
        return get_popular_items()  # Final fallback
```

### Summary

1. **Failures are inevitable** — Design for them, don't assume success
2. **Retry with exponential backoff and jitter** — Prevents thundering herd
3. **Only retry transient errors** — Auth failures should fail fast
4. **Use circuit breakers** — Prevent cascading failures
5. **Always set timeouts** — Unbounded waits exhaust resources

---

## Observability & Transparency

> "Observability is the ability to understand the internal state of a system by examining its external outputs."
> — Charity Majors

### Core Concept

**Observability** makes system behavior visible through structured telemetry. In distributed systems, you cannot attach a debugger—observability becomes your primary debugging tool.

### The Three Pillars

1. **Logs**: Chronological records of discrete events with context
2. **Metrics**: Quantitative measurements over time
3. **Traces**: End-to-end journey of requests through distributed systems

### Observability Principles

1. **Structured Over Unstructured**: Use JSON, key-value pairs
2. **Semantic Prefixes**: Emojis for quick visual scanning
3. **Log Levels Match Intent**: DEBUG, INFO, WARNING, ERROR, CRITICAL
4. **Context Flows Through Systems**: Trace IDs, request IDs
5. **Metadata in Responses**: Return operational metadata
6. **Timing Everything Important**: Instrument performance-critical paths

### Anti-Patterns

- **Silent Failures**: Swallowed exceptions
- **Opaque Error Messages**: Generic, unhelpful messages
- **Missing Request Context**: No correlation IDs
- **Over-Logging**: Logging inside tight loops
- **Logging Sensitive Data**: Credentials in logs

### Summary

1. **Observability is your debugger** in production
2. **Structure your logs** for machine parsing and human readability
3. **Propagate context** (request IDs, trace IDs)
4. **Return metadata** in responses for transparency
5. **Never log secrets** — sanitize sensitive data

---

# User Experience

---

## Principle of Least Surprise

> "In interface design, always do the least surprising thing."
> — Eric S. Raymond

### Core Concept

A component should behave in a way that users and developers expect. Never surprise the user. An interface should behave exactly as the user thinks it behaves.

### Strategies for Reducing Surprise

1. **Command-Query Separation**: Separate methods that change state from those that return information
2. **Naming Conventions That Communicate Intent**: Names match behavior
3. **Consistent Return Types**: Methods with similar purposes return similar types
4. **Sensible Defaults**: Default values are the most common, safest choice
5. **No Hidden Side Effects**: Methods only do what signatures and names imply

### Common Anti-Patterns

- **Inconsistent Error Handling**: Different methods handle errors differently
- **Misleading Method Names**: Name implies query, actually mutates
- **Surprising Parameter Order**: Non-standard parameter order
- **Spooky Action at a Distance**: Unexpected effects on unrelated parts

### Summary

1. **Think like your user**: Design based on what users expect
2. **Separate commands from queries**: Methods that return values shouldn't change state
3. **Names must match behavior**: If you can't name it accurately, the design may be wrong
4. **Consistency over cleverness**: Use established patterns
5. **No hidden side effects**: Every behavior explicit in the signature and name

---

## Elegance

> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."
> — Antoine de Saint-Exupéry

### Core Concept

Elegance in code is **beauty through insight**. An elegant program solves its problem with minimum complexity while revealing something fundamental about the domain.

### Four Criteria

| Criterion | Description |
|-----------|-------------|
| **Minimality** | Shortness and simplicity; no superfluous parts |
| **Accomplishment** | Does exactly what it should (non-negotiable) |
| **Modesty** | Restraint; avoids cleverness and showing off |
| **Revelation** | Shows something new about the problem domain |

### Elegance vs. Cleverness

| Elegant Code | Clever Code |
|--------------|-------------|
| Reveals domain insight | Exploits language tricks |
| Reader says "of course!" | Reader says "how does this work?" |
| Survives language changes | Implementation-dependent, fragile |
| Stands alone | Needs explanatory comments |

### Summary

1. **Minimality** — remove everything superfluous
2. **Accomplishment** — it must work correctly
3. **Modesty** — avoid cleverness and showing off
4. **Revelation** — show insight about the domain
5. **Domain symmetry** — understanding the problem suffices to understand the code

---

## References

### Foundational Texts
- *The Pragmatic Programmer* — Andy Hunt & Dave Thomas
- *Clean Code* — Robert C. Martin
- *Design Patterns* — Gang of Four
- *Object-Oriented Software Construction* — Bertrand Meyer

### Online Resources
- [Martin Fowler's Bliki](https://martinfowler.com/bliki/)
- [Refactoring Guru](https://refactoring.guru/)
- [DevIQ Principles](https://deviq.com/principles/)

---

*This document is designed to be dropped into your `.claude/commands/` folder. Run `/deslop [file-or-directory]` to analyze your code against these principles.*
