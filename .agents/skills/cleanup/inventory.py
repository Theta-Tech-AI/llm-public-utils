#!/usr/bin/env python3
"""Print the cleanup inventory and the change since the last run.

Read-only except `git fetch` and the snapshot it writes at --state; --list-browsers-older-than only reads. Run it at the start of a cleanup, after each
merge batch and at the end:
    python3 .agents/skills/cleanup/inventory.py [--ref origin/main] [--detail] [--state FILE]
        [--code-roots a/,b/] [--frozen-docs docs/library/] [--baseline-glob 'ci/baseline*.txt']
        [--guidance-file AGENTS.md] [--review-label needs-review] [--tree <dir>]
Counts come from the given git ref (not the working tree), so a dirty checkout or a
composed build/ tree does not change them. Every project-specific input is optional: a missing
file, label, gh login or docker daemon makes that row disappear instead of failing the run.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import re
import os
import shutil
import sys
import subprocess
import tokenize
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Run from inside the checkout: a timer runs a copy of this file from outside it.
REPO = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
# Previous snapshot lives outside the repo: it is per machine, not history. A timer passes its own
# --state so its runs do not reset the change shown to an agent running this by hand.
STATE = Path.home() / ".cache" / f"cleanup-inventory-{REPO.name}-{hashlib.sha1(str(REPO).encode()).hexdigest()[:8]}.json"
# Vendored or generated trees are not the project's code; --code-roots overrides this for a narrower scope.
SKIP_DIRS = ("node_modules/", "vendor/", "dist/", "build/", "third_party/", ".venv/", "venv/")
CODE_SUFFIXES = (".py", ".ts", ".tsx", ".sh")
LANGUAGES = {".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript (TSX)", ".sh": "Shell"}
PY_TEST = re.compile(r"^\s*(async\s+)?def test_", re.M)
TS_TEST = re.compile(r"^\s*(it|test)(\.each\([^)]*\))?(\.\w+)?\(", re.M)
TODO = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b")
STALE_AFTER = timedelta(days=14)
# Deslop's measuring guide: nesting, elif chains and branches per function move far more than LOC and are hard to game.
NESTS = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try, ast.Match)
BRANCHES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler, ast.match_case)
SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def sh(*args: str) -> str:
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True, check=True).stdout


def soft(*args: str) -> str | None:
    """Output of an optional probe (gh, docker, a file in the ref); None when it is absent or fails."""
    try:  # a stalled remote must not stall the inventory
        return subprocess.run(args, cwd=REPO, capture_output=True, text=True, check=True, timeout=60).stdout
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def is_test_file(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return (
        "/tests/" in f"/{path}" or "/__tests__/" in f"/{path}"
        or name.startswith("test_") or name.startswith("conftest")
        or ".test." in name or ".spec." in name
    )


def python_comment_lines(text: str) -> set[int]:
    """Line numbers of `#` comments and docstrings."""
    lines: set[int] = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            # Only a comment alone on its line: an inline comment must not erase the code beside it.
            if tok.type == tokenize.COMMENT and tok.line.lstrip().startswith("#"):
                lines.add(tok.start[0])
        for node in ast.walk(ast.parse(text)):
            body = getattr(node, "body", None)
            if isinstance(body, list) and body and isinstance(body[0], ast.Expr) \
                    and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                lines.update(range(body[0].lineno, (body[0].end_lineno or body[0].lineno) + 1))
    except (SyntaxError, tokenize.TokenError):
        pass
    return lines


def ts_comment_lines(text: str) -> set[int]:
    lines: set[int] = set()
    in_block = False
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if in_block:
            lines.add(number)
            in_block = "*/" not in stripped
        elif stripped.startswith("/*"):
            lines.add(number)
            in_block = "*/" not in stripped
        elif stripped.startswith("//"):
            lines.add(number)
    return lines


def shell_comment_lines(text: str) -> set[int]:
    return {n for n, line in enumerate(text.splitlines(), 1) if line.lstrip().startswith("#") and not line.startswith("#!")}


def area(path: str) -> str:
    """The folder a line counts toward: two levels deep, so a service or page folder, not a file."""
    return "/".join(path.split("/")[:2])


def python_shape(text: str) -> tuple[int, int, list[tuple[int, int, str]]]:
    """Max nesting depth, longest if/elif chain, and (lines, branches, name) per function."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return 0, 0, []
    elifs, longest = set(), 0
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and id(node) not in elifs:
            chain, cur = 1, node
            while len(cur.orelse) == 1 and isinstance(cur.orelse[0], ast.If):
                cur = cur.orelse[0]
                elifs.add(id(cur))
                chain += 1
            longest = max(longest, chain)

    def depth(node: ast.AST, level: int) -> int:
        return max([level] + [depth(child, level + (isinstance(child, NESTS) and id(child) not in elifs))
                              for child in ast.iter_child_nodes(node)])

    def branches(node: ast.AST) -> int:
        # McCabe decision points, as radon counts them; a nested function or class is its own block.
        total = 0
        for child in ast.iter_child_nodes(node):
            if isinstance(child, SCOPES):
                continue
            total += isinstance(child, BRANCHES)
            total += len(child.values) - 1 if isinstance(child, ast.BoolOp) else 0
            total += 1 + len(child.ifs) if isinstance(child, ast.comprehension) else 0
            total += branches(child)
        return total

    functions = [(f.end_lineno - f.lineno + 1, branches(f), f"{f.name}:{f.lineno}")
                 for f in ast.walk(tree) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.end_lineno]
    return depth(tree, 0), longest, functions


