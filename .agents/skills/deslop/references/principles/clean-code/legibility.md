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
  [campaign-mode §Sweep 1](../../modes/campaign.md), and the `shatter` skill for the mechanics.)

## Nothing uses it, so nothing will ever need it

The navigation cost of dead things is easy to state and hard to find, because the code still compiles and the
linter only sees the imports. What linters cannot see is the half that survives in production: **a config key
no deployment sets, a toggle stuck on since launch, a handler registered in a table by name, a branch for a
region or plan that no longer exists, a compatibility shim for a dependency removed two majors ago.** Each reads
as a live decision and occupies the place one would occupy.

Three instruments, in order. **Census the consumers** before calling anything dead: importers, call sites, route
and registration tables, DI wiring, plugin entry points, serializers, event subscriptions, and any downstream
the package's own surface declares — a symbol reached only by name is *unproven*, not dead. **Check the read
side against the set side** for every key and toggle, from the deployment side where no linter looks; read and
set nowhere is dead, set and read nowhere is drift. **Apply the expiry test** to a shim or workaround that names
a condition (a version, a ticket, a date): has the condition lapsed? Then it is dead with proof, and the
sentence that lapses it is the proof.

Then delete all of it in one change — the symbol, the key, the enum member, the tests asserting the dead
behaviour, the comment that says "kept for the transition" — and let CI answer. A wrong guess is one reverted
commit; a kept branch is a permanent tax on every future reader. Where a real consumer exists downstream, the
repair is not deletion but a stated contract with an expiry.

What is *not* dead: a library's public API, an extension point for consumers outside the repo, code reached by
reflection or an entry-point declaration, a live expand-and-contract shim whose second phase has not shipped,
and a seam deliberately left so a second implementation can be injected —
[Modularity](../architecture/modularity.md) already decides whether that hop earns its keep. Commented-out
code is a separate tell: git has the history, so delete it (see [Documentation Discipline](documentation-discipline.md)).

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
