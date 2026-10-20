---
name: deslop-architecture-coercion-is-a-boundary
description: Deslop principle — Coercion Is a Boundary, Not a Helper: a private `_truthy`/`_int`/`_first_nonempty` that turns a raw representation into a domain type is proof the boundary was never built, and every call site is guessing what the input meant.
---

# Coercion Is a Boundary, Not a Helper

> "Why is there a `_truthy`? Because nothing in this program is a `bool`."
> — the reading that motivated this principle

A helper whose parameter is the *wire* type and whose return is the *domain* type is a codec. Codecs belong
to the boundary that receives the data — the config loader, the HTTP edge, the CLI parser — and run there,
once, against a type that remembers the answer. A private `_truthy` in the middle of a consumer is that codec
written by someone who did not own the boundary and did not have one to call.

```python
# ❌ No boundary exists, so every read site re-decides what the input meant
def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}

def _first_nonempty(env: Mapping[str, str], *names: str) -> str | None:
    for name in names:
        value = env.get(name)
        if value and value.strip():
            return value.strip()
    return None

use_managed_identity = _truthy(os.getenv("AZURE_OPENAI_USE_MANAGED_IDENTITY"))
stream = _truthy(os.getenv("STREAM"))

# ✅ One parse at the boundary, one type the rest of the program can trust
@dataclass(frozen=True)
class ProviderSettings:
    use_managed_identity: bool
    stream: bool

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}

def _parse_bool(name: str, raw: str) -> bool:
    token = raw.strip().lower()
    if token in _TRUE:
        return True
    if token in _FALSE:
        return False
    raise ValueError(f"{name}: expected a boolean, got {raw!r}")

def load_provider_settings(env: Mapping[str, str]) -> ProviderSettings:
    return ProviderSettings(
        use_managed_identity=_parse_bool(
            "AZURE_OPENAI_USE_MANAGED_IDENTITY", env.get("AZURE_OPENAI_USE_MANAGED_IDENTITY", "false")
        ),
        stream=_parse_bool("STREAM", env.get("STREAM", "true")),
    )
```

The ❌ version is not merely loose typing. It is three failures stacked, and each one is independently
reportable:

- **Loose type.** The signature says `str | None` where the concept is `bool`, so the helper is asked to
  *guess what was meant* rather than receive what was decided. The ambiguity is real, and it has been moved
  from the edge (where it is legitimate and has one owner) into every caller (where it has none).
- **Ambiguity resolved by guess, silently.** `_truthy("maybe")` is `False`; `_truthy("Enabled")` is `False`;
  a typo in a deployment variable turns a feature *off* with no log line and no exception. A definite answer
  was manufactured for an indefinite input — the input was never parsed, only interrogated.
- **Placed in the wrong module.** A private codec inside a consumer means the next consumer writes its own.
  Two `_truthy` functions with two truth tables (`{"1","true","yes","on"}` vs `{"true","TRUE","1"}`) is a
  fork of the definition of "true", created the moment the second file is saved — and it is invisible to
  clone scanners the day the tables differ by one word.

## The second face: sniffing an identifier that already has a type

Same disease, different costume — a string inspected for meaning that a typed value should have carried:

```python
# ❌ The caller must pass a model id and trust a prefix table
def _supports_custom_temperature(model_id: str) -> bool:
    return not model_id.lower().startswith(("gpt-5", "o1", "o3", "o4"))

# ✅ The capability is a property of the model, decided once where models are known
@dataclass(frozen=True)
class ModelCapabilities:
    supports_custom_temperature: bool

CAPABILITIES: Mapping[str, ModelCapabilities] = {...}   # the closed set, in one place
```

Prefix matching on an identifier derives a *capability* from a *name*. It silently misfires the moment a
deployment alias differs from the model id, a new family ships under a colliding prefix, or the same model is
reached by a fully qualified path. If the set is closed, it has a home; if the set is open, the boundary
decides and returns the typed answer.

## Prior art — what is already named, and what is ours

The smells underneath this have names; the label on this file is ours. Claiming otherwise would be the slop it
describes.

| Named concept | Source | How it relates |
|---|---|---|
| **Boolean blindness** | coined by **Dan Licata** (CMU, as a PhD student), recorded by **Robert Harper**; catalogued as a code smell by Jerzyk (2022) | A `bool` carries no information beyond its value — to use it you must remember its provenance (McBride). Here blindness begins *earlier*: the value is still a `str`, and provenance has not been established at all. |
| **Stringly typed / primitive obsession** | Fowler, *Refactoring* (primitive obsession); "stringly typed" as the pejorative for carrying everything as `str` | The representation riding around as `str \| None` instead of the domain type. |
| **Shotgun parsing** | Alexis King, *Parse, Don't Validate* (2019) | The check scattered per call site instead of parsed once — what `_truthy` performs at every read. |
| **Typed settings parsed once at startup** | 12-factor config; `pydantic-settings` `BaseSettings` as the mainstream Python form | The standard repair for the config case: one parse, one typed object, everything downstream reads a `bool`. |

