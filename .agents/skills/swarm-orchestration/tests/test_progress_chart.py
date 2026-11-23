#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("progress_chart", str(Path(__file__).resolve().parents[1] / "scripts" / "progress_chart.py"))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load progress chart module")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

STAGES = [{"name": "Waiting", "color": "#f97316"}, {"name": "Coding", "color": "#22c55e"}, {"name": "Later", "color": "#a855f7"}]


def chart(focus: dict[str, int], rest: dict[str, int]) -> dict:
    return {"title": "t", "focus_group": "g", "stages": STAGES, "focus_items": focus, "rest_items": rest}


class ProgressChartTest(unittest.TestCase):
    def test_empty_stages_are_dropped_and_counts_kept(self) -> None:
        order, _, focus, rest = MODULE.checked(chart({"Coding": 2, "Waiting": 0}, {"Later": 9}))
        self.assertEqual((order, focus, rest), (["Waiting", "Coding", "Later"], {"Coding": 2}, {"Later": 9}))

    def test_an_unknown_stage_or_an_empty_focus_is_refused(self) -> None:
        with self.assertRaises(SystemExit):
            MODULE.checked(chart({"Being built": 2}, {}))
        with self.assertRaises(SystemExit):
            MODULE.checked(chart({}, {"Later": 3}))

    def test_a_wrong_total_or_a_duplicate_stage_is_refused(self) -> None:
        with self.assertRaises(SystemExit):
            MODULE.checked({**chart({"Coding": 2}, {}), "total": 5})
        with self.assertRaises(SystemExit):
            MODULE.checked({**chart({"Coding": 2}, {}), "stages": STAGES + STAGES[:1]})

    def test_outside_labels_on_one_side_never_overlap(self) -> None:
        placed = MODULE.spread([(0.1, 0.1, "a"), (0.12, 0.11, "b"), (0.2, 0.12, "c")])
        ys = sorted(y for _, y, _ in placed)
        self.assertTrue(all(b - a >= MODULE.LABEL_GAP - 1e-9 for a, b in zip(ys, ys[1:])))


if __name__ == "__main__":
    unittest.main()
