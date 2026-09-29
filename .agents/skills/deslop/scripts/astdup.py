#!/usr/bin/env python3
"""Shape-clone scan for Python: functions with the same body shape.

Hashes every function body after replacing identifiers, attributes, arguments
and constants with placeholders, so two functions with the same *structure*
collapse even when every name and SQL string differs — the duplication jscpd
cannot see. Single-`return` bodies are skipped (one function per query is
fine), as are docstrings.

This is supporting evidence, not a verdict: a clone family is a candidate for
one parameterised function only when the members mean the same thing. Read
them before filing.

  astdup.py <src_root> [min_lines=8]
"""

import ast, hashlib, sys, os, collections
root = sys.argv[1].rstrip("/"); minlines = int(sys.argv[2]) if len(sys.argv) > 2 else 8
class Norm(ast.NodeTransformer):
    def visit_Name(self, n): return ast.copy_location(ast.Name(id="N", ctx=n.ctx), n)
    def visit_arg(self, n): n.arg="a"; n.annotation=None; return n
    def visit_Attribute(self, n): self.generic_visit(n); n.attr="A"; return n
    def visit_Constant(self, n): return ast.copy_location(ast.Constant(value=type(n.value).__name__), n)
    def visit_FunctionDef(self, n): self.generic_visit(n); n.name="f"; n.returns=None; n.decorator_list=[]; return n
    visit_AsyncFunctionDef = visit_FunctionDef
    def visit_keyword(self, n): self.generic_visit(n); n.arg = "k" if n.arg else None; return n
groups = collections.defaultdict(list)
for dp, _, fs in os.walk(root):
    if "/tests" in dp or "__pycache__" in dp: continue
    for f in fs:
        if not f.endswith(".py"): continue
        p = os.path.join(dp, f)
        try: tree = ast.parse(open(p).read())
        except Exception: continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                n = node.end_lineno - node.lineno + 1
                if n < minlines: continue
                body = ast.Module(body=node.body, type_ignores=[])
                # drop docstring
                if body.body and isinstance(body.body[0], ast.Expr) and isinstance(getattr(body.body[0],'value',None), ast.Constant): body.body = body.body[1:]
                if not body.body: continue
                if len(body.body) == 1 and isinstance(body.body[0], ast.Return): continue
                h = hashlib.md5(ast.dump(Norm().visit(body)).encode()).hexdigest()
                groups[h].append((p.replace(root+"/",""), node.lineno, node.name, n))
dups = [g for g in groups.values() if len(g) > 1 and len({x[0] for x in g}) > 1 or (len(g)>1 and len({(x[0],x[1]) for x in g})>1)]
dups.sort(key=lambda g: -sum(x[3] for x in g[1:]))
tot = 0
for g in dups:
    tot += sum(x[3] for x in g[1:])
    print(f"--- {len(g)}x {g[0][3]} lines (waste {sum(x[3] for x in g[1:])})")
    for p,l,n,c in g: print(f"    {p}:{l} {n}")
print(f"TOTAL groups={len(dups)} redundant_lines={tot}")
