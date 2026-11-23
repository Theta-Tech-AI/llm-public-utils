---
name: deslop-reliability-complete-mediation
description: Deslop principle — Complete Mediation: a rule every member of a population must obey (every write route holds the lease, every change writes an audit record) is enforced once where every member passes, on by default, and confirmed again where the state changes; a call each member must remember is a check the forgetting member does not have.
---

# Complete Mediation

> "Every access to every object must be checked for authority."
> — Jerome Saltzer and Michael Schroeder, *The Protection of Information in Computer Systems* (1975)

Some rules apply to a whole **population**: every route that changes a project, every state change, every query
of a shared table, every job that spends money. The rule is the same for each member: *hold the edit lease*,
*write an audit record*, *filter by tenant*, *carry an idempotency key*. Slop is when each member enforces the
rule **by a call it must remember to make**. Each member that has the call is correct. The member that forgot has
no check, and nothing fails: no test is red, no reviewer sees a wrong line, because the wrong line does not
exist. **The finding is an enforcement point that not every member passes.** The repair puts the rule where every
member must pass (on by default, with each exemption declared and listed), and confirms it again where the state
changes, under the same lock.

## A small example

A project API lets one editor at a time change a project. The editor holds an **edit lease**. The router checks
each route's role before the handler runs. Three routes change the project:

```python
# ❌ the role is declared once at the edge; the lease is a call each handler must remember
@route("PUT", "/projects/{id}/settings", role="edit")
def update_settings(project_id, settings, user):
    lease.require_lease(project_id, user)              # refuse unless held
    store.save_settings(project_id, settings)

@route("PATCH", "/projects/{id}", role="edit")
def rename(project_id, name, user):
    lease.take_lease(project_id, user)                 # a second helper: take it if free
    store.rename(project_id, name)

@route("POST", "/projects/{id}/documents/{doc}/lock", role="edit")
def lock_document(project_id, doc, user):              # forgot: any editor locks while another holds the lease
    store.lock(doc, by=user.id)
```

Read any one file and it looks right. Two handlers have a lease check; the third has nothing to look at.

```python
# ✅ the router owns the rule; a write route is leased unless it says why not
@route("POST", "/projects/{id}/documents/{doc}/lock", role="edit", writes=True)
def lock_document(project_id, doc, user):              # no lease call to forget
    store.lock(doc, by=user)

@route("DELETE", "/projects/{id}/lease", role="edit", writes=True,
       lease_exempt="releases the lease itself")       # the only way out: a reason, listed in one table
def release_lease(project_id, user): ...

# the store confirms the lease where the state changes, inside the row lock
def save_settings(project_id, settings, user):
    with row_lock(project_id) as row:
        require_holder(row, user)                      # the lease cannot move between this line and the write
        row.settings = settings
```

The router takes the lease for every `writes=True` route before the handler runs, and refuses at start-up a
non-GET route that declares neither `writes` nor an exemption, so a new route cannot be added without a
decision. The handlers lose their lease calls in the same change.

## Why a careful reading misses it

