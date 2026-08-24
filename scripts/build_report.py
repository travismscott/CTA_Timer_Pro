#!/usr/bin/env python3
"""
Render the "CTA Timer Pro Analysis" persisted artifact (self-contained HTML)
from a JSON data structure.

Usage:
    python3 build_report.py <input.json> <output.html>
    python3 build_report.py --sample > sample_input.json   # print an example input to fill in

Keeping the rendering in one script means every run of the cta-timer-pro
skill produces a visually consistent artifact instead of the model
re-inventing HTML/CSS each time. If the layout needs to change, edit this
script rather than hand-writing HTML in conversation.
"""

import argparse
import html
import json
import sys

SAMPLE_INPUT = {
    "generated_at": "17 Aug 2026, 7:45pm AEST",
    "report_date": "8/17/2026",
    "book_as_of": "2026-08-14 (published in the 8/17 lecture)",
    "summary": [
        "Nothing forced today. Steve is watching the VIX grind lower as a setup for a long-vol or "
        "short-index trade, and flags persistent seller resistance in TLT as a possible multi-month "
        "hedge idea rather than an immediate entry.",
        "A backtest note: layering entries over ~10 days only helped leveraged traders; for an "
        "unleveraged buy it made no measurable difference."
    ],
    "book_positions": [
        {"symbol": "GDX", "entry_date": "2026-07-31", "return_pct": 20.15, "stop": 88.54},
        {"symbol": "URA", "entry_date": "2026-08-05", "return_pct": 3.96, "stop": 44.48},
        {"symbol": "SLV", "entry_date": "2026-08-10", "return_pct": 1.18, "stop": 57.82},
        {"symbol": "DBC", "entry_date": "2026-08-12", "return_pct": 0.13, "stop": 29.44},
        {"symbol": "EEM", "entry_date": "2026-08-13", "return_pct": 0.29, "stop": 66.13},
        {"symbol": "XLK", "entry_date": "2026-08-14", "return_pct": -0.59, "stop": 188.11}
    ],
    "comparison": [
        {"symbol": "DBC", "in_book": True, "held": True, "qty": 40, "avg_price": 29.77,
         "market_price": 30.00, "book_stop": 29.44, "live_stop": None,
         "live_stop_status": "missing", "note": "Prior GTC stop at $29.44 shows REPLACED; no successor order found."},
        {"symbol": "SLV", "in_book": True, "held": True, "qty": 20, "avg_price": 57.85,
         "market_price": 59.21, "book_stop": 57.82, "live_stop": 57.47,
         "live_stop_status": "stale", "note": "Live stop is last week's level."},
        {"symbol": "URA", "in_book": True, "held": True, "qty": 20, "avg_price": 42.81,
         "market_price": 45.28, "book_stop": 44.48, "live_stop": 44.27,
         "live_stop_status": "stale", "note": "Live stop is last week's level."},
        {"symbol": "XLK", "in_book": True, "held": True, "qty": 10, "avg_price": 191.22,
         "market_price": 191.25, "book_stop": 188.11, "live_stop": None,
         "live_stop_status": "missing", "note": "Prior GTC stop at $184.77 shows REPLACED; no successor order found."},
        {"symbol": "SMH", "in_book": False, "held": True, "qty": 5, "avg_price": 587.97,
         "market_price": 594.25, "book_stop": None, "live_stop": None,
         "live_stop_status": "n/a", "note": "8/14 buy signal appears cancelled in Steve's report; no longer in the book."},
        {"symbol": "GDX", "in_book": True, "held": False, "qty": None, "avg_price": None,
         "market_price": None, "book_stop": 88.54, "live_stop": None,
         "live_stop_status": "n/a", "note": "In Steve's book since 7/31 (+20.15%), not currently held."},
        {"symbol": "EEM", "in_book": True, "held": False, "qty": None, "avg_price": None,
         "market_price": None, "book_stop": 66.13, "live_stop": None,
         "live_stop_status": "n/a", "note": "In Steve's book since 8/13 (+0.29%), not currently held."}
    ],
    "new_signals": [
        {"symbol": "QQQ", "type": "High conviction", "stop": 716.14, "queued": True},
        {"symbol": "XOP", "type": "High conviction", "stop": 171.13, "queued": True},
        {"symbol": "EWY", "type": "High conviction", "stop": 168.02, "queued": True},
        {"symbol": "USO", "type": "High conviction", "stop": 118.39, "queued": False},
        {"symbol": "CORN", "type": "CTA Slow", "stop": 18.05, "queued": False}
    ],
    "action_items": [
        "SLV: live stop is $57.47, report's current level is $57.82.",
        "URA: live stop is $44.27, report's current level is $44.48.",
        "DBC: no live protective stop found; report's current level is $29.44.",
        "XLK: no live protective stop found; report's current level is $188.11.",
        "SMH: held but no longer in Steve's book and has no live stop — worth a decision either way.",
        "GDX and EEM are in Steve's book but not held.",
        "USO and CORN are today's new signals without a queued entry order yet."
    ],
    "anomalies": [
        "The 8/17 report's cancellation line is labeled \"XLK\" but carries SMH's stop price ($560.38) "
        "— treated as a labeling mix-up in Steve's report rather than a fact about XLK."
    ]
}

