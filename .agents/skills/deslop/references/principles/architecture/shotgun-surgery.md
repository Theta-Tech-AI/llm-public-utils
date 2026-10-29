---
name: deslop-architecture-shotgun-surgery
description: Deslop principle — Shotgun Surgery: one logical change that must be edited in many files and folders, because the code's unit of change does not match its unit of design.
---

# Shotgun Surgery

> "Things that change together should be put together. If you have to make a lot of edits all over the place to make
> one logical change then it's a sign your design has a coupling problem."
> — Samman Technical Coaching, on Fowler's *Shotgun Surgery*

A **change-set** is what one logical change actually costs: the files its author had to touch. When a single
capability edit lands in eight files across five folders, that number is a measurement of the design — not of the
author's care. The disease is that the code's **unit of change** (one concept, evolving) does not match its
**unit of layout** (one technical role, frozen). The most common cause is not accidental: a **layer-first** tree
guarantees it, because a feature's rule, its query, its DTO, its route and its validator were given five different
homes before the first feature existed.

```text
# ❌ layer-first — every feature is a five-folder change by construction
src/
  controllers/order_controller.py
  services/order_service.py
  repositories/order_repository.py
  models/order.py
  validators/order_validator.py
  serializers/order_serializer.py
# "orders can be partially refunded" edits all six, plus one test file per layer
```

```text
# ✅ feature-first — the concept owns its folder, and the change is one place
src/orders/
  __init__.py      # the only surface the rest of the app may import
  model.py
  store.py
  api.py
  refunds.py       # the new rule and its tests land beside the rest of orders
```

The second half of the repair is a **seam**: one public surface per capability (`__init__.py`, an index module, an
exported interface) so other folders cannot reach the internals and re-create the crossing later.

## What this adds over its neighbours

[Separation of Concerns](separation-of-concerns.md) names shotgun surgery as a tell in one sentence and prescribes
"high cohesion, low coupling". This file supplies the instrument: **read git, not opinion.** The change-set size of
real commits is objective, countable, and it is the only available measure of what the design costs per feature.

## The tests

1. **Change-set test** — take the last five capability commits (`git log --name-only -5 -- <paths>`). Count the
   distinct directories each touched. One logical change crossing four or more folders is the finding.
2. **Layout test** — list the top-level folders. Named for a technical role (`controllers/`, `services/`,
   `models/`, `utils/`) or for a capability (`orders/`, `billing/`, `identity/`)? Role-named layout *decides* the
   scattering before any code is written.
3. **Owner test** — name the module with authority over the concept being changed. If the answer is a list
   ("the service plus the validator plus the serializer"), the concept has no owner.
4. **Mirror test** — run it the other way: `git log --name-only -- <one file>`. A file whose history mixes unrelated
   edits is the opposite defect; see [a god file](god-file.md).
5. **Newcomer test** — delete the folder tree and ask what a new engineer must be told to add a feature. A list of
   five locations is the cost, stated plainly.

## The family: one disease, many costumes

| Change | The files it drags along | The missing unit |
|---|---|---|
| add a field to a core concept | migration, model, DTO, serializer, validator, API contract, fixture | the concept's folder |
| add a payment provider | `providers/`, `services/`, `routes/`, `config/`, `tests/` — five folders, one feature | a provider module with one surface |
| rename a domain term | every folder, because the term is not owned anywhere | the one module that names the domain |
| change a validation rule | the rule in three layers, one of them authoritative | one parser at the boundary |

## The repair

**Move the unit of layout to the unit of change**: group by capability, expose one surface per group, and let a
crossing change be the thing review rejects. Enforcement beats exhortation — an import rule that refuses
"orders → billing internals" ([Layering Violations](layering-violations.md)) keeps the layout honest after the
first tidy-up, and the reorganization is done incrementally by moving one capability at a time, not by a big-bang
restructure.

## Boundaries

Some crossing is legitimate. A genuinely cross-cutting concern (logging, authentication, tracing) should have *one*
seam, and the finding is the missing seam, not the spread. Framework-mandated layouts (Django apps, Rails MVC,
Next.js routes) impose some crossing — the finding is then domain policy living in the framework's folders. A repo
split by deployment target is not layer-first. And a split that only relocates lines satisfies nobody: see the
counting rules in [a simplification campaign](../../modes/campaign.md).

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Shotgun Surgery | Martin Fowler, *Refactoring*; catalogued by Refactoring.Guru as a "change preventer" | Names the smell and its opposite, Divergent Change. This file applies it at folder granularity. |
| Package by feature / Screaming Architecture | Robert C. Martin; widely documented practitioner literature | The layout repair. |

**What is this library's own:** the change-set test — reading the last N commits and counting the directories crossed
— as a decidable instrument, and the pairing with the mirror test so a pass reports the right one of the two
opposite smells.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Separation of Concerns**](separation-of-concerns.md) | The parent principle; this is its measurable reading. |
| [**A God File**](god-file.md) | The mirror defect: many changes, one file. |
| [**Modularity**](modularity.md) | What a capability folder should be: a deep module with one surface. |
| [**One Logical Unit, One Home**](one-logical-unit-one-home.md) | The same disease seen as a unit scattered across packages. |
| [**Layering Violations**](layering-violations.md) | The enforceable version: arrows that keep the new layout from eroding. |

## Summary

1. **One logical change should touch one place** — the change-set is the design's real price.
2. **Layer-first layouts manufacture the smell** — this is a structural cause, not an author's mistake.
3. **Read git, not opinion**: last five commits, count the folders crossed.
4. **Group by capability, expose one surface**, and move one capability at a time.
5. **Check the mirror before repairing** — many changes landing in one file is the opposite fix.