The defect is an **absence**. A reader who opens one file at a time sees a correct check in every file that has
one, and sees nothing in the file that has none. Review has the same blind spot: "omissions in particular are the
hardest defects to find because it's difficult to review something that isn't there" (SmartBear). So the defect
shows only when the reader lists **the whole population against the rule** and reads the empty cells. That list is
the population census in [auditing](../../readings/auditing.md#the-population-census); this file is where its
findings are charged.

## The tells

Structural, never lexical: they hold whatever the helpers are called.

1. **Fewer enforcing calls than members.** The rule's enforcing call appears N times; the population has M > N
   members. Each of the M − N members is a finding unless it declares an exemption.
2. **Several helpers for one rule.** Two or more functions enforce the same rule with different meanings (refuse
   unless held, take if free, check the holder by name). Each new group of members grew its own copy.
3. **A new helper that enforces the rule for one more group.** The fix for one forgetting member adds a helper
   for its group, and the population still has no single point of enforcement.
4. **The edge declares one rule and not its sibling.** The route declares its role at the edge, and the lease,
   the audit or the tenant filter is added by hand further in.
5. **An exemption that only a comment states.** `# no lease: ...` beside a handler is an opt-out nobody reviews
   and no check lists.
6. **A refusal with no record.** The audit write sits behind the check, so the refused request leaves no trace;
   the audit rule's population (every decision, refusals included) has its own empty cell.

## The second moment: check, then use

A check at the edge and the write under a lock are **two moments**. Between them the authority can change: another
editor takes the lease, an admin removes a reviewer, a project is archived. CWE-367 names this: "the resource's
state can change between the check and the use in a way that invalidates the results of the check", and its fix is
to "ensure that locking occurs before the check". So moving every check to the edge alone re-creates the defect
for any rule whose authority can change while the request runs. The rule is decided **once** at the point every
member passes (so no member can forget it) **and confirmed** where the state changes, under the lock that write
takes (so it is still true when it counts). Both are one rule with one owner; the second is not a copy of the
first if both call the same function.

## The repair

1. **Write the rule and its population in one sentence.** "Every route that changes a project holds that
   project's edit lease." If the population cannot be named, stop: the rule is not decided yet.
2. **Find the one point every member passes**: the router or its dependency list, a middleware, a base class, a
   repository's write method, a query builder that adds the tenant filter, a database trigger.
3. **Make the rule the default there.** A member is covered unless it declares an exemption with a reason, and
   the declarations are one list a reviewer reads. A member that declares nothing is refused at start-up or in
   CI, never at run time.
4. **Confirm the rule under the write lock** when its authority can change during the request.
5. **Delete the per-member calls and the extra helpers in the same change.** Their disappearance is the measure.
6. **Record refusals at the enforcement point**, so the audit population has no empty cell.

## When to relax

- **A population of two** that changes together: two explicit calls are clearer than a mechanism.
- **A rule that genuinely differs per member** is not one rule. State it per member, in one table, so the
  differences are decisions and not accidents.
- **The enforcement point already exists** and every member passes it: per-member calls on top are redundant,
  not missing. Delete them.
- **A one-off script or a prototype** has no population yet.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Declaration vs Enforcement**](../../patterns/declaration-vs-enforcement.md) | Its *kept on some routes* variant is one protected datum on several paths; this file owns the mechanism when the population is many members under one rule. |
| [**Implicit Coupling**](../architecture/implicit-coupling.md) | Each member must know to call the helper: an unstated agreement. That file reads one call site; this one reads the population. |
| [**Least Privilege**](least-privilege.md) | Decides how much authority a component holds; this decides whether every use of it is checked. |
| [**Errors at the Boundary**](errors-at-the-boundary.md) | Places where a failure is detected and decided; this places a rule's enforcement and adds the second moment. |
| [**DRY**](../architecture/dry.md) | Several enforcing helpers are one rule with several owners; DRY merges them, this also covers the member with none. |
| [**Enforce Invariants with Constraints**](../data-layer/invariant-constraints.md) | The same rule in the schema: enforce where every writer passes, not where the application calls. |
| [**Patchwork**](../clean-code/patchwork.md) | One more helper per forgetting member is patchwork; the repair moves the rule, it does not add the next guard. |

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Complete mediation; fail-safe defaults ("Base access decisions on permission rather than exclusion."); economy of mechanism | Saltzer and Schroeder (1975), [text](https://www.cs.virginia.edu/~evans/cs551/saltzer/); [Shostack's commentary](https://shostack.org/blog/the-security-principles-of-saltzer-and-schroeder) | The principle and its default: every access checked, no access unless granted. |
| "Except for public resources, deny by default." "Implement access control mechanisms once and re-use them throughout the application" | [OWASP Top 10:2021 A01](https://top10.owasp.org/2021/A01_2021-Broken_Access_Control/) | One mechanism, default deny. |
| "Validating permissions correctly on just the majority of requests is insufficient." Global, application-wide configuration rather than per-method checks | [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | Why the point every member passes is the right home. |
| Missing Authorization: "The product does not perform an authorization check when an actor attempts to access a resource or perform an action." | [CWE-862](https://cwe.mitre.org/data/definitions/862.html) | The empty cell, as a weakness class. |
| Time-of-check time-of-use | [CWE-367](https://cwe.mitre.org/data/definitions/367.html) | The second moment and its fix: lock before the check. |
| Policy enforcement point / policy decision point | NIST SP 800-162, in the [NIST zero-trust glossary](https://pages.nist.gov/zero-trust-architecture/glossary.html) | One component decides, one enforces on every request. |
| Omissions are the hardest defects to review | [SmartBear, code review best practices](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/) | Practitioner claim, no data: why the census is a list, not a reading. |

**What is this library's own:** the population census as the reading instrument (member × rule, read the empty
cells), the structural tells above, and the rule that the edge decides once while the write confirms under its lock.

## Summary

1. **A rule every member must remember is a rule the forgetting member does not have.**
2. **The defect is an absence**: list the population against the rule and read the empty cells.
3. **Several helpers for one rule, or a new helper per group, mean no point of enforcement exists.**
4. **Enforce where every member passes, on by default; an exemption is declared with a reason and listed.**
5. **Decide at the edge, confirm under the write lock** when the authority can change in between.