CSS = """
:root {
  --bg: #0b0f14;
  --panel: #121820;
  --panel-2: #171f29;
  --border: #232c38;
  --text: #e8edf3;
  --muted: #93a1b3;
  --accent: #5aa9ff;
  --good: #3ddc84;
  --warn: #f5b942;
  --bad: #ff6b6b;
  --neutral: #93a1b3;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
}
.wrap { max-width: 960px; margin: 0 auto; padding: 32px 20px 64px; }
header { border-bottom: 1px solid var(--border); padding-bottom: 20px; margin-bottom: 28px; }
h1 { font-size: 22px; margin: 0 0 6px; }
.meta { color: var(--muted); font-size: 13px; }
h2 { font-size: 15px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted);
     margin: 36px 0 12px; font-weight: 600; }
p { margin: 0 0 12px; font-size: 14.5px; }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
th, td { text-align: left; padding: 9px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
th { color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.03em; }
tr:last-child td { border-bottom: none; }
.sym { font-weight: 700; letter-spacing: 0.02em; }
.num { font-variant-numeric: tabular-nums; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 600; }
.badge.current { background: rgba(61,220,132,0.15); color: var(--good); }
.badge.stale { background: rgba(245,185,66,0.15); color: var(--warn); }
.badge.missing { background: rgba(255,107,107,0.15); color: var(--bad); }
.badge.na { background: rgba(147,161,179,0.15); color: var(--neutral); }
.badge.queued { background: rgba(61,220,132,0.15); color: var(--good); }
.badge.not-queued { background: rgba(147,161,179,0.15); color: var(--neutral); }
.note { color: var(--muted); font-size: 12.5px; }
ul.actions { margin: 0; padding-left: 20px; }
ul.actions li { margin-bottom: 8px; font-size: 14px; }
.anomaly { background: var(--panel-2); border-left: 3px solid var(--warn); padding: 10px 14px;
           border-radius: 6px; font-size: 13px; color: var(--muted); margin-bottom: 8px; }
.footer-note { margin-top: 40px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--border);
               padding-top: 14px; }
"""

STATUS_LABEL = {
    "current": "Current",
    "stale": "Stale stop",
    "missing": "No live stop",
    "n/a": "N/A",
}


def esc(x):
    if x is None:
        return ""
    return html.escape(str(x))


def money(x):
    if x is None:
        return "—"
    return f"${x:,.2f}"


def pct(x):
    if x is None:
        return "—"
    sign = "+" if x > 0 else ""
    return f"{sign}{x:.2f}%"


