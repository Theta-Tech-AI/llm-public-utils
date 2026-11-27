---
name: deslop-architecture-freshness-from-inputs
description: Deslop principle — Freshness From Inputs: stale only when its inputs changed; never decided by a time or an event.
---

# Freshness From Inputs

**Why this is slop:** A staleness test built on clocks, events or the producer's version redoes finished work when nothing changed, and serves old work as fresh when a real input changed without an event.

> "There are only two hard things in Computer Science: cache invalidation and naming things."
> — Phil Karlton

Derived work is anything computed from other data and kept: a cache entry, a generated draft, a check's findings, a compiled file, a summary, a report. Each one is a function of what it read. So there is only one honest answer to "is this still current?": **has anything it read changed?** Answer it by storing, beside the output, a digest of exactly what the producer read (its *basis*), and by comparing that digest with a fresh one computed by the same function.

The substitutes look cheaper, and each one fails in a direction nobody sees in a test:

- **A time or an event** (`updated_at > built_at`, "changed after the last lock", "a run happened since"). It fires when nothing changed: a save of identical text, an unlock and re-lock, a touch. It also misses a change that came without an event, such as a backfill, a restore or a clock skew. `make` decides by file times, so `touch` rebuilds a target; Bazel keys each action on a digest of its inputs and its command line instead.
- **A key that is too wide** (every setting, every fact in the project, the whole input set). One change anywhere makes everything stale. The results are still right, only slow and expensive, so nobody files the bug.
- **A key that is too narrow** (an input the producer reads is missing from the key). Old output is served as current. This is the dangerous direction: it is wrong, not slow.
- <a id="producer-version"></a>**The producer's own version in the key, with no decision behind it** (code version, model id, prompt hash). Every release makes all finished work stale. Whether a new producer must redo old work is a **policy decision**, and it has two honest answers. (1) The change alters the meaning of every past output, for example a compiler flag, an incompatible output format, or a fix to a wrong algorithm. Then the version belongs in the key, with the reason written beside it; build systems key on the command line for this reason. (2) The change is an improvement that old, reviewed work does not need, for example a better model or a reworded prompt. Then the version is *provenance*: store it beside the output, do not key on it, and make any redo a recorded action. Work that people review or sign needs the second answer by default, because a deploy must not reopen it.

## Example

A function checks one section of a report against the passages and facts that the section cites, and it stores the findings. When must it check the section again?

```python
# ❌ Stale by time, keyed on everything, and on the checker's version
def needs_check(section, last, project):
    return (last is None
            or section.saved_at > last.created_at            # an identical re-save checks again
            or project.facts_changed_at > last.created_at    # one new fact anywhere re-checks every section
            or last.checker_version != CHECKER_VERSION)      # every deploy re-checks everything

# ✅ Stale only when what it read changed; the checker's version is provenance
def basis(section, passages, facts) -> str:
    read = {"text": section.text,
            "passages": sorted((p.id, p.text) for p in passages.cited_by(section)),
            "facts": {key: facts[key] for key in section.cited_fact_keys()}}
    return sha256(canonical_json(read)).hexdigest()

def needs_check(section, last, passages, facts) -> bool:
    return last is None or last.basis != basis(section, passages, facts)

# Stored beside the findings: basis (the key); checker_version and model_id as provenance, by a written
# decision: a new checker applies to new text, and re-checking old text is a recorded action.
```

The ✅ version has one owner of "what this check depends on" (`basis`). The producer and every reader that asks "is it current?" call it.

## How to find it

1. **List every place that answers "is it stale?"** That includes "is it owed?", "must it run again?" and "is it current?". Search for time comparisons (`> .*_at`, `changed after`, `since the last`), and for `stale`, `owed`, `cache_key`, `digest`, `fingerprint`.
2. **For each place, open the producer and write down what it reads.** Include every argument, every query and every file.
3. **Compare the test with that list:**
   - It uses a time or an event: finding.
   - The key holds something the producer does not read: too wide. Look at the miss rate.
   - The producer reads something the key lacks: too narrow. File this at a higher severity, because it serves old output as current.
   - The key holds the producer's version: check it against [the producer-version policy](#producer-version). If no decision is written, that is the finding.
4. **Count the owners.** Two places that compute the basis of one output in different ways are [one fact, many owners](../../patterns/one-fact-many-owners.md).
5. **Measure.** Record how often stored work is reused. On every miss, log which part of the basis changed (part names and short digests, no content). Without that line, a too-wide key looks like normal traffic.

## How to fix it

1. Put one `basis()` function beside the producer. It digests exactly what the producer reads, in a canonical form.
2. Store the basis with the output, together with provenance (producer version, model, time). This is [metadata beside content](metadata-beside-content.md).
3. Make every reader that asks "stale?", "owed?" or "current?" compare the stored basis with a fresh `basis()`. Delete their own time tests.
4. If a new producer version must redo old work, follow [the producer-version policy](#producer-version).
5. Old outputs that have no stored basis: give them one named legacy rule, for example "treat as current until the next real change". Do not scatter fallbacks.

## When a time is the right test

- **Inputs you cannot read.** For a remote resource you do not hold, a time to live or a validator such as an HTTP `ETag` or `Last-Modified` is the only signal. Say so in the code.
- **Inputs that are immutable and versioned.** If an input never changes after it is written, its version id is a safe key. Two versions with the same bytes but different ids cause one extra, harmless re-run; an id can never hide a change.
- **Expiry that is the rule itself.** A token that is valid for an hour, or a quote that is valid for a day. The time is the meaning, not a proxy for change.

---

In relation to other principles, freshness from inputs:

| Principle | Relationship |
|-----------|--------------|
| [**Match the Grain**](../reliability/match-the-grain.md) | The general rule: every mechanism around work, staleness included, acts per unit; this file owns how staleness is decided |
| [**Idempotency**](idempotency.md) | Idempotency makes a repeated run harmless; this decides whether a run is needed at all |
| [**Single Source of Truth**](single-source-of-truth.md) | `basis()` is the one owner of "what this output depends on"; time tests are second owners that disagree |
| [**Liveness**](../reliability/liveness.md) | Liveness asks who moves a stale state forward; this decides, from content, whether the state is stale |
| [**Metadata Beside Content**](metadata-beside-content.md) | The basis and the provenance travel beside the output, never inside it |
| [**Let the Database Own Timestamps**](../data-layer/database-timestamps.md) | A timestamp records *when*; it never answers *whether something changed* |
| [**No Silent Defaults**](../reliability/no-silent-defaults.md) | A missing basis is unknown, not current; the legacy rule for it is named once |

## Summary

1. **Stale means its inputs changed.** Store a digest of exactly what the producer read, and compare it.
2. **Times and events are not changes.** An identical save, or an unlock and re-lock, must leave derived work current.
3. **Size the key to what was read** ([match the grain](../reliability/match-the-grain.md)). A key that is too wide wastes work quietly. A key that is too narrow serves old output as current.
4. **A producer's version in the key is a written policy decision**: see [the producer-version policy](#producer-version).
5. **Log what changed on every miss**, so a reader can tell a real change from a key that is too wide.
