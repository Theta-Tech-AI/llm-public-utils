---
name: deslop-architecture-code-reusability
description: Deslop principle — Code Reusability: Earn reuse from real callers; don't speculate on interfaces.
---

# Code Reusability

> "A little copying is better than a little dependency."
> — Rob Pike

Reusability is forward-looking — code usable in multiple contexts without modification — where DRY is about eliminating duplication that already exists. It's earned, not designed up front: reusable components cost 3-10x more to build, and that cost only pays off with *actual* reuse. Designing for reuse before the need is proven is a YAGNI violation that buys complexity with no payoff (the `GenericDataProcessor` that takes a parser, transformer, validator, and serializer to handle "any" format). Wait for real, concrete callers to reveal the actual shape needed, then generalize — this is about not speculating on a future interface, not about how many times duplicated *knowledge* must appear before it's fixed (that's the DRY question — see [Hunting Duplication](../duplication.md)).

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
