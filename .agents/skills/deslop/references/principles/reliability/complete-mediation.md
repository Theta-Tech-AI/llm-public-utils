---
name: deslop-reliability-complete-mediation
description: Deslop principle — Complete Mediation: a cross-cutting rule that each call site must remember to apply is missing at the site that forgot; make the right to change a thing a value only the access check can build, and let the one door every change passes demand it, so code without the right cannot write.
---

# Complete Mediation

> "Every access to every object must be checked for authority."
> — Jerome Saltzer and Michael Schroeder, *The Protection of Information in Computer Systems* (1975)

The slop is **a cross-cutting rule that each call site must remember to apply**: *hold the edit lease before you
change a project*, *write an audit record for each change*, *filter every query by tenant*. Each site that calls the
check is correct. The site that forgot has no check, and nothing fails. Adding the call to that site is a patch: the
next site forgets it too.

This is a solved problem, and the solution is a design, not a list. Give the right to change a thing a **value**
that only the access check can build: a grant, a capability, a witness. Then make the **one door every change already
passes** (the store's write method, the repository, the audited transaction) demand that value as a parameter. Code
that was not handed the value cannot call the door. The site that would forget cannot be written, so nothing must be
remembered and nothing must be listed. This is least privilege and deny by default, applied at the write: no code
holds the authority to change a project until a check hands it over.

## A small example

A project API lets one editor at a time change a project. The editor holds an **edit lease**. The router checks
each route's role before the handler runs.

```python
# ❌ the store accepts any caller; the lease is a call each handler must remember
@route("PUT", "/projects/{id}/settings", role="edit")
def update_settings(project_id, settings, user):
    lease.require_lease(project_id, user)             # refuse unless held
    store.save_settings(project_id, settings)

@route("PATCH", "/projects/{id}", role="edit")
def rename(project_id, name, user):
    lease.take_lease(project_id, user)                # a second helper, a second meaning: take it if free
    store.rename(project_id, name)

@route("POST", "/projects/{id}/documents/{doc}/lock", role="edit")
def lock_document(project_id, doc, user):             # forgot: any editor locks while another holds the lease
    store.lock(doc, by=user.id)
```

Read any one file and it looks right. The handler that forgot has nothing to read. Fixing it by adding
`require_lease` to `lock_document` closes one route. In a real case of this shape, a fix that added the call to four
routes of one router left two more open on the same build, one in the same router and one in another file, and
they were found within the hour.

```python
# ✅ the right to write is a value; the store demands it
@dataclass(frozen=True)
class EditGrant:                                       # built only in lease.py; no other module constructs one
    project_id: str
    row: Row                                           # the locked project row: the grant lives inside the lock

# lease.py — the only constructors, a closed list in one module
@contextmanager
def held(project_id: str, user: User) -> Iterator[EditGrant]:
    with row_lock(project_id) as row:
        if row.lease_holder != user.id:
            audit.refused(project_id, user, "lease held by another editor")
            raise Conflict("another editor holds this project")
        yield EditGrant(project_id, row)

@contextmanager
def lease_release(project_id: str, user: User) -> Iterator[EditGrant]: ...   # the one exemption, named

# store.py — every write method takes the grant
def save_settings(grant: EditGrant, settings: Settings) -> None: ...
def lock(grant: EditGrant, doc: str, by: User) -> None: ...

# a handler cannot reach the store without passing the check
@route("POST", "/projects/{id}/documents/{doc}/lock", role="edit")
def lock_document(project_id, doc, user):
    with lease.held(project_id, user) as grant:
        store.lock(grant, doc, by=user)
```

A handler that skips `lease.held` has no `EditGrant` to pass, so `store.lock(...)` does not type-check. The review
surface is `lease.py`: its constructors are the complete list of ways to obtain the right to write.

## Why a careful reading misses it

The defect is an **absence**. A reader who opens one file at a time sees a correct check in every file that has
one, and nothing in the file that has none. Review has the same blind spot: "omissions in particular are the hardest
defects to find because it's difficult to review something that isn't there" (SmartBear). So in code that was built
opt-in, the holes show only when the reader lists every member against the rule: the
[population census](../../readings/auditing.md#the-population-census). The census **detects**. It is not the repair:
a standing list of members, or a per-member check added for each hole it finds, is the same opt-in design with a
longer memory.

## The tells

Structural, never lexical: they hold whatever the helpers are called.

1. **The write door accepts a caller with no proof of the right.** The store method takes a bare id, and the check
   lives in the caller. This is the root tell; the others follow from it.
2. **Fewer enforcing calls than members.** The rule's enforcing call appears N times; the class of members (routes,
   handlers, writers of a table) has M > N.
3. **Several helpers for one rule.** Two or more functions enforce the same rule with different meanings: refuse
   unless held, take if free, check the holder by name.
4. **A fix that adds the check to one more site, or one more helper for one more group of sites.**
5. **The edge declares one rule and not its sibling.** The route declares its role, and the lease, the audit or the
   tenant filter is added by hand further in.
6. **A refusal with no record.** The audit write sits after the check, so a refused request leaves no trace.

## The second moment: check, then use

A check and the write it guards are two moments. Between them the authority can change: another editor takes the
lease, an admin removes a reviewer, a project is archived. CWE-367 names this: "the resource's state can change
between the check and the use in a way that invalidates the results of the check", and its fix is to "ensure that
locking occurs before the check". The grant answers both moments with one value: `lease.held` builds it **inside**
the row lock the write takes, and it cannot outlive that lock. The check and the use are then one moment, and the
grant the store receives **is** the confirmation. A check at the edge that hands nothing to the write re-creates the
defect for any rule whose authority can change while the request runs.

## The repair

1. **Write the rule and its door in one sentence.** "Every change to a project goes through the project store, and
   the store needs an edit grant." If no single door exists, make one first.
2. **Make the right a value.** A small, frozen type that only the access-check module can construct. Build it under
   the lock the write takes.
3. **Make the door demand it.** Every write method takes the grant as a parameter. Remove the overloads that do not.
4. **Name each exemption as a second constructor in the same module.** The list of constructors is closed and
   short; it is the only thing a reviewer reads.
5. **Delete the per-site calls and the extra helpers in the same change.** Their disappearance is the measure.
6. **Backstop in the database** where a writer can bypass the code: a trigger or constraint that refuses the write
   without the authority's row ([invariant constraints](../data-layer/invariant-constraints.md)).
7. **Record refusals at the door**, where the grant is refused, so every decision leaves a record.

## When to relax

- **Two sites that change together:** two explicit checks are clearer than a new type.
- **A rule that genuinely differs per site** is not one rule. Give each meaning its own grant type, not a flag.
- **No shared door exists and the writes are few:** a script or a prototype does not need a capability type.
- **A language with no static types:** the grant still works as a required argument the door checks at run time
  (`isinstance`, or a token only the check module can mint); it fails loudly on the first call, not silently.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Least Privilege**](least-privilege.md) | Owns how much authority a component holds. This file owns the mechanism that makes "none until a check grants it" true at every write: authority as a value, not ambient. |
