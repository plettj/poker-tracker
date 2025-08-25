#!/usr/bin/env python3
import csv
import math
import sys
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

CARDS = tuple(["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"])
ORDER = {r: i for i, r in enumerate("23456789TJQKA")}


def two_label(a, b):
    return "".join(sorted([a, b], key=lambda r: ORDER[r], reverse=True))


def family_parts(hi):
    lowers = CARDS[CARDS.index(hi) :]
    return [(lo, len(CARDS) - CARDS.index(lo)) for lo in lowers]  # (lo, n)


def allowed_tags(hi, lo, r1, r2):
    counts = sorted(Counter([hi, lo, r1, r2]).values(), reverse=True)
    if counts == [4]:
        return {"r"}
    if counts == [3, 1]:
        return {"r", "s"}
    if counts == [2, 2]:
        return {"r", "s", "d"}
    if counts == [2, 1, 1]:
        return {"r", "s", "t", "d"}
    return {"r", "s", "t", "d", "m"}


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
    vals = [
        hi.strip().upper(),
        lo.strip().upper(),
        r1.strip().upper(),
        r2.strip().upper(),
    ]
    assert all(v in ORDER for v in vals), f"bad card in label_for: {vals}"
    ranks = sorted(vals, key=lambda x: ORDER[x], reverse=True)
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
    domain = [r for r in CARDS[CARDS.index(lo) :] if r in ORDER]  # ranks only
    assert all(r in ORDER for r in domain), f"bad cards in domain: {domain}"
    n = len(domain)

    EPS = 0.02  # small data margin to avoid clipping strokes
    ax.set_xlim(-EPS, n + EPS)
    ax.set_ylim(-EPS, n + EPS)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i, r_row in enumerate(domain):
        for j, r_col in enumerate(domain):
            x, y = j, i
            ax.add_patch(Rectangle((x, y), 1, 1, fill=False, lw=0.6, ec="0.8"))

            present = {
                "r": label_for(hi, lo, r_row, r_col, "r") in have_set,
                "t": label_for(hi, lo, r_row, r_col, "t") in have_set,
                "s": label_for(hi, lo, r_row, r_col, "s") in have_set,
                "d": label_for(hi, lo, r_row, r_col, "d") in have_set,
            }
            permits = allowed_tags(hi, lo, r_row, r_col)
            base_ns = (1, 1, 1)
            base_s = (0.98, 0.98, 0.5)
            green = (0.35, 0.92, 0.35)
            grey = (0.84, 0.86, 0.85)

            def col(tag):
                if tag not in permits:
                    return grey
                return (
                    green
                    if present.get(tag)
                    else (base_s if tag in ("s", "d") else base_ns)
                )

            cr, ct, cs, cd = col("r"), col("t"), col("s"), col("d")

            if i == j:
                ax.add_patch(
                    Rectangle((x, y), 0.5, 0.5, color=cs, ec="0.8", lw=0.5)
                )  # top-left: s
                ax.add_patch(
                    Rectangle((x + 0.5, y), 0.5, 0.5, color=cd, ec="0.8", lw=0.5)
                )  # top-right: d
                ax.add_patch(
                    Rectangle((x, y + 0.5), 0.5, 0.5, color=cr, ec="0.8", lw=0.5)
                )  # bottom-left: r
                ax.add_patch(
                    Rectangle((x + 0.5, y + 0.5), 0.5, 0.5, color=ct, ec="0.8", lw=0.5)
                )  # bottom-right: t
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
                two_label(r_row, r_col),
                ha="center",
                va="center",
                color="black",
                fontsize=14,
                zorder=5,
            )


def layout_family(m):
    if m <= 6:
        return 1, m
    cols = math.ceil(m / 2)
    return 2, cols


