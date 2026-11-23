#!/usr/bin/env python3
"""Draw the open set as one 300 dpi image: a pie of all open items, the focus group expanded beside it, bars below.

The left pie holds every open item by stage. The focus group's sectors sit together and carry a yellow outline;
dashed lines expand them into a smaller pie on the right. Under each pie the same items are bars in the order of
operations (first stage at the top). Sectors carry their own labels (outside with a leader line when small); there
is no legend. Input is JSON; the order and colours of ``stages`` are the order of operations::

    {"title": "All open: 64, release 1.1: 8 (was 18 at 5:37 PM)",
     "total": 64,
     "focus_group": "Release 1.1",
     "stages": [{"name": "Waiting on the operator", "color": "#f97316"},
                {"name": "Coding", "color": "#22c55e"},
                {"name": "Planned for a later release", "color": "#a855f7"}],
     "focus_items": {"Coding": 8},
     "rest_items": {"Waiting on the operator": 1, "Planned for a later release": 55}}

Every count comes from the tracker at draw time. A duplicate or unknown stage name, a focus group with no items, or
counts that do not add up to the optional ``total`` are refused.

Usage: progress_chart.py INPUT.json OUTPUT.png
"""

from __future__ import annotations

import json
import math
import sys
import textwrap
from pathlib import Path
from typing import NotRequired, TypedDict


class Stage(TypedDict):
    name: str
    color: str


class ChartInput(TypedDict):
    title: str
    focus_group: str
    stages: list[Stage]
    focus_items: dict[str, int]
    rest_items: dict[str, int]
    total: NotRequired[int]


BACKGROUND, FOREGROUND, OUTLINE, AXIS = "#0f172a", "#e2e8f0", "#facc15", "#475569"
INSIDE_SHARE = 0.10  # a sector this big holds its own label; a smaller one gets a leader line
LABEL_GAP = 0.2  # least vertical distance between two outside labels on one side


def checked(data: ChartInput) -> tuple[list[str], dict[str, str], dict[str, int], dict[str, int]]:
    """Stage order, colours and the two count maps without empty stages; unknown stages and an empty focus fail loud."""
    names = [s["name"] for s in data["stages"]]
    if len(set(names)) != len(names):
        raise SystemExit(f"❌ duplicate stage names in {names}")
    unknown = sorted((data["focus_items"].keys() | data["rest_items"].keys()) - set(names))
    if unknown:
        raise SystemExit(f"❌ unknown stage(s): {unknown}; known: {names}")
    focus = {k: v for k, v in data["focus_items"].items() if v > 0}
    rest = {k: v for k, v in data["rest_items"].items() if v > 0}
    if not focus:
        raise SystemExit(f"❌ focus group {data['focus_group']!r} has no items")
    counted = sum(focus.values()) + sum(rest.values())
    if "total" in data and data["total"] != counted:
        raise SystemExit(f"❌ counts add up to {counted}, not the stated total {data['total']}")
    return names, {s["name"]: s["color"] for s in data["stages"]}, focus, rest


def wrap(text: str, width: int = 16) -> str:
    return "\n".join(textwrap.wrap(text, width))


def spread(labels: list[tuple[float, float, str]]) -> list[tuple[float, float, str]]:
    """Outside labels as (angle, y, text); push each side's labels apart so none overlap."""
    placed: list[tuple[float, float, str]] = []
    for right in (True, False):
        side = sorted((l for l in labels if (math.cos(l[0]) >= 0) == right), key=lambda l: l[1])
        last = -9.0
        for angle, y, text in side:
            last = max(y, last + LABEL_GAP)
            placed.append((angle, last, text))
    return placed


def label_sectors(ax, wedges, items: list[tuple[str, int]], total: int, inside_min: float, reach: float, size: int) -> None:
    """Name each sector inside when big enough, else outside on a leader line."""
    outside = []
    for (name, count), wedge in zip(items, wedges):
        angle = math.radians((wedge.theta1 + wedge.theta2) / 2)
        if count / total >= inside_min:
            ax.text(0.6 * math.cos(angle), 0.6 * math.sin(angle), f"{wrap(name)}\n{count}", ha="center", va="center",
                    color="white", fontsize=size, weight="bold")
        else:
            outside.append((angle, reach * math.sin(angle), f"{name}: {count}"))
    for angle, y, text in spread(outside):
        side = 1 if math.cos(angle) >= 0 else -1
        ax.annotate(text, xy=(0.98 * math.cos(angle), 0.98 * math.sin(angle)), xytext=(side * (reach + 0.1), y),
                    ha="left" if side > 0 else "right", va="center", color=FOREGROUND, fontsize=size - 4,
                    arrowprops={"arrowstyle": "-", "color": FOREGROUND, "lw": 1.2})


