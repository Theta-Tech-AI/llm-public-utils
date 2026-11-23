---
name: deslop-architecture-parse-dont-validate
description: Deslop principle — Parse, Don't Validate: Convert input to precise types once at the boundary.
---

# Parse, Don't Validate

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

The opposite is "shotgun parsing" — the same `if not user_id` check scattered across every function, easy to miss and prone to leaving half-processed invalid data behind. It pairs with primitive obsession, where domain concepts ride around as raw `str`/`int`/`dict` (`create_order(customer_id: str, product_id: str, ...)` invites swapping arguments and allows negative quantities). Encode the constraints in the type instead. The *data-model* half of that decision — one variant per state, exactly the fields that state has — belongs to [Make Illegal States Unrepresentable](illegal-states-unrepresentable.md): this file owns the entry point, that file owns the shape the value lands in.

Choose the parsing depth to fit: `NewType` for a zero-overhead marker, a frozen dataclass for richer invariants, Pydantic when you want full coercion and validation at the edge. For quick scripts, prototypes, and simple CRUD, not every field needs its own type.

## The tells: a check that does not hand back the value

A save route checks each field of a request body and then stores the body. The email check trims the text before
it matches it. The check passes, and the untrimmed text is what gets stored, so every reader of that row trims it
again, and the one reader that forgets shows the padded text.

```python
# ❌ the check knows the clean value and throws it away; the raw body is stored
def field_problem(name: str, value: object) -> str | None:
    text = value.strip()                                  # the normalised copy lives only here
    return None if EMAIL.match(text) else "must be an email"

def save(body: dict[str, object]) -> None:
    for name, value in body.items():
        if problem := field_problem(name, value):
            raise Rejected(problem)
    store.put(body)                                       # the padded text, as sent

to = profile["email"].strip()                             # reader 1 repairs it
email = profile["email"].strip().lower()                  # reader 2 repairs it differently

# ✅ the boundary returns the value it checked; that value is stored and read as is
def parse_email(raw: object) -> Email:
    text = raw.strip().lower() if isinstance(raw, str) else ""
    if not EMAIL.match(text):
        raise Rejected("must be an email")
    return Email(text)
```

Three tells, each with a primitive to find it. One instance of any of them is a finding:

1. **A checker that returns only a verdict, and a caller that stores its argument.** Find functions whose return
   type is `-> None`, `-> bool` or `-> str | None` (a complaint) and that take the value they judge
   (`grep -nE 'def \w+\(.*\) -> (None|bool|str \| None|Optional\[str\])' <src>`). For each, read its callers: when
   the caller writes the same argument it passed in (`store.put(body)`, `INSERT ... VALUES (%s)`, `session.add(x)`)
   rather than something the check returned, the check is a validator at a save boundary.
2. **A normalisation inside a check, applied to a local copy.** Inside the checkers from tell 1, look for a
   normalising call bound to a local name (`grep -nE '^\s+\w+ = .*\.(strip|lower|casefold|upper)\(\)|= (int|float|Decimal)\(' <checker files>`):
   `text = value.strip()`, `n = int(raw)`, `key = raw.casefold()`, `items = set(values)`. The check proved the
   normalised value is good and returned nothing, so the stored value was never normalised.
3. **One stored value normalised again by more than one reader.** Grep the normalising calls across the tree, group
   the hits by the value they apply to (the same key, column or field), and count readers per value
   (`grep -rnE '\.(strip|lower|casefold|upper)\(\)|\bset\(|\b(int|float)\(' <src>`, then group by the field each hit reads). Two readers
   repairing one value is a finding against its **writer**, not against the readers: open the writer and apply
   tells 1 and 2 there.

Not a finding: a parser that returns the normalised value which its caller stores; a single normalisation where the
value enters from its own producer (model output trimmed once into a typed result); a reader that formats a
canonical value for display (a postcode split into two groups for a label). The test is whether the stored or
passed value is already in its one form.

**How to fix it**

1. Write one parser per input kind at the boundary, returning the canonical value or refusing (`parse_email(raw) -> Email`).
2. Make the writer store what the parser returned, and answer it back to the caller, so the client sees what was kept.
3. Delete the readers' repairs one by one; the count from tell 3 is the measure, and it falls to zero.
4. For rows already stored raw, parse on read with the same function; do not add a second normaliser.

---

In relation to other principles, parse, don't validate:

| Principle | Relationship |
|-----------|--------------|
| [**Decide, Don't Cope**](../clean-code/decide-dont-cope.md) | Parsing is the boundary decision that ends coping |
| [**Fail-Fast**](../reliability/fail-fast.md) | Illegal states fail at the boundary, not three layers in |
| [**Constrain the Domain in the Schema**](../data-layer/domain-constraints.md) | Parse-don't-validate for data at rest |
| [**Immutability**](immutability.md) | Parsed domain types are best made immutable |
| [**Make Illegal States Unrepresentable**](illegal-states-unrepresentable.md) | The data-model half: this file parses at the entry, that one forbids the combination |
| [**Errors at the Boundary**](../reliability/errors-at-the-boundary.md) | Parsing is the detection moment; translation and the decision belong further in |
