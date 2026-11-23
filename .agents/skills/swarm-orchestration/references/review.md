# 4. Review and validate

Read before you accept a handoff, approve a revision, diagnose a failing check, or start a fourth review round.

## Keep author and reviewer apart

- Independent review means the recorded reviewer identity differs from the recorded author, as actor identifiers that the runtime or hosting service can tell apart. A role label is not an identity. A shared or missing identity leaves review outstanding.
- A review approves one exact revision. Every amendment voids it. Batch small fixes into one revision before you ask again, then review the delta.
- Each report lists the steps it skipped (denied consent, blocked access) in an "unverified" section. An unnamed skipped step is unverified. A verdict on reported, not reproduced, evidence is provisional.

## Cap the review loop

Count review rounds with the class of each finding (for example: boundary parsing, ordering, a missing case of one rule). The worker writes both into its status line, so `board_check.py` flags the loop.

**After three rounds that return the same class of finding, the lane stops patching.** Observation: two lanes ran 12 and 27 rounds on a mid-tier model. Each patch fixed the last example and missed the next. The cause was a missing invariant, not a missing patch. Then:

1. The owner writes the invariants the code must hold, as short statements.
2. The owner builds a property or fuzz check from the review history: every earlier finding becomes a generated case.
3. The owner redesigns to the invariants, and the check runs before the next review.
4. The coordinator escalates the lane to the strongest available model ([2](assign.md#choose-the-model)) by the handover in [2](assign.md#hand-a-lane-over), or takes the design itself.

A round that finds a new class of finding resets the count for that class only.

## Validate the source you deliver

- For layered repositories, record the upstream commit, overlay commit, generated inputs and composition steps. Compose into a fresh, empty tree for each candidate and each amendment; never test a populated scratch tree or a mirror that overlays were copied into.
- Confirm that the changed paths and file hashes match the reviewed revision and the remote.
- A failure is "pre-existing" only after you reproduce it on a pristine baseline with the same composition.
- Run checks in CI's project-wide context: type-check scope, configuration, tool versions. A gate can print errors and exit 0; read its output. Run the cheap repository-wide checks (policy, links, whitespace) before publication.
- Test the behavior the task changes, on the real callers. A test that mocks the hook cannot show the hook's cadence. For generated artifacts, compare fresh generator output with the shipped file. A generated file changes only through its generator: after any regeneration at integration, diff it against each merged branch, because a hand edit is lost silently.
- Name the fixture for each required outcome ([1](establish.md#proof-is-work)). A failure-path run cannot prove a success path. Read the final artifact before you mark a row demonstrated. Assert produced against expected counts: a run once reported success having produced almost nothing.
- Do not widen baselines, add ignores or weaken assertions to hide a regression.
- After a code change, rerun the affected checks. A green review does not survive a conflicting merge: rerun on the merged head. Do not rerun expensive suites after a prose edit.

## Diagnose a failing check

1. Read the failing job's step and log before you change code.
2. Classify: early gate, test, or infrastructure. A skipped or early gate says nothing about later tests.
3. Reproduce on the exact composition.
4. One owner makes the smallest supported repair. When items share the failing prerequisite, it becomes one board item.

## Judge scope and design

- Judge the whole task's acceptance matrix, not the latest patch. A partial change may merge when authorized; the task stays open.
- Before you delete a wrapper or small module, check dynamic imports, packaging and real consumers.
- Prefer the narrow correct change over a generic framework. Record the observable contract before splitting work on it.
- Check a reported defect against the code before you turn it into a decision or a brief: a routed decision on "16 signatures" was 2 in the code.
- Fix provider-neutral behavior in its owning source. Consume an upstream revision only when it keeps the ancestry you consume now; a newer commit can omit deployed fixes. For an adoption, list removed and changed public symbols, schemas and startup requirements, and run the consumer's real startup check.
- Debris from test scripts can look like a data leak. Trace the write in the audit trail first, archive it reversibly, then check for a real missing guard.

Next: [5. Integrate and deliver](integrate-and-deliver.md)
