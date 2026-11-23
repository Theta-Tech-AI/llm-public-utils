#!/usr/bin/env python3
import contextlib
import importlib.util
import io
import json
import tempfile
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

    def test_labels_wrap_on_word_boundaries_only(self) -> None:
        self.assertEqual(MODULE.wrap("Investigating now", 12), "Investigating\nnow")
        self.assertLess(MODULE.inside_font("Investigating", 20), 20)

    def test_shades_of_one_colour_run_light_to_dark(self) -> None:
        light, *_, dark = MODULE.shades("#22c55e", 4)
        self.assertGreater(sum(int(light[i:i + 2], 16) for i in (1, 3, 5)), sum(int(dark[i:i + 2], 16) for i in (1, 3, 5)))


    def test_a_bar_is_cut_only_when_it_dwarfs_the_next_by_five(self) -> None:
        self.assertIsNone(MODULE.bar_cap([12, 4, 1]))
        self.assertEqual(MODULE.bar_cap([15, 3, 1]), 3 * MODULE.CUT_TO)

    def test_board_counts_groups_steps_and_areas(self) -> None:
        board = json.loads((Path(__file__).resolve().parent / "board_fixture.json").read_text())
        data = MODULE.from_board(board, "Release staging")
        groups, stages = MODULE.checked(data)
        self.assertEqual([g["name"] for g in groups], ["Release staging", "Release production", "Later"])
        self.assertEqual(groups[0]["slices"], {"Release staging": 15})
        self.assertEqual(groups[1]["slices"], {"Proof": 1, "Outside party (Release production)": 1})
        self.assertEqual(stages[0], {"name": "Moved in, no worker yet", "always_show": True, "n": 1})
        self.assertEqual(sum(s["n"] for s in stages), 15)
        self.assertNotIn("Waiting on an outside party", [s["name"] for s in stages])

    def test_board_refuses_an_item_without_a_group_or_an_unknown_focus(self) -> None:
        with self.assertRaises(SystemExit):
            MODULE.from_board({"updated": "t", "items": [{"id": 1, "stage": "Coding"}]}, "g")
        with self.assertRaises(SystemExit):
            MODULE.from_board({"updated": "t", "items": [{"id": 1, "stage": "Coding", "group": "g"}]}, "other")

    def test_board_chart_renders_under_the_pixel_cap(self) -> None:
        board = Path(__file__).resolve().parent / "board_fixture.json"
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory, "chart.png")
            with contextlib.redirect_stdout(io.StringIO()):
                code = MODULE.main(["--board", str(board), "--focus-group", "Release staging", str(out)])
            self.assertEqual(code, 0)
            width, height = (int.from_bytes(out.read_bytes()[i:i + 4], "big") for i in (16, 20))
        self.assertLess(max(width, height), 8000)


if __name__ == "__main__":
    unittest.main()
