#!/usr/bin/env python3
"""Prove that every markdown in the skill is reachable by following links from SKILL.md.

No harness builds a manifest of a skill's files: only `SKILL.md` is loaded when the skill activates, and every
other file is read on demand **by path**. So `SKILL.md` is not merely instructions — it is the skill's table of
contents, and a reference it does not lead to (directly, or through an index that does) is a file nobody will
ever open. Nothing in any harness enforces that, and nothing notices when a file is renamed, added, or deleted.

This script is that enforcement, and it runs in CI so a reorganise cannot silently orphan a file:

    python3 scripts/check_reachability.py            # exit 1 and name every orphan
    python3 scripts/check_reachability.py --verbose  # also print the path each file was reached by

Rules:

- Links are markdown links ending `.md`, resolved **relative to the file that contains them** (the Agent Skills
  spec's own rule), and followed transitively from `SKILL.md`.
- Ignored paths: `http(s)://`, absolute paths, and anything outside the skill directory (a link to a sibling
  skill is legal and is not this skill's business).
- A file may be reached through an index (`references/principles/<category>.md` linking each principle), which
  is the intended shape: `SKILL.md` names ~20 entries, the indexes carry the rest.
"""
from __future__ import annotations

import argparse
import posixpath
import re
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # the skill directory
ENTRY = "SKILL.md"
LINK = re.compile(r"\]\(([^)\s]+?\.md)(?:#[^)]*)?\)")


def links_in(path: Path) -> list[str]:
    """Every .md link in a file, resolved to a path relative to the skill root."""
    out: list[str] = []
    base = path.parent
    for target in LINK.findall(path.read_text(errors="ignore")):
        if target.startswith(("http://", "https://", "/", "mailto:")):
            continue
        resolved = (base / target).resolve()
        try:
            rel = resolved.relative_to(ROOT.resolve())
        except ValueError:
            continue                                    # outside the skill (a sibling skill) — not ours to check
        out.append(rel.as_posix())
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verbose", action="store_true", help="print how each file is reached")
    ap.add_argument("--allow", default="", help="comma-separated paths to treat as intentional orphans")
    a = ap.parse_args()

    allow = {p.strip() for p in a.allow.split(",") if p.strip()}
    entry = ROOT / ENTRY
    if not entry.exists():
        print(f"FAIL no {ENTRY} at {ROOT}", file=sys.stderr)
        return 1

    # breadth-first walk from SKILL.md, remembering the shortest path to each file
    seen: dict[str, str] = {ENTRY: "(entry)"}
    order: list[str] = [ENTRY]
    queue: deque[str] = deque([ENTRY])
    broken: list[tuple[str, str]] = []
    while queue:
        current = queue.popleft()
        for nxt in links_in(ROOT / current):
            if not (ROOT / nxt).exists():
                broken.append((current, nxt))
                continue
            if nxt in seen:
                continue
            seen[nxt] = current
            order.append(nxt)
            if nxt.endswith(".md"):
                queue.append(nxt)

    on_disk = sorted(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*.md")
        if ".git" not in p.parts
    )
    orphans = [f for f in on_disk if f not in seen and f not in allow]

    print(f"skill: {ROOT.name}")
    print(f"markdown files on disk: {len(on_disk)}")
    print(f"reachable from {ENTRY}: {len(on_disk) - len(orphans)}")

    if a.verbose:
        for f in order:
            if f != ENTRY:
                print(f"  {f}  <- {seen[f]}")

    if broken:
        print(f"\nFAIL {len(broken)} broken link(s):")
        for src, dst in broken:
            print(f"  {src} -> {dst} (no such file)")
    if orphans:
        print(f"\nFAIL {len(orphans)} file(s) no link path reaches — SKILL.md is the manifest, and it misses these:")
        for f in orphans:
            parent = posixpath.dirname(f)
            index = f"{parent}.md" if parent else ENTRY
            print(f"  {f}   (link it from {index if (ROOT / index).exists() else ENTRY})")
    if broken or orphans:
        return 1
    print(f"\nOK every markdown is reachable from {ENTRY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
