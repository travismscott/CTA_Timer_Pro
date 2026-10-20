#!/usr/bin/env python3
"""Backtest: follow every CTA Timer Pro signal from the first report, 10 shares each.

Reads the daily PDF reports (data/inbox/CTA_Report_*.pdf), rebuilds every trade lot, and writes
results/trades.csv, results/daily_equity.csv and results/summary.md.

How the reports are scored (checked against the report's own numbers):
  * A signal dated D fills at D's open. The report scores it from the LIMIT price, not the real fill.
  * "Stopped out ... at $X. Return: r%" means exit at X, return = X / limit - 1.
  * "TRADE CANCELLED" means the open was at/above the stop, so the lot never existed.
  * Every signal is its own 10-share lot, even when the same symbol is already held.
  * Open lots at the last report are marked at the report's GAIN / LOSS % (vs the limit price).

Usage: backtest.py [--start 2026-09-18] [--inbox data/inbox] [--out results]
"""
import argparse
import csv
import glob
import os
import re
import subprocess
from collections import defaultdict
from datetime import date, datetime

SHARES = 10

# Known report errors, confirmed in Steve's lectures. A cancelled notice that the lecture says to ignore
# becomes a real lot (entry price is unknown, so it is estimated from the later stop-out's return).
IGNORE_CANCEL = {
    ("WOOD", date(2026, 10, 15)): "Lecture 10/16: 'The WOOD trade is still open. Disregard the trade cancelled.'",
}

# The 9/21 report's header says "market data as of 9/18" because of a Japanese holiday (explained in the
# 9/22 lecture), so the date comes from the filename for that file.
DATE_FROM_FILENAME = {"CTA_Report_20260921_2109": date(2026, 9, 21)}

# lecture_20261018.rtf was uploaded under the wrong date; its own header reads 10/8/2026.
LECTURE_DATE_OVERRIDE = {"lecture_20261018": date(2026, 10, 8)}

SYM = r"[A-Z][A-Z.]{0,5}"
NUM = r"[\d,]+\.?\d*"


def money(s):
    return float(s.replace(",", ""))


def mdy(s):
    return datetime.strptime(s, "%m/%d/%Y").date()


def pdf_text(path):
    return subprocess.run(["pdftotext", "-raw", path, "-"], capture_output=True, text=True, check=True).stdout


def report_date(name, text):
    if name in DATE_FROM_FILENAME:
        return DATE_FROM_FILENAME[name]
    m = (re.search(r"Market data (?:through|as of) ([A-Z][a-z]+ \d{1,2}, \d{4})", text)
         or re.search(r"Generated ([A-Z][a-z]+ \d{1,2}, \d{4})", text))
    return datetime.strptime(m.group(1), "%B %d, %Y").date()


def action_section(text):
    body = text.split("SUBSCRIBER DAILY ACTION REPORT", 1)[1]
    body = re.split(r"SUBSCRIBER EXECUTION BRIEF|CTA RESEARCH BRIEF|CTA Data Warnings", body)[0]
    keep = [l.strip() for l in body.splitlines()
            if l.strip() and not l.startswith(("Market data", "© Copyright", "Today’s instruction set"))
            and not ("Generated " in l and " ET" in l)]
    return keep


