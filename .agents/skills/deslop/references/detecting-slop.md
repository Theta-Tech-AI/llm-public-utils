---
name: deslop-detecting-slop
description: How deslop detection is packaged — what automated tools cannot see, why the detector is prose an agent applies, and the control a detector script must pass to earn its lines.
---

# Detecting Slop

Two questions decide how much of this library ever gets used: **which failures detection can see at all**,
and **where detection lives**. Both are operational rather than philosophical — a rule no pass ever trips
over may as well not be in the library.

## What the tools cannot see

Run the standard tools, believe what they cover, and state what they do not. Their blind spots are not
exotic; they are precisely where the expensive slop lives.

- **Cyclomatic complexity counts decisions inside a function.** When a specialist module is forked from a
  general one, the general one gains no branches — the complexity is *outside the metric's view*, in a
  second file. A codebase can carry thousands of lines of silent duplication at a mean cyclomatic
  complexity of 4.
- **Clone scanners compare text, or AST shape.** The expensive copies rename everything, reorder branches
  and re-express one design in another idiom. A copy renames its files, functions and variables and shares
  no lines, so name-matching finds only the copies nobody bothered to rename. What survives a rename is what the
  code *does*: the primitives it calls. (The behaviour-first hunt is in
  [duplication.md](duplication.md) and [one-logical-unit-one-home.md](architecture/one-logical-unit-one-home.md).)
- **Linters and type checkers see contracts, never cohesion.** A unit split across four packages is
  perfectly typed and perfectly linted.
- **Coverage sees what tests touch**, and a fork is usually well covered — that is why it was written.

So a real finding is often *the reader's*: someone opened three files to answer one question. **Treat that
as data.** It is the highest-yield detector in this library and the one no tool replaces.

## Detection is prose, and that is the design

Instructions an agent applies generalise. A script encodes one generation of one rule.

The library **is** the detector. When a pass needs a tell, the tell belongs here, as text an agent reads and
applies with judgement — not as a program that must be rewritten every time a principle's wording sharpens.
A detector script is a **second source of truth for "what slop looks like"**, and second sources drift: the
script keeps firing at a pattern the principle has since narrowed, and the pass then reports findings the
library no longer supports.

**A script must earn its lines.** Settle it with a control, not an opinion:

1. Take a genuinely fresh agent — not the session that wrote the rule, which already knows the answer — and
   give it **only the markdown**, on the same checkout.
2. Give it the same task: find this class of finding.
3. Compare findings, tool calls and wall time.
4. If the markdown-only agent finds the same things in comparable effort, **delete the script**.

**Verify a finding on the current tip before you file it** — a copy may already be consolidated, and an
unverified report costs the reader the check you skipped. File it with the evidence, never as a note.

Reference results, for calibration. Each fresh agent had only the markdown, on a ~100k-line backend:

| Detector tried | Fresh markdown-only agent | Verdict |
|----------------|---------------------------|---------|
| File-name and role-word scanner, ~130 lines; its first version missed the main finding, and its later sections were fitted to one example | Found the main sibling set plus lock and activity copies in 12 calls, about a minute | **Deleted** |
| Name-blind fingerprint scanner, ~90 lines (library calls, SQL tables, status values, exceptions per file, ranked by overlap) | Nine verified sets in 39 calls and under three minutes, by grepping for a primitive and reading the hits: lease-heartbeat threads (6), content hashing (6), TTL caches (4), schema bootstrap (6), run-worker skeletons (4), retrying HTTP clients, project-lock context managers, object-store wrappers (8), CSV exports — the scanner ranked the heartbeats and the object-store wrappers first and missed most of the rest | **Deleted**; the method is in [duplication.md](duplication.md) |
| Field-overlap clustering of record shapes, ~160 lines | Ten calls and under a minute, by writing a throwaway field-overlap script: the activity event described 6 times, user identity 5 times | **Deleted**; the recipe is in [duplication.md](duplication.md) |

The pattern repeats: a detector fitted to the finding in hand describes that finding, while an agent working
from a *method* (grep for the primitive, group by content, read the hits) generalises past it. Each scanner
cost more lines than the method and missed sets the method reached — which is why none of the three ships
with this library.

**The control applies to a principle too, not only to a script.** A principle file is detection prose, and the
same question decides whether it works: does a fresh, markdown-only agent that has the rule actually find the
finding? Measured on one adapter directory, same checkout, same neutral prompt, read-only:

