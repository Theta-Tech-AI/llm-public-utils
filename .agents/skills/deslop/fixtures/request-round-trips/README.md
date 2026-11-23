# Fixture — every query is cheap and the request is not

A small course site, used to control *Every Request Has a Round-Trip Budget*. The database runs on its own host
behind a pooler (`web/db.py`). Every table has the indexes its queries use (`schema.sql`), every statement is
parameterised, and every function is short and asks one owner (`courses/store.py`) for the rows it needs. Counted
with a stub connection, `GET /courses/{course_id}/overview` sends **57 statements for 4 distinct facts**
(enrolment 20 times, results 13, lessons 13, course 11), and `GET /me/inbox` sends **5 + N** on every poll.

**PLANTED**

- **Three readers each load the same rows.** `courses/progress.py` `completion`, `courses/certificate.py`
  `eligibility` and `courses/schedule.py` `next_lesson` each read the enrolment, the results and the lessons for
  themselves; `overview` in `courses/routes.py` calls all three.
- **The access check's answer is thrown away.** `courses/access.py` `require_enrolled` reads role, status, expiry
  and the course's archive date, returns `None`, and the next line of `overview` reads the enrolment again.
- **A context per option.** `courses/actions.py` `available` calls `allowed` once per action, and `allowed` builds a
  fresh `ActionContext` (9 statements) each time: 45 statements for one context's worth of facts.
- **One statement per section of a polled route.** `inbox/routes.py` `inbox` calls four same-shaped section readers
  (`inbox/sources.py`), then loops over the completed enrolments with a `SELECT *` on `certificate` (a row that
  holds a PDF) only to learn that it exists.

**Expected repair** — one finding per route and read owner (the repeated readers, the discarded check and the repeated context are evidence inside it), repaired at the owner of the read. For the course page: the
access check returns what it read, and one immutable facts value (enrolment, course, lessons, results) is read once
at the top of `overview` and handed to `completion`, `eligibility`, `next_lesson` and the action rules as a required
parameter: 3 or 4 statements. For the inbox: one `UNION ALL` over the four sections and an `EXISTS` (or a join) for
the certificates: 2 statements, whatever N is. A repair that adds a per-request cache or memo under
`courses/store.py`, or an optional `facts=None` parameter that keeps the readers' own reads, does not pass.

**LEGITIMATE — must be declined**

- `billing/checkout.py` `buy_seat`: one read of the course under `FOR UPDATE`, then the writes that depend on it, in
  one transaction. Separate statements are the design; the locked read is not a repeat.
- `reports/course_report.py`: three statements for three independent row sets (lessons, learners, results by
  `= ANY`), run by a scheduled job. One statement per fact is the aim, and a join of lessons with learners would
  multiply them.
- `courses/store.py`: each reader is right alone. The finding belongs to the request that composes them, never to
  one of these functions.
- `schema.sql`: every foreign key and every filter has its index. A reading that reports a missing index here has
  not read the schema.
