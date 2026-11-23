#!/usr/bin/env python3
"""Draw the open set as one 300 dpi image: a pie by release group, the focus group expanded by step, bars below.

The left pie holds every open item, one colour per release group; each non-focus group is split into its own slices in
shades of that colour. The focus group is one outlined block; dashed lines expand it into a right pie by step, drawn in
shades of the focus colour so it visibly matches the block. The group key is coloured words under the title. Bars below
repeat both pies with the same shades. Input is JSON; ``stages`` are the focus group by step, in order of operations::

    {"title": "All open: 48 at 9:27 PM EST (was 50)",
     "groups": [{"name": "1.1 staging", "color": "#22c55e", "slices": {"1.1 staging": 14}},
                {"name": "1.2+", "color": "#a855f7", "slices": {"Simulator": 29, "Ops & infra": 5}}],
     "stages": [{"name": "Moved in, no worker yet", "n": 0, "always_show": true},
                {"name": "Coding", "n": 10},
                {"name": "On development, live check left", "n": 4}]}

The focus group is ``groups[0]``. Every count comes from the tracker at draw time. A focus total that differs from the
stage total, a duplicate group, slice or stage name, or an empty focus is refused. A stage with 0 items is drawn only
when it is marked ``"always_show": true`` (as a bar with 0).

Usage: progress_chart.py INPUT.json OUTPUT.png
"""

from __future__ import annotations

import colorsys
import json
import math
import sys
import textwrap
from pathlib import Path
from typing import NotRequired, TypedDict


class Group(TypedDict):
    name: str
    color: str
    slices: dict[str, int]


class Stage(TypedDict):
    name: str
    n: int
    always_show: NotRequired[bool]


class ChartInput(TypedDict):
    title: str
    groups: list[Group]
    stages: list[Stage]


BACKGROUND, FOREGROUND, OUTLINE, AXIS, LEADER = "#0f172a", "#e2e8f0", "#facc15", "#475569", "#94a3b8"
LABEL_GAP = 0.17  # least distance between two outside labels, in pie radii


def checked(data: ChartInput) -> tuple[list[Group], list[Stage]]:
    """Groups without empty slices and the stages to show; a bad focus, a duplicate name or a mismatch fails loud."""
    groups: list[Group] = [{**g, "slices": {k: v for k, v in g["slices"].items() if v > 0}} for g in data["groups"]]
    groups = [g for g in groups if g["slices"]] if groups and groups[0]["slices"] else groups
    names = [g["name"] for g in data["groups"]]
    if len(set(names)) != len(names):
        raise SystemExit(f"❌ duplicate group names in {names}")
    labels = [k for g in groups for k in g["slices"]]
    if len(set(labels)) != len(labels):
        raise SystemExit(f"❌ duplicate slice names in {sorted(labels)}")
    stage_names = [s["name"] for s in data["stages"]]
    if len(set(stage_names)) != len(stage_names):
        raise SystemExit(f"❌ duplicate stage names in {stage_names}")
    if not groups or not groups[0]["slices"]:
        raise SystemExit("❌ the focus group (the first) has no items")
    if any(s["n"] < 0 for s in data["stages"]):
        raise SystemExit("❌ a stage has a negative count")
    stages = [s for s in data["stages"] if s["n"] > 0 or s.get("always_show")]
    focus_total, stage_total = sum(groups[0]["slices"].values()), sum(s["n"] for s in stages)
    if focus_total != stage_total:
        raise SystemExit(f"❌ focus slices total {focus_total} but stages total {stage_total}")
    return groups, stages


def shades(base: str, count: int) -> list[str]:
    """count shades of one colour, light to dark, so a group reads as one colour."""
    from matplotlib.colors import to_hex, to_rgb

    if count == 1:
        return [base]
    hue, _, sat = colorsys.rgb_to_hls(*to_rgb(base))
    return [to_hex(colorsys.hls_to_rgb(hue, 0.72 - 0.42 * i / (count - 1), sat)) for i in range(count)]


def text_color(fill: str) -> str:
    from matplotlib.colors import to_rgb

    red, green, blue = to_rgb(fill)
    return "#0f172a" if 0.2126 * red + 0.7152 * green + 0.0722 * blue > 0.6 else "white"


def wrap(text: str, width: int = 16) -> str:
    return "\n".join(textwrap.wrap(text, width))


