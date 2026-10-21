---
name: deslop-pass-planning
description: Plan a deslop pass — survey the code, design slices, group the principles, write the permutation list, then rank and order the cells against a budget.
---

# Planning a pass: cells, grouping, order

This file is about how to **think about a deslop pass before running one**. It ends where the readings begin;
aggregation, consolidation and reporting are separate references (§11), so planning does not carry context it has
not earned yet. It states principles and leaves the mechanism to you: you may have subagents, a harness with its
own fan-out, one context, or a fleet of cheaper models. None of that is the point. The point is that slop is
found by **looking at a specific piece of code with a specific set of principles in mind**, and by **aggregating
several such readings** — and a pass that does neither finds remarkably little.

[auditing.md](auditing.md) governs the audit itself. This file governs the shape of the pass around it.

## 1. The principle: cells, not surveys

A pass told "audit this directory" reads the indexes, decides what *looks* implicated, and reports. The blind
spot in that approach is structural, and it is not diligence: **it can only open the principle file it has
already suspected.** Principles whose names are visible triggers get opened — a 300-line function summons Small
Functions. Principles that require holding a boundary in mind do not. Separation of Concerns is one index row
reading *high cohesion, low coupling*; a reader looking at a working provider adapter sees a working adapter.

Measured on a real directory: several monolithic neutral passes reported behaviour defects, an unowned setting
and a duplicated retry policy — and not one separation-of-concerns finding. Directed to that principle alone, an
agent found several in the same directory in one pass. The principle was never weak. It was **never read.**

So the unit of work is a **cell**:

> one group of principles × one slice of the code × one reading, reported in that group's terms.

A cell is small enough that the reader can hold its principles and its code at once, which is the condition
under which findings are actually made. A pass is a set of cells whose reports are merged afterwards. Whether
those cells run one after another in your own context, in parallel subagents, or across a fleet of cheaper
models is an execution choice (§7). The decomposition is not.

## 2. Survey before you slice

You cannot slice code you have not looked at, and the slices that matter are rarely the directory tree. Survey
first — cheaply, read-only — and write down what you learn:

- **Shape:** the top-level units, how big they are, which files are the monsters, where the entry points are
  (CLI, HTTP, daemon, scheduled job, library surface).
- **Layers and seams:** where requests, events or commands enter; where persistence lives; where the outside
  world is reached (providers, SDKs, network, filesystem, clocks). Boundary defects live at these seams.
- **Cross-cutting concerns:** every place configuration is read, every retry, every logger, every serializer,
  every error translation. These live in no single directory, which is why a directory walk misses them.
- **The database, if there is one:** where the DDL lives (migrations, `schema.sql`, ORM models, alembic
  versions) and where the queries are written. Both halves are needed: the schema says what was built, the call
  sites say what is actually reached, and neither proves "missing index" or "unused index" alone. The schema is
  usually **outside** the directory being audited, which is why it is missed when the target is an application
  folder.
- **Roles:** which directories play a role — adapters, handlers, workers, schedulers, repositories, migrations.
  A role predicts the defects it characteristically carries.
- **History, where available:** churn and fix density. A file that changes constantly and looks tidy is a
  candidate; one nobody has touched in two years usually is not.
- **Existing findings:** open issues, prior audit reports, TODOs, and what the people who work in this code
  complain about. Your pass should not be their first reporter.

The output is a **short written note**: the units, the seams, the concepts, the roles, and the two or three
places you now suspect. A pass that skips this step is guessing at its own scope.

## 3. Design the slices

A slice is a place where **one kind of decision is made** — small enough to read whole, coherent enough that a
principle applies to all of it. Useful families, roughly in order of how often they pay:

| Family | What it is | Why it pays |
|---|---|---|
| **Schema and indexes** | the DDL (migrations, `schema.sql`, ORM models) **plus** the query call sites that must use it | integrity is a property of the schema (foreign keys, normalization, constraints) and index work is a property of the pair: an index nothing queries is waste, a query with no index is a cliff — neither is visible from one side |
| **Concept cluster** | every file touching one concern, across the tree — config reading, retries, serialization, providers, auth, logging, error translation | the defect is usually that one concern was solved twice in two places, which no single directory shows |
| **Module** | one directory or package | enough context to judge cohesion and coupling inside a boundary |
| **Role archetype** | a module read as the role it plays — adapter, handler, worker, scheduler, repository, migration | roles have signature defects: an adapter parses and reaches, a writer forgets idempotency, a repo re-derives a schema |
| **Flow** | one path end to end: request → handler → service → persistence → response | shows where a value is re-interpreted at every hop, including hops in different directories |
| **Contract surface** | every caller of one function, interface or endpoint | exposes wrappers that exist only to cope, and call sites that duplicate a decision |
| **Diff / change set** | what a PR or the last N commits touched | the pragmatic slice for review rather than audit |

