# CTA Timer Pro - follow-every-signal backtest (2026-09-18 to 2026-10-19)

10 shares per signal, entry at the report's limit price, exits at the report's stop-out prices. 22 daily reports.

## Bottom line

- **Net P/L: $-192.56**  (realized $-393.80 on 35 closed lots, unrealized $+201.24 on 14 open lots)
- Signals followed: 49 lots, $53,563 total bought; peak capital in the market $21,239
- Return on peak capital: -0.91%

## Closed trades

- Win rate: **3/35 = 8.6%**; loss rate 91.4%; flat 0
- Average win $+2.40 (+0.63%), average loss $-12.53 (-0.81%)
- Payoff ratio (avg win / avg loss): 0.19
- Profit factor (gross wins / gross losses): 0.02  (wins $7.20, losses $-401.00)
- Expectancy per closed trade: $-11.25
- Average sessions held: wins 4.0, losses 1.1
- Best: XLU 2026-10-09 $+3.70 (+0.9%); worst: QQQ 2026-10-06 $-92.30 (-1.2%)
- Stops that gapped through (filled below the stop): 8 lots, cost $59.10 beyond the stop price
- Stopped out the same day as entry: 15 lots

## Open at the last report

- 14 open lots, 7 in profit, 7 at/below water; unrealized $+201.24
- Win rate if open lots are counted at their current mark: 10/49 = 20.4%

- Equity curve (realized + open marks): peak $+16.34, max drawdown from a peak $332.38

## By signal class

| Class | Closed | Wins | P/L incl. open |
|---|---|---|---|
| CTA Fast | 14 | 2 | $+45.55 |
| CTA Slow | 10 | 0 | $-50.16 |
| Macro | 11 | 1 | $-187.95 |

## By symbol (P/L incl. open)

| Symbol | P/L |
|---|---|
| XOP | $+68.53 |
| USO | $+67.80 |
| XLE | $+48.56 |
| EWW | $+11.14 |
| SEF | $+1.60 |
| XLF | $-0.50 |
| PHO | $-1.40 |
| DBB | $-2.20 |
| DBA | $-2.30 |
| INDA | $-2.50 |
| WOOD | $-2.70 |
| SLV | $-3.10 |
| IYR | $-4.00 |
| EWZ | $-5.70 |
| EZU | $-5.80 |
| TLT | $-7.85 |
| XLU | $-8.64 |
| XRT | $-9.40 |
| ITB | $-12.80 |
| EWJ | $-18.20 |
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
- Lecture cross-check ran over 56 signals on 22 lecture days; days without a lecture file are not checked.
