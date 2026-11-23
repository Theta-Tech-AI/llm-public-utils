---
name: deslop-reliability-complete-mediation
description: Deslop principle — Complete Mediation: the authority to act (a permission, a lock or lease) checked by a call each site must remember is missing at the site that forgot; let the one door every change passes check it under its own lock and hand back the only handle that can write, so an honest author cannot write without it.
---

# Complete Mediation

> "Every access to every object must be checked for authority."
> — Jerome Saltzer and Michael Schroeder, *The Protection of Information in Computer Systems* (1975)

The slop is **a cross-cutting rule that each call site must remember to apply**, where the rule is the authority to
act: *the caller may change this project*, *the caller holds its edit lease*, *that authority is still current*. Each
site that calls the check is correct. The site that forgot has no check, and nothing fails. Adding the call to that
site is a patch: the next site forgets it too.

The fix is a design, not a list: deny by default at the write. Let the **one door every change already passes** (the
store, the repository) perform the check itself, under the lock its write takes, and hand back the **only handle
that can write**: the open, checked transaction. Code that did not go through the check has no handle, so an honest
author cannot write the route without it, and nothing must be remembered or listed per route. This removes
*forgetting*. It is not a defence against hostile code in the same process; that is the job of the database
privileges below.

## A small example

A project API lets one editor at a time change a project. The editor holds an **edit lease**. The router checks
each route's role before the handler runs.

```python
# ❌ the store accepts any caller; the lease is a call each handler must remember
def update_settings(project_id, settings, user):
    lease.require_lease(project_id, user)            # refuse unless held
    store.save_settings(project_id, settings)

def rename(project_id, name, user):
    lease.take_lease(project_id, user)               # a second helper, a second meaning: take it if free
    store.rename(project_id, name)

def lock_document(project_id, doc, user):            # forgot: any editor locks while another holds the lease
    store.lock(doc, by=user.id)
```

Read any one file and it looks right. The handler that forgot has nothing to read. Adding `require_lease` to
`lock_document` closes one route. A fix of this kind typically closes the routes that were found and leaves the
ones nobody listed open.

```python
# ✅ the door checks under its own lock and returns the only handle that writes
class ProjectStore:
    @contextmanager
    def edit(self, project_id, user) -> Iterator["EditSession"]:
        with self._db.transaction() as tx:
            row = tx.select_for_update("projects", project_id)   # the lease is read under the write's lock
            if row.lease_holder != user.id:
                raise Conflict("another editor holds this project")
            session = EditSession(tx, row)
            try:
                yield session
            finally:
                session.close()                                  # a kept session refuses every later write

    def release_lease(self, project_id, user) -> None: ...      # the one exemption: its own operation, no session

class EditSession:
    def close(self) -> None:
        self._tx = None                                          # the handle forgets its transaction

    def _open(self):
        if self._tx is None:
            raise RuntimeError("this edit session is closed")
        return self._tx

    def lock_document(self, doc_id, by) -> None:
        tx = self._open()
        tx.update("documents", where={"id": doc_id, "project_id": self._row.id}, locked_by=by.id)  # 0 rows: refused

def lock_document(project_id, doc, user):
    with projects.edit(project_id, user) as s:
        s.lock_document(doc, by=user)
```

Each `EditSession` method resolves its child (the document, the section) with the session's own project id and
writes it in the same call, and `_open()` refuses once the session is closed. A handle must not return child objects
that another handle accepts: a document fetched through one session and passed to another would write under the
wrong lease. The exemption is a separate operation on the store, not a second way to get an `EditSession`.

**The limit, plainly:** Python cannot stop code in the same process from reaching `store._db` or building an
`EditSession` by hand. The construction makes the honest path the only short one; the database backstop is what
refuses a writer that goes around it.

## Why a careful reading misses it

