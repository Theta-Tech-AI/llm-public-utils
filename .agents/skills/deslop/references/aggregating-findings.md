---
name: deslop-aggregating-findings
description: Merge deslop cell reports into one candidate list — corroborated, single, disputed — and account for coverage before anything is ordered.
---

# Aggregating findings

**Read this the moment more than one reading has reported** — a planned pass, several agents, or a second-opinion
run. Not before: during planning you do not need this. [pass-planning.md](pass-planning.md) produced the cells;
this stage turns their reports into **one candidate list**, still unordered.

A pass that skips this stage reports the same defect three times under three names, files the loudest rather than
the worst, and cannot say what it never looked at.

## 1. Merge on locus + principle

Normalise first, or the merge is fiction:

- **Paths** relative to the repository root, one spelling, no `./`, no absolute prefixes.
- **Loci** as file + line (a range is fine), and the symbol where the report names one.
- **Principles** by their library file slug (`separation-of-concerns`, `parse-dont-validate`), not by prose. A
  finding charged as "layering" or "concern bleed" is Separation of Concerns wearing a costume; map it.

Then sort the lot into three buckets:

| Bucket | Meaning | What you owe it |
|---|---|---|
| **Corroborated** | same locus, same principle, charged by more than one reading | read the source line before believing it — two readers can share one misreading, especially when they read the same index row |
| **Single** | one reading, one instance | **not weaker.** One instance is enough to be real; several readings only say it was subtle. Verify at the line, then keep it |
| **Disputed** | same locus charged under two different principles | an adjudication, not a duplicate: this is one defect with two candidate owners. Pick the owner whose repair *deletes* the most, and drop the other charge |

Two rules that do the real work here:

- **One defect, one charge.** Three loci expressing one missing owner are one finding naming the owner. Two
  principles charging one locus are one defect; keep the better owner.
- **Corroboration is a hint, never the criterion.** A single sighting in a quiet corner outranks a pair of
  sightings that came from a copy-pasted reading list.

## 2. Account for coverage, not only findings

Findings are half the report. For every cell that ran, record:

- what it **declared reading** — the `files-read-<cell>.txt` manifest diffed against the assignment it was
  given. A file assigned and never opened is a **failed reading**, whatever its report says;
- what it **quoted** — a cell that quotes nothing has not read;
- what it **declined**, and why — a declared "no SQL here" is a healthy result, and it is the only evidence that a
  group looked and found nothing;
- what it **could not decide**, and what would decide it.

A cell that reports zero findings and quotes no code is a **failed reading**, not a clean slice. Re-run it — with
a different slice, a sharper prompt, or a stronger model — before accepting a thin result at face value.

## 3. Carry the leads forward

- **Cross-cell sightings**: a reading that noticed something outside its assigned principles. These are leads for
  the next pass, not findings for this one; list them separately and do not file them.
- **Neighbourhoods**: a locus that produced several findings from one group marks a place worth a directed deep
  dive (one slice, one group, every file read).
- **Recurring costumes**: the same repair proposed at five loci is one missing component. Say so once.

## 4. Deliverable of this stage

A single **candidate list**, each entry carrying: locus, principle, severity as reported, the evidence quoted, the
proposed repair, the bucket it landed in (corroborated / single / disputed-resolved), and whether it was verified
at the source line yet.

Nothing here is ordered, and nothing is filed. That is the next stage: read
[consolidating-and-triage.md](consolidating-and-triage.md) before you tell anyone anything.
