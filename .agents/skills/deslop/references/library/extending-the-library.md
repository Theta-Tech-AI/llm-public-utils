---
name: deslop-extending-the-library
description: How to add a principle to this library — discovery, research, drafting, the two indexes, and the publish path.
---

# Extending the Library

> "The library is only as good as the gap it just closed."

Deslop is not a fixed document. It is a **principles library**, and the reason to keep it open is that the
next piece of slop will not resemble anything already in it. This file is the procedure for adding a
principle: how to find a real gap, how to research and draft it, where it goes, which indexes it must
appear in, and how it reaches consumers.

The governing rule is **the discovery step, not the writing**. A principle that restates a sibling under a
new name makes the library worse — the auditor now has two rows to cross-reference and no way to tell which
one a finding belongs to.

## 1. Discovery — build the list before you write a word

1. **Read `SKILL.md` and every file under `references/`, recursively.** Not the indexes — the principle
   files themselves. This is the only way to know what the library already says, and it is the step that
   gets skipped.
2. **Grep the concept, in the library's own vocabulary.** Near-duplicates hide inside another principle's
   supporting lines more often than they appear as their own file. Search the concept, its common synonyms,
   and the jargon of the adjacent fields:

   ```bash
   grep -rin 'sentinel\|silent default\|absence\|optional\[' references/
   ```

3. **Check the nearest siblings by reading them, not by their titles.** Three boundaries decide most
   placement questions: does an existing principle already *name* this failure (then extend it instead), does
   one own the *mechanism* (then link to it rather than restate it), or does one merely *touch* the topic as
   an aside (then the gap is real)?
4. **Announce the choice and what you avoided.** State the gap, the principle chosen, and the siblings you
   rejected it against. If the operator cannot see why this is not a duplicate, the answer is usually that it
   is one.

## 2. Research

Gather, in this order — the formal definition, the origin and who named it, the trade-offs and the
circumstances in which it is *wrong*, the common violations, and language-local implementations (Python
first). **Verify claims at the source rather than from a search snippet**, and prefer a number you produced
yourself: if the principle makes an assertion about a metric or a tool, run the tool and paste the real
output. A principle file that cites a measurement nobody can reproduce is worse than one that cites none.

## 3. Draft — the house format

Write to `/tmp/new_principle.md` in this shape, then move it into place:

```markdown
---
name: deslop-<category>-<slug>
description: Deslop principle — <Name>: <one-line essence>.
---

# <Name>

> "<a short, attributed, verifiable line>"
> — <attribution>

<The essence in one or two paragraphs: what it is, why it matters, when it applies.>

## <Subsections as needed — the tells, the diagnostics, the method>

```python
# ❌ <what is wrong, named>
...
# ✅ <the same thing, corrected>
...
```

In relation to other principles, <name> <how it sits among its neighbours>:

| Principle | Relationship |
|-----------|--------------|
| [**<Sibling>**](<relative path>) | <the boundary, stated — not "related to"> |

## Summary

1. **<Point>** — <one line>
```

Style notes, all of them load-bearing:

- **The ❌/✅ pair is the point of the file.** Every principle must be recognisable in code. If you cannot
  write the pair, the principle is not yet understood well enough to add.
- **The relation table states boundaries, not admiration.** "Covers errors you can *detect*; this covers the
  case that is undetectable" is a boundary. "Related to fail-fast" is noise.
- **Keep it ~120–150 lines.** A reference, not a textbook.
- **Anonymize every worked example.** This repository is **public**: no client names, no repository paths, no
  internal issue or PR numbers, no product names. Quantities and magnitudes are fine; identifiers are not.

### The refinement loop (expand, then compact — three times)

Drafting once produces a summary of what you already knew. Each cycle: re-read the draft, research one
specific gap (real-world cases → common pitfalls → this principle against its nearest sibling), **expand**
with what the research adds, then **compact** — cut anything that does not change a reader's decision. The
density comes from the compaction, not from the expansion. Two or three cycles is where a file stops being a
restatement.

## 4. Merge — the two indexes, or the file is invisible

1. **Place the file** at `references/<category>/<slug>.md`: `clean-code/`, `architecture/`, `reliability/`,
   `data-layer/` — or propose a new category with its own index file and a matching row in `SKILL.md`.
2. **Add the row to the category index** (`references/<category>.md`), in the section that fits, with a
   one-line essence matching the style of its neighbours.
3. **Add the name to that index's frontmatter `description` list** — this is the list the router reads.
4. **Add the name to the category line in `SKILL.md`'s principle-index table.**
5. **Re-check the links.** Every relative link in the new file, and every link you touched, must resolve —
   `../architecture/<slug>.md` from a `clean-code/` file, `<slug>.md` for a sibling.

A principle that appears in no index is invisible to every future pass. The indexes *are* the discovery
surface; the principle file is the payload.

## 5. Publish

- **Branch and open a PR against `production`** — that is the default branch here, not `main`. There is no
  CI and no index generator in this repo: the reviewer is the only gate, so the index rows and the links are
  yours to get right.
- **Verify the PR, not the push** — `gh pr view <n> --json files,baseRefName,state`.
- **Consumers re-pin their own copies.** Projects install this library with `npx skills`, which records the
  source and a `computedHash` in `skills-lock.json`; after a merge, a consumer picks up the new principle
  with `npx skills update`. Nothing here can push the change into them.

## Pitfalls

- **The vendored copy lags.** A copy materialized inside a consumer repo may be missing files this library
  already has. Read *this* repository when checking for near-duplicates, never the vendored copy.
- **Do not restate a sibling.** `duplication.md` and `data-layer/slop-tells.md` are where near-duplicates
  most often hide.
- **Do not add a principle to fit a finding.** The order is: notice the gap, then find the principle. A file
  written to justify one code review reads like one.
- **Do not skip step 1 because the concept feels obviously missing.** Twice, the obvious gap turned out to
  be a paragraph inside another principle — and once, an apparent duplicate turned out to be a genuine gap
  once the siblings were read rather than skimmed.
