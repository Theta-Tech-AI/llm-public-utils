#!/usr/bin/env python3
"""Emit per-lens audit prompts for a deslop swarm, and prove the assignment covers every principle.

The failure this script exists to prevent: a single neutral pass reads the four category indexes,
decides which principles "look implicated", and never opens the rest — measured, a principle whose
name is not a visible trigger (Separation of Concerns) is never opened at all. So coverage is made
structural rather than hoped for: the assignment is data, and this script refuses to emit anything
unless every per-principle file in the library belongs to exactly one lens.

Usage, from the skill root (the directory containing SKILL.md):

    python3 scripts/swarm_lenses.py --check                 # coverage report; exit 1 if incomplete
    python3 scripts/swarm_lenses.py --list                  # lens table
    python3 scripts/swarm_lenses.py --emit /tmp/deslop-swarm --target <dir> [--run <n>] [--only <lens>]

`--emit` writes /tmp/deslop-swarm/lens-<name>.md, one prompt per lens, plus manifest.txt holding the
per-lens file count. Feed each prompt verbatim to one agent; the prompt already contains the forced
reading list, the read-before-scan order, and the JSONL output contract that swarm_merge.py consumes.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "references"
MANIFEST = REF / "lenses.json"


def load() -> dict:
    with MANIFEST.open() as fh:
        return json.load(fh)


def principle_files() -> set[str]:
    """Every per-principle file: references/<category>/<slug>.md (top-level files are protocols)."""
    return {str(p.relative_to(REF)) for p in sorted((REF / "principles").glob("*/*.md"))}


def top_level_files() -> set[str]:
    return {p.name for p in sorted(REF.glob("*.md"))}


def classify(m: dict) -> tuple[dict[str, str], set[str]]:
    """Every markdown under references/ must be reachable by an enforced path. Returns (classes, all_files)."""
    classes: dict[str, str] = {}
    for lens, spec in m["lenses"].items():
        for f in spec["files"]:
            classes[f] = f"lens:{lens}"
        for idx in spec.get("indexes", []):
            classes[idx] = f"lens-index:{lens}"
        for f in spec.get("also_protocols", []):
            classes[f] = f"lens-protocol:{lens}"
    for f in m["shared"]["protocols"]:
        classes[f] = "lens-protocol:all"
    for f in m["shared"].get("stage_protocols", {}):
        classes[f] = "stage"
    for f in m["shared"].get("modes", {}):
        classes[f] = "mode"
    for f in m["shared"].get("library", {}):
        classes[f] = "library"
    everything = {str(p.relative_to(REF)) for p in REF.rglob("*.md")}
    return classes, everything


def audit(m: dict) -> tuple[list[str], list[str], list[str]]:
    assigned: dict[str, list[str]] = {}
    for lens, spec in m["lenses"].items():
        for f in spec["files"]:
            assigned.setdefault(f, []).append(lens)
    everything = principle_files()
    missing = sorted(everything - set(assigned))
    unknown = sorted(set(assigned) - everything)
    dupes = sorted(f"{f} -> {', '.join(l)}" for f, l in assigned.items() if len(l) > 1)
    # protocol files must exist too
    classes, everything_all = classify(m)
    named = set(classes)
    absent = sorted(n for n in named if not (REF / n).exists())
    problems = []
    # reachability: no markdown left behind — a file reachable by no enforced path is the silent gap
    unreachable = sorted(everything_all - set(classes))
    if unreachable:
        stray = [f for f in unreachable if "/" not in f]
        if stray:
            problems.append(f"{len(stray)} file(s) at the references root — the taxonomy has no role for them "
                            f"(stages/, readings/, modes/, principles/, library/): " + ", ".join(stray))
        problems.append(f"{len(unreachable)} markdown file(s) reachable by no enforced path "
                        f"(not a principle, lens protocol, lens index, stage reference or situational): "
                        + ", ".join(unreachable))
    unknown_kind = sorted(k for k, v in classes.items() if not v)
    if unknown_kind:
        problems.append("unclassified: " + ", ".join(unknown_kind))
    if missing:
        problems.append(f"{len(missing)} principle file(s) assigned to no lens: " + ", ".join(missing))
    if unknown:
        problems.append(f"{len(unknown)} assigned path(s) do not exist: " + ", ".join(unknown))
    if dupes:
        problems.append(f"{len(dupes)} file(s) in more than one lens: " + ", ".join(dupes))
    if absent:
        problems.append(f"{len(absent)} named protocol(s) do not exist: " + ", ".join(absent))
    return problems, sorted(everything), sorted(assigned)


PROMPT = """You are one audited lens in a deslop swarm pass. You are not the whole audit: {n_peers} peers \
are reading the same target through other lenses in parallel, and the orchestrator merges your report with \
theirs. Your value is depth inside your lens, not breadth outside it.

## 1. Read first, in full, before you look at any code

Read each file below completely — the whole file, not the index row. The first is your category index: read it
for the stance and the tells, then read every principle file in full. They are your lens, and your findings must
be expressed in their terms.

{reading_list}

Then write `{out_manifest}` — the read manifest, one absolute-or-reference-relative path per line, naming every
file you actually opened. It is checked against your assignment: a file you did not read cannot be claimed by you,
and a manifest missing a line is reported as a failed reading rather than a clean pass. This is the only
verification the protocol has that a lens read what it was given.

Your stance, in one line: {stance}

## 2. Then scan

Target: `{target}` (repo root `{repo}`).
Read the code in whole files, not snippets — a lens applied to fragments produces confident nonsense. Then \
report every violation **of your assigned principles** that you can substantiate by quoting the code.

