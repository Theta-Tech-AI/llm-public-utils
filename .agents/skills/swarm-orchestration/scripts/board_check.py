#!/usr/bin/env python3
"""Validate the coordinator board and print what needs the coordinator now (the loop in references/coordinator-loop.md).

Exit 0: nothing needs the coordinator. Exit 1: findings (listed). Exit 2: the board is invalid (fix it first).
The schema is documented in references/coordinator-loop.md; tests/board_fixture.json is a worked example.

With ``--status-dir DIR`` each worker's status file is ``DIR/<worker id>.jsonl``: one JSON line per step change, as the
brief in references/assign.md asks (at, step, waiting_on, expected_end, last_result, round, finding_class, unsent). It
needs no message channel, so it still works when a worker's reply to the coordinator fails; ``unsent`` carries that
failed reply, and it stays a finding until the board's ``workers[].read_until`` reaches it. A worker is
late when now is past its expected_end, stuck when neither its step nor its round changed for ``--stall-min``, and
looping when its last three review outcomes (lines that name a finding class; "none" for a clean round) share one class. This is the primary signal.

With ``--activity-dir DIR`` (fallback when a worker writes no status) each worker's activity record is the newest file
named ``<worker id>`` or ``<worker id>.*`` in DIR. A worker is quiet when that file is older than its ``pace_min``
(default ``--quiet-min``), and finished without reporting when its tail holds ``--finished-marker`` and the board does
not mark it ``reported``. Silence is weak evidence: fix the signal, never widen the threshold.

With ``--watch MIN`` the check re-reads the board every MIN minutes and exits at the first finding (so a coordinator
that waits on it is woken), or with 0 after ``--deadline-min``.

Usage: board_check.py BOARD.json [--status-dir DIR] [--activity-dir DIR] [--quiet-min N] [--stall-min N]
                      [--stale-min N] [--handback-min N] [--finished-marker TEXT] [--now ISO-8601]
                      [--watch MIN [--deadline-min N]]
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import NotRequired, TypedDict

FINISHED_MARKER = '"stop_reason":"end_turn"'  # the end-of-turn record of a common runtime; pass yours with --finished-marker
PIPELINE_OK = {"success", "running", "queued"}


class Item(TypedDict):
    id: str | int
    what: str
    stage: str
    owner: str | list[str] | None
    next_event: str
    expected_by: str
    group: NotRequired[str]
    area: NotRequired[str]
    waits_on: NotRequired[str | None]
    live_check: NotRequired[str | None]
    live_check_owner: NotRequired[str | None]
    blocks: NotRequired[list[str | int]]


class Sweep(TypedDict):
    id: str
    what: str
    owner: str | list[str] | None
    next_event: NotRequired[str]
    expected_by: NotRequired[str]


class Worker(TypedDict):
    id: str
    model: str
    pace_min: NotRequired[int]
    reported: NotRequired[bool]
    read_until: NotRequired[str]


class Pipeline(TypedDict):
    name: str
    result: str
    checked: str
    owner: NotRequired[str | None]


class Fixture(TypedDict):
    name: str
    env: str
    stage: str
    used_by: NotRequired[str]


class Environment(TypedDict):
    name: str
    capacity: int
    in_use: int


class Handback(TypedDict):
    worker: str
    what: str
    at: str
    answered: NotRequired[str | None]


class Status(TypedDict, total=False):
    at: str
    step: str
    waiting_on: str
    expected_end: str
    last_result: str
    round: int
    finding_class: str
    unsent: str


class Capacity(TypedDict):
    target: int
    idle_reason: NotRequired[str]


class Board(TypedDict):
    updated: str
    items: list[Item]
    workers: NotRequired[list[Worker]]
    sweeps: NotRequired[list[Sweep]]
    pipelines: NotRequired[list[Pipeline]]
    fixtures: NotRequired[list[Fixture]]
    environments: NotRequired[list[Environment]]
    handbacks: NotRequired[list[Handback]]
    capacity: NotRequired[Capacity]
    stages: NotRequired[list[dict[str, str | bool]]]
    groups: NotRequired[list[dict[str, str]]]


class Activity(TypedDict):
    quiet_min: float
    finished: bool
    changed: float


REQUIRED = {"items": ("id", "what", "stage", "next_event", "expected_by"), "sweeps": ("id", "what"),
            "workers": ("id", "model"), "pipelines": ("name", "result", "checked"), "fixtures": ("name", "env", "stage"),
            "environments": ("name", "capacity", "in_use"), "handbacks": ("worker", "what", "at")}


def when(text: str) -> datetime:
    """An ISO-8601 time; a time without a zone is UTC."""
    moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def owners(owner: str | list[str] | None) -> list[str]:
    return [owner] if isinstance(owner, str) and owner.strip() else [o for o in owner or [] if o.strip()]


def key(thing: str | int) -> str:
    return " ".join(str(thing).lower().split())


TIME_FIELDS = {"items": ("expected_by",), "sweeps": ("expected_by",), "pipelines": ("checked",), "handbacks": ("at", "answered"),
               "workers": ("read_until",)}
TEXT, ID, NAMES = (str,), (str, int), "names"
TYPES: dict[str, dict[str, tuple[type, ...] | str]] = {
    "items": {"id": ID, "what": TEXT, "stage": TEXT, "next_event": TEXT, "expected_by": TEXT, "group": TEXT, "area": TEXT,
              "waits_on": ID, "live_check": TEXT, "owner": NAMES, "live_check_owner": NAMES, "blocks": "ids"},
    "sweeps": {"id": ID, "what": TEXT, "owner": NAMES, "next_event": TEXT, "expected_by": TEXT},
    "workers": {"id": TEXT, "model": TEXT, "pace_min": "int", "reported": (bool,), "read_until": TEXT},
    "pipelines": {"name": TEXT, "result": TEXT, "checked": TEXT, "owner": NAMES},
    "fixtures": {"name": TEXT, "env": TEXT, "stage": TEXT, "used_by": TEXT},
    "environments": {"name": TEXT, "capacity": "int", "in_use": "int"},
    "handbacks": {"worker": TEXT, "what": TEXT, "at": TEXT, "answered": TEXT},
}


def well_typed(value: object, kind: tuple[type, ...] | str) -> bool:
    """A value of the field's type; None is allowed for text and names (required fields are checked apart), never for a number."""
    if kind == "int":
        return type(value) is int
    if value is None:
        return kind != (bool,)
    if kind == "names":
        return isinstance(value, str) or (isinstance(value, list) and all(isinstance(o, str) for o in value))
    if kind == "ids":
        return isinstance(value, list) and all(type(o) in (str, int) for o in value)
    return type(value) in kind  # type: ignore[operator]


