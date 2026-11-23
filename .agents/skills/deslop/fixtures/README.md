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
| `validate-not-parse/` | a save route whose checker returns only a complaint (`-> str \| None`) and trims a local copy (`text = value.strip()`), then stores the raw body; two readers trim and case-fold the stored email again; a report de-duplicates a multi-select the check never de-duplicated | `billing/postcode.py` (a parser that returns the canonical value, which its caller stores), `billing/labels.py` (display formatting of that canonical value), `llm/summary.py` (model output trimmed once into a typed result where it enters) |
| [`population-rule/`](population-rule/README.md) | three edit routes that change a project with no lease check while the router checks only the role; three lease helpers with two meanings; a lease checked before the row lock and not confirmed under it | `add_comment` (a comment role), `export_pdf` (a read), `release_lease` (the lease's own release) |
| [`request-round-trips/`](request-round-trips/README.md) | every query indexed and every function clean alone, yet one course page sends 57 statements for 4 facts: three readers each load the same enrolment, results and lessons; the access check reads the enrolment and returns nothing; a context is rebuilt for each of 5 actions; a polled inbox sends one statement per section and a `SELECT *` per row to learn that a certificate exists | `billing/checkout.py` (a read under the row lock, then the writes that depend on it), `reports/course_report.py` (three statements for three independent row sets, the results by `= ANY`), the readers in `courses/store.py` taken one at a time |
| `clean-control/` | nothing | **everything** — a frozen dataclass with a validating constructor is the shape the principles ask for |

Run one lens against one fixture, two arms (shipped reading vs changed reading), and record the verdict in
`references/library/evaluation.md`.
