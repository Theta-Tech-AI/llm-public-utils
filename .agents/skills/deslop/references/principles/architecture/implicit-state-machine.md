---
name: deslop-architecture-implicit-state-machine
description: Deslop principle — A State Machine Nobody Wrote Down: a status or mode field whose legal transitions exist only as conditions scattered across call sites, so no single place can answer which moves are allowed.
---

# A State Machine Nobody Wrote Down

Every system with a status field already has a state machine. The question is only whether it is
explicit — a graph someone can read and enforce — or implicit, smeared across the conditions of every
caller, so the transitions live in the developers' heads.

The states are rarely the problem; a field holding one of five named values is fine, and
[Make Illegal States Unrepresentable](illegal-states-unrepresentable.md) may already have tightened it.
What is missing is the **transition relation**: which move is legal from which state, and who may cause
it. When that lives nowhere, every writer re-derives it with an `if`, the copies drift, and a workflow
advanced by a worker, a job and an admin endpoint ends up with three answers to "is this move allowed".

```python
# ❌ the transitions exist only as conditions in each writer, in three different modules
class Document:
    status: str            # "draft" | "review" | "approved" | "published" | "archived"
    locked_by: str | None  # a second dimension nobody reconciled with status

def publish(doc):                                # api/handlers.py
    if doc.status not in ("approved", "published") or doc.locked_by:
        raise Conflict("cannot publish")
    doc.status = "published"

def retry_index(doc):                            # jobs/indexer.py
    doc.status = "approved"                      # bypasses publish() entirely

def close(doc):                                  # admin/api.py
    doc.status = "archived"                      # an approved document can be archived — undecided
```

```python
# ✅ one owner names the states and the table of legal moves; callers request a transition
class State(Enum):
    DRAFT = auto(); REVIEW = auto(); APPROVED = auto(); PUBLISHED = auto(); ARCHIVED = auto()

LEGAL = {                                           # every allowed move, in one readable place
    (State.DRAFT, State.REVIEW):        "submit",
    (State.REVIEW, State.APPROVED):     "approve",
    (State.APPROVED, State.PUBLISHED):  "publish",
    (State.PUBLISHED, State.ARCHIVED):  "close",
}

@dataclass
class Document:
    state: State = State.DRAFT

    def transition(self, target: State) -> None:      # the only writer of `state`
        if (self.state, target) not in LEGAL:
            raise IllegalTransition(f"{self.state.name} -> {target.name}")
        self.state = target

def publish(doc):            # the caller asks; the machine answers
    doc.transition(State.PUBLISHED)
```

Three moves, in this order: **name the states**, **centralize the transitions**, **route every mutation
through the owner**. Naming alone fixes the representation and leaves the transitions scattered; the
second move does the work, because it makes the graph one readable function or table and makes "can it
go from X to Y?" a question with an answer. A new rule becomes a new row, not an edit to five call sites.

The cost grows faster than the code: `n` booleans beside a status give up to `2^n × states` combinations,
of which only the intended few mean anything, and every bug of this class is the same bug — a writer left
the system in a row nobody intended.

## What this adds over its neighbours

[Make Illegal States Unrepresentable](illegal-states-unrepresentable.md) governs **what may be true** —
the shape of the datum — and is silent on what may *happen next*: a model can be a perfect variant type
and still be driven by an unwritten graph. [Guard Clauses](../clean-code/guard-clauses.md) is the same
conditionals with a better local shape — flat, early-out, still per-caller.
[Implicit Coupling](implicit-coupling.md) is the closest neighbour: it names two components agreeing on
something unstated, and the legal move set is one such agreement — honoured by one writer, ignored by the
next, neither obviously wrong.

## The tests

1. **Writer census** — grep every assignment to the field (`state =`, `status =`, `set_status`,
   `update(status=…)`). Two or more writers is the finding's first measure: the transition relation has
   no owner, whatever the conditions say.
2. **Event-table test** — draw states against events, a cell per pair, and fill it **from the code only**.
   A cell needing a second file, or coming back "no one knows", is an implicit transition — and the empty
   cells are indistinguishable from the forgotten ones.
3. **Legality question** — ask in plain words, *can it go from X to Y?* If answering requires studying the
   callers, the graph is implicit; if no file can answer it, the graph has no owner and that is the report.
