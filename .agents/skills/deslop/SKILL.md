---
name: deslop
description: "Library of 61 coding principles and 9 diagnostic patterns for finding and fixing slop: duplication, dead code, god files, over-abstraction, needless complexity. High-quality code has one owner per fact; parses input once at the boundary into types that cannot be illegal; small units with one job; dependencies pointing toward stability; written-down lifecycles; fails loud and tells the truth; a schema that enforces integrity; code a stranger can read; less of it. Why: changes stay one edit, bugs surface at their cause, audited code stays reviewable. Provides clean-code, architecture, reliability and data-layer principles, 9 reading lenses, coverage and scoped passes, measured campaigns, and a procedure to extend the library. Load for deslop passes, code or PR review, refactor planning, dedup, tech-debt triage, messy or copy-pasted code, simplification campaigns, or adding a principle."
---

# Deslop: code quality analysis

`/deslop [file-or-directory]` (or `$deslop`;) reads your code against a library of coding principles in [references/](references/) and suggests specific fixes with before/after examples.

**Coverage pass by default.** Any target that is not a diff or PR (a file, directory, module, package, subsystem or whole repository) gets a **coverage pass**: one reading per principle group in [references/lenses.json](references/lenses.json) (all nine today), each reading its group's index and then every principle file in that group, in full. Only a diff or PR review, or an explicit request for a quick or narrow look, gets a **scoped pass**, and its report names the groups it did not read. Pass shapes: [references/stages/recipes.md](references/stages/recipes.md). When the ask is a **campaign** ("massive simplification", "across the board", "minimum 30% LOC", "break up the god files", "get it all done, no excuses, present me a PR") follow [references/modes/campaign.md](references/modes/campaign.md) and measure with [references/library/measuring.md](references/library/measuring.md).

## What good code is, and why it matters

One idea under the library: **a reader can trust what the code appears to say.** Slop is any place that trust breaks: the truth lives in a second copy, a swallowed error or an unwritten assumption. Ten tenets, each with its lead files. Why the principles pay, and which lead for which kind of code: [what-the-principles-buy](references/library/what-the-principles-buy.md).

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

**What the library provides:** 61 principles in four categories (clean code, architecture, reliability, data layer), 9 cross-principle patterns, 9 reading lenses, coverage and scoped passes with planning, aggregation, consolidation and reporting stages, campaigns with honest before/after measurement, and a procedure to [extend the library](references/library/extending-the-library.md).

## The library at a glance

<!-- principle-map:start -->
<!-- generated by scripts/skill_summary.py; do not edit -->

**boundaries** — Where does this code belong, and does each part hold one concern? Judge seams, ownership and cohesion — not function size.

- Separation of Concerns — High cohesion, low coupling
- Modularity — Deep modules, each hiding one design decision
- One Logical Unit, One Home — one module per responsibility
- Encapsulation — Tell, don't ask; hide state behind behavior
- Orthogonality — unrelated things change independently
- A State Machine Nobody Wrote Down — a status field whose legal moves live only in scattered conditions

**duplication** — What knowledge exists more than once, and where is its single owner? Read duplication.md as well — the sweep primitives live there.

- DRY: Don't Repeat Yourself — One authoritative representation per piece of knowledge
- Single Source of Truth — One authoritative location per datum; other copies derive from it
- Code Reusability — Earn reuse from real callers; don't speculate on interfaces

**coupling** — What does each unit know about its neighbours, and what does it construct or reach through that it should have been handed?

- Law of Demeter — talk only to immediate friends
- Dependency Injection — hand a unit what it needs instead of letting it construct or look it…
- Composition Over Inheritance — has-a over is-a; assemble behaviour from small parts behind…
- SOLID Principles — SRP, OCP, LSP, ISP, DIP; with the smell each one catches
- Command-Query Separation — Methods either do or answer, never both
- Convention Over Configuration — sensible defaults with escape hatches
- Implicit Coupling — two components agree on something the code never states
- Layering Violations — a dependency against the intended arrows
- Depend in the Direction of Stability — a rarely-changing unit must not import an often-changing one

