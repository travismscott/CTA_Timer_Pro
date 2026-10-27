# CTA Timer Pro - follow-every-signal backtest (2026-09-18 to 2026-10-26)

10 shares per signal, entry at the report's limit price, exits at the report's stop-out prices. 27 daily reports.

## Bottom line

- **Net P/L: $-162.28**  (realized $-335.40 on 51 closed lots, unrealized $+173.12 on 14 open lots)
- Signals followed: 65 lots, $65,372 total bought; peak capital in the market $21,239
- Return on peak capital: -0.76%

## Closed trades

- Win rate: **10/51 = 19.6%**; loss rate 80.4%; flat 0
- Average win $+17.96 (+2.04%), average loss $-12.56 (-0.91%)
- Payoff ratio (avg win / avg loss): 1.43
- Profit factor (gross wins / gross losses): 0.35  (wins $179.60, losses $-515.00)
- Expectancy per closed trade: $-6.58
- Average sessions held: wins 5.1, losses 1.2
- Best: XOP 2026-10-08 $+40.80 (+2.1%); worst: QQQ 2026-10-06 $-92.30 (-1.2%)
- Stops that gapped through (filled below the stop): 8 lots, cost $59.10 beyond the stop price
- Stopped out the same day as entry: 20 lots

## Open at the last report

- 14 open lots, 11 in profit, 3 at/below water; unrealized $+173.12
- Win rate if open lots are counted at their current mark: 21/65 = 32.3%

- Equity curve (realized + open marks): peak $+16.34, max drawdown from a peak $332.38

## By signal class

| Class | Closed | Wins | P/L incl. open |
|---|---|---|---|
| CTA Slow | 15 | 3 | $-29.39 |
| CTA Fast | 17 | 5 | $-46.00 |
| Macro | 19 | 2 | $-86.88 |

## By symbol (P/L incl. open)

| Symbol | P/L |
|---|---|
| TLT | $+139.05 |
| PHO | $+39.07 |
| USO | $+25.50 |
| ITB | $+11.41 |
| XLU | $+6.10 |
| SEF | $+1.60 |
| XLF | $-0.50 |
| XLE | $-0.50 |
| EWW | $-0.50 |
| XLB | $-0.80 |
| DBB | $-2.20 |
| DBA | $-2.30 |
| INDA | $-2.50 |
| WOOD | $-2.70 |
| SLV | $-3.10 |
| EWZ | $-5.70 |
| EZU | $-5.80 |
| XOP | $-7.30 |
| XRT | $-9.40 |
| EWJ | $-18.20 |
| IYR | $-20.40 |
| IBB | $-26.90 |
| IYT | $-29.00 |
| SPY | $-67.00 |
| EWY | $-87.90 |
| QQQ | $-92.30 |

## Memo: bought before the start date (not in the totals)

- SEF entered 2026-09-14, stopped out 2026-09-23 at 30.59: +3.2% (entry price unknown here)

## Data notes

- 2026-09-18: SEF (entered 2026-09-14) is in the open table but was never listed as a new trade - bought before the start date, memo only.
- 2026-09-21: TLT 2026-09-18 stop 80.74 -> table 80.98 (synced).
- 2026-09-28: TLT trade cancelled (open was at/above the stop) - no lot.
- 2026-09-29: SEF (entered 2026-09-29) is in the open table but was never listed as a new trade - lot rebuilt, entry price estimated from its stop-out return.
- 2026-09-29: ledger vs table mismatch. In ledger only: none. In report table only: SEF 2026-09-29.
- 2026-10-01: TLT trade cancelled (open was at/above the stop) - no lot.
- 2026-10-05: XOP trade cancelled (open was at/above the stop) - no lot.
- 2026-10-07: IWR trade cancelled (open was at/above the stop) - no lot.
- 2026-10-08: IWM trade cancelled (open was at/above the stop) - no lot.
- 2026-10-15: WOOD 'trade cancelled' ignored per lecture; lot kept (entry price estimated).
- 2026-10-16: WOOD stop-out matched on return only (tracked stop did not equal the report's protective stop 66.27).
- 2026-10-20: stopped out SH 2026-10-20 @ 32.15 (-0.6%) matched no lot.
- 2026-10-22: IWR trade cancelled (open was at/above the stop) - no lot.
- 2026-10-23: ITB stop-out matched on return only (tracked stop did not equal the report's protective stop 89.67).
- LECTURE CHECK 2026-10-20: SH signal (stop 32.15) has no lot in the reports.
- Lecture cross-check ran over 80 signals on 30 lecture days; days without a lecture file are not checked.