A target that has a database always earns a `data-layer` cell over the schema — even when the schema lives
outside the named target. If it does not, the pass has silently excluded the most expensive place to be wrong.

Invent the slices the code asks for; the table is a palette, not a taxonomy. Two rules: a slice must be
**nameable in one sentence** ("every place a retry delay is decided"), and a slice that is **one file is fine** —
the largest files are often the richest cells, because the defect is that four concerns share one home.

## 4. Group the principles

The principle files are the other half of the permutation, and grouping them is a real decision. A good group is
a **reading stance**: the principles whose findings you would have to weigh against each other while reading the
same code. Boundary ownership belongs with Modularity and One Logical Unit One Home; boundary parsing belongs
with A Helper That Must Exist and No Silent Defaults; shape with KISS and Guard Clauses; guarantees (state,
lifetime, cancellation, privilege) together; the data layer together.

The library ships a default grouping in [lenses.json](lenses.json) — eight groups over 53 principle files — and
you may regroup it. Two constraints:

- **Related principles must sit together.** Splitting DRY from Single Source of Truth, or Parse Don't Validate
  from A Helper That Must Exist, produces two reports of one defect under two names, and the aggregation step
  will mistake a double-charge for corroboration.
- **Every principle file belongs to exactly one group.** A principle in no group is a principle no reading
  covers; a principle in two groups is paid for twice. Both failures are silent. If your harness can run
  `scripts/swarm_lenses.py --check` it will prove the partition; if not, do the list comparison by hand once and
  trust it thereafter.

**No markdown left behind.** Assignment is not enough for the files that are not principles, so the same check
audits *reachability* of every markdown in the library. Each file must sit in exactly one enforced class:

| Class | How it is reached | When |
|---|---|---|
| **principle** | one group's reading list, read in full | every reading |
| **category index** | read **first** by the groups it governs — it carries the stance and the tells that show a reader what a violation looks like | before the principle files |
| **lens protocol** | `auditing.md` and `when-to-relax.md` in every reading; a situational protocol such as `duplication.md` in the group that needs it | with the lens |
| **stage reference** | an explicit trigger — "read this when reports arrive", "read this before you speak" | at its stage |
| **situational** | on request, e.g. a worked example or the bibliography | never assumed |

An index file is **not** a substitute for the principle files (it carries one-line essences; a finding needs the
full text), and a principle file is not a substitute for the index (the index is what tells a reader what a
violated boundary even looks like). Read both, index first. `--check` fails on any file reachable by none of these
paths and prints the tally — on this library: `72/72 files reachable — lens 54, lens-index 4, lens-protocol 3,
situational 2, stage 9`.

That is a guarantee of **reachability**, not of reading. No harness can prove an agent opened a file, but a
reading can be made to *declare* what it opened: every cell writes `files-read-<cell>.txt` beside its findings,
and the aggregation stage diffs that manifest against the assignment the cell was given (§8). A missing line is a
failed reading — the only check the protocol has against an agent claiming a lens it skimmed.

The shipped groups, for reference — each is one way of looking, not a folder:

| Group | Principles | The question it holds |
|---|---|---|
| `boundaries` | Separation of Concerns, Modularity, One Logical Unit One Home, Encapsulation, Orthogonality | Where does this code belong, and does each part hold one concern? |
| `duplication` | DRY, Single Source of Truth, Code Reusability | What knowledge exists more than once, and where is its single owner? |
| `coupling` | Law of Demeter, DI, Composition Over Inheritance, SOLID, CQS, Convention Over Configuration | What does each unit know about, or construct, that it should have been handed? |
| `parsing` | Parse Don't Validate, A Helper That Must Exist Is an Architecture Finding, No Silent Defaults, Fail-Fast, Postel's Law, Design by Contract | Where does external input enter, and which single component turns it into a decision? |
| `shape` | Small Functions, Guard Clauses, Cognitive Load, Cyclomatic Complexity, SLAP, KISS, YAGNI | How big and how tangled is each unit's control flow? |
| `legibility` | Self-Documenting Code, Documentation Discipline, Elegance, Legibility, Least Surprise, Patchwork, Decide Don't Cope | Can a competent stranger read this without the author present? |
| `guarantees` | An Unclaimed Guarantee, Immutability, Idempotency, Observability, Resilience, Least Privilege, Boy Scout Rule | What is promised, who claims the promise, what happens when it breaks? |
| `data-layer` | the thirteen database principles | What does the schema promise, where is an invariant only in application code, and what access path does each query actually have? |

