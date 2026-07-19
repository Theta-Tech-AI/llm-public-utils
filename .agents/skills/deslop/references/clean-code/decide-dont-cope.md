---
name: deslop-clean-code-decide-dont-cope
description: Deslop principle — Decide, Don't Cope: Decide types once at the boundary; delete downstream type-sniffing ladders.
---

# Decide, Don't Cope

The most common shape of AI-generated slop is not a bad algorithm — it is a **coping mentality**. Generated code treats every input as a hostile mystery and copes with it locally: it accepts `unknown`, then builds an if/else-if ladder of `typeof` checks, `instanceof` tests, inline casts, try/catch rungs, and stacked fallbacks until *something* produces a usable value. Every rung handles a hypothetical ("what if it's an object with a message? what if stringify throws?") that no requirement ever asked for. The code optimizes for "never crash on any conceivable input **here**" instead of "invalid input cannot **reach** here."

Wise architecture inverts this. Somewhere, exactly once, a boundary **decides** what is allowed — normalizes or rejects — and everything downstream trusts that decision and stays on the happy path. The reviewer's question is never "are these branches clean?" but "**why does this function believe it can receive anything at all?**"

This is a mentality, not a typing trick. Stricter type annotations on the same coping code just move the casts around. The fix is architectural: pick the one place where the value enters the system, make it produce the right shape, and delete every downstream accommodation.

**The deeper unwisdom: refusing to make claims about the world.** Coping code is what a mind produces when it declines to commit to any statement about its own system. Every rung of a ladder is a question the author refused to answer — *can this value actually be a non-string here? should it ever be?* — converted into a runtime branch that every future reader must now answer instead, forever. Three failure modes of judgment drive it, in humans and in LLMs alike:

1. **Local completion over global design.** The author's frame is "make *this snippet* survive anything so I can be done here," never "should this situation exist at all?" Adding a branch requires zero understanding of the surrounding system; changing a contract requires owning one. Branches are cheaper to *write*; decisions are cheaper to *own* — and slop authors always buy the former.
2. **Blame-avoidance masquerading as robustness.** A crash looks like the author's failure; quiet complexity doesn't. So the code appeases: it accepts everything, asserts nothing, and holds no opinion about what is valid. That is tolerance, not robustness. Real robustness is a clear contract enforced loudly — a system that says "this cannot happen, and if it does, you will hear about it immediately" is more reliable than one that silently absorbs garbage and keeps going in an undefined state.
3. **Deferred decisions compounding as entropy.** An unmade decision does not disappear — it becomes control flow. Most incidental complexity in a codebase is the fossil record of decisions nobody made: every "what if"-shaped branch, every `?? fallback ?? fallback`, every catch-and-continue is a commitment someone dodged, paid for on every subsequent read.

The corrective habit: treat every speculative branch as a **claim you are refusing to make** — then make it. Assert the invariant, enforce it at the boundary, and let violations fail fast and loud. Code written by a mind willing to be wrong *once, at the edge, visibly* is always simpler than code written by a mind hedging everywhere, invisibly.

**The canonical tell: the coercion ladder.** A mutable accumulator threaded through a chain of runtime type interrogation. Here is one from a real AI-generated error handler:

```typescript
// ❌ Slop — copes inline: accumulator, four guessed shapes, three stacked fallbacks
if (error instanceof ProgramThrow) {
  const value = error.value
  let message: string
  if (containsRuntimeReference(value)) {
    message = "a non-data value"
  } else if (typeof value === "string") {
    message = value
  } else if (
    value !== null &&
    typeof value === "object" &&
    typeof (value as { message?: unknown }).message === "string"
  ) {
    message = (value as { message: string }).message
  } else {
    try {
      message = JSON.stringify(copyOut(value)) ?? String(value)
    } catch {
      message = String(value)
    }
  }
  return { kind: "ExecutionFailure", message: `Uncaught: ${message}` }
}
```

The reflexive cleanup — and why it is not the fix — is to put the ladder inside a function. Look at what that function IS: its signature admits it will cope with anything, and its body is nothing but the coping:

```typescript
// ⚠️ Still slop, now tidier — the function's signature accepts anything,
// so its body must guess four shapes and stack three fallbacks.
function executionFailure(value: unknown): ExecutionFailure {
  let message: string
  if (containsRuntimeReference(value)) {
    message = "a non-data value"
  } else if (typeof value === "string") {
    message = value
  } else if (
    value !== null &&
    typeof value === "object" &&
    typeof (value as { message?: unknown }).message === "string"
  ) {
    message = (value as { message: string }).message
  } else {
    try {
      message = JSON.stringify(copyOut(value)) ?? String(value)
    } catch {
      message = String(value)
    }
  }
  return { kind: "ExecutionFailure", message: `Uncaught: ${message}` }
}
```

Now the same function in a wisely-architected codebase — the only change is that callers are required to supply the right type, and the entire body evaporates:

```typescript
// ✅ Correct — same function, input required to be a string.
// Twenty-six lines of guessing become one line of doing.
function executionFailure(message: string): ExecutionFailure {
  return { kind: "ExecutionFailure", message: `Uncaught: ${message}` }
}
```

Where did the ladder go? Nowhere — **it ceased to exist.** The one legitimate conversion (a thrown value into a policy-checked string) happens once at the throw boundary, where the raw value actually enters the system and where the redaction rule naturally lives. Every function past that boundary takes `message: string` and simply does its job. The consumer collapsed not because the branches were cleaned, but because they can no longer be needed. That is the difference between putting coping code inside a function and architecting so the function has nothing to cope with: compare the two `executionFailure` signatures — `(value: unknown)` is a confession that the codebase never decided what a thrown value is; `(message: string)` is the decision.

How to review for it:

1. **Trace the `unknown` upstream.** When you meet a type-sniffing ladder, find where the value was last known-good. If any code you own touched it between there and here, the fix belongs at that touchpoint, not here.
2. **Count the shapes the code guesses.** Each guessed shape (string? object-with-message? JSON-able? unstringifiable?) is a speculative requirement. If no caller actually produces it, the branch is YAGNI bloat — delete it and let the boundary reject.
3. **One decision point per value.** If two places both interrogate the same value's type, one of them is coping with the other's indecision. Merge them at the earlier one.
4. **Extraction is the fallback, not the fix.** Only when the boundary is genuinely foreign — a wire format, a third-party API, user-thrown JS values you cannot intercept — does the coercion belong in your code, and then in exactly one named, tested function with a comment saying whose mess it absorbs.

In relation to other principles, decide-don't-cope draws on...

| Principle | Relationship |
|-----------|--------------|
| [**Parse, Don't Validate**](../architecture/parse-dont-validate.md) | The mechanism: convert once at the boundary; downstream never re-interrogates |
| [**YAGNI**](yagni.md) | Every guessed shape is a requirement nobody stated |
| [**KISS**](kiss.md) | One required type beats four hypothetical ones |
| [**Fail-Fast**](../reliability/fail-fast.md) | Rejecting at the boundary beats coping in the interior |
| [**Design by Contract**](../reliability/design-by-contract.md) | The boundary's decision IS the contract; consumers assume it holds |
| [**Single Level of Abstraction**](slap.md) | Coping code mixes policy, dispatch, and formatting at one level |
