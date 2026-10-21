#!/usr/bin/env python3
"""Merge a deslop swarm's per-lens findings into one adjudication table.

Eight lenses reading the same target will agree on some findings, duplicate others under two names, and
occasionally charge the same lines under two different principles. None of that should reach the tracker as
it stands, so this script does the bookkeeping the orchestrator would otherwise do by eye:

  corroborated  the same locus charged under the same principle by more than one lens — the strongest
                signal a swarm produces, and still only a prompt to verify at the source line
  single        one lens's finding — not weaker by rule. One instance is enough to be a real finding; the
                swarm only tells you it was subtle
  disputed      two lenses charging the same locus under different principles — an adjudication, not a
                duplicate: pick the owner, drop the other

Usage:

    python3 scripts/swarm_merge.py /tmp/deslop-swarm/findings-*.jsonl --out /tmp/deslop-swarm/merged.md

Findings are JSON Lines (see swarm_lenses.py). The lens name is taken from the file name
(`findings-<lens>-run<N>.jsonl`), so a malformed line is reported and skipped rather than silently dropped.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

LENS_RE = re.compile(r"findings-(?P<lens>[a-z0-9-]+)-run(?P<run>\d+)\.jsonl$")


def lens_of(path: Path) -> str:
    m = LENS_RE.search(path.name)
    return m.group("lens") if m else path.stem


def norm_file(p: str) -> str:
    p = p.strip().strip("`")
    for pre in ("./", "/"):
        while p.startswith(pre) and len(p) > len(pre):
            p = p[len(pre):]
    return p


def load(paths: list[Path]) -> tuple[list[dict], list[str]]:
    rows, bad = [], []
    for path in paths:
        lens = lens_of(path)
        if not path.exists():
            bad.append(f"{path}: missing (a lens produced no file at all)")
            continue
        for i, line in enumerate(path.read_text().splitlines(), 1):
            line = line.strip()
            if not line or line in ("```", "```json"):
                continue
            try:
                import json

                rec = json.loads(line)
            except Exception:
                bad.append(f"{path}:{i}: not JSON, skipped")
                continue
            rec.setdefault("file", "")
            rec.setdefault("line", 0)
            rec.setdefault("symbol", "")
            rec.setdefault("principle", "")
            rec.setdefault("severity", "medium")
            rec["_lens"] = lens
            rec["file"] = norm_file(str(rec["file"]))
            rows.append(rec)
    return rows, bad


def same_locus(a: dict, b: dict, window: int = 4) -> bool:
    if a["file"] != b["file"]:
        return False
    if a.get("symbol") and b.get("symbol") and a["symbol"] == b["symbol"]:
        return True
    try:
        return abs(int(a["line"]) - int(b["line"])) <= window and not (a.get("symbol") and b.get("symbol"))
    except (TypeError, ValueError):
        return False


def cluster(rows: list[dict], window: int) -> list[dict]:
    groups: list[dict] = []
    for rec in rows:
        for g in groups:
            if g["principle"] == rec["principle"] and same_locus(g["rows"][0], rec, window):
                g["rows"].append(rec)
                break
        else:
            groups.append({"principle": rec["principle"], "rows": [rec]})
    return groups


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("findings", nargs="+")
    ap.add_argument("--out", default=None)
    ap.add_argument("--window", type=int, default=4, help="line tolerance for same-locus matching")
    a = ap.parse_args()

    rows, bad = load([Path(p) for p in a.findings])
    if not rows:
        print("no findings parsed", file=sys.stderr)
        for b in bad:
            print("  " + b, file=sys.stderr)
        return 1

    groups = cluster(rows, a.window)
    for g in groups:
        g["lenses"] = sorted({r["_lens"] for r in g["rows"]})
        g["sev"] = min((r["severity"] for r in g["rows"]), key=lambda s: {"high": 0, "medium": 1, "low": 2}.get(s, 3))
        g["file"] = g["rows"][0]["file"]
        g["line"] = min(int(r["line"]) for r in g["rows"])
        g["symbol"] = next((r["symbol"] for r in g["rows"] if r["symbol"]), "")

    corroborated = sorted([g for g in groups if len(g["lenses"]) > 1], key=lambda g: (g["file"], g["line"]))
    single = sorted([g for g in groups if len(g["lenses"]) == 1], key=lambda g: (g["file"], g["line"]))

    # disputed: same locus, different principles
    disputed = []
    for i, g in enumerate(groups):
        for h in groups[i + 1:]:
            if g["principle"] != h["principle"] and same_locus(g["rows"][0], h["rows"][0], a.window):
                disputed.append((g, h))

    by_lens = defaultdict(int)
    by_principle = defaultdict(int)
    for r in rows:
        by_lens[r["_lens"]] += 1
        by_principle[r["principle"] or "(unnamed)"] += 1

    L = []
    L.append("# Deslop swarm — merged findings\n")
    L.append(f"{len(rows)} raw findings → **{len(groups)} distinct** "
             f"({len(corroborated)} corroborated by ≥2 lenses, {len(single)} single-lens, "
             f"{len(disputed)} disputed locus/loci)\n")
    if bad:
        L.append("## Parse problems\n")
        L.extend(f"- {b}" for b in bad)
        L.append("")
    L.append("## Findings per lens\n")
    for lens, n in sorted(by_lens.items(), key=lambda kv: -kv[1]):
        L.append(f"- **{lens}** — {n}")
    L.append("\n## Findings per principle\n")
    for pr, n in sorted(by_principle.items(), key=lambda kv: -kv[1]):
        L.append(f"- `{pr}` — {n}")

    def table(title: str, gs: list[dict], show_lenses: bool) -> None:
        L.append(f"\n## {title}\n")
        if not gs:
            L.append("_none_")
            return
        L.append("| locus | principle | sev | " + ("lenses | " if show_lenses else "") + "what | repair |")
        L.append("|---|---|---|---|" + ("---|" if show_lenses else "") + "---|")
        for g in gs:
            r = g["rows"][0]
            loc = f"`{g['file']}:{g['line']}`" + (f" `{g['symbol']}`" if g["symbol"] else "")
            what = str(r.get("what", "")).replace("|", "\\|")[:180]
            repair = str(r.get("repair", "")).replace("|", "\\|")[:160]
            lens_col = (", ".join(g["lenses"]) + " | ") if show_lenses else ""
            L.append(f"| {loc} | `{g['principle']}` | {g['sev']} | {lens_col}{what} | {repair} |")

    table("Corroborated (≥2 lenses charged the same locus under the same principle)", corroborated, True)
    table("Single-lens findings (one instance is enough — verify at the source line, then file)", single, True)
    dispute_rows: list[dict] = []
    seen: set[tuple[str, int, str]] = set()
    for g, h in disputed:
        for grp in (g, h):
            k = (grp["file"], grp["line"], grp["principle"])
            if k not in seen:
                seen.add(k)
                dispute_rows.append(grp)
    table("Disputed — same locus, different principles (adjudicate: one owner, one principle)",
          sorted(dispute_rows, key=lambda x: (x["file"], x["line"])), True)
    if disputed:
        L.append("\n### Adjudication pairs\n")
        for g, h in disputed:
            L.append(f"- `{g['file']}:{g['line']}` — **{g['principle']}** ({', '.join(g['lenses'])}) vs "
                     f"**{h['principle']}** ({', '.join(h['lenses'])})")

    L.append("\n## Before anything is filed\n")
    L.append("- Read every corroborated locus at its source line — two lenses can share one misreading, and a "
             "swarm multiplies false positives as readily as true ones.\n"
             "- File one issue per concern, not per lens: a locus charged under two principles is one defect "
             "with one owner.\n"
             "- A lens that reports zero findings and never quotes code is a failed lens, not a clean target: "
             "re-run it before accepting a thin result.\n")
    out = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).write_text(out)
        print(out)
        print(f"\nwritten: {a.out}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
