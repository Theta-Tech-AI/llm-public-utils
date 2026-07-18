---
name: deslop-data-layer-unused-indexes
description: Deslop principle — Every Index Is Used or It's Dropped: An index no query uses is pure loss.
---

# Every Index Is Used or It's Dropped

An index is not a quantity to minimize — it's a binary. Either a real query uses it, so it earns the write cost it imposes on every `INSERT`/`UPDATE`/`DELETE` (plus storage and planner time), or no query uses it and it is pure loss. There is no "nice to have" index. So the *count* is irrelevant: ten indexes that each serve a query are all correct; one index that serves none is the bug. Judge each index by that single question — *which query uses this, and does the planner actually pick it?* — and `EXPLAIN` to confirm. The ones that reliably fail the test and should be deleted: a plain index that is a left-prefix of an existing composite (`(a)` when `(a, b)` exists — the composite already serves `a`), a non-unique index duplicating a `UNIQUE` constraint (the unique index already serves every read the plain one would), and any index `pg_stat_user_indexes` reports has never been scanned (`idx_scan = 0`). If you can't name the query an index serves, that's your answer.