def parse_report(path):
    name = os.path.basename(path)[:-4]
    text = pdf_text(path)
    rep = {"name": name, "date": report_date(name, text), "updates": [], "stops": [], "cancels": [],
           "new": [], "open": [], "unparsed": []}
    lines = action_section(text)
    sec = None
    i = 0
    while i < len(lines):
        l = lines[i]
        if l.startswith("1. STOP UPDATES"):
            sec = 1
        elif l.startswith("2. YESTERDAY"):
            sec = 2
        elif l.startswith("3. OPEN POSITIONS"):
            sec = 3
        elif sec == 1:
            m = re.match(rf"^({SYM}) UPDATE STOP$", l)
            if m:
                r = re.match(rf"Raise stop: \$({NUM}) → \$({NUM})", lines[i + 1])
                rep["updates"].append((m.group(1), money(r.group(1)), money(r.group(2))))
                i += 2
            else:
                m = re.match(rf"^({SYM}) REQUIRED ACTION$", l)
                if m:
                    r = re.match(rf"Stopped out (\d\d/\d\d/\d{{4}}) at \$({NUM})\. Return: ([+-]?[\d.]+)%", lines[i + 1])
                    p = re.match(rf"Protective stop: \$({NUM})", lines[i + 2])
                    if not r:
                        rep["unparsed"].append(" / ".join(lines[i:i + 3]))
                    else:
                        rep["stops"].append({"sym": m.group(1), "date": mdy(r.group(1)), "exit": money(r.group(2)),
                                             "ret": float(r.group(3)), "stop": money(p.group(1)) if p else None})
                    i += 2
                else:
                    m = re.match(rf"^({SYM}) TRADE CANCELLED$", l)
                    if m:
                        rep["cancels"].append(m.group(1))
                        i += 1
                    elif re.match(r"^(Do not enter|Protective stop|Trail |Breakeven|\$[\d.]+\.?$|No stop changes)", l):
                        pass
                    else:
                        rep["unparsed"].append(l)
        elif sec == 2:
            m = re.match(rf"^({SYM}): (.+?)\. Buy Limit at Open with Initial Stop at \$({NUM})\.$", l)
            if m:
                r = re.match(rf"LIMIT \$({NUM}) HORIZON (.+?) SIGNAL (\d\d/\d\d/\d{{4}})", lines[i + 1])
                rep["new"].append({"sym": m.group(1), "cls": m.group(2), "stop": money(m.group(3)),
                                   "limit": money(r.group(1)), "horizon": r.group(2), "date": mdy(r.group(3))})
                i += 1
            elif not l.startswith(("No new trades", "LIMIT ")):
                rep["unparsed"].append(l)
        elif sec == 3:
            m = re.match(rf"^(\d\d/\d\d/\d{{4}}) ({SYM}) ([+-]?[\d.]+)% \$({NUM})$", l)
            if m:
                rep["open"].append({"date": mdy(m.group(1)), "sym": m.group(2), "gain": float(m.group(3)),
                                    "stop": money(m.group(4))})
            elif not l.startswith(("ENTRY DATE", "No filled open", "Do not enter")):
                rep["unparsed"].append(l)
        i += 1
    return rep


