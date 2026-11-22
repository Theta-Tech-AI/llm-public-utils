# 3. Build: workers, workspaces and resources

Read when you start, restart or expand workers, use CLI agents or nested agents, or share a host.

## Verify the runtime and the model

- Honor explicit model choices. Do not infer a model from an agent name such as `fast-worker`.
- Requested configuration and runtime-reported identity are different facts. Use a spawn receipt or run metadata. Record agent ID, requested model, observed model and evidence source. If the runtime does not expose identity, report it as unverified.
- Read the installed version, configuration and help before you change a setting. Do not publish a guessed parameter as a working fix.
- Before a large expansion, smoke-test one bounded worker: start it, see a result, check identity, confirm cleanup. A harmless read-only task is enough.
- A larger configured limit does not prove higher throughput. Measure delivery after the expansion.

## Own the workspace

- Use one isolated checkout per delivery item. Worktrees share Git metadata (stash, config); use standalone clones when that is unsafe.
- Give the coordinator the path and the real remote before work starts. A clone of a local repository can keep the local path as `origin`.
- Treat submodules, shared caches and per-user tool profiles as single-writer resources. A worktree isolates only the superproject index. Serialize edits, clone them per worktree, or give each worker an isolated profile or a pinned identity. Forbid bare identity-switch commands in briefs.
- Do not switch branches, pop a shared stash, reset another agent's tree, or overwrite its report. Keep the mistaken edits and move the intended patch to a clean checkout. Check that the final diff holds only the assigned task.
- Give each test composition, browser session, output file and log one owner. Make scratch and output paths unique per run. A gate result is invalid when another run wrote the same tree.
- Run checks that write the same tree one at a time. A gate that rebuilds a shared folder under a running suite produces failures that look like regressions.
- Use an ignored scratch directory only after you check ignore behavior and write access. A different path does not bypass a sandbox or slot limit.

## Cap the resources

- Put a time cap and a memory cap on every heavy or possibly diverging command. Isolate it, so that one runaway test cannot exhaust the host and kill every sibling session.
- After you replace a runaway with a fix, confirm that the process ended. Editing the file does not stop a running loop.
- Run broad suites through the project's memory-capped runner, and one at a time when needed. Do not start duplicate builds or live probes for the same evidence.
- Push each green slice at once, and cap the number of agents that run tests at the same time. A host failure then costs only the work not yet pushed.
- After review, remove only owned disposable builds whose revisions and evidence are recorded.

## Stop processes safely

Stop only a process you started. Use the runtime's cancel operation or the exact PID or process group, and confirm that descendants ended. Never kill by name or pattern: the pattern can match your own shell or other agents' test runs. Put this rule in every worker brief.

Cancelling stops a process. It does not undo committed side effects. Before you re-dispatch, read the target's real state. Make delegated actions checksum-guarded, so that a re-run is safe.

## CLI workers

Use a CLI worker only when the tool exists, delegation is authorized, and it fits the runtime limits. A CLI worker does not evade an enforced limit. Read the help for model and output flags. Do not assume syntax.

Record process or session ID, working directory, source revision, model evidence, log path and result path. Keep the detailed report apart from the CLI's final-output file, so that a short final message cannot overwrite the report. Provide a steering channel that the worker reads at checkpoints. Give every external agent a wall-clock timeout and a non-empty-output assertion.

## Diagnostic hygiene

Ask workers for the specific non-secret fact you need. Never dump credential-helper results or whole process or container environments, and never rely on redaction afterward. If a secret appears in tool output, stop that diagnostic path. Report the scope of the exposure without repeating the value. Follow the operator's decision on use or rotation.

## Failure patterns

- **A worker named after a model did not prove model identity.** — The label was read as runtime metadata. Rule: use a receipt, not self-report. Evidence: runtime receipt.
- **Nested or CLI workers created hidden load.** — Only direct children were counted. Rule: one budget for descendants, processes, memory and shared environments. Evidence: actual active count and resource use.
- **A new patch landed in another task's delivery clone.** — Ownership and workspace were implicit. Rule: path, branch, baseline and scope in every assignment. Evidence: the final diff holds only the assigned task.
- **One unbounded process took down the shared host.** — A runaway test grew until the kernel killed it and every sibling session. Rule: caps above. Evidence: a process that outlives its fix.
- **A host crash erased uncommitted work in throwaway worktrees.** — Green slices sat unpushed. Rule: push each green slice. Evidence: green work left unpushed.
- **A gate reported a false pass and a false failure on the same change.** — Concurrent runs shared one hardcoded scratch tree. Rule: unique scratch paths per run. Evidence: results that contradict a clean re-run.
- **A second worker silently renamed its branch instead of failing.** — One branch can be checked out in one worktree only. Rule: unique names; fail loudly. Evidence: diverted branch names in reports.
- **Two workers editing one submodule collided despite separate worktrees.** — Submodule objects stay shared. Rule: single-writer resource. Evidence: submodule conflicts.
- **Concurrent workers sharing one per-user tool profile retargeted each other.** — Active-identity state is global per user, and a switch fails silently. Rule: isolated profile or pinned identity. Evidence: calls under the wrong identity.
- **A pattern kill matched the coordinator's own shell.** — Workers also tried broad kills that would hit other test runs. Rule: exact PID only. Evidence: unexpected terminations.
- **Cancelled workers had already pushed their effects.** — Cancel was assumed to mean "did nothing". Rule: re-read real state; guard actions. Evidence: duplicate or racing work after a cancel.
- **Hung external workers and a timed-out search were read as results.** — A hung child writes an empty file, and a timed-out search returns empty, which looks like "no match". Rule: timeout plus non-empty assertion; narrow and re-run a timed-out search. Evidence: zero-byte outputs presented as findings.
- **A credential helper and an environment dump printed live secrets.** — Whole payloads were requested, and filtering missed values outside the pattern. Rule: request only the needed fact; filter inside the command. Evidence: no raw secret in tool output or artifacts.

Next: [4. Review](review.md) · Related: [recover](recover.md)
