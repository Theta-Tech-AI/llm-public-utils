---
name: smelt
description: Separate code between an upstream framework and downstream overlays in BOTH directions — push provider-agnostic metal up, pull owned deliverables back, and adopt downstream metal into upstream. Use when deduplicating overlay code, auditing a downstream, or deciding where a fix belongs.
---

# /smelt — separate code into upstream metal + project slag

An overlay tree (files rsynced over a shared upstream submodule before each
build) is expensive to carry: every file is rsynced on every build, re-merged
on every upstream bump, and re-reviewed on every PR. `/smelt` separates
provider-agnostic upstream improvements from project-specific code so each
line lives in the right repository.

- **Metal** — provider-agnostic logic (bug fixes, refactors, Protocols, type
  tightening, anything a *different* downstream of the same upstream framework
  would also want). Flows upstream to the shared framework repo.
- **Slag** — project-specific implementation (your cloud provider's SDK calls,
  your identity verifier, your tenant rules, your branding, your
  client/domain content, your retention/audit policy). Stays in your overlay.

The boundary is **which repository the line of code lives in.** Smelting
decides that boundary deliberately instead of letting it drift.

> **Ownership gate — read this before any heuristic below.** Some code
> belongs to the consumer repo by *ownership*, not by technical shape:
> a contracted deliverable (e.g. an SOW work product the client owns),
> a product's proprietary feature, domain/business logic that is the
> reason the consumer exists. **This code is slag no matter what** —
> even if it looks generic, even if a `cmp -s` says it is byte-identical
> to upstream. Ownership is decided by contracts and product
> boundaries, not by whether a line *could* be reused by a hypothetical
> other downstream. For owned code, "identical to upstream" is not a
> green light to delete the overlay — it is **evidence the boundary was
> already breached** (the deliverable was wrongly copied upstream). The
> fix is to *pull it back* into the overlay and *remove it from
> upstream*, the opposite of a normal smelt. Every heuristic below
> (the <15% diff smell, the byte-identical "pure waste" rule, the
> decision tree) is subordinate to this gate. When you cannot state in
> one sentence that a file is generic platform IP that the upstream
> framework legitimately owns, it is slag — stop.
>
> **The observed failure mode is over-upstreaming, not under-upstreaming.**
> In practice agents put too much in the upstream and assign too little
> to the consumer repository: technical heuristics (byte-identity, low
> diff %, "looks generic") all push code UP, while the ownership force
> that pushes code DOWN exists only on paper — so the drift is one-way.
> One past over-smelt deleted ~447 contracted-deliverable files from a
> consumer repo because they were byte-identical to copies that should
> never have been upstream in the first place. Calibrate accordingly:
> the default for any uncertain file is the CONSUMER repo, an
> upstreaming decision needs the explicit one-sentence ownership
> justification (the reverse never does), and a periodic reverse audit
> — "which upstream files are really the consumer's deliverable?" — is
> mandatory, not optional. The reverse audit has its own procedure
> below.

## Three directions

This skill operates in three directions. Each has its own audit, pre-flight,
and ordered steps:

| Direction | Movement | Trigger |
|---|---|---|
| **Forward smelt** | overlay → upstream | A generic fix/capability lives in the overlay |
| **Reverse smelt** | upstream → overlay | Consumer-owned code found upstream |
| **Upstream-side adoption** | upstream reads a downstream overlay | The upstream maintainer spots adoptable metal |

All three share the ownership gate. A file can move in either direction over
its life; the gate decides, the direction follows the verdict.

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
  the whole file — **but only after clearing the ownership gate above.**
  Byte-identical to upstream proves *redundancy*, never *ownership*. If
  the file is owned deliverable / proprietary domain logic, identical
  content means the boundary was already breached upstream; reverse it
  (pull back to overlay, remove upstream), don't delete the overlay.
- **An upstream file references consumer-owned signals** — tenant names,
  brand strings, contract/issue IDs (`CA-*`, `BR-*`, `OM-*`), downstream
  issue numbers, "contact <consumer> support", "witnessed live on
  <consumer> staging". That file is a reverse-smelt candidate, not
  forward metal.
- **A consumer built substantial machinery around an upstream seam.**
  The seam is upstream; the capability layer that makes the seam useful
  (membership, roles, workflow) evolved only downstream. The missing
  upstream half is the smelt candidate — see "Pattern extraction" below.

