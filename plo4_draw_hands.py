#!/usr/bin/env python3
import csv
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
ORDER = {r: i for i, r in enumerate("23456789TJQKA")}


def pick_csv(stem=None):
    out = Path(__file__).resolve().parent / "output"
    if stem:
        p = out / (stem if stem.endswith(".csv") else f"{stem}.csv")
        return p if p.exists() else None
    csvs = sorted(out.glob("*.csv"))
    return csvs[0] if csvs else None


def load_all_labels(csv_path):
    s = set()
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            h = (row.get("hand") or "").strip()
            if h:
                s.add(h)
    return s


def label_for(hi, lo, r1, r2, tag):
    ranks = sorted([hi, lo, r1, r2], key=lambda r: ORDER[r], reverse=True)
    return "".join(ranks) + tag


def colors(present):
    base_ns = (1, 1, 1)
    base_s = (0.98, 0.98, 0.5)
    green = (0.35, 0.92, 0.35)
    cr = green if present.get("r") else base_ns
    ct = green if present.get("t") else base_ns
    cs = green if present.get("s") else base_s
    cd = green if present.get("d") else base_s
    return cr, ct, cs, cd


def draw_one(ax, have_set, hi, lo):
    allowed = RANKS[RANKS.index(lo) :]  # domain shrinks with lo
    n = len(allowed)
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i, r_row in enumerate(allowed):
        for j, r_col in enumerate(allowed):
            x, y = j, i
            ax.add_patch(Rectangle((x, y), 1, 1, fill=False, lw=0.6, ec="0.8"))
            present = {
                "r": label_for(hi, lo, r_row, r_col, "r") in have_set,
                "t": label_for(hi, lo, r_row, r_col, "t") in have_set,
                "s": label_for(hi, lo, r_row, r_col, "s") in have_set,
                "d": label_for(hi, lo, r_row, r_col, "d") in have_set,
            }
            cr, ct, cs, cd = colors(present)

            if i == j:
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
                ax.add_patch(Rectangle((x, y), 0.5, 1.0, color=cs, ec="0.8", lw=0.5))
                ax.add_patch(
                    Rectangle((x + 0.5, y), 0.5, 1.0, color=cd, ec="0.8", lw=0.5)
                )
            else:
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
                fontsize=22,
                zorder=5,
            )


def layout_family(m):
    if m <= 6:
        return 1, m
    cols = math.ceil(m / 2)
    return 2, cols


def render_family(csv_path, all_labels, hi):
    lowers = RANKS[RANKS.index(hi) :]  # include AA..A2
    parts = [(lo, len(RANKS) - RANKS.index(lo)) for lo in lowers]  # (lo, n)

    total_w = sum(n for _, n in parts)
    cut, acc = 0, 0
    while cut < len(parts) and acc < total_w / 2:
        acc += parts[cut][1]
        cut += 1
    row1, row2 = parts[:cut], parts[cut:]

    r1_max = max(n for _, n in row1) if row1 else 0
    r2_max = max(n for _, n in row2) if row2 else 0
    CELL, HM, VM = 0.46, 1.35, 1.6  # inches per cell, horiz/vert margins

    fig_w = CELL * max(sum(n for _, n in row1), sum(n for _, n in row2)) + HM
    fig_h = CELL * (r1_max + r2_max) + VM
    fig = plt.figure(figsize=(fig_w, fig_h))
    gs = fig.add_gridspec(
        nrows=2 if row2 else 1,
        ncols=1,
        height_ratios=[r1_max] + ([r2_max] if row2 else []),
        hspace=0.15,
    )
    fig.suptitle(f"PLO4 — {hi}-high families  •  {csv_path.stem}", fontsize=20, y=0.98)

    # row 1
    sub1 = gs[0].subgridspec(
        1, len(row1), width_ratios=[n for _, n in row1], wspace=0.06
    )
    for idx, (lo, n) in enumerate(row1):
        ax = fig.add_subplot(sub1[0, idx])
        have = {h for h in all_labels if h.startswith(hi + lo)}
        draw_one(ax, have, hi, lo)
        ax.set_title(f"{hi}{lo}", fontsize=16, pad=6)

    # row 2 (if any)
    if row2:
        sub2 = gs[1].subgridspec(
            1, len(row2), width_ratios=[n for _, n in row2], wspace=0.06
        )
        for idx, (lo, n) in enumerate(row2):
            ax = fig.add_subplot(sub2[0, idx])
            have = {h for h in all_labels if h.startswith(hi + lo)}
            draw_one(ax, have, hi, lo)
            ax.set_title(f"{hi}{lo}", fontsize=16, pad=6)

    out_png = csv_path.with_suffix("").with_name(f"{csv_path.stem}_{hi}_family.png")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_png, dpi=150)
    print(f"Wrote {out_png}")


