# /smelt — separate overlay code into upstream metal + project slag

An overlay tree (the directory whose files you rsync over a shared
upstream submodule before each build) is expensive to carry: every
file is rsynced on every build, re-merged on every upstream bump, and
re-reviewed on every PR. `/smelt` separates provider-agnostic upstream
improvements from project-specific code so each line lives in the right
repository.

- **Metal** — provider-agnostic logic (bug fixes, refactors,
  Protocols, type tightening, anything a *different* downstream of the
  same upstream framework would also want). Flows upstream to the
  shared framework repo.
- **Slag** — project-specific implementation (your cloud provider's
  SDK calls, your identity verifier, your tenant rules, your branding,
  your client/domain content, your retention/audit policy). Stays in
  your overlay tree.

The boundary is **which repository the line of code lives in.**
Smelting decides that boundary deliberately instead of letting it
drift.

## When to smelt

- The smelt audit flags a file with `< 15%` diff against upstream
  (copy-to-flip-a-region — most of the file is metal).
- A bug you're chasing touches code that has nothing project-specific
  about it: no provider-SDK imports, no identity logic, no
  project-only strings. The fix belongs upstream.
- You're about to ADD a new overlay file and can't articulate a
  one-sentence reason it has to be project-only.
- An overlay file has grown past ~250 LOC (frontend) or ~400 LOC
  (backend) — almost certainly an alloy worth fractionating.
- A `cmp -s` after `git -C <submodule> clean -fd && rsync overlay`
  shows a file is byte-identical to upstream: pure waste, smelt out
  the whole file.

## Decision: metal or slag?

Walk the filters top-down. First YES wins.

```
Touches provider-SDK imports / identity-specific logic / branding strings?
       └─ YES → slag (overlay)
       └─ NO  → ↓
Contains client data, domain-specific acceptance logic, example
content, tenant names, workflow assumptions, or project-only
retention / audit / RBAC policy?
       └─ YES → slag (or extract only the generic abstraction upstream)
       └─ NO  → ↓
Adds a new Protocol / factory / registry hook the overlay can extend?
       └─ YES → split: upstream the Protocol, overlay the impl
       └─ NO  → ↓
Pure refactor / bug fix / new test that helps a hypothetical *other*
downstream of the same framework as much as this project?
       └─ YES → metal (upstream)
       └─ NO  → stop and write the one-sentence ownership reason
                before editing
```

Hard architectural invariant: **overlay imports from upstream;
upstream never imports from overlay.** If a candidate change would
need upstream to call into project code, the candidate isn't a smelt —
it's an upstream extension point that the project then configures.

## Split before you smelt

A common smelting failure: the overlay file is 800 lines, 20 of
them project-specific. Smelting the whole 800 lines upstream duplicates
code; smelting nothing leaves the alloy in place.

The fix: split the UPSTREAM file along its natural seam first.
In your canonical upstream checkout, refactor the 800-line file into
per-concern siblings (e.g. `users.py` → `users_core.py` +
`users_emails.py` + `users_lock.py`). Push that split as its own
commit; wait for the submodule mirror; bump the submodule. Then the
overlay only copies the one small file carrying the project seam — the
other split-out files evaporate from the overlay.

Splitting is the prerequisite to smelting when:

- The overlay file is large (>250 / 400 LOC) AND
- The actual project-specific diff against upstream is small (<20% of
  lines) AND
- The diff clusters in 1-2 logical regions of the file

When all three hold, split upstream first, then smelt.

Stash-and-restore pattern (when another agent has WIP in your
canonical upstream checkout): `git stash push -u -m "smelt-temp"`,
branch from clean `development`, edit ONLY the file(s) you're smelting,
commit, push, then `git stash pop` to restore the parallel agent's
work. Pre-flight rule 1 (no stepping on WIP) still applies — only
stash if you're confident your edits won't conflict.

## Pre-flight (mandatory)

Before touching your canonical upstream checkout, verify:

1. **Upstream working tree is clean** —
   `git -C <upstream> status --short`. If another agent has unstaged
   changes there, DO NOT step on them. Either continue your work in
   the overlay until that agent commits, OR coordinate via the user.
   Pushing your changes on top of someone else's WIP commits their WIP
   under your branch.

2. **Submodule pointer is current** —
   compare `git -C <submodule> rev-parse HEAD` against the latest
   upstream `origin/development`. If the submodule is behind, your
   overlay diff may already be partially upstream (do the bump first,
   re-audit).

