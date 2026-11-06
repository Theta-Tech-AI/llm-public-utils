"""HTTP surface. NEGATIVE CONTROL: a name-registered handler is unproven, not dead;
and `dry_run` is a declared policy both audiences exercise."""
from reports.export import export_report


def list_orders(request, dry_run: bool = False):
    if dry_run:                                # both branches reachable: console + admin UI
        return {"orders": [], "dry": True}
    return {"orders": ["o-1", "o-2"]}


def export(request):
    return export_report([], "report", as_pdf=True)


HANDLERS = {                                   # reached by name from the router; nothing imports it
    "GET /orders": list_orders,
    "GET /export": export,
}
