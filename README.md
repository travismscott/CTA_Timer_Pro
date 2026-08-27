# CTA Timer Pro

Data hand-off repo for Travis's CTA Timer Pro Analysis skill.

The original `cta-timer-pro` skill reads Steve Van Metre's Teachable reports directly via a
browser tool and renders the analysis in one pass — it needs a desktop-style session with
Claude-in-Chrome and a local device bridge.

Cloud/remote sessions have neither (and can't reach Teachable's domain at all through the
network proxy), so this repo exists as the hand-off point: Travis captures the report on his
desktop session and drops the raw text into `data/inbox/`, and the `cta-timer-pro-cloud` skill
(see `SKILL.md`) rolls that into a persisted book state (`data/book_state.json`), diffs it
against live IBKR positions/orders, and republishes the same "CTA Timer Pro Analysis" artifact —
no browser required.

See `SKILL.md` for the full workflow and the exact `data/inbox/` file contract.

Naming convention for files:
     `report_yyyy_mm_dd` for pdf report.
     `lecture_yyyy_mm_dd` for text from webpage.
