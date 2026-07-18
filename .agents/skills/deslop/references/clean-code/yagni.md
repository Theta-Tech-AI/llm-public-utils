---
name: deslop-clean-code-yagni
description: Deslop principle — YAGNI: You Aren't Gonna Need It: Don't build functionality until it's required.
---

# YAGNI: You Aren't Gonna Need It

> "Always implement things when you actually need them, never when you just foresee that you need them."
> — Ron Jeffries, XP co-founder

YAGNI is the discipline of **not building functionality until it's required**. Every feature has costs: development, testing, debugging, maintenance, cognitive load, delays, complexity, drift. Features you don't need yet carry these costs without delivering value. Common violations and code smells includes config options no one uses, ABC with one implementation, extensibility points never extended, commented "future" code, or unused API endpoints. Before adding code: **Who needs this today?** (not "might need") — **What breaks without it?** (if nothing, skip it) — **Can we add it later?** (usually yes, with better understanding). Only build what's needed now, delete speculative code, and keep code malleable and maintainable.

**The trap**: *"While I'm here, just in case I need it later, I'll just add..."*

**The reality**: Most speculative features fail to improve their target metrics.