4. **Boolean explosion** — count the flags interacting with the status field. `2^n × states` against the
   handful of intended states measures how much of the state space is undefined behaviour. Report the
   number; do not make a threshold the criterion.
5. **Bypass test** — does any path write the field without the checker — a job, a script, an admin
   endpoint, a fixture? Then the check is a suggestion and the machine is broken at that seam. Report the
   bypass first: a live defect, not a design smell.
6. **Reverse test** — delete the central transition function and repair the callers. If each simply
   re-grows its own `if`, the architecture changed nothing and the graph is still unwritten.

## The family: one disease, many costumes

| Artifact | The transition nobody owns | The component that was missing |
|---|---|---|
| `status: str` written in three modules | publish / archive / retry moves | one transition table plus a guarded setter |
| five `is*` booleans checked in combination | idle, running, paused, failed | one state value and one owner of its changes |
| a UI setting `editing`, `dirty`, `saving` separately | the save lifecycle | one save state in place of three flags |

## The repair

**Give the graph an owner before reaching for a library.** The lowest tier that answers the legality
question is the right one: an enum plus one guarded transition function for most workflows, a transition
table when the graph is dense, per-state types or a statechart when behaviour differs by state or the
graph has hierarchy and parallelism. Order matters — name the states, centralize the mutations, make
callers request a transition instead of writing the field, and delete the scattered conditions in the
same change. Their disappearance is the measure of the fix.

## Boundaries

Not every status deserves this. A genuinely linear flow — `draft → published → archived`, one writer, no
branching — is an enum and a method per transition, and a machine definition longer than the code it
replaces is a net loss. A two-state toggle is a boolean in disguise; a CRUD wrapper that only updates a
column adds indirection and no policy. The finding needs a **graph worth writing down**: several states,
moves that can be illegal, more than one writer, or a question a colleague cannot answer. Where a framework
or external workflow engine already owns the graph, the finding is the writer that escapes it.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Implicit state machines | David Khourshid, via *Finite State Machines: The Developer's Bug Spray* (Scott Logic, 2020); statecharts.dev | The name and the failure: the machine exists, but only in the developers' heads |
| Statecharts | David Harel, *Statecharts: A visual formalism for complex systems* (1987) | Hierarchy, concurrency, refinement — the formalism an explicit machine reaches for |
| Implementation tiers | Miro Samek, *Practical UML Statecharts in C/C++* (2008) | Nested switch, state table, State pattern — the tiers a repair is ordered by |
| Boolean explosion; accident states | EventMachine, *When Not to Use a State Machine*; Leon's Notes, *The Implicit State Machine* (2026) | `2^n × states` as the countable cost, and the graduation signals for formalizing |
| Flag argument; State pattern | Martin Fowler, *Flag Argument* (2011); Gamma et al., *Design Patterns* | The miniature (a boolean selecting behaviour) and the per-state-behaviour repair |

**What is this library's own:** the **writer census** as the first decidable measure — count the
assignments before arguing about the graph; the **legality question** as the owning-module probe; the
bypass test read from the same codebase; and the tier discipline — repair to the lowest formalization
that answers the legality question, not to a library.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Make Illegal States Unrepresentable**](illegal-states-unrepresentable.md) | The shape of one state; this is the legality of moves between states. |
| [**Separation of Concerns**](separation-of-concerns.md) | The symptom: one change scattering across callers. The owner is the repair. |
| [**Implicit Coupling**](implicit-coupling.md) | An unstated agreement between components; the legal move set is one. |
| [**Encapsulation**](encapsulation.md) | Tell, don't ask: a guarded transition is the tell form of a mutable status field. |
| [**Domain Constraints**](../data-layer/domain-constraints.md) | The same closed vocabulary at rest — a `CHECK` constrains values, never moves. |

## Summary

1. **Every status field is a state machine; the defect is that nobody wrote it down.**
2. **Count the writers first** — two or more assignments mean the transition relation has no owner.
3. **The legality question is the probe** — if no file answers "can it go from X to Y?", that absence is the finding.
4. **Name the states, centralize the transitions, route every mutation through the owner**, and delete the scattered conditions as the measure.
5. **Match the formalism to the graph** — an enum and one guarded function for most flows; nothing heavier than the question requires.
