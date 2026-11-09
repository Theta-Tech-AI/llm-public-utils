---
name: deslop-what-the-principles-buy
description: What improving code by the deslop principles buys — the one idea under the library (code you can trust to mean what it says), the families of broken trust and the bug classes each predicts, which principles lead for which kind of code, the honest costs, and a plain brief for workers who fix code in parallel.
---

# What the Principles Buy

*Read this when you must explain why a pass is worth doing, rank which principles to lead with for a codebase,
or brief other agents who will fix code in parallel.*

## The one idea

Most of the library asks one question: **can a reader trust what the code appears to say?**

- One owner per fact: the value you read is the value in effect.
- Failing fast: silence means success.
- A stated contract: "done" means done.
- A legible flow: the order you see is the order that runs.

Slop is any place where that trust breaks. The code says one thing, and the truth lives somewhere else: in a
second copy, in a swallowed error, in an assumption nobody wrote down, or in a step whose side effect another
step needs.

## The families of broken trust, and the bug class each predicts

Each family below predicts a class of bugs, not one bug. The examples are from one day of work on a
production deploy pipeline (shell, infrastructure-as-code, CI workflows). Every one was found only after it
failed.

| Family (principles) | The promise | When broken | Seen in practice |
|---|---|---|---|
| Fail fast, no silent defaults | Silence means success | A failure that looks like success | A helper called inside `$(...)` in an `echo` argument, and again inside a `[ ... ]` test: `errexit` is off there, so a failed read printed nothing and the write went ahead. A script piped into `tail` hid its own non-zero exit. |
| Single source of truth, DRY | The value you read is the value in effect | Copies drift; a change lands in some places | A job schedule written in four files. Of two scripts that write secrets, one compared first and the other did not, so every deploy created new secret versions. |
| Design by contract | "Done" means done | A postcondition that was assumed, never read back | A job's schedule was assumed held during a release and never was. "Maintenance off" returned before the gateway routed traffic again, and the next step met the maintenance page. |
| Implicit coupling | Two parts agree because the code says so | A silent false pass | A check filtered log rows by a resource's display name, but the log table stores an internal id: zero rows matched, so the check passed forever. |
| Legibility, hidden ordering | The order you see is the order that runs | A race that appears when unrelated code moves | Deleting a step that looked useless removed an accidental delay, and a race the delay had hidden appeared. |

The pattern is useful in an audit: when you find one instance, search for the family, not the instance.

## What it buys

1. **Bugs become cheaper to fix.** A failure shows up at its cause, so the log points at it. Most debugging
   time goes to failures that surface far from their cause.
2. **Features become cheaper to add.** When a fact has one owner, adding a case is one edit. When it has five,
   the change that misses one breaks later, somewhere else.
3. **Regulated and security code becomes reviewable.** In audited code, a hidden assumption is a compliance
   risk. When the contract is stated in the code, a reviewer verifies it instead of reconstructing it.
4. **Reviews converge faster.** Review findings cluster in a few families. Fewer places where facts disagree
   means fewer rounds.
5. **Performance follows.** Repeated or serial work only becomes visible when the flow is legible: a check run
   twice, an unchanged resource re-applied, independent steps run one after another. This is a by-product.
   The purpose is maintainability, and a pass should never trade clarity for seconds.

## Which principles lead, by kind of code

Not every principle pays the same everywhere. Lead with the ones that remove a defect class in that code.

| Kind of code | Lead with | Weigh least |
|---|---|---|
| Deploy scripts, infrastructure-as-code, CI workflows | Fail fast; single source of truth; contracts whose postconditions are read back; declared hand-offs between steps and jobs; idempotency (a re-run changes nothing) | Small functions, complexity scores, line counts |
| Application domain code | Parse, don't validate; illegal states unrepresentable; decide, don't cope; separation of concerns | Premature reuse |
| Data layer | Constraints in the schema, single source of truth in columns, the access path for every join | Abstraction layers over SQL |

A correct consolidation can add lines: moving a fact to one owner sometimes costs a loader and a check. Judge
by one owner per fact and a readable flow, not by net lines.

## The honest costs

- **Churn in a path that works.** A cleanup can break what was fine. Require proof that behaviour did not
  change before merging: byte-identical outputs, identical command lines or call transcripts from a stub,
  an identical compiled template, or the same rendered files.
- **Not every finding deserves a fix.** Apply [the guardrail](../readings/when-to-relax.md): a violation that
  would turn into worse code is not a violation.
- **Security and audited behaviour stays exact** unless the change is the point. Then its owner reviews it.

## Briefing workers who fix in parallel

When several agents fix findings at once, give each the same short brief. It keeps every fix pointing the
same way and keeps workers out of each other's files.

1. **Why:** maintainability first: easier changes, bug fixes and features, and an elegant design. Speed is a
   by-product.
2. **The big picture:** the pass's verdict in three lines, so each fix fits the whole.
3. **Ownership:** which worker owns which files now, and what waits. A need in another worker's files goes
   into the report, not into the code.
4. **The principles, in plain words:**
   - One owner per fact.
   - One job per function.
   - A flow you can read top to bottom.
   - No undeclared hand-offs, and no matching of names as text.
   - No new mode flags.
   - No patchwork: fix the decision, not its symptom.
   - Fail loud: no new `|| true`, `2>/dev/null` or empty fallback, and never a synthesized value.
   - Delete dead code, and add nothing "for later".
   - The plainest code that works.
   - Comments say why.
5. **Proof and review:** each worker proves behaviour unchanged, gets an independent review on its exact
   revision, and does not push. The coordinator integrates and ships one batch.
6. **The report:** the revision, net lines, the proof commands and results, the review verdicts, footholds for
   other findings, and anything deferred with its reason.

## Relation to the rest of the library

| File | Boundary |
|---|---|
| [auditing.md](../readings/auditing.md) | How to run a reading. This file says why the reading is worth running. |
| [when-to-relax.md](../readings/when-to-relax.md) | When a principle does not apply. This file says which principles lead when they do. |
| [campaign.md](../modes/campaign.md) | Running fixes at scale. The worker brief above is what each fixer carries. |
| [measuring.md](measuring.md) | How to claim a number. This file makes no numeric claims. |
