---
name: deslop-architecture
description: Deslop principles — Architecture: DRY, Single Source of Truth, Separation of Concerns, Modularity, One Logical Unit One Home, Encapsulation, Demeter, Orthogonality, DI, Composition, Implicit Coupling, Layering Violations, SOLID, CQS, Reusability, Parse Don't Validate, Make Illegal States Unrepresentable, A Helper That Must Exist Is an Architecture Finding, Immutability, Idempotency.
---

# Architecture

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
| [Orthogonality](architecture/orthogonality.md) | Unrelated things change independently |
| [Dependency Injection](architecture/dependency-injection.md) | Inject dependencies; declare what, not how |
| [Composition Over Inheritance](architecture/composition-over-inheritance.md) | Has-a over is-a; black-box composition |
| [Implicit Coupling](architecture/implicit-coupling.md) | **Two components agree on something the code never states** — the order of calls (`configure()` then `use()`), a literal three modules compare (`"csv"`, `"prod"`, `1`), a singleton reached rather than received, config read four layers deep. It compiles and fails in the one caller that did not know. Tells: a required `init`/`configure`/`set_` step before use; the same string literal compared in two modules; a singleton or ambient/global read inside business logic; a listener that assumes a publisher ran first. Count the **degree**: how many modules must change when the agreement changes |
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

*How should data flow and behave? Parse Don't Validate transforms unstructured input into typed domain objects at boundaries, Make Illegal States Unrepresentable fixes the shape it lands in. Immutability eliminates bugs by preventing state changes after creation. Idempotency ensures operations can be safely repeated.*

| Principle | What it says |
|-------------|----------------|
| [Parse, Don't Validate](architecture/parse-dont-validate.md) | Convert input to precise types once at the boundary |
| [Make Illegal States Unrepresentable](architecture/illegal-states-unrepresentable.md) | **A field that is meaningful only in one mode** — `shipped_at` when `status == "shipped"`, `session_id` when connected, `is_admin` implying `is_user`. Read the model as an **implication table**: every "X is set only when Y" is a representable illegal state, and every `if status == …` is a place re-deriving which fields are legal. Test: can an illegal instance be built without raising? Then the type is a suggestion — one variant per state, each holding exactly its own fields, is the repair (the trigger is the *data model*, so this fires where Parse Don't Validate's boundary trigger does not) |
| [A Helper That Must Exist Is an Architecture Finding](architecture/helper-is-an-architecture-finding.md) | **One instance is enough** — a helper that turns a raw representation into a decision exists only because that value travelled unparsed; parse it at the seam and the function has nothing left to do. Never downgrade a lone helper for being the only copy. Tells: a string compared against a set of literal tokens, `startswith` on an identifier, a first-non-empty scan over alternative names, a literal default beside a lookup — plus, as a **sighting aid only**, the same `env.get("NAME", default)` repeated across files (that is not the criterion) |
| [Immutability](architecture/immutability.md) | Values fixed after creation; never mutate caller data |
| [Idempotency](architecture/idempotency.md) | Safe repetition; design for duplicate requests |
