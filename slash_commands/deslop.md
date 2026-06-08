# Deslop: Code Quality Analysis Command
<sub><sup>Note: This file is ≈27k tokens as of 2026-01-19</sup></sub>

> A comprehensive command `/deslop` or $deslop (depending on your harness) for identifying and fixing "slop" in your codebase. Ask your agent to create a command or skill from this markdown file. Then, restart your agent harness and run `/deslop` or $deslop.

This command combines a code analysis workflow with an extensive library of coding principles. When you run `/deslop [file-or-directory]`, or even just `/deslop` or perhaps `/deslop my frontend typescript code` the AI will read your code, cross-reference it against these principles, and suggest specific fixes with before/after examples.

Whether or not you use this deslop command on your code base, you should read all the coding principles yourself, as a human - you might actually learn something useful.

---

## Table of Contents

- [Deslop: Code Quality Analysis Command](#deslop-code-quality-analysis-command)
  - [Table of Contents](#table-of-contents)
  - [Instructions](#instructions)
    - [Installation](#installation)
    - [Deslop](#deslop)
    - [Check for Updates](#check-for-updates)
  - [Part 1: Clean Code](#part-1-clean-code)
    - [KISS: Keep It Simple, Stupid](#kiss-keep-it-simple-stupid)
    - [YAGNI: You Aren't Gonna Need It](#yagni-you-arent-gonna-need-it)
    - [Small Functions](#small-functions)
    - [Guard Clauses](#guard-clauses)
    - [Cognitive Load](#cognitive-load)
    - [Single Level of Abstraction (SLAP)](#single-level-of-abstraction-slap)
    - [Self-Documenting Code](#self-documenting-code)
    - [Documentation Discipline](#documentation-discipline)
    - [Elegance](#elegance)
    - [Principle of Least Surprise](#principle-of-least-surprise)
  - [Part 3: Architecture](#part-3-architecture)
- [Organization \& Structure](#organization--structure)
  - [DRY: Don't Repeat Yourself](#dry-dont-repeat-yourself)
    - [Core Concept](#core-concept)
    - [The Rule of Three](#the-rule-of-three)
    - [The Wrong Abstraction](#the-wrong-abstraction)
    - [Recognizing True vs. Incidental Duplication](#recognizing-true-vs-incidental-duplication)
    - [Common Violations](#common-violations)
    - [Anti-Patterns](#anti-patterns)
    - [Refactoring Techniques](#refactoring-techniques)
    - [DRY Beyond Code](#dry-beyond-code)
    - [Summary](#summary)
  - [Single Source of Truth](#single-source-of-truth)
    - [Core Concept](#core-concept-1)
    - [SSoT vs. DRY](#ssot-vs-dry)
    - [Common Violations](#common-violations-1)
    - [When Duplication Is Acceptable](#when-duplication-is-acceptable)
    - [Summary](#summary-1)
  - [Separation of Concerns](#separation-of-concerns)
    - [Core Concept](#core-concept-2)
    - [Types of Concerns](#types-of-concerns)
    - [Common Violations](#common-violations-2)
    - [Anti-Patterns](#anti-patterns-1)
    - [Summary](#summary-2)
  - [Modularity](#modularity)
    - [Core Concept](#core-concept-3)
    - [Deep vs. Shallow Modules](#deep-vs-shallow-modules)
    - [Common Violations](#common-violations-3)
    - [Summary](#summary-3)
- [Coupling \& Dependencies](#coupling--dependencies)
  - [Encapsulation](#encapsulation)
    - [Core Concept](#core-concept-4)
    - [Tell, Don't Ask](#tell-dont-ask)
    - [Common Violations](#common-violations-4)
    - [Summary](#summary-4)
  - [Law of Demeter](#law-of-demeter)
    - [Core Concept](#core-concept-5)
    - [The "One Dot" Rule](#the-one-dot-rule)
    - [Formal Definition](#formal-definition)
    - [Exceptions: When Chaining Is Acceptable](#exceptions-when-chaining-is-acceptable)
    - [A Note on Tell-Don't-Ask](#a-note-on-tell-dont-ask)
    - [Summary](#summary-5)
  - [Orthogonality](#orthogonality)
    - [Core Concept](#core-concept-6)
    - [Common Violations](#common-violations-5)
    - [Summary](#summary-6)
  - [Dependency Injection](#dependency-injection)
    - [Core Concept](#core-concept-7)
    - [Three Forms](#three-forms)
    - [Anti-Patterns](#anti-patterns-2)
    - [Service Lifetimes](#service-lifetimes)
    - [Summary](#summary-7)
  - [Composition Over Inheritance](#composition-over-inheritance)
    - [Core Concept](#core-concept-8)
    - [Why Composition Is Preferred](#why-composition-is-preferred)
    - [Anti-Patterns](#anti-patterns-3)
    - [Summary](#summary-8)
- [Design Patterns \& Conventions](#design-patterns--conventions)
  - [SOLID Principles](#solid-principles)
    - [Overview](#overview)
    - [S — Single Responsibility Principle](#s--single-responsibility-principle)
    - [O — Open/Closed Principle](#o--openclosed-principle)
    - [L — Liskov Substitution Principle](#l--liskov-substitution-principle)
    - [I — Interface Segregation Principle](#i--interface-segregation-principle)
    - [D — Dependency Inversion Principle](#d--dependency-inversion-principle)
    - [When NOT to Apply SOLID](#when-not-to-apply-solid)
    - [Detection Checklist](#detection-checklist)
  - [Convention Over Configuration](#convention-over-configuration)
    - [Core Concept](#core-concept-9)
    - [The Power of Defaults](#the-power-of-defaults)
    - [Real-World Examples](#real-world-examples)
    - [When to Apply](#when-to-apply)
    - [Common Violations](#common-violations-6)
    - [The Dark Side](#the-dark-side)
    - [Explicit vs. Implicit Trade-off](#explicit-vs-implicit-trade-off)
    - [Relationship to Other Principles](#relationship-to-other-principles)
    - [Summary](#summary-9)
  - [Command-Query Separation](#command-query-separation)
    - [Core Concept](#core-concept-10)
    - [Why CQS Matters](#why-cqs-matters)
    - [Anti-Patterns](#anti-patterns-4)
    - [Pragmatic Exceptions](#pragmatic-exceptions)
    - [Summary](#summary-10)
  - [Code Reusability](#code-reusability)
    - [Core Concept](#core-concept-11)
    - [Characteristics of Reusable Code](#characteristics-of-reusable-code)
    - [Types of Reuse](#types-of-reuse)
    - [The Reusability Trap](#the-reusability-trap)
    - [Designing for Reusability](#designing-for-reusability)
    - [Common Violations](#common-violations-7)
    - [When Reusability Hurts](#when-reusability-hurts)
    - [Summary](#summary-11)
- [Data \& State](#data--state)
  - [Parse, Don't Validate](#parse-dont-validate)
    - [Core Concept](#core-concept-12)
    - [Validation vs. Parsing](#validation-vs-parsing)
    - [The Shotgun Parsing Anti-Pattern](#the-shotgun-parsing-anti-pattern)
    - [Primitive Obsession](#primitive-obsession)
    - [Make Illegal States Unrepresentable](#make-illegal-states-unrepresentable)
    - [Parse at the Boundary](#parse-at-the-boundary)
    - [Lightweight Parsing with NewType](#lightweight-parsing-with-newtype)
    - [Pydantic: Full-Throttle Parsing](#pydantic-full-throttle-parsing)
    - [Common Violations](#common-violations-8)
    - [When NOT to Apply](#when-not-to-apply)
    - [Summary](#summary-12)
  - [Immutability](#immutability)
    - [Core Concept](#core-concept-13)
    - [Benefits](#benefits)
    - [Common Violations](#common-violations-9)
    - [Python Implementation](#python-implementation)
    - [Summary](#summary-13)
  - [Idempotency](#idempotency)
    - [Core Concept](#core-concept-14)
    - [Implementation Strategies](#implementation-strategies)
    - [Naturally Idempotent Operations](#naturally-idempotent-operations)
    - [Summary](#summary-14)
- [Part III: Reliability](#part-iii-reliability)
- [Robustness \& Safety](#robustness--safety)
  - [Fail-Fast \& Defensive Programming](#fail-fast--defensive-programming)
    - [Core Concept](#core-concept-15)
    - [Design by Contract](#design-by-contract)
    - [Common Patterns](#common-patterns)
    - [Error Handling Strategies](#error-handling-strategies)
    - [Summary](#summary-15)
  - [Design by Contract](#design-by-contract-1)
    - [Core Concept](#core-concept-16)
    - [The Three Pillars](#the-three-pillars)
    - [Inheritance Rules (Liskov Substitution)](#inheritance-rules-liskov-substitution)
    - [DbC vs. Defensive Programming](#dbc-vs-defensive-programming)
    - [Summary](#summary-16)
  - [Postel's Law (Robustness Principle)](#postels-law-robustness-principle)
    - [Core Concept](#core-concept-17)
    - [Real-World Examples](#real-world-examples-1)
    - [When to Apply](#when-to-apply-1)
    - [The Tolerant Reader Pattern](#the-tolerant-reader-pattern)
    - [The Dark Side](#the-dark-side-1)
    - [Modern Balanced Approach](#modern-balanced-approach)
    - [Relationship to Other Principles](#relationship-to-other-principles-1)
    - [Summary](#summary-17)
  - [Resilience \& Graceful Degradation](#resilience--graceful-degradation)
    - [Core Concept](#core-concept-18)
    - [The Three Pillars](#the-three-pillars-1)
    - [Pattern 1: Exponential Backoff with Jitter](#pattern-1-exponential-backoff-with-jitter)
    - [Pattern 2: Circuit Breaker](#pattern-2-circuit-breaker)
    - [Pattern 3: Graceful Degradation](#pattern-3-graceful-degradation)
    - [Summary](#summary-18)
  - [Principle of Least Privilege](#principle-of-least-privilege)
    - [Core Concept](#core-concept-19)
    - [Application at Every Level](#application-at-every-level)
    - [Real-World Failures](#real-world-failures)
    - [Common Violations](#common-violations-10)
    - [Anti-Patterns](#anti-patterns-5)
    - [Implementation Strategies](#implementation-strategies-1)
    - [Privilege Creep](#privilege-creep)
    - [Relationship to Zero Trust](#relationship-to-zero-trust)
    - [Summary](#summary-19)
- [Maintainability \& Operations](#maintainability--operations)
  - [Boy Scout Rule](#boy-scout-rule)
    - [Core Concept](#core-concept-20)
    - [Why It Works](#why-it-works)
    - [What "Better" Looks Like](#what-better-looks-like)
    - [The Campground, Not the Forest](#the-campground-not-the-forest)
    - [Common Violations](#common-violations-11)
    - [When NOT to Apply](#when-not-to-apply-1)
    - [Anti-Patterns](#anti-patterns-6)
    - [Relationship to Other Principles](#relationship-to-other-principles-2)
    - [Summary](#summary-20)
  - [Observability \& Transparency](#observability--transparency)
    - [Core Concept](#core-concept-21)
    - [The Three Pillars](#the-three-pillars-2)
    - [Observability Principles](#observability-principles)
    - [Anti-Patterns](#anti-patterns-7)
    - [Summary](#summary-21)
  - [When to Relax Rules](#when-to-relax-rules)
    - [The Meta-Principle](#the-meta-principle)
  - [References](#references)
    - [Foundational Texts](#foundational-texts)
    - [Seminal Articles \& Essays](#seminal-articles--essays)
    - [Online Resources](#online-resources)
    - [Concept Attribution](#concept-attribution)

---

## Instructions

### Installation

[↑ top](#table-of-contents)

Download this entire markdown file into the location for your agent harness's and then restart your harness and run `/deslop` or $deslop. If you use multiple harnesses, consider using symlinks to avoid multiple sources of truth. Also consider adding this GitHub repository (Theta-Tech-AI/llm_public_utils) as a submodule to another repository It is likely one of the following locations:

- `~/.claude/commands/deslop.md`
- `~/.opencode/commands/deslop.md`
- `~/.agents/skills/deslop.md`
- `/home/code/my_repository_root/.claude/commands/deslop.md`
- `/home/code/my_repository_root/.opencode/commands/deslop.md`
- `/home/code/my_repository_root/.agents/skills/deslop.md`

### Deslop

[↑ top](#table-of-contents)

You are an obsessive code quality analyzer. Your task is to identify "slop" - code that violates established coding principles - and suggest concrete improvements. Unless the user asked you to automatically implement the suggested changes, ask first.

Analyze: $ARGUMENTS

If no argument provided, operate on the current folder or current code base. Read all the coding principles in this file, read target files, identify violations, suggest concrete fixes.

For each violation list:

- **Severity:** Extreme, high, medium, low, or optional.
- **Location:** File path and line number.
- **Violation:** Coding principle violated and why.
- **Summary:** One sentence description of the violation.
- **Improvement:** Suggest a less sloppy way.

### Check for Updates
At the end of each deslop session, when preparing the output, use a programming language of your choice and roll a pair of fair dice. If you roll snake eyes, compare this version of deslop.md to the latest version at https://github.com/Theta-Tech-AI/llm-public-utils/blob/production/slash_commands/deslop.md and tell the user about the differences. The user can decide to update or not.

## Part 1: Clean Code

[↑ top](#table-of-contents)

Write clear, simple, readable code. Do less, but better. Reduce complexity, and make the code easily readable.

---

### KISS: Keep It Simple, Stupid

[↑ top](#table-of-contents)


> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."
> — Antoine de Saint-Exupéry

Complexity kills maintainability, and simple does not necessarily equal easy - simple systems may require skill to build. Aim for the simplest sufficient code - neither incomplete nor over-engineered code.

To avoid unnecessary complexity, look for:

- **Parts Plethora:** Too many parts in the system
- **Interconnectedness:** Too many coupled components.
- **Extra Effort:** Easy tasks should require minimal effort.
- **Cyclomaticism:** Many independent paths through the code
- **Cognitive Complexity:** High mental effort to understand code. Can a new junior dev understand the code upon a glance?
- **Over-Abstractions:** Single-implementation interfaces, factories of factories, deep inheritance, "clever" one-liners.
- **Rationaliations:** Look for violations where it seems coder said to themself: *"This pattern will be useful when..."*, or *"Let me make this more flexible..."*, or *"This is the proper enterprise way..."*
- **Overengineering:** Nested ternaries, cleverness over clarity, premature optimization, caching before profiling, interfaces for single implementations, or speculative generality.
-  **Ego:** Spots where the coder was trying to impress instead of communicate plainly.

---

### YAGNI: You Aren't Gonna Need It

[↑ top](#table-of-contents)

> "Always implement things when you actually need them, never when you just foresee that you need them."
> — Ron Jeffries, XP co-founder

YAGNI is the discipline of **not building functionality until it's required**. Every feature has costs: development, testing, debugging, maintenance, cognitive load, delays, complexity, drift. Features you don't need yet carry these costs without delivering value. Common violations and code smells includes config options no one uses, ABC with one implementation, extensibility points never extended, commented "future" code, or unused API endpoints. Before adding code: **Who needs this today?** (not "might need") — **What breaks without it?** (if nothing, skip it) — **Can we add it later?** (usually yes, with better understanding). Only build what's needed now, delete speculative code, and keep code malleable and maintainable.

**The trap**: *"While I'm here, just in case I need it later, I'll just add..."*

**The reality**: Most speculative features fail to improve their target metrics.

---

### Small Functions

[↑ top](#table-of-contents)

> "The first rule of functions is that they should be small. The second rule of functions is that they should be smaller than that."
> — Robert C. Martin (Uncle Bob), *Clean Code*

Small Functions is the principle that **functions should be short, focused, and do one thing well**. Decompose logic into small, named units that can be understood at a glance, preferably under 15 lines long. Prefer many smaller functions over fewer big functions. Any time you notice yourself figuring out what a few lines of code does, extract it into a small, tight function which is named after that "what". Long functions are a code smell. Large functions are hard to name, do too many things with too many levels of abstraction, and are difficult to test in isolation. Claiming everything is related and needs to go in the same function is simply lazy thinking, and comments do not take the place of well-defined specific functions. Refactor now, not later.

The "Stepdown" rule says functions should read like a top-down narrative of what's going on, descending one level of abstraction at a time. For instance:

```python
def process_order(order: Order) -> Receipt:
    # Reads like a story:
    validate_order(order)
    apply_discounts(order)
    charge_payment(order)
    send_confirmation(order)
    return create_receipt(order)
```

Some code smells to watch out for are:
- 30+ lines long
- Comments separating sections inside the function
- Deeply nested conditionals (3+ levels)
- Functions with "And" in the name (e.g. `validateAndSave`)

Sometimes, larger functions are the better choice if too many files is increasing cognitive load, or the overhead of calling other functions is significantly degrading performance.

```python
# ❌ Too shallow - interface complexity exceeds implementation
def is_empty(collection): return len(collection) == 0
def is_not_empty(collection): return len(collection) > 0

# ✅ Better - meaningful abstraction hiding complexity
def get_active_users(user_ids: list[int]) -> list[User]:
    """Fetches users, filters inactive, sorts by last_active."""
    users = fetch_users_batch(user_ids)
    active = [u for u in users if u.is_active]
    return sorted(active, key=lambda u: u.last_active, reverse=True)
```

The "small function" principle is related to several other principles:

| Principle | Connection |
|-----------|------------|
| **Single Responsibility** | Small Functions is the *how*, SRP is the *what* |
| **Separation of Concerns** | Decompose by concern, then make each piece small |
| **DRY** | Extract duplicated code into small reusable functions |
| **Self-Documenting Code** | Function names replace comments when functions are small |
| **KISS** | Small functions are simpler to understand |

---

### Guard Clauses

[↑ top](#table-of-contents)

> "The guard clause says, 'This is rare, and if it happens, do something and get out.'"
> — Martin Fowler, *Refactoring*

Check for invalidate states at the start of a function and exit early when preconditions are not met. This keeps the "happy path" at outermost indentation and fails fast. Use it for null checks, empty inputs, invalid states, edge cases, or recursive termination. Use it to handle the unhappy cases early, not for selecting between equally weighted paths. For instance:

```python
# ❌ Wrong - Nested conditionals obscure the happy path
def get_pay_amount(employee):
    result = 0
    if employee.is_dead:
        result = dead_amount()
    else:
        if employee.is_separated:
            result = separated_amount()
        else:
            if employee.is_retired:
                result = retired_amount()
            else:
                result = normal_pay_amount()
    return result

# ✅ Correct - Guard clauses make special cases obvious
def get_pay_amount(employee):
    if employee.is_dead:
        return dead_amount()
    if employee.is_separated:
        return separated_amount()
    if employee.is_retired:
        return retired_amount()
    return normal_pay_amount()
```

```python
# ✅ Classic guard clause pattern
def send_welcome_email(user):
    if user is None:
        return
    if not user.email:
        return

    # Main logic at natural indentation
    mailer.send(user.email, "Welcome!")
```

```python
# ❌ Wrong - Guards belong at the top
def process(item):
    item.prepare()
    item.validate()
    if not item.is_ready:  # Too late
        return None
    return item.execute()

# ✅ Correct - Check preconditions first
def process(item):
    if not item.can_process:
        return None
    item.prepare()
    item.validate()
    return item.execute()
```

```python
# ❌ Misleading - Both branches are equally valid
def process_order(order):
    if order.is_express:
        return handle_express_shipping(order)
    return handle_standard_shipping(order)

# ✅ Better - if/else signals equal weight
def process_order(order):
    if order.is_express:
        handle_express_shipping(order)
    else:
        handle_standard_shipping(order)
```

In relation to other principles, guard clauses...

| Principle | Relationship |
|-----------|--------------|
| **Fail-Fast** | Guard clauses are fail-fast's implementation: detect problems immediately and exit |
| **Cognitive Load** | Flattening nested conditionals reduces mental overhead |
| **Small Functions** | Guards work best in small, focused functions |
| **Design by Contract** | Guards enforce preconditions at runtime |

---

### Cognitive Load

[↑ top](#table-of-contents)

> "Cognitive load is how much a developer needs to think in order to complete a task."
> — Artem Zakirullin

Code is read 10x more than it's written. Aim for clarity and readability. It requires effort to understand code and our working memory only holds limited pieces of information with full comprehension. Every clever trick forces readers to hold more in their head. While the developer may have been working on some code for a long time, they're often heavily relying on their long-term memory of how the code works and rarely realize how much cognitive effort it takes for newcomers to understand a piece of code seeing it for the first time. Comments are not an excuse for code that does not increase cognitive load. Clever one-liners, excessive layered approaches, prematurely build microservices, all increase the cognitive burden on the reader of the code.

```python
# ❌ Wrong - Each condition fills working memory
if val > THRESHOLD and (cond_a or cond_b) and (cond_c and not cond_d):
    process(val)  # 🤯 Reader is lost

# ✅ Correct - Named intermediates free working memory
is_above_threshold = val > THRESHOLD
is_allowed = cond_a or cond_b
is_secure = cond_c and not cond_d

if is_above_threshold and is_allowed and is_secure:  # 🧠 Fresh
    process(val)
```

In relation to other principles, cognitive load...

| Principle | Connection |
|-----------|------------|
| **KISS** | Cognitive load is *why* simplicity matters |
| **Self-Documenting Code** | Good names reduce mental translation |
| **Small Functions** | Must balance: too many shallow functions *increase* load |
| **Composition Over Inheritance** | Explicit dependencies reduce hidden context |
| **Modularity** | Deep modules hide complexity behind simple interfaces |

1. **Working memory holds ~4 chunks** — Exceed this and comprehension fails
2. **Reduce extraneous load** — Focus on how code is presented
3. **Familiarity ≠ simplicity** — Code you know feels easy; newcomers feel the burden
4. **Prefer deep modules** — Simple interfaces hiding complex implementations
5. **Write boring code** — The best code requires no mental effort to parse

---

### Single Level of Abstraction (SLAP)

[↑ top](#table-of-contents)

> "The code within a function should operate at a single level of abstraction."
> — Robert C. Martin, Clean Code

Single Level of Abstraction Principle (SLAP) states that **every statement within a function should operate at the same level of abstraction**. When you mix high-level operations (like "process order") with low-level details (like "parse JSON field"), the code becomes harder to read because readers must mentally switch between abstraction levels.

**The key insight**: Switching between levels of abstraction forces mental grouping—readers must mentally construct the missing abstractions by finding which statements belong together.

Abstraction Levels

| Level | Examples |
|-------|----------|
| **High** | `process_order()`, `authenticate_user()`, `generate_report()` |
| **Medium** | `validate_email()`, `calculate_tax()`, `format_response()` |
| **Low** | `strip().upper()`, `int(value)`, `encode('utf-8')` |

Common Violations

```python
# ❌ Wrong - Mixed abstraction levels
def process_order(order_data: dict) -> None:
    user = get_user(order_data["user_id"])  # High-level

    # Low-level detail mixed in
    items = []
    for item in order_data.get("items", []):
        items.append({
            "sku": item["sku"].strip().upper(),
            "qty": int(item.get("quantity", 1))
        })

    validate_inventory(items)  # High-level
    charge_payment(user, calculate_total(items))
    send_confirmation(user)

# ✅ Correct - Single level of abstraction
def process_order(order_data: dict) -> None:
    user = get_user(order_data["user_id"])
    items = parse_order_items(order_data)
    validate_inventory(items)
    charge_payment(user, calculate_total(items))
    send_confirmation(user)
```

The Stepdown Rule

Robert Martin's Stepdown Rule: code should read like a top-down narrative. Each function leads to the next level of abstraction, like a newspaper article—headline first, then summary, then details.

```python
# ✅ Reads top-down at consistent level
def generate_monthly_report(month: int, year: int) -> Report:
    data = fetch_monthly_data(month, year)
    metrics = calculate_metrics(data)
    charts = generate_visualizations(metrics)
    return compile_report(metrics, charts)
```

Detecting Violations

**Smell #1: Loops with inline logic**
```python
# ❌ Extract the loop body
for entity in entities:
    dto = ResultDto()
    dto.shoe_size = entity.shoe_size
    dto.age = compute_age(entity.birthday)
    results.append(dto)

# ✅ Single statement in loop
for entity in entities:
    results.append(to_dto(entity))
```

**Smell #2: Comment + code block**
```python
# ❌ Comment indicates missing abstraction
# Validate email format
if not re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email):
    raise ValueError("Invalid email")

# ✅ Named function replaces comment
validate_email_format(email)
```

Caveats

- **Mental inlining**: Over-extraction forces readers to jump between many tiny functions
- **Simple code doesn't need extraction**: A 3-line function is already at one level
- **Guard clauses are OK**: An initial `if param is None: raise` at a higher-level function is acceptable
- **Performance**: Sometimes inlining is necessary for hot paths

When NOT to Apply

- **Test code**: Explicit inline steps improve test readability
- **Single-use transformations**: Don't extract if it obscures more than clarifies
- **Trivially simple functions**: Extraction for its own sake adds noise

Summary

1. **Every statement at the same abstraction level** — Don't mix orchestration with implementation
2. **Extract when you see mixing** — Loops with logic, comments + code blocks
3. **Use the stepdown rule** — High-level functions call medium-level, which call low-level
4. **Avoid over-extraction** — Balance SLAP against readability (see also: [Small Functions](#small-functions), [Cognitive Load](#cognitive-load), [Separation of Concerns](#separation-of-concerns))

---

### Self-Documenting Code

[↑ top](#table-of-contents)


> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand."
> — Martin Fowler

Code that **conveys purpose** through names, structure, and organization—without relying on comments. Comments explain *why*, code shows *what*.

**Reveals:** What/how (through naming and structure) · **Cannot reveal:** Why/context (requires comments/docs)

The Three Pillars

1. Intention-Revealing Names

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

2. Eliminate Magic Values

Replace hardcoded numbers with named constants.

```python
# ❌ Wrong                    # ✅ Correct
if retry_count > 3:           MAX_RETRIES = 3
    time.sleep(0.5)           RETRY_DELAY_SECONDS = 0.5
                              if retry_count > MAX_RETRIES:
                                  time.sleep(RETRY_DELAY_SECONDS)
```

3. Structured Organization

Each function has one clear purpose. Structure tells the story.

Naming Conventions

| Element | Convention | Examples |
|---------|------------|----------|
| **Variables** | Nouns, fully spelled out | `user_count`, `retry_delay_seconds` |
| **Functions** | Verbs/verb phrases | `calculate_total()`, `validate_input()` |
| **Predicates** | `is_`, `has_`, `can_` prefix | `is_active`, `has_permission` |
| **Classes** | Nouns, PascalCase | `UserAccount`, `OrderProcessor` |
| **Constants** | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |

Common Violations

**Code Smells:** Abbreviations (`usr`, `cnt`), single-letter variables outside tiny scopes, boolean parameters without names, vague function names (`process`, `handle`, `do`).

The Comment Balance

Self-documenting handles **what/how**. Comments handle **why/why not**.

```python
# ✅ Correct - Comment explains why
# Exponential backoff: upstream API rate-limits during peak hours (ISSUE-1234)
for attempt in range(MAX_RETRIES):
    time.sleep(2 ** attempt)
```

Summary

1. **Spell out names completely** — `user_count` not `usr_cnt` (reduces [Cognitive Load](#cognitive-load))
2. **Eliminate magic values** — named constants explain meaning
3. **Structure tells story** — one function, one purpose
4. **Code shows what/how** — comments explain why/why not (see also: [Documentation Discipline](#documentation-discipline))

---

### Documentation Discipline

[↑ top](#table-of-contents)


> "Code tells you how, comments tell you why."
> — Jeff Atwood, Stack Overflow co-founder

Core Concept

**Right documentation at the right level.** Comments don't compile, can't be tested, and rot—yet sometimes they're essential for explaining "why." The discipline: knowing the difference.

The Documentation Pyramid

| Layer | Audience | Purpose |
|-------|----------|---------|
| **README** | New users/devs | First contact, setup, overview |
| **API Docs** | Consumers | Contract, usage, edge cases |
| **Docstrings** | Callers | What it does, params, returns |
| **Inline Comments** | Maintainers | Why this specific implementation |

Move documentation to the highest appropriate level.

When Comments Add Value

```python
# ✅ Why - Business logic rationale
# Orders over $1000 require manager approval per SOX compliance (POLICY-2019-04)
if order.total > MANAGER_APPROVAL_THRESHOLD:
    require_approval(order)

# ✅ Why not - Explaining rejected alternatives
# Using linear search instead of binary: list is always <10 items
# and maintaining sort order would cost more than the lookup savings

# ✅ Workarounds - External constraints
# Firefox doesn't fire mouse events when dragging outside the window.
# Workaround: capture position on mouseLeave and extrapolate.

# ✅ Links - Attribution and context
# Algorithm from https://stackoverflow.com/a/46018816 (CC-BY-SA)

# ✅ Warnings - Prevent future mistakes
# Don't use global isFinite()—it returns true for null values
Number.isFinite(value)
```

Comment Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Parrot comments** | `i += 1  # increment i` | Delete—code already says this |
| **Rotting comments** | Comment describes deleted code | Delete or update |
| **Journal comments** | `// Fixed by John, 3/15` | Use git blame instead |
| **Commented-out code** | Dead code polluting the file | Delete—git has history |
| **Closing brace comments** | `} // end if` | Extract to smaller functions |
| **Mandated comments** | Boilerplate on every method | Comment only when valuable |
| **TODO graveyards** | `// TODO: fix this (2019)` | Create tickets or delete |

```python
# ❌ Wrong - Parrot comment
def calculate_tax(amount):
    tax_rate = 0.08  # Set tax rate to 0.08
    return amount * tax_rate  # Return amount times tax rate

# ✅ Correct - Explains the why
def calculate_tax(amount):
    # California state tax rate as of 2024. Updates tracked in POLICY-TAX-01.
    CA_TAX_RATE = 0.08
    return amount * CA_TAX_RATE
```

The Rot Problem

Comments drift from code silently. Keep close to code, review during code review, delete rather than let rot.

```python
# ❌ Rotting comment - Code changed, comment didn't
def get_users():
    # Returns active users sorted by name
    return User.query.filter_by(status='active').order_by(User.created_at).all()
    # ↑ Now sorted by created_at, comment lies
```

Docstrings Done Right

```python
# ❌ Wrong - Restates the obvious
def add(a: int, b: int) -> int:
    """Add two integers. Args: a: First integer. b: Second integer."""
    return a + b

# ✅ Correct - Documents non-obvious behavior
def calculate_shipping(order: Order) -> Decimal:
    """
    Calculate shipping cost with business rules.

    - Free shipping for orders over $100
    - Hawaii/Alaska adds flat $15 (no free shipping)

    Raises:
        InvalidAddressError: If shipping address is incomplete
    """
```

Relationship to Other Principles

| Principle | Connection |
|-----------|------------|
| **Self-Documenting Code** | Code shows *what/how*; comments explain *why/why not* |
| **DRY** | Don't repeat in comments what the code already says |
| **Single Source of Truth** | One authoritative place for each piece of documentation |
| **Boy Scout Rule** | Fix stale comments when you touch the code |

Summary

1. **Code tells how, comments tell why** — Never explain what code does; explain why it does it
2. **Documentation has layers** — README → API docs → docstrings → inline comments
3. **Comments rot** — Review them during code review; delete rather than let them lie
4. **Anti-patterns abound** — Parrot, journal, and TODO graveyard comments add noise
5. **When in doubt, refactor** — If you need a comment to explain what, the code is unclear

---

### Elegance

[↑ top](#table-of-contents)


> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."
> — Antoine de Saint-Exupéry

Core Concept

**Beauty through insight.** Solves the problem with minimum complexity while revealing something fundamental about the domain.

Four Criteria

| Criterion | Description |
|-----------|-------------|
| **Minimality** | Shortness and simplicity; no superfluous parts |
| **Accomplishment** | Does exactly what it should (non-negotiable) |
| **Modesty** | Restraint; avoids cleverness and showing off |
| **Revelation** | Shows something new about the problem domain |

Elegance vs. Cleverness

| Elegant Code | Clever Code |
|--------------|-------------|
| Reveals domain insight | Exploits language tricks |
| Reader says "of course!" | Reader says "how does this work?" |
| Survives language changes | Implementation-dependent, fragile |
| Stands alone | Needs explanatory comments |

Summary

1. **Minimality** — remove everything superfluous
2. **Accomplishment** — it must work correctly
3. **Modesty** — avoid cleverness and showing off
4. **Revelation** — show insight about the domain
5. **Domain symmetry** — understanding the problem suffices to understand the code

---

### Principle of Least Surprise

[↑ top](#table-of-contents)

> "In interface design, always do the least surprising thing."
> — Eric S. Raymond

Core Concept

Components behave as users expect. Never surprise the user.

Strategies

1. **Command-Query Separation**: Separate state-changing methods from queries
2. **Names match behavior**: Naming conventions communicate intent
3. **Consistent return types**: Similar methods return similar types
4. **Sensible defaults**: Most common, safest choice
5. **No hidden side effects**: Methods do only what signatures imply

Common Anti-Patterns

- **Inconsistent Error Handling**: Different methods handle errors differently
- **Misleading Method Names**: Name implies query, actually mutates
- **Surprising Parameter Order**: Non-standard parameter order
- **Spooky Action at a Distance**: Unexpected effects on unrelated parts

Summary

1. **Think like your user**: Design based on what users expect
2. **Separate commands from queries**: Methods that return values shouldn't change state
3. **Names must match behavior**: If you can't name it accurately, the design may be wrong
4. **Consistency over cleverness**: Use established patterns
5. **No hidden side effects**: Every behavior explicit in the signature and name

---

## Part 3: Architecture

[↑ top](#table-of-contents)

> *Structuring and designing systems. These principles govern how code is organized, how components relate, and how systems are designed for change.*

---

# Organization & Structure

[↑ top](#table-of-contents)

*Where does this code belong? DRY and Single Source of Truth ensure knowledge lives in one place, Separation of Concerns defines boundaries between responsibilities, and Modularity packages those boundaries into self-contained units.*

---

## DRY: Don't Repeat Yourself

[↑ top](#table-of-contents)


> "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."
> — Andy Hunt & Dave Thomas, *The Pragmatic Programmer*

### Core Concept

DRY is about **knowledge**, not code. Avoid duplication of *meaning*, not syntax.

**Two types:**
1. **Knowledge Duplication** — Same business rule in multiple places. **Always fix.**
2. **Incidental Duplication** — Code *looks* similar but represents *different* concepts. **Leave it.** Merging couples unrelated concerns.

### The Rule of Three

> **First time**: Write it. **Second time**: Note it. **Third time**: Abstract it.

Patience to find the *right* abstraction. Two occurrences can't distinguish true duplication from incidental similarity. Three reveal the pattern.

### The Wrong Abstraction

> "Duplication is far cheaper than the wrong abstraction."
> — Sandi Metz

**The sunk cost trap**: Developer A creates an abstraction. Developer B needs similar functionality but not quite—adds a parameter. Developer C adds another. Developer D adds conditionals. Eventually the abstraction becomes incomprehensible, but no one deletes it because of the investment already made.

**The fix**: When an abstraction accumulates conditionals or parameters to handle "just one more case," inline it back into all callers, delete the unnecessary parts, and start fresh. It's cheaper to re-extract than to maintain the wrong abstraction.

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
5. **Beyond code**: Databases, APIs, config, documentation (see also: [Single Source of Truth](#single-source-of-truth))

---

## Single Source of Truth

[↑ top](#table-of-contents)


> "There should be one—and preferably only one—obvious way to store a piece of information."

### Core Concept

**Every piece of data has exactly one authoritative location.** All other references derive from that source. The problem: when data exists in multiple places, which is correct?

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

## Separation of Concerns

[↑ top](#table-of-contents)


> "The separation of concerns, even if not perfectly possible, is yet the only available technique for effective ordering of one's thoughts."
> — Edsger W. Dijkstra

### Core Concept

**Decompose systems into distinct parts, each addressing one concern.** A "concern" = any aspect of functionality (business logic, persistence, UI, etc.).

**Measures:** High cohesion (related things together) · Low coupling (unrelated things independent)

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

## Modularity

[↑ top](#table-of-contents)


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

# Coupling & Dependencies

[↑ top](#table-of-contents)

*How do components relate to each other? These principles minimize unhealthy dependencies. Encapsulation hides internal state, Law of Demeter limits knowledge of other objects, Orthogonality ensures independent change, Dependency Injection makes dependencies explicit, and Composition Over Inheritance favors flexible composition.*

---

## Encapsulation

[↑ top](#table-of-contents)


> "Ask not what an object knows; ask what it can do for you."

### Core Concept

**Bundle data with behavior, hide internals behind interfaces.**

1. **Bundling**: Group related data and behavior
2. **Information Hiding**: Restrict direct access to internal state

### Tell, Don't Ask

Don't query state and decide externally—tell the object what to do.

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
4. **Protect invariants** — Use access control to enforce object validity (see also: [Parse, Don't Validate](#parse-dont-validate))

---

## Law of Demeter

[↑ top](#table-of-contents)


> "Each unit should have only limited knowledge about other units: only talk to your immediate friends; don't talk to strangers."
> — Ian Holland

### Core Concept

**Limit knowledge of other objects' structure.** Only interact with immediate dependencies, not through them.

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

### A Note on Tell-Don't-Ask

> "Tell-Don't-Ask encourages moving behavior into objects, but don't become a Getter Eradicator."
> — Martin Fowler

Objects sometimes collaborate effectively by *providing* information. Transformers that simplify data for clients (like `EmbeddedDocument`) are valid query methods. The principle is about co-locating behavior with data, not eliminating all accessors.

### Summary

1. **Only talk to immediate friends** — don't reach through objects
2. **One dot rule** — `a.b()` good, `a.b().c()` suspect
3. **Tell, don't ask** — command objects, don't interrogate (see also: [Encapsulation](#encapsulation))
4. **Exceptions exist** — builders, fluent APIs, DTOs are fine

---

## Orthogonality

[↑ top](#table-of-contents)


> "Eliminate effects between unrelated things. Design self-contained components: independent, and with a single, well-defined purpose."
> — Andy Hunt & Dave Thomas

### Core Concept

**Changes in one component don't affect others.** Like a helicopter with coupled controls: fix one bug, two more pop up elsewhere.

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

[↑ top](#table-of-contents)


> "The key benefit of Dependency Injection is that it removes the dependency that a class has on a concrete implementation."
> — Martin Fowler

### Core Concept

Dependencies "injected" from outside rather than created internally. A class declares what it needs, not how to get it.

### Three Forms

1. **Constructor Injection** (Preferred): Through constructor
2. **Setter Injection**: Through setters after construction
3. **Interface Injection**: Dependency provides injector method

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

## Composition Over Inheritance

[↑ top](#table-of-contents)


> "Favor object composition over class inheritance."
> — Gang of Four, *Design Patterns*

### Core Concept

**Build complex behavior by combining objects rather than extending classes.**

- **Inheritance** ("is-a"): White-box — subclass sees parent internals
- **Composition** ("has-a"): Black-box — interact via interfaces only

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

# Design Patterns & Conventions

[↑ top](#table-of-contents)

*Proven approaches to common problems. SOLID provides five foundational OO principles, Convention Over Configuration reduces boilerplate through sensible defaults, Command-Query Separation distinguishes actions from queries, and Code Reusability addresses when and how to make code reusable.*

---

## SOLID Principles

[↑ top](#table-of-contents)


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

## Convention Over Configuration

[↑ top](#table-of-contents)


> "You're not a beautiful and unique snowflake. By giving up vain individuality, you can leapfrog the toils of mundane decisions, and make faster progress in areas that really matter."
> — David Heinemeier Hansson, The Rails Doctrine

### Core Concept

**Sensible defaults that work out of the box.** Explicit configuration only when deviating from norm. Core insight: most decisions aren't worth making—if 90% use `id` as primary key, don't force specification.

### The Power of Defaults

| Without CoC | With CoC |
|------------|----------|
| Specify database table name for every model | `User` class → `users` table automatically |
| Configure primary key column | `id` assumed unless overridden |
| Define foreign key naming | `user_id` derived from `User` association |
| Set up file locations manually | `app/models/`, `app/views/`, etc. by convention |

Conventions compose: `has_many :posts` resolves `Post` → `posts` table → `user_id` FK automatically.

### Real-World Examples

| Framework | Convention | Override When Needed |
|-----------|-----------|---------------------|
| **Rails** | `User` → `users` table | `self.table_name = "legacy_accounts"` |
| **Spring Boot** | Auto-configure from classpath | `@Configuration` for custom beans |
| **Django** | `model_name` → `appname_modelname` table | `class Meta: db_table = "custom"` |
| **Next.js** | `pages/about.js` → `/about` route | Custom routing configuration |
| **pytest** | `test_*.py` files auto-discovered | `pytest.ini` for custom patterns |

### When to Apply

| Good Fit | Poor Fit |
|----------|----------|
| Repeated patterns across projects | Highly unique domain requirements |
| Reducing boilerplate for common cases | Legacy systems with established conventions |
| Framework/library design | When explicitness aids understanding |
| Lowering barriers for beginners | Security-critical configurations |

### Common Violations

```python
# ❌ Wrong - Forcing configuration for obvious defaults
class UserService:
    def __init__(
        self,
        table_name: str,
        id_column: str,
        created_at_column: str,
        updated_at_column: str,
    ):
        self.table_name = table_name
        self.id_column = id_column
        # ... exhausting

# Usage requires specifying everything
service = UserService(
    table_name="users",
    id_column="id",
    created_at_column="created_at",
    updated_at_column="updated_at"
)

# ✅ Correct - Sensible defaults with escape hatches
class UserService:
    def __init__(
        self,
        table_name: str = "users",
        id_column: str = "id",
        timestamps: bool = True,
    ):
        self.table_name = table_name
        self.id_column = id_column
        self.timestamps = timestamps

# Usage: zero config for common case
service = UserService()  # Just works

# Override only what differs
legacy_service = UserService(table_name="legacy_accounts")
```

### The Dark Side

1. **Hidden Magic** — implicit behavior hard to debug
2. **Learning Cliff** — must learn convention to deviate
3. **Rigidity at Scale** — common-case optimizations may not scale

```python
# When convention fails: trying to use a legacy database
# Rails convention: User → users table
# Reality: Legacy DB uses "tbl_usr_accounts"
# Now you're fighting the framework instead of working with it
```

### Explicit vs. Implicit Trade-off

| Approach | Advantages | Disadvantages |
|----------|-----------|---------------|
| **Explicit (Configuration)** | Clear, searchable, no surprises | Verbose, repetitive, decision fatigue |
| **Implicit (Convention)** | Concise, consistent, fast start | Hidden behavior, learning curve |

**Python's "Explicit > implicit"** seems contradictory. Resolution: conventions must be *discoverable* and well-documented.

### Relationship to Other Principles

| Principle | Relationship |
|-----------|-------------|
| **KISS** | Both reduce unnecessary complexity; CoC removes decision complexity |
| **YAGNI** | Don't configure what you don't need to configure |
| **DRY** | Conventions eliminate repetitive configuration |
| **Cognitive Load** | Fewer decisions = lower mental burden |
| **Principle of Least Surprise** | Good conventions match developer expectations |

### Summary

1. **Provide sensible defaults** — Common cases should require zero configuration
2. **Allow overrides** — Escape hatches for when convention doesn't fit
3. **Conventions compose** — Build deeper abstractions from consistent patterns
4. **Document the magic** — Implicit behavior must be discoverable
5. **Know when to deviate** — Convention serves you until it doesn't; then configure explicitly

---

## Command-Query Separation

[↑ top](#table-of-contents)


> "Asking a question should not change the answer."
> — Bertrand Meyer

### Core Concept

| Type | Purpose | Returns | Side Effects |
|------|---------|---------|--------------|
| **Query** | Return info | Yes | None |
| **Command** | Change state | None | Yes |

Methods returning values shouldn't change state. Methods changing state shouldn't return values.

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

## Code Reusability

[↑ top](#table-of-contents)


> "A little copying is better than a little dependency."
> — Rob Pike

### Core Concept

**Code usable in multiple contexts without modification.** Unlike DRY (eliminating existing duplication), reusability is forward-looking.

**The paradox**: Reusable components cost 3-10x more to develop. Payoff only materializes with actual reuse.

### Characteristics of Reusable Code

| Trait | Description |
|-------|-------------|
| **Modular** | Self-contained with minimal external dependencies |
| **Generic** | Handles a range of inputs without modification |
| **Well-documented** | Clear API, usage examples, edge cases documented |
| **Stable Interface** | Public API changes infrequently |
| **Thoroughly Tested** | Works reliably across scenarios |

### Types of Reuse

| Type | Scope | Example |
|------|-------|---------|
| **Copy-paste** | Lowest | Snippets, templates |
| **Functions** | Local | Utility functions within a project |
| **Libraries** | Organization | Shared packages across teams |
| **Frameworks** | Industry | Django, React, Rails |

### The Reusability Trap

Designing for reuse before proving need creates complexity without value. Rule of Three applies: wait until three different contexts.

**Santa Claus Problem**: A billion open source components—finding, learning, and integrating often costs more than the reuse saves.

```python
# ❌ Wrong - Premature reusability (YAGNI violation)
class GenericDataProcessor:
    """Handles any data format with any transformation."""
    def __init__(self, parser, transformer, validator, serializer):
        self.parser = parser
        self.transformer = transformer
        self.validator = validator
        self.serializer = serializer

    def process(self, data, options=None):
        options = options or {}
        parsed = self.parser.parse(data, **options.get('parse', {}))
        transformed = self.transformer.transform(parsed, **options.get('transform', {}))
        if options.get('validate', True):
            self.validator.validate(transformed)
        return self.serializer.serialize(transformed, **options.get('serialize', {}))

# ✅ Correct - Start specific, generalize when needed
def parse_user_csv(csv_data: str) -> list[dict]:
    """Parse user data from CSV format."""
    rows = csv_data.strip().split('\n')
    headers = rows[0].split(',')
    return [dict(zip(headers, row.split(','))) for row in rows[1:]]
```

### Designing for Reusability

When code has proven its need for reuse, apply these principles:

**1. Minimize Dependencies**
```python
# ❌ Wrong - Tight coupling to specific libraries
def format_date(date):
    import pandas as pd  # Heavy dependency for simple task
    return pd.Timestamp(date).strftime('%Y-%m-%d')

# ✅ Correct - Use standard library
from datetime import datetime

def format_date(date: datetime) -> str:
    return date.strftime('%Y-%m-%d')
```

**2. Accept Abstract Inputs**
```python
# ❌ Wrong - Only accepts specific type
def process_users(users: list[User]) -> None:
    for user in users:
        send_email(user.email)

# ✅ Correct - Accept any iterable of objects with email
from typing import Protocol, Iterable

class HasEmail(Protocol):
    email: str

def process_contacts(contacts: Iterable[HasEmail]) -> None:
    for contact in contacts:
        send_email(contact.email)
```

**3. Provide Sensible Defaults**
```python
# ❌ Wrong - Requires all parameters
def retry(func, max_retries, delay, backoff_factor, exceptions):
    ...

# ✅ Correct - Sensible defaults, only specify what differs
def retry(
    func,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
):
    ...
```

### Common Violations

**Code Smells**:
- Over-parameterized functions trying to handle every case
- Components that can't be tested in isolation
- Libraries that require complex configuration before basic use
- Code with implicit dependencies on global state

**Organizational Barriers**:
- Politics: Teams block other teams from using "their" code
- Psychology: Developers view reuse as stifling creativity
- NIH Syndrome: "Not Invented Here" bias against external solutions

### When Reusability Hurts

Verbose, redundant code sometimes beats elegant abstractions:
- **Debugging**: Isolated code means problems stay isolated
- **Onboarding**: Simple duplication is easier to understand than clever abstractions
- **Change velocity**: Modifying copy-pasted code can't break other systems
- **Coupling**: "Reusable" components become coupling points across systems

The construction paradox: demolishing and rebuilding often costs less than renovating. Similarly, rewriting 50 lines sometimes beats understanding 500 lines of "reusable" framework code.

### Summary

1. **Reusability is earned, not designed** — Wait for three use cases before investing
2. **Upfront cost is real** — Reusable code costs more to develop and understand
3. **Dependencies are the enemy** — Minimize external coupling; a little copying beats a little dependency
4. **Simple duplication can be better** — Isolated, obvious code often beats clever abstractions
5. **Stable interfaces enable reuse** — Public APIs should change rarely

---

# Data & State

[↑ top](#table-of-contents)

*How should data flow and behave? Parse Don't Validate transforms unstructured input into typed domain objects at boundaries. Immutability eliminates bugs by preventing state changes after creation. Idempotency ensures operations can be safely repeated.*

---

## Parse, Don't Validate

[↑ top](#table-of-contents)

> "A parser is just a function that consumes less-structured input and produces more-structured output."
> — Alexis King

### Core Concept

**Transform data into precise types that make illegal states unrepresentable.** Validation checks then forgets. Parsing checks and *remembers* in the type system.

### Validation vs. Parsing

```python
# ❌ Wrong - Validation: checks then discards knowledge
def validate_non_empty(items: list) -> None:
    if not items:
        raise ValueError("List cannot be empty")
    # Returns nothing—knowledge is lost

def process(items: list) -> None:
    validate_non_empty(items)
    first = items[0]  # Caller must trust validation happened

# ✅ Correct - Parsing: checks and returns proof
from typing import NewType, TypeVar
T = TypeVar('T')
NonEmptyList = NewType('NonEmptyList', list)

def parse_non_empty(items: list[T]) -> NonEmptyList[T]:
    if not items:
        raise ValueError("List cannot be empty")
    return NonEmptyList(items)  # Type proves non-emptiness

def process(items: NonEmptyList[T]) -> None:
    first = items[0]  # Type guarantees safety—no trust needed
```

### The Shotgun Parsing Anti-Pattern

Checks spread everywhere hoping to catch bad data:
1. **Redundant checks**: Same validation repeated
2. **Inconsistent coverage**: Easy to miss checks
3. **Rollback hell**: Invalid data after partial processing
4. **Silent corruption**: Invalid state if check forgotten

```python
# ❌ Wrong - Shotgun parsing
def get_user(user_id: str) -> User:
    if not user_id:
        raise ValueError("user_id required")
    ...

def update_user(user_id: str, data: dict) -> None:
    if not user_id:  # Repeated check!
        raise ValueError("user_id required")
    ...

# ✅ Correct - Parse once at the boundary
UserId = NewType('UserId', str)

def parse_user_id(raw: str) -> UserId:
    if not raw or not raw.strip():
        raise ValueError("user_id required")
    return UserId(raw.strip())

def get_user(user_id: UserId) -> User: ...      # No validation needed
def update_user(user_id: UserId, data: dict): ...  # Type guarantees validity
```

### Primitive Obsession

Over-reliance on `str`, `int`, `dict` for domain concepts. Primitives carry no context—validation knowledge is lost.

```python
# ❌ Wrong - Primitive obsession
def create_order(customer_id: str, product_id: str, quantity: int, price: float): ...
# Easy to swap customer_id/product_id; negative quantity allowed; what currency?

# ✅ Correct - Domain types encode constraints
def create_order(customer_id: CustomerId, product_id: ProductId,
                 quantity: PositiveInt, price: Money): ...
```

### Make Illegal States Unrepresentable

```python
# ❌ Wrong - Invalid states representable
@dataclass
class Order:
    status: str  # "pending", "shipped", "delivered"
    shipped_at: datetime | None  # Bug: can be None when status="shipped"

# ✅ Correct - Invalid states unrepresentable
@dataclass
class PendingOrder:
    items: list[Item]

@dataclass
class ShippedOrder:
    items: list[Item]
    shipped_at: datetime  # Required—impossible to forget

Order = PendingOrder | ShippedOrder | DeliveredOrder
```

### Parse at the Boundary

```python
# ❌ Wrong - Raw data flows through system
def handle_request(request: dict) -> Response:
    user_id = request.get("user_id")
    if not user_id:
        raise ValueError("user_id required")
    # More validation scattered deeper...

# ✅ Correct - Parse at boundary, use typed data internally
@dataclass(frozen=True)
class CreateUserRequest:
    user_id: UserId
    email: Email
    age: PositiveInt

def parse_request(raw: dict) -> CreateUserRequest:
    return CreateUserRequest(
        user_id=parse_user_id(raw.get("user_id", "")),
        email=parse_email(raw.get("email", "")),
        age=parse_positive_int(raw.get("age", 0)),
    )

def handle_request(request: CreateUserRequest) -> Response:
    ...  # All data already validated
```

### Lightweight Parsing with NewType

`NewType` marks validated data without runtime overhead:

```python
from typing import NewType

UserId = NewType('UserId', str)  # Still a str at runtime

def parse_user_id(raw: str) -> UserId:
    if not raw or not raw.startswith("U"):
        raise ValueError("Invalid user ID")
    return UserId(raw)

def load_user(user_id: UserId) -> User: ...

load_user(parse_user_id(url))  # ✅ OK
load_user("U6789679")  # ❌ Type checker error
```

### Pydantic: Full-Throttle Parsing

```python
from pydantic import BaseModel, TypeAdapter

class User(BaseModel):
    username: str
    age: int  # Coerced from string automatically
    last_login: datetime

users = TypeAdapter(list[User]).validate_json(raw_json)
```

### Common Violations

- **Functions returning `None` after validation** — Return the proof instead
- **Boolean flags instead of types** — `is_valid: bool` vs. `ValidatedData` type
- **Re-validating inside trusted code** — Parse at boundaries only
- **Passing raw dicts through layers** — Parse to domain types at the edge
- **Using `str` for everything** — Email, phone, SSN as `str` is primitive obsession

### When NOT to Apply

- **Quick scripts**: Overhead of custom types may not pay off
- **Performance-critical paths**: Sometimes primitives are faster
- **Prototyping**: Over-engineering types slows exploration
- **Simple CRUD**: Not every field needs a custom type

### Summary

1. **Parsers return proof, validators return nothing** — Transform data into types that encode validity
2. **Parse at the boundary** — Convert external data to domain types immediately
3. **Make illegal states unrepresentable** — Design types where invalid combinations can't exist
4. **Eliminate shotgun parsing** — Centralize validation, then trust the types
5. **Avoid primitive obsession** — Use domain types instead of raw `str`/`int`
6. **Choose parsing depth** — `NewType` for lightweight, classes for rich, Pydantic for full (see also: [Fail-Fast](#fail-fast--defensive-programming), [Design by Contract](#design-by-contract), [Encapsulation](#encapsulation), [Immutability](#immutability))

---

## Immutability

[↑ top](#table-of-contents)


> "Immutable types are safer from bugs, easier to understand, and more ready for change."
> — MIT 6.005 Software Construction

### Core Concept

**Once created, state cannot be modified.** Create new structures with desired changes instead.

Mutable shared state causes most concurrency and aliasing bugs. Immutability eliminates them by design.

### Benefits

- **Thread safety without locks**: Share freely between threads
- **No defensive copying**: Share directly
- **Simpler reasoning**: Only understand creation site
- **Safe hash keys**: Can be dictionary keys
- **Enables caching**: Results remain valid indefinitely

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
4. **Prefer immutability** — use frozen dataclasses, tuples, frozensets (see also: [Parse, Don't Validate](#parse-dont-validate))

---

## Idempotency

[↑ top](#table-of-contents)


> "An operation is idempotent if performing it multiple times has the same effect as performing it once."

### Core Concept

**Multiple executions produce same result as one.** In distributed systems, duplicate requests are inevitable—design around them.

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

# Part III: Reliability

[↑ top](#table-of-contents)

> *Building robust, maintainable systems. These principles govern how code handles errors, maintains itself over time, and operates in production.*

---

# Robustness & Safety

[↑ top](#table-of-contents)

*How does code handle the unexpected? Fail-Fast detects errors early, Design by Contract makes expectations explicit, Postel's Law enables interoperability, Resilience keeps systems running despite failures, and Principle of Least Privilege limits damage from breaches.*

---

## Fail-Fast & Defensive Programming

[↑ top](#table-of-contents)


> "The best debugging is the debugging you never have to do because you found the problem immediately."
> — Jim Shore

### Core Concept

**Detect and report errors at the earliest possible moment.** Don't let invalid state propagate.

1. **Fail-Fast** — Detect early, fail immediately with clear diagnostics
2. **Defensive Programming** — Anticipate misuse, validate at boundaries

### Design by Contract

[↑ top](#table-of-contents)

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
4. **Use assertions for invariants** — Things that should never be false (see also: [Design by Contract](#design-by-contract))
5. **Trust validated data** — Don't re-validate inside trusted boundaries (see also: [Parse, Don't Validate](#parse-dont-validate))

---

## Design by Contract

[↑ top](#table-of-contents)


> "A software system is not a bunch of components thrown together. It is a construction of interacting elements, connected by clear contracts."
> — Bertrand Meyer

### Core Concept

**Agreements between callers and routines.** Functions promise results (postconditions) **if** callers meet requirements (preconditions).

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
3. **Assertions are executable contracts** — Document and verify simultaneously (see also: [Fail-Fast](#fail-fast--defensive-programming))
4. **DbC complements defensive programming** — Use DbC internally, defensive at boundaries

---

## Postel's Law (Robustness Principle)

[↑ top](#table-of-contents)


> "Be conservative in what you send, be liberal in what you accept."
> — Jon Postel, RFC 793 (1981)

### Core Concept

**Conservative output, liberal input.** Generate strictly conformant output; accept non-conformant input if meaning is clear. Instrumental in Internet's growth.

- **Conservative output** — Follow specs exactly
- **Liberal input** — Accept reasonable variations

### Real-World Examples

| System | How Postel's Law Applied | Outcome |
|--------|-------------------------|---------|
| **HTML Browsers** | Render malformed HTML gracefully | Web grew explosively; browser code became nightmarishly complex |
| **Unix Pipes** | Tools accept varied input, produce consistent output | Composable ecosystem; `cat`, `grep`, `sort` chain reliably |
| **SMTP Email** | Accept lines >998 chars despite spec limit | Pragmatic interop; many systems now depend on non-standard behavior |
| **JSON APIs** | Ignore unknown fields | Forward-compatible evolution; old clients work with new servers |

### When to Apply

| Context | Recommendation |
|---------|----------------|
| **Protocol extensions** | Ignore unknown fields; don't reject |
| **Public APIs** | Accept variations; can't control all clients |
| **Backward compatibility** | Old clients shouldn't break with new servers |
| **Security-critical input** | Validate strictly; liberal acceptance creates attack surface |
| **Internal systems** | Strict validation catches bugs early |

### The Tolerant Reader Pattern

Ignore unknown fields rather than failing:

```python
# ❌ Wrong - Strict parsing breaks when API adds fields
def parse_user(data: dict) -> User:
    if set(data.keys()) != {"id", "name", "email"}:
        raise ValueError("Unexpected fields in response")
    return User(id=data["id"], name=data["name"], email=data["email"])

# ✅ Correct - Tolerant reader ignores unknown fields
def parse_user(data: dict) -> User:
    return User(
        id=data["id"],       # Required: fail if missing
        name=data["name"],   # Required: fail if missing
        email=data["email"]  # Required: fail if missing
        # Unknown fields silently ignored - forward compatible
    )
```

### The Dark Side

Postel's Law has significant criticisms in modern hostile environments:

| Problem | Description |
|---------|-------------|
| **Specification Rot** | Receivers accept malformed input → senders never fix bugs → incorrect behavior becomes de facto standard |
| **Security Vulnerabilities** | "Reasonable" input may be crafted to exploit edge cases |
| **Hidden Bugs** | Liberal receivers mask sender bugs; problems surface years later |
| **Bug-for-Bug Compatibility** | New implementations must replicate bugs to maintain compatibility |

**HTML Lesson**: Browser tolerance enabled rapid growth but created nightmares—"incorrect" became the only way.

### Modern Balanced Approach

```python
# ✅ Balance: strict where it matters, tolerant for extensibility
def process_webhook(data: dict) -> None:
    # STRICT: Validate required fields (fail-fast)
    if "event_type" not in data:
        raise ValueError("Missing required field: event_type")
    if "timestamp" not in data:
        raise ValueError("Missing required field: timestamp")

    # TOLERANT: Ignore unknown fields (enables future extensions)
    event_type = data["event_type"]
    payload = data.get("payload", {})

    # CONSERVATIVE: Output follows strict contract
    handle_event(event_type, payload)
```

### Relationship to Other Principles

| Principle | Relationship |
|-----------|-------------|
| **Fail-Fast** | Tension: liberal acceptance delays failure detection; balance by validating *required* fields strictly |
| **Resilience** | Supportive: liberal acceptance aids graceful degradation |
| **Principle of Least Surprise** | Supportive: conservative output is predictable |
| **Defensive Programming** | Tension: strict boundary validation vs. liberal acceptance |

### Summary

1. **Conservative output, liberal input** — Generate strictly, accept generously
2. **Enables extensibility** — Unknown fields should be ignored, not rejected
3. **Has a dark side** — Masks bugs, enables specification rot, creates security risks
4. **Context matters** — Liberal for interop and extensibility; strict for security
5. **Modern balance** — Validate required fields strictly, ignore unknowns, output predictably

---

## Resilience & Graceful Degradation

[↑ top](#table-of-contents)


> "In complex systems, failure is the normal state. Success is the special case that requires explanation."
> — Richard Cook

### Core Concept

**Continue operating despite partial failures.** Anticipate failure, implement recovery, degrade gracefully.

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

## Principle of Least Privilege

[↑ top](#table-of-contents)


> "Every program and every user of the system should operate using the least set of privileges necessary to complete the job."
> — Jerome Saltzer, *Protection and the Control of Information Sharing in Multics* (1974)

### Core Concept

**Minimum permissions necessary for intended function—nothing more.**

1. **Minimize Attack Surface** — Fewer permissions = fewer entry points
2. **Limit Blast Radius** — Contain damage when breaches occur

74% of breaches start with privileged credential abuse.

### Application at Every Level

| Level | Example |
|-------|---------|
| **Function** | A function that reads config shouldn't have write access |
| **Class** | A `ReportGenerator` shouldn't have user deletion capabilities |
| **Service** | A payment microservice shouldn't access user profile data |
| **Account** | A database user for reads shouldn't have DROP TABLE privileges |

### Real-World Failures

| Breach | What Happened | PoLP Failure |
|--------|---------------|--------------|
| **Equifax (2017)** | 143M records stolen; attackers executed 9,000 DB queries | Permissive access controls; no network segmentation |
| **Target (2013)** | 40M credit cards via HVAC vendor | Third-party had excessive network access |

### Common Violations

**Code Smells**: Service accounts with `*` wildcard permissions, database connections with admin privileges, shared credentials across services, functions that accept more capabilities than needed.

**Verbal Cues**: "Just give it admin access, it's easier", "We'll lock it down later", "It needs these permissions for debugging"

### Anti-Patterns

```python
# ❌ Wrong - Over-privileged database connection
def get_user_email(user_id: int) -> str:
    conn = get_admin_connection()  # Has DELETE, DROP, etc.
    return conn.execute("SELECT email FROM users WHERE id = ?", user_id)

# ✅ Correct - Minimal privileges for the task
def get_user_email(user_id: int) -> str:
    conn = get_readonly_connection()  # Only SELECT privilege
    return conn.execute("SELECT email FROM users WHERE id = ?", user_id)
```

```python
# ❌ Wrong - Function accepts overly broad context
def send_notification(user: User, db: DatabaseAdmin):
    email = db.query(f"SELECT email FROM users WHERE id = {user.id}")
    # db could delete the entire users table!

# ✅ Correct - Function receives only what it needs
def send_notification(email: str):
    send_email(email, "Your notification...")  # Cannot access database
```

```yaml
# ❌ Wrong - IAM policy with wildcard
Effect: Allow
Action: "s3:*"
Resource: "*"

# ✅ Correct - Scoped to specific actions and resources
Effect: Allow
Action: ["s3:GetObject", "s3:PutObject"]
Resource: "arn:aws:s3:::my-bucket/uploads/*"
```

### Implementation Strategies

| Strategy | Description |
|----------|-------------|
| **Default deny** | Start with no access, explicitly grant what's needed |
| **Separate accounts by function** | Different credentials for read vs. write operations |
| **Time-bounded access** | Temporary elevated privileges that expire |
| **Audit unused permissions** | Regularly review and remove permissions not being used |

### Privilege Creep

Permissions accumulate beyond current needs: role changes without revocation, temporary access becoming permanent, misleading role names.

**Prevention**: Regular access reviews, automated permission expiration, minimal scope at design time.

### Relationship to Zero Trust

| Framework | Focus |
|-----------|-------|
| **Zero Trust** | Verify identity ("never trust, always verify") |
| **Least Privilege** | Limit access ("need to know") |

Partners: Zero Trust authenticates requests; PoLP limits authenticated access. Defense in depth.

### Summary

1. **Grant minimum necessary permissions** — Start with nothing, add only what's required
2. **Scope permissions tightly** — Specific resources, specific actions, specific time windows
3. **Separate credentials by function** — Read-only users for reads, write users for writes
4. **Audit and prune regularly** — Permissions accumulate; actively remove unused access
5. **Design for minimal access** — Functions, classes, and services should request only what they need

---

# Maintainability & Operations

[↑ top](#table-of-contents)

*Code is a living artifact. The Boy Scout Rule keeps code improving incrementally with every change, while Observability & Transparency ensure you can understand what your systems are doing in production.*

---

## Boy Scout Rule

[↑ top](#table-of-contents)


> "Always leave the code better than you found it."
> — Robert C. Martin (Uncle Bob), *Clean Code*

### Core Concept

**With each commit, leave code slightly better than you found it.** Without active maintenance, technical debt accumulates. Continuous small improvements beat periodic "refactoring sprints."

### Why It Works

| Traditional Approach | Boy Scout Rule |
|---------------------|----------------|
| Accumulate debt, then "refactoring sprint" | Continuous small improvements |
| Cleanup disrupts feature delivery | Cleanup happens alongside features |
| Requires dedicated time allocation | Built into every commit |
| Big changes = big risk | Small changes = low risk |
| Code rot between sprints | Code improves continuously |

### What "Better" Looks Like

Small improvements that take seconds to minutes:

| Category | Examples |
|----------|----------|
| **Naming** | Rename `$a` to `$account`, `proc()` to `process_order()` |
| **Cleanup** | Remove unused imports, dead code, extra blank lines |
| **Deprecations** | Replace deprecated API calls with current alternatives |
| **Formatting** | Fix inconsistent indentation, add missing whitespace |
| **Duplication** | Extract repeated logic into a helper (if pattern is proven) |
| **Clarity** | Simplify a complex conditional into a named method |

### The Campground, Not the Forest

Clean the campground, not the entire forest.

```python
# ❌ Wrong - Changed 350 files to remove blank lines project-wide
# This makes code review impossible and introduces huge risk

# ✅ Correct - Cleaned up the file you're actually working in
def process_order(order_id: int) -> Order:
    # While adding this method, noticed and fixed:
    # - Renamed 'o' to 'order'
    # - Removed unused import
    # - Fixed inconsistent indentation
    order = self.repository.get(order_id)
    return self.apply_discount(order)
```

Scope cleanup to files you're already touching. Issues elsewhere? Create a ticket.

### Common Violations

**Code Smells Left Behind**:
- Ignoring deprecation warnings
- Leaving unused variables/imports
- Not fixing obvious naming issues
- Copying code instead of extracting

**Verbal Cues**:
- "I'll clean it up later" (you won't)
- "That's not my code"
- "It works, don't touch it"
- "We need a refactoring sprint"

### When NOT to Apply

**Exceptions**:
- **Unfamiliar code**: Don't "improve" code you don't fully understand
- **No test coverage**: Risky refactors in untested code can introduce bugs
- **Time-critical fixes**: Production incidents need the fix, not cleanup
- **Shared/external code**: Extra care when changes affect other teams

Clean up obvious issues; for larger concerns, create a ticket.

### Anti-Patterns

```python
# ❌ Wrong - "Not my problem" attitude
def add_discount(order):
    # Just adding my feature, ignoring the mess
    o = order  # terrible variable name from legacy code
    d = o.total * 0.1  # magic number
    o.total = o.total - d
    return o

# ✅ Correct - Boy Scout approach
def add_discount(order: Order) -> Order:
    # Cleaned up while adding feature:
    # - Renamed variables for clarity
    # - Extracted magic number to constant
    DISCOUNT_RATE = 0.1
    discount = order.total * DISCOUNT_RATE
    order.total = order.total - discount
    return order
```

### Relationship to Other Principles

| Principle | Connection |
|-----------|------------|
| **Broken Windows Theory** | Boy Scout Rule is the *antidote*—fix small issues before they invite bigger ones |
| **DRY** | Boy Scout Rule helps you spot and fix duplication incrementally |
| **Self-Documenting Code** | Rename unclear variables as you encounter them |
| **YAGNI** | Delete unused code when you find it |
| **Opportunistic Refactoring** | Same concept, different name—improve code while you're there |
| **Technical Debt** | Boy Scout Rule is continuous debt payment |

**Broken Windows**: Neglect invites more neglect. Boy Scout Rule signals "this code is cared for."

### Summary

1. **Leave code better than you found it** — Every commit is an opportunity
2. **Small improvements compound** — Minutes daily beats weeks annually
3. **Clean the campground, not the forest** — Scope to files you're touching
4. **Don't ignore the mess** — "Not my code" is not an excuse
5. **Make cleanup socially expected** — It should be as unacceptable to leave mess as to litter

---

## Observability & Transparency

[↑ top](#table-of-contents)


> "Observability is the ability to understand the internal state of a system by examining its external outputs."
> — Charity Majors

### Core Concept

**Make system behavior visible through structured telemetry.** In distributed systems, observability is your primary debugging tool.

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

## When to Relax Rules

[↑ top](#table-of-contents)

*Over-applying principles causes as much harm as ignoring them. Know when to make exceptions.*

| Context | Relaxed Principles | Why |
|---------|-------------------|-----|
| **Prototypes/Spikes** | All | Exploring, not building. Throw it away. |
| **Test Code** | DRY | DAMP (Descriptive And Meaningful Phrases) > DRY. Readability trumps deduplication. |
| **Performance-Critical** | Abstractions, DI | Hot paths may need inlining. Profile first. |
| **Scripts < 100 lines** | Modularity, SRP | Overhead exceeds benefit. Keep it simple. |
| **Glue Code** | Most patterns | Thin integration layers don't need architecture. |
| **Generated Code** | All | Don't hand-edit generated code. Fix the generator. |
| **Legacy Migration** | Boy Scout | Large refactors need dedicated effort, not incremental changes. |
| **Data Transfer Objects** | Encapsulation | DTOs are meant to expose data. That's their job. |
| **Configuration** | YAGNI | Config flexibility is often worth it—cheaper than redeployment. |
| **Security Boundaries** | Postel's Law | Be paranoid, not liberal. Validate everything strictly. |

### The Meta-Principle

> **"Rules are for the guidance of wise men and the obedience of fools."** — Douglas Bader

Principles are heuristics, not laws. Understand WHY before applying. If following makes code worse, don't.

---

## References

[↑ top](#table-of-contents)

### Foundational Texts

Essential books that shaped modern software design thinking.

| Book | Author(s) | Key Contribution |
|------|-----------|------------------|
| *The Pragmatic Programmer* | Andy Hunt & Dave Thomas | Practical heuristics including DRY, orthogonality, tracer bullets, and "Tell Don't Ask" |
| *Clean Code* | Robert C. Martin | Function size, naming, and the Single Responsibility Principle |
| *A Philosophy of Software Design* | John Ousterhout | Deep vs. shallow modules, complexity as the root problem, strategic vs. tactical programming |
| *Design Patterns* | Gang of Four (Gamma, Helm, Johnson, Vlissides) | 23 reusable OO patterns; established patterns vocabulary |
| *Object-Oriented Software Construction* | Bertrand Meyer | Design by Contract, Command-Query Separation, Open-Closed Principle |
| *Refactoring* | Martin Fowler | Systematic code improvement techniques; code smells catalog |
| *Working Effectively with Legacy Code* | Michael Feathers | Seams, characterization tests, safely changing untested code |
| *Domain-Driven Design* | Eric Evans | Ubiquitous language, bounded contexts, strategic design |

### Seminal Articles & Essays

Influential writings that introduced or crystallized important concepts.

| Article | Author | Year | Key Idea |
|---------|--------|------|----------|
| [Parse, Don't Validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) | Alexis King | 2019 | Transform unstructured data into types that prove validity; let the type system enforce invariants |
| [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) | Sandi Metz | 2016 | "Duplication is far cheaper than the wrong abstraction"; prefer inline code over premature DRY |
| [Cognitive Load is What Matters](https://github.com/zakirullin/cognitive-load) | Artem Zakirullin | 2023 | Minimize mental effort required to understand code; endorsed by Rob Pike, Andrej Karpathy |
| [Tell Don't Ask](https://martinfowler.com/bliki/TellDontAsk.html) | Martin Fowler | 2013 | Tell objects what to do rather than asking for data and acting on it |
| [Four Rules of Simple Design](https://martinfowler.com/bliki/BeckDesignRules.html) | Kent Beck | ~1990s | (1) Passes tests, (2) Reveals intention, (3) No duplication, (4) Fewest elements |
| [Law of Demeter](https://www2.ccs.neu.edu/research/demeter/papers/law-of-demeter/oopsla88-law-of-demeter.pdf) | Karl Lieberherr et al. | 1987 | Only talk to your immediate friends; minimize coupling chains |

### Online Resources

Living references for patterns, principles, and refactoring techniques.

- [Martin Fowler's Bliki](https://martinfowler.com/bliki/) — Authoritative essays on patterns, refactoring, and architecture
- [Refactoring Guru](https://refactoring.guru/) — Visual catalog of design patterns and refactoring techniques
- [DevIQ Principles](https://deviq.com/principles/) — Concise summaries of software development principles
- [c2 Wiki (Cunningham & Cunningham)](http://wiki.c2.com/) — The original patterns wiki; historical discussions on OO design
- [Source Making](https://sourcemaking.com/) — Design patterns, anti-patterns, and refactoring catalog

### Concept Attribution

Origins of specific principles referenced in this document.

| Concept | Origin |
|---------|--------|
| **KISS** | U.S. Navy, 1960s; popularized by Kelly Johnson (Lockheed Skunk Works) |
| **YAGNI** | Extreme Programming (Kent Beck, Ron Jeffries), late 1990s |
| **DRY** | *The Pragmatic Programmer* (Hunt & Thomas), 1999 |
| **SOLID** | Robert C. Martin, early 2000s (acronym coined by Michael Feathers) |
| **Separation of Concerns** | Edsger Dijkstra, 1974 |
| **Design by Contract** | Bertrand Meyer, 1986 (Eiffel language) |
| **Postel's Law** | Jon Postel, RFC 761 (TCP), 1980 |
| **Deep Modules** | John Ousterhout, *A Philosophy of Software Design*, 2018 |
| **Rule of Three** | Folk wisdom; formalized in *Refactoring* (Fowler) |
| **Cognitive Load** | Psychology (John Sweller, 1988); applied to code by Zakirullin, 2023 |

---

*This document is designed to be dropped into your `~/.claude/commands/` and/or `~/.opencode/commands` folders. Run `/deslop [file-or-directory]` to analyze your code against these principles and let the agent fix any slop it detects.*
