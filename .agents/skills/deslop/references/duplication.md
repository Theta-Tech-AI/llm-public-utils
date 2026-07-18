---
name: deslop-duplication
description: How to hunt duplication beyond token scanners — the three-axis taxonomy, semantic dedup sweeps, and verification rules for the deslop skill.
---

## Hunting Duplication — Beyond Token Scanners

Mechanical clone detectors (jscpd, token/AST diffing) only catch byte-for-byte
or near-identical text. The more expensive duplication is semantic: the same
business rule reimplemented with different variable names, different control
flow, or split across files — invisible to any scanner, visible only to
someone who actually reads the code. A duplication hunt that only runs a
scanner is a sample, not a sweep.

Be aggressively skeptical about duplication. Search for duplicate logic, data
shape decisions, validation rules, error mapping, state transitions, SQL
fragments, constants, tests, and UI workflow patterns — not only pasted code.
When two places encode the same decision for the same reason, treat that as a
real finding even if the syntax is different. Keep asking "what knowledge is
being repeated here?" until the duplicated rule has one owner or you can clearly
explain why the resemblance is incidental.

**Use the Rule of Two for confirmed knowledge duplication.** Two occurrences
of the SAME knowledge — not two similar-looking blocks, the actual same business
rule doing the same job on the same inputs — is duplication now. The question
is always "is this the same knowledge," never "how many times does it appear."
Apply the True-Knowledge-Duplication-vs-Incidental-Similarity test from the DRY section
of [architecture.md](architecture.md) starting at the second occurrence.

**A taxonomy of duplication — hunt on three axes.** "Duplication" is not one
thing; a sweep that only imagines copy-pasted blocks misses most of it. Slice
the hunt along three independent axes: WHAT is duplicated, WHERE it lives, and
HOW it fails. Each cell of that grid is a different search technique.

*Axis 1 — WHAT is duplicated (the substance):*

1. **Text/token clones** — literal copy-paste, possibly renamed. The only kind
   scanners catch. Cheapest to find, often the least interesting.
2. **Logic/algorithm duplication** — the same computation re-expressed with
   different names, reordered branches, or a different idiom.
3. **Business-rule duplication** — the same *decision* (eligibility, gating,
   validation, staleness) encoded independently at two decision points.
4. **Flow/orchestration duplication** — the same multi-step sequence
   (validate → mutate → audit → notify) re-scripted across handlers.
5. **Control-flow skeleton duplication** — the same try/except/retry/branch
   shell wrapped around different cores (retry loops, lock idioms).
6. **Constant/literal duplication** — magic strings, status enums, sentinels,
   thresholds, poll intervals, event-type names free-typed at each use site.
7. **Data-structure/shape duplication** — one record shape declared as a
   TypedDict AND a Pydantic model AND a TS interface AND a DDL column list.