## Triggers during ordinary work (do not wait for /smelt)

The heuristics above fire only when someone runs the audit. Most smelt
opportunities surface while doing something else. Pause and run the smelt
decision tree when ANY of these happen — they are triggers, not suggestions:

- **Bug fix in a shared file.** The file has no provider-SDK import, no
  identity/tenant logic, no project-only strings. The fix likely belongs
  upstream — check for an upstream counterpart BEFORE writing the fix,
  not after.
- **Deploy bring-up.** You are standing up a stage or fixing a Dockerfile,
  compose file, reverse-proxy config, plugin script, CI workflow, or env
  plumbing. These are generic infrastructure; bugs found here are almost
  always metal (image-build drift, template rot, plugin contracts,
  ingress/CSP wiring). Audit every deploy-path file you touch for a
  project-only reason before keeping it in the overlay.
- **Code review of overlay files.** Flag: (a) tests referencing
  consumer-only paths for generic behavior, (b) test-bootstrap hacks
  (fixture path juggling) that exist only because generic code lives in
  the overlay, (c) generic helpers with no project seam.
- **Doc authoring or porting.** Generic operational/architectural
  markdown written in the overlay is metal too. Same ownership question:
  would another downstream want this doc verbatim? De-brand before
  moving (see "Doc smelting").
- **You cannot name the upstream counterpart.** An overlay file with no
  upstream counterpart is not automatically slag — run the orphan metal
  scan below before assuming it is project-specific.
- **You register with a seam.** If you build policy infrastructure
  around an upstream extension point (register a resolver, fill a
  registry, implement an overlay-side Protocol), ask whether the *rest*
  of that capability — the part the seam exists to enable — belongs
  upstream too. A seam with no upstream substance is an unfinished
  smelt.

## Decision: metal or slag?

Walk the filters top-down. First YES wins.

```
Is this owned deliverable / proprietary / domain-defining code?
(contracted work product the consumer owns, a product's secret-sauce
feature, the business logic that is the consumer's reason to exist)
       └─ YES → slag (overlay) — ALWAYS, even if byte-identical to
                upstream. If it is already identical/present upstream,
                the boundary was breached: pull back + remove upstream.
       └─ NO  → ↓
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
Depends on a type, exception, config key, or Protocol that is
consumer-owned (or scheduled for pull-back in a reverse smelt)?
       └─ YES → generalize the seam first: land a neutral upstream
                 type, map it to the consumer type in the overlay
                 adapter, de-brand the diff, THEN re-walk this tree
       └─ NO  → ↓
Pure refactor / bug fix / new test that helps a hypothetical *other*
downstream of the same framework as much as this project?
       └─ YES → metal (upstream)
       └─ NO  → slag by default. A written justification is only valid
                if it argues the file is generic platform IP the
                upstream framework owns; uncertainty resolves to the
                overlay.
```

Hard architectural invariant: **overlay imports from upstream; upstream
never imports from overlay.** If a candidate change would need upstream to
call into project code, the candidate isn't a smelt — it's an upstream
extension point that the project then configures.

### Pattern extraction (alloys that have no file to diff)

The audits below compare files that exist on both sides. A whole pattern can
be metal without any near-copy existing: a consumer feature that is mostly
**scaffolding** for a domain concept — a work container, its cards/pages,
project-scoped routes, per-entity metering — where only the domain content
is consumer-owned. Two signals find these:

- **Consumer built substantial machinery around an upstream seam** (a
  registerable resolver, a factory hook, a config contract). The seam was
  smelted; the substance around it wasn't. The missing upstream half is
  the candidate — e.g. a visibility seam upstream that exists but is
  never *registered*, while the downstream carries the entire
  role/membership capability layer the seam enables. The upstream fix is
  usually "make the seam's default real and gate enforcement through it,"
  not "copy the downstream policy."
- **A consumer feature is 80% scaffolding for a domain concept.** Project
  cards → project-scoped routes → bounded content → per-project metering
  is a *pattern*; the domain (which kind of project) is the slag. Extract
  the container, parameterize the domain, leave the domain in the overlay.

These candidates are invisible to byte-identity and diff-percentage
audits — nothing is a near-copy. They are found by the triggers above
(code review, deploy bring-up, "can't name the counterpart") plus this
question: **when a downstream builds policy infrastructure around a
platform seam, what upstream half is missing?**

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

