"""The 16 line simple hold list for 9/6 Jacks or Better, as published by
Wizard of Odds, written as code so the calculator can score it exactly.

Look up every way to play the deal, then keep the one highest on the list.
When two holds fall on the same line, the one with the higher exact expected
value is kept. A high card is a jack, queen, king or ace.
"""
LINES = [
    "Four of a kind, straight flush, royal flush",
    "4 to a royal flush",
    "Three of a kind, straight, flush, full house",
    "4 to a straight flush",
    "Two pair",
    "High pair (jacks or better)",
    "3 to a royal flush",
    "4 to a flush",
    "Low pair (twos to tens)",
    "4 to an outside straight",
    "2 suited high cards",
    "3 to a straight flush",
    "2 unsuited high cards (if more than 2, the lowest 2)",
    "Suited 10 with a jack, queen or king",
    "One high card",
    "Discard everything",
]


def _window(ranks):
    """True if distinct ranks fit inside one five-rank straight window."""
    if len(set(ranks)) != len(ranks):
        return False
    if max(ranks) - min(ranks) <= 4:
        return True
    low = [-1 if r == 12 else r for r in ranks]
    return max(low) - min(low) <= 4


def line_of(hand, mask, final_class):
    """Line number (1 to 16) for holding the cards in mask, or None if this
    hold is not on the list. final_class is the class of the full 5 cards."""
    held = [hand[i] for i in range(5) if mask >> i & 1]
    n = len(held)
    ranks = sorted(c >> 2 for c in held)
    suited = n > 0 and len({c & 3 for c in held}) == 1
    counts = sorted((ranks.count(r) for r in set(ranks)), reverse=True)
    if n == 5:
        if final_class >= 7:
            return 1
        if final_class in (4, 5, 6):
            return 3
        return None
    if n == 4:
        if suited and min(ranks) >= 8:
            return 2
        if suited and _window(ranks):
            return 4
        if counts == [2, 2]:
            return 5
        if suited:
            return 8
        if counts == [1, 1, 1, 1] and ranks[3] - ranks[0] == 3 and ranks[3] <= 11:
            return 10
        return None
    if n == 3:
        if counts == [3]:
            return 3
        if suited and min(ranks) >= 8:
            return 7
        if suited and _window(ranks):
            return 12
        return None
    if n == 2:
        if counts == [2]:
            return 6 if ranks[0] >= 9 else 9
        if ranks[0] >= 9:
            if suited:
                return 11
            highs = sorted(c >> 2 for c in hand if c >> 2 >= 9)
            if ranks == highs[:2]:
                return 13
            return None
        if suited and ranks[0] == 8 and 9 <= ranks[1] <= 11:
            return 14
        return None
    if n == 1:
        return 15 if ranks[0] >= 9 else None
    return 16
