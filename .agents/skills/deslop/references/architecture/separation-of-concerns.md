---
name: deslop-architecture-separation-of-concerns
description: Deslop principle — Separation of Concerns: High cohesion, low coupling; one concern per part.
---

# Separation of Concerns

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