### Generalize the seam, don't copy the coupling

When the overlay code is good but *hardened to the consumer* — it raises a
downstream-specific error type, imports a consumer policy module for a
constant, or resolves a consumer identity inline — the smelt is a **seam
generalization**: land the algorithm upstream with the consumer-shaped
dependency injected (a parameter, a Protocol, a registered resolver), and
let the overlay keep supplying the consumer shape. Do not upstream the
consumer vocabulary to make the copy easy. Example shape: a message-budget
algorithm that raises the downstream's `GatewayViolation` becomes an
upstream `PromptBudgetExceeded(ValueError)`; the overlay's gateway policy
module catches it and maps to its own type.

## Pre-flight (mandatory)

Before touching your canonical upstream checkout, verify:

1. **Upstream working tree is clean** —
   `git -C <upstream> status --short`. If another agent has unstaged
   changes there, DO NOT step on them. Either continue your work in
   the overlay until that agent commits, OR coordinate via the user.
   Pushing your changes on top of someone else's WIP commits their WIP
   under your branch.

2. **Submodule pointer is current** - against the branch the
   submodule's refspec actually tracks (check
   `git -C <submodule> config remote.origin.fetch`; a mirror pinned to
   `production` has a stale or absent `origin/development` ref, and a
   plain `git fetch origin` will not fix it). If the submodule is
   behind, your overlay diff may already be partially upstream (do the
   bump first, re-audit):
   ```bash
   MIRROR_BRANCH=production   # the branch this submodule tracks
   git -C <submodule> fetch origin "+refs/heads/$MIRROR_BRANCH:refs/remotes/origin/$MIRROR_BRANCH"
   git -C <submodule> merge-base --is-ancestor HEAD "origin/$MIRROR_BRANCH" \
       || echo "SUBMODULE BEHIND - bump first, re-audit"
   ```

3. **Submodule is clean** —
   `git -C <submodule> status --short` should be empty. Run
   `git -C <submodule> clean -fd` if not. A dirty submodule will
   silently contaminate `cmp -s` audits. Always run the clean-submodule
   check before trusting byte-identical or low-diff overlay counts.

## The forward workflow (overlay → upstream)

### 1. Scope the change in the consumer repo first

Make the smallest possible commit on `development` so you have a
working baseline. Don't try to smelt code that doesn't compile yet.

### 2. Run the smelt audit

