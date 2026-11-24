---
name: deslop-architecture
description: Deslop principles — Architecture: DRY, Single Source of Truth, Separation of Concerns, Modularity, One Logical Unit One Home, Encapsulation, Demeter, Orthogonality, DI, Composition, Implicit Coupling, Layering Violations, SOLID, CQS, Reusability, Parse Don't Validate, Metadata Beside Content, Make Illegal States Unrepresentable, A State Machine Nobody Wrote Down, A Helper That Must Exist Is an Architecture Finding, Immutability, Idempotency, Freshness From Inputs, Depend in the Direction of Stability.
---

# Architecture

**Why this is slop:** Leaking responsibilities and knowledge across module boundaries makes a local requirement change disturb code that should be independent.

> *Structuring and designing systems. These principles govern how code is organized, how components relate, and how systems are designed for change.*

Each principle is a self-contained file — open it when a finding implicates that principle.

## Organization & Structure

*Where does this code belong? DRY and Single Source of Truth ensure knowledge lives in one place, Separation of Concerns defines boundaries between responsibilities, Modularity packages those boundaries into self-contained units, One Logical Unit, One Home gives a unit that has drifted across packages back to a single owner. Separation of Concerns and Modularity now carry the *change* record with them — one change scattering across the tree, and one change landing in every file.*

