---
name: shatter
description: Break large files into focused, single-responsibility pieces. Use when a file exceeds size thresholds (~250 LOC frontend, ~400 LOC backend) or mixes multiple responsibilities.
---

# Shatter: Break Large Files Into Focused, Single-Responsibility Pieces

> We hate large files. A file that crosses the size threshold or holds more than
> one responsibility is a refactor target. `/shatter [file-or-directory]` finds
> the biggest offenders and splits them — safely, behavior-preserving, verified.

This is a focused companion to `/deslop`. Deslop covers all code-quality
principles; **shatter** is the single-minded "make this file small" pass.

## Thresholds

| Kind | Soft limit | Hard target |
|---|---|---|
| Frontend `.tsx` / `.ts` | ~250 lines | one responsibility per file |
| Backend `.py` | ~400 lines | one service responsibility per module |
| Hook | one hook per file | — |
| Test file | mirrors its source 1:1 | — |

A file over the soft limit is a *candidate*, not automatically a violation: a
large file that merely **composes** sub-components (mostly imports + wiring) is
acceptable. The real target is the file that **mixes responsibilities** — a page
that is also a state machine that is also five presentational components.

## Process

1. **Find the offenders.** Rank by size, excluding any read-only upstream
   submodule, generated data files, caches, and `node_modules`:
   ```bash
   git ls-files '*.tsx' '*.ts' '*.py' | grep -v <submodule-dir> \
     | xargs wc -l 2>/dev/null | sort -rn | head -40
   ```
   For files that live upstream (inside the submodule), shatter them in your
   canonical upstream checkout and smelt up — never edit the submodule directly.

2. **Read the file and name its responsibilities.** List every distinct thing
   it does: page layout, a state machine, CRUD handlers, presentational leaf
   components, helpers. Each cluster is a potential extraction.

3. **Pick extraction boundaries that minimize coupling and swap risk**, in order
   of preference (safest first):
   - **Pure leaf components / helpers** → sibling `*Parts.tsx` or a shared
     `components/common/` file. Zero behavior risk (pure function moves).
   - **Self-contained state machines** → a custom hook (`useXxx.ts`). Hooks
     take a **named deps object** and return a **named handlers object** — far
     less prone to same-typed argument swaps than a positional prop bag.
   - **Conditionally-rendered modal/panel clusters** → a `XxxModals.tsx`
     component. Pass props **by name** matching the originals.
   - **The main render body** → a `XxxWorkspace.tsx` — last, because it usually
     needs the widest prop surface (highest swap risk).
   - A single-use hook/component that exists ONLY to satisfy the line count is
     over-abstraction — don't extract it (a hook with one consumer is cosplay).

4. **Respect in-code refactor warnings.** If a comment says "do NOT collapse
   these / refactoring this broke X" (e.g. two audit-trail render paths that must
   stay distinct), you may *extract* the block but must NOT merge the distinct
   paths.

5. **Verify every split** — extraction is only safe if all of these pass:
   - `npx tsc -b` clean (proves all prop/closure wiring types).
   - The file's tests pass. **If there is no behavior test, add a render/mount
     smoke test FIRST** (mock the hooks/stores; assert it mounts and renders a
     key element). Validate the smoke test against the *current* file before you
     touch it, so it's a real baseline.
   - `npx vite build` (frontend) / the service's `pytest` (backend) succeeds.

6. **Commit per logical extraction**, smelt up if upstream, bump the submodule.

## What "shatter" produces

Before: one 800-line page that is layout + state + handlers + modals + leaves.

After: a ~250-line orchestrator that wires hooks and composes components, plus
`useXxxActions.ts` (handlers), `XxxModals.tsx` (modals), `XxxParts.tsx` /
`XxxWorkspace.tsx` (render), each under threshold and single-responsibility.
Readers fan out via go-to-definition instead of scrolling. The tradeoff —
more import lines at the top of each file — is a net win.

## Anti-patterns (don't do these)

- **Collapsing** distinct logic to save lines (merging two render paths that
  write different audit events, deduping two functions that only look alike).
- **Single-use abstraction** created solely to drop a line count.
- **Unverified extraction.** tsc-green is necessary but not sufficient for a
  prop bag — a render/mount test catches same-typed swaps tsc can't.
- **Editing the read-only submodule directly.** Shatter upstream files in your
  canonical upstream checkout, then smelt + bump.

## Output

For each offender: its responsibilities, the proposed file split (new file →
what moves into it), and the verification result (tsc / tests / build). Then
ask the user whether to apply, or apply directly if running under a standing
"shatter" goal.