```bash
cd "$(git rev-parse --show-toplevel)" || exit 1
OVERLAY=overlays/files        # your overlay tree root
SUBMODULE=upstream            # your upstream submodule dir

echo "=== candidates: run the ownership gate on each BEFORE upstreaming ==="
# A near-copy is an INPUT to the gate, never a conclusion. For a
# consumer-owned file, a near-copy is evidence of a breach upstream
# (pull back), not waste to delete from the overlay.
# Math note: `diff` counts < and > lines, so every REPLACED line counts
# twice while additions count once - additive deltas flag at ~2x the
# sensitivity of edit deltas. Your CI mechanization (multiset excess)
# removes the double-count; treat the raw number as approximate.
for f in $(find "$OVERLAY" -type f \( -name '*.py' -o -name '*.ts' -o -name '*.tsx' \
      -o -name '*.yml' -o -name '*.yaml' -o -name 'Dockerfile*' -o -name '*.sh' \
      -o -name '*.md' -o -name '*.json' \) \
      ! -path '*/__pycache__/*' ! -path '*/tests/*' ! -path '*/__tests__/*' \
      ! -name '*.ico' ! -name '*.png' ! -name '*.jpg'); do
  upstream="$SUBMODULE/${f#$OVERLAY/}"
  [ -f "$upstream" ] || { printf 'GONE-UPSTREAM %s (counterpart deleted - owned pull-back that must NOT be re-smelted?)\n' "${f#$OVERLAY/}"; continue; }
  ol=$(wc -l < "$f"); ol=${ol// /}
  diff_lines=$(diff "$f" "$upstream" 2>/dev/null | grep -cE '^[<>]' || true)
  pct=$((diff_lines * 100 / (ol + 1)))
  [ "$pct" -lt 15 ] && [ "$ol" -gt 40 ] && printf '%3d%% %4d/%4d %s\n' "$pct" "$diff_lines" "$ol" "${f#$OVERLAY/}"
done | sort -n

echo ""
echo "=== orphan metal scan: overlay-only files that look generic ==="
# Consumer-domain terms - extend per project (tenant names, product names,
# cloud, domain nouns). Matches CONTENT and PATH: a file can be consumer-
# owned by its directory or filename alone (hic_*, fda_*, simulator_*)
# even when its body reads generically.
DOMAIN_RE='(boto3|azure|google\.cloud|<consumer-brand>|<tenant-name>|<domain-terms>)'
for f in $(find "$OVERLAY" -type f \( -name '*.py' -o -name '*.ts' -o -name '*.tsx' \) \
            ! -path '*/__pycache__/*' ! -path '*/tests/*' ! -path '*/__tests__/*'); do
  upstream="$SUBMODULE/${f#$OVERLAY/}"
  [ -f "$upstream" ] && continue          # only files with NO upstream counterpart
  rel="${f#$OVERLAY/}"

  # Ownership gate lives here: a branded path or branded content is slag,
  # even if the body reads generically.
  if printf '%s' "$rel" | grep -qiE "$DOMAIN_RE"; then continue; fi
  has_sdk=$(grep -cE 'import (boto3|azure|google\.cloud)|from (boto3|azure|google\.cloud)' "$f" 2>/dev/null || echo 0)
  has_domain=$(grep -ciE "$DOMAIN_RE" "$f" 2>/dev/null || echo 0)
  [ "$has_domain" -gt 0 ] && continue

  base=$(basename "$f" | sed -E 's/\.(py|tsx?)$//')
  has_test=$(find "$OVERLAY" -type f \( -name "test_${base}*" -o -name "${base}.test.*" \) | head -1)

  printf '%-18s %s (sdk=0 domain=0 test=%s)\n' \
    "ORPHAN-METAL?" "$rel" "$([ -n "$has_test" ] && echo yes || echo no)"
done | sort -k2

echo ""
echo "=== orphaned / stale overlay TESTS (the 1:1 migration rule, enforced) ==="
for f in $(find "$OVERLAY" -type f \( -name 'test_*.py' -o -path '*/tests/*' \
      -o -name '*.test.ts' -o -name '*.test.tsx' -o -path '*/__tests__/*' \) \
      ! -path '*/__pycache__/*'); do
  upstream="$SUBMODULE/${f#$OVERLAY/}"
  if [ -f "$upstream" ] && cmp -s "$f" "$upstream"; then
    printf 'STALE-TEST %s (identical to upstream test - migrate with the smelt or delete)\n' "${f#$OVERLAY/}"
  elif [ ! -f "$upstream" ]; then
    printf 'OVERLAY-ONLY-TEST %s (which source did this test follow? if the source smelted upstream, the test must too)\n' "${f#$OVERLAY/}"
  fi
done | sort

```

Three patterns from the audit output:

| Pattern | Upstream PR shape |
|---|---|
| **One-field-add copy** | Add the field (with `Optional[T] = None` default for back-compat) directly upstream. Delete the entire overlay file once upstream lands. |
| **Tenant/provider policy override** | Extract a Protocol or factory hook upstream. Overlay shrinks to a small project-specific implementation. |
| **Route / registry copy** | Make upstream's registry `extend()`-able or scan a directory. The overlay contributes a small registration call. |

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

### 5. De-brand before you push

Upstream must read as the framework's own code. Before pushing:

- Strip consumer names, tenant/product strings, contract IDs
  (`CA-*`, `BR-*`, `OM-*`, `D-0*`), downstream issue numbers, and
  "witnessed live on <consumer> staging" narration from docstrings,
  comments, and test names.
- Generalize consumer-shaped error types/vocabularies into upstream
  types (see "Generalize the seam").
- Keep the WHY; the incident belongs to the downstream's history, not
  the framework's.
- Add a hygiene gate if the repo has one (a pytest that greps the new
  files for banned consumer terms is cheap and permanent).

### 6. Push to the upstream repo

```bash
cd <upstream>
git push origin feat/<scope>
PUSHED_SHA=$(git rev-parse HEAD)
```

If your upstream replicates to a separate read-only mirror that the
submodule tracks, a mirror Action fires within ~1 min.

