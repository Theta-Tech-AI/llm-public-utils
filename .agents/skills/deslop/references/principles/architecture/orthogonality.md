---
name: deslop-architecture-orthogonality
description: Deslop principle — Orthogonality: unrelated things change independently; a unit whose independent reasons to change meet with no seam between them is welded, even when every function in it is clean.
---

# Orthogonality

> "Each software module should have one and only one reason to change."
> — Robert C. Martin, "The Single Responsibility Principle" (2014)

Two components are orthogonal when a change in one leaves the other alone. Orthogonality is a property of a unit's **reasons to change**, not of its functions. A unit that detects that something changed, reads the item from an external system, converts it, chunks it, summarises it and writes it to an index has six independent reasons to change, and each can change while the others stay untouched. The code can be correct line by line and still weld those reasons into one flow. A reader who goes function by function sees good code, and nothing in that reading enumerates the reasons to change, so the weld passes review.

The defect is the weld, not the reasons to change. Several reasons to change in one unit are fine when a seam separates them. The finding is a pair of reasons to change that cannot be separated, where a plausible change would have to touch both sides at a point with no seam. The blast radius of a change is the measure this principle shares with [Separation of Concerns](separation-of-concerns.md); here it is read from one unit's code, not from its history.

## The reasons to change, and the census

A **reason to change** is one independent way a unit could need to change. Read the reasons to change from what the unit does, never from its name or its functions' names:

- **Trigger** — what starts a run: an incoming message or request, a change appearing, or a clock tick.
- **External read or write** — which system it talks to, and what it asks of it.
- **Transformation** — what it computes from data: conversion, chunking, summarising, scoring. Each is a separate reason to change.
- **Persistence** — what it stores, and under which key.
- **Policy** — how a run copes with failure or overrun: retry, backoff, dead-lettering, budget. Trigger says when a run starts; policy says what happens when it goes wrong. A scheduled poll is one trigger, counted once.

The census **nominates** and does not convict:

1. List the units in scope: modules, classes, pipelines, dependency bundles.
2. For each unit, write one line per reason to change present, citing the line that makes it so. One line cites one reason to change.
3. A unit with two or more reasons to change is nominated. Nomination is not a finding.

## The seam, operationally

A **seam** between two reasons to change is a **contract**: the types and values that cross it. A seam counts only when that contract is expressible in the unit's own vocabulary, meaning the core's own records, identifiers and values. A record or value the composition defines and owns jointly is core; a shape received from or keyed to one collaborator is that collaborator's representation; bare primitives are core unless their meaning is a collaborator's vocabulary. If what crosses is one collaborator's representation (its record shape, identifiers, metadata fields, status values or parent links), the seam is **nominal** and the reasons to change stay welded, however many ports the unit holds. A private helper function is never a seam by itself.

The stub test decides it. A second, different implementation could be written against the contract without imitating the first one's shape. Equivalently, stub one side behind the contract and the other side needs no edit. If writing the second implementation means copying the first one's shape, the seam is nominal. A call that performs one reason to change's work inside another reason to change's statement is not a seam, and neither is a loop whose body performs two reasons to change.

## The degree test is the report gate

A nominated unit becomes a finding only when its degree test fails. Two canonical probes run first, in every nominated unit, before any others:

- **Probe A** — add a second, different implementation of each external system the unit reads or writes.
- **Probe B** — add a second consumer of whatever the unit's trigger detects.

For each probe, count the touch points the change needs inside the unit, and the reasons to change they span. A touch point that spans two reasons to change with no contract in the unit's own vocabulary is the finding. Cite each touch point and the reason to change it belongs to. Other plausible requirements may follow. Where the canonical probes have no grip, because the unit has no external system or no trigger, a plausible-requirement probe for the nominated pair of reasons to change substitutes, and its cited touch-point result opens the gate. Without a cited probe result, the nomination stays a nomination.

## The tells

Each tell nominates; none decides:

