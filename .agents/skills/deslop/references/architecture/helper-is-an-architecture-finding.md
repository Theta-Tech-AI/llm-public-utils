---
name: deslop-architecture-helper-is-an-architecture-finding
description: Deslop principle — A Helper That Must Exist Is an Architecture Finding: when a private function exists to reconcile a value with the shape the system expects, the finding is not the helper and not its type — it is that nothing in the architecture owns that value's life, so the repair assigns the owner instead of tidying the helper.
---

# A Helper That Must Exist Is an Architecture Finding

> "A properly architected system wouldn't need this helper function in the first place."
> — the correction that produced this principle

Read any private helper that exists to make a value usable — `_truthy(value)`, `_first_nonempty(env, *names)`,
`_normalize_key`, `_coerce_int_or_zero`, `_supported_by_prefix(id)` — and the question is not "is this function
well written?". It is **"what would have to be true about this system for this function to be unnecessary?"**
The answer is always an architectural fact that is missing: something should have owned the value between the
moment it entered the system and the moment it was used, and nothing did. The helper grew in that gap.

```python
# ❌ Four helpers, one missing owner: no layer decides what a setting *is*
def _truthy(value: str | None) -> bool: ...
def _first_nonempty(env: Mapping[str, str], *names: str) -> str | None: ...
def _supports_custom_temperature(model_id: str) -> bool: ...   # capability sniffed from a name
def _normalize_region(region: str | None) -> str: ...          # "" means the default, apparently

use_managed_identity = _truthy(os.getenv("USE_MANAGED_IDENTITY"))
region = _normalize_region(_first_nonempty(os.environ, "REGION", "AZURE_REGION"))
temperature_ok = _supports_custom_temperature(model_id)

# ✅ One owner: configuration decides once, and the rest of the program receives decisions
@dataclass(frozen=True)
class ProviderSettings:
    use_managed_identity: bool
    region: Region
    capabilities: ModelCapabilities

def load_provider_settings(env: Mapping[str, str]) -> ProviderSettings:   # the only place env is read
    ...
```

The helpers in the ❌ version are not badly written; `_truthy` is correct, `_first_nonempty` is careful. They
are **load-bearing patchwork**: they exist because the architecture terminated configuration at "a dictionary of
strings" and never built the component whose job is to turn that dictionary into decisions. Nothing owns the
setting, so every consumer improvises — and each improvisation is locally reasonable and jointly incoherent.

## One is enough

**The finding fires on a single instance.** Duplication is corroboration, never the criterion: a helper is
pointless because of *why it must exist*, not because there are two of it. If the value had been parsed at the
seam it entered — a `bool`, a `Region`, a capability, a resolved credential — the function would have nothing
left to do, and that is true whether the codebase contains one copy or nine.

Two corollaries the audit must obey:

- **Never downgrade a lone helper for being "only used in one place".** The single call site is the proof, not
  the mitigation: the value crossed a boundary still raw, and one consumer is reconciling what should never
  have arrived in that shape.
- **Never wait for a second copy before filing it.** Waiting is how the fork happens: the second consumer
  arrives, writes its own version with a slightly different token set, and now the finding looks like
  duplication and gets fixed as duplication — leaving both versions where they are.

This is also why "the repo already has one of these" is not the end of the analysis (see the signature test
below): sharing an owner that the caller cannot reach still leaves the value unparsed at the point of use.

## The test

Do not audit the helper. Audit its absence:

1. **Reverse test** — delete the helper and repair the call sites. If the repair is "add the same helper
   somewhere else", the architecture changed nothing and the finding stands. If the repair is "one module now
   decides, and six call sites receive a decision", you have found the component the design was missing.
2. **Owning-module test** — name the module with the authority to answer this question. If the answer is "none",
   the decision is unowned, and every helper is a separate vote on what it means.
3. **Authority-duplication test** — *corroboration only, never the trigger.* Would a second consumer write this
   function? Two token sets for one concept mean the fork has already happened, which strengthens a finding you
   should already have from test 1. Use it as evidence, never as the reason.
4. **Layer test** — how far is the helper from where the value entered? A codec at the edge is doing its job; a
   codec four layers in is a message that the edge did not finish its work and nobody noticed.
