# CTA Timer Pro - follow-every-signal backtest (2026-09-18 to 2026-10-16)

10 shares per signal, entry at the report's limit price, exits at the report's stop-out prices. 21 daily reports.

## Bottom line

- **Net P/L: $-112.01**  (realized $-389.80 on 34 closed lots, unrealized $+277.79 on 12 open lots)
- Signals followed: 46 lots, $51,113 total bought; peak capital in the market $21,239
- Return on peak capital: -0.53%

## Closed trades

- Win rate: **3/34 = 8.8%**; loss rate 91.2%; flat 0
- Average win $+2.40 (+0.63%), average loss $-12.81 (-0.83%)
- Payoff ratio (avg win / avg loss): 0.19
- Profit factor (gross wins / gross losses): 0.02  (wins $7.20, losses $-397.00)
- Expectancy per closed trade: $-11.46
- Average sessions held: wins 4.0, losses 1.1
- Best: XLU 2026-10-09 $+3.70 (+0.9%); worst: QQQ 2026-10-06 $-92.30 (-1.2%)
- Stops that gapped through (filled below the stop): 8 lots, cost $59.10 beyond the stop price
- Stopped out the same day as entry: 14 lots

## Open at the last report

- 12 open lots, 10 in profit, 2 at/below water; unrealized $+277.79
- Win rate if open lots are counted at their current mark: 13/46 = 28.3%

- Equity curve (realized + open marks): peak $+16.34, max drawdown from a peak $332.38

## By signal class

| Class | Closed | Wins | P/L incl. open |
|---|---|---|---|
| CTA Fast | 14 | 2 | $+68.78 |
| CTA Slow | 9 | 0 | $-46.43 |
| Macro | 11 | 1 | $-134.37 |

## By symbol (P/L incl. open)

| Symbol | P/L |
|---|---|
| XOP | $+88.13 |
| USO | $+77.05 |
| XLE | $+58.39 |
| TLT | $+21.43 |
| EWW | $+6.68 |
| PHO | $+2.79 |
| SEF | $+1.60 |
| XLU | $+0.22 |
| XLF | $-0.50 |
| DBB | $-2.20 |
| DBA | $-2.30 |
| INDA | $-2.50 |
| WOOD | $-2.70 |
| SLV | $-3.10 |
| EWZ | $-5.70 |
| EZU | $-5.80 |
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
- Lecture cross-check ran over 53 signals on 21 lecture days; days without a lecture file are not checked.