1. **A dependency bundle mixing a source client with sink or transform services.** The collaborators of one unit span an external read and a write or a transformation.
2. **A trigger handler that performs the work it was triggered for.** The handler is the trigger reason and the work reason at once.
3. **A persisted key derived from one collaborator's representation.** The key must come from a value the unit owns, not from a collaborator's shape.
4. **A second implementation that imitates the first collaborator's interface.** The reason to change has no seam of its own; a copy stands in for it.

## The diagnostics

Decidable from the code alone:

1. **Census** — count and cite the reasons to change of each unit.
2. **Trigger-work** — does the code that starts a run also perform the work it starts? If so, the trigger and the work share one body.
3. **Emit** — does the unit's output for other consumers exist as a value, or must a consumer call the producer's internals to get state?

Judgements, each citing the line pair it rests on:

4. **Seam** — for each pair of reasons to change, apply the stub test: could a second, different implementation of one side be written against the contract without imitating the other side's shape?
5. **Independence** — could a change to one of the two (its format, schedule, policy or external system) leave the other's code unedited? This is a counterfactual, so cite the lines a change would touch.
6. **Degree** — the two canonical probes, which gate the report.

## The shape, before and after

```python
# ❌ monitor.py — one flow with six independent reasons to change
class ChangeMonitor:
    def __init__(self, client: SourceClient, converter: Converter, chunker: Chunker,
                 index: SearchIndex, summarizer: Summarizer) -> None: ...

    def poll(self, folder_id: str) -> None:                              # trigger: a clock tick
        for item in self._client.list_changes(folder_id):                # external read: the listing
            raw = self._client.download(item.id)                         # external read: the same source
            text = self._converter.to_text(raw)                          # transformation: conversion
            for part in self._chunker.split(text):                       # transformation: chunking
                self._index.upsert(item_id=item.id, body=part,           # persistence, keyed by the source's id
                                   summary=self._summarizer.run(part))   # transformation: summarising
```

Probe A fails. A second source must be a second client whose listing yields the first client's `.id` and `.name` fields, and whose download takes the first client's ids. What crosses is one collaborator's representation, so the seam is nominal. Probe B fails. A second consumer of the listing cannot reuse it without copying the loop, because detection and work share one body; the touch points span the trigger and read reasons to change and the work reasons to change with no contract between them. The unit is welded, and it is a finding.

```python
# ✅ detector.py — one reason to change: "what changed". It emits records and does no work.
@dataclass(frozen=True)
class ChangeRecord:
    item_id: str
    revision: str

class ChangeDetector:
    def __init__(self, feed: ChangeFeed, subscribers: list[Callable[[ChangeRecord], None]]) -> None:
        self._feed, self._subscribers = feed, subscribers    # the external read sits behind the feed port

    def poll(self, scope: str) -> None:
        for change in self._feed.changes(scope):
            for notify in self._subscribers:
                notify(change)                               # the detector stops at the record

# ingest.py — one consumer; its reasons to change are fetch, conversion and persistence
class IngestConsumer:
    def __init__(self, store: DocumentStore, converter: Converter, index: SearchIndex) -> None:
        self._store, self._converter, self._index = store, converter, index

    def __call__(self, change: ChangeRecord) -> None:
        raw = self._store.open(change.item_id)               # seam: bytes, the fetch's whole output
        self._index.upsert(item_id=change.item_id, body=self._converter.to_text(raw))   # seam: text

# audit.py — another consumer, added without touching the detector
class AuditConsumer:
    def __call__(self, change: ChangeRecord) -> None:
        log.info("changed %s at %s", change.item_id, change.revision)
```

`IngestConsumer` matches tell 1, since its bundle holds a source port, a converter and an index. It passes both probes. Probe A: a second store returns bytes for a core `item_id`, and a second converter returns text; neither copies the first one's shape. Probe B: an audit consumer reads only the core's `ChangeRecord`. The crossing data is the core's own vocabulary, so tell 3 does not fire either: `item_id` is the record's own field, and the feed's representation ends in its adapter. `ChangeDetector.poll` passes too: its contract is `ChangeRecord`, and a second feed writes records without imitating the first.

