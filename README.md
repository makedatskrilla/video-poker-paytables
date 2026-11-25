# Jacks or Better 9/6 vs 8/5: video poker paytables and hold strategy

Exact returns for the 9/6 and 8/5 Jacks or Better paytables, the final hand mix under the best play, a ranked hold chart for 9/6 and the cost of 21 common hold mistakes in percent of the bet.

Live page: https://makedatskrilla.github.io/video-poker-paytables/

## Paytables

Pays per 1 unit bet with maximum coins, so a royal flush is 4,000 for 5, or 800 per unit.

| Hand | 9/6 | 8/5 | Duel tier 0 |
| --- | ---: | ---: | ---: |
| Royal flush | 800 | 800 | 812.97 |
| Straight flush | 50 | 50 | 58 |
| Four of a kind | 25 | 25 | 26 |
| Full house | 9 | 8 | 9 |
| Flush | 6 | 5 | 6 |
| Straight | 4 | 4 | 4 |
| Three of a kind | 3 | 3 | 3 |
| Two pair | 2 | 2 | 2 |
| Jacks or better | 1 | 1 | 1 |

The Duel column is the paytable the casino publishes for its own Jacks or Better game at bets up to $1,182.85, from the duel.com game info and the config file in the ProvablyFair.org audit repo. It is included as a data point only.

## Results

| Paytable | Return with best play | Loss per 1,000 units |
| --- | ---: | ---: |
| 9/6 | 99.5439% | 4.56 |
| 8/5 | 97.2984% | 27.02 |
| Duel tier 0 | 99.9000% | 1.00 |
| 8/5 played with the 9/6 strategy | 97.2912% | 27.09 |
| 9/6 played with the simple 16 line list | 99.4593% | 5.41 |

## Files

| File | What it holds |
| --- | --- |
| `data/paytables.csv` | The three paytables, per 1 unit bet. |
| `data/paytable-returns.csv` | Exact return, house edge and loss per 1,000 units for each paytable and strategy, next to the published figure. |
| `data/hand-frequencies.csv` | Combination count, probability and return contribution of every final hand under the best play, for all three paytables. |
| `data/hold-strategy-9-6.csv` | The 16 line hold list for 9/6 with how often each line is used, its average value and how often it is the exact best hold. |
| `data/hold-mistakes.csv` | 21 common hold mistakes with an example deal, the right and wrong hold, both expected values and the cost in percent of the bet on 9/6 and 8/5. |
| `code/vpcalc.py` | The calculator. Exact over all 2,598,960 deals and 32 holds, no simulation. |
| `code/strategy.py` | The 16 line hold list as code. |
| `code/build_data.py` | Rebuilds all five CSV files. |

Expected values are in units of the bet. Combination counts use the shared denominator 19,933,230,517,200, which is 2,598,960 deals times 5 times C(47,5), the same convention Wizard of Odds uses.

## Rebuild

```
python code/build_data.py
```

Needs Python 3 and nothing else. Takes about a minute and roughly 500 MB of memory.

## Checks

- Returns match Wizard of Odds to every published digit: 0.99543904 for 9/6 and 0.97298434 for 8/5. https://wizardofodds.com/games/video-poker/tables/jacks-or-better/
- Combination counts match the Wizard of Odds tables exactly for every hand on both paytables.
- The simple 16 line list scores 99.4593%, against the 99.46% Wizard of Odds states for it. https://wizardofodds.com/games/video-poker/strategy/jacks-or-better/9-6/simple/
- The Duel tier 0 table comes out at 99.9000%, against the 99.90% the casino states for optimal play.

## Related

- Kaggle dataset: https://www.kaggle.com/datasets/makedatskrilla/video-poker-paytables-and-hold-strategy
- Kaggle notebook: https://www.kaggle.com/code/makedatskrilla/video-poker-9-6-vs-8-5-what-the-paytable-costs
- House Edge Index, sourced house edge and RTP figures: https://makedatskrilla.github.io/house-edge-index/
- Blackjack Strategy Cost, computed blackjack charts and mistake costs: https://makedatskrilla.github.io/blackjack-strategy-cost/

## License

Data, code and text: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See `LICENSE`.

Long-run expected values only. Not affiliated with any casino and not advice to play.