| Principle | What it says |
|-------------|----------------|
| [DRY: Don't Repeat Yourself](architecture/dry.md) | One authoritative representation per piece of knowledge; fix at the 2nd occurrence |
| [Single Source of Truth](architecture/single-source-of-truth.md) | One authoritative location per datum; other copies derive from it |
| [Separation of Concerns](architecture/separation-of-concerns.md) | High cohesion, low coupling; one concern per part — read it against **where one change lands**. Change-set test: `git log --name-only` over the last five capability commits; **four or more folders crossed for one logical change is shotgun surgery** (a feature's rule, query, DTO and route given five homes by a **layer-first** tree: `controllers/`, `services/`, `models/`, `validators/`), and the mirror — `git log --name-only -- <file>` showing unrelated areas in one file, with a name that needs an "and" (`utils.py`, `helpers.py`, `manager.py`) — is divergent change, whose body is the god file. Enforceability test: what import rule refuses the crossing that would recreate it. Report only whichever of the two the evidence supports, and never split a file for line count alone |
| [Modularity](architecture/modularity.md) | Deep modules, each hiding one design decision — and the **shallow module** is a hop that adds a name and no policy: a `XService` that only calls its repository, a module re-exporting a library, arguments forwarded unchanged in the same order. Policy test: name in one sentence what the hop adds (translation, authorisation, transaction boundary, retry, cache, a port with two implementations); "nothing" is the finding. Then count the hops from entry point to work. Proxy, Decorator, Adapter and Facade are legitimate — the test decides, not the shape |
| [One Logical Unit, One Home](architecture/one-logical-unit-one-home.md) | A unit spread across packages, or a shape copied per feature, is a finding — consolidate to one module per responsibility |

## Coupling & Dependencies

*How do components relate to each other? These principles minimize unhealthy dependencies. Encapsulation hides internal state, Law of Demeter limits knowledge of other objects, Orthogonality ensures independent change, Dependency Injection makes dependencies explicit, Composition Over Inheritance favors flexible composition — and the last two ask what a component *knows* that its signature never says, and which way that knowledge is allowed to point.*

| Principle | What it says |
|-------------|----------------|
| [Encapsulation](architecture/encapsulation.md) | Tell, don't ask; hide state behind behavior |
| [Law of Demeter](architecture/law-of-demeter.md) | Talk only to immediate friends; the one-dot rule |
| [Orthogonality](architecture/orthogonality.md) | **Unrelated things change independently** — census each unit's reasons to change (trigger, external read or write, transformation, persistence, policy); two reasons to change nominate a unit, and a probe that needs a touch point spanning both with no contract in the unit's own vocabulary is the finding (probes: a second implementation of each external system, a second consumer of the trigger). Tells: a bundle mixing a source client with sink or transform services; a handler that performs the work it was triggered for; a key derived from one collaborator's representation; a second implementation imitating the first's interface |
| [Dependency Injection](architecture/dependency-injection.md) | Inject dependencies; declare what, not how |
| [Composition Over Inheritance](architecture/composition-over-inheritance.md) | Has-a over is-a; black-box composition |
| [Implicit Coupling](architecture/implicit-coupling.md) | **Two components agree on something the code never states** — the order of calls (`configure()` then `use()`), a literal three modules compare (`"csv"`, `"prod"`, `1`), a singleton reached rather than received, config read four layers deep. It compiles and fails in the one caller that did not know. Tells: a required `init`/`configure`/`set_` step before use; the same string literal compared in two modules; a singleton or ambient/global read inside business logic; a listener that assumes a publisher ran first. Count the **degree**: how many modules must change when the agreement changes |
| [Depend in the Direction of Stability](architecture/dependency-stability.md) | **An import whose far end moves far more often than its near end** — the business rule importing the vendor SDK, the long-lived core importing the remote endpoint's schema, the domain importing a toggle reader. Reason test: enumerate the far end's *own* reasons to change (vendor version, wire format, auth flow, a product experiment); if any of them obliges the near end to change, the edge is wrong whatever layer it points at. Churn is evidence for ranking, never proof; fan-in multiplies the blast radius. Repair: a port where the rate changes, in the stable side's own vocabulary, then delete the direct import |
| [Layering Violations](architecture/layering-violations.md) | **A dependency running against the intended arrows**, filed together with the missing gate that would refuse it. Tells: `flask.request` / `express req` / an HTTP context inside a domain rule; a repository returning a serialised DTO; a migration importing an application service; one feature importing another's internals; a cycle between two packages; a driver exception in a public signature. Ask for the arrows in one sentence, then ask **what machine checks them on every push** — an architecture asserted only in a README has already eroded |

## Design Patterns & Conventions

*Proven approaches to common problems. SOLID provides five foundational OO principles, Convention Over Configuration reduces boilerplate through sensible defaults, Command-Query Separation distinguishes actions from queries, and Code Reusability addresses when and how to make code reusable.*

| Principle | What it says |
|-------------|----------------|
| [SOLID Principles](architecture/solid.md) | SRP, OCP, LSP, ISP, DIP — with code smells |
| [Convention Over Configuration](architecture/convention-over-configuration.md) | Sensible defaults with escape hatches |
| [Command-Query Separation](architecture/command-query-separation.md) | Methods either do or answer, never both |
| [Code Reusability](architecture/code-reusability.md) | Earn reuse from real callers; don't speculate on interfaces |

## Data & State

*How should data flow and behave? Parse Don't Validate transforms unstructured input into typed domain objects at boundaries, Make Illegal States Unrepresentable fixes the shape it lands in, and A State Machine Nobody Wrote Down gives the moves between those states one owner. Immutability eliminates bugs by preventing state changes after creation. Idempotency ensures operations can be safely repeated, and Freshness From Inputs decides from content, not from clocks, whether derived work must be redone.*

| Principle | What it says |
|-------------|----------------|
| [Parse, Don't Validate](architecture/parse-dont-validate.md) | Convert input to precise types once at the boundary. **One instance is enough:** what a boundary learned about a value is not carried by what it keeps. Sighting aids (confirm each by reading): a checker returning `None` / `bool` / a complaint (`-> str \| None`) whose caller then stores the argument it passed in; a normalisation bound to a local copy inside a check (`text = value.strip()`, `n = int(raw)`) while the raw value is kept; one stored value normalised again by two or more readers (`.strip()`, `.lower()`, `set(...)` on the same field, not counting calls to the owner's parser) — that count points at the **writer**, not the readers |
| [Metadata Beside Content](architecture/metadata-beside-content.md) | What is true *about* content (source, status, availability, confidence, to-dos) travels beside it as typed fields, annotations or states, never inside it as markers, status sentences, sentinels or appended notes. Tell: a reader that searches text for meaning (a marker regex, a sentinel prefix, a status substring) |
| [Make Illegal States Unrepresentable](architecture/illegal-states-unrepresentable.md) | **A field that is meaningful only in one mode** — `shipped_at` when `status == "shipped"`, `session_id` when connected, `is_admin` implying `is_user`. Read the model as an **implication table**: every "X is set only when Y" is a representable illegal state, and every `if status == …` is a place re-deriving which fields are legal. Test: can an illegal instance be built without raising? Then the type is a suggestion — one variant per state, each holding exactly its own fields, is the repair (the trigger is the *data model*, so this fires where Parse Don't Validate's boundary trigger does not) |
| [A Helper That Must Exist Is an Architecture Finding](architecture/helper-is-an-architecture-finding.md) | **One instance is enough** — a helper that turns a raw representation into a decision exists only because that value travelled unparsed; parse it at the seam and the function has nothing left to do. Never downgrade a lone helper for being the only copy. Tells: a string compared against a set of literal tokens, `startswith` on an identifier, a first-non-empty scan over alternative names, a literal default beside a lookup — plus, as a **sighting aid only**, the same `env.get("NAME", default)` repeated across files (that is not the criterion) |
| [A State Machine Nobody Wrote Down](architecture/implicit-state-machine.md) | **A status or mode field whose legal transitions exist only as conditions across callers** — no file says which move is allowed. Count the **writers**: two or more assignments means the transition relation has no owner. Then the **legality question** — *can it go from X to Y?* — an answer that requires studying the callers is the finding. Tells: `status` written in three modules; a job that sets the field directly instead of calling the checker; `n` booleans interacting with a status field (`2^n × states` combinations, only a few intended); a stale `# only valid when …` comment at a write site. Repair: name the states, centralize the transitions, route every mutation through the owner |
| [Immutability](architecture/immutability.md) | Values fixed after creation; never mutate caller data |
| [Idempotency](architecture/idempotency.md) | Safe repetition; design for duplicate requests |
| [Freshness From Inputs](architecture/freshness-from-inputs.md) | **Derived work is stale only when what it read changed.** Store a digest of exactly what the producer read beside the output and compare it; never a time or event (`updated_at > built_at`, "changed after the lock"), never a key wider or narrower than what was read, a producer's own version only by a written decision that the change alters every past output (otherwise it is provenance, and redoing old work with a new producer is a recorded action). Tells: an identical re-save or an unlock and re-lock makes work stale; a cache whose hit rate collapses after any unrelated change; a deploy that invalidates every stored result |
