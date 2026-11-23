# Fixture — a rule every member must remember

A small project API with an edit lease, used to control *Complete Mediation*. The router checks each route's
role before the handler runs (`web/app.py`). The rule under test: **every route that changes a project needs
the caller to hold that project's edit lease**. Packages: `projects/` (the lease and project routes),
`documents/`, `jobs/`, `sections/`.

**PLANTED**

- Three edit routes change state with no lease check, and nothing fails: `documents/routes.py`
  `lock_document` and `sign_off`, and `jobs/routes.py` `start_summary` (a paid job).
- Three enforcing helpers with two meanings: `lease.require_lease` (refuse unless held), `lease.take_lease`
  (take if free) and `documents/session.py` `editing_session` (a third copy, written for one more group of routes).
  The rule is enforced by a call each route must remember; the router, which every route passes, does not know it.
- `sections/routes.py` `save_section` checks the lease before it takes the row lock and does not confirm it
  under the lock: the lease can move between the check and the write.

**Expected repair** — the right to write as a value: a grant only the lease module builds, under the row lock, that
every store write demands, with the lease release as a second named constructor. A repair that adds a lease call to
each route, or a route flag checked at start-up, is the patch and does not pass.

**LEGITIMATE — must be declined** — `add_comment` (a comment role; a reading may list it as an undeclared
exemption, at low severity at most), `export_pdf`
(a read), `release_lease` (the lease's own release), `jobs/runner.py` and `projects/db.py` (no route).
