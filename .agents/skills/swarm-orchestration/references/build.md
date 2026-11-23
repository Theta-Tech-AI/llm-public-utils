# 3. Build: workers, workspaces and resources

Read when you start, restart or expand workers, use CLI or nested agents, or share a host.

## Verify the runtime and the model

- Honor explicit model choices. Do not infer a model from an agent name.
- Requested and observed model are different facts. Record agent ID, requested model, observed model and the evidence source (spawn receipt, run metadata), or report the identity as unverified.
- Read the installed version, configuration and help before you change a setting. Do not publish a guessed parameter as a fix.
- Before a large expansion, smoke-test one bounded worker: start, result, identity, cleanup.

## Own the workspace

- One isolated checkout per item. Worktrees share Git metadata (stash, config); use standalone clones when that is unsafe. Record the path and the real remote.
- Submodules, shared caches and per-user tool profiles are single-writer resources. A worktree isolates only the superproject index. Two workers once collided in one submodule, and two others retargeted each other through one shared tool profile. Serialize, clone per worktree, or give each worker an isolated profile.
- Never switch branches, pop a shared stash, or reset another agent's tree. Move a stray patch to a clean checkout.
- Each test composition, browser session, output file and log has one owner and a unique path. A gate whose tree another run wrote is invalid; one shared scratch tree once gave a false pass and a false failure on the same change.
- Run checks that write the same tree one at a time.
- Push each green slice to its own branch at once. A host crash once erased green work left unpushed.

## Cap the resources

- Put a time cap and a memory cap on every heavy or possibly diverging command, and isolate it. One runaway test once killed every sibling session on the host.
- After you fix a runaway, confirm that the process ended. Editing the file does not stop a running loop.
- Cap concurrent test runs. Count shards and nested jobs. Give the next landing's blocking check first access. Bound live probes against shared quotas.
- Count nested agents, CLI processes and their memory in the same budget as direct workers.
- After review, remove only owned builds whose revisions and evidence are recorded.

## Stop processes safely

Stop only a process you started: the runtime's cancel operation, or the exact PID or process group, then confirm that descendants ended. Never kill by name or pattern; a pattern kill once matched the coordinator's own shell. Put this rule in every brief. Cancelling does not undo pushed side effects: read the real state before you re-dispatch, and make delegated actions safe to re-run.

## CLI workers

Use a CLI worker only when the tool exists, delegation is authorized and it fits the runtime limits. Read its help; do not assume syntax. Record process ID, directory, revision, model evidence, log path and result path. Keep the report apart from the CLI's final-output file. Give every external agent a wall-clock timeout and a non-empty-output check: a hung child writes an empty file, and a timed-out search looks like "no match".

## Diagnostic hygiene

Ask for the specific non-secret fact. Never dump credential-helper output or whole environments, and do not rely on redaction afterward. If a secret appears, stop that path, report the exposure without the value, and follow the operator's decision on rotation.

Next: [4. Review](review.md)
