#!/usr/bin/env python3
"""Representation clustering: the same record described N times.

Collects every record shape in the tree — Python dataclasses / TypedDicts /
Pydantic models / NamedTuples (field names), TypeScript interfaces and object
type aliases (member names), and DB tables (column names from CREATE TABLE) —
then clusters them by shared field names. A cluster with several members is
one entity that the code describes several times: DB row, service dataclass,
tool payload, API model, TS type, report row. Each member is a place a field
rename must be repeated by hand.

Field names are normalised (snake/camel → snake) so `sourceChunkIds` and
`source_chunk_ids` count as the same field.

  representations.py --py <src> [--py <upstream src>] [--ts <fe src>] [--min-shared 4] [--top 40] [--skip <folder>]
"""

from __future__ import annotations

import argparse
import ast
import collections
import itertools
import os
import re

TESTS = re.compile(r"(^|/)(tests?|__tests__)(/|$)|\.(test|spec)\.(ts|tsx)$|(^|/)test_[^/]*\.py$")
RECORD_BASES = ("TypedDict", "BaseModel", "NamedTuple", "Protocol")


SKIP: list[str] = []


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower().strip("_")


def py_records(roots):
    out = []
    for root in roots:
        root = root.rstrip("/")
        for dp, dn, fs in os.walk(root):
            dn[:] = [d for d in dn if d not in ("__pycache__", "node_modules", *SKIP) and not d.startswith(".")]
            for f in fs:
                if not f.endswith(".py"):
                    continue
                rel = os.path.join(dp, f)[len(root) + 1 :]
                if TESTS.search(rel):
                    continue
                try:
                    src = open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
                    tree = ast.parse(src)
                except (OSError, SyntaxError):
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        is_record = any(any(b in ast.unparse(x) for b in RECORD_BASES) for x in node.bases) or any(
                            "dataclass" in ast.unparse(d) for d in node.decorator_list
                        )
                        if not is_record:
                            continue
                        fields = {snake(s.target.id) for s in node.body if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name) and not s.target.id.startswith("_")}
                        if len(fields) >= 3:
                            out.append((f"py:{rel}:{node.lineno}:{node.name}", fields))
                # DB tables from CREATE TABLE text
                for m in re.finditer(r"CREATE TABLE (?:IF NOT EXISTS )?([a-z_]+)\s*\((.*?)\n\s*\)", src, re.S | re.I):
                    cols = set()
                    for line in m.group(2).split("\n"):
                        t = line.strip()
                        mm = re.match(r"([a-z_][a-z0-9_]*)\s+[A-Z]", t)
                        if mm and mm.group(1).upper() not in ("PRIMARY", "UNIQUE", "CONSTRAINT", "FOREIGN", "CHECK"):
                            cols.add(mm.group(1))
                    if len(cols) >= 3:
                        out.append((f"db:{m.group(1)}", cols))
    return out


def ts_records(root):
    out = []
    if not root:
        return out
    root = root.rstrip("/")
    # interfaces always open a brace; a type alias counts only when it is an object literal (`type X = {`),
    # never a string-literal union (`type X = "a" | "b"`), which owns no fields
    decl = re.compile(r"^(?:export\s+)?(?:interface\s+(\w+)[^{]*\{|type\s+(\w+)\s*(?:<[^>]*>)?\s*=\s*\{)", re.M)
    for dp, dn, fs in os.walk(root):
        dn[:] = [d for d in dn if d not in ("node_modules", "dist", "build", *SKIP) and not d.startswith(".")]
        for f in fs:
            if not f.endswith((".ts", ".tsx")) or f.endswith(".d.ts"):
                continue
            rel = os.path.join(dp, f)[len(root) + 1 :]
            if TESTS.search(rel):
                continue
            src = open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
            for m in decl.finditer(src):
                start = m.end()
                depth, i = 1, start
                while i < len(src) and depth:
                    if src[i] == "{":
                        depth += 1
                    elif src[i] == "}":
                        depth -= 1
                    i += 1
                body = src[start:i]
                fields = {snake(x) for x in re.findall(r"^\s*(?:readonly\s+)?([A-Za-z_]\w*)\??\s*:", body, re.M)}
                if len(fields) >= 3:
                    out.append((f"ts:{rel}:{src[: m.start()].count(chr(10)) + 1}:{m.group(1) or m.group(2)}", fields))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--py", action="append", default=[])
    ap.add_argument("--ts")
    ap.add_argument("--min-shared", type=int, default=4, help="shared normalised fields to link two records")
    ap.add_argument("--min-jaccard", type=float, default=0.3)
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--skip", action="append", default=[], help="folder name to leave out (repeatable)")
    args = ap.parse_args()
    SKIP.extend(args.skip)
    records = py_records(args.py) + ts_records(args.ts)
    print(f"records={len(records)} (py/db/ts)")
    # union-find on pairs with enough shared fields
    parent = list(range(len(records)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    by_field = collections.defaultdict(list)
    for i, (_n, fields) in enumerate(records):
        for f in fields:
            by_field[f].append(i)
    pair_shared = collections.Counter()
    for f, idxs in by_field.items():
        if len(idxs) > 60:  # very common field names (id, created_at) carry no signal on their own
            continue
        for a, b in itertools.combinations(idxs, 2):
            pair_shared[(a, b)] += 1
    for (a, b), n in pair_shared.items():
        fa, fb = records[a][1], records[b][1]
        jacc = n / len(fa | fb)
        if n >= args.min_shared and jacc >= args.min_jaccard:
            parent[find(a)] = find(b)
    clusters = collections.defaultdict(list)
    for i in range(len(records)):
        clusters[find(i)].append(i)
    rows = [(len(m), m) for m in clusters.values() if len(m) >= 3]
    rows.sort(reverse=True)
    print(f"clusters with >= 3 members: {len(rows)}\n")
    for n, members in rows[: args.top]:
        common = set.intersection(*(records[i][1] for i in members))
        kinds = collections.Counter(records[i][0].split(":")[0] for i in members)
        print(f"== {n} representations ({dict(kinds)}); fields shared by all: {sorted(common)[:8]}")
        for i in sorted(members, key=lambda i: records[i][0]):
            print(f"   {records[i][0]}  ({len(records[i][1])} fields)")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
