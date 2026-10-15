#!/usr/bin/env python3
"""Measure milestone close and reopen events from GitHub or a JSON fixture.

GitHub mode performs paginated GET requests through ``gh api`` only.
Fixture format::

    {"milestone": {"number": 1, "title": "Example"},
     "issues": [{"number": 10, "state": "closed"}],
     "timelines": {"10": [{"event": "closed", "created_at": "..."}]}}
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NotRequired, TypeAlias, TypedDict, cast

JSONValue: TypeAlias = None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]
JSONObject: TypeAlias = dict[str, JSONValue]
Metric: TypeAlias = dict[str, JSONValue]


class Milestone(TypedDict):
    number: int
    title: str


class Issue(TypedDict):
    number: int
    state: str
    created_at: NotRequired[str]
    pull_request: NotRequired[JSONObject]


class TimelineEvent(TypedDict, total=False):
    event: str
    created_at: str


class EventBuckets(TypedDict):
    closed: list[datetime]
    reopened: list[datetime]


def object_value(value: JSONValue, context: str) -> JSONObject:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a JSON object")
    return cast(JSONObject, value)


def array_value(value: JSONValue, context: str) -> list[JSONValue]:
    if not isinstance(value, list):
        raise ValueError(f"{context} must be a JSON array")
    return value


def required_string(obj: JSONObject, key: str, context: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{context}.{key} must be a string")
    return value


def optional_string(obj: JSONObject, key: str, context: str) -> str | None:
    if key not in obj or obj[key] is None:
        return None
    return required_string(obj, key, context)


def required_int(obj: JSONObject, key: str, context: str) -> int:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{context}.{key} must be an integer")
    return value


def parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"invalid ISO-8601 timestamp: {value!r}") from error
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp must include a timezone: {value!r}")
    return parsed.astimezone(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def decode_json(text: str, context: str) -> JSONValue:
    try:
        return cast(JSONValue, json.loads(text))
    except json.JSONDecodeError as error:
        raise ValueError(f"{context} is not valid JSON: {error}") from error


def gh_get(path: str) -> list[JSONObject]:
    try:
        result = subprocess.run(
            ["gh", "api", "--method", "GET", "--paginate", "--slurp", path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or "").strip()
        raise RuntimeError(f"gh GET failed for {path}: {detail or error}") from error
    pages = array_value(decode_json(result.stdout, path), path)
    flattened: list[JSONObject] = []
    for page_index, page_value in enumerate(pages):
        page = array_value(page_value, f"{path} page {page_index}")
        flattened.extend(object_value(item, f"{path} page {page_index} item {item_index}") for item_index, item in enumerate(page))
    return flattened


def parse_milestone(obj: JSONObject, context: str) -> Milestone:
    return {"number": required_int(obj, "number", context), "title": required_string(obj, "title", context)}


def parse_issue(obj: JSONObject, context: str) -> Issue:
    issue: Issue = {"number": required_int(obj, "number", context), "state": required_string(obj, "state", context)}
    created = optional_string(obj, "created_at", context)
    if created is not None:
        issue["created_at"] = created
    if "pull_request" in obj:
        issue["pull_request"] = object_value(obj["pull_request"], f"{context}.pull_request")
    return issue


def parse_timeline(obj: JSONObject, context: str) -> TimelineEvent:
    event: TimelineEvent = {}
    kind = optional_string(obj, "event", context)
    created = optional_string(obj, "created_at", context)
    if kind is not None:
        event["event"] = kind
    if created is not None:
        event["created_at"] = created
    return event


def load_data(args: argparse.Namespace) -> tuple[Milestone, list[Issue], dict[int, list[TimelineEvent]]]:
    if args.fixture:
        root = object_value(decode_json(Path(args.fixture).read_text(encoding="utf-8"), "fixture"), "fixture")
        milestone = parse_milestone(object_value(root.get("milestone"), "fixture.milestone"), "fixture.milestone")
        raw_issues = array_value(root.get("issues"), "fixture.issues")
        raw_timelines = object_value(root.get("timelines"), "fixture.timelines")
        issues = [parse_issue(object_value(value, f"fixture.issues[{index}]"), f"fixture.issues[{index}]") for index, value in enumerate(raw_issues)]
        timelines: dict[int, list[TimelineEvent]] = {}
        for key, value in raw_timelines.items():
            try:
                number = int(key)
            except (TypeError, ValueError) as error:
                raise ValueError(f"fixture.timelines key {key!r} is not an issue number") from error
            events = array_value(value, f"fixture.timelines[{key}]")
            timelines[number] = [parse_timeline(object_value(item, f"fixture.timelines[{key}][{index}]"), f"fixture.timelines[{key}][{index}]") for index, item in enumerate(events)]
        return milestone, issues, timelines
    if not args.repo or not args.milestone:
        raise ValueError("--repo and --milestone are required without --fixture")
    raw_milestones = gh_get(f"repos/{args.repo}/milestones?state=all&per_page=100")
    selector = str(args.milestone)
    matches = [item for item in raw_milestones if (selector.isdigit() and item.get("number") == int(selector)) or (not selector.isdigit() and item.get("title") == selector)]
    if len(matches) != 1:
        raise ValueError(f"milestone selector must match exactly one milestone; found {len(matches)}")
    milestone = parse_milestone(matches[0], "GitHub milestone")
    number = milestone["number"]
    raw_issues = gh_get(f"repos/{args.repo}/issues?milestone={number}&state=all&per_page=100")
    issues = [parse_issue(item, f"GitHub issue[{index}]") for index, item in enumerate(raw_issues) if "pull_request" not in item]
    if len({issue["number"] for issue in issues}) != len(issues):
        raise ValueError("current milestone membership contains duplicate issue numbers")
    timelines = {
        issue["number"]: [parse_timeline(item, f"GitHub issue {issue['number']} timeline[{index}]") for index, item in enumerate(gh_get(f"repos/{args.repo}/issues/{issue['number']}/timeline?per_page=100"))]
        for issue in issues
    }
    return milestone, issues, timelines


def event_times(issues: list[Issue], timelines: dict[int, list[TimelineEvent]]) -> dict[int, EventBuckets]:
    result: dict[int, EventBuckets] = {}
    for issue in issues:
        number = issue["number"]
        events = timelines.get(number)
        if events is None:
            raise ValueError(f"missing timeline for issue {number}")
        buckets: EventBuckets = {"closed": [], "reopened": []}
        for index, event in enumerate(events):
            kind = event.get("event")
            if kind not in {"closed", "reopened"}:
                continue
            created = event.get("created_at")
            if created is None:
                raise ValueError(f"{kind} event for issue {number} timeline[{index}] has no created_at")
            buckets[kind].append(parse_time(created))
        result[number] = buckets
    return result


def metrics(events: dict[int, EventBuckets], numbers: set[int], since: datetime, until: datetime, *, end_inclusive: bool = True) -> Metric:
    def in_window(timestamp: datetime) -> bool:
        return since <= timestamp <= until if end_inclusive else since <= timestamp < until

    closure_pairs = sorted((timestamp, number) for number in numbers for timestamp in events[number]["closed"] if in_window(timestamp))
    closures = [timestamp for timestamp, _ in closure_pairs]
    reopens = [timestamp for number in numbers for timestamp in events[number]["reopened"] if in_window(timestamp)]
    history = [timestamp for number in numbers for timestamp in events[number]["closed"] if (timestamp <= until if end_inclusive else timestamp < until)]
    gaps = [(right - left).total_seconds() for left, right in zip(closures, closures[1:])]
    boundary_gaps = [(closures[0] - since).total_seconds(), (until - closures[-1]).total_seconds()] if closures else [(until - since).total_seconds()]
    elapsed_hours = (until - since).total_seconds() / 3600
    latest = max(history) if history else None
    return cast(Metric, {
        "closure_events": len(closures),
        "reopen_events": len(reopens),
        "unique_closed_issues": len({number for _, number in closure_pairs}),
        "net_closed_minus_reopened": len(closures) - len(reopens),
        "closures_per_hour": len(closures) / elapsed_hours,
        "median_inter_close_gap_seconds": statistics.median(gaps) if gaps else None,
        "longest_gap_including_window_boundaries_seconds": max(gaps + boundary_gaps),
        "elapsed_since_last_closure_seconds": (until - latest).total_seconds() if latest else None,
        "elapsed_since_last_closure_scope": "Latest available closure at or before window end, including before window start.",
        "window": {"since": iso(since), "until": iso(until), "elapsed_hours": elapsed_hours},
    })


def analysis_window(args: argparse.Namespace, issues: list[Issue], events: dict[int, EventBuckets], observed_at: datetime) -> tuple[datetime, datetime, datetime | None]:
    """(since, until, split): --since defaults to the earliest event, --until to now; split must sit strictly inside."""
    history_timestamps = [parse_time(issue["created_at"]) for issue in issues if "created_at" in issue]
    history_timestamps.extend(timestamp for buckets in events.values() for timestamp in buckets["closed"] + buckets["reopened"])
    since = parse_time(args.since) if args.since else (min(history_timestamps) if history_timestamps else None)
    if since is None:
        raise ValueError("cannot infer --since from an empty history; provide --since and --until")
    until = parse_time(args.until) if args.until else observed_at
    if until <= since:
        raise ValueError("--until must be strictly after --since")
    split = parse_time(args.split_at) if args.split_at else None
    if split is not None and not since < split < until:
        raise ValueError("--split-at must be strictly inside the analysis window")
    return since, until, split


def state_counts(issues: list[Issue]) -> dict[str, int]:
    states = {"open": 0, "closed": 0}
    for issue in issues:
        state = issue["state"]
        if state not in states:
            raise ValueError(f"unsupported issue state: {state!r}")
        states[state] += 1
    return states


def attributed_numbers(raw: str, numbers: set[int]) -> set[int]:
    try:
        attributed = {int(value.strip()) for value in raw.split(",") if value.strip()}
    except ValueError as error:
        raise ValueError("--attributed-issues must be comma-separated integers") from error
    if not attributed:
        raise ValueError("--attributed-issues cannot be empty")
    missing = attributed - numbers
    if missing:
        raise ValueError(f"attributed issue numbers are outside current membership: {sorted(missing)}")
    return attributed


def percent(part: int, whole: int) -> float | None:
    return part * 100 / whole if whole else None


def build_report(args: argparse.Namespace) -> dict[str, JSONValue]:
    observed_at = datetime.now(timezone.utc)
    milestone, issues, timelines = load_data(args)
    events = event_times(issues, timelines)
    since, until, split = analysis_window(args, issues, events, observed_at)
    states = state_counts(issues)
    numbers = {issue["number"] for issue in issues}
    denominator = len(issues)
    output: dict[str, JSONValue] = cast(dict[str, JSONValue], {
        "scope": {
            "milestone": {"number": milestone["number"], "title": milestone["title"]},
            "observed_at": iso(observed_at),
            "member_issue_numbers": sorted(numbers),
            "current_membership_issue_count": denominator,
            "membership_caveat": "The denominator is current membership; historical events are measured only for those issues.",
            "window": {"since": iso(since), "until": iso(until), "split_at": iso(split) if split else None},
        },
        "current_membership": {
            "open": states["open"],
            "closed": states["closed"],
            "open_percent": percent(states["open"], denominator),
            "closed_percent": percent(states["closed"], denominator),
        },
        "events": metrics(events, numbers, since, until),
    })
    if split:
        output["events_before_split"] = cast(JSONValue, metrics(events, numbers, since, split, end_inclusive=False))
        output["events_after_split"] = cast(JSONValue, metrics(events, numbers, split, until))
    if args.attributed_issues is not None:
        attributed = attributed_numbers(args.attributed_issues, numbers)
        output["attributed_subset"] = cast(JSONValue, {
            "issue_numbers": sorted(attributed),
            "events": metrics(events, attributed, since, until),
            "attribution_caveat": "This is an explicit issue-number subset; no actor or username attribution is inferred.",
        })
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="OWNER/REPOSITORY")
    parser.add_argument("--milestone", help="milestone number or exact title")
    parser.add_argument("--since", help="UTC ISO-8601 window start")
    parser.add_argument("--until", help="UTC ISO-8601 window end")
    parser.add_argument("--split-at", help="optional UTC ISO-8601 split point")
    parser.add_argument("--attributed-issues", help="comma-separated issue numbers for a separate subset")
    parser.add_argument("--fixture", help="offline JSON fixture; skips GitHub calls")
    args = parser.parse_args()
    if args.fixture and (args.repo or args.milestone):
        raise ValueError("--fixture cannot be combined with --repo or --milestone")
    print(json.dumps(build_report(args), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, TypeError, KeyError, IndexError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error