def spread(wanted: list[float], lines: list[int] | None = None) -> list[float]:
    """Push wanted positions (ascending) apart so neighbours clear each other; a label of n lines is n times as tall."""
    lines = lines or [1] * len(wanted)
    placed: list[float] = []
    for value, count, before in zip(sorted(wanted), lines, [1] + lines):
        placed.append(max(value, placed[-1] + LABEL_GAP * (count + before) / 2) if placed else value)
    return placed


def plan_outside(angles_labels: list[tuple[float, str]], free: int) -> list[tuple[float, str, tuple[float, float], str]]:
    """Plan outside labels as (angle, text, label position, alignment) for a pie whose free side is ``free`` (+1 right, -1 left).

    Slices facing the free side get a column there, spread by height so no two overlap and no leader crosses another
    label. Slices facing the other side (where the dashed lines and the other pie are) get stacks above or below the
    pie, the one nearest the blocked side lowest and its text running toward that side, so a leader never runs through a neighbour's text."""
    planned: list[tuple[float, str, tuple[float, float], str]] = []
    column = sorted((al for al in angles_labels if math.cos(al[0]) * free >= 0), key=lambda al: math.sin(al[0]))
    for (angle, text), y in zip(column, spread([1.15 * math.sin(a) for a, _ in column], [t.count("\n") + 1 for _, t in column])):
        planned.append((angle, text, (free * 1.4, y), "left" if free > 0 else "right"))
    for up in (1, -1):
        stack = [al for al in angles_labels if math.cos(al[0]) * free < 0 and math.sin(al[0]) * up > 0]
        stack.sort(key=lambda al: free * math.cos(al[0]))  # nearest the blocked side first = lowest
        for (angle, text), height in zip(stack, spread([1.3] * len(stack), [t.count("\n") + 1 for _, t in stack])):
            planned.append((angle, text, (math.cos(angle), up * height), "right" if free > 0 else "left"))
    return planned


def label_sectors(ax, wedges, items: list[tuple[str, int, str]], total: int, free: int, size: int, inside_min: float) -> None:
    """Name each sector (name, count, fill colour) inside when big enough, else outside on a leader line; make room for the stacks."""
    outside: list[tuple[float, str]] = []
    for (name, count, fill), wedge in zip(items, wedges):
        angle = math.radians((wedge.theta1 + wedge.theta2) / 2)
        if count / total >= inside_min:
            ax.text(0.6 * math.cos(angle), 0.6 * math.sin(angle), f"{wrap(name, 12)}\n{count}", ha="center", va="center",
                    color=text_color(fill), fontsize=size, weight="bold")
        else:
            outside.append((angle, wrap(f"{name}: {count}", 40)))
    planned = plan_outside(outside, free)
    for angle, text, position, align in planned:
        ax.annotate(text, xy=(0.98 * math.cos(angle), 0.98 * math.sin(angle)), xytext=position, ha=align, va="center",
                    color=FOREGROUND, fontsize=size - 4, arrowprops={"arrowstyle": "-", "color": LEADER, "lw": 1.2})
    # the stacks above and below the pie sit inside the axes, so the caption and the bars below never touch them
    top = max([p[1] for *_, p, _ in planned if p[1] > 1.2] + [1.15]) + 0.15
    bottom = min([p[1] for *_, p, _ in planned if p[1] < -1.2] + [-1.15]) - 0.15
    ax.set_ylim(bottom, top)


def draw_bars(ax, rows: list[tuple[str, int, str]], title: str) -> None:
    """Horizontal bars, first row at the top; a bar over three times the next is clipped and labelled."""
    names, values, colors = (list(c) for c in zip(*rows))
    ranked = sorted((v for v in values if v > 0), reverse=True)
    cap = ranked[1] * 1.6 if len(ranked) > 1 and ranked[0] > 3 * ranked[1] else None
    shown = [min(v, cap) if cap else v for v in values]
    pad = max(max(shown), 1) * 0.01
    ax.barh(range(len(names)), shown, color=colors)
    ax.invert_yaxis()
    ax.set_yticks(range(len(names)), names, color=FOREGROUND, fontsize=14)
    for i, (value, bar) in enumerate(zip(values, shown)):
        clipped = cap is not None and value > cap
        ax.text(bar - pad if clipped else bar + pad, i, f"{value} ▸ bar cut short" if clipped else str(value), va="center",
                ha="right" if clipped else "left", color="white" if clipped else FOREGROUND, fontsize=14,
                weight="bold" if clipped else "normal")
    ax.set_facecolor(BACKGROUND)
    ax.tick_params(colors=FOREGROUND, labelsize=12)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.xaxis.get_major_locator().set_params(integer=True)
    ax.set_title(title, color=FOREGROUND, fontsize=20)


