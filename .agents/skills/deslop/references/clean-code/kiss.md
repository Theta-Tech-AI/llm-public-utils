---
name: deslop-clean-code-kiss
description: Deslop principle — KISS: Keep It Simple, Stupid: Simplest sufficient code; watch parts plethora, over-abstraction, overengineering.
---

# KISS: Keep It Simple, Stupid

> Worked example: [case-study-simplification-agent-fleet.md](../case-study-simplification-agent-fleet.md) — a production deslop pass that collapsed a per-section LLM agent fleet, a duplicated prompt fragment, and a prose-policing regex into one agent, one preamble, and zero regexes.

> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."
> — Antoine de Saint-Exupéry

Complexity kills maintainability, and simple does not necessarily equal easy - simple systems may require skill to build. Aim for the simplest sufficient code - neither incomplete nor over-engineered code.

To avoid unnecessary complexity, look for:

- **Parts Plethora:** Too many parts in the system
- **Interconnectedness:** Too many coupled components.
- **Extra Effort:** Easy tasks should require minimal effort.
- **Cyclomaticism:** Many independent paths through the code
- **Cognitive Complexity:** High mental effort to understand code. Can a new junior dev understand the code upon a glance?
- **Over-Abstractions:** Single-implementation interfaces, factories of factories, deep inheritance, "clever" one-liners.
- **Rationalizations:** Look for violations where it seems coder said to themself: *"This pattern will be useful when..."*, or *"Let me make this more flexible..."*, or *"This is the proper enterprise way..."*
- **Overengineering:** Nested ternaries, cleverness over clarity, premature optimization, caching before profiling, interfaces for single implementations, or speculative generality.
-  **Ego:** Spots where the coder was trying to impress instead of communicate plainly.
