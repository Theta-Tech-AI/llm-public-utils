# Fixture: change-rate edges and special cases

A planted corpus for two principles — **Depend in the Direction of Stability** and **A Special Case Is a
Requirement the Design Never Accounted For** — plus the two rules folded into their owners
(`small-functions` flag arguments, `legibility` dead code). Small on purpose: every planted defect is
nameable in one sentence, and each has a **negative control** beside it that a correct reading must decline.

| Planted | Where | What is wrong |
|---|---|---|
| dependency-stability | `pricing/rules.py` | the most stable file in the tree imports the vendor client directly |
| special cases | `orders/handlers.py` | `tenant == "acme"` and `provider == "paypal"` in a shared path |
| special cases | `ui/dialogs.py` | a `sleep` that makes an ordering work, and a module-global `skip_refocus` |
| flag argument | `reports/export.py` | `as_pdf` / `include_headers` select two different write paths |
| dead code | `settings.py`, `integrations/stripe_v1.py` | `LEGACY_MODE` set in no deployment; a shim for a dependency removed two majors ago |

| Negative control | Where | Why a correct reading declines it |
|---|---|---|
| an adapter that reaches the vendor | `integrations/rates.py` | a thin adapter at the edge *is* the port |
| a policy read from data | `policies/limits.py` | per-customer behaviour with an owner, not a special case |
| a flag with two real audiences | `api/routes.py` (`dry_run`) | both branches are exercised and registered; it is a policy, not one workflow's switch |
| a symbol reached by name only | `api/routes.py` (`HANDLERS`) | registered in a table, never imported — unproven, not dead |

Not a fixture for the library's other lenses: it is not meant to be clean, only *correct for this test*.