### 7. Wait for the mirror — verify by SHA

If the submodule tracks a mirror, wait for the SHA to appear before
bumping (skip this step if the submodule tracks the upstream directly):

```bash
mirrored=""
for _ in $(seq 1 30); do                      # 5 min at 10s - matches the failure-mode table
  mirrored=$(git ls-remote <mirror-url> "refs/heads/feat/<scope>" | cut -f1)
  [ "$mirrored" = "$PUSHED_SHA" ] && break
  sleep 10
done
[ "$mirrored" = "$PUSHED_SHA" ] || { echo "mirror did not pick up $PUSHED_SHA in 5 min - check the mirror Action" >&2; exit 1; }
echo "mirror synced: $PUSHED_SHA"
```

### 8. Bump the submodule

```bash
cd <consumer-repo>/<submodule>
# Fetch the SHA explicitly - the submodule's refspec may track only the
# mirror's default branch, so a plain `git fetch origin` will NOT download
# your feature branch and `git checkout $PUSHED_SHA` fails as unknown.
git fetch origin "refs/heads/feat/<scope>:refs/remotes/origin/feat/<scope>" \
                 "refs/heads/<mirror-branch>:refs/remotes/origin/<mirror-branch>"
git checkout "$PUSHED_SHA"
cd ..
git add <submodule>
git commit -m "chore(upstream): bump submodule to $PUSHED_SHA — <one-line rationale>"
```

**Submodule pointer must be a monotonic upstream superset.** Before
checkout, verify the new SHA contains every commit any current
consumer branch references:
`git -C <submodule> merge-base --is-ancestor <old-sha> <new-sha>`.

### 9. Delete or shrink the overlay

If upstream landed the field/behaviour the overlay was replicating,
the overlay file should now be byte-identical to upstream after rsync.
Delete it:

```bash
# Verify identical against the PRISTINE bumped upstream. Do not rsync
# first: rsync makes the two identical by construction, so a following
# `cmp` always "passes" and proves nothing.
git -C <submodule> clean -fd
git -C <submodule> show "HEAD:path/to/file" | cmp -s - <overlay>/path/to/file \
    && echo "safe to delete"

# Then remove the overlay:
git rm <overlay>/path/to/file
```

If upstream landed a Protocol and the overlay carries the
implementation, the overlay shrinks to just the project-specific bit.

### 10. Open the upstream PR

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

### 11. Run an automated review before promoting draft → ready

Run your second-opinion reviewer against the diff and address its
findings before flipping the PR to ready.

## The reverse audit (upstream-side scan — run periodically)

The forward audit compares overlay ↔ upstream files. It can never see the
opposite leak: consumer-owned content that was committed upstream. That
requires scanning the UPSTREAM tree for consumer signals. Run this
quarterly and after any big downstream push:

```bash
UPSTREAM=~/code/<upstream>       # canonical upstream checkout, clean tree
OUT=reverse-audit-$(date +%F).md

{
  echo "# Reverse smelt audit $(date +%F) — consumer-owned signals in upstream"
  echo
  echo "## Brand / tenant / contract strings (consumer-owned by definition)"
  grep -rnE '\b<consumer-brand>\b|<tenant-tag>|CA-[0-9]{2}|BR-[0-9]+|OM-[0-9]+|D-0[0-9]|SOW ' \
    "$UPSTREAM/backend/src" "$UPSTREAM/frontend/src" \
    --include='*.py' --include='*.ts' --include='*.tsx' --include='*.md' || true
  echo
  echo "## Domain-shaped services (verify ownership gate per package)"
  for pkg in <domain-packages>; do
    d="$UPSTREAM/backend/src/services/$pkg"
    [ -d "$d" ] && echo "$pkg: $(find "$d" -name '*.py' | wc -l) files, $(find "$d" -name '*.py' -exec cat {} + | wc -l) LOC"
  done
  echo
  echo "## Downstream issue references buried in upstream code"
  grep -rnE '#[0-9]{3,4}|bug ?[0-9]{3,4}|staging 20[0-9]{2}-' \
    "$UPSTREAM/backend/src" || true
} > "$OUT"
echo "wrote $OUT — classify each hit through the ownership gate before acting"
```

Produce the named artifact. Classify every hit through the ownership gate:
consumer-owned by definition (brand/contract strings), domain-shaped
(apply the gate per package), or a stale comment (fix in place).

