---
name: deslop-architecture
description: Deslop principles — Architecture: DRY, Single Source of Truth, Separation of Concerns, Modularity, One Logical Unit One Home, Shotgun Surgery, A God File, Encapsulation, Demeter, Orthogonality, DI, Composition, Implicit Coupling, Layering Violations, Pass-Through Wrappers, SOLID, CQS, Reusability, Parse Don't Validate, Make Illegal States Unrepresentable, A Helper That Must Exist Is an Architecture Finding, Immutability, Idempotency.
---

# Architecture

> *Structuring and designing systems. These principles govern how code is organized, how components relate, and how systems are designed for change.*

Each principle is a self-contained file — open it when a finding implicates that principle.

## Organization & Structure

*Where does this code belong? DRY and Single Source of Truth ensure knowledge lives in one place, Separation of Concerns defines boundaries between responsibilities, Modularity packages those boundaries into self-contained units, One Logical Unit, One Home gives a unit that has drifted across packages back to a single owner, and the last two read the code's *change* record — one change scattering across the tree, or every change landing in one file.*

| Principle | What it says |
|-------------|----------------|
| [DRY: Don't Repeat Yourself](architecture/dry.md) | One authoritative representation per piece of knowledge; fix at the 2nd occurrence |
| [Single Source of Truth](architecture/single-source-of-truth.md) | One authoritative location per datum; other copies derive from it |
| [Separation of Concerns](architecture/separation-of-concerns.md) | High cohesion, low coupling; one concern per part |
| [Modularity](architecture/modularity.md) | Deep modules, each hiding one design decision |
| [One Logical Unit, One Home](architecture/one-logical-unit-one-home.md) | A unit spread across packages, or a shape copied per feature, is a finding — consolidate to one module per responsibility |
| [Shotgun Surgery](architecture/shotgun-surgery.md) | **One logical change edited in many files is a design measurement, not tidiness** — read the change-set: `git log --name-only` over the last five capability commits and count the folders crossed. A **layer-first** tree (`controllers/`, `services/`, `models/`, `validators/`) manufactures the crossing by construction; a feature's rule, query, DTO and route are given five homes before the first feature exists. Tells: one field added → migration + model + DTO + serializer + validator + API docs; a new provider → five folders; a rename that opens twenty files; a folder named for a technical role rather than a capability |
| [A God File](architecture/god-file.md) | **A name that cannot state its responsibility** — `utils.py`, `helpers.py`, `common.py`, `manager.py`, or a 2,000-line module importing three of the app's own layers. The finding is divergent change, not size: `git log --name-only -- <file>` shows unrelated feature areas in one file, so unrelated owners queue on one path. Tells: the name needs an "and"; the test file is edited by unrelated teams; half its functions have an existing owner elsewhere — the dead-copy test comes **before** any extraction, and a split that only relocates lines repairs nothing |

## Coupling & Dependencies

*How do components relate to each other? These principles minimize unhealthy dependencies. Encapsulation hides internal state, Law of Demeter limits knowledge of other objects, Orthogonality ensures independent change, Dependency Injection makes dependencies explicit, Composition Over Inheritance favors flexible composition — and the last three ask what a component *knows* that its signature never says, which way that knowledge points, and whether each hop along the way pays for itself.*

| Principle | What it says |
|-------------|----------------|
| [Encapsulation](architecture/encapsulation.md) | Tell, don't ask; hide state behind behavior |
| [Law of Demeter](architecture/law-of-demeter.md) | Talk only to immediate friends; the one-dot rule |
| [Orthogonality](architecture/orthogonality.md) | Unrelated things change independently |
| [Dependency Injection](architecture/dependency-injection.md) | Inject dependencies; declare what, not how |
| [Composition Over Inheritance](architecture/composition-over-inheritance.md) | Has-a over is-a; black-box composition |
| [Implicit Coupling](architecture/implicit-coupling.md) | **Two components agree on something the code never states** — the order of calls (`configure()` then `use()`), a literal three modules compare (`"csv"`, `"prod"`, `1`), a singleton reached rather than received, config read four layers deep. It compiles and fails in the one caller that did not know. Tells: a required `init`/`configure`/`set_` step before use; the same string literal compared in two modules; a singleton or ambient/global read inside business logic; a listener that assumes a publisher ran first. Count the **degree**: how many modules must change when the agreement changes |
| [Layering Violations](architecture/layering-violations.md) | **A dependency running against the intended arrows**, filed together with the missing gate that would refuse it. Tells: `flask.request` / `express req` / an HTTP context inside a domain rule; a repository returning a serialised DTO; a migration importing an application service; one feature importing another's internals; a cycle between two packages; a driver exception in a public signature. Ask for the arrows in one sentence, then ask **what machine checks them on every push** — an architecture asserted only in a README has already eroded |
| [Pass-Through Wrappers](architecture/pass-through-wrappers.md) | **An indirection that adds a name and no policy** — a `XService` that only calls its repository, a module that re-exports a library, arguments forwarded unchanged in the same order. Test it by naming in one sentence what the hop adds; then count the hops from entry point to work, and name each. Legitimate only when the policy is nameable: translation, authorisation, transaction boundary, retry, cache, a port with two implementations |

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