3. **Submodule is clean** —
   `git -C <submodule> status --short` should be empty. Run
   `git -C <submodule> clean -fd` if not. A dirty submodule will
   silently contaminate `cmp -s` audits. Always run the clean-submodule
   check before trusting byte-identical or low-diff overlay counts.

## The workflow

### 1. Scope the change in the consumer repo first

Make the smallest possible commit on `development` so you have a
working baseline. Don't try to smelt code that doesn't compile yet.

### 2. Identify the upstream shape

Three patterns from the smelt audit:

| Pattern | Upstream PR shape |
|---|---|
| **One-field-add copy** | Add the field (with `Optional[T] = None` default for back-compat) directly upstream. Delete the entire overlay file once upstream lands. |
| **Tenant/provider policy override** | Extract a Protocol or factory hook upstream. Overlay shrinks to a small project-specific implementation. |
| **Route / registry copy** | Make upstream's registry `extend()`-able or scan a directory. The overlay contributes a small registration call. |
| **Big alloy needing shatter** | Split upstream first (see "Split before you smelt"), then smelt the resulting small-file diff. |

Run the smelt audit before choosing a target (adjust the overlay path
and submodule name to your repo):

```bash
OVERLAY=overlays/files        # your overlay tree root
SUBMODULE=upstream            # your upstream submodule dir

echo "=== overlay files <15% diff against upstream (copy-to-flip smell) ==="
for f in $(find "$OVERLAY" -type f \( -name '*.py' -o -name '*.tsx' -o -name '*.ts' \) ! -path '*/tests/*' ! -path '*/__pycache__/*'); do
  upstream="$SUBMODULE/${f#$OVERLAY/}"
  [ -f "$upstream" ] || continue
  ol=$(wc -l < "$f")
  diff_lines=$(diff "$f" "$upstream" 2>/dev/null | grep -cE '^[<>]' || true)
  pct=$((diff_lines * 100 / (ol + 1)))
  [ "$pct" -lt 15 ] && [ "$ol" -gt 100 ] && printf '%3d%% %4d/%4d %s\n' "$pct" "$diff_lines" "$ol" "${f#$OVERLAY/}"
done | sort -n

echo ""
echo "=== overlay files without upstream counterpart (verify project-specific) ==="
for f in $(find "$OVERLAY/backend" -type f -name '*.py' ! -path '*/tests/*' ! -path '*/__pycache__/*' 2>/dev/null); do
  upstream="$SUBMODULE/${f#$OVERLAY/}"
  if [ ! -f "$upstream" ]; then
    rel="${f#$OVERLAY/}"
    # heuristic: does it import a provider SDK or reference provider-only modules?
    has_provider=$(grep -cE 'import (boto3|azure|google\.cloud)|from (boto3|azure|google\.cloud)' "$f" 2>/dev/null || true)
    if [ "$has_provider" = "0" ]; then
      printf 'WARN %s (no provider SDK import - verify it belongs in overlay)\n' "$rel"
    else
      printf 'OK   %s\n' "$rel"
    fi
  fi
done | sort
```

### 3. Branch in your canonical upstream checkout

```bash
cd <upstream>
git checkout development && git pull --ff-only
git checkout -b feat/<scope>
```

### 4. Make the upstream change + ship tests in the same commit

Every upstream commit ships with at least one regression test. Run
the upstream suite:

```bash
cd <upstream>
pytest -q                                    # full suite
pytest backend/src/services/<area>/ -v       # targeted
```

Per the upstream coding principles, 250+ LOC frontend files / 400+ LOC
backend files should be split. Don't push a god-file upstream just
because the existing one is bigger.

### 5. Push to the upstream repo

```bash
cd <upstream>
git push origin feat/<scope>
PUSHED_SHA=$(git rev-parse HEAD)
```

If your upstream replicates to a separate read-only mirror that the
submodule tracks, a mirror Action fires within ~1 min.

### 6. Wait for the mirror — verify by SHA

If the submodule tracks a mirror, wait for the SHA to appear before
bumping (skip this step if the submodule tracks the upstream directly):

```bash
until [ "$(git ls-remote <mirror-url> refs/heads/feat/<scope> | cut -f1)" = "$PUSHED_SHA" ]; do
    sleep 10; echo "waiting for mirror..."
done
echo "mirror synced: $PUSHED_SHA"
```

### 7. Bump the submodule

```bash
cd <consumer-repo>/<submodule>
git fetch origin
git checkout "$PUSHED_SHA"
cd ..
git add <submodule>
git commit -m "chore(upstream): bump submodule to $PUSHED_SHA — <one-line rationale>"
```