def add_detail(detail: dict[str, dict[str, list[int]]] | None, language: str, folder: str, column: int, n: int) -> None:
    """Adds n to one column (0 code, 1 comments, 2 tests) of the file's language row and folder row."""
    if detail is None:
        return
    for kind, key in (("language", language), ("folder", folder)):
        detail.setdefault(kind, {}).setdefault(key, [0, 0, 0])[column] += n


def count_test_file(path: str, text: str, nonblank: set[int], totals: dict[str, int]) -> None:
    totals["test_files"] += 1
    # A per-bug file usually repeats a behaviour test; fold it into the module's file.
    totals["per_bug_test_files"] += bool(re.search(r"(^|/)(test_)?bug\d", path, re.I))
    totals["test_lines"] += len(nonblank)
    totals["test_cases"] += len((PY_TEST if path.endswith(".py") else TS_TEST).findall(text))


def comment_lines(path: str, text: str, shape: dict[str, int], functions: list[tuple[int, int, str]]) -> set[int]:
    """The file's comment lines; a Python file also feeds the nesting, elif-chain and per-function shape."""
    if path.endswith(".py"):
        nesting, chain, found = python_shape(text)
        shape["py_max_nesting"] = max(shape["py_max_nesting"], nesting)
        shape["py_longest_elif_chain"] = max(shape["py_longest_elif_chain"], chain)
        functions += [(lines, branches, f"{path}:{name}") for lines, branches, name in found]
        return python_comment_lines(text)
    return shell_comment_lines(text) if path.endswith(".sh") else ts_comment_lines(text)


def complexity_shape(functions: list[tuple[int, int, str]]) -> dict[str, int]:
    return {
        "py_functions_over_100_lines": sum(lines > 100 for lines, _, _ in functions),
        # Cyclomatic complexity approximated as 1 + branch points, averaged over production functions.
        "py_mean_branches_x100": round(100 * sum(1 + b for _, b, _ in functions) / max(len(functions), 1)),
        "py_functions_cc_over_20": sum(b + 1 > 20 for _, b, _ in functions),
        # Branches above 10 per function, summed: splitting a function below the threshold lowers it without
        # removing a decision, so read it beside the total and look for real consolidation.
        "py_excess_complexity_over_10": sum(max(0, b + 1 - 10) for _, b, _ in functions),
        "py_total_decision_points": sum(b for _, b, _ in functions),
    }


