#!/usr/bin/env python3
import copy
import contextlib
import importlib.util
import io
import json
import os
import random
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("board_check", str(HERE.parent / "scripts" / "board_check.py"))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load board check module")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FIXTURE = json.loads((HERE / "board_fixture.json").read_text())
NOW = MODULE.when("2026-11-23T05:20Z")


def item(id_: str, **fields) -> dict:
    return {"id": id_, "what": id_, "stage": "Coding", "owner": "w1", "next_event": "push",
            "expected_by": "2026-11-23T06:00Z", **fields}


def board(*items: dict, **sections) -> dict:
    return {"updated": "2026-11-23T05:10Z", "items": list(items), "workers": [{"id": "w1", "model": "routine"}], **sections}


class BoardCheckTest(unittest.TestCase):
    def test_a_healthy_board_has_no_findings(self) -> None:
        self.assertEqual(MODULE.findings(board(item("a"), item("b", waits_on="a")), NOW), {})

    def test_each_loop_question_is_found(self) -> None:
        found = MODULE.findings(board(
            item("a", owner=None),
            item("b", expected_by="2026-11-23T05:00Z"),
            item("c", waits_on="release window"), item("d", waits_on="Release  window"),
            item("e", waits_on="f"), item("f", owner=[]),
            item("g", live_check="UI check on the deployed build"),
            pipelines=[{"name": "nightly", "result": "failure", "checked": "2026-11-23T05:15Z"}],
            capacity={"target": 4}), NOW)
        self.assertEqual(found["no owner"], ["a a", "f f"])
        self.assertIn("b", found["late"][0])
        self.assertEqual(found["shared blocker is not an item"], ["'release window' waited on by c, d"])
        self.assertEqual(found["blocker item has no owner"], ["f (waited on by e)"])
        self.assertEqual(found["live check has no owner"], ["g UI check on the deployed build"])
        self.assertEqual(found["pipeline red with no owner"], ["nightly: failure"])
        self.assertIn("1 of 4 slots busy", found["idle capacity"][0])

    def test_an_owned_blocker_or_an_idle_reason_clears_the_finding(self) -> None:
        sweep = {"id": "promo", "what": "promotion", "owner": "coordinator", "next_event": "x", "expected_by": "2026-11-23T06:00Z"}
        found = MODULE.findings(board(item("c", waits_on="promo"), item("d", waits_on="promo"), sweeps=[sweep],
                                      capacity={"target": 4, "idle_reason": "review queue full"}), NOW)
        self.assertEqual(found, {})

    def test_stale_board_and_unread_pipeline(self) -> None:
        found = MODULE.findings({**board(item("a")), "updated": "2026-11-23T04:00Z",
                                 "pipelines": [{"name": "deploy", "result": "success", "checked": "2026-11-23T04:00Z"}]}, NOW)
        self.assertIn("board not refreshed", found)
        self.assertIn("pipeline not checked", found)

    def test_activity_records_find_quiet_finished_and_missing_workers(self) -> None:
        workers = [{"id": "w1", "model": "routine"}, {"id": "w2", "model": "routine", "pace_min": 90},
                   {"id": "w3", "model": "routine"}, {"id": "w4", "model": "routine"}, {"id": "w5", "model": "routine", "reported": True}]
        items = [item(w["id"], owner=w["id"]) for w in workers]
        with tempfile.TemporaryDirectory() as directory:
            def record(name: str, text: str, minutes_ago: float) -> None:
                path = Path(directory, name)
                path.write_text(text)
                stamp = NOW.timestamp() - minutes_ago * 60
                os.utime(path, (stamp, stamp))
            record("w1.output", "working", 50)
            record("w2.output", "working", 50)
            record("w3.output", '{"stop_reason":"end_turn"}', 10)
            record("w5.output", '{"stop_reason":"end_turn"}', 10)
            found = MODULE.findings({**board(*items), "workers": workers}, NOW, Path(directory))
        self.assertEqual([r.split()[0] for r in found["quiet past its pace"]], ["w1"])
        self.assertEqual([r.split()[0] for r in found["finished without reporting"]], ["w3"])
        self.assertEqual(found["worker has no activity record"], ["w4"])

    def test_status_lines_find_late_stuck_and_looping_workers(self) -> None:
        def line(at: str, step: str, end: str, round_: int | None = None, cls: str | None = None) -> str:
            return json.dumps({"at": at, "step": step, "expected_end": end, "round": round_, "finding_class": cls})
        workers = [{"id": w, "model": "routine"} for w in ("late", "stuck", "loop", "fine", "silent", "unsent")]
        with tempfile.TemporaryDirectory() as directory:
            def status(worker: str, *lines: str) -> None:
                Path(directory, f"{worker}.jsonl").write_text("\n".join(lines) + "\n")
            status("late", line("2026-11-23T05:00Z", "tests", "2026-11-23T05:10Z"))
            status("stuck", line("2026-11-23T03:00Z", "build", "2026-11-23T03:30Z"),
                   line("2026-11-23T04:00Z", "review", "2026-11-23T06:00Z"), line("2026-11-23T05:00Z", "review", "2026-11-23T06:00Z"))
            status("loop", *(line(f"2026-11-23T05:1{r}Z", "review", "2026-11-23T06:00Z", r, "boundary parsing") for r in (2, 3, 4)))
            Path(directory, "unsent.jsonl").write_text(json.dumps({"at": "2026-11-23T05:15Z", "step": "review", "expected_end":
                "2026-11-23T06:00Z", "unsent": "could not reach coordinator: review PASS, ready to land"}) + "\n")
            status("fine", line("2026-11-23T05:00Z", "review", "2026-11-23T06:00Z", 1, "a"), "not json",
                   line("2026-11-23T05:10Z", "review", "2026-11-23T06:00Z", 2, "b"))
            found = MODULE.findings({**board(*(item(w["id"], owner=w["id"]) for w in workers)), "workers": workers},
                                    NOW, status_dir=Path(directory))
        self.assertEqual([r.split()[0] for r in found["late past its expected end"]], ["late"])
        self.assertEqual([r.split()[0] for r in found["no step change"]], ["stuck"])
        self.assertEqual([r.split()[0] for r in found["review loop: same finding class 3 rounds"]], ["loop"])
        self.assertEqual(found["worker writes no status"], ["silent"])
        self.assertEqual([r.split()[0] for r in found["reply to the coordinator failed"]], ["unsent"])

    def test_environment_over_capacity_and_unanswered_handback(self) -> None:
        found = MODULE.findings(board(item("a"), environments=[{"name": "stack", "capacity": 2, "in_use": 3}],
                                      handbacks=[{"worker": "w1", "what": "ready", "at": "2026-11-23T05:00Z"},
                                                 {"worker": "w1", "what": "old", "at": "2026-11-23T04:00Z", "answered": "2026-11-23T04:05Z"}]), NOW)
        self.assertEqual(found["environment over capacity"], ["stack: 3 runs on 2 (cap the proofs)"])
        self.assertEqual(len(found["hand-back waits on the coordinator"]), 1)
        self.assertIn("median 5 min", "\n".join(MODULE.summary(board(handbacks=[
            {"worker": "w1", "what": "old", "at": "2026-11-23T04:00Z", "answered": "2026-11-23T04:05Z"}]))))

    def test_watch_returns_at_the_first_finding(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            code = MODULE.main(["--watch", "1", "--now", "2026-11-23T05:20Z", str(HERE / "board_fixture.json")])
        self.assertEqual(code, 1)

    def test_invalid_board_is_refused(self) -> None:
        bad = board(item("a", stage="Nowhere"), item("a"), stages=[{"name": "Coding"}])
        errors = MODULE.invalid(bad)
        self.assertTrue(any("not in stages" in e for e in errors))
        self.assertTrue(any("duplicate id a" in e for e in errors))
        shape = board(item("a", expected_by="tomorrow"), {"what": "x", "stage": "Coding"}, "not a row",
                      environments=[{"name": "e", "capacity": "2", "in_use": 1}])
        errors = MODULE.invalid(shape)
        for expected in ("not an ISO-8601 time", "items[1] has no id", "items[2] is not an object", "environments[0].capacity"):
            self.assertTrue(any(expected in e for e in errors), expected)

    def test_malformed_boards_exit_2_without_a_crash(self) -> None:
        cases = [{"updated": None, "items": []}, {"updated": "2026-11-23T05:00Z", "items": None}, [],
                 {"updated": "2026-11-23T05:00Z", "items": [{"what": "no id", "stage": "s", "next_event": "e", "expected_by": "2026-11-23T06:00Z"}]}]
        with tempfile.TemporaryDirectory() as directory:
            for n, case in enumerate(cases + ["{not json"]):
                path = Path(directory, f"b{n}.json")
                path.write_text(case if isinstance(case, str) else json.dumps(case))
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(MODULE.main([str(path)]), 2, case)

    def test_a_failed_reply_stays_until_read_and_bad_status_lines_are_reported(self) -> None:
        workers = [{"id": "w1", "model": "routine"}]
        lines = [{"at": "2026-11-23T05:00Z", "step": "tests", "expected_end": "2026-11-23T06:00Z", "unsent": "ready to land"},
                 {"at": "2026-11-23T05:10Z", "step": "docs", "expected_end": "2026-11-23T06:00Z"}]
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "w1.jsonl").write_text("\n".join([*map(json.dumps, lines), "{}", "null", json.dumps({"at": "x", "step": "s"})]))
            found = MODULE.findings({**board(item("a")), "workers": workers}, NOW, status_dir=Path(directory))
            self.assertEqual(len(found["reply to the coordinator failed"]), 1)
            self.assertEqual(found["unusable status lines"], ["w1: 3 (each needs at, step and valid times)"])
            read = MODULE.findings({**board(item("a")), "workers": [{**workers[0], "read_until": "2026-11-23T05:00Z"}]},
                                   NOW, status_dir=Path(directory))
            self.assertNotIn("reply to the coordinator failed", read)
            Path(directory, "w1.jsonl").write_text("{}\n")
            only_bad = MODULE.findings({**board(item("a")), "workers": workers}, NOW, status_dir=Path(directory))
        self.assertEqual(only_bad["worker writes no status"], ["w1"])

    def test_repair_steps_do_not_erase_review_outcomes_and_bad_fields_are_unusable(self) -> None:
        lines = []
        for r, minute in ((1, 0), (2, 2), (3, 4)):
            lines.append({"at": f"2026-11-23T05:{minute}0Z", "step": "review", "round": r, "finding_class": "ordering"})
            lines.append({"at": f"2026-11-23T05:{minute}5Z", "step": "repair", "round": r, "finding_class": ""})
        lines += [{"at": "2026-11-23T05:50Z", "step": "s", "round": []}, {"at": "2026-11-23T05:50Z", "step": "s", "finding_class": []},
                  {"at": "2026-11-23T05:50Z", "step": "s", "round": "4"}]
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "w1.jsonl").write_text("\n".join(map(json.dumps, lines)))
            found = MODULE.findings(board(item("a")), NOW, status_dir=Path(directory))
            self.assertEqual(len(found["review loop: same finding class 3 rounds"]), 1)
            self.assertEqual(found["unusable status lines"], ["w1: 3 (each needs at, step and valid times)"])
            clean = lines[:6] + [{"at": "2026-11-23T05:15Z", "step": "review", "round": 4, "finding_class": "none"}]
            Path(directory, "w1.jsonl").write_text("\n".join(map(json.dumps, clean)))
            self.assertNotIn("review loop: same finding class 3 rounds", MODULE.findings(board(item("a")), NOW, status_dir=Path(directory)))

    def test_a_round_with_several_classes_still_counts_and_null_pace_is_invalid(self) -> None:
        lines = [{"at": f"2026-11-23T05:{r}0Z", "step": "review", "round": r, "finding_class": c}
                 for r in (1, 2, 3) for c in ("boundary parsing", f"other {r}")]
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "w1.jsonl").write_text("\n".join(map(json.dumps, lines)))
            found = MODULE.findings(board(item("a")), NOW, status_dir=Path(directory))
        self.assertEqual(len(found["review loop: same finding class 3 rounds"]), 1)
        self.assertTrue(any("pace_min" in e for e in MODULE.invalid({**board(item("a")), "workers": [{"id": "w1", "model": "m", "pace_min": None}]})))

    def test_an_earlier_end_of_turn_or_newer_status_is_not_finished(self) -> None:
        with tempfile.TemporaryDirectory() as status, tempfile.TemporaryDirectory() as activity:
            record = Path(activity, "w1.output")
            record.write_text('{"stop_reason":"end_turn"}\n{"type":"tool_use"}\n')
            stamp = NOW.timestamp() - 600
            os.utime(record, (stamp, stamp))
            self.assertNotIn("finished without reporting", MODULE.findings(board(item("a")), NOW, activity_dir=Path(activity)))
            record.write_text('{"type":"tool_use"}\n{"stop_reason":"end_turn"}\n')
            os.utime(record, (stamp, stamp))
            self.assertIn("finished without reporting", MODULE.findings(board(item("a")), NOW, activity_dir=Path(activity)))
            Path(status, "w1.jsonl").write_text(json.dumps({"at": "2026-11-23T05:15Z", "step": "build", "expected_end": "2026-11-23T06:00Z"}))
            self.assertNotIn("finished without reporting",
                             MODULE.findings(board(item("a")), NOW, activity_dir=Path(activity), status_dir=Path(status)))

    def test_wrongly_typed_fields_are_invalid(self) -> None:
        bad = {**board(item("a", stage=["Coding"]), item("b", blocks=None)),
               "workers": [{"id": ["w1"], "model": "routine"}],
               "pipelines": [{"name": "p", "result": ["failure"], "checked": "2026-11-23T05:00Z"}]}
        errors = MODULE.invalid(bad)
        for expected in ("items[0].stage", "items[1].blocks is null", "workers[0].id", "pipelines[0].result"):
            self.assertTrue(any(expected in e for e in errors), expected)

    def test_fresh_status_needs_no_activity_record(self) -> None:
        with tempfile.TemporaryDirectory() as status, tempfile.TemporaryDirectory() as activity:
            Path(status, "w1.jsonl").write_text(json.dumps({"at": "2026-11-23T05:15Z", "step": "build", "expected_end": "2026-11-23T06:00Z"}))
            found = MODULE.findings(board(item("a")), NOW, activity_dir=Path(activity), status_dir=Path(status))
        self.assertEqual(found, {})

    def test_a_zero_id_is_a_real_blocker(self) -> None:
        found = MODULE.findings(board(item("a", waits_on=0), item("b", waits_on=0)), NOW)
        self.assertEqual(found["shared blocker is not an item"], ["'0' waited on by a, b"])

    def test_a_pipeline_owner_is_busy(self) -> None:
        found = MODULE.findings(board(item("a", owner="coordinator"), capacity={"target": 1},
                                      pipelines=[{"name": "p", "result": "failure", "checked": "2026-11-23T05:15Z", "owner": "w1"}]), NOW)
        self.assertEqual(found, {})

    def test_watch_runs_its_last_check_at_the_deadline(self) -> None:
        clock = [0.0]
        sleeps: list[float] = []
        healthy = board(item("a"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "b.json")
            path.write_text(json.dumps(healthy))
            original = (MODULE.time.monotonic, MODULE.time.sleep)
            MODULE.time.monotonic = lambda: clock[0]
            MODULE.time.sleep = lambda seconds: (sleeps.append(seconds), clock.__setitem__(0, clock[0] + seconds))
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = MODULE.main(["--watch", "10", "--deadline-min", "25", "--now", "2026-11-23T05:20Z", str(path)])
            finally:
                MODULE.time.monotonic, MODULE.time.sleep = original
        self.assertEqual(code, 0)
        self.assertEqual(sleeps, [600, 600, 300])

    def test_property_any_accepted_board_and_any_status_line_never_crash_the_check(self) -> None:
        """Invariant from three review rounds of crash findings: invalid() never raises, and a board it accepts,
        with any status lines and activity records, never makes findings() raise."""
        rng = random.Random(9)
        values = [None, [], {}, "", "x", 0, -1, 2.5, True, ["w1"], [1, None], {"a": 1}, "2026-11-23T05:00Z", "tomorrow"]
        sections = ["items", "sweeps", "workers", "pipelines", "environments", "handbacks", "fixtures"]
        with tempfile.TemporaryDirectory() as status, tempfile.TemporaryDirectory() as activity:
            for case in range(400):
                mutant = copy.deepcopy(FIXTURE)
                for _ in range(rng.randint(1, 4)):
                    section = rng.choice(sections + ["updated", "capacity", "stages"])
                    if section in sections and mutant.get(section):
                        row = rng.choice(mutant[section])
                        row[rng.choice(list(row) + ["blocks", "pace_min", "read_until", "answered"])] = rng.choice(values)
                    else:
                        mutant[section] = rng.choice(values)
                line = {k: rng.choice(values) for k in ("at", "step", "expected_end", "round", "finding_class", "unsent")}
                Path(status, "w-acadd5.jsonl").write_text(json.dumps(line) + "\n" + json.dumps({**line, "at": "2026-11-23T05:00Z", "step": "s"}))
                Path(activity, "w-acadd5.output").write_text(rng.choice(['{"stop_reason":"end_turn"}', "x", ""]))
                try:
                    if not MODULE.invalid(mutant):
                        MODULE.findings(mutant, NOW, Path(activity), status_dir=Path(status))
                except Exception as error:  # noqa: BLE001 - the property is "no exception of any kind"
                    self.fail(f"case {case} raised {error!r}")

    def test_worked_example_board_is_valid_and_needs_the_coordinator(self) -> None:
        self.assertEqual(MODULE.invalid(copy.deepcopy(FIXTURE)), [])
        found = MODULE.findings(FIXTURE, NOW)
        self.assertEqual(found["shared blocker is not an item"], ["'dependency bump' waited on by 104, 105"])
        statuses = MODULE.findings(FIXTURE, NOW, status_dir=HERE / "status_fixture")
        self.assertEqual([r.split()[0] for r in statuses["review loop: same finding class 3 rounds"]], ["w-ab4587"])
        self.assertEqual([r.split()[0] for r in statuses["reply to the coordinator failed"]], ["w-a08502"])
        with contextlib.redirect_stdout(io.StringIO()):
            code = MODULE.main(["--now", "2026-11-23T05:20Z", str(HERE / "board_fixture.json")])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
