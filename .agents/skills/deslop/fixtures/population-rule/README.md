# Fixture — a rule every member must remember

**Why this is slop:** Routes that enforce leases only by convention leave project writes unprotected and permit a lease to change between its check and the write.

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

**Expected repair** — the store becomes the one door: it checks the lease under the row lock its write takes and
returns the only handle that writes (closed on exit, resolving documents and sections through itself); the lease
release is its own narrow operation. A repair that adds a lease call to
each route, or a route flag checked at start-up, is the patch and does not pass.

**LEGITIMATE — must be declined** — `add_comment` (a comment role; a reading may list it as an undeclared
exemption, at low severity at most), `export_pdf`
(a read), `release_lease` (the lease's own release), `jobs/runner.py` and `projects/db.py` (no route).