Rules that bind you:
- READ-ONLY **with respect to the repository**. Do not modify, create, move or delete anything inside it, and do not run state-changing git commands. Your one permitted write is the findings file at the absolute path above, which lives outside the repo.
- Judge against your principles only. If you see something outside your lens, do not argue it — list it under \
`CROSS-LENS SIGHTINGS` in prose, one line each, so nothing is lost and nothing is double-counted.
- One instance is enough to report. Do not wait for a second copy to prove a point, and do not downgrade a \
finding because it appears once.
- Obey `references/readings/when-to-relax.md`: if the code survives scrutiny and fixing it would make things worse, say \
so and move on instead of manufacturing a violation.
- No name lists. Do not grep for "functions that look like X" and call the match a finding; read for the \
property the principle defines.

## 3. Output contract

Write JSON Lines to `{out_jsonl}` — one object per finding, no prose around it:

{{"file": "path/from/repo/root.py", "line": 191, "symbol": "function-or-class", "principle": "library-slug", "severity": "high|medium|low", "what": "quoted code and why it violates the principle", "repair": "the concrete change, one or two sentences, owner-first"}}

`principle` is the file slug of the principle you are charging, e.g. `separation-of-concerns`. Quote real \
lines and real numbers; an unlocatable finding is worthless to the merge step.

Then, in your final message, give: the files you read, the count of findings by principle, the `CROSS-LENS \
SIGHTINGS`, and anything in your lens you could not decide (say what would decide it).
"""


def emit(m: dict, outdir: Path, target: str, repo: str, run: int, only: str | None,
         label: str = "", file_list: str | None = None) -> int:
    problems, _, _ = audit(m)
    if problems:
        print("REFUSING TO EMIT — the lens assignment is not a valid partition:", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        return 1
    outdir.mkdir(parents=True, exist_ok=True)
    lenses = m["lenses"]
    names = [only] if only else list(lenses)
    if only and only not in lenses:
        print(f"no such lens: {only}", file=sys.stderr)
        return 1
    lines = []
    for lens in names:
        spec = lenses[lens]
        files = list(spec["files"]) + [p for p in spec.get("also_protocols", [])]
        ordered = list(spec.get("indexes", [])) + m["shared"]["protocols"] + files
        reading = "\n".join(f"- `references/{f}`" for f in ordered)
        stem = f"{lens}-{label}-run{run}" if label else f"{lens}-run{run}"
        scope_note = ""
        scan_target = target
        if file_list:
            paths = [l.strip() for l in Path(file_list).read_text().splitlines() if l.strip()]
            files_md = "\n".join(f"- `{p}`" for p in paths)
            scan_target = f"the {len(paths)} files listed below — a cross-folder slice, not a directory"
            scope_note = f"\n### Scope files\n\n{files_md}\n"
        out_jsonl = str(outdir / f"findings-{stem}.jsonl")
        out_manifest = str(outdir / f"files-read-{stem}.txt")
        body = PROMPT.format(
            n_peers=len(names) - 1,
            reading_list=reading,
            stance=spec["stance"],
            target=scan_target,
            repo=repo,
            out_jsonl=out_jsonl,
            out_manifest=out_manifest,
        ) + scope_note
        if spec.get("skip_when"):
            body += f"\nScope note: {spec['skip_when']}.\n"
        (outdir / f"lens-{stem}.md").write_text(body)
        (outdir / f"assignment-{stem}.txt").write_text("\n".join(f"references/{f}" for f in ordered) + "\n")
        lines.append(f"{stem}\t{len(files) + len(m['shared']['protocols'])} files\t{out_jsonl}")
    (outdir / "manifest.txt").write_text(
        f"target: {target}\nrepo: {repo}\nrun: {run}\nlenses: {len(names)}\n\n" + "\n".join(lines) + "\n"
    )
    total = sum(len(lenses[l]["files"]) + len(lenses[l].get("also_protocols", [])) for l in names)
    print(f"emitted {len(names)} lens prompt(s) to {outdir}")
    print(f"principle coverage: {total} assigned files loaded across lenses")
    for line in lines:
        print("  " + line.replace("\t", "  "))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--emit", metavar="DIR")
    ap.add_argument("--target", default=".")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--run", type=int, default=1)
    ap.add_argument("--only", default=None)
    ap.add_argument("--label", default="", help="suffix for output names, for per-module drill cells")
    ap.add_argument("--file-list", default=None,
                    help="a file of paths (one per line) — use for cross-folder concept slices, which are not "
                         "a directory and cannot be named by a single path")
    a = ap.parse_args()

    m = load()
    if a.check:
        problems, everything, assigned = audit(m)
        classes, all_md = classify(m)
        print(f"principle files: {len(everything)}   assigned: {len(assigned)}   lenses: {len(m['lenses'])}")
        counts: dict[str, int] = {}
        for kind in classes.values():
            head = kind.split(":")[0]
            counts[head] = counts.get(head, 0) + 1
        print(f"markdown reachability: {len(classes)}/{len(all_md)} files reachable — "
              + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
        if problems:
            for p in problems:
                print("FAIL " + p)
            return 1
        print("OK — every principle file belongs to exactly one lens")
        return 0
    if a.list:
        for lens, spec in m["lenses"].items():
            print(f"{lens:12s} {len(spec['files']):2d} principles  {spec['stance'][:90]}")
        return 0
    if a.emit:
        return emit(m, Path(a.emit), a.target, a.repo, a.run, a.only, a.label, a.file_list)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
