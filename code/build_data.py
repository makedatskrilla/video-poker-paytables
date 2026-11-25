"""Rebuilds every CSV file in ../data. Run from the repo root:
python code/build_data.py
Takes a few minutes and about 500 MB of memory. Pure Python 3."""
import csv, os, sys, time
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vpcalc as v
from strategy import LINES, line_of

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)
DEALS = 2598960
SCALE = 10 ** 13      # lets the Duel royal of 812.9719437907615 be an exact integer

# Duel tier 0 pays as captured from duel.com/api/v2/video-poker/config
# (ProvablyFair.org repo duel-video-poker, videoPokerConfig.json).
DUEL = ["0", "1", "2", "3", "4", "6", "9", "26", "58", "812.9719437907615"]
TABLES = {
    "9/6": [p * SCALE for p in v.PAYTABLES["9/6"]],
    "8/5": [p * SCALE for p in v.PAYTABLES["8/5"]],
    "Duel tier 0": [int(Fraction(x) * SCALE) for x in DUEL],
}
NAMES = list(TABLES)
PUBLISHED = {
    "9/6": ("99.5439", "Wizard of Odds"),
    "8/5": ("97.2984", "Wizard of Odds"),
    "Duel tier 0": ("99.90", "duel.com game info, ProvablyFair.org"),
}


def pays_text(name):
    if name == "Duel tier 0":
        return DUEL
    return [str(p) for p in v.PAYTABLES[name]]


t0 = time.time()
table, deals = v.build()
print(f"table built: {len(table)} card sets, {len(deals)} distinct deals, {time.time() - t0:.0f}s")

freq = {n: [0] * 10 for n in NAMES}           # weighted final hand counts, denominator DEALS * LCM
total = {n: 0 for n in NAMES}                 # weighted scaled return
simple_total = 0
simple_freq = [0] * 10
line_weight = [0] * 17
line_return = [0] * 17
line_agree = [0] * 17
p96 = TABLES["9/6"]
for hand, w in deals:
    hand = list(hand)
    hc = v.hold_counts(table, hand)
    nums = {}
    for name in NAMES:
        pays = TABLES[name]
        best_m, best_x = 0, -1
        row = []
        for m in range(32):
            x = sum(n * p for n, p in zip(hc[m], pays) if n) * v.MULT[v.popcount(m)]
            row.append(x)
            if x > best_x:
                best_m, best_x = m, x
        nums[name] = row
        total[name] += w * best_x
        k = v.MULT[v.popcount(best_m)]
        fr = freq[name]
        for c in range(10):
            fr[c] += w * k * hc[best_m][c]
    # simple list, 9/6
    fc = v.classify(hand)
    row = nums["9/6"]
    pick, pick_line = None, 99
    for m in range(32):
        ln = line_of(hand, m, fc)
        if ln is None:
            continue
        if ln < pick_line or (ln == pick_line and row[m] > row[pick]):
            pick, pick_line = m, ln
    simple_total += w * row[pick]
    k = v.MULT[v.popcount(pick)]
    for c in range(10):
        simple_freq[c] += w * k * hc[pick][c]
    line_weight[pick_line] += w
    line_return[pick_line] += w * row[pick]
    if row[pick] == max(row):
        line_agree[pick_line] += w
print(f"solved in {time.time() - t0:.0f}s")

DEN = DEALS * v.LCM * SCALE
ret = {n: Fraction(total[n], DEN) for n in NAMES}
simple_ret = Fraction(simple_total, DEN)
for n in NAMES:
    print(n, f"{float(ret[n]) * 100:.6f}%")
print("simple list 9/6", f"{float(simple_ret) * 100:.6f}%")


def pct(x, d=4):
    return f"{float(x) * 100:.{d}f}"


# 1. Paytables
with open(os.path.join(OUT, "paytables.csv"), "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["hand", "pays_9_6", "pays_8_5", "pays_duel_tier_0"])
    for c in range(9, 0, -1):
        wr.writerow([v.HANDS[c], v.PAYTABLES["9/6"][c], v.PAYTABLES["8/5"][c], DUEL[c]])

# 2. Returns
with open(os.path.join(OUT, "paytable-returns.csv"), "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["paytable", "royal_flush", "straight_flush", "four_of_a_kind", "full_house", "flush",
                 "optimal_return_pct", "house_edge_pct", "expected_loss_per_1000_units",
                 "published_return_pct", "published_by"])
    for n in NAMES:
        p = pays_text(n)
        r = ret[n]
        wr.writerow([n, p[9], p[8], p[7], p[6], p[5], pct(r, 6), pct(1 - r, 6),
                     f"{float((1 - r) * 1000):.3f}", PUBLISHED[n][0], PUBLISHED[n][1]])
    # 8/5 pays with the 9/6 strategy. The final hand mix stays the same, so this is exact.
    mix = freq["9/6"]
    cross = Fraction(sum(n * p for n, p in zip(mix, v.PAYTABLES["8/5"])), sum(mix))
    print("8/5 with 9/6 strategy", f"{float(cross) * 100:.6f}%")
    wr.writerow(["8/5 played with the 9/6 strategy", 800, 50, 25, 8, 5, pct(cross, 6), pct(1 - cross, 6),
                 f"{float((1 - cross) * 1000):.3f}", "", ""])
    wr.writerow(["9/6 simple 16 line list", 800, 50, 25, 9, 6, pct(simple_ret, 6), pct(1 - simple_ret, 6),
                 f"{float((1 - simple_ret) * 1000):.3f}", "99.46", "Wizard of Odds"])

