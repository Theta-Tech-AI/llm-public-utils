---
name: deslop-clean-code-cognitive-load
description: Deslop principle — Cognitive Load: Minimize mental effort to read code; named intermediates over clever conditions.
---

# Cognitive Load

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
