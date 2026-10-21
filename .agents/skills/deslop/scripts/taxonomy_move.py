#!/usr/bin/env python3
"""Reorganise references/ into a role taxonomy, rewriting every cross-link.

Run from the skill root (the directory holding SKILL.md):

    python3 scripts/taxonomy_move.py --apply

The taxonomy is by ROLE IN THE PASS, not by topic, because that is the question a reader has: "what am I doing
now, and what should I open?" Topic is already carried by the principle category (`principles/architecture/`).

    references/
      lenses.json              the principle partition and the triggers (data, not prose)
      stages/                  the four stages of a pass, each read at its own moment
      readings/                what a single reading carries: the audit protocol, the guardrail,
                               the dedup sweep, the detector rationale
      modes/                   the modes a pass can run in (campaign, loop-until-dry)
      principles/              <category>.md as the index, <category>/<slug>.md as the principles
      library/                 reading for when the library itself is the subject (extend it, measure
                               it, cite it, see it worked)

Everything under a directory has one role, so reachability becomes structural: a file's class is derivable from
its path, and `swarm_lenses.py --check` can fail on anything that has no role.
"""
from __future__ import annotations

import argparse
import posixpath
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "references"

MOVES: dict[str, str] = {
    # stages — one per moment of a pass
    "pass-planning.md": "stages/planning.md",
    "aggregating-findings.md": "stages/aggregation.md",
    "consolidating-and-triage.md": "stages/consolidation.md",
    "reporting-results.md": "stages/reporting.md",
    # readings — carried by a reading, not by a stage
    "auditing.md": "readings/auditing.md",
    "when-to-relax.md": "readings/when-to-relax.md",
    "duplication.md": "readings/duplication.md",
    "detecting-slop.md": "readings/detecting-slop.md",
    # modes
    "campaign-mode.md": "modes/campaign.md",
    "loop-until-dry.md": "modes/loop-until-dry.md",
    # library — about the library itself
    "extending-the-library.md": "library/extending-the-library.md",
    "measuring.md": "library/measuring.md",
    "further-reading.md": "library/further-reading.md",
    "case-study-simplification-agent-fleet.md": "library/case-study-simplification-agent-fleet.md",
    # principles — indexes move with their folders so intra-category links stay valid
    "architecture.md": "principles/architecture.md",
    "clean-code.md": "principles/clean-code.md",
    "data-layer.md": "principles/data-layer.md",
    "reliability.md": "principles/reliability.md",
}
for cat in ("architecture", "clean-code", "data-layer", "reliability"):
    for f in sorted((REF / cat).glob("*.md")):
        MOVES[f"{cat}/{f.name}"] = f"principles/{cat}/{f.name}"

LINK = re.compile(r"\]\(([^)#\s]+?\.(?:md|json|py))(#[^)\s]*)?\)")


def rewrite_links(text: str, old_rel: str) -> str:
    """Point every relative link at its new home."""
    new_rel = MOVES[old_rel]
    old_dir, new_dir = posixpath.dirname(old_rel), posixpath.dirname(new_rel)

    def sub(m: re.Match[str]) -> str:
        target, anchor = m.group(1), (m.group(2) or "")
        if target.startswith(("http://", "https://", "/")):
            return m.group(0)
        resolved = posixpath.normpath(posixpath.join(old_dir, target))
        if resolved not in MOVES:
            return m.group(0)          # outside references/ (scripts/, assets/) — scripts do not move
        new_target = posixpath.relpath(MOVES[resolved], new_dir or ".")
        return f"]({new_target}{anchor})"

    return LINK.sub(sub, text)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="perform the move (otherwise print the plan)")
    a = ap.parse_args()

    missing = [o for o in MOVES if not (REF / o).exists()]
    if missing:
        print(f"refusing: {len(missing)} source file(s) absent: {', '.join(missing[:5])}", file=sys.stderr)
        return 1

    plan = [(o, MOVES[o]) for o in MOVES]
    print(f"{len(plan)} file(s) to move:")
    for o, n in plan:
        print(f"  {o:55s} -> {n}")

    if not a.apply:
        return 0

    # 1. read + rewrite every file's links before anything moves
    rewritten: dict[str, str] = {}
    for old in MOVES:
        text = (REF / old).read_text()
        rewritten[old] = rewrite_links(text, old)

    # 2. move with git so history follows, then write the rewritten text
    for new in {n for n in MOVES.values()}:
        (REF / new).parent.mkdir(parents=True, exist_ok=True)
    for old, new in MOVES.items():
        subprocess.run(["git", "mv", str(REF / old), str(REF / new)], check=True)
    for old, new in MOVES.items():
        (REF / new).write_text(rewritten[old])

    # 3. report any link that no longer resolves, resolved against the file's new directory
    broken = []
    for new in MOVES.values():
        for target in LINK.findall((REF / new).read_text()):
            if target.startswith(("http://", "https://", "/")):
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(new), target))
            if not (REF / resolved).exists():
                broken.append(f"{new} -> {target}")
    print(f"links rewritten; unresolved after the move: {len(broken)}")
    for b in broken:
        print("  " + b)
    return 0 if not broken else 2


if __name__ == "__main__":
    sys.exit(main())
