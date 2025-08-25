#!/usr/bin/env python3
# count_distinct_plo4_labels.py
from itertools import combinations

RANKS = "23456789TJQKA"
SUITS = "cdhs"
RANK_IDX = {r: i for i, r in enumerate(RANKS)}


def suit_tag(cards):
    from collections import Counter

    c = Counter(s for _, s in cards)
    counts = sorted(c.values(), reverse=True)
    if counts == [4]:
        return "m"
    if counts == [3, 1]:
        return "t"
    if counts == [2, 2]:
        return "p"
    if counts == [2, 1, 1]:
        return "d"
    return "r"


def label(cards):
    rs = sorted((r for r, _ in cards), key=lambda x: RANK_IDX[x], reverse=True)
    return "".join(rs) + suit_tag(cards)


def main():
    deck = [(r, s) for r in RANKS for s in SUITS]
    labels = set(label(combo) for combo in combinations(deck, 4))
    print(len(labels))


if __name__ == "__main__":
    main()
