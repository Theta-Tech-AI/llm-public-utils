---
name: deslop-clean-code
description: Deslop principles — Clean Code: KISS, YAGNI, Small Functions, Guard Clauses, Decide Don't Cope, Cognitive Load, Cyclomatic Complexity, SLAP, Self-Documenting Code, Documentation Discipline, Elegance, Legibility, Patchwork, An Unclaimed Guarantee, Least Surprise.
---

# Clean Code

Write clear, simple, readable code. Do less, but better. Reduce complexity, and make the code easily readable.

Each principle is a self-contained file — open it when a finding implicates that principle.

| Principle | What it says |
|-------------|----------------|
| [KISS: Keep It Simple, Stupid](clean-code/kiss.md) | Simplest sufficient code; watch parts plethora, over-abstraction, overengineering |
| [YAGNI: You Aren't Gonna Need It](clean-code/yagni.md) | Don't build functionality until it's required |
| [Small Functions](clean-code/small-functions.md) | Short, focused functions that do one thing (~15 lines) |
| [Guard Clauses](clean-code/guard-clauses.md) | Exit early on invalid states; keep the happy path flat |
| [Decide, Don't Cope](clean-code/decide-dont-cope.md) | Decide types once at the boundary; delete downstream type-sniffing ladders |
| [Cognitive Load](clean-code/cognitive-load.md) | Minimize mental effort to read code; named intermediates over clever conditions |
| [Cyclomatic Complexity](clean-code/cyclomatic-complexity.md) | A testability metric — read as a locator, never optimized as a target |
| [Single Level of Abstraction (SLAP)](clean-code/slap.md) | Each function operates at one level of abstraction |
| [Self-Documenting Code](clean-code/self-documenting-code.md) | Names and structure over comments; comments for why only |
| [Documentation Discipline](clean-code/documentation-discipline.md) | Where docs live; which comments earn their place |
| [Elegance](clean-code/elegance.md) | Minimality, accomplishment, modesty, revelation |
| [Legibility](clean-code/legibility.md) | Navigable codebase: followable call paths, discoverable entry points, honest names |
| [Patchwork](clean-code/patchwork.md) | Compensating code you cannot simplify by deleting — re-decide the interface, don't trim the guards |
| [An Unclaimed Guarantee](clean-code/unclaimed-guarantee.md) | Tells: a second handle beside an existing owner — an added `WithCancel`/`done`/returned cleanup beside a `ctx`, a lock beside a transaction, a retry loop beside a retry client. For every one you see: name the guarantee it adds and the caller that would be wrong without it, then **delete it or claim it**. No claimant is the finding |
| [Principle of Least Surprise](clean-code/least-surprise.md) | Components behave the way users expect |
