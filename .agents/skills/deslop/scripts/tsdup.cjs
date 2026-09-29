#!/usr/bin/env node
/**
 * Shape-clone scan for TypeScript/TSX: functions with the same body shape.
 * Requires a `typescript` package on disk; pass its path as the third argument
 * or set TS_PATH (default: ./node_modules/typescript).
 *
 *   node tsdup.cjs <src_root> [min_lines=8] [path/to/node_modules/typescript]
 */
const tsPath = process.argv[4] || process.env.TS_PATH || "node_modules/typescript";
const ts = require(require("path").resolve(tsPath));
const fs = require("fs"), path = require("path"), crypto = require("crypto");
const root = process.argv[2], min = +process.argv[3] || 8;
const files = [];
(function walk(d){ for (const f of fs.readdirSync(d)) { const p = path.join(d,f); const st = fs.statSync(p);
  if (st.isDirectory()) { if (!/__tests__|node_modules/.test(f)) walk(p); } else if (/\.(ts|tsx)$/.test(f) && !/\.test\.|\.spec\./.test(f)) files.push(p); } })(root);
const groups = new Map();
function shape(node, sf) {
  // structural fingerprint: kind tree, identifiers/literals stripped
  let out = [];
  (function rec(n){ const k = ts.SyntaxKind[n.kind];
    if (n.kind === ts.SyntaxKind.Identifier || ts.isLiteralExpression(n) || n.kind === ts.SyntaxKind.JsxText) { out.push("_"); return; }
    if (n.kind === ts.SyntaxKind.TypeReference || ts.isTypeNode(n)) { out.push("T"); return; }
    out.push(k + "("); ts.forEachChild(n, rec); out.push(")"); })(node);
  return out.join("");
}
for (const p of files) {
  const src = fs.readFileSync(p, "utf8");
  const sf = ts.createSourceFile(p, src, ts.ScriptTarget.Latest, true, p.endsWith("x") ? ts.ScriptKind.TSX : ts.ScriptKind.TS);
  (function visit(n){
    if ((ts.isFunctionDeclaration(n) || ts.isFunctionExpression(n) || ts.isArrowFunction(n) || ts.isMethodDeclaration(n)) && n.body) {
      const s = sf.getLineAndCharacterOfPosition(n.getStart()).line + 1, e = sf.getLineAndCharacterOfPosition(n.end).line + 1, lines = e - s + 1;
      if (lines >= min) {
        let name = n.name ? n.name.getText() : (n.parent && ts.isVariableDeclaration(n.parent) ? n.parent.name.getText() : (n.parent && ts.isPropertyAssignment(n.parent) ? n.parent.name.getText() : "<anon>"));
        const h = crypto.createHash("md5").update(shape(n.body, sf)).digest("hex");
        if (!groups.has(h)) groups.set(h, []);
        groups.get(h).push({ f: path.relative(root, p), l: s, name, lines });
      }
    }
    ts.forEachChild(n, visit);
  })(sf);
}
const dups = [...groups.values()].filter(g => g.length > 1 && new Set(g.map(x => x.f + ":" + x.l)).size > 1);
dups.sort((a, b) => b.slice(1).reduce((s, x) => s + x.lines, 0) - a.slice(1).reduce((s, x) => s + x.lines, 0));
let tot = 0;
for (const g of dups) { const w = g.slice(1).reduce((s, x) => s + x.lines, 0); tot += w;
  console.log(`--- ${g.length}x ${g[0].lines} lines (waste ${w})`); for (const x of g) console.log(`    ${x.f}:${x.l} ${x.name}`); }
console.log(`TOTAL groups=${dups.length} redundant_lines=${tot} files=${files.length}`);