def render_family(csv_path, all_labels, hi, one_row=False):
    parts = family_parts(hi)

    if one_row:
        row1, row2 = parts, []
    else:
        total_w = sum(n for _, n in parts)
        cut, acc = 0, 0
        while cut < len(parts) and acc < total_w / 2:
            acc += parts[cut][1]
            cut += 1
        row1, row2 = parts[:cut], parts[cut:]

    CELL = 0.42
    GAP_W = 0.24
    GAP_H = 0.42
    TITLE_H = 0.70

    def row_dims(row):
        if not row:
            return 0.0, 0.0
        w = sum(n * CELL for _, n in row) + GAP_W * (len(row) - 1)
        h = max(n for _, n in row) * CELL
        return w, h

    w1, h1 = row_dims(row1)
    w2, h2 = row_dims(row2)
    inner_w = max(w1, w2)
    fig_w = inner_w
    fig_h = TITLE_H + h1 + (GAP_H if row2 else 0) + h2

    fig = plt.figure(figsize=(fig_w, fig_h))
    fig.suptitle(f"PLO4 — {hi}-high family  •  {csv_path.stem}", fontsize=20, y=0.995)

    def place_row(row, y_bottom_in, row_height_in):
        if not row:
            return
        row_w, _ = row_dims(row)
        x = (inner_w - row_w) / 2
        for lo, n in row:
            gw = gh = n * CELL
            bottom = y_bottom_in + (row_height_in - gh) / 2
            left = x
            ax = fig.add_axes([left / fig_w, bottom / fig_h, gw / fig_w, gh / fig_h])
            have = {hnd for hnd in all_labels if hnd.startswith(hi + lo)}
            draw_one(ax, have, hi, lo)
            ax.set_title(rf"$\mathbf{{{hi}{lo}}}$??", fontsize=16, pad=6)
            x += gw + GAP_W

    y1 = fig_h - TITLE_H - h1
    place_row(row1, y1, h1)
    if row2:
        place_row(row2, 0.0, h2)

    out_png = csv_path.with_suffix("").with_name(f"{csv_path.stem}_{hi}_family.png")
    fig.savefig(out_png, dpi=150, bbox_inches="tight", pad_inches=0.15)
    print(f"Wrote {out_png}")


def render_pair(csv_path, all_labels, pair):
    hi, lo = pair[0], pair[1]
    n = len(CARDS) - CARDS.index(lo)
    CELL, PAD = 0.46, 1.35  # inches per cell, padding
    fig = plt.figure(figsize=(CELL * n + PAD, CELL * n + PAD), constrained_layout=True)
    ax = fig.add_subplot(111)
    have = {h for h in all_labels if h.startswith(hi + lo)}
    draw_one(ax, have, hi, lo)
    ax.set_title(f"PLO4 — {hi}{lo}  •  {csv_path.stem}", fontsize=18, pad=28)
    out_png = csv_path.with_suffix("").with_name(f"{csv_path.stem}_{hi}{lo}_grid.png")
    fig.savefig(out_png, dpi=180, bbox_inches="tight", pad_inches=0.4)
    print(f"Wrote {out_png}")