**parsing** — Where does an external value enter, and which single component turns it into a decision? Follow each input from the edge to every place that re-interprets it.

- Parse, Don't Validate — Convert input to precise types once at the boundary
- A Helper That Must Exist Is an Architecture Finding — a function that reconciles a value with the shape the system expects…
- No Silent Defaults — model absence, never synthesize a plausible value for it
- Fail-Fast & Defensive Programming — Detect and report errors at the earliest possible moment
- Postel's Law (Robustness Principle) — Strict output, tolerant input; paranoid at security boundaries
- Design by Contract — Explicit preconditions, postconditions, invariants
- Illegal States Unrepresentable — a field valid only given another field's value makes every reader…

**shape** — How big and how tangled is each unit's control flow? Depth, conditional chains, parameter lists, nesting — the measurable shape of the code.

- Small Functions — short functions that do one thing (~15 lines)
- Guard Clauses — Exit early on invalid states; keep the happy path flat
- Cognitive Load — Minimize mental effort to read code
- Cyclomatic Complexity — a testability metric, read as a locator, never optimized as a target
- Single Level of Abstraction (SLAP) — Each function operates at one level of abstraction
- KISS: Keep It Simple, Stupid — Simplest sufficient code
- YAGNI: You Aren't Gonna Need It — Don't build functionality until it's required

**legibility** — Can a competent stranger read this without the author present? Naming, comment discipline, surprise, elegance, and code that copes where it should decide.

- Self-Documenting Code — Names and structure over comments; comments for why only
- Documentation Discipline — docs live next to what they describe
- Elegance — the least code that fully does the job and shows its intent
- Legibility — a navigable codebase where the path from entry point to effect is…
- Principle of Least Surprise — a name, default or side effect behaves as a reader expects, so no one…
- Patchwork — compensating code you cannot simplify by deleting
- A Special Case Is a Requirement the Design Never Accounted For — a branch that exists for one situation is evidence of a missing…
- Decide, Don't Cope — Decide types once at the boundary

**guarantees** — What does this code promise, who claims the promise, and what happens when it is broken? State, lifetime, cancellation, privilege, and telling the truth when it fails.

- An Unclaimed Guarantee — machinery promising a capability no caller claims
- Immutability — values fixed after creation; never mutate caller data
- Idempotency — repeating an operation changes nothing the second time
- Observability & Transparency — structured, correlated telemetry as the production debugger
- Resilience & Graceful Degradation — bounded retries, timeouts, fallbacks and circuit breakers for partial…
- Principle of Least Privilege — minimum permissions per component, so a flaw has a small blast radius
- Boy Scout Rule — leave code better than you found it, scoped to what you touch
- Errors at the Boundary — validate where untrusted input enters

**data-integrity** — What does the schema promise and enforce — keys, references, constraints, one home per fact?

- Generate Identity and Order in the Database — IDENTITY/SEQUENCE + ON CONFLICT; never SELECT-then-INSERT
- Let the Database Own Timestamps and Derived Values — DEFAULT now() plus a BEFORE UPDATE trigger
- Constrain the Domain in the Schema — CHECK/ENUM/FK for closed vocabularies, NOT NULL, range checks
- Foreign Keys Are Not Optional — Every reference column gets REFERENCES + an explicit ON DELETE
- Enforce Invariants with Constraints, Not Application Code — Rules live where writes happen, not where the app calls
- Normalize to a Single Source of Truth — Each fact lives in one column; the DB owns derivations
- The Common Slop Tells — grep-able schema smells, each mapped to the principle that owns it

**query-access-paths** — How does each query actually reach its rows — access paths, index shape, joins, and what defeats them?

