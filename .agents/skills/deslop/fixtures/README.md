# Fixtures

Planted-defect corpora for controlling a change to a rule. Each directory is a small repo: what is
**PLANTED** must be found, and what is marked **LEGITIMATE** must be declined — a reading that reports the clean
control has produced a false positive and the change is not ready.

| Fixture | Planted | Must be declined |
|---|---|---|
| `sql-join-and-normalization/` | unindexed FK used by a join and a parent delete; N+1 loop; leading-wildcard and expression predicates without indexes; comma-joined column; hand-maintained total; copied address | the `GENERATED ALWAYS AS … STORED` column — the database owning its own derivation |
| `python-loose-value/` | one setting parsed by three different functions (`_truthy`, a second comparison, a third read) | the dataclass-free test file, which is ordinary |
| [`implicit-state-machine/`](implicit-state-machine/README.md) | a shipment lifecycle whose transitions are defined independently by an HTTP handler, a picking module, a nightly reconciler and an admin tool; a subscription lifecycle carried by three interacting booleans | `billing/invoices.py` — a linear three-state flow with one guarded transition table, which is the repair this principle asks for |
| [`dependency-and-specials/`](dependency-and-specials/README.md) | a stable pricing rule importing the vendor client; `tenant == "acme"` and `provider == "paypal"` in a shared handler; a `sleep` plus a module-global `skip_refocus`; `as_pdf`/`include_headers` writing two paths; `LEGACY_MODE` set in no deployment; a v1 shim for a dependency removed two majors ago | the vendor adapter at the edge (that *is* the port), a policy table read from data, `dry_run` with two registered audiences, and a handler reached by name from `HANDLERS` |
| `clean-control/` | nothing | **everything** — a frozen dataclass with a validating constructor is the shape the principles ask for |

Run one lens against one fixture, two arms (shipped reading vs changed reading), and record the verdict in
`references/library/evaluation.md`.