| [**Make Illegal States Unrepresentable**](../architecture/illegal-states-unrepresentable.md) | A write without the right becomes a call that cannot be built, the same move applied to an operation. |
| [**Parse, Don't Validate**](../architecture/parse-dont-validate.md) | A check that returns only a verdict leaves the caller free to ignore it; the grant is the check's typed result, carried to where it is used. |
| [**Declaration vs Enforcement**](../../patterns/declaration-vs-enforcement.md) | Its *kept on some routes* variant is one datum on several paths; when the paths are many sites under one rule, this file owns the repair. |
| [**Implicit Coupling**](../architecture/implicit-coupling.md) | Each site must know to call the check: an unstated agreement. The grant states it in the signature. |
| [**Enforce Invariants with Constraints**](../data-layer/invariant-constraints.md) | The backstop in the schema for writers that bypass the code. |
| [**Patchwork**](../clean-code/patchwork.md) | One more check per forgetting site is patchwork; the repair changes the door, not the next site. |

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Complete mediation; fail-safe defaults ("Base access decisions on permission rather than exclusion."); economy of mechanism | Saltzer and Schroeder (1975), [text](https://www.cs.virginia.edu/~evans/cs551/saltzer/); [Shostack's commentary](https://shostack.org/blog/the-security-principles-of-saltzer-and-schroeder) | The goal and its default: every access checked, no access unless granted. |
| Capability, C-list ("Each capability in a C-list locates by means of a pointer some computing object, and indicates the actions that the computation may perform") | Dennis and Van Horn, *Programming Semantics for Multiprogrammed Computations*, CACM 9(3), 1966, [PDF](https://cs.ucf.edu/courses/cop6614/fall2005/dennis-vanhorn.pdf) | The origin of authority as a held value. |
| The confused deputy ("The capability both identifies the file and authorizes the compiler to write there.") | Hardy (1988), [text](https://css.csail.mit.edu/6.5660/2011/readings/confused-deputy.html) | Ambient authority is the failure; a value that carries the right is the fix. |
| A reference "indivisibly combining designation of the object, the permission to access it, and the means to access it" | Miller and Shapiro, *Paradigm Regained* (2003), [PDF](https://pdos.csail.mit.edu/6.1810/2004/readings/miller03paradigm.pdf); "No designation without authority" and ambient authority, summarised from Miller, Yee and Shapiro, *Capability Myths Demolished*, in [The Morning Paper](https://blog.acolyer.org/2016/02/16/capability-myths-demolished/) | The object-capability form of the grant. |
| "Except for public resources, deny by default." "Implement access control mechanisms once and re-use them throughout the application" | [OWASP Top 10:2021 A01](https://top10.owasp.org/2021/A01_2021-Broken_Access_Control/) | One mechanism, default deny. |
| "Validating permissions correctly on just the majority of requests is insufficient." | [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | Why a per-site check is not enough. |
| Missing Authorization (CWE-862); time-of-check time-of-use (CWE-367) | [CWE-862](https://cwe.mitre.org/data/definitions/862.html), [CWE-367](https://cwe.mitre.org/data/definitions/367.html) | The empty cell, and the second moment with its fix. |
| A type that carries "a proof that the list is non-empty" | Alexis King, [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) | The grant is the same proof-carrying value, for a right instead of a shape. |
| Policy enforcement point / policy decision point | NIST SP 800-162, in the [NIST zero-trust glossary](https://pages.nist.gov/zero-trust-architecture/glossary.html) | The door enforces; the check module decides. |
| Omissions are the hardest defects to review | [SmartBear, code review best practices](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/) | Practitioner claim, no data: why per-site review does not close this class. |

**What is this library's own:** the root tell (a write door that accepts a caller with no proof of the right), the
grant built under the write's lock as the answer to both moments, and the split between the census that detects
and the construction that repairs.

## Summary

1. **A cross-cutting rule each call site must remember is missing at the site that forgot.** Adding it there is a patch.
2. **Make the right a value only the check can build**, and make the one door every change passes demand it.
3. **Build the value under the write's lock**, so the check and the use are one moment.
4. **Exemptions are named constructors in one module**, a closed list; delete the per-site calls and extra helpers.
5. **The population census finds the holes in code built opt-in; it is never the repair.**
