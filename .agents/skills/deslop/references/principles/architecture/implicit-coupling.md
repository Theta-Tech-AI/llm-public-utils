---
name: deslop-architecture-implicit-coupling
description: Deslop principle — Implicit Coupling: two components agree on something the code never states, so the agreement is invisible to readers and compilers until a new caller breaks it.
---

# Implicit Coupling

> "Connascence codifies what many experienced engineers have learned by trial and error: having a common set of
> nouns to refer to different types of coupling allows us to share that experience more easily."
> — connascence.io, after Page-Jones

Declared coupling is cheap: a signature, a type, an interface. **Implicit coupling** is everything two components
must agree on that the code never says out loud — the order in which members are called, which string literal means
"fast", which module must have initialised which singleton, which environment variable is read at the point of use.
It compiles, it reviews clean, and it fails in the one caller that did not already know. The finding is not the
magic string or the `configure()` step; it is that **no component owns the agreement** — so every consumer must
carry a piece of it.

```python
# ❌ The caller must know the order, and which string selects the branch
class Exporter:
    def __init__(self, fmt: str):
        self._fmt = fmt          # "csv" — a vocabulary four other modules also compare

    def export(self, rows: list[Row]) -> None:
        target = self._target   # AttributeError for any caller who skipped configure()
        target.write_text(render(rows, self._fmt))

    def configure(self, path: str) -> None:
        self._target = Path(path)

# elsewhere
if settings.mode == "csv":
    exporter = Exporter("csv")
    exporter.configure(out)     # the order lives in the caller's head
    exporter.export(rows)
```

```python
# ✅ The vocabulary has one owner, and the object cannot exist half-built
mode = ExportMode.parse(settings.mode)          # the only place "csv" is interpreted

@dataclass(frozen=True)
class Exporter:
    target: Path
    mode: ExportMode

    def export(self, rows: list[Row]) -> None:
        self.target.write_text(self.mode.render(rows))
```

Three failures stack behind the ❌, each independently reportable: the object has a state it cannot legally be
used in; the string vocabulary is re-interpreted at every comparison site; and the ordering constraint exists only
in the callers that happened to get it right.

## What this adds over its neighbours

**Encapsulation** says hold the invariant inside the type; **Dependency Injection** says declare what you need.
Both are prescriptions. This file is the *reading*: walk a call site and ask what the callee requires that the
signature does not state — order, vocabulary, ambient state, identity. It is the diagnostic the other two presume
the reader has already performed.

## The tests

1. **Signature test** — read one call site. For every value the callee depends on, is it in the signature, or must
   the caller have known something else to write this line?
2. **Order test** — can the members be called in any order? If one must precede another, the type should not admit
   the unconfigured state at all.
3. **Vocabulary test** — grep each literal the code compares (`"csv"`, `"active"`, `1`, `"prod"`). Two modules
   comparing the same literal means the vocabulary is unowned.
4. **Ambient test** — does the component read a global, singleton, or environment at the point of use instead of
   receiving it? Legitimate only in the composition root.
5. **Fan-out test** — change the literal, the order, or the singleton and count the modules that must change. That
   count is the *degree* of the hidden agreement, and it is what makes it a finding.

## The family: one disease, many costumes

| Artifact | The agreement nobody owns | The component that was missing |
|---|---|---|
| `configure()` then `use()` | the required call order | a type that cannot be constructed incomplete |
| the same literal compared in five modules | what a value means | one parser returning a typed decision |
| `get_instance()` reached, never injected | which instance is live | the composition root handing it in |
| env var read four layers deep | the configuration contract | a settings loader at start-up |
| a listener assuming the publisher ran first | the event order | a single orchestrator, or an explicit dependency |

## The repair

**Own the agreement first, then delete the ways to break it.** One module parses the vocabulary and returns a
typed decision; constructors become the only door so the illegal intermediate state cannot be built; collaborators
are handed in from the composition root. Delete the `configure()` step and the raw literal comparison in the same
change — their disappearance is the measure.

## Boundaries

Not all coupling is implicit: **connascence of name** (a function's name) is the weakest kind and is not a finding.
Request-scoped ambient context (a thread-local, a framework's request object) is fine when it is entered and exited
by framework code at a seam — the violation is reading it deep inside business logic. Wiring performed by a DI
container at start-up is the composition root doing its job. A one-shot script may legitimately have modules that
must be called in order.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| Connascence | Meilir Page-Jones, *What Every Programmer Should Know about Object-Oriented Design* (1996); connascence.io | Names the types — static (name, type, meaning, position, algorithm) and dynamic (execution, timing, value, identity) — and the axes of strength, degree and locality. This file's taxonomy is theirs. |
| Temporal coupling | Mark Seemann, "Design Smell: Temporal Coupling" (2011) | The order-of-calls case, and the observation that it is broken encapsulation. |
| Connascence of meaning | connascence.io | The shared-magic-value case. |

**What is this library's own:** the reading order — signature, then order, then vocabulary, then ambient — and the
repair order, which owns the vocabulary before removing the unbuildable state.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Encapsulation**](encapsulation.md) | The invariant this principle finds unprotected. |
| [**Dependency Injection**](dependency-injection.md) | The repair for the ambient and identity cases. |
| [**Law of Demeter**](law-of-demeter.md) | Limits what a collaborator may *reach*; this limits what it must *know*. |
| [**A Helper That Must Exist Is an Architecture Finding**](helper-is-an-architecture-finding.md) | That file finds the raw value; this one finds the agreement around it. |
| [**Parse, Don't Validate**](parse-dont-validate.md) | The boundary-side repair; this is the coupling-side diagnosis. |
| [**Layering Violations**](layering-violations.md) | Direction of knowledge between layers; here it is the shape of what is known. |

## Summary

1. **If a caller must know something the signature does not say, the code has an ownerless agreement.**
2. **Count the degree:** how many modules must change together when the agreement changes.
3. **The literal, the order and the singleton are symptoms** — the finding is the missing owner.
4. **Own the vocabulary, then make the illegal state unbuildable**, and delete the call-site knowledge.
5. **Weakest coupling is name; strongest is identity** — prefer agreements that are declared and local.
