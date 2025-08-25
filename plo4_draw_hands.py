#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]


def pick_csv(arg=None):
    out = Path(__file__).resolve().parent / "output"
    if arg:
        p = out / (arg if arg.endswith(".csv") else f"{arg}.csv")
        return p
    csvs = sorted(out.glob("*.csv"))
    return csvs[0] if csvs else None


def load_have(csv_path):
    have = set()
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            h = (row.get("hand") or "").strip()
            if not h:
                continue
            if not h.startswith("AA"):
                continue
            have.add(h)
    return have


def label_for(r1, r2, tag):
    order = {r: i for i, r in enumerate("23456789TJQKA")}
    ranks = sorted(["A", "A", r1, r2], key=lambda r: order[r], reverse=True)
    return "".join(ranks) + tag


def colors(present):
    base_ns = (1, 1, 1)  # r,t
    base_s = (0.98, 0.98, 0.5)  # s,d
    green = (0.35, 0.92, 0.35)
    cr = green if present.get("r") else base_ns
    ct = green if present.get("t") else base_ns
    cs = green if present.get("s") else base_s
    cd = green if present.get("d") else base_s
    return cr, ct, cs, cd


def draw_grid(have):
    n = len(RANKS)
    fig, ax = plt.subplots(figsize=(13, 13))
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i, r_row in enumerate(RANKS):
        for j, r_col in enumerate(RANKS):
            x, y = j, i
            ax.add_patch(Rectangle((x, y), 1, 1, fill=False, lw=0.6, ec="0.8"))

            present = {
                "r": label_for(r_row, r_col, "r") in have,
                "t": label_for(r_row, r_col, "t") in have,
                "s": label_for(r_row, r_col, "s") in have,
                "d": label_for(r_row, r_col, "d") in have,
            }
            cr, ct, cs, cd = colors(present)

            # thin light border for every cell
            ax.add_patch(Rectangle((x, y), 1, 1, fill=False, lw=0.6, ec="0.8"))

            if i == j:
                # mini 2×2: top-left r, top-right t, bottom-left s, bottom-right d
                ax.add_patch(Rectangle((x, y), 0.5, 0.5, color=cr, ec="0.8", lw=0.5))
                ax.add_patch(
                    Rectangle((x + 0.5, y), 0.5, 0.5, color=ct, ec="0.8", lw=0.5)
                )
                ax.add_patch(
                    Rectangle((x, y + 0.5), 0.5, 0.5, color=cs, ec="0.8", lw=0.5)
                )
                ax.add_patch(
                    Rectangle((x + 0.5, y + 0.5), 0.5, 0.5, color=cd, ec="0.8", lw=0.5)
                )
                # darker outer border for paired (diagonal) cells
                pad = 0.01
                ax.add_patch(
                    Rectangle(
                        (x + pad, y + pad),
                        1 - 2 * pad,
                        1 - 2 * pad,
                        fill=False,
                        lw=1,
                        ec="0.2",
                        zorder=6,
                        joinstyle="miter",
                    )
                )
            elif j > i:
                # upper-right: suited only → left=s (2,1,1), right=d (2,2)
                ax.add_patch(Rectangle((x, y), 0.5, 1.0, color=cs, ec="0.8", lw=0.5))
                ax.add_patch(
                    Rectangle((x + 0.5, y), 0.5, 1.0, color=cd, ec="0.8", lw=0.5)
                )
            else:
                # bottom-left: non-suited only → left=r, right=t
                ax.add_patch(Rectangle((x, y), 0.5, 1.0, color=cr, ec="0.8", lw=0.5))
                ax.add_patch(
                    Rectangle((x + 0.5, y), 0.5, 1.0, color=ct, ec="0.8", lw=0.5)
                )

            ax.text(
                x + 0.5,
                y + 0.52,
                r_row + r_col,
                ha="center",
                va="center",
                color="black",
                fontsize=30,
                zorder=5,
            )

    ax.set_title("PLO4 — AA??", fontsize=18, pad=12)
    ax.set_title(
        "PLO4 — AA??\nbottom-left: rainbow|tri • top-right: single|double",
        fontsize=16,
        pad=12,
    )
    plt.tight_layout()
    return fig


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    csv_path = pick_csv(arg)
    if not csv_path or not csv_path.exists():
        print("No CSV found in ./output" + ("" if not arg else f" for {arg}"))
        raise SystemExit(1)
    have = load_have(csv_path)
    fig = draw_grid(have)
    out_img = csv_path.with_suffix("").with_name(csv_path.stem + "_AA_grid.png")
    fig.savefig(out_img, dpi=220, bbox_inches="tight")
    print(f"Drew AA grid from {csv_path.name} -> {out_img}")


if __name__ == "__main__":
    main()