- Index What You Filter, Join, and Sort On — Index the queries the table actually serves
- Know What Defeats an Index — Leading wildcards, functions on columns, type mismatches
- Index Every Foreign Key — Postgres does not auto-index FKs
- Match the Index to the Query Shape — Composite order, partial, covering, the right index type
- Every Join Needs an Access Path on the Side Being Probed — an index on the driver's key is not enough
- Every Index Is Used or It's Dropped — An index no query uses is pure loss

**patterns** — recurring shapes that span principles; never charged by themselves, each instance is filed under the owning principle

- One Fact, Many Owners — two places decide the same thing and already disagree on an input *(boundaries, duplication)*
- Fork Instead of Extension — a downstream module copies an upstream one and edits it *(duplication)*
- Unnamed Decision — a question never asked, answered per site *(duplication, parsing)*
- Vocabulary Drift — one closed set of values spelled as literals in several layers *(coupling, data-integrity)*
- Consumer Re-Decides the Producer — a client or later stage reconciles what the producer already decided *(parsing)*
- Grammar Without an Owner — one input format (an identifier, a config value) taken apart by… *(parsing)*
- Absence Equals Failure — one value answers both "nothing there" and "the read failed" *(parsing, guarantees)*
- One-Sided Contract — one end of an agreement exists without the other *(parsing, guarantees)*
- Declaration vs Enforcement — a name, docstring, route or config key promises what the body never… *(legibility, guarantees)*

<!-- principle-map:end -->

## Where to read what


One row per file, in the order a pass meets them. CI fails on a markdown that no row here and no index links.

| File | When |
|------|------|
| [references/readings/auditing.md](references/readings/auditing.md) | **Always** — the audit itself: persona, the mode question, the autonomy rule, report format, and the **input census** (per external input: who owns turning it into a decision, how many places re-interpret it; zero owners or several is a finding, reported even when it ranks last) |
| [references/readings/when-to-relax.md](references/readings/when-to-relax.md) | **With every reading** — the guardrail: where a principle is over-applied; a violation worth "fixing" into worse code is not a violation |
| [references/patterns.md](references/patterns.md) | **In each reading, for the patterns of its lens** (`lenses.json`), after the principles; **at consolidation** as the axis that themes cross concerns. A *pattern* is a recurring diagnostic shape, never charged by itself; a *principle* is one mechanism with one owner |
| [references/stages/recipes.md](references/stages/recipes.md) | **At the start of any pass** — the shapes: **coverage pass** (default for any non-diff target), scoped pass (diff, PR, quick look), directed cell, campaign, library extension, second round |
| [references/stages/planning.md](references/stages/planning.md) | **Before every coverage pass**, or after one that missed something: survey, slice, group, rank against a budget, choose the mechanism |
| [references/stages/aggregation.md](references/stages/aggregation.md) | **When more than one reading has reported** — merge on locus + principle (corroborated / single / disputed); a cell quoting nothing failed |
| [references/stages/consolidation.md](references/stages/consolidation.md) | **After aggregation, before reporting or filing** — verify, apply the guardrail, bucket now / next / wait-or-drop, one issue per concern |
| [references/stages/reporting.md](references/stages/reporting.md) | **Just before you speak to the asker** — answer first, bucketed work, short |
| [references/modes/campaign.md](references/modes/campaign.md) | **Whole-codebase campaigns** ("massive simplification", "minimum 30% LOC", "present me a PR") — five sweeps, target discipline, scale, delivery |
| [references/modes/loop-until-dry.md](references/modes/loop-until-dry.md) | Thorough passes ("keep going") — iterate until a full scan finds nothing actionable |
| [references/library/evaluation.md](references/library/evaluation.md) | **Before claiming a pass proved anything**, and after any control run — the recorded controls, their numbers, and how to add one |
| [references/library/measuring.md](references/library/measuring.md) | **Any pass that will claim a number** — the harnesses, the unbiased task corpus, the metrics that carry the story, the honest before/after skeleton |
| [references/library/what-the-principles-buy.md](references/library/what-the-principles-buy.md) | **Explaining why a pass is worth doing, choosing which principles lead for a kind of code, or briefing parallel fixers** — families of broken trust, the bug class each predicts, honest costs, a plain worker brief |
| [references/library/extending-the-library.md](references/library/extending-the-library.md) | **Adding a principle** (a *gap*, not a pass over code) — discovery against existing principles, research, house format, both indexes, publish path |
| [references/library/detecting-slop.md](references/library/detecting-slop.md) | Building or questioning a detector — what the tools cannot see, and the control a detector script must pass to earn its lines |
| [references/principles/data-layer.md](references/principles/data-layer.md) | The target has a database (schema, SQL, migrations, keys, constraints, **indexes and join access paths beside the queries that use them**). Treat the schema as a slice of its own: it usually sits outside the audited directory, and no index finding is provable from the DDL alone |
| [references/readings/duplication.md](references/readings/duplication.md) | Running a dedup sweep — hunting duplication beyond token scanners: the primitives to grep for, the field-overlap recipe for one entity described many times, and the shape-clone scripts in [scripts/](scripts/) |
| [references/library/case-study-simplification-agent-fleet.md](references/library/case-study-simplification-agent-fleet.md) | Worked KISS example — a real pass that collapsed an LLM agent fleet into one agent |
| [references/library/further-reading.md](references/library/further-reading.md) | Background bibliography and concept attribution (not needed mid-audit) |
| [references/lenses.json](references/lenses.json) | The default partition of 61 principles into 9 reading stances ; regroup it for different stances |

