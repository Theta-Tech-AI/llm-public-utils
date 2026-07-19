---
name: deslop-clean-code-slap
description: Deslop principle — Single Level of Abstraction (SLAP): Each function operates at one level of abstraction.
---

# Single Level of Abstraction (SLAP)

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

In relation to other principles, SLAP:

| Principle | Relationship |
|-----------|--------------|
| [**Small Functions**](small-functions.md) | The stepdown rule is how small functions stay readable |
| [**Cognitive Load**](cognitive-load.md) | Mixing levels forces readers to reconstruct the missing abstractions |
| [**Self-Documenting Code**](self-documenting-code.md) | Extraction is how low-level details get named |
| [**Separation of Concerns**](../architecture/separation-of-concerns.md) | SLAP is separation applied within a single function |
