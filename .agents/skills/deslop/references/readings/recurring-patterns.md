---
name: deslop-recurring-patterns
description: The ten cross-principle patterns a very large audit measured — one fact with many owners, declaration vs enforcement, consumers re-deciding, vocabulary drift, absence equals failure, ungoverned grammar, upstream forks, state in a column, one-sided contracts, config parsed twice — each with its structural tell, owner-first repair and owning principles.
---

# Recurring patterns

The principles name mechanisms; a real codebase shows the same few **patterns** across them, each charged by two or
three principles under different names. This file names the pattern, gives the tell, and points at the owners —
it restates none of them. Read it in every reading: a reader who finds one instance inside its own group should
recognise the pattern, then file it under the owning principle and **name the single owner the fix needs**.
[Consolidation](../stages/consolidation.md#5-classify-then-theme-the-cross-concerns) uses the pattern as the L1 class
when it builds themes.

**Measured on** a coverage pass over a ~236k-line web application (Python API, TypeScript SPA overlaid on an
upstream framework, ops scripts): 332 read-only cells produced 9,407 findings; verification dropped 32%; the rest
collapsed into 2,136 concerns (1,023 local, 582 **cross** — the right fix needs one owner across modules or layers —
and 531 design or migration changes). Counts below are heuristic text classes over the quoted evidence; they
**overlap**, so never add them. "High" is the verified high-severity count.

| # | Pattern | Findings | High | Caught most by |
|---|---|---|---|---|
| 1 | One fact, many owners, already disagreeing | 705 | 171 (40% of all high) | duplication, parsing, boundaries |
| 2 | Declaration vs enforcement | 785 | 64 | guarantees, legibility |
| 3 | Consumer re-decides the producer's decision | 736 | 54 | parsing, duplication |
| 4 | Vocabulary drift across layers | 584 | 47 | coupling, parsing |
| 5 | Absence and failure share one value | 433 | 33 | parsing, guarantees |
| 6 | Grammar without an owner | 427 | 37 | parsing |
| 7 | Fork of upstream instead of extension | 211 | 40 | duplication, boundaries |
| 8 | Unwritten state machine in a column | 181 | 23 | boundaries |
| 9 | One-sided contract | 123 | 16 | parsing, guarantees |
| 10 | Config parsed twice with different rules | 114 | 12 | parsing |

Every pattern's repair has the same order: **name the owner first, route every consumer through it, delete the
copies in the same change.** Polishing one copy of a fact that has several is the commonest wasted fix.

## 1. One fact, many owners, already disagreeing

The single-fact disease, and the most expensive: 40% of the high findings.

- **Tell:** two places decide the same thing and their answers differ on at least one input — a threshold, a
  status label, a permission rule, a default, a mapping. Check disagreement, not resemblance: feed both the edge
  case. Four projections of one run status that disagree on *cancelling* vs *cancelled* is one instance.
- **Arises:** each copy was correct when written; no module was ever named the owner.
- **Repair:** pick the module whose change would be least surprising to the others, expose the decision as one
  function or table, delete the rest. Disagreeing copies are a bug report, not a style note.
- **Owners:** [single-source-of-truth](../principles/architecture/single-source-of-truth.md),
  [dry](../principles/architecture/dry.md),
  [one-logical-unit-one-home](../principles/architecture/one-logical-unit-one-home.md),
  [helper-is-an-architecture-finding](../principles/architecture/helper-is-an-architecture-finding.md).

```python
# ❌ two owners of "is this invoice overdue?" — they disagree on the due date itself
def badge(inv):  return "overdue" if inv.due < today() else "ok"          # api/serializers
def reminder(inv): return inv.due <= today() and not inv.paid              # jobs/reminders
# ✅ one owner, both call it
def is_overdue(inv, today): return inv.due < today and not inv.paid
```

## 2. Declaration vs enforcement

- **Tell:** a docstring, name, comment, route declaration or config key promises what the body does not do: a
  `validate_*` that only logs, a route marked admin-only whose handler never checks, a "idempotent" docstring over
  an append, a `timeout` setting nothing reads. Read the promise, then read the code for the line that keeps it.
- **Arises:** the declaration is written once and the code changes under it; nothing couples them.
- **Repair:** make the code carry the promise (a type, a guard, a constraint), or delete the claim. Never fix the
  comment to match a behaviour nobody chose.
- **Owners:** [unclaimed-guarantee](../principles/clean-code/unclaimed-guarantee.md),
  [design-by-contract](../principles/reliability/design-by-contract.md),
  [least-surprise](../principles/clean-code/least-surprise.md),
  [documentation-discipline](../principles/clean-code/documentation-discipline.md).

```typescript
// ❌ the route declares who may call it; the handler never looks
router.delete("/orders/:id", requireRole("admin"), (req) => remove(req.params.id)); // role middleware not mounted
// ✅ the guarantee lives in the handler's own dependency, so it cannot be skipped
router.delete("/orders/:id", (req) => remove(authorize(req, "admin"), req.params.id));
```

## 3. Consumer re-decides the producer's decision

- **Tell:** the client, or a later stage, reconciles two answers the producer already reconciled — merging two
  server lists into one view, a second parse of a field the API already typed, a hand copy of a server rule
  ("orders over 50 ship free") in the SPA.
- **Arises:** the producer returned raw ingredients, or the consumer did not trust the contract.
- **Repair:** the producer returns the decision (a field, a typed variant); the consumer renders it. One
  producer, one decision, and the reconciler is deleted rather than hardened.
- **Owners:** [helper-is-an-architecture-finding](../principles/architecture/helper-is-an-architecture-finding.md),
  [parse-dont-validate](../principles/architecture/parse-dont-validate.md),
  [dry](../principles/architecture/dry.md).

```typescript
// ❌ the SPA recomputes what the server knows
const shipsFree = order.total >= 50 && !order.items.some(i => i.oversize);
// ✅ the server sent the decision
const shipsFree = order.shipping.free;
```

## 4. Vocabulary drift across layers

- **Tell:** one closed set of values (status, kind, reason) spelled as string literals in several modules and again
  in the UI; the spellings or the *set* differ (`cancelling` handled in one switch, absent from another).
- **Repair:** one enum or table per vocabulary, produced at the owner, with a schema constraint where it is
  stored and a generated or shared type where it crosses the wire. A switch over it must fail loudly on a new
  member.
- **Owners:** [implicit-coupling](../principles/architecture/implicit-coupling.md),
  [domain-constraints](../principles/data-layer/domain-constraints.md),
  [illegal-states-unrepresentable](../principles/architecture/illegal-states-unrepresentable.md).

```python
# ❌ the same four statuses spelled in the worker, the API filter and the SPA
if run.status in ("queued", "running", "cancelling"): ...
# ✅ one owner of the set
class RunStatus(StrEnum): QUEUED = "queued"; RUNNING = "running"; CANCELLING = "cancelling"; CANCELLED = "cancelled"
ACTIVE = {RunStatus.QUEUED, RunStatus.RUNNING, RunStatus.CANCELLING}
```

## 5. Absence and failure share one value

- **Tell:** one return value (`None`, `[]`, `""`, `"not available"`, a `fallback=` argument) answers both "nothing
  is saved" and "the read failed"; a catch-all wrapper turns every exception into the empty answer.
- **Repair:** make the two cases different values — a result type, a raised error, or an explicit "unavailable"
  variant — and let the caller choose. A degrade wrapper may exist only where the policy is named.
- **Owners:** [no-silent-defaults](../principles/reliability/no-silent-defaults.md),
  [errors-at-the-boundary](../principles/reliability/errors-at-the-boundary.md),
  [fail-fast](../principles/reliability/fail-fast.md).

```python
# ❌ the UI shows "no drafts" while the database is down
def drafts(user): return degrade(lambda: db.drafts(user), fallback=[])
# ✅ empty is a result; failure is not
def drafts(user) -> list[Draft]: return db.drafts(user)   # raises Unavailable; the route maps it to 503
```

## 6. Grammar without an owner

- **Tell:** one identifier format (`INV-2024-0042`, `doc#page=3`) taken apart by several regexes or `split`s that
  disagree on prefix set, digit width, or optional parts. Collect them: seven patterns for one format is a
  grammar with no parser.
- **Repair:** one parse and one format function owning the grammar; callers receive a typed value. Add the
  disagreeing inputs as cases of the one parser.
- **Owners:** [parse-dont-validate](../principles/architecture/parse-dont-validate.md),
  [helper-is-an-architecture-finding](../principles/architecture/helper-is-an-architecture-finding.md),
  [single-source-of-truth](../principles/architecture/single-source-of-truth.md).

```python
# ❌ two regexes, two grammars: one accepts INV-42, the other needs four digits
re.match(r"INV-(\d+)", ref);   re.match(r"INV-(\d{4})-(\d{4})", ref)
# ✅ one parser; every caller holds an InvoiceRef
def parse_invoice_ref(s: str) -> InvoiceRef: ...
```

## 7. Fork of upstream instead of extension

- **Tell:** a downstream module copies an upstream module and edits it; the two drift; sometimes both write a
  store (two receipts for one "verified" fact). Tell by behaviour, not name: same job, same inputs, two writers.
- **Repair:** extend through the upstream's own seam (a hook, subclass, config); where there is none, add the seam
  upstream, then delete the copy. Never paste an upstream fix downstream.
- **Owners:** [code-reusability](../principles/architecture/code-reusability.md),
  [one-logical-unit-one-home](../principles/architecture/one-logical-unit-one-home.md),
  [dependency-stability](../principles/architecture/dependency-stability.md), and the cross-repo sweep in
  [duplication](duplication.md).

```python
# ❌ the overlay carries its own copy of the verifier and writes its own receipt
def verify_bearer(token): ...   # forked from upstream auth.verify_bearer, now different
# ✅ configure the upstream verifier; one receipt
auth.configure(verifier=Verifier(audience=settings.audience))
```

## 8. Unwritten state machine in a column

- **Tell:** a nullable self-reference or timestamp that encodes current / released / replaced, written by raw
  `UPDATE`s in several modules and read by several query builders, each with its own `WHERE` for "current".
- **Repair:** name the states, one transition function and one "current" query or view; constrain the column
  (a partial unique index for "at most one current").
- **Owners:** [implicit-state-machine](../principles/architecture/implicit-state-machine.md),
  [invariant-constraints](../principles/data-layer/invariant-constraints.md),
  [one-logical-unit-one-home](../principles/architecture/one-logical-unit-one-home.md).

```sql
-- ❌ "current" means replaced_by IS NULL, in five UPDATEs and three SELECTs
UPDATE plans SET replaced_by = :new WHERE id = :old;
-- ✅ one owner of the move, and the schema refuses two current rows
CREATE UNIQUE INDEX one_current_plan ON plans (account_id) WHERE replaced_by IS NULL;
```

## 9. One-sided contract

- **Tell:** one end of an agreement exists without the other — the client retries and polls on an error code the
  server never emits; an idempotency key is sent and never honoured; a configured group list is parsed and logged
  but used only as an on/off switch. Walk each end to its partner.
- **Repair:** implement the missing side or delete the present one; put the shared constant or schema where both
  import it.
- **Owners:** [unclaimed-guarantee](../principles/clean-code/unclaimed-guarantee.md),
  [idempotency](../principles/architecture/idempotency.md),
  [implicit-coupling](../principles/architecture/implicit-coupling.md),
  [design-by-contract](../principles/reliability/design-by-contract.md).

```typescript
// ❌ retries on "RATE_LIMITED"; the API answers 429 with no such code
if (err.code === "RATE_LIMITED") return retry(call);
// ✅ the status both sides share
if (err.status === 429) return retry(call);
```

## 10. Config parsed twice with different rules

- **Tell:** one environment value read with `== "true"` here and a strict true/1/yes/on parser there, so the same
  value means two things.
- **Repair:** one settings loader returns typed decisions; delete the per-site reads.
- **Owners:** [helper-is-an-architecture-finding](../principles/architecture/helper-is-an-architecture-finding.md),
  [no-silent-defaults](../principles/reliability/no-silent-defaults.md),
  [parse-dont-validate](../principles/architecture/parse-dont-validate.md).

```python
# ❌ DEBUG=1 is on in one module and off in the other
a = os.environ.get("DEBUG") == "true";   b = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes", "on")
# ✅ parsed once
settings = Settings.from_env()   # settings.debug: bool
```

## Boundaries

A pattern is a way to **group and order** findings, never a finding by itself: file each instance under its owning
principle and let consolidation theme them. Two copies that cannot disagree (generated code, a deliberately
independent module) are guardrail cases — see [when-to-relax](when-to-relax.md).