5. **Reversibility test** — what does the helper do with input it cannot interpret (`"maybe"`, an unknown model
   name, a region nobody offers)? If it manufactures a value instead of raising, the missing owner is not merely
   absent, it is being impersonated at the read site.
6. **Family check** — grep for the *shape* rather than the subject: `_`-prefixed, one or two parameters, returns
   a domain type, body is normalising. Where they cluster in one file, that file is standing in for a component.
7. **Bypass test** — does the codebase already own this decision somewhere (a util module, a catalog, a domain
   type)? Then the finding is that the consumer was free to ignore it. Report the bypass, not merely the
   duplication.

## Detection — census the inputs, never scan for names

A principle an agent must *remember to apply* will be missed by an agent scanning for behaviour bugs. But the
correction is not a list of function names: a grep for `_truthy` finds `_truthy` and misses `_as_flag`,
`_setting_switch`, `_resolve_capability` and every name invented after the list was written. Name-matching is
the same fitted detector this library refuses elsewhere — it encodes the instance and not the rule.

**Trigger and criterion are different things, and neither may be mistaken for the other.** The criterion is
architectural — a raw value reached a consumer that had to interpret it. The *trigger* is whatever makes that
visible on sight, and a cheap sighting aid is legitimate even when it is evidence rather than proof: the same
`env.get("NAME", default)` appearing in several files, a set of literal tokens sitting in a consumer, an
identifier tested with `startswith`. Removing a hook because it is not the criterion costs recall — measured: a
row that led with "one instance is enough" and dropped the repeated-across-files hook stopped surfacing a lone
helper, while rows carrying it surfaced it twice. Keep the hook, label it a hook, and never let it decide
whether the finding is real.

**The instrument is a census.** For every external input the target consumes — environment variables, request
bodies, query params, database rows, provider payloads, file contents — answer:

1. **Where does it enter?** The seam: a constructor parameter, a request handler, a loader, a reader.
2. **Which single component turns it into a decision or a domain value?** Name it. If you cannot, that is the
   finding ("no owner"). If you can, but consumers re-interpret the same input anyway, that is the other shape
   ("owner exists, nothing enforces its use").
3. **How many places interpret it again afterwards?** Count them. Two is already a finding; three is a design
   that never had a boundary.

The tell is **structural and needs no vocabulary**: a consumer holding the vocabulary of a decision instead of
asking its owner — a set of literal tokens compared against a string, a `startswith` on an identifier that names
a thing, a first-non-empty scan over alternative spellings of one setting, a literal default sitting beside a
lookup. Where those appear, ask what component should have answered and why the caller could not ask it.

Report the result even when it is the least interesting finding in the pass: an unowned input outranks a tidy
bug, and it will not be found by anyone else's tool.

## The forest: instances of one disease

| Helper | The value nobody owned | The component that was missing |
|---|---|---|
| `_truthy(str \| None)` | a setting, decided per read site | settings/config loader returning typed decisions |
| `_first_nonempty(env, *names)` | precedence between aliases of one setting | the same loader, holding the alias table |
| `_supports_custom_temperature(model_id.startswith(...))` | what a model *is* when only its name travels | a model registry returning capabilities |
| `_normalize_region(str \| None)` | "empty means default" as tribal knowledge | the domain type (`Region`) with parsing at its constructor |
| `_coerce_int_or_zero(text)` | whether absence is zero or an error | the parser at the boundary, with a stated policy |
| `_get_or_default(d, k, v)` | who may invent a missing value | the caller's contract, or a type that cannot be partial |

The type-level reading (primitive obsession, "stringly typed", boolean blindness) describes the *symptom* in
the value's type. The architectural reading describes the *cause*: no component owns the transition from
external representation to internal decision. Fixing the type without placing the owner converts
`_truthy(str) -> bool` into `_parse_bool(str) -> bool` in the same wrong file, and the next consumer writes
`_parse_bool` again. Fixing the owner deletes the helper as a consequence.

## The repair

**Assign the owner, then let the type follow** — this order matters, because the type is the vehicle and the
owner is the fix.

- Name the component that owns the decision: config loader, model registry, request parser, domain constructor.
  Put it where the value enters, or where the closed set of answers is known.