## The repair

1. **Give each reason to change one owner, separated by a value or a port the flow crosses.** The detector's output is a `ChangeRecord`.
2. **Put every external read or write behind a port the consumer holds.** The fetch moves to the store port, and the detector never sees the source's API.
3. **Make consumers subscribers.** A new consumer is a line at the composition root.
4. **Re-key persistence on the unit's own identity, not the collaborator's.** Migrate by renaming and backfilling, and keep the stored values.
5. **Hold the line with a test.** Construct the detector with no subscribers and assert that no fetch occurs. The test is decidable and fails the moment the weld returns.

## Boundaries

- **Cost rule: the probes decide whether a seam is worth building.** A seam costs a contract and an indirection. It earns that cost when a probe needs a second implementation or a second consumer. Where the probes find neither, the unit gains nothing from a seam, and the gate sets it aside. Scripts under 100 lines are exempt, as [When to Relax](../../readings/when-to-relax.md) states.
- **Prototypes are exempt**, as [When to Relax](../../readings/when-to-relax.md) states for spikes.
- **Performance boundary.** On a hot path a seam can cost an allocation, a dispatch or a serialisation per item. Deliberate welding there is legitimate. Measure the cost, and record the weld and the measurement beside the code, as [SOLID](solid.md) exempts performance-critical paths.
- **Deliberate cohesion is a decision, not a defect.** Two reasons to change that must share one transaction or one lock are welded on purpose. Record the invariant beside the code.
- **A composed pipeline is not a weld** when each stage is its own unit and the composition is wiring at the composition root.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Orthogonality | Andy Hunt & Dave Thomas, *The Pragmatic Programmer* (1999) | The concept: independent components, measured by how many modules a requirement change touches. Paraphrased; the tip's exact wording could not be confirmed at source. |
| Decomposition by design decisions likely to change | David L. Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules" (1972) | A unit should hide one decision likely to change. The census finds the decisions a unit holds. Paraphrased; not quoted. |
| Single responsibility | Robert C. Martin, "The Single Responsibility Principle" (2014) | The epigraph. The essay ties each module to the people who request its changes; this census counts a unit's reasons to change, read from its behaviour, not its requesters. |

**What is this library's own:** the census, which reads a unit's reasons to change from its behaviour and not from its names, and the seam and degree tests that decide whether two reasons to change can move apart.

In relation to other principles, orthogonality sits among its neighbours thus:

| Principle | Relationship |
|-----------|--------------|
| [**Separation of Concerns**](separation-of-concerns.md) | SoC reads where one logical change lands across folders and history. This reads the reasons to change inside one unit from its code. Same property, two instruments. |
| [**Modularity**](modularity.md) | A deep module hides one design decision. The census tells you whether a unit hides one or several. |
| [**Implicit Coupling**](implicit-coupling.md) | Its degree count is the degree test here. Implicit agreements are what keep two reasons to change from moving apart in practice. |
| [**SOLID**](solid.md) | Dependency Inversion is the port that separates a reason to change from its collaborator. This principle says which reasons to change need one. |
| [**Dependency Injection**](dependency-injection.md) | Injection removes one source of coupling at construction; the census says which reasons to change are worth removing. |

## Summary

1. **Orthogonality is a property of reasons to change, not of functions.** A unit can be clean line by line and still weld reasons to change.
2. **Census the reasons to change, citing a line for each.** Two or more nominates a unit; nomination is not a finding.
3. **A seam is a contract in the unit's own vocabulary, whose two sides each hold one reason to change.** A collaborator's representation crossing it makes the seam nominal.
4. **A nomination becomes a finding only when a probe fails:** a second implementation or a second consumer needs a touch point that spans two reasons to change with no such contract.
5. **Cost, performance and deliberate cohesion keep some welds legitimate**, and the reason is recorded beside the code.