def simulate(reports, start):
    lots, notes = [], []
    marks = {}  # id(lot) -> list of (date, gain%)
    daily = []
    seen_new = set()
    for rep in reports:
        d = rep["date"]
        for n in rep["new"]:
            key = (n["sym"], n["date"], n["limit"], n["stop"])
            if key in seen_new:
                continue
            seen_new.add(key)
            lots.append({"sym": n["sym"], "cls": n["cls"], "entry": n["date"], "limit": n["limit"],
                         "init_stop": n["stop"], "stop": n["stop"], "status": "open", "exit": None,
                         "exit_date": None, "est": False, "pre_start": n["date"] < start, "marks": [], "note": ""})
        for r in rep["open"]:
            if not any(l["sym"] == r["sym"] and l["entry"] == r["date"] for l in lots):
                lots.append({"sym": r["sym"], "cls": "?", "entry": r["date"], "limit": None, "init_stop": r["stop"],
                             "stop": r["stop"], "status": "open", "exit": None, "exit_date": None, "est": True,
                             "pre_start": r["date"] < start, "marks": [], "note": "rebuilt from open-positions table"})
                notes.append(f"{d}: {r['sym']} (entered {r['date']}) is in the open table but was never listed as a new trade"
                             f"{' - bought before the start date, memo only' if r['date'] < start else ' - lot rebuilt, entry price estimated from its stop-out return'}.")
        for sym in rep["cancels"]:
            if (sym, d) in IGNORE_CANCEL:
                lots.append({"sym": sym, "cls": "CTA Slow", "entry": d, "limit": None, "init_stop": None, "stop": None,
                             "status": "open", "exit": None, "exit_date": None, "est": True, "pre_start": False,
                             "marks": [], "note": IGNORE_CANCEL[(sym, d)]})
                notes.append(f"{d}: {sym} 'trade cancelled' ignored per lecture; lot kept (entry price estimated).")
            else:
                notes.append(f"{d}: {sym} trade cancelled (open was at/above the stop) - no lot.")
        used = set()
        for sym, old, new in rep["updates"]:
            cand = [l for l in lots if l["sym"] == sym and l["status"] == "open" and id(l) not in used
                    and l["stop"] is not None and abs(l["stop"] - old) < 0.006]
            if cand:
                cand[0]["stop"] = new
                used.add(id(cand[0]))
            elif not any(l["sym"] == sym and l["status"] == "open" and l["stop"] is not None
                         and abs(l["stop"] - new) < 0.006 for l in lots):
                notes.append(f"{d}: stop update {sym} {old}->{new} matched no open lot.")
        for s in rep["stops"]:
            cand = [l for l in lots if l["sym"] == s["sym"] and l["status"] == "open" and l["entry"] <= s["date"]]

            def fits(l):
                if l["limit"] is None:
                    return True
                return abs((s["exit"] / l["limit"] - 1) * 100 - s["ret"]) <= 0.11

            good = [l for l in cand if fits(l)]
            exact = [l for l in good if l["stop"] is not None and s["stop"] is not None and abs(l["stop"] - s["stop"]) < 0.006]
            pick = (exact or good or [])
            if not pick:
                notes.append(f"{d}: stopped out {s['sym']} {s['date']} @ {s['exit']} ({s['ret']}%) matched no lot.")
                continue
            if not exact:
                notes.append(f"{d}: {s['sym']} stop-out matched on return only (tracked stop did not equal the "
                             f"report's protective stop {s['stop']}).")
            l = sorted(pick, key=lambda x: x["entry"])[0]
            l.update(status="closed", exit=s["exit"], exit_date=s["date"], gap=s["stop"] is not None and s["exit"] < s["stop"] - 0.005)
            if l["limit"] is None:
                l["limit"] = round(s["exit"] / (1 + s["ret"] / 100), 2)
                if l["init_stop"] is None:
                    l["init_stop"] = s["stop"]
        # check ledger against the report's own open-positions table
        want = sorted((l["entry"], l["sym"]) for l in lots if l["status"] == "open" and l["entry"] <= d
                      and not (l["est"] and l["entry"] == d))
        got = sorted((r["date"], r["sym"]) for r in rep["open"])
        if want != got:
            miss = [x for x in want if x not in got]
            extra = [x for x in got if x not in want]
            fmt = lambda xs: ", ".join(f"{sym} {dt.isoformat()}" for dt, sym in xs) or "none"
            notes.append(f"{d}: ledger vs table mismatch. In ledger only: {fmt(miss)}. In report table only: {fmt(extra)}.")
        for r in rep["open"]:
            cand = [l for l in lots if l["sym"] == r["sym"] and l["entry"] == r["date"] and l["status"] == "open"]
            if cand:
                l = min(cand, key=lambda x: abs((x["stop"] or 0) - r["stop"]))
                if l["stop"] is None or abs(l["stop"] - r["stop"]) > 0.006:
                    notes.append(f"{d}: {r['sym']} {r['date']} stop {l['stop']} -> table {r['stop']} (synced).")
                    l["stop"] = r["stop"]
                l["marks"].append((d, r["gain"]))
                l["last_gain"] = r["gain"]
        # daily mark-to-market equity
        realized = sum(SHARES * (l["exit"] - l["limit"]) for l in lots
                       if l["status"] == "closed" and l["exit_date"] <= d and not l["pre_start"])
        unreal = 0.0
        for r in rep["open"]:
            lot = next((l for l in lots if l["sym"] == r["sym"] and l["entry"] == r["date"] and not l["pre_start"]
                        and (l["status"] == "open" or l["exit_date"] > d)), None)
            if lot and lot["limit"]:
                unreal += SHARES * lot["limit"] * r["gain"] / 100
        daily.append({"date": d, "realized": realized, "unrealized": unreal, "equity": realized + unreal,
                      "open_lots": len([r for r in rep["open"]])})
    return lots, daily, notes


