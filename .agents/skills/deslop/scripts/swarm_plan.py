#!/usr/bin/env python3
"""Plan a deslop pass: enumerate principle x slice permutations, score them, spend a budget on the best.

The observation behind this script is uncomfortable but reliable: an agent finds slop when it is pointed at
**a specific piece of code with a specific principle in mind**, and finds much less when told to "audit this
directory". So the unit of work is neither a directory walk nor a lens — it is a **cell**: one principle group
applied to one *slice* of the code. The full set of cells is the permutation space, far too large to run
(8 lenses x dozens of slices x cross-folder combinations). This script does the four steps a pass needs
instead of running everything:

  1. **enumerate** every permutation worth naming — the whole target, each module, each module x role
     archetype, and each cross-folder **concept cluster** (every retry, every env reader, every provider
     adapter) — the last being cells a directory walk cannot express;
  2. **score** each cell on explicit, printable components — signal density, fit, cross-cuttingness, size;
  3. **select** the best under an agent budget with diversity caps and an overlap penalty, so the plan is
     neither a thousand agents nor eight lenses fired blindly;
  4. **order** them into waves, so an early wave can reroute the later ones.

Nothing here reads code for quality. It locates evidence; the orchestrator owns the plan.

    python3 scripts/swarm_plan.py --repo <root> --target <dir> --out /tmp/deslop-plan [--budget 24]

Writes `plan.md` (selected cells in wave order), `candidates.md` (the whole permutation space with each
score component and why it stood or fell), and `dispatch.sh` (ready-to-run `swarm_lenses.py` calls).
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
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "venv", "__pycache__", ".agents",
             "site-packages", ".next", "coverage"}
# Test trees are not slop targets: they are fixtures, they are allowed to repeat themselves, and a
# guarantees/data-layer drill over them reports the harness rather than the product. --include-tests opts in.
TEST_DIRS = {"test", "tests", "__tests__", "spec", "specs", "testdata", "e2e", "integration_tests"}

SIGNALS = {
    "parsing": re.compile(
        r"os\.environ|os\.getenv|getenv\(|argparse|sys\.argv|json\.loads|yaml\.safe_load|"
        r"\brequest\.(?:json|form|args|query_params|body)|Query\(|req\.body", re.I),
    "guarantees": re.compile(
        r"async def|await |asyncio\.|threading\.Lock|Semaphore|retry|backoff|timeout|cancel\(|"
        r"context\.Context|finally:|try_lock", re.I),
    "data-layer": re.compile(
        r"CREATE TABLE|ALTER TABLE|\bSELECT\b[\s\S]{0,120}\bFROM\b|__tablename__|sqlalchemy|psycopg|"
        r"asyncpg|alembic|\.execute\(|session\.commit|migration", re.I),
}

# Archetype matching is per path SEGMENT, never a substring of the joined path: "model_provider" must read as
# an adapter, not as "model" (a data layer), or every adapter directory earns a pointless SQL drill.
ROLE_LENSES = [
    ({"adapter", "adapters", "provider", "providers", "client", "clients", "sdk", "integrations", "connectors"},
     ["boundaries", "parsing", "coupling"]),
    ({"handler", "handlers", "endpoint", "endpoints", "route", "routes", "api", "controller", "controllers",
      "views"}, ["parsing", "guarantees"]),
    ({"worker", "workers", "scheduler", "schedulers", "job", "jobs", "queue", "tasks", "consumer", "consumers"},
     ["guarantees"]),
    ({"repo", "repos", "repository", "repositories", "store", "stores", "dao", "sql", "db", "database",
      "models", "entities", "schema", "migrations"}, ["data-layer"]),
]

# Cross-folder concept clusters: slices a directory walk cannot express, because the defect is that the SAME
# concern is re-implemented in several places. Each concept names the lenses that read it well.
CONCEPTS = {
    "config-env": (re.compile(r"config|settings|env|option|feature_flag", re.I),
                   re.compile(r"os\.environ|os\.getenv|getenv\(|settings\.|Config\(", re.I),
                   ["parsing", "duplication", "boundaries"]),
    "retry-timeout": (re.compile(r"retry|backoff|timeout|resilien|circuit", re.I),
                      re.compile(r"retry|backoff|timeout|max_attempts|sleep\(", re.I),
                      ["duplication", "guarantees", "coupling"]),
    "provider-adapter": (re.compile(r"adapter|provider|client|sdk", re.I),
                         re.compile(r"class\s+\w*(?:Adapter|Client|Provider)|def\s+(?:complete|invoke|call)", re.I),
                         ["boundaries", "parsing", "coupling"]),
    "serialization": (re.compile(r"serial|pars|codec|schema|marshal|dto|mapper", re.I),
                      re.compile(r"json\.|\.dict\(|model_validate|from_dict|to_dict|loads\(|dumps\(", re.I),
                      ["parsing", "duplication", "boundaries"]),
    "persistence": (re.compile(r"repo|store|dao|query|persist|session|transaction", re.I),
                    re.compile(r"\.execute\(|session\.|commit\(|rollback\(|SELECT |INSERT ", re.I),
                    ["data-layer", "duplication", "guarantees"]),
    "auth-identity": (re.compile(r"auth|token|credential|identity|permission|rbac", re.I),
                      re.compile(r"token|bearer|credential|api_key|scope|role|permission", re.I),
                      ["guarantees", "parsing", "coupling"]),
    "error-translation": (re.compile(r"error|exception|fail|fault", re.I),
                          re.compile(r"raise |except |catch|Error\(|Exception", re.I),
                          ["guarantees", "duplication", "legibility"]),
    "logging-telemetry": (re.compile(r"log|trace|metric|telemetry|observ", re.I),
                          re.compile(r"logger\.|log\.|span|metric|emit_event|counter\(", re.I),
                          ["legibility", "guarantees", "duplication"]),
}

GLOBAL_LENSES = ["boundaries", "coupling", "shape", "legibility", "duplication"]


@dataclass
class Cell:
    lens: str
    kind: str            # global | module | archetype | concept
    scope: str           # module path, concept name, or target path
    files: int
    loc: int
    evidence: str
    signal: float = 0.0
    components: dict[str, float] = field(default_factory=dict)
    score: float = 0.0
    selected: bool = False
    reason: str = ""
    _files: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        tail = Path(self.scope).parts[-2:] if self.kind != "global" else ["target"]
        head = re.sub(r"[^a-z0-9]+", "-", "-".join(tail).lower()).strip("-")
        return head[:36] or "root"

    def fileset(self) -> set[str]:
        return set(self._files)


def read(p: Path) -> str:
    try:
        return p.read_text(errors="ignore")
    except OSError:
        return ""


def walk(root: Path, target: Path, include_tests: bool):
    for dirpath, dirnames, filenames in os.walk(target):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS
                       and (include_tests or d.lower() not in TEST_DIRS)]
        code = [f for f in filenames if Path(f).suffix in CODE_EXT]
        if code:
            yield Path(dirpath), code


def enumerate_cells(root: Path, target: Path, include_tests: bool, min_loc: int, min_hits: int) -> list[Cell]:
    modules: dict[str, dict] = {}
    concept_files: dict[str, set[str]] = defaultdict(set)
    concept_loc: dict[str, int] = defaultdict(int)
    sym_home: dict[str, set[str]] = defaultdict(set)

    for dirpath, code in walk(root, target, include_tests):
        rel = str(dirpath.relative_to(root))
        m = modules.setdefault(rel, {"files": [], "loc": 0, "hits": defaultdict(int), "biggest": (0, "")})
        for name in code:
            fp = dirpath / name
            text = read(fp)
            lines = text.splitlines()
            relfile = str(fp.relative_to(root))
            m["files"].append(relfile)
            m["loc"] += len(lines)
            if len(lines) > m["biggest"][0]:
                m["biggest"] = (len(lines), name)
            for lens, pat in SIGNALS.items():
                n = len(pat.findall(text))
                if n:
                    m["hits"][lens] += n
            for sym in re.findall(r"^(?:def|class)\s+([A-Za-z_]\w+)", text, re.M):
                if not sym.startswith("_"):
                    sym_home[sym].add(rel)
            for concept, (namepat, bodypat, _lenses) in CONCEPTS.items():
                if namepat.search(name) or namepat.search(rel) or bodypat.search(text):
                    concept_files[concept].add(relfile)
                    concept_loc[concept] += len(lines)

    total_files = sum(len(m["files"]) for m in modules.values())
    total_loc = sum(m["loc"] for m in modules.values()) or 1
    cells: list[Cell] = []

    # tier 1 — orientation: cross-cutting lenses over the whole target
    for lens in GLOBAL_LENSES:
        c = Cell(lens, "global", str(target.relative_to(root)), total_files, total_loc,
                 "cross-cutting: findings span modules")
        c._files = [f for m in modules.values() for f in m["files"]]
        cells.append(c)

    # tier 2/3 — module drills (signal-gated) and archetype drills (role-inferred)
    for rel, m in modules.items():
        if m["loc"] < min_loc:
            continue
        assigned: dict[str, tuple[str, str]] = {}
        for lens in SIGNALS:
            if m["hits"].get(lens, 0) >= min_hits:
                assigned[lens] = (f"{m['hits'][lens]} signal line(s) in {len(m['files'])} file(s)", "module")
        segments = {s.lower() for s in re.split(r"[^A-Za-z0-9]+", rel) if s}
        for keywords, lenses in ROLE_LENSES:
            hit = sorted(segments & keywords)
            if hit:
                for lens in lenses:
                    assigned.setdefault(lens, (f"archetype segment {hit[0]!r}", "archetype"))
        dup = {s for s in sym_home if len(sym_home[s]) > 1 and rel in sym_home[s]}
        if dup:
            assigned.setdefault("duplication", (f"{len(dup)} symbol(s) also defined elsewhere", "module"))
        for lens, (why, kind) in assigned.items():
            c = Cell(lens, kind, rel, len(m["files"]), m["loc"], why)
            c._files = list(m["files"])
            cells.append(c)

    # tier 4 — cross-folder concept clusters
    for concept, (_namepat, _bodypat, lenses) in CONCEPTS.items():
        files = sorted(concept_files.get(concept, set()))
        if len(files) < 3:
            continue
        for lens in lenses:
            c = Cell(lens, "concept", concept, len(files), concept_loc.get(concept, 0),
                     f"{len(files)} file(s) across the tree carry this concept")
            c._files = files
            cells.append(c)
    return cells


def score_cells(cells: list[Cell]) -> None:
    """Score with printed components, so the ranking can be argued with rather than trusted."""
    max_loc = max((c.loc for c in cells), default=1) or 1
    prefer = max_loc / 8
    for c in cells:
        if c.kind == "global":
            c.components = {"signal": 0.55, "fit": 1.0, "cross": 1.0, "size": 0.5, "overlap": 0.0}
        else:
            density = min(1.0, c.loc / 400.0)                                   # evidence needs bulk to hide in
            fit = {"module": 1.0, "archetype": 0.72, "concept": 0.9}[c.kind]
            cross = 1.0 if c.kind == "concept" else 0.0                          # only concepts cross folders
            size = 1.0 - min(1.0, abs(c.loc - prefer) / max_loc)                 # mid-size: hides defects, affordable
            c.components = {"signal": round(density, 2), "fit": fit, "cross": cross,
                            "size": round(size, 2), "overlap": 0.0}
        c.score = round(0.34 * c.components["signal"] + 0.26 * c.components["fit"]
                        + 0.18 * c.components["cross"] + 0.22 * c.components["size"], 3)


def select_cells(cells: list[Cell], budget: int, per_module: int) -> list[Cell]:
    """Greedy by score under a budget, with diversity caps and an overlap penalty for re-reading ground."""
    globs = [c for c in cells if c.kind == "global"]
    ranked = sorted([c for c in cells if c.kind != "global"], key=lambda c: -c.score)
    chosen: list[Cell] = []
    per_scope: dict[str, int] = defaultdict(int)
    per_lens: dict[str, int] = defaultdict(int)
    lens_cap = max(3, budget // 5)
    # Redundancy is per LENS, never across lenses: two lenses reading the same file is the whole point of a
    # swarm, while the same lens reading the same files twice is money burnt. A shared "covered" set would let a
    # cross-folder concept cluster (which touches the whole tree) veto every module cell for every other lens.
    covered: dict[str, set[str]] = defaultdict(set)
    # orientation is not optional: it runs before the budgeted drills, as the first wave
    for c in globs:
        c.selected, c.reason = True, "orientation — always include"
        chosen.append(c)
        per_scope[c.scope] += 1
        per_lens[c.lens] += 1
        covered[c.lens] |= c.fileset()
    for c in ranked:
        if len(chosen) >= budget:
            c.reason = "budget exhausted"
            continue
        if per_scope[c.scope] >= per_module:
            c.reason = f"scope already has {per_module} cell(s) — cap reached"
            continue
        if per_lens[c.lens] >= lens_cap:
            c.reason = f"lens cap reached ({lens_cap})"
            continue
        fs = c.fileset()
        overlap = len(fs & covered[c.lens]) / max(1, len(fs))
        c.components["overlap"] = round(overlap, 2)
        if overlap > 0.6:
            c.reason = f"{int(overlap * 100)}% of these files are already being read by the same lens"
            continue
        c.score = round(c.score * (1 - 0.35 * overlap), 3)
        c.selected, c.reason = True, "selected"
        chosen.append(c)
        per_scope[c.scope] += 1
        per_lens[c.lens] += 1
        covered[c.lens] |= fs
    chosen.sort(key=lambda c: (c.kind != "global", -c.score))
    return chosen


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget", type=int, default=24, help="max agents to spend (default 24)")
    ap.add_argument("--wave", type=int, default=4, help="agents per wave in the ordering")
    ap.add_argument("--per-module", type=int, default=2, help="cells a single module may earn")
    ap.add_argument("--min-loc", type=int, default=60)
    ap.add_argument("--min-hits", type=int, default=2)
    ap.add_argument("--skillsrc", default=".")
    ap.add_argument("--include-tests", action="store_true")
    a = ap.parse_args()

    root = Path(a.repo).resolve()
    target = (root / a.target).resolve()
    if not target.exists():
        print(f"target does not exist: {target}", file=sys.stderr)
        return 1
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    cells = enumerate_cells(root, target, a.include_tests, a.min_loc, a.min_hits)
    score_cells(cells)
    chosen = select_cells(cells, a.budget, a.per_module)
    waves = [chosen[i:i + a.wave] for i in range(0, len(chosen), a.wave)]

    C = ["# Deslop candidate cells — the permutation space\n",
         f"`{a.target}`: **{len(cells)} candidate cell(s)** enumerated, **{len(chosen)}** selected under a "
         f"{a.budget}-agent budget. Score = 0.34·signal + 0.26·fit + 0.18·cross + 0.22·size, then a "
         "0.35·overlap penalty against files the same lens is already reading.\n",
         "| score | lens | kind | slice | files | LOC | sig | fit | cross | size | ovl | evidence | verdict |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in sorted(cells, key=lambda c: -c.score):
        k = c.components
        C.append(f"| {c.score} | `{c.lens}` | {c.kind} | `{c.scope}` | {c.files} | {c.loc} | {k['signal']} | "
                 f"{k['fit']} | {k['cross']} | {k['size']} | {k['overlap']} | {c.evidence} | "
                 f"{'**selected**' if c.selected else c.reason or 'rejected'} |")
    (out / "candidates.md").write_text("\n".join(C) + "\n")

    P = ["# Deslop pass plan\n",
         f"Target `{a.target}` — **{len(chosen)} agent(s)** in {len(waves)} wave(s), selected from "
         f"{len(cells)} candidate cells. Each cell is **one principle group against one slice**, because that "
         "is the shape in which an agent actually finds slop.\n", "## Waves\n"]
    for i, wave in enumerate(waves, 1):
        P.append(f"### Wave {i} — {len(wave)} agent(s)\n")
        P.append("| # | lens | slice | evidence | score | prompt |")
        P.append("|---|---|---|---|---|---|")
        for j, c in enumerate(wave, 1):
            P.append(f"| {j} | `{c.lens}` | `{c.scope}` ({c.kind}) | {c.evidence} | {c.score} | "
                     f"`lens-{c.lens}-{c.label}-run1.md` |")
        P.append("")
    P.append("Run wave 1, merge with `scripts/swarm_merge.py`, then let its findings reroute wave 2: a cell that "
             "came back thin is evidence about the *code*, and a rich cell marks a neighbourhood worth a "
             "directed deep dive (`--only <lens> --target <that module>`).\n")
    P.append("## How the selection was made\n")
    P.append("- **Enumerated** four slice families: the whole target, each module, each module×role archetype, "
             "and cross-folder **concept clusters** (config/env, retry/timeout, provider/adapter, serialization, "
             "persistence, auth, error translation, logging). The last is the family a directory walk cannot "
             "express and the one where duplicated knowledge hides.\n"
             "- **Scored** on signal density (does the slice contain the evidence at all), fit (signal-gated vs "
             "role-inferred vs concept), cross-cuttingness, and size (mid-size slices hide defects and are "
             "affordable; the largest are covered by their concept clusters instead).\n"
             "- **Selected** greedily under a budget with caps — at most "
             f"{a.per_module} cell(s) per module, a per-lens cap of max(3, budget/5) — and a 35% overlap "
             "penalty, so the plan does not pay twice for the same ground.\n"
             "- **Ordered** into waves so cheap evidence lands first.\n")
    P.append("## Rules the plan must obey\n")
    P.append("- Never split an orientation lens per module: boundary and coupling findings cross modules, and a "
             "per-module split hides exactly that.\n"
             "- If the plan looks thin, add **slices** (a concept cluster, a module), not a lens across every "
             "module — that cross-product is the thousand-agent swarm this step exists to prevent.\n"
             "- Test trees are excluded unless `--include-tests`: fixtures may repeat themselves.\n"
             "- The orchestrator owns the plan. The archetype tier guesses from a path name, so drop a cell whose "
             "only evidence is that word, and add one where you know the codebase and the grep does not.\n")
    (out / "plan.md").write_text("\n".join(P) + "\n")

    S = ["#!/usr/bin/env bash", "# generated by swarm_plan.py — dispatch the selected plan, wave by wave",
         "set -uo pipefail", f'SRC="{Path(a.skillsrc).resolve()}"', f'REPO="{root}"', f'OUT="{out}"',
         'mkdir -p "$OUT"', ""]
    used: dict[str, int] = defaultdict(int)
    for i, wave in enumerate(waves, 1):
        S.append(f"# ---- wave {i}")
        for c in wave:
            key = f"{c.lens}/{c.label}"
            used[key] += 1
            label = c.label if used[key] == 1 else f"{c.label}-{used[key]}"
            if c.kind == "concept":
                flist = out / f"cell-{c.lens}-{label}.files"
                flist.write_text("\n".join(c._files) + "\n")
                S.append(f'python3 "$SRC/scripts/swarm_lenses.py" --emit "$OUT" --target "{a.target}" '
                         f'--repo "$REPO" --only {c.lens} --label {label} --file-list "{flist}" --run 1')
            else:
                scope = a.target if c.kind == "global" else c.scope
                S.append(f'python3 "$SRC/scripts/swarm_lenses.py" --emit "$OUT" --target "{scope}" '
                         f'--repo "$REPO" --only {c.lens} --label {label} --run 1')
        S.append("")
    S.append('echo "prompts written to $OUT — one agent per lens-*.md, merge with scripts/swarm_merge.py"')
    (out / "dispatch.sh").write_text("\n".join(S) + "\n")
    os.chmod(out / "dispatch.sh", 0o755)

    print(f"enumerated {len(cells)} candidate cells → selected {len(chosen)} "
          f"({len(waves)} wave(s) of ≤{a.wave}) under a {a.budget}-agent budget")
    for c in chosen:
        print(f"  [{c.kind:9s}] {c.lens:12s} x {c.scope:58s} score {c.score}")
    print(f"plan: {out/'plan.md'}   candidates: {out/'candidates.md'}   dispatch: {out/'dispatch.sh'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
