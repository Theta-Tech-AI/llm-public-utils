# Fixture — implicit state machine

A shipment service used to control *A State Machine Nobody Wrote Down*. Packages: `logistics/` (records
and picking), `api/` (HTTP handlers), `jobs/` (nightly jobs), `admin/` (operator tools), `billing/`
(invoices), `accounts/` (subscriptions).

**PLANTED**

- `logistics/shipment.py` and its four writers — `logistics/picking.py`, `api/routes.py`,
  `jobs/reconciler.py`, `admin/tools.py` — each define shipment transitions independently: the nightly
  reconciler marks a shipment delivered whether or not it was ever dispatched, and the admin tool voids
  one from any state. No file answers *can it go from X to Y?*
- `accounts/subscription.py` — `is_trial`, `is_past_due`, `is_cancelled` carry one lifecycle with no owner;
  `cancel()` followed by `start_trial()` leaves all three flags in contradictory combinations.

**LEGITIMATE — must be declined** — `billing/invoices.py`: a three-state linear flow with a single guarded
`transition()` and one `ALLOWED` table. It is the repair this principle asks for, so a reading that reports
it has produced a false positive.
