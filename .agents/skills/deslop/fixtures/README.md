# Fixtures

Planted-defect corpora for controlling a change to a rule. Each directory is a small repo: what is
**PLANTED** must be found, and what is marked **LEGITIMATE** must be declined — a reading that reports the clean
control has produced a false positive and the change is not ready.

| Fixture | Planted | Must be declined |
|---|---|---|
| `sql-join-and-normalization/` | unindexed FK used by a join and a parent delete; N+1 loop; leading-wildcard and expression predicates without indexes; comma-joined column; hand-maintained total; copied address | the `GENERATED ALWAYS AS … STORED` column — the database owning its own derivation |
| `python-loose-value/` | one setting parsed by three different functions (`_truthy`, a second comparison, a third read) | the dataclass-free test file, which is ordinary |
| `clean-control/` | nothing | **everything** — a frozen dataclass with a validating constructor is the shape the principles ask for |

Run one lens against one fixture, two arms (shipped reading vs changed reading), and record the verdict in
`references/library/evaluation.md`.
