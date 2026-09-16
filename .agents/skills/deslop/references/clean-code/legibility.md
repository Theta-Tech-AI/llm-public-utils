---
name: deslop-clean-code-legibility
description: Deslop principle — Legibility: a codebase you can navigate, where the path from entry point to effect is followable and the map in the reader's head matches the code.
---

# Legibility

> "Any fool can write code that a computer can understand. Good programmers write code that humans
> can understand."
> — Martin Fowler

Most clean-code principles govern *reading one function*. Legibility governs **finding your way
around the whole thing**. It is the property that lets a newcomer — or you, in six months — answer
three questions quickly:

1. **Where does this behavior live?** (navigation)
2. **What happens when I change this?** (blast radius)
3. **How does data get from here to there?** (connection)

A codebase can be made of flawless small functions and still be illegible: a maze of well-written
rooms with no corridors. That is the failure this principle names.

## Connection: the map in the reader's head

The reader builds a mental model of how things connect. Legibility is the size of the gap between
that model and the code.

**Violations:**

- **A call path you cannot follow.** `handler → service → helper → registry → callback → the thing
  that actually happens`. The behavior is real but no single file says so. Fix by collapsing
  indirection with one caller, or by documenting the path.
- **Action at a distance.** A global, event bus, or module-level side effect changes state from
  somewhere unrelated. The reader must hold the whole system in mind to predict one function.
- **Hidden wiring.** Frameworks that resolve behavior from decorators, conventions, or string names
  with no local evidence of what runs. Not always removable — but it needs a map or a pointer comment
  at the seam.
- **Two names for one concept**, or one name for two — the reader cannot tell whether `Job`,
  `Run`, and `Task` are the same thing. Naming *is* the map; when names lie, navigation becomes
  archaeology.

## Navigation: entry points and boundaries

**Violations:**

- **No discoverable entry point.** Behavior reachable only by knowing which of seven similarly-named
  modules to open.
- **Boundary blur.** HTTP concerns, domain logic, and persistence interleaved so no layer is
  identifiable; you cannot tell where a change belongs, which is how the next violation gets created.
- **A directory tree that does not match the domain.** Files grouped by technical kind (`utils/`,
  `helpers/`, `misc/`) rather than by concept, so locating a feature means searching for its name
  across every folder.
- **Dead routes** — endpoints, handlers, or flags nothing reaches. Navigation cost with no payoff.

## Blast radius: making change predictable

A legible codebase lets you answer "what breaks if I touch this?" without running the system.

**Violations:**

- **Wide fan-out from a shared helper.** One `format()` used by 40 call sites across 6 domains — any
  change is unownable. Fix by splitting along the actual axes of variation, not by "sharing".
- **Leaky abstraction.** Callers reach through an interface into its internals, so the abstraction
  documents a boundary that does not exist.
- **God module** — everything imports it, so everything is coupled to everything. (See
  [campaign-mode §Sweep 1](../campaign-mode.md), and the `shatter` skill for the mechanics.)

## The legibility artifacts

Legibility is unusual among these principles: the fix is sometimes **writing the connection down**,
not restructuring the code.

- **A module map** — one page: the top-level concepts and which module owns each.
- **Documented call paths** for the two or three core flows, naming the files in order.
- **A pointer comment at every seam** where the framework or a registry decides what runs.
- **Accurate names** for the concepts, applied consistently — the cheapest legibility win available
  and the one most often skipped because it touches many files.

Prefer restructuring when the path *can* be made short. Document when it genuinely cannot — a
framework boundary or a required indirection. **A list of files in the order they run is worth more
than a diagram that will drift.**

```python
# ❌ Wrong - the path exists only in the reader's imagination
# request -> ProjectService.handle() -> ProjectHelpers.dispatch()
#   -> Registry.resolve(name) -> SomeHandler.run()   [no single file shows this]

# ✅ Correct - the seam states what runs, so it can be followed and checked
# Handlers are resolved by name from PLUGIN_REGISTRY (see plugins/__init__.py).
# Adding a handler means adding it there; no other file needs to know this name.
handler = PLUGIN_REGISTRY[name]
```

## Summary

1. **Connection** — the reader must be able to follow a path from entry point to effect; collapse
   needless indirection, document what remains.
2. **Navigation** — one discoverable entry point per feature; directory structure and naming that
   match the domain, not the technical layer.
3. **Blast radius** — narrow, ownable fan-out; no caller reaching through an interface into internals.
4. **Names are the map** — one name per concept, used consistently; a lying name costs more than a
   missing one.
5. **Write the seam down** when it cannot be shortened — but only where the code genuinely cannot say
   it itself.

**Important caveat:** unlike deletion, legibility work has **no LOC metric**. Some of it adds lines
(comments at seams, a module map) and that is correct. Do not let a LOC target talk you out of the
one sweep that makes everything else findable.