def is_time(value: object) -> bool:
    try:
        when(value)  # type: ignore[arg-type]
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def invalid(board: object) -> list[str]:
    """Schema errors, checked before any field is read: a board with any of these cannot be checked."""
    if not isinstance(board, dict):
        return ["the board is not a JSON object"]
    errors: list[str] = []
    if not isinstance(board.get("updated"), str) or not is_time(board["updated"]):
        errors.append(f"updated {board.get('updated')!r} is not an ISO-8601 time")
    if not isinstance(board.get("items"), list):
        errors.append("items is not a list")
    rows: dict[str, list[dict]] = {}
    for section, fields in REQUIRED.items():
        value = board.get(section, [])
        if not isinstance(value, list):
            errors.append(f"{section} is not a list")
            continue
        rows[section] = [r for r in value if isinstance(r, dict)]
        errors += [f"{section}[{n}] is not an object" for n, r in enumerate(value) if not isinstance(r, dict)]
        for n, row in enumerate(rows[section]):
            errors += [f"{section}[{n}] has no {f}" for f in fields if row.get(f) in (None, "")]
            errors += [f"{section}[{n}].{f} {row[f]!r} is not an ISO-8601 time"
                       for f in TIME_FIELDS.get(section, ()) if row.get(f) not in (None, "") and not is_time(row[f])]
            errors += [f"{section}[{n}].{f} {row[f]!r} has the wrong type"
                       for f, kind in TYPES[section].items() if f in row and not well_typed(row[f], kind)]
            if section == "items" and "blocks" in row and row["blocks"] is None:
                errors.append(f"items[{n}].blocks is null (leave it out or give a list)")
    capacity = board.get("capacity")
    if capacity is not None and not (isinstance(capacity, dict) and type(capacity.get("target")) is int):
        errors.append("capacity.target is not a whole number")
    stages = board.get("stages", [])
    if not isinstance(stages, list) or not all(isinstance(s, dict) and isinstance(s.get("name"), str) for s in stages):
        errors.append("stages is not a list of objects with a name")
    if errors:
        return errors
    ids = [key(r["id"]) for r in rows["items"] + rows["sweeps"]]
    errors += [f"duplicate id {d}" for d, c in Counter(ids).items() if c > 1]
    listed = [s["name"] for s in stages]
    if listed:
        errors += [f"item {i['id']} has stage {i['stage']!r}, not in stages" for i in rows["items"] if i["stage"] not in listed]
    return errors


