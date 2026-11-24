---
name: deslop-data-layer-round-trips-per-request
description: Deslop principle — Every Request Has a Round-Trip Budget: count the statements one request sends; give each route a budget, read each fact once at its owner and pass the value.
---

# Every Request Has a Round-Trip Budget

**Why this is slop:** Repeated remote reads make a request wait on the network for facts it already has, even when each query is fast.

> "…the number of database round trips is more important for the response time than the amount of data transferred."
> — Markus Winand, *Use The Index, Luke*

The index principles make each statement cheap. This one counts the statements. When the application and the
database run on different hosts, every statement costs one network round trip whatever its plan says: often a few
milliseconds. A request that sends 40 indexed statements one after another at 8 ms
each waits 320 ms on the network, and no query plan shows it. (Pipelined sends overlap the waits: count the
synchronisation round trips.)

No line of code states the count. It is the sum of what every function in the call tree reads for itself, so it is
a **design output**: it grows each time a function is added. Two rules follow. **Count the statements of each
route and give the route a budget. Read each fact once per request, at its owner, and pass the value down.**

## A small example

A project page asks the server for its state: is the project locked, how far along are its documents, and which
moves may the caller make. Each answer has its own function, and each function reads the rows it needs.

```python
# ❌ every function is right alone; the request sends 1 + 1 + 1 + 2 + 3 × 3 = 14 statements for 3 facts
def page_state(conn, project_id, user):
    require_member(conn, project_id, user)        # reads the membership and the project, returns None
    project = get_project(conn, project_id)       # the project row again
    return {
        "name": project.name,
        "locked": is_locked(conn, project_id),    # the project row again
        "progress": progress(conn, project_id),   # the project row, then its documents
        "moves": [m for m in MOVES if may(conn, project_id, user, m)],   # membership, project, documents: per move
    }

# ✅ the owner reads once; everything below is a function of the value: 2 statements
@dataclass(frozen=True)
class ProjectFacts:                               # what this page's answers are computed from
    project: Project
    role: Role                                    # what the access check learned
    documents: tuple[Document, ...]

def page_state(conn, project_id, user):
    facts = read_project_facts(conn, project_id, user)   # refuses a non-member and returns what it read
    return {
        "name": facts.project.name,
        "locked": is_locked(facts),
        "progress": progress(facts),
        "moves": [m for m in MOVES if may(facts, m)],
    }
```

Now the readers take the facts, not a connection and an id, and the answers agree: under
read committed, five reads of one row can see five versions.

**Why tuning each statement cannot see it.** The cost is latency × count: `EXPLAIN` judges one statement, and the
slow-query log is empty because no statement is slow. Every function is correct alone: asking the one owner for the
row it needs is what [Single Source of Truth](../architecture/single-source-of-truth.md) asks for. The repeat
exists only in the request.

## The tells

Each is a lead. Confirm it by counting the route's statements: with the counter below, or in a read-only pass by
walking the route from its handler and writing one line per statement (reader, table, key). Start with the routes
called most: a polled route, the read every page makes. Decline a route that is called rarely, or whose statements
each read an independent collection that must stay separate (see the end). Several compatible sections that could
share one measured round trip are not that: five statements for five same-shaped sections are still a finding.

1. **A reader that takes a connection and an id, called beside others of the same shape.**
   `grep -rnE 'def \w+\((conn|db|session|cur)\w*, \w+_id' <src>`. One such function is fine. The tell is a handler
   that calls five, each loading the same row.
2. **The same owner reached from two layers of one request**: the route computes a state, and the service it
   calls computes it again.
3. **A context built inside a loop over options**: `for move in MOVES: build_context(conn, project_id)`. The
   facts do not depend on the move; only the rule does.
