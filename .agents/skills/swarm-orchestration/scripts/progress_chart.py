#!/usr/bin/env python3
"""Draw the open set as one image: a pie on the left, the same slices as horizontal bars on the right.

The bars run in the order of operations for an item (waiting → building → checks → batch → proof), so the reader
sees where work piles up. Pie and bars share one colour per stage. Input is JSON::

    {"title": "79 open · release 1.1 = 20 (was 24 at 5:37 PM)",
     "total": 79,
     "slices": [{"group": "release 1.1", "stage": "Coding", "count": 3},
                {"group": "release 1.2", "count": 51}]}

A slice without a stage is a whole milestone outside the focus; it sorts last. ``stages`` may replace the default
order and colours: ``[{"name": "...", "color": "#rrggbb"}]``. When ``total`` is given, the slices must add up to it.

Usage: progress_chart.py INPUT.json OUTPUT.png
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import NotRequired, TypedDict


class Stage(TypedDict):
    name: str
    color: str


class Slice(TypedDict):
    group: str
    count: int
    stage: NotRequired[str]


class ChartInput(TypedDict):
    title: str
    slices: list[Slice]
    total: NotRequired[int]
    stages: NotRequired[list[Stage]]


# Order of operations for one item; blocked states first, delivery last.
DEFAULT_STAGES: list[Stage] = [
    {"name": "Waiting on the operator or an outside party", "color": "#f97316"},
    {"name": "Scheduled event", "color": "#0ea5e9"},
    {"name": "Ready, no owner", "color": "#ef4444"},
    {"name": "Finding the cause", "color": "#84cc16"},
    {"name": "Coding", "color": "#22c55e"},
    {"name": "Waits a deploy for its next step", "color": "#eab308"},
    {"name": "Final checks", "color": "#6366f1"},
    {"name": "In a batch (lands at push)", "color": "#3b82f6"},
    {"name": "Proof running", "color": "#14b8a6"},
    {"name": "After the release window", "color": "#b45309"},
]
OTHER_COLORS = ["#a855f7", "#7e22ce", "#c084fc", "#6b21a8"]
BACKGROUND = "#0f172a"
NAMED_SHARE = 0.10  # pie slices at least this big carry their group name; the bars name every slice


def ordered(data: ChartInput) -> list[tuple[Slice, str]]:
    """Slices in order of operations, each with its colour; unknown stages fail loud."""
    stages = data.get("stages", DEFAULT_STAGES)
    index = {stage["name"]: position for position, stage in enumerate(stages)}
    colors = {stage["name"]: stage["color"] for stage in stages}
    staged = [s for s in data["slices"] if "stage" in s]
    unknown = sorted({s["stage"] for s in staged} - index.keys())
    if unknown:
        raise SystemExit(f"❌ unknown stage(s): {unknown}; known: {list(index)}")
    staged.sort(key=lambda s: (index[s["stage"]], s["group"]))
    others = [s for s in data["slices"] if "stage" not in s]
    return [(s, colors[s["stage"]]) for s in staged] + [
        (s, OTHER_COLORS[i % len(OTHER_COLORS)]) for i, s in enumerate(others)
    ]


def label(item: Slice, one_group: bool) -> str:
    """One shared group goes to the title, so each bar names only its stage."""
    if "stage" not in item:
        return item["group"]
    return item["stage"] if one_group else f"{item['group']} · {item['stage']}"


def checked_rows(data: ChartInput) -> tuple[list[tuple[Slice, str]], int]:
    """The non-empty slices in drawing order, refused when they do not add up to the stated total."""
    rows = [(s, c) for s, c in ordered(data) if s["count"] > 0]
    total = sum(s["count"] for s, _ in rows)
    if "total" in data and data["total"] != total:
        raise SystemExit(f"❌ slices add up to {total}, not the stated total {data['total']}")
    return rows, total


def draw(data: ChartInput, output: Path) -> None:
    rows, total = checked_rows(data)
    one_group = len({s["group"] for s, _ in rows}) == 1
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (pie_ax, bar_ax) = plt.subplots(1, 2, figsize=(17, 8.5), dpi=150, gridspec_kw={"width_ratios": [1, 1.1]})
    fig.patch.set_facecolor(BACKGROUND)
    wedges, _ = pie_ax.pie(
        [s["count"] for s, _ in rows],
        colors=[c for _, c in rows],
        startangle=90,
        counterclock=False,
        wedgeprops={"edgecolor": BACKGROUND, "linewidth": 2},
    )
    for (item, _), wedge in zip(rows, wedges):
        share = item["count"] / total
        angle = math.radians((wedge.theta1 + wedge.theta2) / 2)
        named = share >= NAMED_SHARE and not one_group
        radius = 0.6 if named else 0.8
        text = f"{item['group']}\n{item['count']}" if named else str(item["count"])
        pie_ax.text(radius * math.cos(angle), radius * math.sin(angle), text, ha="center", va="center",
                    color="white", fontsize=12 if named else 9, fontweight="bold", linespacing=1.0)
    pie_ax.set_aspect("equal")

    bar_ax.set_facecolor(BACKGROUND)
    positions = list(range(len(rows)))[::-1]  # first stage at the top
    staged_max = max((s["count"] for s, _ in rows if "stage" in s), default=1)
    limit = max(5.0, staged_max * 1.6)  # a huge non-focus bar must not squash the focus bars
    bar_ax.barh(positions, [min(s["count"], limit) for s, _ in rows], color=[c for _, c in rows])
    bar_ax.set_xlim(0, limit * 1.08)
    bar_ax.set_yticks(positions, [label(s, one_group) for s, _ in rows], color="white", fontsize=9)
    for position, (item, _) in zip(positions, rows):
        clipped = item["count"] > limit
        x = limit * 0.97 if clipped else item["count"] + limit * 0.01
        text = f"{item['count']} ▸" if clipped else str(item["count"])
        bar_ax.text(x, position, text, va="center", ha="right" if clipped else "left", color="white",
                    fontsize=9, fontweight="bold" if clipped else "normal")
    bar_ax.tick_params(axis="x", colors="#94a3b8")
    for side in ("top", "right"):
        bar_ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        bar_ax.spines[side].set_color("#475569")
    bar_ax.set_xlabel("open items, in order of operations (top = earliest)", color="#94a3b8")

    fig.suptitle(data["title"], color="white", fontsize=14)
    fig.tight_layout()
    fig.savefig(output, facecolor=BACKGROUND, bbox_inches="tight")
    print(f"✅ wrote {output} ({len(rows)} slices, {total} items)")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    data: ChartInput = json.loads(Path(argv[1]).read_text())
    draw(data, Path(argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
