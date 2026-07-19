---
name: deslop-clean-code-self-documenting-code
description: Deslop principle — Self-Documenting Code: Names and structure over comments; comments for why only.
---

# Self-Documenting Code

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

In relation to other principles, self-documenting code:

| Principle | Relationship |
|-----------|--------------|
| [**Documentation Discipline**](documentation-discipline.md) | Where comments earn their place when names can't carry the why |
| [**Cognitive Load**](cognitive-load.md) | Good names eliminate mental translation |
| [**Small Functions**](small-functions.md) | Small functions let names replace comments |
| [**Principle of Least Surprise**](least-surprise.md) | Accurate names are the first defense against surprise |