| Version of the rule | Fresh markdown-only agent (identical neutral prompt, read-only) | Verdict |
|---------------------|------------------------------|---------|
| Doctrine only — "a private reconciling helper proves nothing owns the value" | Seven findings; caught the prefix sniffing sibling seven lines away and **never mentioned the boolean helper between it and its quoted line**, nor the sibling duplicated in a second adapter | **Failed** |
| Doctrine + a grep for helper *names* (`_truthy|_first_nonempty|to_bool|…`) | Nine findings; helper, twin and prefix all reported under the principle by name, owner-first repair prescribed | **Passed — and rejected anyway**: a name list fires only on the spellings its author had, which is the fitted detector described above, and it passed because detector and control case came from the same example |
| Doctrine + input census in `auditing.md` only (no names) | Caught the configuration *seam* via [one-logical-unit-one-home](architecture/one-logical-unit-one-home.md) — alias precedence that ignores a credential alias the chat path supports — and applied the new principle twice, on the prefix sniff and on a bypassed wire-parameter decision, but never named the boolean helper | **Partial** |
| Same, with the tells placed where a neutral pass actually reads them: the architecture index row states the *structural* tells (a string compared against a literal token set, `startswith` on an identifier, first-non-empty scans, the same `env.get("NAME", default)` repeated across files), and `SKILL.md` names the census in its always-read row | Six findings, two of them High, both under the new principle: one naming **the boolean helper and its twin** inside the Foundry-credential seam, one the prefix sniff — and it ran in-memory probes to confirm the stream-close, delay-cap and empty-validator defects rather than asserting them | **Passed, with no names anywhere** |
| Principle file named directly (usability test rather than discovery) | Five instances, including a fourth — repeated `float(env.get("AGENT_MODEL_TEMPERATURE", "0"))` across four adapters — that appears nowhere in the principle, and three plausible false positives correctly declined because an owner already existed | **Usable** |

**The index row is a trigger, and a trigger is not a criterion.** Three further runs, identical prompt, differing
only in the architecture index row for this principle:

| Row variant | Lone helper reported? | Reading |
|---|---|---|
| Thesis clause added, repeated-`env.get` sighting tell kept | Yes — twice, once as the first High finding | Hook present |
| Rewritten to lead with "one instance is enough", sighting tell **removed** | **No** — the duplicate was reported, the lone helper was not | Removing an evidence hook because it is not the criterion costs recall |
| One-instance rule **and** the hook, labelled "sighting aid only — not the criterion" | Yes | Both properties held |

So: state the criterion architecturally (a raw value reached a consumer that had to interpret it — one instance
is enough), and keep the cheap sighting pattern in the trigger position, named for what it is. Conflating the two
in either direction fails — a hook allowed to decide admits padding, a hook deleted for being imperfect loses the
finding. And note what no neutral run did: *speak* the thesis. Detection came from the index; the reasoning came
only from opening the principle file, which is the division of labour those two files are for.

**A control proves a rule FIRES; only a review proves it is RIGHT.** Both runs above passed on a rule whose
central claim — "delete the added lines and behaviour is identical" — was false: a context signals cancellation
and never establishes completion, so the added handle did supply a guarantee (completion synchronisation) that
the original lacked. The agents agreed with the rule because the fixture encoded the rule's own framing. An
adversarial review by an independent harness, asked to challenge the Go semantics, the stated facts, the
overreach and the decidability, returned **UNSOUND** and named all four; the second version of the file corrects
them and adds a short 'facts this file's first version got wrong' section. Always run both instruments: the
fixture for discovery, the review for soundness, and never quote the first as evidence of the second.

**A decoy fixture beats a real repo for testing a change-shaped principle.** A principle about *diffs* cannot be
controlled on a codebase that only contains the finished code, so build the target: one planted instance plus the
look-alikes that a wrong rule would also flag, and require the pass to separate them.

| Principle controlled | Fixture | Fresh markdown-only agent, neutral prompt | Verdict |
|---|---|---|---|
| **An Unclaimed Guarantee** | a small Go package holding the diff's added trio (derived `WithCancel` + `done` + returned cleanup beside an existing `ctx`), a legitimate returned closer (`os.Open`-shaped), a legitimate `WithTimeout` + `defer cancel`, a hand-rolled retry and a watcher | Runs 1 and 2 both reported the trio as a High finding under the principle by name, both declined the two legitimate look-alikes, and one found a real double-close panic in a decoy | **Fired 2 of 2 — but see below** |