def render_book_table(rows):
    if not rows:
        return '<p class="note">No book data.</p>'
    body = ""
    for r in rows:
        body += f"""
        <tr>
          <td class="sym">{esc(r.get('symbol'))}</td>
          <td class="num">{esc(r.get('entry_date'))}</td>
          <td class="num">{pct(r.get('return_pct'))}</td>
          <td class="num">{money(r.get('stop'))}</td>
        </tr>"""
    return f"""
    <table>
      <thead><tr><th>Symbol</th><th>In since</th><th>Return</th><th>Current stop</th></tr></thead>
      <tbody>{body}</tbody>
    </table>"""


def render_comparison_table(rows):
    if not rows:
        return '<p class="note">No comparison data.</p>'
    body = ""
    for r in rows:
        status = r.get("live_stop_status", "n/a")
        badge_class = {"current": "current", "stale": "stale", "missing": "missing"}.get(status, "na")
        held_txt = "—"
        if r.get("held"):
            qty = r.get("qty")
            avg = r.get("avg_price")
            mkt = r.get("market_price")
            held_txt = f"{qty} @ {money(avg)}" if qty is not None else "held"
            if mkt is not None:
                held_txt += f" (now {money(mkt)})"
        in_book_txt = "Yes" if r.get("in_book") else "No"
        body += f"""
        <tr>
          <td class="sym">{esc(r.get('symbol'))}</td>
          <td>{in_book_txt}</td>
          <td class="num">{held_txt}</td>
          <td class="num">{money(r.get('book_stop'))}</td>
          <td class="num">{money(r.get('live_stop'))}</td>
          <td><span class="badge {badge_class}">{esc(STATUS_LABEL.get(status, status))}</span></td>
          <td class="note">{esc(r.get('note', ''))}</td>
        </tr>"""
    return f"""
    <table>
      <thead>
        <tr>
          <th>Symbol</th><th>In book</th><th>Held</th><th>Book stop</th>
          <th>Live stop</th><th>Status</th><th>Note</th>
        </tr>
      </thead>
      <tbody>{body}</tbody>
    </table>"""


def room_above_stop(last_price, stop):
    """Percentage the last price sits above the initial stop.

    Negative means the stop is ABOVE the price, in which case Steve's
    "stop >= open" rule cancels the trade before it ever starts.
    """
    if last_price is None or stop is None or not stop:
        return None
    return (last_price - stop) / stop * 100.0


def render_signals_table(rows, price_as_of=None, resolved=False, price_label=None):
    """Render the day's new signals.

    When ``resolved`` is False (the normal pre-open case) the price column holds
    an indicative last/pre-market print and the badges describe *start risk*.
    When the newest lecture's signals have already traded their opening print
    (e.g. the run happens the morning after, before the next report is posted),
    pass ``resolved=True`` and put the actual opening price in ``last_price`` —
    the badges then describe what happened rather than what might.
    """
    if not rows:
        return '<p class="note">No new signals today.</p>'
    body = ""
    for r in rows:
        queued = r.get("queued")
        q_class = "queued" if queued else "not-queued"
        if resolved:
            q_txt = "Position held" if queued else "Not taken"
        else:
            q_txt = "Order queued" if queued else "Not queued"

        last = r.get("last_price")
        room = r.get("room_pct")
        if room is None:
            room = room_above_stop(last, r.get("stop"))

        if room is None:
            r_class, r_txt = "na", "No price"
        elif room < 0:
            r_class, r_txt = "missing", "Did not start" if resolved else "Would cancel"
        elif room < 1.0:
            r_class, r_txt = "stale", "Started, thin" if resolved else "Thin margin"
        else:
            r_class, r_txt = "current", "Started" if resolved else "Clear of stop"

        room_txt = "—" if room is None else f"{'+' if room > 0 else ''}{room:.1f}%"

        body += f"""
        <tr>
          <td class="sym">{esc(r.get('symbol'))}</td>
          <td>{esc(r.get('type'))}</td>
          <td class="note">{esc(r.get('grade', ''))}</td>
          <td class="num">{money(r.get('stop'))}</td>
          <td class="num">{money(last)}</td>
          <td class="num">{room_txt}</td>
          <td><span class="badge {r_class}">{r_txt}</span></td>
          <td><span class="badge {q_class}">{q_txt}</span></td>
        </tr>"""

    caption = ""
    if price_as_of and resolved:
        caption = (
            f'<p class="note" style="margin-top:12px">Prices are the actual opening prints for '
            f"{esc(price_as_of)}. A trade whose initial stop sits at or above the opening price "
            "is cancelled automatically, so anything marked <em>Did not start</em> never entered "
            "the book. The others are open positions that should appear in the next published "
            "file of open trades.</p>"
        )
    elif price_as_of:
        caption = (
            f'<p class="note" style="margin-top:12px">Prices as of {esc(price_as_of)}. '
            "A trade whose initial stop sits at or above the opening price is cancelled "
            "automatically before it starts, so anything marked <em>Would cancel</em> may "
            "never reach the book. Pre-market prints are thin, so treat this as indicative "
            "of the open rather than a forecast of it.</p>"
        )

    if price_label is None:
        price_label = "Open" if resolved else "Last"
    room_label = "Room above stop at open" if resolved else "Room above stop"
    status_label = "Outcome" if resolved else "Start risk"

    return f"""
    <table>
      <thead><tr>
        <th>Symbol</th><th>Tier</th><th>Report grade</th><th>Initial stop</th><th>{esc(price_label)}</th>
        <th>{esc(room_label)}</th><th>{esc(status_label)}</th><th>IBKR order</th>
      </tr></thead>
      <tbody>{body}</tbody>
    </table>{caption}"""


