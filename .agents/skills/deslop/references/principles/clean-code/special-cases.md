---
name: deslop-clean-code-special-cases
description: Deslop principle — A Special Case Is a Requirement the Design Never Accounted For: code that exists for one situation instead of following from how the system works, so the branches are evidence of a missing mechanism rather than the defect itself.
---

# A Special Case Is a Requirement the Design Never Accounted For

> "Special cases: code that exists for one situation instead of following from how the system works."
> — the framing borrowed from an outside skill, kept because it is the clearest statement of the rule

A special case is a branch, parameter, delay or flag that exists because **one situation had to be
accommodated** and the design had no way to express it. It is not a styling problem: every one of them is a
requirement that arrived after the shape was chosen, and was absorbed at the point of impact instead of being
folded into how the system works. Fixing them one at a time is how a file becomes
[Patchwork](../clean-code/patchwork.md); the useful move is to read them together, because they are the
specification of the design the system actually needs.

```python
# ❌ four situations, four local accommodations, no mechanism behind any of them
def close_dialog(dialog):
    dialog.hide()
    if dialog.kind == "logout":            # one dialog needs something no dialog has
        time.sleep(0.1)                    # a race, absorbed with a delay
    if tenant == "acme":                   # one customer's rule, at the call site
        audit_log.write("acme-close")      # a global poked from deep inside
    if order.provider == "paypal":         # one vendor's special path
        ...
```

```python
# ✅ the mechanism the special cases were each impersonating
class Dialog:                              # every dialog returns focus to its opener — the rule, not a case
    def close(self) -> None:
        self.hide()
        self.opener.focus()
```

The count is the interesting part. **A single special case is a bug report; three that share a shape are a
missing concept.** That is why the workflow is collect first, then decide: the deliverable of the reading is
the list, grouped by what each case reaches for, and only then the mechanism that retires the group.

## What this entry is not

It is **not** the same finding as its neighbours, and it is worth keeping the distinction sharp:

- [Patchwork](../clean-code/patchwork.md) is the **accumulated form** — a file no line of which you are
  willing to delete. A special case is the **unit**, and the signal is what it stands for: a requirement
  nobody encoded. Patchwork is read when the file feels wrong; this is read when a branch appears for one
  situation.
- [Guard Clauses](../clean-code/guard-clauses.md) makes a special case *tidier* — flat, early, readable — and
  leaves it a special case. Shape is not provenance.
- [Decide, Don't Cope](../clean-code/decide-dont-cope.md) covers the same instinct at the type boundary;
  this covers it everywhere the design meets a situation it did not model.
- [Implicit Coupling](../architecture/implicit-coupling.md) is an agreement between two components; a special
  case is usually where one of them broke it unilaterally.

## The tests

1. **Owning-module test** — name the component whose existence would make this branch unnecessary. "None" is
   the finding, and it is the finding even when the branch is one line and correct. Naming it is the finding;
   writing it is the repair.
2. **Reverse test** — delete the special case and repair the call sites. If the repair is **another
   conditional** somewhere else, the design changed nothing; if it is one component deciding and N call sites
   receiving, the missing mechanism has been named.
3. **Provenance test** — does the condition follow from a value the system already models (a tenant's policy,
   a provider's capability, a state), or from a situation nothing models? The first is derivable and belongs
   in data or a policy table; the second is the design gap.
4. **Census and grouping** — collect every special case in the slice, then group by *what each one reaches
   for* (a focus owner, a policy, a provider capability, a timing guarantee). A group of three is one missing
   owner. Report the grouping, not a flat list — and report **how many survive**, which is a better measure
   of design distance than line count.
5. **Incident test** — `git log -S'<condition>'` on the line. A branch added by a fix commit with a ticket
   number is an incident absorbed on the spot; that is where these come from, and it is corroboration, never
   the criterion.
6. **Bypass test** — does the codebase already own this decision? Then the special case is a caller that
   opted out of the owner, which is a live defect rather than a design smell.

## The family: one disease, many costumes

| Special case | The situation it accommodates | The mechanism that retires it |
|---|---|---|
| `if tenant == "acme"` at a call site | one customer's rule | policy per tenant, owned and loaded once |
| a `sleep`/retry to make an ordering work | a race nobody named | the event or guarantee that was assumed |
| a global flag (`skipRefocus`) set by one caller | one interaction needing different behaviour | the behaviour as a property of the component |
| `if provider == "x": …` in a shared path | one implementation's difference | a variant behind a common interface |
| a parameter only one caller sets to `False` | one caller's exception to the rule | a second entry point, or the option removed |

## The repair

**Find the common statement, then delete the cases.** Read the list, name the one mechanism that would have
made all of them unnecessary, and place it where the situations are actually decided — an owner, a policy
table, a variant type, a property of the component. Then remove every special case that mechanism retires,
in the same change, and keep the ones that are genuine one-offs **with their reason written down**. The
measure of the fix is the fall in the count.

## Boundaries

Some special cases are legitimate and should be kept deliberately: a workaround for a defect in something you
do not control (kept, named, linked to a ticket, with a condition that lapses it); a regulatory or contractual
one-off that genuinely is one-off (put it in data, not in code); a hand-tuned hot path (keep it, mark it, and
keep the general path beside it); a migration shim with an expiry. What makes a case legitimate is **that its
reason is written where it lives, and that its condition can lapse** — an unowned special case in a file with
no reason beside it is indistinguishable from slop, and it is the one that outlives its requirement.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Special Case; Null Object | Martin Fowler, *Patterns of Enterprise Application Architecture* (2002) | The named technique for absorbing one situation behind an ordinary-looking object |
| Replace Conditional with Polymorphism; Consolidate Conditional Expression | Martin Fowler, *Refactoring* (1999, 2018) | The mechanical refactorings that retire a group of conditionals once the owner exists |
| Shotgun surgery; divergent change | Martin Fowler, *Refactoring* | The downstream cost when one situation is absorbed in several places instead of one |

**What is this library's own:** the **framing** — a special case is a *requirement the design never accounted
for*, so the branch is evidence and the requirement is the finding; the **owning-module and reverse tests**
as the decidable instruments; and the **census-as-measure** — how few special cases survive is a truer
statement of design distance than any size metric.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Patchwork**](../clean-code/patchwork.md) | The accumulated file. This is the unit, and the requirement behind it. |
| [**YAGNI**](../clean-code/yagni.md) | Nothing built yet versus nothing the design can express: YAGNI removes a feature, this names a missing mechanism. |
| [**One Logical Unit, One Home**](../architecture/one-logical-unit-one-home.md) | The same shape copied per feature; here the shape is a per-situation exception. |
| [**A State Machine Nobody Wrote Down**](../architecture/implicit-state-machine.md) | A special case is often a transition that had no legal-move table to join. |
| [**Principle of Least Surprise**](../clean-code/least-surprise.md) | Consequence: the reader meets behaviour that follows from one situation nobody documented. |

## Summary

1. **A special case is a requirement the design never accounted for; the branch is evidence, not the crime.**
2. **Ask what component would have made it unnecessary** — "none" is the finding.
3. **Collect before you fix** — group by the mechanism each case reaches for; three of a shape is one missing owner.
4. **Repair by placing the mechanism where the situation is decided**, and delete the cases it retires as the measure.
5. **A legitimate one-off keeps its reason beside it and a condition that lapses it.**