def render_all(csv_path, all_labels):
    CELL = 0.42
    GAP_W = 0.24  # inside a family (between grids)
    FAM_GAP = 0.80  # between complete families (bigger)
    ROW_GAP = 0.42
    TITLE_H = 0.90

    def family_dims(parts):
        if not parts:
            return (0.0, 0.0)
        w = sum(n * CELL for _, n in parts) + GAP_W * (len(parts) - 1)
        h = max(n for _, n in parts) * CELL
        return w, h

    # banded order; first in each row will be flush-left, the rest flush-right
    bands = [
        ["A", "4", "3", "2"],
        ["K", "6", "5"],
        ["Q", "7"],
        ["J", "8"],
        ["T", "9"],
    ]
    bands = [[hi for hi in grp if hi in CARDS] for grp in bands]

    fam_parts = {hi: family_parts(hi) for grp in bands for hi in grp}

    # rows: [( [(hi, parts, w, h), ...], row_w, row_h ), ...]
    row_specs = []
    for grp in bands:
        fams, row_w, row_h = [], 0.0, 0.0
        for idx, hi in enumerate(grp):
            parts = fam_parts[hi]
            w, h = family_dims(parts)
            fams.append((hi, parts, w, h))
            row_w += (FAM_GAP if idx > 0 else 0.0) + w
            row_h = max(row_h, h)
        row_specs.append((fams, row_w, row_h))

    inner_w = max((rw for _, rw, _ in row_specs), default=0.0)
    fig_w = inner_w
    fig_h = TITLE_H + sum(h for _, _, h in row_specs) + ROW_GAP * (len(row_specs) - 1)

    fig = plt.figure(figsize=(fig_w, fig_h))
    fig.suptitle(
        f"PLO4 — All 6851 possible hands  •  {csv_path.stem}", fontsize=22, y=0.995
    )

    y = fig_h - TITLE_H
    for fams, row_w, row_h in row_specs:
        y -= row_h
        x_left = 0.0
        x_right = inner_w

        if not fams:
            y -= ROW_GAP
            continue

        # place FIRST family flush-left (bottom-aligned)
        first_hi, first_parts, first_w, _ = fams[0]
        gx = x_left
        for lo, n in first_parts:
            gw = gh = n * CELL
            bottom = y  # flat bottoms
            ax = fig.add_axes([gx / fig_w, bottom / fig_h, gw / fig_w, gh / fig_h])
            have = {h for h in all_labels if h.startswith(first_hi + lo)}
            draw_one(ax, have, first_hi, lo)
            ax.set_title(rf"$\mathbf{{{first_hi}{lo}}}$??", fontsize=14, pad=4)
            gx += gw + GAP_W

        # place remaining families as a right-aligned block
        rest = fams[1:]
        if rest:
            rest_w = sum(w for _, _, w, _ in rest) + FAM_GAP * (len(rest) - 1)
            gx = x_right - rest_w
            for idx, (hi, parts, w, _) in enumerate(rest):
                # grids inside a family
                for j, (lo, n) in enumerate(parts):
                    gw = gh = n * CELL
                    bottom = y
                    ax = fig.add_axes(
                        [gx / fig_w, bottom / fig_h, gw / fig_w, gh / fig_h]
                    )
                    have = {h for h in all_labels if h.startswith(hi + lo)}
                    draw_one(ax, have, hi, lo)
                    ax.set_title(rf"$\mathbf{{{hi}{lo}}}$??", fontsize=14, pad=4)
                    gx += gw + GAP_W
                # convert last internal GAP_W into a FAM_GAP, but skip after final family
                if idx < len(rest) - 1:
                    gx += FAM_GAP - GAP_W

        y -= ROW_GAP

    out_png = csv_path.with_suffix("").with_name(f"{csv_path.stem}_ALL_families.png")
    fig.savefig(out_png, dpi=120, bbox_inches="tight", pad_inches=0.15)
    print(f"Wrote {out_png}")


def main():
    if len(sys.argv) == 1:
        csv_path = pick_csv(None)
        if not csv_path:
            print("No CSV in ./output")
            return
        all_labels = load_all_labels(csv_path)
        render_all(csv_path, all_labels)
        return

    token = sys.argv[1].upper()
    csv_path = pick_csv(sys.argv[2] if len(sys.argv) > 2 else None)
    if not csv_path:
        print("No CSV in ./output")
        return
    all_labels = load_all_labels(csv_path)

    if len(token) == 1 and token in CARDS:
        render_family(csv_path, all_labels, token)
    elif (
        len(token) == 2
        and token[0] in CARDS
        and token[1] in CARDS
        and ORDER[token[0]] > ORDER[token[1]]
    ):
        render_pair(csv_path, all_labels, token)
    elif len(token) == 2 and token[0] == token[1] and token[0] in CARDS:  # e.g., AA
        render_pair(csv_path, all_labels, token)
    else:
        print("Usage:")
        print("  python plo4_draw_hands.py              # super-PNG")
        print("  python plo4_draw_hands.py A [csv]      # family: AA..A2")
        print("  python plo4_draw_hands.py AQ [csv]     # single grid")
        print("Valid ranks: A,K,Q,J,T,9,8,7,6,5,4,3,2")


if __name__ == "__main__":
    main()