- Terminate the raw representation at that seam: no `str | None` for that concept exists past it. Not a policy
  anyone must remember — a fact the next reader cannot avoid.
- State the ambiguity policy once (which tokens are accepted, what absence means, what an unrecognisable value
  does), in the owner, and make the unresolvable case raise.
- Delete every helper the owner makes unnecessary **in the same change**, and let the deletion be the evidence
  the architecture improved. A refactor that leaves the helpers in place did not fix the system.

The generalisation worth carrying: **helpers are where architecture leaks.** A helper that reconciles a value
with the shape the system expects is a marker of a seam nobody built. Tidy it and you have hidden the marker.

## Boundaries

This is not "no helper functions". Extraction for readability — naming a complex expression, decomposing a long
function, isolating a side effect — is *within* a component that already owns its subject. The finding needs the
value to be **foreign**: created elsewhere, in a shape the consumer must reconcile. Nor is this a demand for
`Pydantic` or a settings class specifically; the owner may be a plain function whose return type is not a string.
Small scripts are exempt only until they become services.

| Principle | Relationship |
|-----------|--------------|
| [**One Logical Unit, One Home**](one-logical-unit-one-home.md) | The same rule seen from the other side: that one names the unit that has drifted; this names the unit that was never created, detected through the helpers squatting in its place. |
| [**Parse, Don't Validate**](parse-dont-validate.md) | Supplies the *repair mechanism* — parse once into a precise type. This supplies the *finding and its location*: who is missing, not what type to use. |
| [**DRY**](dry.md) | Names the copy and its usual repair — delete the duplicate, call the shared one. Reach for this principle when that repair is *possible*; when the shared implementation's seam does not fit the caller's, the finding has moved up a level and DRY alone will prescribe a change that cannot be made. |
| [**Single Source of Truth**](single-source-of-truth.md) | Two helpers answering one question are two sources of truth; the cause is one missing owner, and fixing only the duplication leaves the owner missing. |
| [**Patchwork**](../clean-code/patchwork.md) | The general theory this is a sharp instance of: compensating code you cannot simplify by deleting. This adds the architectural reason it cannot be deleted — deletion requires building the owner. |
| [**No Silent Defaults**](../reliability/no-silent-defaults.md) | What the impersonating helper does when the owner is absent: manufactures a value from absence or nonsense. |
| [**Modularity**](modularity.md) | A deep module hides one decision. Here the decision is hidden nowhere, so it is re-decided in every consumer. |
| [**Fail-Fast**](../reliability/fail-fast.md) | The owner raises where the helper guesses; the venue for the failure is the seam, not four layers in. |
| [**Encapsulation**](encapsulation.md) | The knowledge the helper encodes belongs behind the object that owns the concept, not beside its consumers. |

## Prior art

The type-level names exist and are useful for describing the symptom: **primitive obsession** and its string
variant ("stringly typed") — Fowler, *Refactoring*; **boolean blindness** — coined by Dan Licata (CMU, as a PhD
student), recorded by Robert Harper, catalogued as a smell by Jerzyk (2022); **shotgun parsing** — Alexis King,
*Parse, Don't Validate*; and the typed-settings convention of parsing configuration once at startup
(`pydantic-settings` in Python). Boolean blindness in particular is *not* the frame here — a `bool` is only one
of the shapes the missing owner leaves behind.

What is this library's own: framing the helper as evidence rather than as the crime, the six-test audit above,
the table of helpers against their missing components, and the ordering rule that the owner is assigned before
any type is chosen.

## Summary

1. **An unnecessary helper is an architecture finding.** Ask what would have to be true for it to be
   unnecessary; the answer names the component that is missing.
2. **The helper is evidence, never the crime** — and one instance is enough. It is correct, careful and
   load-bearing because a raw value travelled; there is nothing to tidy and nothing to wait for.
3. **The disease is a value nobody owns** between entry and use — which is why the same shape recurs as
   `_truthy`, `_first_nonempty`, prefix sniffers, normalisers and coercers. One cause, many costumes.
4. **Assign the owner, then let the type follow**, delete the helpers in the same change, and treat their
   disappearance as the measure of the fix.
5. **Helpers are where architecture leaks.** Where they cluster, a seam is missing; where a type was fixed in
   place instead, the leak has been hidden rather than closed.
