#!/usr/bin/env python3
# plo4_first_wins_by_convention.py
import csv
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

RANKS = "23456789TJQKA"
RANK_IDX = {r: i for i, r in enumerate(RANKS)}

RX_HDR = re.compile(
    r"Poker Hand #(?P<id>\S+): (?P<game>.+?) - (?P<ts>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"
)
RX_BLOCK_START = re.compile(r"^Poker Hand #")
RX_DEALT_HERO = re.compile(r"^Dealt to Hero \[(?P<cards>[^\]]+)\]$")
RX_WIN_1 = re.compile(r"^Hero collected \$(\d[\d.]*) from pot")
RX_WIN_2 = re.compile(r"^Seat \d+: Hero .* (won|collected) \(\$[\d.]+\)")
RX_WIN_3 = re.compile(r"^Hero won \(\$[\d.]+\)")
# street detection tolerant to "FIRST FLOP", etc.
RX_FLOP = re.compile(r"\*\*\*\s*FLOP(?:\s*\*\*\*)?", re.I)
RX_TURN = re.compile(r"\*\*\*\s*TURN(?:\s*\*\*\*)?", re.I)
RX_RIVER = re.compile(r"\*\*\*\s*RIVER(?:\s*\*\*\*)?", re.I)
RX_SHOW = re.compile(r"( shows \[| showed \[)", re.I)


def suit_tag(cards):
    suits = [c[1].lower() for c in cards]
    counts = sorted(Counter(suits).values(), reverse=True)
    if counts == [4]:
        return "m"  # Mono-suited
    if counts == [3, 1]:
        return "t"  # Tri-suited
    if counts == [2, 2]:
        return "d"  # Double-suited (pure)
    if counts == [2, 1, 1]:
        return "s"  # Single-suited
    return "r"  # Rainbow


def hand_label(cards):
    ranks = sorted(
        [c[0].upper() for c in cards], key=lambda r: RANK_IDX[r], reverse=True
    )
    return "".join(ranks) + suit_tag(cards)


def exact_suits_string(cards):
    return "".join([r + s for r, s in cards])


def parse_blocks(text):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if not RX_BLOCK_START.match(lines[i]):
            i += 1
            continue
        start = i
        i += 1
        while i < len(lines) and not RX_BLOCK_START.match(lines[i]):
            i += 1
        yield lines[start:i]


def hero_cards_from_block(block):
    for l in block:
        m = RX_DEALT_HERO.match(l)
        if m:
            toks = m["cards"].split()
            return [(t[0], t[1]) for t in toks]
    return None


def hero_won(block):
    return any(
        RX_WIN_1.match(l) or RX_WIN_2.match(l) or RX_WIN_3.match(l) for l in block
    )


def classify_stage(block, showdown_hint):
    if showdown_hint:
        return "showdown"
    blob = "\n".join(block)
    f = bool(RX_FLOP.search(blob))
    t = bool(RX_TURN.search(blob))
    r = bool(RX_RIVER.search(blob))
    if not f:
        return "preflop"
    if f and not t:
        return "flop"
    if t and not r:
        return "turn"
    return "river"


def ts_from_header(block):
    m = RX_HDR.search(block[0])
    return datetime.strptime(m["ts"], "%Y/%m/%d %H:%M:%S") if m else None


def process_paths(inp_path):
    files = []
    p = Path(inp_path)
    if p.is_file():
        files = [p]
    else:
        for root, _, fn in os.walk(p):
            for name in fn:
                if name.lower().endswith((".txt", ".log")):
                    files.append(Path(root) / name)

    wins = {}
    for fp in files:
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for block in parse_blocks(text):
            ts = ts_from_header(block)
            if ts is None:
                continue
            cards = hero_cards_from_block(block)
            if not cards or len(cards) != 4:  # skip PLO-5/others
                continue
            if not hero_won(block):
                continue
            label = hand_label(cards)
            stage = classify_stage(block, any(RX_SHOW.search(l) for l in block))
            wins.setdefault(label, []).append(
                {
                    "ts": ts,
                    "day": ts.date().isoformat(),
                    "stage": stage,
                    "s": exact_suits_string(cards),
                }
            )
    return wins


def main():
    if len(sys.argv) < 2:
        print("Usage: python plo4_wins_by_hand.py <folder_name_inside_data>")
        sys.exit(1)

    folder_name = os.path.basename(sys.argv[1].strip("/\\"))
    root = Path(__file__).resolve().parent
    inp_dir = root / "data" / folder_name
    if not inp_dir.exists() or not inp_dir.is_dir():
        print(f"Input folder not found: {inp_dir}")
        sys.exit(1)

    out_dir = root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    outcsv = out_dir / f"{folder_name}.csv"

    wins = process_paths(str(inp_dir))
    rows = []
    for label, evts in wins.items():
        evts.sort(key=lambda e: e["ts"])
        first = evts[0]
        rows.append(
            {
                "hand": label,
                "first_win_day": first["day"],
                "first_win_situation": first["stage"],
                "wins": json.dumps([e["s"] for e in evts], ensure_ascii=False),
            }
        )

    rows.sort(key=lambda r: (r["first_win_day"], r["hand"]))
    with open(outcsv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f, fieldnames=["hand", "first_win_day", "first_win_situation", "wins"]
        )
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {outcsv}")


if __name__ == "__main__":
    main()