The defect is an **absence**. A reader who opens one file at a time sees a correct check in every file that has
one, and nothing in the file that has none. Review has the same blind spot: "omissions in particular are the hardest
defects to find because it's difficult to review something that isn't there" (SmartBear). So in code built opt-in,
the holes show only when the reader lists every member against the rule: the
[population census](../../readings/auditing.md#the-population-census). The census **detects**. It is not the repair:
a standing list, or one more check per hole, is the same opt-in design with a longer memory.

## The tells

Structural, never lexical: they hold whatever the helpers are called.

1. **The write door accepts a caller with no proof of the check.** The store method takes a bare id, and the check
   lives in the caller. This is the root tell.
2. **Fewer enforcing calls than members.** The check appears N times; the members it covers (routes, handlers,
   writers of a table) number M > N.
3. **Independent decisions with different meanings.** Two functions decide the same authority differently: refuse
   unless held, take if free. Several functions that delegate to one decision are a lead to read, not a finding.
4. **A fix that adds the check to one more site, or one more helper for one more group of sites.**
5. **The edge declares one rule and not its sibling.** The route declares its role, and the lease is added by hand
   further in.
6. **A refusal with no record.** The refused request leaves no trace.

## The second moment: check, then use

A check and the write it guards are two moments. CWE-367 names the gap: "the resource's state can change between the
check and the use in a way that invalidates the results of the check", and its fix: "ensure that locking occurs before
the check". The door above reads the lease under the row lock its write holds, and the session dies with the
transaction, so for the lease they are one moment. That holds only when **every change of an authority input takes
a conflicting lock** on that authority state, held through the write: the same row, or the policy's own rows locked
with `SELECT ... FOR SHARE` (or `FOR UPDATE`) by the check, as the PostgreSQL row-security page shows. A lease
handoff, a reviewer removal or an archive that changes its rows without that lock races the write; reading them again
under an unrelated lock closes nothing. Another serialization mechanism works only if it is named and justified, for
example serializable isolation with retry. Time-based expiry is checked at each write, not only at the start.

## The repair

1. **Name the door.** "Every change to a project goes through the project store." If no single door exists, make
   one first.
2. **Move the check into the door**, under the lock its write takes (and a conflicting lock on every authority
   input the check reads), and return the only handle that can write
   (the open transaction or a session over it). Close it on exit; a closed handle refuses.
3. **Resolve and write child resources in one handle call**, so the handle's scope bounds what it can touch; never
   return a child object another handle accepts.
4. **Give each exemption its own narrow operation** on the door, never the general handle. The door's entry points
   are the closed list a reviewer reads.
5. **Delete the per-site calls and the extra helpers in the same change.** Their disappearance is the measure.
6. **Backstop in the database** where a writer can go around the code. A row that merely exists is not authority:
   the policy needs a trusted principal (the database role or session identity of the caller), a check specific to
   the resource and the action, policy reads under the same lock, and privileges that stop bypass. In PostgreSQL,
   row-level security fits, with its own caveats: "Superusers and roles with the `BYPASSRLS` attribute always bypass
   the row security system", table owners do too unless `FORCE ROW LEVEL SECURITY`, and a policy that reads another
   table can race unless it uses `SELECT ... FOR SHARE`. A restricted procedure is the other shape.
7. **Record refusals at the door**, in a write that a rolled-back transaction does not undo.

## What this file owns, and what it does not

It owns **the authority to act**: permission, a lock or lease, and whether that authority is still current. The
population census finds other cross-cutting rules too, and each goes to its own owner: tenancy on a **read** (a
disclosure a write handle does not close) to [least privilege](least-privilege.md) or a scoped query in the data
layer; an audit record that must commit with its change to the transaction that writes both; validation to
[parse, don't validate](../architecture/parse-dont-validate.md); repeated requests to
[idempotency](../architecture/idempotency.md).

## When to relax

- **Two sites that change together:** two explicit checks are clearer than a new door.
- **A rule that genuinely differs per site** is not one rule. Give each meaning its own operation.
- **A script or a prototype** with a few writes has no door to build yet.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Least Privilege**](least-privilege.md) | Owns how much authority a component holds; this file owns the door that makes "none until checked" true at every write. |
| [**Make Illegal States Unrepresentable**](../architecture/illegal-states-unrepresentable.md) | A write without the check becomes a call an honest author cannot build, the same move applied to an operation. |
| [**Parse, Don't Validate**](../architecture/parse-dont-validate.md) | A check that returns only a verdict leaves the caller free to ignore it; the session is the check's result, carried to the write. |
| [**Declaration vs Enforcement**](../../patterns/declaration-vs-enforcement.md) | Its *kept on some routes* variant, when the paths are many sites under one authority rule. |
| [**Implicit Coupling**](../architecture/implicit-coupling.md) | Each site must know to call the check: an unstated agreement. |
| [**Enforce Invariants with Constraints**](../data-layer/invariant-constraints.md) | The schema-side backstop, under the conditions in step 6. |
| [**Patchwork**](../clean-code/patchwork.md) | One more check per forgetting site is patchwork; the repair changes the door. |

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Complete mediation; fail-safe defaults ("Base access decisions on permission rather than exclusion."); economy of mechanism | Saltzer and Schroeder (1975), [text](https://www.cs.virginia.edu/~evans/cs551/saltzer/); [Shostack's commentary](https://shostack.org/blog/the-security-principles-of-saltzer-and-schroeder) | The goal and its default. |
| Capability, C-list: each capability locates "some computing object, and indicates the actions that the computation may perform" | Dennis and Van Horn, *Programming Semantics for Multiprogrammed Computations*, CACM 9(3), 1966, [PDF](https://cs.ucf.edu/courses/cop6614/fall2005/dennis-vanhorn.pdf) (read from a scan) | Authority as a held handle bound to an object and its actions. |
| The confused deputy ("The capability both identifies the file and authorizes the compiler to write there.") | Hardy (1988), [text](https://css.csail.mit.edu/6.5660/2011/readings/confused-deputy.html) | Ambient authority is the failure; a handle that carries the right is the fix. |
| A reference "indivisibly combining designation of the object, the permission to access it, and the means to access it" | Miller and Shapiro, *Paradigm Regained* (2003), [PDF](https://pdos.csail.mit.edu/6.1810/2004/readings/miller03paradigm.pdf); *Capability Myths Demolished*, summarised in [The Morning Paper](https://blog.acolyer.org/2016/02/16/capability-myths-demolished/) | Why the session also resolves the document: designation and permission travel together. |
| "Except for public resources, deny by default." "Implement access control mechanisms once and re-use them throughout the application" | [OWASP Top 10:2021 A01](https://top10.owasp.org/2021/A01_2021-Broken_Access_Control/) | One mechanism, default deny. |
| "Validating permissions correctly on just the majority of requests is insufficient." | [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | Why a per-site check is not enough. |
| Missing Authorization; time-of-check time-of-use | [CWE-862](https://cwe.mitre.org/data/definitions/862.html), [CWE-367](https://cwe.mitre.org/data/definitions/367.html) | The empty cell, and the second moment. |
| Row security: bypass roles and policy races | [PostgreSQL, Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) | The conditions of the backstop. |
| A type that carries "a proof that the list is non-empty" | Alexis King, [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) | The same idea for a shape; here the proof is a live handle. |
| Policy enforcement point / policy decision point | NIST SP 800-162, in the [NIST zero-trust glossary](https://pages.nist.gov/zero-trust-architecture/glossary.html) | The door enforces and decides in one place. |
| Omissions are the hardest defects to review | [SmartBear, code review best practices](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/) | Practitioner claim, no data. |

**What is this library's own:** the root tell (a write door that accepts a caller with no proof of the check), the
door that checks under its own lock and returns the only writing handle, and the split between the census that
detects and the door that repairs.

## Summary

1. **A cross-cutting rule each call site must remember is missing at the site that forgot.** Adding it there is a patch.
2. **Move the check into the one door every change passes**, under its lock, and return the only handle that writes.
3. **Bind the handle**: it closes with the transaction, resolves and writes each child in one call, and an exemption is its own narrow operation; every authority input takes a conflicting lock.
4. **Name the limit**: this removes forgetting by honest authors; database privileges stop the dishonest path.
5. **The population census finds the holes in code built opt-in; it is never the repair.**
