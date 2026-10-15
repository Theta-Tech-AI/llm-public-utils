#!/usr/bin/env python3
import argparse
import importlib.util
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("closure_metrics", str(Path(__file__).resolve().parents[1] / "scripts" / "closure_metrics.py"))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load closure metrics module")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def timestamp(minutes: int) -> datetime:
    return datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=minutes)


class FakeGh:
    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        self.commands.append(command)
        endpoint = command[-1]
        pages: list[list[dict[str, object]]]
        if endpoint == "repos/acme/project/milestones?state=all&per_page=100":
            pages = [[], [{"number": 7, "title": "Sample"}]]
        elif endpoint == "repos/acme/project/issues?milestone=7&state=all&per_page=100":
            pages = [
                [
                    {"number": 10, "state": "closed", "created_at": "2026-01-01T00:00:00Z"},
                    {"number": 11, "state": "closed", "created_at": "2026-01-01T00:00:00Z", "pull_request": {}},
                ],
                [{"number": 12, "state": "open", "created_at": "2026-01-01T00:00:00Z"}],
            ]
        elif endpoint == "repos/acme/project/issues/10/timeline?per_page=100":
            pages = [[{"event": "closed", "created_at": "2026-01-01T00:01:00Z"}], [{"event": "reopened", "created_at": "2026-01-01T00:02:00Z"}]]
        elif endpoint == "repos/acme/project/issues/12/timeline?per_page=100":
            pages = [[]]
        else:
            raise AssertionError(f"unexpected route: {endpoint}")
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(pages), stderr="")


class ClosureMetricsTests(unittest.TestCase):
    def test_fixture_rejects_live_source_selectors(self) -> None:
        for option, value in (("--repo", "acme/project"), ("--milestone", "7")):
            with self.subTest(option=option):
                with patch.object(MODULE.sys, "argv", ["closure_metrics.py", "--fixture", "unused.json", option, value]):
                    with self.assertRaisesRegex(ValueError, "cannot be combined"):
                        MODULE.main()

    def test_github_routes_paginate_and_exclude_pull_requests(self) -> None:
        fake = FakeGh()
        args = argparse.Namespace(repo="acme/project", milestone="7", fixture=None)
        with patch.object(MODULE.subprocess, "run", side_effect=fake):
            milestone, issues, timelines = MODULE.load_data(args)
        self.assertEqual(milestone["number"], 7)
        self.assertEqual([issue["number"] for issue in issues], [10, 12])
        self.assertEqual(sorted(timelines), [10, 12])
        endpoints = [command[-1] for command in fake.commands]
        self.assertIn("repos/acme/project/issues?milestone=7&state=all&per_page=100", endpoints)
        self.assertNotIn("repos/acme/project/milestones/7/issues?state=all&per_page=100", endpoints)
        self.assertNotIn("repos/acme/project/issues/11/timeline?per_page=100", endpoints)
        self.assertTrue(all(command[0:6] == ["gh", "api", "--method", "GET", "--paginate", "--slurp"] for command in fake.commands))

    def test_window_split_repeat_close_prior_close_and_no_close(self) -> None:
        events = {
            1: {"closed": [timestamp(-5), timestamp(5), timestamp(10), timestamp(20), timestamp(21)], "reopened": [timestamp(3)]},
            2: {"closed": [], "reopened": [timestamp(4)]},
            3: {"closed": [timestamp(-5)], "reopened": []},
        }
        since, split, until = timestamp(0), timestamp(10), timestamp(20)
        overall = MODULE.metrics(events, {1, 2, 3}, since, until)
        before = MODULE.metrics(events, {1, 2, 3}, since, split, end_inclusive=False)
        after = MODULE.metrics(events, {1, 2, 3}, split, until)
        self.assertEqual((overall["closure_events"], overall["reopen_events"], overall["unique_closed_issues"]), (3, 2, 1))
        self.assertEqual(overall["elapsed_since_last_closure_seconds"], 0.0)
        self.assertEqual(before["closure_events"], 1)
        self.assertEqual(before["elapsed_since_last_closure_seconds"], 300.0)
        self.assertEqual(after["closure_events"], 2)
        self.assertEqual(MODULE.metrics({1: {"closed": [timestamp(-5)], "reopened": []}}, {1}, since, until)["elapsed_since_last_closure_seconds"], 1500.0)
        self.assertIsNone(MODULE.metrics({2: {"closed": [], "reopened": [timestamp(4)]}}, {2}, since, until)["elapsed_since_last_closure_seconds"])

    def test_empty_explicit_window_and_strict_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "empty.json"
            fixture.write_text(json.dumps({"milestone": {"number": 1, "title": "Empty"}, "issues": [], "timelines": {}}), encoding="utf-8")
            empty_args = argparse.Namespace(fixture=str(fixture), repo=None, milestone=None, since="2026-01-01T00:00:00Z", until="2026-01-01T00:01:00Z", split_at=None, attributed_issues=None)
            report = MODULE.build_report(empty_args)
            self.assertEqual(report["scope"]["current_membership_issue_count"], 0)
        fixture_args = argparse.Namespace(fixture=str(Path(__file__).with_name("closure_fixture.json")), repo=None, milestone=None, since="2026-01-01T00:00:00Z", until="2026-01-01T01:00:00Z", split_at="2026-01-01T00:04:00Z", attributed_issues=None)
        with self.assertRaisesRegex(ValueError, "strictly after"):
            MODULE.build_report(argparse.Namespace(**{**vars(fixture_args), "until": "2026-01-01T00:00:00Z"}))
        with self.assertRaisesRegex(ValueError, "strictly inside"):
            MODULE.build_report(argparse.Namespace(**{**vars(fixture_args), "split_at": "2026-01-01T00:00:00Z"}))
        with self.assertRaisesRegex(ValueError, "strictly inside"):
            MODULE.build_report(argparse.Namespace(**{**vars(fixture_args), "split_at": "2026-01-01T01:00:00Z"}))

    def test_malformed_fixture_is_a_clear_value_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "bad.json"
            fixture.write_text(json.dumps({"milestone": {"number": 1, "title": "Bad"}}), encoding="utf-8")
            args = argparse.Namespace(fixture=str(fixture), repo=None, milestone=None)
            with self.assertRaisesRegex(ValueError, "fixture.issues must be a JSON array"):
                MODULE.load_data(args)


if __name__ == "__main__":
    unittest.main(verbosity=2)
