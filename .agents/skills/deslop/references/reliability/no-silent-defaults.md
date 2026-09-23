---
name: deslop-reliability-no-silent-defaults
description: Deslop principle — No Silent Defaults: model absence, never synthesize a plausible value for it.
---

# No Silent Defaults

> "Errors should never pass silently. Unless explicitly silenced."
> — Tim Peters, The Zen of Python (PEP 20)

A signature is a claim about what comes back. When the honest answer is *there isn't one*, the code must
say so — not manufacture something of the right type. `return ""`, `?? "unknown"`, `or []`,
`catch { return [] }`, `os.environ.get("HOST", "localhost")`: each hands the caller a value that satisfies
the type checker and privately means *we could not find out*.

The caller cannot tell that apart from a genuine empty string, a genuinely unknown name, or a real
localhost. The failure is not lost; it is **laundered** — it resurfaces later, somewhere without the
context that could explain it, as wrong behaviour rather than as an error.

This is the failure no harness reports. Nothing threw, nothing crashed, every test passed. That is
precisely the point: a silent default is how a misconfiguration becomes a plausible production state.

## The three tells

- **The synthesized literal.** A branch that returns a constant of the declared type for a case the type
  cannot express: `return ""`, `return 0`, `return []`, `return "unknown"`, `return False`. Ask of each:
  could the caller distinguish this from a real answer? If not, it is a lie with a good type.
- **The coalescing swallow.** `value or fallback`, `value ?? fallback`, `dict.get(k, default)`,
  `try: ... except: return default`. The value is replaced by the fallback *whenever it is falsy*, which is
  not the same condition as *absent*.
- **The fail-open default.** A default that lets the system proceed is worse than one that stops it. A
  timeout that defaults to permissive, a permission check that defaults to allowed, a required key that
  defaults to a placeholder — each converts "we did not know" into "we decided, generously".

## The falsy trap

The coalescing swallow has a second victim that has nothing to do with absence:

```python
# ❌ A configured 0, an empty-but-deliberate string, and False are all overwritten.
timeout = config.get("timeout") or 30          # config said 0 ("no timeout") → silently 30
label   = options.get("label") or "default"    # an explicit "" is a valid label → silently replaced
retries = settings.get("retries") or 3         # 0 (never retry) → silently 3
```

Nothing is missing here. The values are present and deliberate, and the `or` discards them because falsy
and absent were conflated. `if k not in d` / `d.get(k)` / `??` distinguish them; `or` does not.

## Diagnosis

1. **Does the type admit absence?** If the signature promises `str`/`int`/`list`, either the value is
   genuinely always derivable — prove it — or the signature is stating something the body cannot keep.
   A `str` that is sometimes unavailable is a contract defect, not a style question.
2. **Is the substituted value distinguishable downstream?** Trace the returned value to its first
   consumer. If the consumer cannot tell the defaulted case from the real one, that consumer is where the
   wrong behaviour will be attributed later.
3. **Which direction does the failure fall?** For each default, ask what happens when it is wrong: does
   the system stop, or does it continue in a state nobody chose? Fail-open defaults are the expensive ones.
4. **Grep the shapes.** `return ""`, `or []`, `?? "`, `\.get\([^)]*,\s*("|\[|0|False)`, `catch.*return`,
   `os\.getenv\([^)]*,` — then check each hit for whether absence was actually representable.

## The repair

Absence is a state, so model it as one. Pick per case, not per preference:

- **Required, but missing** → raise at the boundary, where the context still exists. This is
  [fail-fast](fail-fast.md) applied to a value that has no valid substitute.
- **Genuinely optional** → say so in the type — `Optional[T]`, `T | None`, `Option<T>` — and let every
  consumer be forced to decide what it does about the missing case. The compiler becomes the checklist.
- **Optional with a real default** → make the default an explicit, named, deliberate policy
  (`DEFAULT_TIMEOUT_SECONDS = 30`) applied where absence is *proved*, not where a value merely looks falsy.
- **Absent as a normal outcome** → return a shape that carries the reason: a `Result`/`Refusal` union, a
  status enum, a third state. A caller that must handle "insufficient evidence" cannot forget to.

For arguments where `None` itself is a meaningful value, use a dedicated sentinel singleton (PEP 661 exists
for exactly this) so that *not provided* and *provided as nothing* stop being the same thing.

## Before and after

```python
# ❌ Three shapes guessed, and every failure answered with "" — indistinguishable
#    from a tool genuinely called "".
def _tool_name(tool: object) -> str:
    if isinstance(tool, dict):
        name = tool.get("name")
        if isinstance(name, str):
            return name
        function = tool.get("function")
        if isinstance(function, dict) and isinstance(function.get("name"), str):
            return str(function["name"])
        return ""                                   # absence laundered as a value
    return str(getattr(tool, "name", "") or "")     # default and `or` — the same cope twice
```

```python
# ✅ Parse the shape once at the boundary, and let absence be absent.
@dataclass(frozen=True)
class ToolName:
    value: str

def parse_tool_name(tool: object) -> ToolName | None:
    """Return the tool's name, or None if this object does not declare one."""
    name = tool.get("name") if isinstance(tool, dict) else getattr(tool, "name", None)
    if name is None and isinstance(tool, dict) and isinstance(tool.get("function"), dict):
        name = tool["function"].get("name")
    return ToolName(name) if isinstance(name, str) and name else None
```

The caller now must decide what a nameless tool means — skip it, refuse the run, log it — in the place that
has the information to decide. Two secondary defects evaporate with it: the inline shape ladder belongs to
a boundary parse ([decide-dont-cope](../clean-code/decide-dont-cope.md)), and `str()` applied to a value
already proved `isinstance(str)` was distrust made visible.

## Where this is not the answer

Not every default is a sin. Version fallbacks, feature flags, and compatibility shims apply a documented
policy to a condition the system has already declared acceptable. The test is not "is there a default"
but **"could this value only be produced by us not knowing something?"** If yes, say so in the type.

In relation to other principles, no silent defaults completes the error-handling family:

| Principle | Relationship |
|-----------|--------------|
| [**Fail-Fast**](fail-fast.md) | Covers errors you can *detect*. This covers the case that is undetectable because absence became a valid value before anyone looked. |
| [**Design by Contract**](design-by-contract.md) | The contract is what absence must respect: a postcondition that promises `str` is the defect |
| [**Parse, Don't Validate**](../architecture/parse-dont-validate.md) | The mechanism — parse once at the boundary into a type that admits the missing case |
| [**Postel's Law**](postels-law.md) | The most-quoted justification for this sin, misapplied: tolerant of *unknown* fields means strict about *required* ones |
| [**Principle of Least Surprise**](../clean-code/least-surprise.md) | A caller that cannot distinguish absence from a value is being surprised, quietly |
| [**Decide, Don't Cope**](../clean-code/decide-dont-cope.md) | Every default is a question the author declined to answer, converted into a runtime value |

## Summary

1. **Absence is a state, not a value.** Substituting a plausible value does not handle it — it hides it.
2. **The tell is indistinguishability**: no downstream caller can tell the defaulted case from a real one.
3. **`or` conflates falsy with absent**; `0`, `""` and `False` are values, and they get discarded too.
4. **Check the direction of failure.** A default that lets the system proceed is the expensive kind.
5. **Repair by modelling**: raise when required, `Optional` when genuine, a named policy where a default is
   real, a result type when absence is a normal outcome.