# 3. Hand frequencies under optimal play
with open(os.path.join(OUT, "hand-frequencies.csv"), "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["paytable", "hand", "pays", "combinations", "probability", "return_contribution_pct"])
    for n in NAMES:
        p = pays_text(n)
        tot = sum(freq[n])
        for c in range(9, -1, -1):
            pr = Fraction(freq[n][c], tot)
            wr.writerow([n, v.HANDS[c], p[c], freq[n][c], f"{float(pr):.8f}",
                         f"{float(pr * Fraction(p[c])) * 100:.6f}"])
        wr.writerow([n, "Total", "", tot, "1.00000000", pct(ret[n], 6)])

# 4. Hold list for 9/6 with exact usage
with open(os.path.join(OUT, "hold-strategy-9-6.csv"), "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["rank", "hold", "share_of_deals_pct", "average_ev_when_used",
                 "share_where_list_is_optimal_pct"])
    for i, label in enumerate(LINES, start=1):
        lw = line_weight[i]
        wr.writerow([i, label, f"{lw / DEALS * 100:.4f}",
                     f"{line_return[i] / lw / v.LCM / SCALE:.4f}" if lw else "",
                     f"{line_agree[i] / lw * 100:.2f}" if lw else ""])

# 5. Mistakes
MISTAKES = [
    # label, deal, right hold, wrong hold
    ("Keeping a kicker with a high pair", "Js Jh Ad 7c 3s", "Js Jh", "Js Jh Ad"),
    ("Keeping a kicker with a low pair", "6s 6h Ad 9c 2s", "6s 6h", "6s 6h Ad"),
    ("Keeping a kicker with three of a kind", "7s 7h 7d Kc 2s", "7s 7h 7d", "7s 7h 7d Kc"),
    ("Standing on two pair", "4c 4d 9s 9h Kc", "4c 4d 9s 9h", "4c 4d 9s 9h Kc"),
    ("Keeping a pat flush instead of 4 to a royal", "Th Jh Qh Kh 4h", "Th Jh Qh Kh", "Th Jh Qh Kh 4h"),
    ("Keeping a high pair instead of 4 to a royal", "Ks Kh Qh Jh Ah", "Kh Qh Jh Ah", "Ks Kh"),
    ("Breaking a high pair for 4 to a flush", "Qh Qs 3h 7h 9h", "Qh Qs", "Qh 3h 7h 9h"),
    ("Keeping a low pair instead of 4 to a flush", "6h 6s 2h 9h Kh", "6h 2h 9h Kh", "6h 6s"),
    ("Keeping 4 to an outside straight instead of a low pair", "5s 6h 7d 8c 8s", "8c 8s", "5s 6h 7d 8c"),
    ("Keeping 4 to a flush instead of 3 to a royal", "Ts Js Qs 3s 8h", "Ts Js Qs", "Ts Js Qs 3s"),
    ("Keeping only the jack from 4 to an outside straight", "Jh Td 9c 8s 2h", "Jh Td 9c 8s", "Jh"),
    ("Keeping 2 suited high cards instead of 3 to a straight flush", "9h Th Jh 4c 2s", "9h Th Jh", "Th Jh"),
    ("Keeping one high card instead of a suited queen and jack", "Qh Jh 8c 5d 2s", "Qh Jh", "Jh"),
    ("Keeping K Q J instead of unsuited A K Q J", "Ad Ks Qh Jc 7s", "Ad Ks Qh Jc", "Ks Qh Jc"),
    ("Keeping 3 to a flush with a high card", "Ks 7s 3s 9h 2d", "Ks", "Ks 7s 3s"),
    ("Keeping 4 to an inside straight instead of two high cards", "9s Th Qd Kc 3s", "Qd Kc", "9s Th Qd Kc"),
    ("Keeping all three unsuited high cards with an ace", "Ac Kd Qh 9s 3c", "Kd Qh", "Ac Kd Qh"),
    ("Keeping a lone ace instead of an unsuited queen and jack", "Ah Qd Jc 9h 3s", "Qd Jc", "Ah"),
    ("Keeping an unsuited 10 with a jack", "Td Jc 8s 5h 2d", "Jc", "Td Jc"),
    ("Drawing to a low inside straight instead of discarding all", "5s 6h 8d 9c 2s", "", "5s 6h 8d 9c"),
    ("Throwing away a lone high card", "Kc 8d 6h 4s 2c", "Kc", ""),
]
rows = []
for label, deal, right, wrong in MISTAKES:
    hand = v.parse(deal)
    mr, mw = v.mask_of(hand, right), v.mask_of(hand, wrong)
    e96 = v.all_evs(table, hand, v.PAYTABLES["9/6"])
    e85 = v.all_evs(table, hand, v.PAYTABLES["8/5"])
    for e in (e96, e85):
        assert e[mr] >= max(e) - 1e-12, (label, "right hold is not optimal")
        assert e[mw] < e[mr], label
    rows.append([label, deal, right or "Discard all", wrong or "Discard all",
                 f"{e96[mr]:.4f}", f"{e96[mw]:.4f}", f"{(e96[mr] - e96[mw]) * 100:.2f}",
                 f"{e85[mr]:.4f}", f"{e85[mw]:.4f}", f"{(e85[mr] - e85[mw]) * 100:.2f}"])
rows.sort(key=lambda r: -float(r[6]))
with open(os.path.join(OUT, "hold-mistakes.csv"), "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["mistake", "deal", "right_hold", "wrong_hold", "ev_right_9_6", "ev_wrong_9_6",
                 "cost_pct_of_bet_9_6", "ev_right_8_5", "ev_wrong_8_5", "cost_pct_of_bet_8_5"])
    wr.writerows(rows)
print(f"done in {time.time() - t0:.0f}s")