8. **Query/predicate duplication** — the same logical WHERE/JOIN ("latest
   version of X", "active run for Y") re-derived in multiple queries with
   subtly different SQL.
9. **Schema/DDL duplication** — the same table/trigger shaped by more than
   one ensure/migration path.
10. **State duplication** — the same fact persisted in two stores
    (client cache + server, two tables, derived column + source) with no
    single writer.
11. **Abstraction duplication** — two competing helpers/base classes/wrapper
    layers for the same concept, each with partial adoption.
12. **Utility duplication** — generic helpers (date formatting, retry,
    slugify, clamping) re-implemented per module, or re-implemented locally
    when a vendored/upstream utility already exists.
13. **Interface/API duplication** — two endpoints doing the same job;
    inconsistent error envelopes/pagination across sibling routes; duplicated
    client wrappers.
14. **Configuration duplication** — the same values/lists/section orders in
    multiple config files, env templates, IaC modules, CI workflows.
15. **Prompt/instruction duplication** — the same LLM rule (citation policy,
    identity constraints, formatting) restated across prompt surfaces that
    can drift independently.
16. **Structural/organizational duplication** — parallel package trees or
    file layouts that must evolve in lockstep; whole shadow/fork files
    (overlay-vs-upstream) differing in a few lines.
17. **Temporal duplication** — old and new implementations coexisting after a
    migration ("dual paths", provider-order knobs, dead fallbacks).
18. **Test-knowledge duplication** — fixtures, scaffolds, and patch-sets
    encoding the same setup knowledge across suites (real, but usually the
    lowest-priority tier).

*Axis 2 — WHERE it lives (the boundary):* intra-function self-clone →
intra-file → cross-file within a module → cross-module → cross-layer
(frontend ↔ backend ↔ DB) → cross-artifact-type (code ↔ config ↔ prompt ↔
schema ↔ docs) → cross-repo (overlay ↔ upstream, fork ↔ origin) →
cross-language. Search cost rises along this axis — and so does drift damage,
because fewer eyes ever see both copies at once.

*Axis 3 — HOW it fails (why it matters):* silent drift (copies diverge and one
becomes a lie); shotgun surgery (every change needs N synchronized edits);
inconsistent behavior (the user hits a different rule depending on code path);
misleading authority (readers trust the stale copy — worst when a doc or
guidance file *claims* to quote the authoritative text); doubled test burden.
Rank findings by failure mode, not by clone size: a 2-line already-drifted
contract beats a 200-line mechanically-identical scaffold.

**Empirical notes from mining ~900 real dedup findings** (multiple scanner
generations over one production codebase):

- **Where fixing pays:** local, mechanical, single-language clones — intra-file
  self-clones, sibling-module logic clones, router/endpoint patterns, and
  schema/DDL duplication had ~100% fix rates. **Where it stalls:** cross-layer
  contract drift and config/prompt drift — real and dangerous, but the remedy
  is a shared source of truth, codegen, or a sync contract test, not a code
  move; file those with the remedy named or they rot.
- **Dedupe the dedup tracker first.** Successive scanner generations re-file
  the same clones (one triple-clone was filed 9–12 times). Before filing,
  search open AND closed prior findings; before fixing, re-scan at HEAD — the
  clone may already be gone.
- **Deliberate symmetry is the dominant false positive.** Parallel domain
  packages built to the same scaffold, framework DI idioms, per-model config
  lines, parent→child prop passing, and belt-and-suspenders security checks
  *look* duplicated and must not be merged. So do test seams: module-level
  wrappers kept so tests can patch by name. Ask "would merging couple things
  that evolve independently?" before proposing an extraction.
- **The gold finding is already-drifted duplication**: two surfaces that claim
  to state the same contract and already disagree. Diff every pair of
  surfaces that *should* agree (guidance vs renderer, DB CHECK vs frontend
  enum, template vs prompt) — where they differ, you have both a bug and the
  proof the duplication matters. Where they still agree, pin them with a sync
  contract test so the drift fails loudly next time.

**Two complementary approaches — use both, they catch different things:**

- **Token/AST matching (mechanical).** Tools like `jscpd`, `pmd-cpd`, or a
  simple AST-diff catch byte-for-byte or near-identical text fast and
  cheaply, with zero false negatives on literal copy-paste. Run one early in
  a pass — it's the quickest way to find the "someone copy-pasted this file
  and changed three lines" class of duplication, and it's exhaustive over
  the whole repo in seconds where a manual read is not. Concretely:
  `npx jscpd <path> --min-lines 5 --min-tokens 50 --reporters console,json`
  (tune `--min-lines`/`--min-tokens` down for a small codebase, up for a
  large monorepo to keep the hit list reviewable), then triage every hit —
  a scanner has no concept of "same knowledge," so a hit can be incidental
  (two unrelated 5-line blocks that happen to match) or load-bearing (the
  same validation rule copy-pasted). Don't skip the triage step; a raw
  jscpd report is a lead list, not a fix list.
- **Semantic reading (manual/agent-driven).** Catches everything the
  scanner is structurally blind to: the same business rule reimplemented
  with different variable names, reordered conditions, or split across
  files/languages. This is the more expensive but higher-yield approach for
  a genuinely thorough sweep, and the one most dedup passes skip because
  it doesn't have a single command to run. The action items below are how
  to do this systematically instead of an unstructured skim.

Run the token scanner first (cheap, fast, catches the obvious copy-paste),
then do the semantic read for what it structurally cannot see. A dedup pass
that only runs the scanner is a sample, not a sweep — the token-match tool
finds *duplicated text*, not *duplicated knowledge*, and most of the
duplication worth fixing in a mature codebase is the latter.

**Concrete action items for the semantic read, in order:**

1. **Dispatch read-only research agents per architectural surface area**, not
   one scan of the whole repo. Split by directory/module/domain (e.g. "every
   backend router," "the intake pages," "the auth dependency chain") so each
   agent reads every file in its slice end-to-end instead of skimming scanner
   hits. A single whole-repo pass misses cross-file business-rule duplication
   a scanner would never flag — different variable names and different
   control flow hiding the same underlying rule.
2. **Read the code's own comments for self-admissions.** Duplication is
   frequently already flagged by the developer who wrote it: "mirrors X's
   fix," "same shape as Y," "consistent with the other 3 hops." Grep for
   these cross-references — a strong, cheap signal pointing straight at a
   duplicate that was never consolidated.
3. **Verify skeptically before proposing any fix:**
   - Confirm the SAME rule, not similar-looking code for genuinely different
     concepts — a schema-level, safety-profile, or scope difference between
     two "duplicate-looking" functions can mean they must NOT be merged.
     Check class hierarchies, unique constraints, and transactional behavior
     directly; don't take a resemblance at face value.
   - Grep for an existing shared helper before proposing a new one.
   - Grep the test suite for `patch.object(<module>, "<name>", ...)` (or the
     language's equivalent mocking) on the exact functions about to move.
     Name resolution is lexical in most dynamic languages: moving a shared
     call into a new module silently defeats a test that patches the OLD
     module's namespace. This is the single most common way an
     ostensibly-safe extraction breaks a previously-green test.
4. **Fix in an isolated copy or with a revert-compare, never blind.** Prove
   the fix is behavior-preserving — run the affected tests before and after,
   or stash the change to diff pre/post behavior on the identical input.
   Never call a fix "safe" without having run something.
5. **When a duplicate-looking pair turns out to have irreconcilable
   differences** (different scope semantics, different safety guarantees,
   different concurrency model), say so explicitly, document WHY, and look
   for a smaller, independently-safe fix inside each copy instead of forcing
   a merge (e.g. the same missing validation bug existing in both copies,
   fixable in each without unifying the two implementations).
6. **A duplicate finding is not "done" until it's fixed or explicitly ruled
   out with a documented reason.** "Found it, moving on" with neither action
   is a report, not a deslop pass.

When asked for a genuinely thorough dedup sweep, the token scanner alone is
not sufficient — budget time for the subagent-driven, surface-by-surface
semantic read too.