The lesson is the same one the scanners taught: **the rule that fires is the one the workflow obliges**, not the
one the doctrine implies. A principle whose detection depends on the agent remembering to think of it will be
outranked by whatever the pass finds more interesting — so put the trigger (a grep the pass must run, an
obligation to report) in the protocol, and keep the doctrine in the principle file.

**And the trigger must not be a list of names.** The first attempt at the sweep above was a grep for
`def _(truthy|first_nonempty|to_bool|coerce|normali[sz]e|...)` — and it passed its control, which is exactly why
it is dangerous: it fires on the spellings the author had in hand and walks past `_as_flag`, `_setting_switch`,
`_resolve_capability` and every name invented afterwards. That is the fitted-detector failure this file already
describes, reproduced inside the protocol. The replacement obligation is a *census* — for each external input,
who owns turning it into a decision, and how many consumers re-interpret it — which is answerable without knowing
any names, and which generalises to inputs that are not configuration at all (request bodies, rows, payloads).

## Where a script does earn its keep

Three properties, all required:

- **Mechanical** — no judgement anywhere in the decision it makes.
- **Exhaustive** — it must sweep the whole tree; a sample is not a sweep.
- **Stable** — the rule it encodes will not move as the principles are refined.

Token and AST clone matching qualifies — `jscpd`, `pmd-cpd`, and `scripts/astdup.py` / `scripts/tsdup.cjs`,
which hash function bodies with every name and constant erased so renamed copies collapse, and print a
redundant-line total usable as a CI ratchet. This class is admitted on its **properties**, not on a control:
the decision is mechanical, the sweep is exhaustive, and the rule does not move when a principle is reworded.
Finding *which primitive a mechanism uses* does not qualify — that is one grep, and shell is the ceiling for
cheap views.

```bash
# every file that hand-rolls a heartbeat thread — then read the hits
grep -rlE 'Event\(\)' <src> --include='*.py' | xargs grep -lE '\.wait\(' | xargs grep -lE 'Thread\('
```

If a view fits in one command, it belongs in the instructions, not in a file. See
[duplication.md](duplication.md) for the primitives to grep for and the token scanner's proper role.

## Detection runs twice: at design, and at audit

The views above audit code that already exists. The cheapest place for this library is the design, before
the second copy exists: **re-read the applicable principles while designing, not only when auditing.** The
design-time question is not "is this slop?" but "am I about to make a second home for something that
already has one?" ([one-logical-unit-one-home.md](architecture/one-logical-unit-one-home.md)). A fork caught
while it is still a plan costs nothing to avoid; the same fork after it has callers costs a consolidation
campaign.

## A finding is an issue, not a note

The audit's output contract, and the reason a good observation still goes to waste: **a finding that changes
code must leave the pass as an actionable item.** For a consolidation that means the proposal — the unit
named, the owning module named, the pieces to move listed. "This looks similar to X" in a report is a note;
the next reader must re-notice it, re-scope it and re-decide it on your behalf. A note is a finding you
declined to finish.

In relation to other references, detecting slop governs the detector rather than the code:

| Reference | Relationship |
|-----------|--------------|
| [**Hunting Duplication**](duplication.md) | Its scanners look for repeated text; this file is about the detector's own packaging |
| [**Auditing**](auditing.md) | The pass this file arms — the judgment stays with the agent |
| [**Measuring a Campaign**](measuring.md) | The same discipline, a different object: measure the mechanism, not your part in it |
| [**Extending the Library**](extending-the-library.md) | A detector script is a library artifact; the discovery-first rule applies before writing one |
| [**One Logical Unit, One Home**](architecture/one-logical-unit-one-home.md) | The finding class that motivated the control test |

## Summary

1. **State what your tools cannot see.** Complexity counts decisions inside a function; clone scanners
   compare text; neither sees a design forked into a second file.
2. **A copy renames everything except what it does**, so search by primitive and by field content, never by
   file or function name. "I opened three files to answer one question" is a finding, not a feeling.
3. **Detection is prose an agent applies** — a script is a second source of truth and drifts from the
   principles it encodes.
4. **Make a script pass a control**: a fresh, markdown-only agent on the same checkout. Match its findings
   and the script is deleted.
5. **One-line shell is the ceiling for cheap views**, and a finding that changes code leaves the pass as a
   named, actionable item — never a note.
