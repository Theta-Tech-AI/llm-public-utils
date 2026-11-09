---
name: deslop-consolidating-and-triage
description: Consolidate and triage deslop findings — decide what matters now, what can wait and what to drop, then group it into ordered work.
---

# Consolidating and triage

**Read this after aggregation and before you communicate anything.** Its job is the judgement a merged list cannot
do: a pass will always return more than anyone should act on at once, so somebody has to decide — out loud, with
reasons — what is worth attention now, what can wait, and what should be dropped.

Two failure modes it prevents, both common: reporting the *longest* list instead of the *load-bearing* one, and
reporting a flat queue with no notion of what matters.

## 1. Verify before you rank

Every candidate — corroborated or single — is read at its source line first. Confirm the quoted code is there, the
claim is about that code, and the repair would work. Findings that cannot be verified are dropped, not deferred:
a wrong finding costs more than a missing one, because it teaches the reader to skim.

## 2. Apply the guardrail

Run the list through [when-to-relax.md](../readings/when-to-relax.md) before ranking. Where the "violation" is the cheaper
truth — a small amount of duplication that keeps two modules independent, an explicit check that documents a real
edge case — drop it, and say that you dropped it. An audit that files churn is an audit nobody reads.

## 3. Score, then sort into three buckets

Score each surviving finding on three axes, not one:

- **Severity** — what breaks, and how silently. A wrong number returned without an error outranks a crash.
- **Blast radius** — how much depends on it: one script, one module, every request.
- **Fix cost** — an hour, a day, a refactor with a migration.

Then sort into buckets you will actually communicate:

| Bucket | Test | What the reader does with it |
|---|---|---|
| **Now** | high severity or wide blast radius, and cheap enough to fix while the code is fresh | fix first, before the context decays |
| **Next** | real, but contained: worth a planned slot, not an interruption | schedule it; keep it in the milestone |
| **Wait / drop** | low severity with high fix cost, or the guardrail says leave it | do not do it, and say why — with the condition that would change the answer ("if this becomes public API, revisit") |

The split is the deliverable. A list of forty findings with no bucket is not a triage, it is a burden. Buckets of
five, ten and twenty-five are usually right; if everything lands in "now", either the codebase is on fire or the
scoring was not done.

## 4. Consolidate by concern, not by finding

Before ordering, collapse to **concerns**:

- Three loci expressing one missing owner → one item, naming the owner and listing the loci.
- Two principles charging one locus → one defect, one owner (the aggregation stage decided which).
- The same repair proposed in five places → one missing component, said once.

Then **one issue per concern**, never per finding or per cell. Each carries: the owner or missing component, the
loci, the evidence (quoted, with line numbers), the repair stated so a stranger can start it, and the bucket.

## 5. Classify, then theme the cross concerns

Per-chunk fixing is the default failure at scale. In a measured pass, about 970 small reviewed local commits came
from per-chunk fixers — yet 27% of verified concerns were **cross**: one fact with several owners cannot be fixed
inside one chunk, and a chunk fixer polishes copies the real fix deletes. So before any fixer is dispatched:

1. **Classify every verified concern on two axes** — **L2**, the fact or mechanism it is about (the run status, the
   invoice reference grammar, the plan-replacement column); **L1**, the pattern class from
   [patterns](../patterns.md). Tag each *local*, *cross* (needs one owner across
   modules or layers) or *next* (design, migration or API change).
2. **Merge each L2 × L1 cluster into a theme with one owner.** A theme names the owner, the loci, and the consumers
   to reroute. Local concerns stay with their chunk; cross concerns go to themes.
3. **Order themes by dependency**: vocabularies, grammars and contracts first (everything else consumes them),
   then the consumers that re-decided them, then the cleanups that become dead.
4. **Schedule file-disjoint.** Themes that share a file never run at once; land and verify each wave before the
   next begins, so a later theme reads the code the earlier one left.

The taxonomy and clustering are the orchestration step, not bookkeeping: skip them and the pass produces many
correct commits and an unfixed disease.

**Read the reviewer's diffs yourself.** An adversarial reviewer that passes ~95% of commits (912 ok, 37 fix, 1 revert
of 950) is a signal, not a result: sample the diffs by hand before trusting the rate.

## 6. Group into a programme

Put the "now" and "next" work into a milestone or epic with a denominator, so progress is a ratio ("18 of 24
closed") rather than an unbounded queue. Order inside it by **risk per unit of effort**: the dangerous and cheap
first, because that is where attention is available.

## 7. State the edges

Before the summary leaves your hands, write down — for the reader:

- cells that were **skipped**, and why;
- findings **relaxed** under the guardrail;
- areas **not surveyed** at all;
- anything that was **failed** (a reading that quoted nothing) and left un-rerun.

Coverage claims are what make the next pass credible. An audit that claims completeness without them is the reason
the next reader trusts nothing in it.

## 8. Hand-off

The consolidated, bucketed, concern-level list is now ready to be shown. How to say it — length, shape, what leads
— is [reporting-results.md](reporting.md). Read it immediately before you speak, not now.
