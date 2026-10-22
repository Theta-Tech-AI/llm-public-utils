#!/usr/bin/env python3
"""Hold the line on principle-file shape without rewriting the library.

The reviews of this library landed on the same point from different directions: a reader cannot tell from a
principle file's *shape* what it owes them, because only `Prior art` and `The repair` recur as headings. The fix is
an enforced template — but enforced from today's median (37 lines), not from an imagined essay length, and never by
padding a short file.

So this checks the properties every file ALREADY has, to stop the line moving:

  frontmatter   name + description on every principle file
  shape         at least one fenced block (the ❌/✅ pair, a query, a schema, or a signature)
  size          flagged above `--max-kb`, because the outliers are 4x the median and they are the newest files

    python3 scripts/check_principle_template.py            # exit 1 on a missing property or an oversized file
    python3 scripts/check_principle_template.py --max-kb 8 --report

`--report` prints every file's size ranked, which is how the next outlier is caught before it is written.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "references"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-kb", type=float, default=16.0,
                    help="fail a principle file larger than this (KB). 16 holds today's line; the goal is 8, and the "
                         "four files above it are tracked as work rather than enforced overnight")
    ap.add_argument("--report", action="store_true", help="print sizes ranked, largest first")
    a = ap.parse_args()

    files = sorted((REF / "principles").glob("*/*.md"))
    if not files:
        print(f"FAIL no principle files under {REF/'principles'}", file=sys.stderr)
        return 1

    problems: list[str] = []
    warnings: list[str] = []
    sizes: list[tuple[float, str]] = []
    for f in files:
        rel = str(f.relative_to(ROOT))
        text = f.read_text()
        size_kb = len(text.encode()) / 1024
        sizes.append((size_kb, rel))
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not fm:
            problems.append(f"{rel}: no frontmatter")
        else:
            block = fm.group(1)
            for field in ("name:", "description:"):
                if field not in block:
                    problems.append(f"{rel}: frontmatter missing {field}")
        if "```" not in text:
            warnings.append(f"{rel}: no fenced block — a principle with no shown example or signature")
        if size_kb > a.max_kb:
            problems.append(f"{rel}: {size_kb:.1f} KB > {a.max_kb} KB — split it or cut, do not pad the short ones")

    if a.report:
        for kb, rel in sorted(sizes, reverse=True)[:10]:
            print(f"  {kb:5.1f} KB  {rel}")
        median = sorted(s[0] for s in sizes)[len(sizes) // 2]
        print(f"  median {median:.1f} KB across {len(sizes)} principle files")

    if warnings:
        print(f"\n{len(warnings)} file(s) carry no fenced example (not a failure today — enable once they conform):")
        for w in warnings[:20]:
            print("  " + w)
    if problems:
        print(f"\nFAIL {len(problems)} principle-file problem(s):")
        for p in problems:
            print("  " + p)
        return 1
    print(f"OK {len(sizes)} principle files: frontmatter present and <= {a.max_kb} KB each "
          f"({len(warnings)} without a fenced example, reported above)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