Every group also carries [auditing.md](auditing.md) (report format and the input census) and
[when-to-relax.md](when-to-relax.md) as its guardrail.

## 5. Write the permutation list

Now the cross-product, **written down rather than run**: slices × groups. (Ordering the *cells* happens here; triaging the *findings* that come back is a later stage — §11.) It is far too large to execute, and
that is the point — writing it makes the choice explicit and stops the pass from quietly becoming "one reading,
one directory, whatever it noticed".

For each cell record: the group, the slice, **the evidence** that put it there, the expected yield, the cost, and
— the part people skip — **what would make it worth running**. A cell justified by a directory name is a guess;
a cell justified by "eleven files read `os.environ`, across five layers" is a finding waiting to be written.

## 6. Order the cells against a budget

Ordering is where a plan becomes a pass. Sort on these, in this order:

1. **Evidence strength** — observed signal (config reads, async/retry/locks, SQL, duplicate symbols) beats a role
   inferred from a path name, which beats a hunch.
2. **Blast radius** — what breaks if this slop is real. A boundary defect on an authentication path outranks a
   naming complaint in a script, however obvious the naming.
3. **Prior misses** — a group that came back empty before, or that someone had to point at by hand, runs early.
   The miss is evidence about the reading, not about the code.
4. **Verification cost** — can a finding be confirmed by reading a call site, or does it need a harness? Early
   cells should be cheap to confirm, so the first wave produces findings you can prove.
5. **Redundancy** — two cells of the **same group** over the same files is waste; two *different* groups over the
   same files is the whole idea. Never penalise cross-group overlap.

Then cut into tiers, and be honest about the budget:

| Tier | Contents |
|---|---|
| **Must run** | orientation cells (cross-cutting groups over the whole target, because their findings span modules) and every cell with high evidence and high blast radius |
| **If budget allows** | role-archetype and mid-evidence cells |
| **Explicitly skipped** | cells you are *not* running, and why. A skipped cell can be picked up next pass; a forgotten one is how coverage quietly regresses |

Where cost constrains, spend by **difficulty, not symmetry**: structural judgement (boundaries, coupling,
guarantees) rewards the strongest reasoning available; mechanical sweeps (naming, comment discipline, log
formatting, repeated literals) are safe to hand to a smaller or cheaper model. One expensive cell that thinks
well beats six cheap ones that pattern-match.

## 7. Choose the mechanism — whatever you have

The decomposition is fixed; the execution is not. You may have parallel subagents to dispatch with distinct
prompts; a harness that fans out on its own (batch queue, worktree per agent); model tiers, a strong model for
judgement-heavy cells and a cheap one for mechanical ones, or a second different model as an independent second
opinion — which reliably finds what the first reader normalised away; or simply this context, sequentially, one
cell at a time. All of these are legitimate.

What must hold regardless of mechanism:

- **One cell, one reading.** A reading covering three groups at once degrades into a survey.
- **Whole files, not snippets.** A group applied to fragments produces confident nonsense.
- **Read-only**, and fresh state where possible. A reader that may write becomes a refactorer, and the next cell
  reports the wreckage.
- **Prompts are not paraphrased.** If a prompt carries the assigned principle files and the report contract,
  pass it through verbatim; paraphrase is where coverage leaks.
- **Never merge groups to save budget.** Folding the boundary group back into the size-and-style group is exactly
  how the blind spot returns.
- **If the plan looks thin, add slices — never a group across every module.** The full cross-product is the
  thousand-agent pass; the filtered list is the pass.


## 8. Let the results reroute the plan

A pass is a loop, not a batch:

- A **thin** cell is evidence about the code, or about the reading. Do not re-run it identically — change the
  slice or the group, or check whether the group's index row is too abstract to fire.
- A **rich** cell marks a neighbourhood for a **directed deep dive**: one slice, one group, every file read. That
  is the form in which subtle slop is found, and six of them are cheap.
- Finish with an **independent second opinion** — another model, another harness, or the same one after the
  fixes. A different prior finds what the first reader normalised away.

## 9. Instruments (optional)

