"""Exact Jacks or Better calculator. Pure Python 3, standard library only.

Every one of the 2,598,960 five-card deals and all 32 ways to hold cards are
covered without simulation. The work is cut down in two ways.

1. A table holds, for every set of 0 to 5 cards, how many final hands of each
   rank contain that set. Inclusion and exclusion over the discarded cards then
   gives the exact draw outcomes for any hold.
2. Deals that differ only by a relabelling of suits play the same, so only
   134,459 distinct deals are solved and each is weighted by its count.

Cards are numbers 0 to 51: rank * 4 + suit. Rank 0 is a two, 12 is an ace.
"""
from itertools import combinations
from math import comb

RANKS = "23456789TJQKA"
SUITS = "cdhs"
HANDS = ["Nothing", "Jacks or better", "Two pair", "Three of a kind", "Straight",
         "Flush", "Full house", "Four of a kind", "Straight flush", "Royal flush"]
NOTHING, JOB, TWO_PAIR, TRIPS, STRAIGHT, FLUSH, FULL_HOUSE, QUADS, STR_FLUSH, ROYAL = range(10)
BITS = 22                      # 2,598,960 fits in 22 bits
MASK = (1 << BITS) - 1
DRAWS = [comb(47, 5 - k) for k in range(6)]      # draws for a hold of k cards
LCM = 7669695                                     # 5 * comb(47, 5), shared denominator
MULT = [LCM // d for d in DRAWS]

# Pays per 1 unit bet (max coins, so a royal is 4000 for 5 = 800 per unit).
PAYTABLES = {
    "9/6": [0, 1, 2, 3, 4, 6, 9, 25, 50, 800],
    "8/5": [0, 1, 2, 3, 4, 5, 8, 25, 50, 800],
}


def card_name(c):
    return RANKS[c >> 2] + SUITS[c & 3]


def parse(text):
    """'Js Jh Ad 7c 3s' to a sorted list of card numbers."""
    return sorted(RANKS.index(t[0]) * 4 + SUITS.index(t[1]) for t in text.split())


def _rank_class(ranks):
    """Class of five sorted ranks, returned as (no flush, flush)."""
    counts = sorted((ranks.count(r) for r in set(ranks)), reverse=True)
    u = sorted(set(ranks))
    straight = len(u) == 5 and (u[4] - u[0] == 4 or u == [0, 1, 2, 3, 12])
    if straight:
        return STRAIGHT, (ROYAL if u[0] == 8 else STR_FLUSH)
    if counts[0] == 4:
        return QUADS, None
    if counts[:2] == [3, 2]:
        return FULL_HOUSE, None
    if counts[0] == 3:
        return TRIPS, FLUSH
    if counts[:2] == [2, 2]:
        return TWO_PAIR, None
    if counts[0] == 2:
        pr = [r for r in u if ranks.count(r) == 2][0]
        return (JOB if pr >= 9 else NOTHING), None
    return NOTHING, FLUSH


_RANK_TABLE = {}
for _a in range(13):
    for _b in range(_a, 13):
        for _c in range(_b, 13):
            for _d in range(_c, 13):
                for _e in range(_d, 13):
                    t = (_a, _b, _c, _d, _e)
                    if max(t.count(x) for x in t) <= 4:
                        nf, fl = _rank_class(list(t))
                        _RANK_TABLE[t] = (nf, fl if fl is not None else nf)


def classify(cards):
    cards = sorted(cards)
    nf, fl = _RANK_TABLE[tuple(c >> 2 for c in cards)]
    s = cards[0] & 3
    if all((c & 3) == s for c in cards):
        return fl
    return nf


def build():
    """Returns (subset table, list of distinct deals with weights)."""
    table = {}
    get = table.get
    deals = {}
    for h in combinations(range(52), 5):
        a, b, c, d, e = h
        nf, fl = _RANK_TABLE[(a >> 2, b >> 2, c >> 2, d >> 2, e >> 2)]
        s = a & 3
        cls = fl if (b & 3) == s and (c & 3) == s and (d & 3) == s and (e & 3) == s else nf
        v = 1 << (BITS * cls)
        m = [0]
        for x in h:
            bit = 1 << x
            m += [y | bit for y in m]
        for y in m:
            table[y] = get(y, 0) + v
        sm = [0, 0, 0, 0]
        for x in h:
            sm[x & 3] |= 1 << (x >> 2)
        key = tuple(sorted(sm))
        if key in deals:
            deals[key][1] += 1
        else:
            deals[key] = [h, 1]
    return table, list(deals.values())


def hold_counts(table, hand):
    """For a 5-card hand, a list over the 32 hold masks of the count of each
    final hand class. Bit i of a mask means hand[i] is held."""
    f = []
    for mask in range(32):
        key = 0
        for i in range(5):
            if mask >> i & 1:
                key |= 1 << hand[i]
        f.append(table[key])
    for i in range(5):
        bit = 1 << i
        for mask in range(32):
            if not mask & bit:
                f[mask] -= f[mask | bit]
    out = []
    for mask in range(32):
        v = f[mask]
        out.append([(v >> (BITS * k)) & MASK for k in range(10)])
    return out


def popcount(m):
    return bin(m).count("1")


def ev(counts, mask, pays):
    """Expected return per unit bet for one hold."""
    k = popcount(mask)
    return sum(n * p for n, p in zip(counts, pays)) / DRAWS[k]


def all_evs(table, hand, pays):
    hc = hold_counts(table, hand)
    return [ev(hc[m], m, pays) for m in range(32)]


def hold_text(hand, mask):
    held = [card_name(hand[i]) for i in range(5) if mask >> i & 1]
    return " ".join(held) if held else "Discard all"


def mask_of(hand, held_text):
    held = set(parse(held_text)) if held_text.strip() else set()
    return sum(1 << i for i in range(5) if hand[i] in held)