4. **A check that reads a row and returns `None`, a `bool` or the id it was given.** The handler's next line reads
   that row again. The discarded answer belongs to [Parse, Don't Validate](../architecture/parse-dont-validate.md);
   here it is one cause in the route's count.
5. **One statement per section of one page or poll**: `runs(conn) + replies(conn) + alerts(conn)`.
6. **A statement inside a loop over rows that no join owns**: an insert or an enqueue per item, a `SELECT *` on a
   wide row only to learn that it exists. A child read per parent is the join run in the client: charge it once,
   to [join access paths](join-access-paths.md), and add its statements to this route's count.
7. **A counter that reads low**: it sits in the query helper, so transaction control, batch executes and
   statements sent through a raw cursor are not counted.

Report **one finding per route and read owner**: the tells that fire (repeated readers, a discarded check, a context
per option) are evidence inside it, with one repair at the owner. Open a separate finding only for an independent
defect, such as a parse that is also wrong.

## The repair, by what the count shows

| The count shows | Repair |
|---|---|
| the same rows read by several readers | one immutable **facts value per concern**, read once at the top of the request by its owner and handed down as a **required** parameter; the readers become plain functions of it, and their own reads are deleted in the same change |
| an access check whose answer is thrown away | the check returns what it read (role, lock state, archive state) and the handler takes that value |
| a context built per option, or once per layer | build the shared context once outside the loop and pass it; evaluate each option's rule separately on it; reuse a verdict only for identical decision inputs (one option may be allowed while another is refused) |
| a statement per section or per item | one statement per result set: `UNION ALL` for sections of one shape, a join or `LATERAL` for a parent with its newest child, `= ANY(%s)` for a list of keys, `EXISTS` for "is there one", one multi-row `INSERT … SELECT … FROM unnest(%s)`; a view or a database function when the composite is a stable unit |

**What is not the repair:**

- **A hidden per-request cache**: `@lru_cache`, or a memo in a context variable or on the request object, put
  under the readers so that the second call is free. The memo is a
  second owner of the fact inside the request. A reader that runs after the request's own write gets the value
  from before it, and no signature shows which readers those are. (An explicit loader or identity map
  passed per request, with a declared lifetime and invalidation after writes, fits where the client chooses the reads
  at run time, as in a GraphQL resolver tree.)
- **An optional parameter**: `def progress(conn, project_id, facts=None)`. The self-reading path stays alive, and
  the caller that forgets to pass the value pays in silence.
- **A value reused after a fact it depends on changed.** A compliance or permission check that used to read its
  facts again after the slow step or after the request's own write now judges stale ones. Refresh the facts that a
  write affects or that carry a freshness requirement: build a new facts value after it, or keep the check's own
  read. A value read under `FOR UPDATE` stays valid only while what it depends on is unchanged, or when used as the
  intended before-value; after a write that changes it (a decremented `seats_left`), refresh it with `RETURNING` or a
  re-read. A transaction snapshot meant to stay valid across a wait is not stale.
- **One statement that fetches everything a page might need.** A fact that one rare branch needs is read there.

## When separate statements are right

- **Independent row sets.** Two child collections of one parent multiply each other in a join; read each once.
- **A fused statement with a worse plan than its parts.** Confirm with `EXPLAIN`, as for any query.
- **A read under a lock.** A write that depends on a fact reads it again under its own lock
  ([Complete Mediation](../reliability/complete-mediation.md#the-second-moment-check-then-use)). The facts value is
  a snapshot from the top of the request and is never the basis of a check-then-write. Do not widen a row lock into a join.
- **Different transactions**: a record that must survive the rollback of the work it describes.
- **A read that must see the request's own write**, when `RETURNING` cannot give it, or a read after a long wait
  (a lock, a job, a stream). Build a new facts value; never patch the old one.

## Measure it

1. **Count at the driver**, with a counting cursor or connection wrapper, so that every statement is counted:
   `BEGIN`, `COMMIT` and `ROLLBACK` (with some drivers, two more round trips per transaction), batch executes and
   raw-cursor statements. Make the counter honest before any budget is set.
2. **Put the count on every response and log line**, by route template:
   `Server-Timing: db;dur=41.2;desc="n=7"`. Send it only to callers who may see it.
3. **Keep one committed budget file**, route template to statement count, read by the check that already calls
   each route. A budget changes in the same commit as the code that changes the count, so a review shows
   `22 → 30` beside its reason. A breach is loud; whether it blocks is the team's choice.
4. **Know the floor**: what authentication and the access check cost before the handler runs. It can be one
   statement. Everything above it belongs to the route's design.
5. **Make the timing line sum.** Print the database, handler, serialisation and wait times, and the remainder as
   its own field: a line that leaves a third of the time unnamed hides a third of the cost.
6. **Rank by round trips × calls**, not by the slowest request. A few routes usually pay most of the total.

## When to relax

- **The database is in the same process or on the same host** (SQLite, a unix socket): a round trip costs
  microseconds. A repeat still shows a reader that should take a value, but there is no budget to defend.
- **A job, migration or admin page** called a few times a day.
- **A route whose result sets must stay separate, one statement each.** Do not fuse those; compatible sections that could share one round trip are still a finding.

## Measured

One web API, database on another host behind a pooler, 8 to 10 ms per statement: median 7 statements per request,
top tenth 42 or more, largest 98. Almost no statement was slow; database time was over half of all server time; six
routes paid 80% of the round trips; the floor was one statement.

| Route kind | Before | After | What removed the difference |
|---|---|---|---|
| a page overview composed of a dozen readers | 29; 39 to 42 on heavier records | 7; 10 to 11 | one immutable facts value read at the top of the route; twelve readers take it as a required parameter, no self-reading path left; a derived document built once and handed down; catalogue rows by `= ANY`. Bodies byte-identical on 9 records; median server time on the heavier records about 199 → 100 ms. One statement per distinct fact remains |
| a notification poll that every open tab calls | 9 to 14 | 3 to 5 | six source pages in one `UNION ALL`; the roster passed in; one `= ANY` existence read in place of a per-item `SELECT *`. A write inside the poll stayed: moving it was not provably identical |
| a page-state read that every page loads | 56 on a mature record (43 and 34 in other states) | 44 (32 and 29) | one lazily read value object passed as a parameter. It **missed its target of about 20**: 14 statements belonged to another concern's readers and 11 to a block that reading the code had not counted |
| a grid page | 16 to 20 | 9 to 14 | repeated reads removed; the fix was not itemised further |

**What the page-state row teaches.** The estimate made by reading the code was wrong in both directions. Only the
counter on the real route is evidence: count first, fix, count again, and let the remainder name the next concern.

---

| Principle | Relationship |
|-----------|--------------|
| [**Every Join Needs an Access Path on the Side Being Probed**](join-access-paths.md) | Owns the loop that is a join run in the client, and its index. This file owns the count of a whole request, including the repeats that no join removes. A request can pass every index principle and fail this one |
| [**Single Source of Truth**](../architecture/single-source-of-truth.md) | One owner per fact is not one read per request: every reader may call the owner, and the row is still read five times |
| [**Parse, Don't Validate**](../architecture/parse-dont-validate.md) | Owns the check that discards what it learned. Here that answer has a price in round trips |
| [**Complete Mediation**](../reliability/complete-mediation.md) | Owns where authority is checked. Its read under the write's lock is a required second statement, never a repeat to remove |
| [**Implicit Coupling**](../architecture/implicit-coupling.md) | A hidden memo makes a reader's result depend on which reader ran before it |
| [**Observability**](../reliability/observability.md) | Owns telemetry. This file names two fields a request's line owes: its statement count, and a remainder so that the parts sum |

## Control

Planted fixture `fixtures/request-round-trips/`: every query indexed, every function clean alone; a page that sends
57 statements for 4 facts, a polled inbox that sends 5 + N, and two routes to decline. Neutral prompt, read-only,
readers not told what is planted. Results by arm and round, with the misses and the findings nobody planted:
[evaluation](../../library/evaluation.md).

**The honest reading:** on a fixture this small the shipped library finds the defect, under a neighbour (a join
run in the client, or *DRY*). With the file the lens charged the causes here; the small model's whole pass missed
the discarded check and the poll's sections. The control does not show recall at scale.

## Prior art

The cost model is the **chatty I/O** antipattern ("the cumulative effect of a large number of I/O requests",
[Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/antipatterns/chatty-io/)). The
per-item loop is the **N+1 selects problem**
([Winand](https://use-the-index-luke.com/sql/join/nested-loops-join-n1-problem)). Call granularity across a
process boundary is Martin Fowler's: "batch all that into a single call"
([First Law of Distributed Objects](https://martinfowler.com/articles/distributed-objects-microservices.html)).
The explicit per-request loader is [DataLoader](https://github.com/graphql/dataloader). A count asserted in a
test is Django's [`assertNumQueries`](https://docs.djangoproject.com/en/5.2/topics/testing/tools/). The header is
W3C [Server Timing](https://www.w3.org/TR/server-timing/). Further sources: [further reading](../../library/further-reading.md#the-data-layer).

**This library's own:** the count as a design output with a committed budget per route; the causes that are not
loops (each reader loading its own facts, a check that discards its answer, a context per option); the required
facts value as the repair, with the hidden memo and the optional parameter named as non-repairs.

## Summary

1. **A request's statement count is a design output.** Count it at the driver, per route, against a budget.
2. **Read each fact once per request, at its owner, and pass the value** as a required parameter, never through a hidden memo.
3. **One statement per distinct fact is the aim.** A read under a lock, another transaction or an independent row set stays separate; compatible sections share one statement.
