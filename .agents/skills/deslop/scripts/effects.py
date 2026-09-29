#!/usr/bin/env python3
"""Same-design scan that ignores every name in the project.

A copied design keeps what it does to the outside world even when every file,
function and variable is renamed: the library calls it makes, the SQL tables
and clauses it touches, the status values it writes, the exceptions it handles.
Each file gets that fingerprint; file pairs in different packages are ranked by
weighted overlap and each pair prints the shared features, so the reader can see
*why* two files look like one design. Then read both files and judge.

  effects.py <src_root> [min_lines=60] [top=25] [skip_dir ...]     (tests/ is always skipped)
"""

import ast, collections, itertools, math, os, re, sys

root, min_lines, top = sys.argv[1].rstrip("/"), int(sys.argv[2]) if len(sys.argv) > 2 else 60, int(sys.argv[3]) if len(sys.argv) > 3 else 25
SKIP = {"tests", "__pycache__", *sys.argv[4:]}
SQL = re.compile(r"\b(?:FROM|INTO|UPDATE|JOIN|TABLE(?: IF NOT EXISTS)?)\s+([a-z_][a-z0-9_]*)|(ON CONFLICT|FOR UPDATE|SKIP LOCKED|ADVISORY|RETURNING|NOW\(\)|INTERVAL|DISTINCT ON|ORDER BY|LIMIT)", re.I)
GLUE = {"fastapi", "pydantic", "re", "typing", "dataclasses", "__future__", "logging", "collections", "enum", "abc"}
WORD = re.compile(r"^[a-z][a-z_]{2,24}$")


def dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr); node = node.value
    return (node.id, *reversed(parts)) if isinstance(node, ast.Name) else None


def fingerprint(tree, own):
    ext, feats = {}, collections.Counter()
    defined = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            ext.update({(a.asname or a.name).split(".")[0]: a.name for a in n.names if a.name.split(".")[0] not in own})
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0 and n.module.split(".")[0] not in own:
            ext.update({a.asname or a.name: f"{n.module}.{a.name}" for a in n.names})
    for n in ast.walk(tree):
        if isinstance(n, (ast.Call, ast.Attribute)) and (d := dotted(n.func if isinstance(n, ast.Call) else n)) and d[0] in ext:
            if ext[d[0]].split(".")[0] not in GLUE:
                feats["call:" + ".".join((ext[d[0]], *d[1:]))] += 1
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr not in defined:
            feats["method:" + n.func.attr] += 1
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            if WORD.match(n.value):
                feats["value:" + n.value] += 0.3
            for table, clause in SQL.findall(n.value):
                feats["sql:" + (table or clause).lower()] += 1
        elif isinstance(n, ast.ExceptHandler) and n.type is not None and (d := dotted(n.type)):
            feats["catch:" + ".".join(d[-2:])] += 1
        elif isinstance(n, (ast.While, ast.Try, ast.With, ast.AsyncWith)):
            feats["shape:" + type(n).__name__] += 1
    return feats


def weighted_jaccard(a, b):
    keys = a.keys() | b.keys()
    lo, hi = sum(min(a[k], b[k]) for k in keys), sum(max(a[k], b[k]) for k in keys)
    return lo / hi if hi else 0.0


files = []
own = {d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))} | {"src"}
for dp, _, fs in os.walk(root):
    if SKIP & set(dp.split(os.sep)):
        continue
    for f in fs:
        path = os.path.join(dp, f)
        if not f.endswith(".py") or f == "__init__.py":
            continue
        src = open(path).read()
        lines = src.count("\n") + 1
        if lines < min_lines:
            continue
        try:
            feats = fingerprint(ast.parse(src), own)
        except SyntaxError:
            continue
        if sum(feats.values()) >= 12:
            files.append((os.path.relpath(path, root), lines, feats))

idf = collections.Counter(k for _, _, fs in files for k in fs)
weight = lambda fs: collections.Counter({k: v * math.log(len(files) / idf[k]) for k, v in fs.items() if idf[k] < len(files) * 0.05})
files = [(p, n, weight(fs)) for p, n, fs in files]
ranked = []
for (pa, na, fa), (pb, nb, fb) in itertools.combinations(files, 2):
    if os.path.dirname(pa) == os.path.dirname(pb):
        continue
    if (score := weighted_jaccard(fa, fb)) > 0.15:
        shared = sorted((k for k in fa.keys() & fb.keys()), key=lambda k: -min(fa[k], fb[k]))[:8]
        ranked.append((score * math.sqrt(min(na, nb)), score, na, nb, pa, pb, shared))
for _, score, na, nb, pa, pb, shared in sorted(ranked, reverse=True)[:top]:
    print(f"{score:.2f}  {na:>4}/{nb:<4} {pa}  ~  {pb}\n      shared: {' '.join(shared)}")
