---
name: deslop-pattern-grammar-without-owner
description: Deslop pattern — Grammar Without an Owner: one input format (an identifier, a config value) taken apart by several parsers that disagree; one parser and one formatter.
---

# Grammar without an owner

## The structural tell

One identifier format (`INV-2024-0042`, `doc#page=3`) is taken apart by several regexes or `split`s that disagree on the prefix set, the digit width or the optional parts. Collect them: seven patterns for one format is a grammar with no parser.

## Why it arises

Each caller needed one piece, so each wrote the smallest pattern that worked on the examples it had seen.

## Repair shape, owner first

One parse function and one format function own the grammar; callers receive a typed value. Add every disagreeing input as a case of the one parser, so the disagreement becomes a test of the owner.

## Who owns the mechanism

| Principle | Owns | Boundary with this pattern |
|---|---|---|
| [parse-dont-validate](../principles/architecture/parse-dont-validate.md) | turning a string into a typed value once | the mechanism the callers skip |
| [helper-is-an-architecture-finding](../principles/architecture/helper-is-an-architecture-finding.md) | the missing owner behind repeated helpers | each regex is such a helper |
| [single-source-of-truth](../principles/architecture/single-source-of-truth.md) | one authority for the format | the format's definition |

## Variant: config parsed twice with different rules

The same shape with an environment value as the input: `== "true"` in one module and a strict true/1/yes/on parser in another, so one value means two things. Grep the key, not a helper: every read site is a candidate. Repair is the same owner-first move — one settings loader returns typed decisions, per-site reads are deleted, and an unknown value fails at startup instead of defaulting. It is a variant, not its own pattern, because its tell (one input, several parsers) and its repair (one parser, typed output) match the identifier case; the owning principles are the same three plus [no-silent-defaults](../principles/reliability/no-silent-defaults.md).

```python
# ❌ DEBUG=1 is on in one module and off in the other
a = os.environ.get("DEBUG") == "true";   b = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes", "on")
# ✅ parsed once
settings = Settings.from_env()   # settings.debug: bool
```

## Caught by

Lens `parsing`.

## Measured

427 findings, 37 high for identifier grammars; the config variant adds 114 findings, 12 high. Heuristic classes; they overlap.

## Example

```python
# ❌ two regexes, two grammars: one accepts INV-42, the other needs four digits
re.match(r"INV-(\d+)", ref);   re.match(r"INV-(\d{4})-(\d{4})", ref)
# ✅ one parser; every caller holds an InvoiceRef
def parse_invoice_ref(s: str) -> InvoiceRef: ...
```