def draw_bars(ax, order: list[str], colors: dict[str, str], counts: dict[str, int], title: str) -> None:
    """Horizontal bars in order of operations; one bar over three times the next is clipped and labelled."""
    stages = [s for s in order if counts.get(s)]
    values = [counts[s] for s in stages]
    ranked = sorted(values, reverse=True)
    cap = ranked[1] * 1.6 if len(ranked) > 1 and ranked[0] > 3 * ranked[1] else None
    shown = [min(v, cap) if cap else v for v in values]
    pad = max(shown) * 0.01
    ax.barh(range(len(stages)), shown, color=[colors[s] for s in stages])
    ax.invert_yaxis()
    ax.set_yticks(range(len(stages)), stages, color=FOREGROUND, fontsize=16)
    for i, (value, bar) in enumerate(zip(values, shown)):
        clipped = cap is not None and value > cap
        ax.text(bar - pad if clipped else bar + pad, i, f"{value} ▸ bar cut short" if clipped else str(value), va="center",
                ha="right" if clipped else "left", color="white" if clipped else FOREGROUND, fontsize=16,
                weight="bold" if clipped else "normal")
    ax.set_facecolor(BACKGROUND)
    ax.tick_params(colors=FOREGROUND, labelsize=14)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.xaxis.get_major_locator().set_params(integer=True)
    ax.set_title(title, color=FOREGROUND, fontsize=20)
    ax.set_xlabel("open items, top = earliest in order of operations", color="#94a3b8", fontsize=14)


def draw(data: ChartInput, output: Path) -> None:
    order, colors, focus, rest = checked(data)
    focus_total, rest_total = sum(focus.values()), sum(rest.values())
    total = focus_total + rest_total
    group = data["focus_group"]
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import ConnectionPatch, Wedge

    fig = plt.figure(figsize=(24, 19), dpi=300, facecolor=BACKGROUND)
    grid = fig.add_gridspec(2, 2, height_ratios=[1.25, 1], width_ratios=[1.35, 1], hspace=0.18, wspace=0.75)
    big, small = fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1])
    fig.suptitle(data["title"], color=FOREGROUND, fontsize=26, y=0.985)

    # Big pie: the focus sectors first, centred on the right so they face the small pie.
    half = 180 * focus_total / total
    sectors = [(s, n, True) for s in order if (n := focus.get(s))] + [(s, n, False) for s in order if (n := rest.get(s))]
    wedges, _ = big.pie([n for _, n, _ in sectors], colors=[colors[s] for s, _, _ in sectors], startangle=-half,
                        counterclock=True, wedgeprops={"edgecolor": BACKGROUND, "linewidth": 2})
    others = [(i, s, n) for i, (s, n, is_focus) in enumerate(sectors) if not is_focus]
    label_sectors(big, [wedges[i] for i, _, _ in others], [(s, n) for _, s, n in others], total, INSIDE_SHARE, 1.5, 20)
    big.add_patch(Wedge((0, 0), 1.0, -half, half, fill=False, edgecolor=OUTLINE, linewidth=5, zorder=5))
    big.text(0.58, 0, f"{wrap(group, 9)}\n{focus_total}", ha="center", va="center", color="white", fontsize=17, weight="bold", zorder=6)
    big.text(0, -1.22, f"All open items ({total})", ha="center", va="top", color=FOREGROUND, fontsize=22)

    # Small pie: the focus sectors expanded, joined to the big pie by dashed lines from the wedge's two edges.
    small_wedges, _ = small.pie(list(focus.values()), colors=[colors[s] for s in focus], startangle=90, counterclock=False,
                                wedgeprops={"edgecolor": BACKGROUND, "linewidth": 2})
    label_sectors(small, small_wedges, list(focus.items()), focus_total, 0.18, 1.2, 17)
    small.add_patch(plt.Circle((0, 0), 1.0, fill=False, edgecolor=OUTLINE, linewidth=5, zorder=5))
    small.text(0, -1.22, f"{group} ({focus_total})", ha="center", va="top", color=FOREGROUND, fontsize=22)
    for angle, y in ((half, 1), (-half, -1)):
        radians = math.radians(angle)
        fig.add_artist(ConnectionPatch(xyA=(math.cos(radians), math.sin(radians)), coordsA=big.transData, xyB=(0, y),
                                       coordsB=small.transData, color=OUTLINE, linewidth=3, linestyle="--"))

    draw_bars(fig.add_subplot(grid[1, 0]), order, colors, {s: focus.get(s, 0) + rest.get(s, 0) for s in order},
              f"All open items by stage ({total})")
    draw_bars(fig.add_subplot(grid[1, 1]), order, colors, focus, f"{group} by stage ({focus_total})")
    fig.savefig(output, facecolor=BACKGROUND, bbox_inches="tight")
    print(f"✅ wrote {output} ({total} items, {focus_total} in {group})")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    data: ChartInput = json.loads(Path(argv[1]).read_text())
    draw(data, Path(argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