Two scripts implement the bookkeeping above. They are conveniences, not requirements: if your harness cannot run
them, do the same steps by hand — the **plan** is the deliverable, not the script.

```bash
# plan: enumerate slices×groups, score, select under a budget, order into waves
python3 scripts/swarm_plan.py --repo <root> --target <dir> --out /tmp/deslop-plan --budget 24
#   plan.md        — selected cells in wave order, with the reasoning per cell
#   candidates.md  — the whole permutation list: score components and why each cell stood or fell
#   dispatch.sh    — ready-to-run prompts, one per selected cell

python3 scripts/swarm_lenses.py --check          # prove every principle file sits in exactly one group
python3 scripts/swarm_lenses.py --emit /tmp/cell --target <slice> --only <group> --run 1   # one cell
python3 scripts/swarm_merge.py /tmp/plan/findings-*.jsonl --out /tmp/plan/merged.md        # aggregate
```

## 10. Control

A protocol that promises coverage is tested like a detector: does it find what a monolithic pass missed, on the
same commit and the same neutral prompt? Recorded runs belong here — version, what changed, verdict, failures
included.

| Run | Setup | Result |
|---|---|---|
| 1 | Paired control, same commit and same target (`backend/src/services/agents/model_provider/`, 10 files): **A** — one neutral monolithic pass with the shipped skill; **B** — eight cells, one per group, each forced to read its assigned principle files in full. Read-only, same model, same neutral prompt. | **A: 19 findings across 9 principles. B: 55 findings, 54 distinct, across 25 principles.** B raised **17 principles A never touched** — encapsulation, orthogonality, SOLID, immutability, observability, least privilege, fail-fast, helper-is-an-architecture-finding, small-functions, SLAP, cognitive load, guard clauses, KISS, self-documenting-code, documentation-discipline, least-surprise, elegance — and A raised exactly one B did not (`yagni`, once). Groups that carried the difference: duplication 12 (A had 4 DRY), legibility 11 (A: none of its principles), parsing 10, boundaries 7, guarantees 6, shape 6. `data-layer` returned **0 with an explicit no-schema statement** — a correctly declining group, which is the shape a healthy cell makes when its slice lacks the signal. 34 loci were charged under two different principles, which is precisely the adjudication work the aggregation step (§8) exists for, and 0 were corroborated — no two groups independently fixed the same charge, so the reports were complementary rather than redundant. |
| 1a | Sample verification of run 1 B's findings at source | `model_provider/azure_openai.py:70-90` read directly: the connection decision is re-derived in the adapter (`_first_nonempty` over `AZURE_OPENAI_*`/`FOUNDRY_*`, a bare `env.get("AZURE_OPENAI_API_VERSION")`, `_truthy` over two identity flags), confirming the `one-logical-unit-one-home` / `dry` / `immutability` charges on those lines. Findings remain *candidates*: every one is verified at its line before filing (§9). |

## 11. The next stages (each is its own file, read when you reach it)

This file ends where the readings begin. The stages after dispatch live in their own references so that planning
does not carry context it has not earned yet:

| Stage | Read | When |
|---|---|---|
| **Aggregation** — merge reports on locus + principle; corroborated / single / disputed; coverage accounting; failed readings | [aggregating-findings.md](aggregating-findings.md) | the moment more than one reading has reported |
| **Consolidation and triage** — verify, apply the guardrail, bucket into now / next / wait-or-drop, collapse to concerns, group into a milestone | [consolidating-and-triage.md](consolidating-and-triage.md) | after aggregation, before anything is reported or filed |
| **Reporting** — the shape of the message: lead with the answer, bucket the work, stay short | [reporting-results.md](reporting-results.md) | immediately before you speak to the person who asked |

## 12. What this is not

- **Not a mandate to parallelise.** Sequential cells in one context satisfy the principle; parallelism is an
  accelerator, and a bad plan parallelised is just faster noise.
- **Not a licence to skip the indexes.** The category indexes still explain how the library is organised; the
  plan decides what gets read in full.
- **Not the campaign fleet.** [campaign-mode.md](campaign-mode.md) parallelises over *files being rewritten*,
  with file-level disjointness so writers do not clobber each other. This parallelises over *readings applied* to
  the same files, read-only. Confusing the two produces eight agents editing one file.
- **Not a coverage guarantee by itself.** The partition guarantees every principle is *assigned*; only §8 can tell
  you whether each assignment actually *fired*, and only §9 keeps you honest about what you skipped.