## Layout and checks

`references/` is organised by **role in the pass**: `stages/` (read at their moment), `readings/` (`auditing` and `when-to-relax` in every reading), `modes/`, `principles/` (`<category>.md` index first, then `<category>/<slug>.md`), `patterns/` (index, then one file each), `library/` (on request). Principle files are linked from their category index: [clean-code](references/principles/clean-code.md), [architecture](references/principles/architecture.md), [reliability](references/principles/reliability.md), [data-layer](references/principles/data-layer.md).

**This file is the manifest**: a reference nothing here leads to is a file nobody opens. CI checks every push and pull request:

```bash
python3 scripts/check_reachability.py     # every markdown reachable by links from this file
python3 scripts/swarm_lenses.py --check   # every principle in exactly one group
python3 scripts/skill_summary.py --check  # map matches the references; description <= 1024 chars; links resolve; size <= 24 KB
python3 -m py_compile scripts/*.py
```

Edit a `description:` line, then run `python3 scripts/skill_summary.py` to regenerate the map. The library is code too: [deslop it](references/library/extending-the-library.md#the-library-is-code-too-deslop-it). Moving files: `scripts/taxonomy_move.py`.

## Plan the pass before you audit

**A pass is planned.** The unit of work is a **cell**: one group of principles × one slice of code × one reading, merged afterwards. Survey the shape, design the slices (modules, role archetypes, concept clusters, the schema and its queries, flows, a diff), rank the permutations under a budget, rotate rounds so a second pass is the complement of the first, and choose the mechanism you have (subagents, a harness fan-out, or this context one cell at a time): [planning](references/stages/planning.md), [recipes](references/stages/recipes.md). Scripted:

```bash
python3 scripts/swarm_lenses.py --emit /tmp/cells --repo <root> --target <dir>        # every group, one prompt each
python3 scripts/swarm_plan.py --repo <root> --target <dir> --out /tmp/plan --budget 24 [--ledger <jsonl> --round N]
```

For a **specific ask** (*"look at separation of concerns in the provider adapters"*) skip the plan and read one cell: emit that group against that module, or open its principle files and read the module whole.

## Scope bounds the code, not the principles

A scoped pass still gets one or two assigned groups, chosen by what the code is ([recipes](references/stages/recipes.md)): a pass opens only principles it already suspects, so those needing a boundary held in mind (Separation of Concerns) go unread forever. Index-only reconnaissance is a legitimate mode; name it, never default to it. After the readings: [aggregation](references/stages/aggregation.md), [consolidation](references/stages/consolidation.md), [reporting](references/stages/reporting.md).
