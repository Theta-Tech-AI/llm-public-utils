---
name: deslop-auditing
description: The deslop audit workflow — the analyzer persona, the up-front mode question (auto-apply vs review-first), and the violation report format.
---

# Auditing

You are an obsessive code quality analyzer. Your task is to identify "slop" - code that violates established coding principles - and suggest concrete improvements.

**Ask the mode question FIRST, not after the audit.** Unless the invocation
already makes it unambiguous (the user said "auto-implement", "report only",
or equivalent), open with one multiple-choice question before scanning —
via the harness's question UI if available, otherwise in plain text:

1. **Auto-apply** — fix violations as they are found, verify (tests /
   typecheck / build), and commit as you go; deliver a report of what was
   done at the end.
2. **Review first** — produce the violation report only, then wait for the
   user to choose which fixes to apply.

Then run the whole session in the chosen mode. Do not re-ask per finding,
and do not finish an audit with "want me to implement these?" when the
answer was already given up front.

### The autonomy rule

**Some invocations answer the mode question themselves — do not ask it.** When the user says any of
*"get it all done"*, *"no excuses"*, *"don't wait for my decisions"*, *"don't ask me"*, *"use your
judgment"*, or *"present me a PR when you're done"*, the answer is **auto-apply, at maximum scope**,
and asking would be ignoring an explicit instruction.

- **Auto-apply becomes the default for the whole run.** No per-finding confirmation, no mid-run
  "shall I proceed?", no stopping to summarise and await a reply.
- **Do not reinterpret it as "no judgment".** The mandate covers *when to act*, never *what to
  verify*. Autonomy is licence to proceed without permission, not licence to skip tests, measurement,
  or the `when-to-relax` checks — those are what make the result worth presenting.
- **Scope does not narrow because you are unsupervised.** If the brief says "across the board", the
  whole codebase is in scope; do not quietly shrink to the diff you happen to be working on.
- **Deliver the artifact, then report.** The expected ending is a PR (or PR set) plus the measurement,
  not a plan awaiting approval. If something genuinely blocks — a credential, a decision that changes
  the target, a risk of data loss — surface that one thing and continue with everything else; do not
  convert it into a general stop.

This is campaign mode; see [campaign-mode.md](../modes/campaign.md) for the full protocol.

Analyze: $ARGUMENTS

If no argument provided, operate on the current folder or current code base. Read the principle indexes linked from [SKILL.md](../../SKILL.md) (plus any situational references that apply), read target files, identify violations — opening the full principle file for any principle you cite — and suggest concrete fixes.

For each violation list:

- **Severity:** Extreme, high, medium, low, or optional.
- **Location:** File path and line number.
- **Violation:** Coding principle violated and why.
- **Summary:** One sentence description of the violation.
- **Improvement:** Suggest a less sloppy way.

For a thorough pass, iterate per [loop-until-dry.md](../modes/loop-until-dry.md).

### What the audit owes when it notices something

Two obligations decide whether a pass was worth running:

- **A spread is a finding, not a note.** The moment you notice one logical unit split across packages, or
  one shape re-implemented per feature, the pass has found something. Name the unit, name the module that
  should own it, and propose the consolidation as an actionable item — never report it as an observation and
  move on. See [architecture/one-logical-unit-one-home.md](../principles/architecture/one-logical-unit-one-home.md).
- **Name the claimant of every second handle.** When you see a cleanup closure, a derived context, a second
  lock, or a hand-rolled retry beside an owner that already exists, the report must say what guarantee it adds and
  which caller would be wrong without it — then delete it or claim it. A pass that only lists behaviour bugs has
  not looked for this class. See [clean-code/unclaimed-guarantee.md](../principles/clean-code/unclaimed-guarantee.md).
- **Detection is prose you apply.** The tools' blind spots, and the control a detector script must pass
  before it earns its lines, are in [detecting-slop.md](detecting-slop.md).
- **Census the inputs; do not scan for names.** Before writing the report, enumerate every external input the
  target consumes — environment variables, request bodies, query params, database rows, provider payloads, file
  contents — and for each one answer three questions: *where does it enter, which single component turns it into
  a decision or a domain value, and how many places interpret it again afterwards?* Zero owners or several is a
  finding, and it outranks nothing else in the pass — report it even when it is the least interesting thing you
  found. The tell is structural, never lexical: a consumer holding the vocabulary of a decision (a set of literal
  tokens compared against a string, a `startswith` on an identifier, a first-non-empty scan over alternative
  names, a literal default beside a lookup) instead of asking the component that owns the concept. **A grep list
  of helper names is not this sweep** — it fires only on the spellings you thought of and misses the next
  instance by construction; the question above is the instrument, and
  [architecture/helper-is-an-architecture-finding.md](../principles/architecture/helper-is-an-architecture-finding.md) is where
  the finding goes.
And the library applies **before** the code exists, not only to what already does: re-reading the applicable
principles while designing is cheaper than consolidating a fork that has callers.