**Submodule pointer must be a monotonic upstream superset.** Before
checkout, verify the new SHA contains every commit any current
consumer branch references:
`git -C <submodule> merge-base --is-ancestor <old-sha> <new-sha>`.

### 8. Delete or shrink the overlay

If upstream landed the field/behaviour the overlay was replicating,
the overlay file should now be byte-identical to upstream after rsync.
Delete it:

```bash
# Verify identical (after clean submodule + rsync of overlay):
rsync -a <overlay>/ <submodule>/
cmp -s <overlay>/path/to/file <submodule>/path/to/file \
    && echo "safe to delete"
git -C <submodule> clean -fd  # reset submodule to upstream HEAD

# Then remove the overlay:
git rm <overlay>/path/to/file
```

If upstream landed a Protocol and the overlay carries the
implementation, the overlay shrinks to just the project-specific bit.

### 9. Open the upstream PR

```bash
cd <upstream>
gh pr create --base development --head feat/<scope> --draft \
  --title "<conventional-commit-style>" \
  --body "$(cat <<EOF

### Summary
- bullet what changed and why
- which overlay code can shrink as a result

### Test plan
- [ ] backend tests pass
- [ ] frontend tests pass (if applicable)
- [ ] cross-downstream sanity (does this regress other consumers of the framework?)
EOF
)"
```

### 10. Run an automated review before promoting draft → ready

Run your second-opinion reviewer against the diff and address its
findings before flipping the PR to ready.

## Anti-patterns to refuse

- **Smelting on top of another agent's WIP.** Their uncommitted
  changes in the upstream checkout will be committed by you and pushed
  under your branch. Wait for them, or coordinate via the user.
- **Overlay-as-fallback.** "We'll keep the overlay just in case the
  upstream PR is rejected." If you're shipping the same logic on
  both sides you're paying the carrying cost twice. Pick one.
- **Smelting without verifying the rebuild.** After bumping the
  submodule, always rebuild locally + boot the app. A passing upstream
  test suite doesn't prove the rsync produces a working image
  downstream.
- **Smelting without splitting when the file is huge.** Pushing a
  one-line fix into upstream's 1,200-line module doesn't reduce overlay
  carrying cost — the overlay still has to copy the whole file to flip
  1 line. Split upstream first.
- **Upstreaming project defaults.** A new Protocol or hook is metal,
  but the tenant ids / identity group names / regions / retention
  periods / example assumptions / branding strings that configure it
  are slag. Land the abstraction empty upstream; configure it from the
  overlay.
- **Leaving a regression test behind.** If behavior moves upstream,
  its test migrates too. The consumer's tests should only cover the
  project implementation/adapter — never the generic behavior that's
  now upstream-owned.
- **Treating partial acceptance as failure.** Upstream may accept
  the hook but ask for a different shape than your impl. Rebase
  the follow-up onto the accepted shape; don't preserve the rejected
  variant in the overlay as "the version we prefer."

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Mirror never picks up the SHA after 5 min | Mirror workflow disabled or rate-limited | Check the mirror workflow runs; manually trigger it if it's stuck |
| Submodule bump fails with detached HEAD | You checked out a SHA without fetching first | `git -C <submodule> fetch origin && git -C <submodule> checkout <sha>` |
| Another consumer branch loses upstream commits after your bump | New submodule SHA is not a superset of the SHA already referenced by active work | Before committing the bump, verify `git -C <submodule> merge-base --is-ancestor <old-sha> <new-sha>`; if not, merge the lagging branch into your target upstream first |
| Local tests pass but container `import` fails | Service-specific `requirements.txt` missing a transitive dep through a shared `lib/` | Add the transitive dep to the relevant service's `requirements.txt`; rebuild image |
| `git rm overlay/.../foo` then frontend build fails | Frontend dist still references the deleted overlay file | Hard rebuild: `rm -rf dist node_modules/.vite && npm ci && npm run build` |

## Measure success

After every smelt, re-run the smelt audit and capture the
before/after overlay LOC in the consumer PR description. A smelt that
doesn't shrink overlay carrying cost (or doesn't unblock a future
shrink via split-then-smelt) was a code-mover, not a code-separator.

## See also

- `/shatter` — split a large file into focused pieces; the prerequisite
  to smelting when an overlay file is a big alloy.
- `/deslop` — the full code-quality pass that flags overlay files worth
  smelting.