def render_pair(csv_path, all_labels, pair):
    hi, lo = pair[0], pair[1]
    n = len(RANKS) - RANKS.index(lo)
    CELL, PAD = 0.42, 1.2
    fig = plt.figure(figsize=(CELL * n + PAD, CELL * n + PAD))
    ax = fig.add_subplot(111)
    have = {h for h in all_labels if h.startswith(hi + lo)}
    draw_one(ax, have, hi, lo)
    ax.set_title(f"PLO4 — {hi}{lo}  •  {csv_path.stem}", fontsize=18, pad=10)
    out_png = csv_path.with_suffix("").with_name(f"{csv_path.stem}_{hi}{lo}_grid.png")
    fig.tight_layout()
    fig.savefig(out_png, dpi=180)
    print(f"Wrote {out_png}")


def render_super(csv_path, all_labels):
    pairs = [(hi, lo) for hi in RANKS for lo in RANKS[RANKS.index(hi) :]]
    N = len(pairs)  # 91
    cols = 6
    rows = math.ceil(N / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5.2, rows * 5.2))
    try:
        axes = axes.ravel().tolist()
    except AttributeError:
        axes = [axes]
    fig.suptitle(f"PLO4 — ALL families  •  {csv_path.stem}", fontsize=22, y=0.995)

    for k, (hi, lo) in enumerate(pairs):
        ax = axes[k]
        have = {h for h in all_labels if h.startswith(hi + lo)}
        draw_one(ax, have, hi, lo)
        ax.set_title(f"{hi}{lo}", fontsize=14, pad=4)

    for k in range(N, len(axes)):
        axes[k].axis("off")

    out_png = csv_path.with_suffix("").with_name(f"{csv_path.stem}_ALL_families.png")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(out_png, dpi=120)
    print(f"Wrote {out_png}")


def main():
    if len(sys.argv) == 1:
        csv_path = pick_csv(None)
        if not csv_path:
            print("No CSV in ./output")
            return
        all_labels = load_all_labels(csv_path)
        render_super(csv_path, all_labels)
        return

    token = sys.argv[1].upper()
    csv_path = pick_csv(sys.argv[2] if len(sys.argv) > 2 else None)
    if not csv_path:
        print("No CSV in ./output")
        return
    all_labels = load_all_labels(csv_path)

    if len(token) == 1 and token in RANKS:
        render_family(csv_path, all_labels, token)
    elif (
        len(token) == 2
        and token[0] in RANKS
        and token[1] in RANKS
        and ORDER[token[0]] > ORDER[token[1]]
    ):
        render_pair(csv_path, all_labels, token)
    elif len(token) == 2 and token[0] == token[1] and token[0] in RANKS:  # e.g., AA
        render_pair(csv_path, all_labels, token)
    else:
        print("Usage:")
        print("  python plo4_draw_hands.py              # super-PNG")
        print("  python plo4_draw_hands.py A [csv]      # family: AA..A2")
        print("  python plo4_draw_hands.py AQ [csv]     # single grid")
        print("Valid ranks: A,K,Q,J,T,9,8,7,6,5,4,3,2")


if __name__ == "__main__":
    main()
