---
name: deslop-clean-code
description: Deslop principles, Part I: Clean Code — KISS, YAGNI, Small Functions, Guard Clauses, Decide Don't Cope, Cognitive Load, SLAP, Self-Documenting Code, Documentation Discipline, Elegance, Least Surprise.
---

# Part I: Clean Code

Write clear, simple, readable code. Do less, but better. Reduce complexity, and make the code easily readable.

**Contents:**

- [KISS: Keep It Simple, Stupid](#kiss-keep-it-simple-stupid)
- [YAGNI: You Aren't Gonna Need It](#yagni-you-arent-gonna-need-it)
- [Small Functions](#small-functions)
- [Guard Clauses](#guard-clauses)
- [Decide, Don't Cope](#decide-dont-cope)
- [Cognitive Load](#cognitive-load)
- [Single Level of Abstraction (SLAP)](#single-level-of-abstraction-slap)
- [Self-Documenting Code](#self-documenting-code)
- [Documentation Discipline](#documentation-discipline)
- [Elegance](#elegance)
- [Principle of Least Surprise](#principle-of-least-surprise)

---

## KISS: Keep It Simple, Stupid

> Worked example: [case-study-simplification-agent-fleet.md](case-study-simplification-agent-fleet.md) — a production deslop pass that collapsed a per-section LLM agent fleet, a duplicated prompt fragment, and a prose-policing regex into one agent, one preamble, and zero regexes.

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

## YAGNI: You Aren't Gonna Need It

> "Always implement things when you actually need them, never when you just foresee that you need them."
> — Ron Jeffries, XP co-founder

YAGNI is the discipline of **not building functionality until it's required**. Every feature has costs: development, testing, debugging, maintenance, cognitive load, delays, complexity, drift. Features you don't need yet carry these costs without delivering value. Common violations and code smells includes config options no one uses, ABC with one implementation, extensibility points never extended, commented "future" code, or unused API endpoints. Before adding code: **Who needs this today?** (not "might need") — **What breaks without it?** (if nothing, skip it) — **Can we add it later?** (usually yes, with better understanding). Only build what's needed now, delete speculative code, and keep code malleable and maintainable.

**The trap**: *"While I'm here, just in case I need it later, I'll just add..."*

**The reality**: Most speculative features fail to improve their target metrics.

---

## Small Functions

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

## Guard Clauses

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

## Decide, Don't Cope

The most common shape of AI-generated slop is not a bad algorithm — it is a **coping mentality**. Generated code treats every input as a hostile mystery and copes with it locally: it accepts `unknown`, then builds an if/else-if ladder of `typeof` checks, `instanceof` tests, inline casts, try/catch rungs, and stacked fallbacks until *something* produces a usable value. Every rung handles a hypothetical ("what if it's an object with a message? what if stringify throws?") that no requirement ever asked for. The code optimizes for "never crash on any conceivable input **here**" instead of "invalid input cannot **reach** here."

Wise architecture inverts this. Somewhere, exactly once, a boundary **decides** what is allowed — normalizes or rejects — and everything downstream trusts that decision and stays on the happy path. The reviewer's question is never "are these branches clean?" but "**why does this function believe it can receive anything at all?**"

This is a mentality, not a typing trick. Stricter type annotations on the same coping code just move the casts around. The fix is architectural: pick the one place where the value enters the system, make it produce the right shape, and delete every downstream accommodation.

**The deeper unwisdom: refusing to make claims about the world.** Coping code is what a mind produces when it declines to commit to any statement about its own system. Every rung of a ladder is a question the author refused to answer — *can this value actually be a non-string here? should it ever be?* — converted into a runtime branch that every future reader must now answer instead, forever. Three failure modes of judgment drive it, in humans and in LLMs alike:

1. **Local completion over global design.** The author's frame is "make *this snippet* survive anything so I can be done here," never "should this situation exist at all?" Adding a branch requires zero understanding of the surrounding system; changing a contract requires owning one. Branches are cheaper to *write*; decisions are cheaper to *own* — and slop authors always buy the former.
2. **Blame-avoidance masquerading as robustness.** A crash looks like the author's failure; quiet complexity doesn't. So the code appeases: it accepts everything, asserts nothing, and holds no opinion about what is valid. That is tolerance, not robustness. Real robustness is a clear contract enforced loudly — a system that says "this cannot happen, and if it does, you will hear about it immediately" is more reliable than one that silently absorbs garbage and keeps going in an undefined state.
3. **Deferred decisions compounding as entropy.** An unmade decision does not disappear — it becomes control flow. Most incidental complexity in a codebase is the fossil record of decisions nobody made: every "what if"-shaped branch, every `?? fallback ?? fallback`, every catch-and-continue is a commitment someone dodged, paid for on every subsequent read.

The corrective habit: treat every speculative branch as a **claim you are refusing to make** — then make it. Assert the invariant, enforce it at the boundary, and let violations fail fast and loud. Code written by a mind willing to be wrong *once, at the edge, visibly* is always simpler than code written by a mind hedging everywhere, invisibly.

**The canonical tell: the coercion ladder.** A mutable accumulator threaded through a chain of runtime type interrogation. Here is one from a real AI-generated error handler:

```typescript
// ❌ Slop — copes inline: accumulator, four guessed shapes, three stacked fallbacks
if (error instanceof ProgramThrow) {
  const value = error.value
  let message: string
  if (containsRuntimeReference(value)) {
    message = "a non-data value"
  } else if (typeof value === "string") {
    message = value
  } else if (
    value !== null &&
    typeof value === "object" &&
    typeof (value as { message?: unknown }).message === "string"
  ) {
    message = (value as { message: string }).message
  } else {
    try {
      message = JSON.stringify(copyOut(value)) ?? String(value)
    } catch {
      message = String(value)
    }
  }
  return { kind: "ExecutionFailure", message: `Uncaught: ${message}` }
}
```

The reflexive cleanup — and why it is not the fix — is to put the ladder inside a function. Look at what that function IS: its signature admits it will cope with anything, and its body is nothing but the coping:

```typescript
// ⚠️ Still slop, now tidier — the function's signature accepts anything,
// so its body must guess four shapes and stack three fallbacks.
function executionFailure(value: unknown): ExecutionFailure {
  let message: string
  if (containsRuntimeReference(value)) {
    message = "a non-data value"
  } else if (typeof value === "string") {
    message = value
  } else if (
    value !== null &&
    typeof value === "object" &&
    typeof (value as { message?: unknown }).message === "string"
  ) {
    message = (value as { message: string }).message
  } else {
    try {
      message = JSON.stringify(copyOut(value)) ?? String(value)
    } catch {
      message = String(value)
    }
  }
  return { kind: "ExecutionFailure", message: `Uncaught: ${message}` }
}
```

Now the same function in a wisely-architected codebase — the only change is that callers are required to supply the right type, and the entire body evaporates:

```typescript
// ✅ Correct — same function, input required to be a string.
// Twenty-six lines of guessing become one line of doing.
function executionFailure(message: string): ExecutionFailure {
  return { kind: "ExecutionFailure", message: `Uncaught: ${message}` }
}
```

Where did the ladder go? Nowhere — **it ceased to exist.** The one legitimate conversion (a thrown value into a policy-checked string) happens once at the throw boundary, where the raw value actually enters the system and where the redaction rule naturally lives. Every function past that boundary takes `message: string` and simply does its job. The consumer collapsed not because the branches were cleaned, but because they can no longer be needed. That is the difference between putting coping code inside a function and architecting so the function has nothing to cope with: compare the two `executionFailure` signatures — `(value: unknown)` is a confession that the codebase never decided what a thrown value is; `(message: string)` is the decision.

How to review for it:

1. **Trace the `unknown` upstream.** When you meet a type-sniffing ladder, find where the value was last known-good. If any code you own touched it between there and here, the fix belongs at that touchpoint, not here.
2. **Count the shapes the code guesses.** Each guessed shape (string? object-with-message? JSON-able? unstringifiable?) is a speculative requirement. If no caller actually produces it, the branch is YAGNI bloat — delete it and let the boundary reject.
3. **One decision point per value.** If two places both interrogate the same value's type, one of them is coping with the other's indecision. Merge them at the earlier one.
4. **Extraction is the fallback, not the fix.** Only when the boundary is genuinely foreign — a wire format, a third-party API, user-thrown JS values you cannot intercept — does the coercion belong in your code, and then in exactly one named, tested function with a comment saying whose mess it absorbs.

In relation to other principles, decide-don't-cope draws on...

| Principle | Relationship |
|-----------|--------------|
| **Parse, Don't Validate** | The mechanism: convert once at the boundary; downstream never re-interrogates |
| **YAGNI** | Every guessed shape is a requirement nobody stated |
| **KISS** | One required type beats four hypothetical ones |
| **Fail-Fast** | Rejecting at the boundary beats coping in the interior |
| **Design by Contract** | The boundary's decision IS the contract; consumers assume it holds |
| **Single Level of Abstraction** | Coping code mixes policy, dispatch, and formatting at one level |

---

## Cognitive Load

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

## Single Level of Abstraction (SLAP)

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

## Self-Documenting Code

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

## Documentation Discipline

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

## Elegance

> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."
> — Antoine de Saint-Exupéry

Elegant code solves the problem with minimum complexity while revealing something fundamental about the domain. Four criteria define it: **minimality** (no superfluous parts), **accomplishment** (it does exactly what it should — non-negotiable), **modesty** (restraint, no showing off), and **revelation** (it shows something new about the problem). The test is the reader's reaction: elegant code makes them say "of course," where clever code makes them ask "how does this work?" Elegance reveals domain insight and survives language changes; cleverness exploits language tricks and stays fragile.

---

## Principle of Least Surprise

> "In interface design, always do the least surprising thing."
> — Eric S. Raymond

Components should behave the way users expect. Separate state-changing commands from queries, make names match behavior, return consistent types from similar methods, choose sensible defaults, and never hide side effects the signature doesn't imply. The usual surprises: methods whose names imply a query but secretly mutate, non-standard parameter order, inconsistent error handling across sibling methods, and "spooky action at a distance" where one call perturbs something unrelated. If you can't name a thing accurately, the design — not the name — is probably wrong.
