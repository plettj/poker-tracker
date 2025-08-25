#!/usr/bin/env python3
# plot_aa_grid.py
import csv
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]


def pick_csv(arg=None):
    out = Path(__file__).resolve().parent / "output"
    if arg:
        p = out / arg
        if p.suffix != ".csv":
            p = p.with_suffix(".csv")
        return p
    csvs = sorted(out.glob("*.csv"))
    return csvs[0] if csvs else None


def load_hands(csv_path):
    hands = set()
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            h = row["hand"]
            if not h:
                continue
            if not h.startswith("AA"):
                continue
            # ignore mono for this plot
            if h.endswith("m"):
                continue
            hands.add(h)
    return hands


def label_for(r1, r2, tag):
    ranks = sorted(["A", "A", r1, r2], key=lambda r: RANKS.index(r))
    ranks = ranks[::-1]
    return "".join(ranks) + tag


def cell_colors(present):
    base_ns = (1, 1, 1)  # white
    base_s = (1.0, 1.0, 0.85)  # faint yellow
    green = (0.6, 0.9, 0.6)
    return (
        green if present.get("r") else base_ns,
        green if present.get("t") else base_ns,
        green if present.get("d") else base_s,
        green if present.get("p") else base_s,
    )


def draw_grid(have):
    n = len(RANKS)
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(RANKS)
    ax.set_yticklabels(RANKS)
    ax.tick_params(length=0)

    for i, r_row in enumerate(RANKS):
        for j, r_col in enumerate(RANKS):
            x, y = j, i
            if r_row != r_col:
                present = {
                    "r": label_for(r_row, r_col, "r") in have,
                    "t": label_for(r_row, r_col, "t") in have,
                    "d": label_for(r_row, r_col, "d") in have,
                    "p": label_for(r_row, r_col, "p") in have,
                }
                c_r, c_t, c_d, c_p = cell_colors(present)
                ax.add_patch(Rectangle((x, y), 1, 1, fill=False, lw=0.5, ec="0.8"))
                ax.add_patch(Rectangle((x, y), 0.5, 1, color=c_r, ec="0.8", lw=0.5))
                ax.add_patch(
                    Rectangle((x, y + 0.5), 0.5, 0.5, color=c_t, ec="0.8", lw=0.5)
                )
                ax.add_patch(
                    Rectangle((x + 0.5, y), 0.5, 1, color=c_d, ec="0.8", lw=0.5)
                )
                ax.add_patch(
                    Rectangle((x + 0.5, y + 0.5), 0.5, 0.5, color=c_p, ec="0.8", lw=0.5)
                )
            else:
                present = {
                    "r": label_for(r_row, r_col, "r") in have,
                    "t": label_for(r_row, r_col, "t") in have,
                    "d": label_for(r_row, r_col, "d") in have,
                    "p": label_for(r_row, r_col, "p") in have,
                }
                c_r, c_t, c_d, c_p = cell_colors(present)
                ax.add_patch(Rectangle((x, y), 1, 1, fill=False, lw=0.5, ec="0.8"))
                ax.add_patch(Rectangle((x, y), 0.5, 0.5, color=c_r, ec="0.8", lw=0.5))
                ax.add_patch(
                    Rectangle((x + 0.5, y), 0.5, 0.5, color=c_t, ec="0.8", lw=0.5)
                )
                ax.add_patch(
                    Rectangle((x, y + 0.5), 0.5, 0.5, color=c_d, ec="0.8", lw=0.5)
                )
                ax.add_patch(
                    Rectangle((x + 0.5, y + 0.5), 0.5, 0.5, color=c_p, ec="0.8", lw=0.5)
                )

            text = r_row + r_col
            ax.text(
                x + 0.5,
                y + 0.5,
                text,
                ha="center",
                va="center",
                color="black",
                fontsize=8,
            )

    ax.set_title("PLO4 – AA with Other Two Cards (r/t on left half, d/p on right half)")
    # tiny legend
    lx, ly = n + 0.2, 0.2
    ax.add_patch(Rectangle((lx, ly), 0.5, 0.5, fc=(1, 1, 1), ec="0.7"))
    ax.text(lx + 0.25, ly + 0.25, "r", ha="center", va="center")
    ax.add_patch(Rectangle((lx + 0.5, ly), 0.5, 0.5, fc=(1, 1, 1), ec="0.7"))
    ax.text(lx + 0.75, ly + 0.25, "t", ha="center", va="center")
    ax.add_patch(Rectangle((lx, ly + 0.6), 0.5, 0.5, fc=(1.0, 1.0, 0.85), ec="0.7"))
    ax.text(lx + 0.25, ly + 0.85, "d", ha="center", va="center")
    ax.add_patch(
        Rectangle((lx + 0.5, ly + 0.6), 0.5, 0.5, fc=(1.0, 1.0, 0.85), ec="0.7")
    )
    ax.text(lx + 0.75, ly + 0.85, "p", ha="center", va="center")
    ax.set_xlim(0, n + 1.5)
    plt.tight_layout()
    return fig


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    csv_path = pick_csv(arg)
    if not csv_path or not csv_path.exists():
        print("No CSV found in ./output" + ("" if not arg else f" for {arg}"))
        sys.exit(1)
    have = load_hands(csv_path)
    fig = draw_grid(have)
    out_img = Path(__file__).resolve().parent / "output" / "hands_made.png"
    fig.savefig(out_img, dpi=200)
    print(f"Drew AA grid from {csv_path.name} -> {out_img}")


if __name__ == "__main__":
    main()