def activity(directory: Path, worker: str, marker: str, now: datetime) -> Activity | None:
    """The worker's newest activity record: minutes since it last changed, and whether its tail is an end of turn."""
    files = [p for p in directory.glob(f"{worker}*") if p.is_file() and (p.name == worker or p.name.startswith(worker + "."))]
    if not files:
        return None
    newest = max(files, key=lambda p: p.stat().st_mtime)
    quiet = (now.timestamp() - newest.stat().st_mtime) / 60
    with newest.open("rb") as handle:
        handle.seek(max(0, newest.stat().st_size - 4000))
        tail = handle.read().decode("utf-8", "replace")
    last = next((line for line in reversed(tail.splitlines()) if line.strip()), "")
    # only the final record says whether the run ended; a marker from an earlier turn is history
    return {"quiet_min": quiet, "finished": marker in last, "changed": newest.stat().st_mtime}


def statuses(directory: Path, worker: str) -> tuple[list[Status], int]:
    """The worker's usable status lines, oldest first, and the count of unusable ones (not JSON, no step, no valid time)."""
    path = directory / f"{worker}.jsonl"
    lines: list[Status] = []
    unusable = 0
    for line in path.read_text().splitlines() if path.is_file() else []:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            record = None
        usable = (isinstance(record, dict) and isinstance(record.get("step"), str) and is_time(record.get("at"))
                  and (record.get("expected_end") in (None, "") or is_time(record["expected_end"]))
                  and (record.get("round") is None or type(record["round"]) is int)
                  and all(record.get(f) is None or isinstance(record[f], str)
                          for f in ("finding_class", "unsent", "waiting_on", "last_result")))
        if usable:
            lines.append(record)
        elif line.strip():
            unusable += 1
    return lines, unusable


def minutes(since: str, now: datetime) -> float:
    return (now - when(since)).total_seconds() / 60


def status_findings(history: list[Status], now: datetime, stall_min: float, read_until: str | None = None) -> dict[str, list[str]]:
    """Failed replies, late, stuck and looping, from one worker's status lines (progress, not liveness).

    A failed reply stays a finding until the coordinator records ``read_until`` at or after it on the board, so the
    worker's next ordinary step does not hide it."""
    last = history[-1]
    found: dict[str, list[str]] = defaultdict(list)
    for line in history:
        if line.get("unsent") and (not read_until or when(line["at"]) > when(read_until)):
            found["reply to the coordinator failed"].append(
                f"{line['unsent']!r} at {line['at']} (read it, then set read_until; fix the reply address in the brief)")
    if last.get("expected_end") and when(last["expected_end"]) < now:
        found["late past its expected end"].append(f"{last['step']!r} expected {last['expected_end']} "
                                                   f"({minutes(last['expected_end'], now):.0f} min late)")
    position = (last["step"], last.get("round"))
    changed = next((n for n in range(len(history) - 1, -1, -1) if (history[n]["step"], history[n].get("round")) != position), None)
    since = history[changed + 1] if changed is not None else history[0]
    if minutes(since["at"], now) >= stall_min:
        found["no step change"].append(f"{last['step']!r} since {since['at']} ({minutes(since['at'], now):.0f} min)")
    # a review outcome is a line that names a finding class; a round can name several; work steps leave it empty
    per_round: dict[int, set[str]] = defaultdict(set)
    for line in history:
        if line.get("round") is not None and line.get("finding_class"):
            per_round[line["round"]].add(line["finding_class"])
    rounds = sorted(per_round)[-3:]
    recurring = set.intersection(*(per_round[r] for r in rounds)) - {"none"} if len(rounds) == 3 else set()
    for finding_class in sorted(recurring):
        found["review loop: same finding class 3 rounds"].append(f"{finding_class!r} in rounds {rounds} (escalate, see review.md)")
    return found


