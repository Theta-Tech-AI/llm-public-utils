#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("progress_chart", str(Path(__file__).resolve().parents[1] / "scripts" / "progress_chart.py"))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load progress chart module")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ProgressChartTest(unittest.TestCase):
    def test_slices_follow_the_order_of_operations_and_other_milestones_go_last(self) -> None:
        data = {"title": "t", "slices": [
            {"group": "next", "count": 9},
            {"group": "r1", "stage": "Proof running", "count": 1},
            {"group": "r1", "stage": "Coding", "count": 2},
            {"group": "r1", "stage": "Waiting on the operator or an outside party", "count": 3},
        ]}
        rows, total = MODULE.checked_rows(data)
        self.assertEqual([s.get("stage", s["group"]) for s, _ in rows],
                         ["Waiting on the operator or an outside party", "Coding", "Proof running", "next"])
        self.assertEqual(total, 15)

    def test_a_wrong_total_or_an_unknown_stage_is_refused(self) -> None:
        with self.assertRaises(SystemExit):
            MODULE.checked_rows({"title": "t", "total": 5, "slices": [{"group": "r1", "stage": "Coding", "count": 2}]})
        with self.assertRaises(SystemExit):
            MODULE.checked_rows({"title": "t", "slices": [{"group": "r1", "stage": "Being built", "count": 2}]})


if __name__ == "__main__":
    unittest.main()