def draw(data: ChartInput, output: Path) -> None:
    groups, stages = checked(data)
    focus, rest = groups[0], groups[1:]
    focus_total = sum(focus["slices"].values())
    total = focus_total + sum(sum(g["slices"].values()) for g in rest)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import ConnectionPatch, Wedge

    fig = plt.figure(figsize=(26, 22), dpi=300, facecolor=BACKGROUND)
    grid = fig.add_gridspec(2, 2, height_ratios=[1.6, 1], width_ratios=[1.45, 1], hspace=0.28, wspace=0.8)
    big, small = fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1])
    fig.suptitle(data["title"], color=FOREGROUND, fontsize=26, y=0.995)

    # Big pie: the focus block first, centred on the right so it faces the small pie.
    half = 180 * focus_total / total
    rows = [(s, n, c) for g in rest for (s, n), c in zip(g["slices"].items(), shades(g["color"], len(g["slices"])))]
    wedges, _ = big.pie([focus_total] + [n for _, n, _ in rows], colors=[focus["color"]] + [c for *_, c in rows],
                        startangle=-half, counterclock=True, wedgeprops={"edgecolor": BACKGROUND, "linewidth": 2.5})
    label_sectors(big, wedges[1:], rows, total, -1, 20, 0.12)
    big.add_patch(Wedge((0, 0), 1.0, -half, half, fill=False, edgecolor=OUTLINE, linewidth=5, zorder=5))
    big.text(0.6, 0, f"{wrap(focus['name'], 12)}\n{focus_total}", ha="center", va="center", color=text_color(focus["color"]),
             fontsize=20, weight="bold", zorder=6)
    big.set_title(f"All open issues ({total})", color=FOREGROUND, fontsize=22, pad=14)

    # Group key: coloured words under the title, centred, no legend box.
    keys = [(f"■ {g['name']} ({sum(g['slices'].values())})", g["color"]) for g in groups]
    widths = [0.0105 * len(text) + 0.03 for text, _ in keys]
    position = 0.5 - sum(widths) / 2
    for (text, color), width in zip(keys, widths):
        fig.text(position, 0.958, text, color=color, fontsize=20, weight="bold", ha="left", va="center")
        position += width

    # Small pie: the focus block by step in shades of its colour, joined by dashed lines from the block's two edges.
    step_colors = dict(zip((s["name"] for s in stages), shades(focus["color"], len(stages))))
    drawn = [s for s in stages if s["n"] > 0]
    small_wedges, _ = small.pie([s["n"] for s in drawn], colors=[step_colors[s["name"]] for s in drawn], startangle=90,
                                counterclock=False, wedgeprops={"edgecolor": BACKGROUND, "linewidth": 2})
    label_sectors(small, small_wedges, [(s["name"], s["n"], step_colors[s["name"]]) for s in drawn], focus_total, 1, 18, 0.2)
    small.add_patch(plt.Circle((0, 0), 1.0, fill=False, edgecolor=OUTLINE, linewidth=5, zorder=5))
    small.set_title(f"{focus['name']} by step ({focus_total})", color=FOREGROUND, fontsize=22, pad=14)
    for angle, y in ((half, 1), (-half, -1)):
        radians = math.radians(angle)
        fig.add_artist(ConnectionPatch(xyA=(math.cos(radians), math.sin(radians)), coordsA=big.transData, xyB=(0, y),
                                       coordsB=small.transData, color=OUTLINE, linewidth=3, linestyle="--"))

    draw_bars(fig.add_subplot(grid[1, 0]), [(f"{focus['name']} (all steps)", focus_total, focus["color"])]
              + [(s, n, c) for s, n, c in rows], f"All open issues by group ({total})")
    draw_bars(fig.add_subplot(grid[1, 1]), [(s["name"], s["n"], step_colors[s["name"]]) for s in stages],
              f"{focus['name']} by step, top = earliest ({focus_total})")
    fig.savefig(output, facecolor=BACKGROUND, bbox_inches="tight")
    print(f"✅ wrote {output} ({total} items, {focus_total} in {focus['name']})")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    draw(json.loads(Path(argv[1]).read_text()), Path(argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
