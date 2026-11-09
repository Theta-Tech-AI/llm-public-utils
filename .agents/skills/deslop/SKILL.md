---
name: deslop
description: "Library of 61 coding principles and 8 diagnostic patterns for finding and fixing slop: duplication, dead code, god files, over-abstraction, needless complexity. High-quality code has one owner per fact; parses input once at the boundary into types that cannot be illegal; small units with one job; dependencies pointing toward stability; written-down lifecycles; fails loud and tells the truth; a schema that enforces integrity; code a stranger can read; less of it. Why: changes stay one edit, bugs surface at their cause, audited code stays reviewable. Provides clean-code, architecture, reliability and data-layer principles, 9 reading lenses, coverage and scoped passes, measured campaigns, and a procedure to extend the library. Load for deslop passes, code or PR review, refactor planning, dedup, tech-debt triage, messy or copy-pasted code, simplification campaigns, or adding a principle."
---

# Deslop: code quality analysis
<sub><sup>Only this file loads when the skill activates; everything under `references/` is opened by path, so nothing here is paid for twice.</sup></sub>

`/deslop [file-or-directory]` (or `$deslop`; `/deslop my frontend code` works too) reads your code against a library of coding principles in [references/](references/) and suggests specific fixes with before/after examples. Read the principles yourself as well, as a human; you might learn something useful.

**Coverage pass by default.** Any target that is not a diff or PR (a file, directory, module, package, subsystem or whole repository) gets a **coverage pass**: one reading per principle group in [references/lenses.json](references/lenses.json) (all nine today), each reading its group's index and then every principle file in that group, in full. Only a diff or PR review, or an explicit request for a quick or narrow look, gets a **scoped pass**, and its report names the groups it did not read. The shape of each pass, the mechanism and the receipt are in [references/stages/recipes.md](references/stages/recipes.md). When the ask is a **campaign** ("massive simplification", "across the board", "minimum 30% LOC", "break up the god files", "get it all done, no excuses, present me a PR") follow [references/modes/campaign.md](references/modes/campaign.md) and measure with [references/library/measuring.md](references/library/measuring.md).

## What good code is, and why it matters

One idea under the library: **a reader can trust what the code appears to say.** Slop is any place that trust breaks: the truth lives in a second copy, a swallowed error, an unwritten assumption or a step whose side effect another step needs. Ten tenets, each with its lead principle and pattern files (the map below lists every one). Why the principles pay, and which lead for which kind of code: [what-the-principles-buy](references/library/what-the-principles-buy.md).

1. **One owner per fact.** Every fact is decided in one place and everything else derives from it. *Why:* a change is one edit instead of five, and copies cannot drift into disagreement.
   [dry](references/principles/architecture/dry.md), [single-source-of-truth](references/principles/architecture/single-source-of-truth.md), [one-logical-unit-one-home](references/principles/architecture/one-logical-unit-one-home.md); patterns: [one-fact-many-owners](references/patterns/one-fact-many-owners.md), [fork-instead-of-extension](references/patterns/fork-instead-of-extension.md)
2. **Parse at the boundary, decide once.** Turn external input into precise types at the edge; downstream code receives a decision, never raw material. *Why:* type-sniffing ladders, re-validation and compensating helpers disappear, and the bug class "the value was not what we assumed" goes with them.
   [parse-dont-validate](references/principles/architecture/parse-dont-validate.md), [decide-dont-cope](references/principles/clean-code/decide-dont-cope.md), [illegal-states-unrepresentable](references/principles/architecture/illegal-states-unrepresentable.md), [errors-at-the-boundary](references/principles/reliability/errors-at-the-boundary.md); patterns: [consumer-redecides-producer](references/patterns/consumer-redecides-producer.md), [grammar-without-owner](references/patterns/grammar-without-owner.md)