def count_code(ref: str, roots: tuple[str, ...], detail: dict[str, dict[str, list[int]]] | None = None) -> dict[str, int]:
    paths = [p for p in sh("git", "ls-tree", "-r", "--name-only", ref).splitlines()
             if p.endswith(CODE_SUFFIXES) and (p.startswith(roots) if roots else not any(d in f"/{p}" for d in SKIP_DIRS))]
    totals = dict.fromkeys(("test_cases", "test_files", "per_bug_test_files", "test_lines",
                            "comment_lines", "code_lines", "todo_markers"), 0)
    shape = dict.fromkeys(("py_max_nesting", "py_longest_elif_chain", "py_functions_over_100_lines"), 0)
    functions: list[tuple[int, int, str]] = []
    for path in paths:
        text = sh("git", "show", f"{ref}:{path}")
        nonblank = {n for n, line in enumerate(text.splitlines(), 1) if line.strip()}
        language, folder = LANGUAGES[path[path.rfind("."):]], area(path)
        if is_test_file(path):
            add_detail(detail, language, folder, 2, len(nonblank))
            count_test_file(path, text, nonblank, totals)
            continue
        comments = comment_lines(path, text, shape, functions) & nonblank
        totals["comment_lines"] += len(comments)
        totals["code_lines"] += len(nonblank - comments)
        add_detail(detail, language, folder, 0, len(nonblank - comments))
        add_detail(detail, language, folder, 1, len(comments))
        totals["todo_markers"] += len(TODO.findall(text))
    shape.update(complexity_shape(functions))
    if detail is not None:
        detail["worst"] = {name: [1 + b, lines, 0] for lines, b, name in sorted(functions, key=lambda f: -f[1])[:12]}
    return {**totals, **shape}


def open_issues() -> list[dict] | None:
    """Open issues from the gh CLI; None when gh, its login or the remote is unavailable."""
    out = soft("gh", "issue", "list", "--state", "open", "--limit", "2000", "--json", "labels,updatedAt")
    return json.loads(out) if out else None


def issue_counts(issues: list[dict], review_label: str | None) -> dict[str, int]:
    cutoff = datetime.now(timezone.utc) - STALE_AFTER
    labels = [{label["name"] for label in issue["labels"]} for issue in issues]
    counts = {
        "open_issues": len(issues),
        "unlabeled_issues": sum(not names for names in labels),
        # Untouched for two weeks: likely stale, moot or already fixed; verify and close.
        "stale_issues": sum(datetime.fromisoformat(i["updatedAt"].replace("Z", "+00:00")) < cutoff for i in issues),
    }
    if review_label:
        counts["awaiting_review_issues"] = sum(review_label in names for names in labels)
    return counts


def issue_breakdown(issues: list[dict]) -> dict[str, dict[str, int]]:
    groups: dict[str, dict[str, int]] = {"kind": {}, "severity": {}, "area": {}}
    kinds = {"bug", "enhancement", "tech-debt", "documentation", "feature", "chore"}
    for issue in issues:
        for name in {label["name"] for label in issue["labels"]}:
            group = "kind" if name in kinds else "severity" if name.startswith(("severity:", "priority:")) else "area"
            groups[group][name] = groups[group].get(name, 0) + 1
    return groups