**What this file adds, and does not claim as prior art:** the *artifact* is the finding. Existing vocabulary
names the type disease (primitive obsession) and its symptom (boolean blindness), but leaves the repair to
judgement; nothing names the private codec helper as the thing to hunt for, nor states that its presence is
evidence a boundary was never built. The six diagnostics below, and the rule that the helper is deleted rather
than tightened, are this library's own framing.

## Diagnostics

Ask these of every `_`-prefixed function that returns `bool`, `int`, `float`, an enum, or `Path`:

1. **Signature split test** — is the parameter the representation (`str`, `str | None`, `dict[str, str]`,
   `Any`) while the return is the domain type? That is a codec. Does the boundary that received the data
   own it, or is it a copy living downstream?
2. **Sole-purpose test** — if its whole body is `strip().lower() in {...}`, `int(x or 0)`, or a first-match
   loop over `*names`, the function exists only to re-derive a decision. The decision belongs in one place.
3. **Silence test** — what does it return for `""`, `"  "`, `"maybe"`, `"Enabled"`, `"0x1"`? A definite value
   for an indistinct input is a laundered failure, not a convenience.
4. **Frequency test** — grep the tree for the *concept* (`truthy`, `to_bool`, `as_bool`, `env_bool`,
   `_first_nonempty`, `int(os.getenv`). One occurrence is slop; three occurrences with different sets is a
   missing settings type plus a DRY violation.
5. **Annotation test** — does the domain type appear in any signature at all? If no field is `enabled: bool`
   and no parameter is `stream: bool`, the program has no booleans; it has strings it re-reads.
6. **Prefix test** — for a string sniff: is this identifier matched against a closed set already enumerated
   somewhere else in the codebase? If yes, the answer should have been looked up, not inferred.

## Boundaries

This is not "validate all input" and it is not "ban helper functions". A parser that returns the domain type
at the edge is the goal, not the violation; and a boundary may legitimately accept `"yes"` as well as
`"true"` — that tolerance is a *policy*, stated once, in the code that owns the setting. A prototype reading
one env var honestly does not need a settings dataclass; it needs to not ship the shortcut into a service.

| Principle | Relationship |
|-----------|--------------|
| [**Parse, Don't Validate**](parse-dont-validate.md) | The doctrine. This is the diagnostic that finds the code that never reached the boundary at all — the coercion helper is what validation looks like when no parser was built. |
| [**No Silent Defaults**](../reliability/no-silent-defaults.md) | `os.environ.get("HOST", "localhost")` synthesises absence; `_truthy(unrecognized)` synthesises a *decision*. Same laundering, one step further. |
| [**Fail-Fast**](../reliability/fail-fast.md) | An unparseable `bool` must raise at the boundary rather than become `False` three layers in. |
| [**Single Source of Truth**](single-source-of-truth.md) | Two `_truthy` helpers are two authoritative definitions of one datum — which tokens mean "on". |
| [**One Logical Unit, One Home**](one-logical-unit-one-home.md) | The unit here is "parse this setting"; its home is the config module, and it currently has none. |
| [**Patchwork**](../clean-code/patchwork.md) | A coercion helper is compensating code: it exists to fix a value that should already have been the right type. |
| [**Encapsulation**](encapsulation.md) | The setting's knowledge — its names, defaults, and accepted tokens — is in the consumer instead of behind the object that owns it. |

## Summary

1. **A helper that converts a raw representation into a domain type is a codec, and a codec without a
   boundary is proof the boundary was never built.** Find it by the signature: wire type in, domain type out.
2. **The function is the evidence, not the crime.** Its existence means the unparsed value escaped the edge
   and every read site is re-deciding what it meant — so the repair parses once and deletes the helper, it
   does not tighten the helper.
3. **Resolving ambiguity by guess is a silent default.** An unrecognised token becoming `False` is a failure
   laundered into a definite answer; the boundary raises instead.
4. **Privately placing it forks the definition.** The second consumer writes a second truth table, and the
   two diverge by one word without any clone tool noticing.
5. **Sniffing a name where a type belongs is the same slop** — capability derived from a prefix will misfire
   silently, and a closed set already has a home to be looked up in.