3. **Small units, one job, one reason to change.** Each module hides one design decision; each function does one thing at one level. *Why:* a change lands in one place, units are testable alone, and no one has to hold the whole system in their head.
   [separation-of-concerns](references/principles/architecture/separation-of-concerns.md), [modularity](references/principles/architecture/modularity.md), [orthogonality](references/principles/architecture/orthogonality.md), [small-functions](references/principles/clean-code/small-functions.md)
4. **Dependencies point toward stability, no reaching through.** What changes rarely is depended on; units are handed what they need and know only their neighbours. *Why:* a volatile edit cannot force work in stable code, and hidden agreements stop breaking the next caller.
   [dependency-stability](references/principles/architecture/dependency-stability.md), [layering-violations](references/principles/architecture/layering-violations.md), [law-of-demeter](references/principles/architecture/law-of-demeter.md), [implicit-coupling](references/principles/architecture/implicit-coupling.md)
5. **Write state machines and lifecycles down.** A status field has one place that says which moves are legal; values are immutable and operations safe to repeat. *Why:* races, double-applies and "how did it get into that state" incidents become impossible to write rather than hard to find.
   [implicit-state-machine](references/principles/architecture/implicit-state-machine.md), [immutability](references/principles/architecture/immutability.md), [idempotency](references/principles/architecture/idempotency.md); patterns: [one-sided-contract](references/patterns/one-sided-contract.md)
6. **Fail loud, tell the truth.** An error stops the work at its cause; absence is modelled, never replaced by a plausible default; a stated contract is read back. *Why:* silence means success only if failure cannot be silent; this is also what makes audited code reviewable.
   [fail-fast](references/principles/reliability/fail-fast.md), [no-silent-defaults](references/principles/reliability/no-silent-defaults.md), [design-by-contract](references/principles/reliability/design-by-contract.md), [observability](references/principles/reliability/observability.md); patterns: [absence-equals-failure](references/patterns/absence-equals-failure.md), [one-sided-contract](references/patterns/one-sided-contract.md)
7. **The schema enforces integrity.** Keys, references, closed vocabularies and invariants live in the database, with an access path for every query. *Why:* the data stays valid whatever the application does, and queries stay fast without folklore.
   [foreign-keys](references/principles/data-layer/foreign-keys.md), [invariant-constraints](references/principles/data-layer/invariant-constraints.md), [normalization](references/principles/data-layer/normalization.md), [join-access-paths](references/principles/data-layer/join-access-paths.md); patterns: [vocabulary-drift](references/patterns/vocabulary-drift.md)
8. **Say only what the code does.** A name, comment, route or config key never promises more than the body keeps; machinery with no claimant is removed. *Why:* readers trust what they read, so review is verification instead of reconstruction.
   [unclaimed-guarantee](references/principles/clean-code/unclaimed-guarantee.md), [self-documenting-code](references/principles/clean-code/self-documenting-code.md), [least-surprise](references/principles/clean-code/least-surprise.md); patterns: [declaration-vs-enforcement](references/patterns/declaration-vs-enforcement.md)
9. **Code a stranger can read.** Navigable entry points, honest names, flat control flow, low mental load; complexity metrics locate trouble but are never the target. *Why:* onboarding and review cost fall, and the order you read is the order that runs.
   [legibility](references/principles/clean-code/legibility.md), [cognitive-load](references/principles/clean-code/cognitive-load.md), [kiss](references/principles/clean-code/kiss.md)
10. **Delete before you add.** No feature for later, no special case without a missing mechanism, no patch over a decision; leave touched code better, and relax a rule when applying it makes worse code. *Why:* every line is a liability that must be read, tested and kept true, so the best change often removes lines.
   [yagni](references/principles/clean-code/yagni.md), [special-cases](references/principles/clean-code/special-cases.md), [patchwork](references/principles/clean-code/patchwork.md), [when-to-relax](references/readings/when-to-relax.md)

**What the library provides:** 61 principle files in four categories (clean code, architecture, reliability, data layer) and 8 cross-principle patterns; 9 reading lenses that partition the principles into stances; coverage and scoped passes with a planning, aggregation, consolidation and reporting protocol; campaigns with honest before/after measurement; and a procedure to extend the library with a researched principle ([extending-the-library](references/library/extending-the-library.md)). Open a principle file when a finding implicates it, and every file of a lens in a coverage pass.