def lecture_signals(inbox):
    """{(date, symbol): (initial stop, class text)} from the lecture RTFs (needs pandoc; skipped if absent)."""
    out, dates = {}, set()
    for path in sorted(glob.glob(os.path.join(inbox, "lecture_*.rtf"))):
        m = re.search(r"lecture_(\d{4})(\d\d)(\d\d)", path)
        d = LECTURE_DATE_OVERRIDE.get(os.path.basename(path)[:-4],
                                      date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
        dates.add(d)
        try:
            txt = subprocess.run(["pandoc", "-f", "rtf", "-t", "plain", "--wrap=none", path],
                                 capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            return {}, set()
        for mm in re.finditer(rf"^({SYM}): (.*?)Initial Stops? at \$?({NUM})", txt, re.M):
            out[(d, mm.group(1))] = (money(mm.group(3)), mm.group(2))
    return out, dates


def pnl(l):
    if l["status"] == "closed":
        return SHARES * (l["exit"] - l["limit"])
    return SHARES * l["limit"] * l.get("last_gain", 0.0) / 100


def sessions_between(reports, a, b):
    ds = [r["date"] for r in reports]
    return sum(1 for x in ds if a < x <= b) or 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-09-18")
    ap.add_argument("--inbox", default="data/inbox")
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    start = date.fromisoformat(a.start)
    reports = sorted((parse_report(p) for p in glob.glob(os.path.join(a.inbox, "CTA_Report_*.pdf"))),
                     key=lambda r: r["date"])
    reports = [r for r in reports if r["date"] >= start]
    lots, daily, notes = simulate(reports, start)
    for r in reports:
        for u in r["unparsed"]:
            notes.append(f"{r['date']}: UNPARSED line: {u}")

    sig, lec_dates = lecture_signals(a.inbox)
    if sig:
        cancelled = {(r["date"], c) for r in reports for c in r["cancels"]}
        for (d, sym), (stop, cls) in sorted(sig.items()):
            if not (reports[0]["date"] <= d <= reports[-1]["date"]):
                continue
            hit = [l for l in lots if l["sym"] == sym and l["entry"] == d]
            if not hit and (d, sym) not in cancelled:
                notes.append(f"LECTURE CHECK {d}: {sym} signal (stop {stop}) has no lot in the reports.")
            for l in hit:
                if l["init_stop"] is not None and abs(l["init_stop"] - stop) > 0.006:
                    notes.append(f"LECTURE CHECK {d}: {sym} lecture stop {stop} != report stop {l['init_stop']}.")
                if l["cls"] == "?":
                    l["cls"] = "Macro" if "Macro" in cls else ("CTA Fast & Slow" if "Fast & Slow" in cls else
                                                               ("CTA Slow" if "Slow" in cls else "CTA Fast"))
        for l in lots:
            if (not l["pre_start"] and l["entry"] in lec_dates and (l["entry"], l["sym"]) not in sig):
                notes.append(f"LECTURE CHECK {l['entry']}: {l['sym']} lot has no matching lecture signal.")
        notes.append(f"Lecture cross-check ran over {len(sig)} signals on {len(lec_dates)} lecture days; "
                     f"days without a lecture file are not checked.")

    trades = [l for l in lots if not l["pre_start"]]
    memo = [l for l in lots if l["pre_start"]]
    closed = [l for l in trades if l["status"] == "closed"]
    opened = [l for l in trades if l["status"] == "open"]
    last = reports[-1]["date"]
    os.makedirs(a.out, exist_ok=True)

    rows = []
    for l in sorted(trades, key=lambda x: (x["entry"], x["sym"])):
        held = sessions_between(reports, l["entry"], l["exit_date"] or last) if True else 0
        rows.append({"symbol": l["sym"], "class": l["cls"], "entry_date": l["entry"], "entry_price(limit)": l["limit"],
                     "initial_stop": l["init_stop"], "status": l["status"], "exit_date": l["exit_date"] or "",
                     "exit_or_mark_price": l["exit"] if l["status"] == "closed" else round(l["limit"] * (1 + l.get("last_gain", 0) / 100), 2),
                     "return_pct": round((l["exit"] / l["limit"] - 1) * 100, 2) if l["status"] == "closed" else l.get("last_gain"),
                     "pnl_usd": round(pnl(l), 2), "sessions_held": held, "gap_through_stop": l.get("gap", ""),
                     "entry_estimated": l["est"]})
    with open(os.path.join(a.out, "trades.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(a.out, "daily_equity.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "realized", "unrealized", "equity", "open_lots"])
        w.writeheader()
        for d in daily:
            w.writerow({k: (round(v, 2) if isinstance(v, float) else v) for k, v in d.items()})

    import json
    seen_lot = defaultdict(int)
    for r in rows:
        k = f"{r['symbol']}_{r['entry_date'].isoformat()}"
        seen_lot[k] += 1
        r["lot"] = k if seen_lot[k] == 1 else f"{k}_{seen_lot[k]}"
    jt = [{"lot": r["lot"], "symbol": r["symbol"], "class": r["class"], "entry_date": r["entry_date"].isoformat(),
           "entry_price": r["entry_price(limit)"], "initial_stop": r["initial_stop"], "status": r["status"],
           "exit_date": r["exit_date"].isoformat() if r["exit_date"] else None,
           "exit_or_mark_price": r["exit_or_mark_price"], "return_pct": r["return_pct"], "pnl_usd": r["pnl_usd"],
           "sessions_held": r["sessions_held"], "gap_through_stop": bool(r["gap_through_stop"]),
           "entry_estimated": r["entry_estimated"]} for r in rows]
    je = [{"date": d["date"].isoformat(), "realized": round(d["realized"], 2), "unrealized": round(d["unrealized"], 2),
           "equity": round(d["equity"], 2), "open_lots": d["open_lots"]} for d in daily]
    memo_notes = [{"kind": "before start", "note": f"{l['sym']} bought {l['entry'].isoformat()}, before the start date, "
                   f"stopped out {l['exit_date'].isoformat()} at {l['exit']}; not in the totals."}
                  for l in memo if l["status"] == "closed"]
    jn = memo_notes + [{"kind": "data", "note": n} for n in notes]
    for name, obj in (("trades.json", jt), ("equity.json", je), ("notes.json", jn)):
        with open(os.path.join(a.out, name), "w") as f:
            json.dump(obj, f, indent=1)

    wins = [l for l in closed if pnl(l) > 0.004]
    losses = [l for l in closed if pnl(l) < -0.004]
    flats = [l for l in closed if abs(pnl(l)) <= 0.004]
    gw = sum(pnl(l) for l in wins)
    gl = -sum(pnl(l) for l in losses)
    realized = sum(pnl(l) for l in closed)
    unreal = sum(pnl(l) for l in opened)
    ret = lambda l: (l["exit"] / l["limit"] - 1) * 100
    held = lambda l: sessions_between(reports, l["entry"], l["exit_date"])
    pk, mdd, peak_d = 0.0, 0.0, None
    for d in daily:
        if d["equity"] > pk:
            pk = d["equity"]
        if pk - d["equity"] > mdd:
            mdd, peak_d = pk - d["equity"], d["date"]
    avg = lambda xs: sum(xs) / len(xs) if xs else 0.0
    by_sym, by_cls = defaultdict(float), defaultdict(lambda: [0, 0, 0.0])
    for l in trades:
        by_sym[l["sym"]] += pnl(l)
        c = by_cls[l["cls"]]
        c[2] += pnl(l)
        if l["status"] == "closed":
            c[0] += 1
            c[1] += 1 if pnl(l) > 0.004 else 0
    deployed = sum(SHARES * l["limit"] for l in trades)
    peak_cap = max((sum(SHARES * l["limit"] for l in trades if l["entry"] <= d["date"] and (l["status"] == "open" or l["exit_date"] >= d["date"]))
                    for d in daily), default=0)

    L = []
    P = L.append
    P(f"# CTA Timer Pro - follow-every-signal backtest ({reports[0]['date']} to {last})\n")
    P(f"{SHARES} shares per signal, entry at the report's limit price, exits at the report's stop-out prices. "
      f"{len(reports)} daily reports.\n")
    P("## Bottom line\n")
    P(f"- **Net P/L: ${realized + unreal:+,.2f}**  (realized ${realized:+,.2f} on {len(closed)} closed lots, "
      f"unrealized ${unreal:+,.2f} on {len(opened)} open lots)")
    P(f"- Signals followed: {len(trades)} lots, ${deployed:,.0f} total bought; peak capital in the market ${peak_cap:,.0f}")
    P(f"- Return on peak capital: {(realized + unreal) / peak_cap * 100:+.2f}%\n")
    P("## Closed trades\n")
    P(f"- Win rate: **{len(wins)}/{len(closed)} = {len(wins) / len(closed) * 100:.1f}%**; loss rate {len(losses) / len(closed) * 100:.1f}%"
      f"; flat {len(flats)}")
    P(f"- Average win ${avg([pnl(l) for l in wins]):+.2f} ({avg([ret(l) for l in wins]):+.2f}%), "
      f"average loss ${avg([pnl(l) for l in losses]):+.2f} ({avg([ret(l) for l in losses]):+.2f}%)")
    P(f"- Payoff ratio (avg win / avg loss): {avg([pnl(l) for l in wins]) / -avg([pnl(l) for l in losses]):.2f}")
    P(f"- Profit factor (gross wins / gross losses): {gw / gl:.2f}  (wins ${gw:,.2f}, losses ${-gl:,.2f})")
    P(f"- Expectancy per closed trade: ${realized / len(closed):+.2f}")
    P(f"- Average sessions held: wins {avg([held(l) for l in wins]):.1f}, losses {avg([held(l) for l in losses]):.1f}")
    best, worst = max(closed, key=pnl), min(closed, key=pnl)
    P(f"- Best: {best['sym']} {best['entry']} ${pnl(best):+.2f} ({ret(best):+.1f}%); "
      f"worst: {worst['sym']} {worst['entry']} ${pnl(worst):+.2f} ({ret(worst):+.1f}%)")
    gaps = [l for l in closed if l.get("gap")]
    P(f"- Stops that gapped through (filled below the stop): {len(gaps)} lots, "
      f"cost ${sum(SHARES * (l['stop'] - l['exit']) for l in gaps):.2f} beyond the stop price")
    P(f"- Stopped out the same day as entry: {sum(1 for l in closed if l['entry'] == l['exit_date'])} lots\n")
    P("## Open at the last report\n")
    ow = [l for l in opened if l.get('last_gain', 0) > 0]
    P(f"- {len(opened)} open lots, {len(ow)} in profit, {len(opened) - len(ow)} at/below water; unrealized ${unreal:+,.2f}")
    P(f"- Win rate if open lots are counted at their current mark: "
      f"{(len(wins) + len(ow))}/{len(closed) + len(opened)} = {(len(wins) + len(ow)) / (len(closed) + len(opened)) * 100:.1f}%\n")
    P(f"- Equity curve (realized + open marks): peak ${max(d['equity'] for d in daily):+,.2f}, "
      f"max drawdown from a peak ${mdd:,.2f}\n")
    P("## By signal class\n")
    P("| Class | Closed | Wins | P/L incl. open |\n|---|---|---|---|")
    for c, (n, w, p) in sorted(by_cls.items(), key=lambda x: -x[1][2]):
        P(f"| {c} | {n} | {w} | ${p:+,.2f} |")
    P("\n## By symbol (P/L incl. open)\n")
    P("| Symbol | P/L |\n|---|---|")
    for s, p in sorted(by_sym.items(), key=lambda x: -x[1]):
        P(f"| {s} | ${p:+,.2f} |")
    if memo:
        P("\n## Memo: bought before the start date (not in the totals)\n")
        for l in memo:
            if l["status"] == "closed":
                P(f"- {l['sym']} entered {l['entry']}, stopped out {l['exit_date']} at {l['exit']}: "
                  f"{(l['exit'] / l['limit'] - 1) * 100:+.1f}% (entry price unknown here)" if l["limit"] else
                  f"- {l['sym']} entered {l['entry']}, stopped out {l['exit_date']} at {l['exit']}")
    P("\n## Data notes\n")
    for n in notes:
        P(f"- {n}")
    with open(os.path.join(a.out, "summary.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