## The reverse workflow (upstream → overlay pull-back)

For files the reverse audit proves are consumer-owned:

1. **Classify** every flagged upstream file through the ownership gate.
2. **Port upstream-only bits to the overlay FIRST** — anything upstream
   gained since the leak (imports, router registrations, tests, schema
   columns, fixes) must be replicated or shimmed in the overlay so the
   downstream keeps building without the upstream copies.
3. **Prove the overlay stands alone** — build a scratch tree from the
   CURRENT pinned submodule + overlay and run its suite against a submodule
   SHA that still contains the files.
4. **Only then** `git rm` upstream (moving the tests too, per "Leaving a
   regression test behind"), PR, wait for the mirror, bump the submodule
   (monotonic superset).
5. Rebuild downstream. Only now delete any overlay dead weight.

**ORDER IS THE CONTRACT: overlay first, upstream removal second.**

Anti-pattern: **"Deleting upstream before the overlay can stand alone."**
The moment the upstream PR merges and consumers bump, every checkout that
referenced those files breaks. The monotonic-superset rule does not save
you — file deletion is a *content* regression, not an ancestry one. And
every upstream commit that touches the leaked code deepens the eventual
pull-back diff; each day of "we'll pull it back later" is archaeology
budget. The leak is also live while it lasts: every upstream fix to the
owned code is a fix the consumer doesn't control.

## Upstream-side adoption (pulling metal out of a downstream overlay)

The upstream maintainer may run this skill in reverse-reading mode: the
downstream overlay is a **read-only reference** (never commit to it, never
rsync into it, never PR into it — same discipline as the read-only mirror).

1. Scan the overlay with the orphan metal scan above (from the upstream
   side, the overlay is where un-smelted metal hides).
2. Apply the ownership gate *from the upstream side*: adopt only what
   passes the one-sentence generic-IP test. When in doubt, don't adopt —
   adoption re-runs the cardinal-sin risk in reverse.
3. Generalize the seam (see "Generalize the seam") — strip consumer
   error types, identity lookups, brand strings.
4. Land the PR shaped like the forward smelt: generic module + `tests/`
   in the same commit, no downstream defaults.
5. The downstream deletes its now-duplicated copy at its next submodule
   bump. If it doesn't, the near-copy audit will flag it.

## Deploy smelting

A fresh stage bring-up is the densest smelt-discovery event there is.
Infrastructure bugs (image-build drift, package availability, template
pin rot, plugin contracts, ingress/CSP wiring, pool/network posture) are
generic by construction — the deploy path is shared framework code; the
stage is the only thing that differs. **After every deploy, classify
every fix you made**: "would this bite any downstream of this framework
on a fresh account?" If yes, it's metal — the decision tree applies.
Deploy-path files (`Dockerfile*`, compose, Caddyfile, plugins, CI
workflows) belong in every smelt audit; most overlay carry them without
a second thought.

## Doc smelting

Markdown follows the same ownership gate. Generic engineering playbooks,
operations discipline, and architecture docs written by a consumer are
metal; product/compliance/deliverable docs are slag. When porting:

- **De-brand**: strip consumer names, tenant tags, contract IDs, provider
  specifics, and issue numbers. Replace consumer case studies with the
  generic lesson or framework-native examples.
- **Gate it**: add an automated hygiene test (a pytest asserting the
  ported docs contain none of a banned-term list) so the slag can't creep
  back. Existence + non-emptiness + banned-term contract, per doc.

## Worked examples

Shortened case records. Classify each new situation against them.

| Case | Shape | Lesson |
|---|---|---|
| Five generic modules living overlay-only (audit hook, prompt includes, text repair, JSON sniff, message budget) | Orphan metal | Orphans are invisible to near-copy audits; the orphan metal scan + "can't name the counterpart" trigger found them. One needed a seam generalization (consumer error type → upstream exception). |
| ~127 files / ~22k LOC of consumer-owned domain code committed upstream | Reverse smelt | Landed by a "restore omitted tree" commit; *still edited upstream months later*. Each upstream edit deepened the pull-back diff. The 7 upstream-only files had to be rescued to the overlay BEFORE removal — ordering is the contract. |
| A stage bring-up producing 10+ fixes: image packages missing from a newer base OS, version-pin rot, plugin aborting phase-1 of a two-phase deploy, compose variable-parsing, ingress CSP missing the API host, search contract null-vs-list | Deploy smelt | All generic, all found only by deploying, all invisible to a code-only audit glob. The deploy loop is the best smelt detector there is. |
| A platform seam (registerable visibility resolver) upstream, with the entire capability layer (role matrix, membership, roster rules) evolved downstream-only; the upstream per-project gate ignores its own user argument | Pattern extraction | The seam was fully smelted; the substance wasn't. Discovery trigger: consumer machinery built *around* an upstream seam. The pull-up is the missing upstream half — the authorization core, with the consumer's identity resolution extracted into a registered resolver. |
| Three waves of playbooks/docs ported with a banned-term pytest | Doc smelt | Docs are metal too; the hygiene gate is what keeps the slag out after the port. |

## Anti-patterns to refuse

- **Smelting on top of another agent's WIP.** Their uncommitted
  changes in the upstream checkout will be committed by you and pushed
  under your branch. Wait for them, or coordinate via the user.
- **Overlay-as-fallback.** "We'll keep the overlay just in case the
  upstream PR is rejected." If you're shipping the same logic on
  both sides you're paying the carrying cost twice. Pick one.
  *Time-box exception:* when the upstream review won't fit a deploy
  window, a temporary overlay delta is acceptable — but it must ship
  with an open upstream issue (or PR) in the same commit, and the
  overlay dies the moment the upstream change lands. An overlay delta
  without a tracking upstream change is the anti-pattern; a time-boxed
  one with a tracker is not.
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
- **Upstreaming owned deliverables (the cardinal sin).** Never move
  contracted work product, proprietary features, or domain-defining
  business logic upstream — regardless of how generic it looks or
  whether it is byte-identical to existing upstream code. Doing so
  silently reassigns ownership of the consumer's code to the framework
  vendor. On a signed deliverable (an SOW work product the client
  owns), that is not just carrying-cost waste — it misrepresents who
  owns the code and is an integrity breach. The audit question is
  literal: *if the owner opened the upstream repo and found their
  deliverable there, could you justify it?* If not, it is slag, and any
  copy already upstream must be pulled back and deleted from upstream.
  Schema/migrations for owned tables follow the code: the deliverable's
  database DDL lives in the owner's repo too, never upstream.
- **Leaving a regression test behind.** If behavior moves upstream,
  its test migrates too. The consumer's tests should only cover the
  project implementation/adapter — never the generic behavior that's
  now upstream-owned.
- **Deleting upstream before the overlay can stand alone.** The reverse
  workflow's ordering rule. Removing upstream files before the overlay
  carries them (and their tests) breaks every consumer checkout at the
  next bump — and ancestry-superset checks do not catch it, because
  deletion is a content regression. Rescue first, verify the overlay
  tree builds, then remove upstream.
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
| Reverse pull-back breaks downstream at bump | Owned files removed upstream before the overlay could stand alone | Rescue upstream-only bits into the overlay first; prove the scratch tree builds against the current pin; only then remove upstream |
| Orphan scan returns nothing but the overlay feels heavy | Domain-term regex is stale (consumer terms renamed) | Refresh `DOMAIN_RE`; the ownership gate, not the regex, is the ground truth |

## Measure success

Different directions, different numbers — report the one for the direction
you ran:

- **Forward smelt**: overlay LOC delta in the consumer PR description
  (target: negative), plus the audit re-run.
- **Reverse smelt**: consumer-owned LOC removed from upstream and now
  carried in the overlay, and the count of consumer-signal grep hits in
  upstream trending to **zero**.
- **Upstream-side adoption**: overlay files deleted downstream at the next
  submodule bump.
- **Pattern extraction**: enforcement routes covered by the seam (e.g.
  "N of M project routes now gate through the resolver") — not LOC.

A smelt that doesn't shrink overlay carrying cost (or doesn't unblock a future
shrink via split-then-smelt, or close a seam-enforcement gap) was a
code-mover, not a code-separator.

## See also

- `/shatter` — split a large file into focused pieces; the prerequisite
  to smelting when an overlay file is a big alloy.
- `/deslop` — the full code-quality pass; when it touches overlay files,
  apply the smelt triggers above to whatever it flags.