## The library at a glance

<!-- principle-map:start -->
<!-- generated by scripts/skill_summary.py from the references' description lines; do not edit -->

**boundaries** — Where does this code belong, and does each part hold one concern? Judge seams, ownership and cohesion — not function size.

- [Separation of Concerns](references/principles/architecture/separation-of-concerns.md) — High cohesion, low coupling
- [Modularity](references/principles/architecture/modularity.md) — Deep modules, each hiding one design decision — and a hop that adds no policy is a shallow module, not a seam
- [One Logical Unit, One Home](references/principles/architecture/one-logical-unit-one-home.md) — one module per responsibility
- [Encapsulation](references/principles/architecture/encapsulation.md) — Tell, don't ask; hide state behind behavior
- [Orthogonality](references/principles/architecture/orthogonality.md) — unrelated things change independently
- [A State Machine Nobody Wrote Down](references/principles/architecture/implicit-state-machine.md) — a status field whose legal moves live only in scattered conditions; write the transitions down in one place

**duplication** — What knowledge exists more than once, and where is its single owner? Read duplication.md as well — the sweep primitives live there.

- [DRY: Don't Repeat Yourself](references/principles/architecture/dry.md) — One authoritative representation per piece of knowledge; fix at the 2nd occurrence
- [Single Source of Truth](references/principles/architecture/single-source-of-truth.md) — One authoritative location per datum; other copies derive from it
- [Code Reusability](references/principles/architecture/code-reusability.md) — Earn reuse from real callers; don't speculate on interfaces

**coupling** — What does each unit know about its neighbours, and what does it construct or reach through that it should have been handed?

- [Law of Demeter](references/principles/architecture/law-of-demeter.md) — talk only to immediate friends
- [Dependency Injection](references/principles/architecture/dependency-injection.md) — hand a unit what it needs instead of letting it construct or look it up
- [Composition Over Inheritance](references/principles/architecture/composition-over-inheritance.md) — has-a over is-a; assemble behaviour from small parts behind interfaces instead of inheriting it
- [SOLID Principles](references/principles/architecture/solid.md) — SRP, OCP, LSP, ISP, DIP; with the smell each one catches
- [Command-Query Separation](references/principles/architecture/command-query-separation.md) — Methods either do or answer, never both
- [Convention Over Configuration](references/principles/architecture/convention-over-configuration.md) — sensible defaults with escape hatches; configure only what departs from the convention
- [Implicit Coupling](references/principles/architecture/implicit-coupling.md) — two components agree on something the code never states
- [Layering Violations](references/principles/architecture/layering-violations.md) — a dependency against the intended arrows, invisible because no gate checks direction
- [Depend in the Direction of Stability](references/principles/architecture/dependency-stability.md) — a rarely-changing unit must not import an often-changing one

**parsing** — Where does an external value enter, and which single component turns it into a decision? Follow each input from the edge to every place that re-interprets it.

- [Parse, Don't Validate](references/principles/architecture/parse-dont-validate.md) — Convert input to precise types once at the boundary
- [A Helper That Must Exist Is an Architecture Finding](references/principles/architecture/helper-is-an-architecture-finding.md) — a function that reconciles a value with the shape the system expects means nothing owns that value's life
- [No Silent Defaults](references/principles/reliability/no-silent-defaults.md) — model absence, never synthesize a plausible value for it
- [Fail-Fast & Defensive Programming](references/principles/reliability/fail-fast.md) — Detect and report errors at the earliest possible moment
- [Postel's Law (Robustness Principle)](references/principles/reliability/postels-law.md) — Strict output, tolerant input; paranoid at security boundaries
- [Design by Contract](references/principles/reliability/design-by-contract.md) — Explicit preconditions, postconditions, invariants
- [Illegal States Unrepresentable](references/principles/architecture/illegal-states-unrepresentable.md) — a field valid only given another field's value makes every reader re-check a combination the domain forbids

**shape** — How big and how tangled is each unit's control flow? Depth, conditional chains, parameter lists, nesting — the measurable shape of the code.

- [Small Functions](references/principles/clean-code/small-functions.md) — short functions that do one thing (~15 lines); judged by the one job, not only the line count
- [Guard Clauses](references/principles/clean-code/guard-clauses.md) — Exit early on invalid states; keep the happy path flat
- [Cognitive Load](references/principles/clean-code/cognitive-load.md) — Minimize mental effort to read code; named intermediates over clever conditions
- [Cyclomatic Complexity](references/principles/clean-code/cyclomatic-complexity.md) — a testability metric, read as a locator, never optimized as a target
- [Single Level of Abstraction (SLAP)](references/principles/clean-code/slap.md) — Each function operates at one level of abstraction
- [KISS: Keep It Simple, Stupid](references/principles/clean-code/kiss.md) — Simplest sufficient code; watch parts plethora, over-abstraction, overengineering
- [YAGNI: You Aren't Gonna Need It](references/principles/clean-code/yagni.md) — Don't build functionality until it's required

**legibility** — Can a competent stranger read this without the author present? Naming, comment discipline, surprise, elegance, and code that copes where it should decide.

- [Self-Documenting Code](references/principles/clean-code/self-documenting-code.md) — Names and structure over comments; comments for why only
- [Documentation Discipline](references/principles/clean-code/documentation-discipline.md) — docs live next to what they describe; a comment earns its place by saying why, and stale prose is deleted
- [Elegance](references/principles/clean-code/elegance.md) — the least code that fully does the job and shows its intent; nothing to add, nothing left to remove
- [Legibility](references/principles/clean-code/legibility.md) — a navigable codebase where the path from entry point to effect is followable
- [Principle of Least Surprise](references/principles/clean-code/least-surprise.md) — a name, default or side effect behaves as a reader expects, so no one must read the body to be safe
- [Patchwork](references/principles/clean-code/patchwork.md) — compensating code you cannot simplify by deleting; find the decision it re-derives and re-state it
- [A Special Case Is a Requirement the Design Never Accounted For](references/principles/clean-code/special-cases.md) — a branch that exists for one situation is evidence of a missing mechanism, not the defect itself
- [Decide, Don't Cope](references/principles/clean-code/decide-dont-cope.md) — Decide types once at the boundary; delete downstream type-sniffing ladders

**guarantees** — What does this code promise, who claims the promise, and what happens when it is broken? State, lifetime, cancellation, privilege, and telling the truth when it fails.

- [An Unclaimed Guarantee](references/principles/clean-code/unclaimed-guarantee.md) — machinery promising a capability no caller claims, beside an owner that already covers it, is ceremony
- [Immutability](references/principles/architecture/immutability.md) — values fixed after creation; never mutate caller data
- [Idempotency](references/principles/architecture/idempotency.md) — repeating an operation changes nothing the second time
- [Observability & Transparency](references/principles/reliability/observability.md) — structured, correlated telemetry as the production debugger; a failure is understood from the logs alone
- [Resilience & Graceful Degradation](references/principles/reliability/resilience.md) — bounded retries, timeouts, fallbacks and circuit breakers for partial failure; never a retry that hides a bug
- [Principle of Least Privilege](references/principles/reliability/least-privilege.md) — minimum permissions per component, so a flaw has a small blast radius
- [Boy Scout Rule](references/principles/reliability/boy-scout-rule.md) — leave code better than you found it, scoped to what you touch; no drive-by rewrites
- [Errors at the Boundary](references/principles/reliability/errors-at-the-boundary.md) — validate where untrusted input enters, translate at each abstraction seam, decide where it can be acted on

**data-integrity** — What does the schema promise and enforce — keys, references, constraints, one home per fact?

- [Generate Identity and Order in the Database](references/principles/data-layer/database-identity.md) — IDENTITY/SEQUENCE + ON CONFLICT; never SELECT-then-INSERT
- [Let the Database Own Timestamps and Derived Values](references/principles/data-layer/database-timestamps.md) — DEFAULT now() plus a BEFORE UPDATE trigger
- [Constrain the Domain in the Schema](references/principles/data-layer/domain-constraints.md) — CHECK/ENUM/FK for closed vocabularies, NOT NULL, range checks
- [Foreign Keys Are Not Optional](references/principles/data-layer/foreign-keys.md) — Every reference column gets REFERENCES + an explicit ON DELETE
- [Enforce Invariants with Constraints, Not Application Code](references/principles/data-layer/invariant-constraints.md) — Rules live where writes happen, not where the app calls
- [Normalize to a Single Source of Truth](references/principles/data-layer/normalization.md) — Each fact lives in one column; the DB owns derivations
- [The Common Slop Tells](references/principles/data-layer/slop-tells.md) — grep-able schema smells, each mapped to the principle that owns it

**query-access-paths** — How does each query actually reach its rows — access paths, index shape, joins, and what defeats them?

- [Index What You Filter, Join, and Sort On](references/principles/data-layer/index-access-columns.md) — Index the queries the table actually serves
- [Know What Defeats an Index](references/principles/data-layer/index-defeaters.md) — Leading wildcards, functions on columns, type mismatches
- [Index Every Foreign Key](references/principles/data-layer/index-foreign-keys.md) — Postgres does not auto-index FKs
- [Match the Index to the Query Shape](references/principles/data-layer/index-query-shape.md) — Composite order, partial, covering, the right index type
- [Every Join Needs an Access Path on the Side Being Probed](references/principles/data-layer/join-access-paths.md) — an index on the driver's key is not enough, and the plan decides which side that is
- [Every Index Is Used or It's Dropped](references/principles/data-layer/unused-indexes.md) — An index no query uses is pure loss

**patterns** — recurring shapes that span principles; never charged by themselves, each instance is filed under the owning principle

- [One Fact, Many Owners](references/patterns/one-fact-many-owners.md) — two places decide the same thing and already disagree on an input *(read in: boundaries, duplication)*
- [Fork Instead of Extension](references/patterns/fork-instead-of-extension.md) — a downstream module copies an upstream one and edits it *(read in: duplication)*
- [Vocabulary Drift](references/patterns/vocabulary-drift.md) — one closed set of values spelled as literals in several layers, with the spellings or the set differing *(read in: coupling, data-integrity)*
- [Consumer Re-Decides the Producer](references/patterns/consumer-redecides-producer.md) — a client or later stage reconciles what the producer already decided *(read in: parsing)*
- [Grammar Without an Owner](references/patterns/grammar-without-owner.md) — one input format (an identifier, a config value) taken apart by several disagreeing parsers *(read in: parsing)*
- [Absence Equals Failure](references/patterns/absence-equals-failure.md) — one value answers both "nothing there" and "the read failed"; make them two values and let the caller choose *(read in: parsing, guarantees)*
- [One-Sided Contract](references/patterns/one-sided-contract.md) — one end of an agreement exists without the other *(read in: parsing, guarantees)*
- [Declaration vs Enforcement](references/patterns/declaration-vs-enforcement.md) — a name, docstring, route or config key promises what the body never does *(read in: legibility, guarantees)*

<!-- principle-map:end -->

## Where to read what


One row per file, in the order a pass meets them. Every markdown in this skill is reachable from this table or from the indexes, and CI fails if one is not.

| File | When |
|------|------|
| [references/readings/auditing.md](references/readings/auditing.md) | **Always** — the audit itself: persona, the mode question, the autonomy rule, report format, and the **input census** (per external input: who owns turning it into a decision, how many places re-interpret it; zero owners or several is a finding, reported even when it ranks last) |
| [references/readings/when-to-relax.md](references/readings/when-to-relax.md) | **With every reading** — the guardrail: contexts where a principle is over-applied, and the meta-principle that says a violation worth "fixing" into worse code is not a violation |
| [references/patterns.md](references/patterns.md) | **In each reading, for the patterns of its lens** (`lenses.json`), after the principles; **at consolidation** as the axis that themes cross concerns. A *pattern* is a recurring diagnostic shape, never charged by itself; a *principle* is one mechanism with one owner |
| [references/stages/recipes.md](references/stages/recipes.md) | **At the start of any pass** — the shapes of a pass: the **coverage pass** (the default for any target that is not a diff), the scoped pass (a diff, PR, or an explicit quick look), directed cell, campaign, library extension, second round. Pick the shape before the readings |
| [references/stages/planning.md](references/stages/planning.md) | **Before every coverage pass** (the default) — or after a pass that missed something: survey, slice, group the principles, write the permutation list, rank it against a budget, choose the execution mechanism you actually have |
| [references/stages/aggregation.md](references/stages/aggregation.md) | **The moment more than one reading has reported** — merge on locus + principle into corroborated / single / disputed, account for coverage, and mark a cell that quotes nothing as a failed reading |
| [references/stages/consolidation.md](references/stages/consolidation.md) | **After aggregation, before anything is reported or filed** — verify, apply the guardrail, bucket into now / next / wait-or-drop, collapse findings into concerns, group into a milestone |
| [references/stages/reporting.md](references/stages/reporting.md) | **Immediately before you speak to the person who asked** — lead with the answer, bucket the work, keep it short, and never bury the result in method |
| [references/modes/campaign.md](references/modes/campaign.md) | **Whole-codebase campaigns** — "massive simplification", "across the board", "minimum 30% LOC", "get it all done", "present me a PR". The five sweeps, the target discipline, running it at scale, and the delivery protocol |
| [references/modes/loop-until-dry.md](references/modes/loop-until-dry.md) | Thorough passes ("keep going") — iterate until a full scan finds nothing actionable |
| [references/library/evaluation.md](references/library/evaluation.md) | **Before claiming a pass proved anything**, and after any control run — the recorded controls, their numbers, and how to add one |
| [references/library/measuring.md](references/library/measuring.md) | **Any pass that will claim a number** — the four measurement harnesses, the unbiased task corpus, the metrics that carry the story (nesting depth, `elif` chains, cyclomatic complexity), and the honest before/after reporting skeleton |
| [references/library/what-the-principles-buy.md](references/library/what-the-principles-buy.md) | **Explaining why a pass is worth doing, choosing which principles lead for a kind of code, or briefing parallel fixers** — families of broken trust, the bug class each predicts, honest costs, a plain worker brief |
| [references/library/extending-the-library.md](references/library/extending-the-library.md) | **Adding a principle** — the ask is a *gap* in the library, not a pass over code: discovery against every existing principle, research, the house draft format, both indexes, and the publish path |
| [references/library/detecting-slop.md](references/library/detecting-slop.md) | Building or questioning a detector — what the tools cannot see, and the control a detector script must pass to earn its lines |
| [references/principles/data-layer.md](references/principles/data-layer.md) | The target has a database (schema, SQL, migrations, keys, constraints, **indexes and join access paths beside the queries that use them**). Treat the schema as a slice of its own: it usually sits outside the audited directory, and no index finding is provable from the DDL alone |
| [references/readings/duplication.md](references/readings/duplication.md) | Running a dedup sweep — hunting duplication beyond token scanners: the primitives to grep for, the field-overlap recipe for one entity described many times, and the shape-clone scripts in [scripts/](scripts/) |
| [references/library/case-study-simplification-agent-fleet.md](references/library/case-study-simplification-agent-fleet.md) | Worked KISS example — a real pass that collapsed an LLM agent fleet into one agent |
| [references/library/further-reading.md](references/library/further-reading.md) | Background bibliography and concept attribution (not needed mid-audit) |
| [references/lenses.json](references/lenses.json) | Grouping the principles for a planned pass — the default partition of 61 principle files into 9 reading stances (validated by `scripts/swarm_lenses.py --check`); regroup it if the codebase asks for different stances |

## Layout and checks

`references/` is a taxonomy by **role in the pass**, not by topic: `stages/` (planning, aggregation, consolidation, reporting; read at their moment), `readings/` (what a single reading carries; `auditing` and `when-to-relax` in every reading), `modes/` (campaign, loop-until-dry), `principles/` (`<category>.md` is the index to read first, `<category>/<slug>.md` one principle), `patterns/` (the index, then one file per pattern, after a lens's principles and all of them at consolidation), `library/` (opened on request). Category indexes: [clean-code](references/principles/clean-code.md), [architecture](references/principles/architecture.md), [reliability](references/principles/reliability.md), [data-layer](references/principles/data-layer.md).

**This file is the manifest.** No harness builds one, so a reference nothing here leads to (directly, or through an index that does) is a file nobody opens. CI runs these on every push and pull request (`.github/workflows/skill-checks.yml`):

```bash
python3 scripts/check_reachability.py     # every markdown reachable by following links from this file
python3 scripts/swarm_lenses.py --check   # every principle in exactly one group; no unclassified markdown
python3 scripts/skill_summary.py --check  # the map above matches the references; description within 1024 characters; links resolve
python3 -m py_compile scripts/*.py        # the instruments still load
```

Edit a principle's or pattern's `description:` line and run `python3 scripts/skill_summary.py` to regenerate the map. Moving a file between roles is `scripts/taxonomy_move.py`, which rewrites every cross-link.

## Plan the pass before you audit

**A pass is planned, not merely started.** Slop is found when a reader looks at a specific piece of code with a specific set of principles in mind, so the unit of work is a **cell**: one group of principles × one slice of code × one reading, merged with the others afterwards. Survey the shape, design the slices (modules, role archetypes, cross-folder concept clusters, the schema and its queries, flows, a diff), group the principles into stances, write the permutation list, rank it under a budget, rotate the rounds so a second pass is the complement of the first, and choose the execution mechanism you have: subagents, a harness fan-out, model tiers, or this context one cell at a time. Protocol: [planning](references/stages/planning.md); a coverage pass emits every group, one reading each ([recipes](references/stages/recipes.md)). The bookkeeping is scripted:

```bash
python3 scripts/swarm_lenses.py --emit /tmp/cells --repo <root> --target <dir>        # every group, one prompt each
python3 scripts/swarm_plan.py --repo <root> --target <dir> --out /tmp/plan --budget 24 [--ledger <jsonl> --round N]   # slice choice and rounds
```

For a **specific ask** (*"look at separation of concerns in the provider adapters"*) skip the plan and read one cell: emit the `boundaries` group against that module, or open those principle files and read the module whole. A general pass cannot satisfy that request, because it decides for itself what to open.

## Aggregate, consolidate, then report

A pass finds more than anyone should act on at once. After the readings: [aggregation](references/stages/aggregation.md) (merge on locus + principle; a cell that quotes nothing is a *failed reading*), [consolidation](references/stages/consolidation.md) (verify at the source line, apply the guardrail, bucket now / next / wait-or-drop, one issue per concern), [reporting](references/stages/reporting.md) (the answer first, the short fix-first list, what was left out with the coverage receipt, then stop).

## Scope bounds the code, not the principles

A coverage pass gives every group its reading over the target. A scoped pass still gets one or two assigned groups, chosen by what the code is ([recipes](references/stages/recipes.md)), because reading the indexes and opening a principle only when a finding "implicates" it leaves Separation of Concerns unopened forever: a pass can only open a principle it has already suspected, and the ones that need a boundary held in mind are routinely never read. Index-only reconnaissance is a legitimate mode, but name it as one and never let it be the default.

---

*Run `/deslop [file-or-directory]` to analyze your code against these principles and let the agent fix any slop it detects.*
