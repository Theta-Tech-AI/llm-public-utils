---
name: deslop-architecture-god-file
description: Deslop principle — A God File: a file whose name cannot state its responsibility, because unrelated changes from unrelated owners all land in it.
---

# A God File

> "Classes usually start small. But over time, they get bloated as the program grows."
> — Refactoring.Guru, *Large Class* — the same accumulation, one unit up, where no compiler notices

Size alone is not the finding: a 3,000-line generated table, a schema module, or a long single-concept implementation
is honest work. The finding is **divergent change at file granularity** — the file answers many questions that change
for unrelated reasons, so unrelated features, unrelated owners and unrelated reviewers all queue on the same path. The
confession is usually in the name: `utils.py`, `helpers.py`, `common.py`, `manager.py`, `order_service_helpers.py`.
A file that cannot state its responsibility in a noun from the domain has no owner, and its contents will accumulate
whatever the last author could not place.

```python
# ❌ utils.py — 1,900 lines, and the name is the admission
def parse_date(s): ...       # billing
def send_email(to, t): ...   # notifications
def calculate_tax(a, r): ... # pricing
def retry(fn, n): ...        # resilience — a second copy of one that already exists
def format_address(a): ...   # shipping
```

```python
# ✅ each concept names its own home; utils.py is deleted, not shrunk
billing/tax.py           # calculate_tax, its rates table and its tests
notifications/email.py   # send_email and its template resolution
shipping/address.py      # format_address beside the address model it formats
# resilience/retry.py    # already existed: the check came first, so nothing was created
```

Note the last line: the reverse test frequently shows the god file held **no unique knowledge** — it held a second
copy of decisions already owned elsewhere, filed where they were easy to reach.

## What this adds over its neighbours

[Modularity](modularity.md) says a "God module" encapsulates nothing, and
[Separation of Concerns](separation-of-concerns.md) names the god object — both at class level, both as a siteline.
This file makes the repository's real unit, the **file**, decidable: five tests that a reader can run on the file in
front of them, without a metrics tool and without arguing about responsibilities. Taken alone, test 2 (the name) is
sufficient to report; the history test needs enough commits to speak (ten is a working threshold), and a short or
squashed history means the finding rests on the name, the import list and the extraction test instead.

## The tests

1. **Divergent-change test** — `git log --name-only -- <file>`. Count the distinct feature areas in the commit
   subjects. **Three or more unrelated areas across its last ten commits** is the finding; it is the mirror of
   [shotgun surgery](shotgun-surgery.md), and you must report only the one the evidence supports.
2. **Name test** — can the responsibility be stated without `and`, or without `utils` / `helpers` / `common` /
   `manager` / `misc`? If not, the file has no owner to state.
3. **Leaf test** — what does it import? A leaf module imports the standard library or its own folder, never several
   of the app's own layers. A file importing the HTTP layer, the persistence layer and the domain is a wiring point
   pretending to be a utility.
4. **Extraction test** — split it on paper by reason to change. If two pieces then immediately need each other, they
   were one concept and the file was merely long: not this finding.
5. **Dead-copy test** — before extracting anything, grep each function for an existing owner. God files are where
   duplication hides, and deleting a copy is cheaper and safer than moving it.

## The family: one disease, many costumes

| Artifact | The reason it accumulated | The missing unit |
|---|---|---|
| `utils.py` / `helpers.py` | no owner for "small shared things" | one home per concept; a small shared set with its own name |
| `models.py` with 40 classes | no capability boundaries | one module per concept |
| `service.py` that also queries, validates and formats | layer-first layout pushed everything here | the capability folder |
| one 5,000-line module with a good name | one concept, poorly partitioned | internal structure by reason to change, not a new file per class |

## The repair

**Split by reason to change, never by line count.** Extract each responsibility to a home named by domain vocabulary,
delete the residual bucket file, and let its disappearance be the measure — a god file that survives at 300 lines was
not repaired, it was trimmed. Do the dead-copy test first so the split does not launder duplication into new files.

## Boundaries

Generated code, database schemas, vendored sources, fixtures and registry-style files are legitimately long. A
single-concept module may be large and correct. Splitting to satisfy a line-count rule is the anti-pattern this file
borders: a split that only relocates lines counts as nothing in
[a campaign](../../modes/campaign.md), and class-per-file fragmentation replaces one unowned file with thirty
unowned files. The measure is always *reasons to change*, not size.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Long Method / Large Class | Refactoring.Guru, "bloaters" | The class-scoped catalogues this file extends to the file. |
| Divergent Change | Martin Fowler, *Refactoring* | The precise name for the defect: one unit edited for many unrelated reasons. |
| Big Ball of Mud | Foote & Yoder (1997) | The system-wide form of the same accumulation. |

**What is this library's own:** applying the smell at file granularity — the repository's real unit of change — and
the name-plus-history pair as a decidable test that needs no metric tool.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Shotgun Surgery**](shotgun-surgery.md) | The mirror: one change, many files. Report the one the evidence shows. |
| [**Modularity**](modularity.md) | What the extracted pieces must be — deep modules, one surface. |
| [**Separation of Concerns**](separation-of-concerns.md) | The principle the file violates; this file is its instrument. |
| [**One Logical Unit, One Home**](one-logical-unit-one-home.md) | The knowledge of a god file is usually already owned elsewhere. |
| [**Small Functions**](../clean-code/small-functions.md) | Function granularity; this is the file. |

## Summary

1. **A file that cannot state its responsibility has no owner** — the name is the first test.
2. **Divergent change, read from history**, is the decidable evidence — not line count.
3. **God files hide duplication**; run the dead-copy test before extracting anything.
4. **Split by reason to change and delete the bucket**, and treat its disappearance as the fix.
5. **Never split for size alone** — relocation is not simplification.