def print_detail(detail: dict[str, dict[str, list[int]]], issues: list[dict] | None) -> None:
    for kind, limit in (("language", 10), ("folder", 40)):
        rows = sorted(detail.get(kind, {}).items(), key=lambda item: -(item[1][0] + item[1][2]))[:limit]
        print(f"\n  {kind:<44} {'code':>8} {'comments':>9} {'tests':>8} {'tests/code':>10}")
        for key, (code, comments, tests) in rows:
            ratio = f"{tests / code:.2f}" if code else "-"
            print(f"  {key:<44} {code:>8,} {comments:>9,} {tests:>8,} {ratio:>10}")
    print(f"\n  {'most complex Python functions':<96} {'CC':>4} {'lines':>6}")
    for name, (cc, lines, _) in detail.get("worst", {}).items():
        print(f"  {name[-96:]:<96} {cc:>4} {lines:>6}")
    print(f"\n  {'markdown folder':<44} {'files':>8} {'tokens':>9}")
    for folder, (files, tokens, _) in sorted(detail.get("markdown", {}).items(), key=lambda item: -item[1][1])[:15]:
        print(f"  {folder:<44} {files:>8,} {tokens:>9,}")
    for group, counts in (issue_breakdown(issues) if issues else {}).items():
        print(f"\n  open issues by {group}: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])))


def markdown_counts(ref: str, frozen_prefix: str | None, detail: dict[str, dict[str, list[int]]] | None) -> dict[str, int]:
    """Working markdown (files, tokens = words x 1.35) per folder in --detail; frozen reference docs are counted apart."""
    all_paths = [p for p in sh("git", "ls-tree", "-r", "--name-only", ref).splitlines() if p.endswith(".md")]
    frozen = [p for p in all_paths if frozen_prefix and p.startswith(frozen_prefix)]
    paths = [p for p in all_paths if p not in frozen]
    tokens = 0
    for path in paths:
        words = len(sh("git", "show", f"{ref}:{path}").split())
        tokens += round(words * 1.35)
        if detail is not None:
            parts = path.split("/")
            folder = "/".join(parts[:2]) if len(parts) > 2 else parts[0] if len(parts) > 1 else "(root)"
            row = detail.setdefault("markdown", {}).setdefault(folder, [0, 0, 0])
            row[0] += 1
            row[1] += round(words * 1.35)
    counts = {"markdown_files": len(paths), "markdown_tokens": tokens}
    if frozen_prefix:
        counts["frozen_doc_files"] = len(frozen)
        counts["frozen_doc_tokens"] = sum(round(len(sh("git", "show", f"{ref}:{p}").split()) * 1.35) for p in frozen)
    return counts


def baseline_lines(ref: str, pattern: str) -> int | None:
    """Debt a CI ratchet tolerates (one known failure or ceiling per line) in files matching the git pathspec; None if none exist."""
    paths = (soft("git", "ls-tree", "-r", "--name-only", ref, "--", pattern) or "").splitlines()
    if not paths:
        return None
    return sum(1 for p in paths for line in sh("git", "show", f"{ref}:{p}").splitlines()
               if line.strip() and not line.lstrip().startswith("#"))


def collected_cases(tree: str) -> int:
    """Test cases pytest collects in a composed CI tree; unlike the source count, parametrized cases count."""
    if not Path(tree).is_dir():
        return -1
    run = subprocess.run(["python3", "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
                         cwd=tree, capture_output=True, text=True)
    match = re.search(r"(\d+) tests? collected", run.stdout)
    # -1 means the collection failed (exit status other than 0), never a partial count.
    return int(match.group(1)) if match and run.returncode == 0 else -1


def default_ref() -> str:
    head = (soft("git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD") or "").strip()
    return head or "origin/main"


def processes() -> list[tuple[int, int, int, str]]:
    """(pid, ppid, age in seconds, command line) for every process on the box."""
    out = subprocess.run(["ps", "-eo", "pid=,ppid=,etimes=,args="], capture_output=True, text=True).stdout
    rows = []
    for line in out.splitlines():
        parts = line.split(None, 3)
        if len(parts) == 4 and all(p.isdigit() for p in parts[:3]):
            rows.append((int(parts[0]), int(parts[1]), int(parts[2]), parts[3]))
    return rows


def agent_browser_processes() -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """(daemons, browsers) as (pid, age seconds), counted from `ps`; both empty when agent-browser never ran.

    A daemon is an agent-browser process (not this script, not a browser). A browser is a Chrome/Chromium main
    process (no --type= flag, so its renderers and GPU helpers do not inflate the count) that agent-browser
    started: its command line or an ancestor's mentions agent-browser.
    """
    rows = processes()
    by_pid = {pid: (ppid, cmd) for pid, ppid, _, cmd in rows}
    me = os.getpid()

    def exe(cmd: str) -> str:
        return os.path.basename(cmd.split()[0])

    def is_chrome(cmd: str) -> bool:
        return exe(cmd) in ("chrome", "chromium", "chromium-browser", "google-chrome", "google-chrome-stable")

    def started_by_agent_browser(pid: int) -> bool:
        # The browser binary usually lives under an agent-browser folder, and its parent is the daemon.
        for _ in range(12):  # bounded walk up the parent chain
            if pid not in by_pid:
                return False
            ppid, cmd = by_pid[pid]
            if "agent-browser" in cmd and "inventory.py" not in cmd:
                return True
            pid = ppid
        return False

    daemons = [(pid, age) for pid, _, age, cmd in rows
               if pid != me and exe(cmd).startswith("agent-browser") and not is_chrome(cmd)]
    browsers = [(pid, age) for pid, _, age, cmd in rows
                if is_chrome(cmd) and "--type=" not in cmd and started_by_agent_browser(pid)]
    return daemons, browsers


def dev_server_processes() -> list[tuple[int, int, int]]:
    """(pid, age seconds, RSS KB) of node processes running vite (not vitest): dev and preview servers."""
    out = subprocess.run(["ps", "-u", str(os.getuid()), "-o", "pid=,etimes=,rss=,args="], capture_output=True, text=True).stdout
    rows = []
    for line in out.splitlines():
        parts = line.split(None, 3)
        argv = parts[3].split() if len(parts) == 4 else []
        # The script itself must be vite, and a build is not a server.
        if len(argv) > 1 and os.path.basename(argv[0]) == "node" and re.search(r"/vite(\.js)?$", argv[1]) and "build" not in argv[2:]:
            rows.append((int(parts[0]), int(parts[1]), int(parts[2])))
    return rows


def list_stale_browsers(hours: float) -> None:
    """List agent-browser Chrome main processes and node dev servers older than HOURS: candidates to inspect.

    Listing only. Its matching is a heuristic (an agent-browser path in the process tree, vite in the arguments), so
    stop processes with a reaper that applies the skill's rules (exact launcher profile, running binary, scopes,
    pidfd with a scan-time start check), never from this list by pid.
    """
    if not hours > 0:
        sys.exit("--list-browsers-older-than needs a positive number of hours")
    _, browsers = agent_browser_processes()
    stale = [(pid, age) for pid, age in browsers if age > hours * 3600]
    for pid, age in stale:
        print(f"  browser pid {pid} (age {age / 3600:.1f} h)")
    print(f"  {len(stale)} of {len(browsers)} agent-browser browsers older than {hours} h")
    servers = dev_server_processes()
    old, unknown = [], 0
    reader_ns = os.readlink("/proc/self/ns/cgroup")
    for pid, age, rss in servers:
        if age <= hours * 3600:
            continue
        # Scope and age must describe one process: the start time is read before and after the cgroup, and the age
        # comes from it, so a PID reused since the ps snapshot is young or changes start time and counts as unknown.
        try:
            before = Path(f"/proc/{pid}/stat").read_bytes().rsplit(b")", 1)[1].split()[19]
            raw = Path(f"/proc/{pid}/cmdline").read_bytes()
            argv = [x.decode(errors="replace") for x in raw.removesuffix(b"\0").split(b"\0")]
            rss = next(int(l.split()[1]) for l in Path(f"/proc/{pid}/status").read_text().splitlines() if l.startswith("VmRSS:"))
            cgroup = Path(f"/proc/{pid}/cgroup").read_text(errors="replace")
            cgroup_ns = os.readlink(f"/proc/{pid}/ns/cgroup")
            raw_after = Path(f"/proc/{pid}/cmdline").read_bytes()
            after = Path(f"/proc/{pid}/stat").read_bytes().rsplit(b")", 1)[1].split()[19]
            uptime = float(Path("/proc/uptime").read_text().split()[0])
            age = int(uptime - int(before) / os.sysconf("SC_CLK_TCK"))
        except (OSError, IndexError, ValueError, StopIteration):
            unknown += 1
            continue
        # Still a vite server now (a process may exec another program and keep its pid and start time).
        if not (len(argv) > 1 and os.path.basename(argv[0]) == "node" and re.search(r"/vite(\.js)?$", argv[1])
                and "build" not in argv[2:]):
            unknown += 1
            continue
        # exec'd during the sample (raw bytes compared): RSS and cgroup may describe another program. A cgroup path of
        # "/" is a namespace root that hides any enclosing scope, so the scope is unknown there.
        # Paths show the enclosing scope only from the initial cgroup namespace (the kernel's fixed inode); inside any
        # other namespace a scope above its root is hidden. Every record must parse as id:controllers:/absolute-path.
        lines = cgroup.splitlines()
        records = [re.fullmatch(r"\d+:[^:]*:(/\S*)", line) for line in lines]
        # The reader's namespace matters too: /proc/PID/cgroup is rendered relative to it.
        if (raw != raw_after or cgroup_ns != "cgroup:[4026531835]" or reader_ns != "cgroup:[4026531835]"
                or not lines or not all(records)):
            unknown += 1
            continue
        paths = [m.group(1) for m in records]
        scoped = any("devserver-" in p for p in paths)
        if before != after or age <= hours * 3600:
            unknown += before != after
            continue
        if not scoped:
            old.append((pid, age, rss))
    for pid, age, rss in old:
        print(f"  dev server pid {pid} (age {age / 3600:.1f} h, {rss // 1024} MB)")
    print(f"  {len(old)} candidates (older than {hours} h, confirmed outside devserver scopes) of {len(servers)} node dev servers;"
          f" {unknown} with unknown scope")


def positive_hours(text: str) -> float:
    value = float(text)
    if not 0 < value < float("inf"):
        raise argparse.ArgumentTypeError("must be a positive number of hours")
    return value


def meminfo_mb() -> dict[str, int]:
    """MemTotal, MemAvailable and swap used in MB from /proc/meminfo."""
    kb = {k: int(v.split()[0]) for k, v in (line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())}
    return {"MemTotal": kb["MemTotal"] // 1024, "MemAvailable": kb["MemAvailable"] // 1024,
            "SwapUsed": (kb["SwapTotal"] - kb["SwapFree"]) // 1024}


CONTAINER_ID = re.compile(r"(?:^|[/-])([0-9a-f]{64})(?:\.scope)?(?:/|$)")  # systemd and cgroupfs layouts, any parent


def cgroup_path(text: str) -> str:
    """The cgroup path to own a process by: a container record first, else the v2 record, else the systemd hierarchy."""
    records = [line.split(":", 2) for line in text.splitlines() if line.count(":") >= 2]
    for pick in (lambda r: CONTAINER_ID.search(r[2]), lambda r: r[0] == "0", lambda r: r[1] == "name=systemd", lambda r: True):
        if match := next((r for r in records if pick(r)), None):
            return match[2]
    return ""


def proc_table() -> dict[int, tuple[int, int, int, str, str]]:
    """pid -> (ppid, rss KB, age seconds (float), cgroup unit, comm) from /proc; a process that exits mid-scan is skipped."""
    page_kb = os.sysconf("SC_PAGE_SIZE") // 1024
    ticks = os.sysconf("SC_CLK_TCK")
    uptime = float(Path("/proc/uptime").read_text().split()[0])
    table = {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            stat = Path(f"/proc/{entry}/stat").read_bytes()
            comm = stat[stat.index(b"(") + 1:stat.rindex(b")")].decode(errors="replace")
            rest = stat[stat.rindex(b")") + 2:].split()
            rss_kb = int(Path(f"/proc/{entry}/statm").read_text().split()[1]) * page_kb
            cgroup = cgroup_path(Path(f"/proc/{entry}/cgroup").read_text())
            if Path(f"/proc/{entry}/stat").read_bytes().rpartition(b")")[2].split()[19] != rest[19]:
                continue  # the pid was reused while its files were read
        except (OSError, ValueError, IndexError):
            continue
        parts = cgroup.split("/")
        last = max((i for i, part in enumerate(parts) if part.endswith((".scope", ".service"))), default=-1)
        # A container keeps its id as the unit; otherwise the path through the owning unit keeps two users' same-named services apart.
        unit = cgroup if CONTAINER_ID.search(cgroup) else "/".join(parts[:last + 1]) if last >= 0 else ""
        table[int(entry)] = (int(rest[1]), rss_kb, max(0.0, uptime - int(rest[19]) / ticks), unit, comm)
    return table


GENERIC_UNIT = re.compile(r"^(user@[^/]*\.service|session-[^/]*\.scope|init\.scope)$")


def unit_name(path: str) -> str:
    return path.rsplit("/", 1)[-1]


def host_memory_owners(table: dict[int, tuple[int, int, int, str, str]]) -> list[dict]:
    """Host processes grouped by owner: the cgroup unit (a tmux pane, an app, a service). A process in a generic unit
    (login session, user manager) is grouped by the top of its parent chain. Container processes are left to docker stats.
    An owner is flagged reparented when every root process has init or the user manager as parent: its starter is gone
    or was never tracked (a pane shell started by the user manager looks the same), so check it before stopping it.
    Container processes form one group per container id, matched to docker stats by the report."""
    groups: dict[str, list[int]] = {}
    for pid, (_, _, _, unit, _) in table.items():
        name = unit_name(unit)
        if (container := CONTAINER_ID.search(unit)):
            groups.setdefault(f"container:{container[1]}", []).append(pid)
        elif not unit or GENERIC_UNIT.match(name):
            top, seen = pid, {pid}
            while (parent := table[top][0]) in table and parent > 1 and parent not in seen and table[parent][4] not in ("systemd", "sshd", "sshd-session", "login"):
                top = parent
                seen.add(top)  # a pid reused during the scan can make a parent cycle
            groups.setdefault(f"{table[top][4]}[{top}] in {name or 'no unit'}", []).append(pid)
        else:
            groups.setdefault(unit, []).append(pid)
    owners = []
    for key, pids in groups.items():
        members = set(pids)
        roots = [p for p in pids if table[p][0] not in members]
        reparented = all(table[p][0] == 1 or table.get(table[p][0], (0, 0, 0, "", ""))[4] == "systemd" for p in roots)
        tracks_parent = " in " in key or not key.endswith(".service")
        owners.append({"owner": key, "container": key.removeprefix("container:") if key.startswith("container:") else None, "procs": len(pids), "rss_kb": sum(table[p][1] for p in pids),
                       "age_h": max(table[p][2] for p in pids) / 3600, "reparented": tracks_parent and reparented})
    return owners


def docker_memory_samples() -> dict[str, tuple[str, int]] | None:
    """Container id -> (name, memory KB) from docker stats; None when docker gave no sample."""
    out = soft("docker", "stats", "--no-stream", "--no-trunc", "--format", "{{.ID}}\t{{.Name}}\t{{.MemUsage}}") if shutil.which("docker") else None
    if out is None:
        return None
    scale = {"B": 1 / 1048576, "KiB": 1 / 1024, "MiB": 1, "GiB": 1024, "TiB": 1048576}
    samples = {}
    for line in out.splitlines():
        cid, name, usage = (line.split("\t") + ["", ""])[:3]
        # "0B / 0B" is docker's empty sample for a container that just restarted: keep the scanned RSS instead
        if (m := re.match(r"([\d.]+)\s*([KMGT]?i?B)", usage)) and float(m[1]) > 0:
            samples[cid] = (name, int(float(m[1]) * scale.get(m[2], 0) * 1024))
    return samples


def label_owners(owners: list[dict], samples: dict[str, tuple[str, int]] | None) -> None:
    """Name each container from docker stats and use its cgroup memory; a container with no sample stays a host row by id."""
    for o in owners:
        if o["container"] and samples and o["container"] in samples:
            o["owner"], o["rss_kb"] = f"docker:{samples[o['container']][0]}", samples[o["container"]][1]
        elif o["container"]:
            o["owner"] = f"container:{o['container'][:12]} (no docker stats)"
    names = [unit_name(o["owner"]) for o in owners]
    for o, name in zip(owners, names):  # a short name that two owners share gets its full path
        o["shown"] = name if names.count(name) == 1 else o["owner"]  # a collision prints the full path, widening the column


def print_memory_report(old_hours: float, top: int = 15) -> None:
    """List-only: host memory totals, then the top owners by memory, with reparented and old owners flagged."""
    try:
        info = meminfo_mb()
        table = proc_table()
        owners = host_memory_owners(table)
        samples = docker_memory_samples()
    except (OSError, ValueError, KeyError) as error:  # /proc missing (not Linux) must not stop the rest of the inventory
        print(f"  memory report unavailable: {error}")
        return
    label_owners(owners, samples)
    owners.sort(key=lambda o: -o["rss_kb"])
    print(f"🧠 memory: total {info['MemTotal']:,} MB, available {info['MemAvailable']:,} MB, swap used {info['SwapUsed']:,} MB")
    if len(table) < 50 or 1 not in table:
        print("  few processes are visible (restricted /proc or PID namespace?): the ranking may not be host-wide")
    if samples is None:
        print("  docker stats unavailable: container memory is summed per-process RSS")
    print(f"  {'owner':64} {'procs':>5} {'mem MB':>8} {'oldest h':>9}  flags")
    for o in owners[:top]:
        flags = ["reparented" if o["reparented"] else "", f"older than {old_hours:g}h" if o["age_h"] > old_hours else ""]
        print(f"  {o['shown']:64} {o['procs']:>5} {o['rss_kb'] // 1024:>8,} {o['age_h']:>9.1f}  {' '.join(f for f in flags if f)}")
    print(f"  ({len(owners)} owners among {len(table)} visible processes; host rows sum per-process RSS, docker rows are docker stats usage without inactive file cache; nothing is stopped)")


def optional_rows(ref: str, args: argparse.Namespace, issues: list[dict] | None) -> dict[str, int]:
    """Rows that exist only when the project has the input; each is skipped, not failed, when it is missing."""
    rows: dict[str, int] = {}
    if args.baseline_glob and (baseline := baseline_lines(ref, args.baseline_glob)) is not None:
        rows["baseline_lines"] = baseline
    if issues is not None:
        rows.update(issue_counts(issues, args.review_label))
    if (prs := soft("gh", "pr", "list", "--state", "open", "--limit", "500", "--json", "number")) is not None:
        rows["open_prs"] = len(json.loads(prs))
    # Ask the remote: local remote-tracking refs keep branches that were deleted on origin.
    if (heads := soft("git", "ls-remote", "--heads", "origin")) is not None:
        rows["origin_branches"] = len(heads.splitlines())
    # Local stacks and test databases left running hold memory for every agent on the box.
    if shutil.which("docker") and (containers := soft("docker", "ps", "-q")) is not None:
        rows["containers"] = len(containers.splitlines())
    guidance = soft("git", "show", f"{ref}:{args.guidance_file}")
    if guidance is not None:
        # Always-loaded agent guidance costs every session: words x 1.35 estimates its tokens.
        rows["guidance_file_tokens"] = round(len(guidance.split()) * 1.35)
    skipped = [name for name, ok in (("gh issues", issues is not None), ("gh prs", "open_prs" in rows),
                                     ("origin branches", "origin_branches" in rows), ("docker", "containers" in rows),
                                     ("guidance file", guidance is not None)) if not ok]
    if skipped:  # a vanished row can hide an auth failure; name it
        print("  skipped (unavailable): " + ", ".join(skipped))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ref", default=None, help="git ref to count (default: origin/HEAD, else origin/main)")
    parser.add_argument("--tree", help="a composed test dir whose pytest-collected case count is added")
    parser.add_argument("--detail", action="store_true", help="also print lines per language and folder, and open issues by kind, severity and area")
    parser.add_argument("--state", type=Path, default=STATE, help="snapshot file the change is shown against")
    parser.add_argument("--code-roots", default="", help="comma-separated path prefixes to count (default: the whole tree minus vendored folders)")
    parser.add_argument("--frozen-docs", help="path prefix of reference markdown to count apart from working docs")
    parser.add_argument("--baseline-glob", help="git pathspec of CI ratchet files, one tolerated failure per line")
    parser.add_argument("--guidance-file", default="AGENTS.md", help="always-loaded agent guidance file whose tokens are reported")
    parser.add_argument("--review-label", help="issue label meaning 'waiting for a human', counted when given")
    parser.add_argument("--list-browsers-older-than", type=float, metavar="HOURS",
                        help="list agent-browser Chrome and node dev-server processes older than HOURS and exit (listing only)")
    parser.add_argument("--memory-old-hours", type=positive_hours, default=6, help="flag memory owners older than this many hours (default 6)")
    args = parser.parse_args()
    if args.list_browsers_older_than is not None:
        list_stale_browsers(args.list_browsers_older_than)
        return
    ref = args.ref or default_ref()
    soft("git", "fetch", "-q", "--no-recurse-submodules", "origin")
    detail: dict[str, dict[str, list[int]]] | None = {} if args.detail else None
    issues = open_issues()
    roots = tuple(r for r in args.code_roots.split(",") if r)
    daemons, browsers = agent_browser_processes()
    servers = dev_server_processes()
    stale_cutoff = 6 * 3600  # a browser older than any legitimate run is a leak; the reaper takes its own limit
    now = {
        **count_code(ref, roots, detail),
        **markdown_counts(ref, args.frozen_docs, detail),
        **optional_rows(ref, args, issues),
        "worktrees": len(sh("git", "worktree", "list").splitlines()),
        "local_branches": len(sh("git", "branch", "--format=%(refname)").splitlines()),
        "stashes": len(sh("git", "stash", "list").splitlines()),
        # Browser daemons and Chrome processes pile up when agents crash mid-run; each holds hundreds of MB.
        "agent_browser_daemons": len(daemons),
        "agent_browser_chrome": len(browsers),
        "agent_browser_chrome_over_6h": sum(age > stale_cutoff for _, age in browsers),
        # Detached vite servers with no owner leak the same way; one box once held 110 of them (25 GB).
        "node_dev_servers": len(servers),
        "node_dev_servers_over_6h": sum(age > stale_cutoff for _, age, _ in servers),
        "node_dev_servers_rss_mb": sum(rss for _, _, rss in servers) // 1024,
    }
    if args.tree:
        now["collected_test_cases"] = collected_cases(args.tree)
    before = json.loads(args.state.read_text()) if args.state.exists() else {}
    print(f"🧮 cleanup inventory at {ref} ({sh('git', 'rev-parse', '--short', ref).strip()})")
    for key, value in now.items():
        delta = value - before[key] if key in before else None
        print(f"  {key:28} {value:>9,}" + (f"  ({delta:+,})" if delta else ""))
    print_memory_report(args.memory_old_hours)
    if detail is not None:
        print_detail(detail, issues)
    args.state.parent.mkdir(parents=True, exist_ok=True)
    args.state.write_text(json.dumps(now))


if __name__ == "__main__":
    main()
