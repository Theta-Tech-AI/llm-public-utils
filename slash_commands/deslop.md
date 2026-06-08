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

Code is read 10x more than it's written. Aim for clarity and readability. It requires effort to understand code and our working memory only holds limited pieces of information with full comprehension. Every clever trick forces readers to hold more in their head. While the developer may have been working on some code for a long time, they're often heavily relying on their long-term memory of how the code works and rarely realize how much cognitive effort it takes for newcomers to understand a piece of code seeing it for the first time. Comments are not an excuse for code that does not increase cognitive load. Clever one-liners, excessive layered approaches, prematurely build microservices, all increase the cognitive burden on the reader of the code. The best code requires no extra mental effort to parse.

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

---

### Single Level of Abstraction (SLAP)

[↑ top](#table-of-contents)

> "The code within a function should operate at a single level of abstraction."
> — Robert C. Martin, Clean Code

Every statement within a function should operate at the same level of abstraction. When you mix high-level operations ("process order") with low-level details ("parse a JSON field", `strip().upper()`), readers must mentally switch between levels and reconstruct the missing abstractions themselves — figuring out which statements belong together. The fix is to extract the low-level details into named functions so the caller reads as a top-down narrative. This is Robert Martin's "stepdown rule": code descends one level of abstraction at a time, like a newspaper article moving from headline to summary to details.

```python
# ❌ Wrong - Mixed abstraction levels
def process_order(order_data: dict) -> None:
    user = get_user(order_data["user_id"])  # High-level

    items = []  # Low-level detail mixed in
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

The usual tells are loops with inline body logic (extract the body) and a comment introducing a code block (the comment is naming a function that should exist). Don't over-extract, though: a 3-line function is already at one level, an initial guard clause at a higher-level function is fine, and test code, single-use transformations, and hot paths often read better inlined.

---

### Self-Documenting Code

[↑ top](#table-of-contents)


> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand."
> — Martin Fowler

Code should convey its purpose through names, structure, and organization rather than relying on comments. Names express intent and should be spelled out completely — abbreviations like `usr` or `cnt` force mental translation. Replace magic numbers and strings with named constants, and give each function one clear purpose so the structure itself tells the story. Code reveals *what* and *how*; comments are reserved for *why* and *why not*.

```python
# ❌ Wrong
def proc(d, w):
    return d * w * 8

# ✅ Correct
def calculate_billable_hours(days_worked: int, weeks: int) -> int:
    hours_per_day = 8
    return days_worked * weeks * hours_per_day
```

| Element | Convention | Examples |
|---------|------------|----------|
| **Variables** | Nouns, fully spelled out | `user_count`, `retry_delay_seconds` |
| **Functions** | Verbs/verb phrases | `calculate_total()`, `validate_input()` |
| **Predicates** | `is_`, `has_`, `can_` prefix | `is_active`, `has_permission` |
| **Classes** | Nouns, PascalCase | `UserAccount`, `OrderProcessor` |
| **Constants** | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |

Watch for abbreviations, single-letter variables outside tiny scopes, unnamed boolean parameters, and vague names like `process`, `handle`, or `do`. When a comment *is* warranted, make it explain the rationale the code can't:

```python
# Exponential backoff: upstream API rate-limits during peak hours (ISSUE-1234)
for attempt in range(MAX_RETRIES):
    time.sleep(2 ** attempt)
```

---

### Documentation Discipline

[↑ top](#table-of-contents)


> "Code tells you how, comments tell you why."
> — Jeff Atwood, Stack Overflow co-founder

Comments don't compile, can't be tested, and rot — yet sometimes they're essential for explaining *why*. The discipline is knowing the difference and moving documentation to the highest appropriate level.

| Layer | Audience | Purpose |
|-------|----------|---------|
| **README** | New users/devs | First contact, setup, overview |
| **API Docs** | Consumers | Contract, usage, edge cases |
| **Docstrings** | Callers | What it does, params, returns |
| **Inline Comments** | Maintainers | Why this specific implementation |

Comments earn their place when they explain business-rule rationale, justify a rejected alternative, document a workaround for an external constraint, attribute a borrowed algorithm, or warn about a non-obvious footgun. They don't earn it when they parrot what the code already says, journal who-changed-what (use git blame), pile up as a TODO graveyard, or preserve commented-out dead code (git has the history).

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Parrot comments** | `i += 1  # increment i` | Delete—code already says this |
| **Rotting comments** | Comment describes deleted code | Delete or update |
| **Journal comments** | `// Fixed by John, 3/15` | Use git blame instead |
| **Commented-out code** | Dead code polluting the file | Delete—git has history |
| **Mandated comments** | Boilerplate on every method | Comment only when valuable |
| **TODO graveyards** | `// TODO: fix this (2019)` | Create tickets or delete |

Comments drift from code silently, so keep them next to the code they describe, review them during code review, and delete rather than let them lie. Docstrings should document non-obvious behavior — business rules, edge cases, what gets raised — not restate a signature the reader can already see.

```python
# ✅ Documents non-obvious behavior
def calculate_shipping(order: Order) -> Decimal:
    """
    Calculate shipping cost with business rules.

    - Free shipping for orders over $100
    - Hawaii/Alaska adds flat $15 (no free shipping)

    Raises:
        InvalidAddressError: If shipping address is incomplete
    """
```

---

### Elegance

[↑ top](#table-of-contents)


> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."
> — Antoine de Saint-Exupéry

Elegant code solves the problem with minimum complexity while revealing something fundamental about the domain. Four criteria define it: **minimality** (no superfluous parts), **accomplishment** (it does exactly what it should — non-negotiable), **modesty** (restraint, no showing off), and **revelation** (it shows something new about the problem). The test is the reader's reaction: elegant code makes them say "of course," where clever code makes them ask "how does this work?" Elegance reveals domain insight and survives language changes; cleverness exploits language tricks and stays fragile.

---

### Principle of Least Surprise

[↑ top](#table-of-contents)

> "In interface design, always do the least surprising thing."
> — Eric S. Raymond

Components should behave the way users expect. Separate state-changing commands from queries, make names match behavior, return consistent types from similar methods, choose sensible defaults, and never hide side effects the signature doesn't imply. The usual surprises: methods whose names imply a query but secretly mutate, non-standard parameter order, inconsistent error handling across sibling methods, and "spooky action at a distance" where one call perturbs something unrelated. If you can't name a thing accurately, the design — not the name — is probably wrong.

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

DRY is about **knowledge**, not code — avoid duplicating *meaning*, not syntax. Knowledge duplication (the same business rule living in multiple places) must always be fixed. Incidental duplication (code that *looks* similar but represents *different* concepts that will evolve independently) should be left alone; merging it couples unrelated concerns. Apply the **Rule of Three**: write it the first time, note it the second, abstract it the third — two occurrences can't distinguish true duplication from coincidence, three reveal the pattern.

> "Duplication is far cheaper than the wrong abstraction." — Sandi Metz

The wrong abstraction is the more expensive failure. One developer extracts it; the next needs it slightly different and adds a parameter; the next adds a conditional; eventually it's incomprehensible but no one deletes it because of sunk cost. When an abstraction starts accumulating parameters and conditionals to handle "just one more case," inline it back into its callers and start fresh — re-extracting is cheaper than maintaining the wrong abstraction.

| True Knowledge Duplication (FIX) | Incidental Similarity (LEAVE) |
|---------------------------------|------------------------------|
| Same business rule/concept | Different business concepts |
| Changes *must* affect all instances | Instances will evolve independently |
| 3+ occurrences confirm the pattern | 1-2 occurrences—pattern unclear |
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

---

## Single Source of Truth

[↑ top](#table-of-contents)


> "There should be one—and preferably only one—obvious way to store a piece of information."

Every piece of data should have exactly one authoritative location; all other references derive from it. Where DRY targets duplicated *code and logic* within a codebase, SSoT targets duplicated *data storage* across systems and databases. The diagnostic question is simply "which copy is correct?" — if you can't answer immediately, the design is broken. Typical violations are the same foreign key stored in multiple databases, user data copied across services, and derived data with no clear owner. Duplication is fine when it's deliberate and synchronization isn't required: TTL caches, CQRS read-model denormalization, computed values, and cross-region replicas.

---

## Separation of Concerns

[↑ top](#table-of-contents)


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

## Modularity

[↑ top](#table-of-contents)


> "Every module is characterized by its knowledge of a design decision which it hides from all others."
> — David Parnas

Divide software into independent components, each encapsulating one responsibility and hiding its implementation behind a well-defined interface. The Parnas principle is to decompose by **design decisions likely to change**, so each module hides one such decision. Aim for high cohesion (elements within a module belong together) and low coupling (modules depend only on each other's interfaces, not internals). Prefer **deep** modules — a simple interface hiding complex implementation — over **shallow** ones that expose a complex interface while hiding little. A "God module" that does everything encapsulates nothing.

---

# Coupling & Dependencies

[↑ top](#table-of-contents)

*How do components relate to each other? These principles minimize unhealthy dependencies. Encapsulation hides internal state, Law of Demeter limits knowledge of other objects, Orthogonality ensures independent change, Dependency Injection makes dependencies explicit, and Composition Over Inheritance favors flexible composition.*

---

## Encapsulation

[↑ top](#table-of-contents)


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

## Law of Demeter

[↑ top](#table-of-contents)


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

## Orthogonality

[↑ top](#table-of-contents)


> "Eliminate effects between unrelated things. Design self-contained components: independent, and with a single, well-defined purpose."
> — Andy Hunt & Dave Thomas

Two components are orthogonal when a change in one doesn't affect the other — like a helicopter with coupled controls, non-orthogonal code means fixing one bug pops up two more elsewhere. Coupling is viral: a little leads to more. Measure orthogonality by how many places must change when one requirement changes. The usual culprits are global state, business logic coupled to a specific database dialect, presentation mixed with computation, and objects that accrete unrelated responsibilities. Dependency injection, abstract interfaces, and avoiding global state all push toward independence.

---

## Dependency Injection

[↑ top](#table-of-contents)


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

## Composition Over Inheritance

[↑ top](#table-of-contents)


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

# Design Patterns & Conventions

[↑ top](#table-of-contents)

*Proven approaches to common problems. SOLID provides five foundational OO principles, Convention Over Configuration reduces boilerplate through sensible defaults, Command-Query Separation distinguishes actions from queries, and Code Reusability addresses when and how to make code reusable.*

---

## SOLID Principles

[↑ top](#table-of-contents)


> "SOLID principles are the foundation of good software design—they make code more maintainable, flexible, and testable."
> — Robert C. Martin (Uncle Bob)

| Letter | Principle | Core Idea | Code Smells |
|--------|-----------|-----------|-------------|
| **S** | Single Responsibility | One reason to change | Class name has "And"/"Manager", mixed I/O and logic, methods don't use most attributes |
| **O** | Open/Closed | Open for extension, closed for modification | `if/elif`/`isinstance()` chains on type, modifying existing code for each new variant |
| **L** | Liskov Substitution | Subtypes substitutable for base types | Subclass raises `NotImplementedError`, empty `pass` overrides, type checks before calls |
| **I** | Interface Segregation | Many specific interfaces over one general | Fat interfaces (10+ methods), implementations that `raise NotImplementedError` |
| **D** | Dependency Inversion | Depend on abstractions, not concretions | Direct instantiation in constructors, concrete imports in business logic, can't mock |

SOLID earns its keep in code that must evolve, but it's overhead in simple scripts, prototypes, and performance-critical paths. Don't create an interface for a class that will only ever have one implementation, and wait for patterns to emerge (Rule of Three) before abstracting.

---

## Convention Over Configuration

[↑ top](#table-of-contents)


> "You're not a beautiful and unique snowflake. By giving up vain individuality, you can leapfrog the toils of mundane decisions, and make faster progress in areas that really matter."
> — David Heinemeier Hansson, The Rails Doctrine

### Core Concept

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

## Command-Query Separation

[↑ top](#table-of-contents)


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

## Code Reusability

[↑ top](#table-of-contents)


> "A little copying is better than a little dependency."
> — Rob Pike

Reusability is forward-looking — code usable in multiple contexts without modification — where DRY is about eliminating duplication that already exists. It's earned, not designed up front: reusable components cost 3-10x more to build, and that cost only pays off with *actual* reuse. Designing for reuse before the need is proven is a YAGNI violation that buys complexity with no payoff (the `GenericDataProcessor` that takes a parser, transformer, validator, and serializer to handle "any" format). Wait for the Rule of Three, then generalize.

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

# Data & State

[↑ top](#table-of-contents)

*How should data flow and behave? Parse Don't Validate transforms unstructured input into typed domain objects at boundaries. Immutability eliminates bugs by preventing state changes after creation. Idempotency ensures operations can be safely repeated.*

---

## Parse, Don't Validate

[↑ top](#table-of-contents)

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

## Immutability

[↑ top](#table-of-contents)


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

## Idempotency

[↑ top](#table-of-contents)


> "An operation is idempotent if performing it multiple times has the same effect as performing it once."

An idempotent operation produces the same result whether run once or many times. Duplicate requests are inevitable in distributed systems — retries, at-least-once queues, impatient users — so design around them rather than assuming exactly-once delivery. The main techniques: idempotency keys, deterministic IDs derived from content, database upserts (`INSERT ... ON CONFLICT`), conditional writes with version numbers, and lease-based processing. Some operations are naturally idempotent (`GET`, `PUT`, `DELETE`, and assignment `x = 5`) while others are not (`x += 5`). The cheap test is to call it twice and confirm the state matches.

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

Detect and report errors at the earliest possible moment, and never let invalid state propagate. Fail-fast means checking inputs at function entry and config at startup, then raising loudly — a clear error at the boundary beats silent corruption three layers downstream. Match the response to the error type: raise immediately on precondition violations, retry transient failures with backoff, fail permanently on deterministic ones, and assert invariants that should never be false. Once data has been validated at a boundary, trust it — don't re-validate inside.

```python
# ✅ Guard clauses - fail fast at entry
def process_order(order):
    if order is None:
        raise ValueError("order required")
    if not order.items:
        raise ValueError("items required")

# ✅ Config validation at startup
def __init__(self):
    self.key = os.getenv("API_KEY")
    if not self.key:
        raise ConfigError("API_KEY required")
```

---

## Design by Contract

[↑ top](#table-of-contents)


> "A software system is not a bunch of components thrown together. It is a construction of interacting elements, connected by clear contracts."
> — Bertrand Meyer

A contract makes the agreement between caller and routine explicit: the function guarantees its results (**postconditions**) *provided* the caller meets its requirements (**preconditions**), and **invariants** hold throughout the object's lifetime. Assertions are these contracts made executable — they document and verify at once. Under inheritance (Liskov substitution), a subtype may only *weaken* preconditions and only *strengthen* postconditions and invariants. DbC complements defensive programming rather than replacing it: trust-but-verify with contracts across internal interfaces where the caller is responsible for preconditions, and trust-no-one defensive checks at external boundaries.

---

## Postel's Law (Robustness Principle)

[↑ top](#table-of-contents)


> "Be conservative in what you send, be liberal in what you accept."
> — Jon Postel, RFC 793 (1981)

Be conservative in what you send and liberal in what you accept: generate strictly conformant output, but accept non-conformant input when the meaning is clear. This "tolerant reader" stance — ignore unknown fields rather than rejecting them — is what lets old clients keep working as servers evolve, and it powered the explosive growth of HTML, Unix pipes, SMTP, and JSON APIs.

```python
# ❌ Wrong - Strict parsing breaks when the API adds fields
def parse_user(data: dict) -> User:
    if set(data.keys()) != {"id", "name", "email"}:
        raise ValueError("Unexpected fields in response")
    return User(id=data["id"], name=data["name"], email=data["email"])

# ✅ Correct - Tolerant reader: require what you need, ignore the rest
def parse_user(data: dict) -> User:
    return User(id=data["id"], name=data["name"], email=data["email"])
```

But it has a dark side: liberal receivers mask sender bugs, "incorrect" behavior calcifies into a de facto standard (specification rot), and "reasonable" input can be crafted to exploit edge cases. The modern balance is to validate *required* fields strictly (fail-fast) while tolerantly ignoring unknown ones — and to be paranoid, not liberal, at security boundaries.

---

## Resilience & Graceful Degradation

[↑ top](#table-of-contents)


> "In complex systems, failure is the normal state. Success is the special case that requires explanation."
> — Richard Cook

In any non-trivial system, partial failure is the normal state — design to keep operating through it rather than assuming success. Three pillars carry most of the load: **retry** transient failures with exponential backoff and jitter (`delay = min(base * 2^attempt + jitter, max)`) to recover without a thundering herd; **fall back** to cached or default data to degrade gracefully; and **protect** against cascades with circuit breakers (CLOSED → OPEN → HALF-OPEN) and timeouts on every external call. Only retry *transient* errors — an auth failure should fail fast, not loop.

```python
# Cascading fallback: personalized → cached → popular
def get_recommendations(user_id: str) -> list[Product]:
    try:
        return recommendation_service.get_personalized(user_id)
    except ServiceUnavailableError:
        cached = cache.get(f"recommendations:{user_id}")
        if cached:
            return cached
        return get_popular_items()  # Final fallback
```

---

## Principle of Least Privilege

[↑ top](#table-of-contents)


> "Every program and every user of the system should operate using the least set of privileges necessary to complete the job."
> — Jerome Saltzer, *Protection and the Control of Information Sharing in Multics* (1974)

Every component should run with the minimum permissions its job requires — nothing more. Fewer permissions mean fewer entry points (smaller attack surface) and less damage when a breach happens (smaller blast radius); most breaches start with a privileged credential being abused, as Equifax (permissive DB access, no segmentation) and Target (an over-privileged HVAC vendor) both showed. The principle applies at every level: a config-reading function shouldn't have write access, a read path shouldn't hold a connection with `DROP TABLE`, a payment service shouldn't reach user profiles, and an IAM policy shouldn't say `Action: "s3:*", Resource: "*"`.

```python
# ❌ Wrong - Function accepts overly broad context
def send_notification(user: User, db: DatabaseAdmin):
    email = db.query(f"SELECT email FROM users WHERE id = {user.id}")
    # db could delete the entire users table!

# ✅ Correct - Function receives only what it needs
def send_notification(email: str):
    send_email(email, "Your notification...")  # Cannot touch the database
```

Default to deny and grant explicitly, separate credentials by function (read vs. write), time-bound elevated access, and audit regularly — permissions accumulate as roles change and "temporary" access becomes permanent. Watch for the verbal tells: "just give it admin, it's easier," "we'll lock it down later," "it needs that for debugging." Least privilege partners with Zero Trust: Zero Trust authenticates *who* is making a request, PoLP limits what that authenticated identity can *do*.

---

# Maintainability & Operations

[↑ top](#table-of-contents)

*Code is a living artifact. The Boy Scout Rule keeps code improving incrementally with every change, while Observability & Transparency ensure you can understand what your systems are doing in production.*

---

## Boy Scout Rule

[↑ top](#table-of-contents)


> "Always leave the code better than you found it."
> — Robert C. Martin (Uncle Bob), *Clean Code*

Leave the code slightly better than you found it with each commit. Continuous small improvements — renaming `o` to `order`, removing a dead import, extracting a magic number, simplifying a tangled conditional — compound and beat periodic "refactoring sprints," because each change is small enough to be low-risk and ride along with the feature you're already shipping. But clean the campground, not the forest: scope cleanup to the files you're already touching (a 350-file blank-line sweep makes review impossible), and file a ticket for anything larger.

```python
# ❌ Wrong - "Not my problem" attitude
def add_discount(order):
    o = order          # terrible name from legacy code
    d = o.total * 0.1  # magic number
    o.total = o.total - d
    return o

# ✅ Correct - cleaned up while adding the feature
def add_discount(order: Order) -> Order:
    DISCOUNT_RATE = 0.1
    discount = order.total * DISCOUNT_RATE
    order.total = order.total - discount
    return order
```

The excuses to distrust: "I'll clean it up later" (you won't), "that's not my code," "it works, don't touch it." The exceptions to respect: don't "improve" code you don't understand or that has no test coverage, and don't fold cleanup into a time-critical production fix. This is the antidote to broken windows — neglect invites more neglect, and a tidy file signals the code is cared for.

---

## Observability & Transparency

[↑ top](#table-of-contents)


> "Observability is the ability to understand the internal state of a system by examining its external outputs."
> — Charity Majors

Make system behavior visible through structured telemetry — in distributed systems, the logs, metrics, and traces you emit are your primary debugger, because you can't attach one in production. Structure logs for machine parsing (JSON, key-value pairs, semantic prefixes), match log levels to intent, propagate correlation IDs (request IDs, trace IDs) so one request reads as a single story across services, and return operational metadata in responses. The anti-patterns are the ones that leave you blind: silently swallowed exceptions, opaque generic error messages, missing request context, over-logging inside tight loops — and the one that's actively dangerous, logging secrets.

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