def findings(board: Board, now: datetime, activity_dir: Path | None = None, quiet_min: float = 30,
             stale_min: float = 30, marker: str = FINISHED_MARKER, status_dir: Path | None = None,
             stall_min: float = 60, handback_min: float = 10) -> dict[str, list[str]]:
    """Each loop question with the rows that fail it; an empty dict means nothing needs the coordinator."""
    found: dict[str, list[str]] = defaultdict(list)
    items, sweeps = board["items"], board.get("sweeps", [])
    workers = {w["id"]: w for w in board.get("workers", [])}
    age = (now - when(board["updated"])).total_seconds() / 60
    if age > stale_min:
        found["board not refreshed"].append(f"updated {age:.0f} min ago (refresh from the tracker first)")

    rows = [(str(i["id"]), i) for i in items] + [(str(s["id"]), s) for s in sweeps]
    owned = {key(rid): bool(owners(r.get("owner"))) for rid, r in rows}
    for rid, row in rows:
        if not owners(row.get("owner")):
            found["no owner"].append(f"{rid} {row['what']}")
        elif not row.get("next_event") or not row.get("expected_by"):
            found["no next event with an expected time"].append(f"{rid} {row['what']}")
        elif when(row["expected_by"]) < now:
            late = (now - when(row["expected_by"])).total_seconds() / 60
            found["late"].append(f"{rid} {row['next_event']!r} expected {row['expected_by']} ({late:.0f} min late)")

    waiting: dict[str, list[str]] = defaultdict(list)
    for item in items:
        if item.get("waits_on") not in (None, ""):  # an item id can be 0
            waiting[key(item["waits_on"])].append(str(item["id"]))
    for thing, waiters in waiting.items():
        if thing in owned and not owned[thing]:
            found["blocker item has no owner"].append(f"{thing} (waited on by {', '.join(waiters)})")
        elif thing not in owned and len(waiters) >= 2:
            found["shared blocker is not an item"].append(f"{thing!r} waited on by {', '.join(waiters)}")
    for item in items:
        for blocked in item.get("blocks", []):
            if key(blocked) not in owned:
                found["blocks names an unknown id"].append(f"{item['id']} blocks {blocked}")

    for item in items:
        if item.get("live_check") and not owners(item.get("live_check_owner")):
            found["live check has no owner"].append(f"{item['id']} {item['live_check']}")

    for pipe in board.get("pipelines", []):
        if pipe["result"] not in PIPELINE_OK and not owners(pipe.get("owner")):
            found["pipeline red with no owner"].append(f"{pipe['name']}: {pipe['result']}")
        checked = (now - when(pipe["checked"])).total_seconds() / 60
        if checked > stale_min:
            found["pipeline not checked"].append(f"{pipe['name']} last read {checked:.0f} min ago")

    busy = ({o for _, r in rows for o in owners(r.get("owner"))} | {o for i in items for o in owners(i.get("live_check_owner"))}
            | {o for p in board.get("pipelines", []) for o in owners(p.get("owner"))})
    for wid, worker in workers.items():
        if wid not in busy:
            found["worker owns nothing"].append(wid)
        history, unusable = statuses(status_dir, wid) if status_dir else ([], 0)
        if unusable:
            found["unusable status lines"].append(f"{wid}: {unusable} (each needs at, step and valid times)")
        for question, rows_ in (status_findings(history, now, stall_min, worker.get("read_until")).items() if history else ()):
            found[question] += [f"{wid} {r}" for r in rows_]
        if status_dir and not history:
            found["worker writes no status"].append(wid)
        if activity_dir is None:
            continue
        record = activity(activity_dir, wid, marker, now)
        if record is None:
            if not history:
                found["worker has no activity record"].append(wid)
        elif (record["finished"] and not worker.get("reported") and record["quiet_min"] >= 3
              and not (history and when(history[-1]["at"]).timestamp() > record["changed"])):
            found["finished without reporting"].append(f"{wid} (last activity {record['quiet_min']:.0f} min ago)")
        elif not history and record["quiet_min"] >= worker.get("pace_min", quiet_min):
            found["quiet past its pace"].append(f"{wid} quiet {record['quiet_min']:.0f} min (ask it; check its processes)")

    for env in board.get("environments", []):
        if env["in_use"] > env["capacity"]:
            found["environment over capacity"].append(f"{env['name']}: {env['in_use']} runs on {env['capacity']} (cap the proofs)")
    for back in board.get("handbacks", []):
        if not back.get("answered") and minutes(back["at"], now) > handback_min:
            found["hand-back waits on the coordinator"].append(
                f"{back['worker']} {back['what']} ({minutes(back['at'], now):.0f} min; answer before anything else)")

    capacity = board.get("capacity")
    if capacity:
        running = len([w for w in workers if w in busy])
        if running < capacity["target"] and not capacity.get("idle_reason"):
            found["idle capacity"].append(f"{running} of {capacity['target']} slots busy: run the idle-work search, "
                                          "or write capacity.idle_reason")
    return dict(found)


