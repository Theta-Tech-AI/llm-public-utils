---
name: deslop-data-layer-index-access-columns
description: Deslop principle — Index What You Filter, Join, and Sort On: Index the queries the table actually serves.
---

# Index What You Filter, Join, and Sort On

Beyond foreign keys, the index set is dictated by the queries the table actually serves: every column that recurs in a `WHERE`, a `JOIN` condition, or an `ORDER BY` is an index candidate. Don't guess — collect the real queries against the table and index their access paths. An `ORDER BY created_at DESC LIMIT 20` feed wants `created_at DESC` indexed so the database reads 20 rows instead of sorting the whole table; a recurring `WHERE status = ?` wants `status` reachable by index. The discipline is bidirectional: a hot predicate with no index to use is a latent slow query, and an index no query ever uses is pure write-time cost (see "Every Index Is Used or It's Dropped").