def render_list(items, cls="note"):
    if not items:
        return ""
    lis = "".join(f"<li>{esc(i)}</li>" for i in items)
    return f'<ul class="actions">{lis}</ul>'


def render_anomalies(items):
    if not items:
        return ""
    blocks = "".join(f'<div class="anomaly">{esc(i)}</div>' for i in items)
    return f'<h2>Data quirks worth knowing about</h2>{blocks}'


def build_html(data):
    summary_html = "".join(f"<p>{esc(p)}</p>" for p in data.get("summary", []))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CTA Timer Pro Analysis</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>CTA Timer Pro Analysis</h1>
    <div class="meta">
      Steve's report: {esc(data.get('report_date', '—'))} &middot;
      Book as of: {esc(data.get('book_as_of', '—'))} &middot;
      Generated {esc(data.get('generated_at', '—'))}
    </div>
  </header>

  <h2>Summary</h2>
  <div class="card">{summary_html or '<p class="note">No summary provided.</p>'}</div>

  <h2>Steve's current book</h2>
  <div class="card">{render_book_table(data.get('book_positions', []))}</div>

  <h2>Your book vs Steve's book</h2>
  <div class="card">{render_comparison_table(data.get('comparison', []))}</div>

  <h2>{esc(data.get('signals_heading', "Today's new signals"))}</h2>
  <div class="card">{render_signals_table(data.get('new_signals', []), data.get('price_as_of'), data.get('signals_resolved', False), data.get('price_label'))}</div>

  <h2>Open action items</h2>
  <div class="card">{render_list(data.get('action_items', []))}</div>

  {render_anomalies(data.get('anomalies', []))}

  <div class="footer-note">
    Read-only analysis. Nothing on this page has been sent to IBKR as an order, modification, or cancellation —
    "Buy at Open" and stop levels shown here are Steve's data, displayed for Travis to act on himself.
  </div>
</div>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="Path to input JSON")
    parser.add_argument("output", nargs="?", help="Path to write output HTML")
    parser.add_argument("--sample", action="store_true", help="Print a sample input JSON to stdout and exit")
    args = parser.parse_args()

    if args.sample:
        json.dump(SAMPLE_INPUT, sys.stdout, indent=2)
        print()
        return

    if not args.input or not args.output:
        parser.error("input and output are required unless --sample is used")

    with open(args.input, "r") as f:
        data = json.load(f)

    out = build_html(data)
    with open(args.output, "w") as f:
        f.write(out)

    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
