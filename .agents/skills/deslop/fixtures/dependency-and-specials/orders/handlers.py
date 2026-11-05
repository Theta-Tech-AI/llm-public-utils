"""Order handlers shared by the web app, the CLI and the worker."""
from orders.models import Order


def handle(order: Order) -> None:
    if order.tenant == "acme":                 # PLANTED: one customer's rule at the call site
        order.audit_note = f"acme-{order.id}"
    if order.provider == "paypal":             # PLANTED: one vendor's special path
        order.status = "pending_review"
        return
    order.status = "confirmed"
