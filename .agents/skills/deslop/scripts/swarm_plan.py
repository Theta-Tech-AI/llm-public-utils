#!/usr/bin/env python3
"""Plan a deslop swarm: which lens goes where, before a single agent is dispatched.

The mistake this script prevents is dispatching the full cross-product — eight lenses over N directories —
which is expensive, and worse, mis-scoped: a boundary defect is invisible to an agent looking at one file,
while a data-layer defect is invisible to an agent looking at a module that has no SQL at all. So the plan
couples each lens to the scope where its signal lives:

  orientation   cross-cutting lenses over the whole target: boundaries, coupling, shape, legibility,
                duplication. These findings span modules; a per-module split of them fragments the evidence.
  module drill  signal-gated lenses only where the signal fires: parsing where external input enters,
                guarantees where async/retry/lock/lifetime appears, data-layer where SQL, migrations or an
                ORM model does. One lens × one module × one agent, which is how slop that only a directed
                reader finds gets found.
  archetype     roles carry characteristic defects: an adapter parses and reaches, a scheduler is not
                idempotent, a repo re-derives a schema. Each module is matched to a role by its path, and the
                archetype's lenses are drilled even when the signal grep is quiet.

Usage:

    python3 scripts/swarm_plan.py --repo <root> --target backend/src --out /tmp/deslop-plan

Writes plan.md (the plan, with the reasoning per cell) and dispatch.sh (the ready-to-run commands, using
swarm_lenses.py --only --label so every cell writes its own findings file). Nothing here reads the code for
quality — it only locates the signals, so a human or orchestrating agent can disagree with the plan and edit it
before spending the agents.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

CODE_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".rb", ".cs", ".sql"}
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "venv", "__pycache__",
             ".agents", "site-packages", ".next", "coverage"}
# test trees are not the slop target: they are fixtures, they are allowed to repeat themselves, and a
# guarantees/data-layer drill over them reports the harness rather than the product. Opt in with --include-tests.
TEST_DIRS = {"test", "tests", "__tests__", "spec", "specs", "testdata", "e2e"}

SIGNALS = {
    "parsing": re.compile(
        r"os\.environ|os\.getenv|getenv\(|argparse|sys\.argv|json\.loads|yaml\.safe_load|"
        r"\brequest\.(?:json|form|args|query_params|body)|Query\(|pathParam|req\.body", re.I),
    "guarantees": re.compile(
        r"async def|await |asyncio\.|threading\.Lock|Semaphore|retry|backoff|timeout|cancel\(|"
        r"context\.Context|finally:|try_lock", re.I),
    "data-layer": re.compile(
        r"CREATE TABLE|ALTER TABLE|\bSELECT\b[\s\S]{0,120}\bFROM\b|__tablename__|sqlalchemy|psycopg|"
        r"asyncpg|alembic|\.execute\(|session\.commit|migration", re.I),
}
# Archetype matching is per path SEGMENT, never a substring of the joined path: "model_provider" must read as
# provider (an adapter), not as "model" (a data layer), or every adapter directory gets a pointless SQL drill.
ROLE_LENSES = [
    ({"adapter", "adapters", "provider", "providers", "client", "clients", "sdk", "integrations", "connectors"},
     ["boundaries", "parsing", "coupling"]),
    ({"handler", "handlers", "endpoint", "endpoints", "route", "routes", "api", "controller", "controllers",
      "views"}, ["parsing", "guarantees"]),
    ({"worker", "workers", "scheduler", "schedulers", "job", "jobs", "queue", "tasks", "consumer", "consumers"},
     ["guarantees"]),
    ({"repo", "repos", "repository", "repositories", "store", "stores", "dao", "sql", "migrations", "db",
      "database", "models", "entities", "schema"}, ["data-layer"]),
]
GLOBAL_LENSES = ["boundaries", "coupling", "shape", "legibility", "duplication"]


@dataclass
class Module:
    path: str
    files: int = 0
    loc: int = 0
    biggest: tuple[int, str] = (0, "")
    hits: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    symbols: list[str] = field(default_factory=list)

    def lenses(self, min_hits: int = 2) -> list[tuple[str, str]]:
        """(lens, why) pairs for the module drills."""
        out: list[tuple[str, str]] = []
        for lens, _pat in SIGNALS.items():
            if self.hits.get(lens, 0) >= min_hits:
                out.append((lens, f"{self.hits[lens]} signal line(s) in {self.files} file(s)"))
        segments = {seg.lower() for seg in re.split(r"[^A-Za-z0-9]+", self.path) if seg}
        for keywords, lenses in ROLE_LENSES:
            hit = sorted(segments & keywords)
            if hit:
                for lens in lenses:
                    if lens not in {l for l, _ in out}:
                        out.append((lens, f"archetype: segment {hit[0]!r}"))
        return out


def collect(root: Path, target: Path, include_tests: bool = False) -> list[Module]:
    mods: dict[str, Module] = {}
    sym_home: dict[str, set[str]] = defaultdict(set)
    pats = {k: v for k, v in SIGNALS.items()}
    for dirpath, dirnames, filenames in os.walk(target):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS
                       and (include_tests or d.lower() not in TEST_DIRS)]
        code = [f for f in filenames if Path(f).suffix in CODE_EXT]
        if not code:
            continue
        rel = str(Path(dirpath).relative_to(root))
        mod = mods.setdefault(rel, Module(path=rel))
        for name in code:
            fp = Path(dirpath) / name
            try:
                text = fp.read_text(errors="ignore")
            except OSError:
                continue
            lines = text.splitlines()
            mod.files += 1
            mod.loc += len(lines)
            if len(lines) > mod.biggest[0]:
                mod.biggest = (len(lines), name)
            for lens, pat in pats.items():
                if pat.search(text):
                    mod.hits[lens] += 1
            for m in re.finditer(r"^(?:def|class)\s+([A-Za-z_]\w+)", text, re.M):
                mod.symbols.append(m.group(1))
                sym_home[m.group(1)].add(rel)
    dupes = {s: d for s, d in sym_home.items() if len(d) > 1 and not s.startswith("_")}
    for mod in mods.values():
        if any(s in dupes for s in mod.symbols):
            mod.hits["duplication"] += 1
    return sorted(mods.values(), key=lambda m: -m.loc)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--skillsrc", default=".", help="skill root, for the emitted dispatch commands")
    ap.add_argument("--min-loc", type=int, default=60, help="modules smaller than this are folded into parent")
    ap.add_argument("--min-hits", type=int, default=2, help="signal lines a module needs to earn a drill")
    ap.add_argument("--include-tests", action="store_true", help="drill test trees too (usually noise)")
    ap.add_argument("--global-lenses", default=",".join(GLOBAL_LENSES))
    a = ap.parse_args()

    root = Path(a.repo).resolve()
    target = (root / a.target).resolve()
    if not target.exists():
        print(f"target does not exist: {target}", file=sys.stderr)
        return 1
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    allmods = collect(root, target, a.include_tests)
    mods = [m for m in allmods if m.loc >= a.min_loc]
    folded = sum(1 for m in allmods if m.loc < a.min_loc)
    glob_lenses = [l.strip() for l in a.global_lenses.split(",") if l.strip()]

    L: list[str] = []
    L.append(f"# Deslop swarm plan — `{a.target}`\n")
    L.append(f"{len(mods)} module(s) over {sum(m.files for m in mods)} file(s), "
             f"{sum(m.loc for m in mods)} LOC. {folded} smaller module(s) folded into orientation.\n")
    L.append("## Orientation (cross-cutting lenses, whole target)\n")
    L.append("| lens | why |")
    L.append("|---|---|")
    for lens in glob_lenses:
        L.append(f"| `{lens}` | findings span modules; a per-module split fragments the evidence |")
    L.append("\n## Module drills (one lens × one module × one agent)\n")
    L.append("| module | files | LOC | biggest | drilled lens | why |")
    L.append("|---|---|---|---|---|---|")
    cells: list[tuple[str, str]] = []
    for m in mods:
        assigned = m.lenses(a.min_hits)
        if not assigned:
            L.append(f"| `{m.path}` | {m.files} | {m.loc} | {m.biggest[1]} ({m.biggest[0]}) | — | no signal; orientation only |")
            continue
        for lens, why in assigned:
            L.append(f"| `{m.path}` | {m.files} | {m.loc} | {m.biggest[1]} ({m.biggest[0]}) | `{lens}` | {why} |")
            cells.append((lens, m.path))

    agents = len(glob_lenses) + len(cells)
    L.append(f"\n## Cost\n\n**{agents} agent(s)**: {len(glob_lenses)} orientation + {len(cells)} drill cell(s). "
             "Merge every report with `scripts/swarm_merge.py`.\n")
    L.append("## Directed deep dives — the one-module, one-principle pass\n")
    L.append("Use when a sweep hinted at a defect and could not substantiate it, or when a module *is* the "
             "archetype of a concern. One agent, one module, one principle, whole files only:\n")
    deep = [c for c in cells if c[0] in {"boundaries", "coupling"}][:3] or cells[:3]
    for lens, path in deep:
        L.append(f"- `{lens}` × `{path}` — the shape of a dialog, not a sweep: the agent holds one principle "
                 "and reads every file in the module before reporting.")
    if not deep:
        L.append("- none inferred — pick the module where the orientation pass was thinnest.")
    L.append("\n## Rules the plan must obey\n")
    L.append("- Every drill cell names the lens, the module, and the evidence that put it there. A cell with no "
             "evidence is the archetype table guessing — keep it only if the path really reads as that role.\n"
             "- Global lenses are never split per module: SoC and coupling findings cross module boundaries, "
             "and a per-module split hides them.\n"
             "- Adding a lens to every module is the cross-product this plan exists to avoid. If the plan looks "
             "thin, add **modules**, not lenses.\n")
    (out / "plan.md").write_text("\n".join(L) + "\n")

    sh = ["#!/usr/bin/env bash", "# generated by swarm_plan.py — dispatch the plan", "set -uo pipefail",
          f'SRC="{Path(a.skillsrc).resolve()}"', f'REPO="{root}"', f'OUT="{out}"',
          'mkdir -p "$OUT"', ""]
    for lens in glob_lenses:
        sh.append(f'python3 "$SRC/scripts/swarm_lenses.py" --emit "$OUT" --target "{a.target}" '
                  f'--repo "$REPO" --only {lens} --label global --run 1')
    used: dict[str, int] = defaultdict(int)
    for lens, path in cells:
        tail = Path(path).parts[-2:]                      # last two segments read better than a truncated path
        base = re.sub(r"[^a-z0-9]+", "-", "-".join(tail).lower()).strip("-")[:36] or "root"
        key = f"{lens}/{base}"
        used[key] += 1
        label = base if used[key] == 1 else f"{base}-{used[key]}"
        sh.append(f'python3 "$SRC/scripts/swarm_lenses.py" --emit "$OUT" --target "{path}" '
                  f'--repo "$REPO" --only {lens} --label {label} --run 1')
    sh.append('echo "prompts written to $OUT — run one agent per lens-*.md, then merge findings-*.jsonl"')
    (out / "dispatch.sh").write_text("\n".join(sh) + "\n")
    os.chmod(out / "dispatch.sh", 0o755)

    print(f"plan written: {out/'plan.md'}  ({agents} agents: {len(glob_lenses)} orientation + {len(cells)} drills)")
    for lens, path in cells:
        print(f"  drill {lens:12s} x {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
