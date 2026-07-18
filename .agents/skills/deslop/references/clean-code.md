---
name: deslop-clean-code
description: Deslop principles, Part I: Clean Code — KISS, YAGNI, Small Functions, Guard Clauses, Decide Don't Cope, Cognitive Load, SLAP, Self-Documenting Code, Documentation Discipline, Elegance, Least Surprise.
---

# Part I: Clean Code

Write clear, simple, readable code. Do less, but better. Reduce complexity, and make the code easily readable.

Each principle is a self-contained file; read every file when auditing this layer.

| Principle | What it says |
|-------------|----------------|
| [KISS: Keep It Simple, Stupid](clean-code/kiss.md) | Simplest sufficient code; watch parts plethora, over-abstraction, overengineering |
| [YAGNI: You Aren't Gonna Need It](clean-code/yagni.md) | Don't build functionality until it's required |
| [Small Functions](clean-code/small-functions.md) | Short, focused functions that do one thing (~15 lines) |
| [Guard Clauses](clean-code/guard-clauses.md) | Exit early on invalid states; keep the happy path flat |
| [Decide, Don't Cope](clean-code/decide-dont-cope.md) | Decide types once at the boundary; delete downstream type-sniffing ladders |
| [Cognitive Load](clean-code/cognitive-load.md) | Minimize mental effort to read code; named intermediates over clever conditions |
| [Single Level of Abstraction (SLAP)](clean-code/slap.md) | Each function operates at one level of abstraction |
| [Self-Documenting Code](clean-code/self-documenting-code.md) | Names and structure over comments; comments for why only |
| [Documentation Discipline](clean-code/documentation-discipline.md) | Where docs live; which comments earn their place |
| [Elegance](clean-code/elegance.md) | Minimality, accomplishment, modesty, revelation |
| [Principle of Least Surprise](clean-code/least-surprise.md) | Components behave the way users expect |