def summary(board: Board) -> list[str]:
    order = [s["name"] for s in board.get("stages", [])]
    counts = Counter(i["stage"] for i in board["items"])
    staged = [s for s in order if s in counts] + [s for s in counts if s not in order]
    lines = [f"Board {board['updated']}: {len(board['items'])} items, {len(board.get('workers', []))} workers, "
             f"{len(board.get('sweeps', []))} sweeps, {len(board.get('pipelines', []))} pipelines, "
             f"{len(board.get('fixtures', []))} fixtures"]
    lines.append("Stages: " + " · ".join(f"{s} {counts[s]}" for s in staged))
    waits = [minutes(h["at"], when(h["answered"])) for h in board.get("handbacks", []) if h.get("answered")]
    if waits:
        lines.append(f"Coordinator latency: median {statistics.median(waits):.0f} min, max {max(waits):.0f} min "
                     f"over {len(waits)} answered hand-backs (target under 10)")
    groups = Counter(i.get("group", "(no group)") for i in board["items"])
    lines.append("Groups: " + " · ".join(f"{g} {n}" for g, n in groups.items()))
    return lines


def check(args: argparse.Namespace) -> tuple[int, str]:
    try:
        board = json.loads(args.board.read_text())
    except (OSError, json.JSONDecodeError) as error:
        return 2, f"❌ invalid board: cannot read {args.board}: {error}"
    errors = invalid(board)
    if errors:
        return 2, "❌ invalid board:\n" + "\n".join(f"  - {e}" for e in errors)
    now = when(args.now) if args.now else datetime.now(timezone.utc)
    found = findings(board, now, args.activity_dir, args.quiet_min, args.stale_min, args.finished_marker,
                     args.status_dir, args.stall_min, args.handback_min)
    lines = summary(board)
    for question, rows in found.items():
        lines.append(f"❌ {question} ({len(rows)}):")
        lines += [f"  - {r}" for r in rows]
    lines.append(f"❌ {sum(map(len, found.values()))} findings need the coordinator" if found else "✅ nothing needs the coordinator")
    return (1 if found else 0), "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("board", type=Path)
    parser.add_argument("--status-dir", type=Path, help="per-worker status files <worker id>.jsonl (primary signal)")
    parser.add_argument("--activity-dir", type=Path, help="per-worker activity records (fallback signal)")
    parser.add_argument("--quiet-min", type=float, default=30, help="minutes of silence before a worker without status is quiet")
    parser.add_argument("--stall-min", type=float, default=60, help="minutes without a step or round change before a worker is stuck")
    parser.add_argument("--stale-min", type=float, default=30, help="minutes before the board or a pipeline read is stale")
    parser.add_argument("--handback-min", type=float, default=10, help="minutes a hand-back may wait for the coordinator")
    parser.add_argument("--finished-marker", default=FINISHED_MARKER, help="text that marks an end of turn in an activity record")
    parser.add_argument("--now", help="check as of this ISO-8601 time (default: now)")
    parser.add_argument("--watch", type=float, help="re-check every N minutes; exit at the first finding")
    parser.add_argument("--deadline-min", type=float, default=240, help="with --watch: exit 0 after this many minutes")
    args = parser.parse_args(argv)
    deadline = time.monotonic() + args.deadline_min * 60
    while True:
        code, report = check(args)
        remaining = deadline - time.monotonic()
        if code or not args.watch or remaining <= 0:
            if args.watch and not code:
                report += f"\n✅ watch ended at its {args.deadline_min:g} min deadline with no finding"
            print(report)
            return code
        time.sleep(min(args.watch * 60, remaining))  # the last sleep ends at the deadline, and one more check runs there

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
