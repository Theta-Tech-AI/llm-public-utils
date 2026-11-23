#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("progress_chart", str(Path(__file__).resolve().parents[1] / "scripts" / "progress_chart.py"))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load progress chart module")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def chart(focus: dict[str, int], stages: list[dict]) -> dict:
    return {"title": "t", "groups": [{"name": "g", "color": "#22c55e", "slices": focus},
                                      {"name": "h", "color": "#a855f7", "slices": {"x": 3, "y": 0}}], "stages": stages}


class ProgressChartTest(unittest.TestCase):
    def test_zero_stage_is_kept_only_when_always_show(self) -> None:
        stages = [{"name": "New", "n": 0, "always_show": True}, {"name": "Gone", "n": 0}, {"name": "Coding", "n": 2}]
        groups, kept = MODULE.checked(chart({"g": 2}, stages))
        self.assertEqual([s["name"] for s in kept], ["New", "Coding"])
        self.assertEqual(groups[1]["slices"], {"x": 3})

    def test_mismatch_duplicate_and_empty_focus_are_refused(self) -> None:
        with self.assertRaises(SystemExit):
            MODULE.checked(chart({"g": 3}, [{"name": "Coding", "n": 2}]))
        with self.assertRaises(SystemExit):
            MODULE.checked(chart({"g": 2}, [{"name": "Coding", "n": 1}, {"name": "Coding", "n": 1}]))
        with self.assertRaises(SystemExit):
            MODULE.checked(chart({}, []))

    def test_outside_labels_never_overlap(self) -> None:
        ys = MODULE.spread([0.1, 0.11, 0.12])
        self.assertTrue(all(b - a >= MODULE.LABEL_GAP - 1e-9 for a, b in zip(ys, ys[1:])))

    def test_shades_of_one_colour_run_light_to_dark(self) -> None:
        light, *_, dark = MODULE.shades("#22c55e", 4)
        self.assertGreater(sum(int(light[i:i + 2], 16) for i in (1, 3, 5)), sum(int(dark[i:i + 2], 16) for i in (1, 3, 5)))


if __name__ == "__main__":
    unittest.main()
