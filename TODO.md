# TODO

## Framework
- [ ] Settle v2 filter list from `FRAMEWORK_v2.md` using Opus-vs-Claude disagreements as test cases
- [ ] Add prior-cycle survivorship and value-accrual filters (BCH 8.0 vs LTC 10.0 shows the gap)
- [ ] Backtest: score the top 60 as of 2022-11-15 with information available then; compare Core hold vs Avoid to 2025-01-15 returns
- [ ] Anchors and controls in every run: BTC, ETH must be Core hold; EOS, IOTA, LUNC, BCH, ETC, XTZ must be Avoid
- [ ] Draft the Opus research prompt from `research/RUBRIC.md` so both raters use identical definitions
- [ ] Automate unlock schedule (TokenUnlocks or similar) for FA2 / FB3

## Data
- [ ] Revenue per day and per month plus P/S (mcap / annualized revenue) from DeFiLlama; chain fees vs protocol revenue labelled clearly
- [x] Move news sourcing to outlet RSS (8 outlets, rolling 14-day store, seeded from Google 2026-09-10); headlines + links only
- [x] `build.py` snapshots `data/*.json` into `data/history/<date>/`; the workflow commits it daily. **Design note from 2026-09-10.**
- [ ] Nine tokens have no DeFiLlama revenue source (QNT, TAO, FET, KAS, VET, LTC, WLD, PLUME, KAITO): find alternatives or mark n/a explicitly

## Page
- [x] Portfolio view: allocation per token, portfolio multiple (all hit / Core-only flat / rest to zero)
- [x] Share plan as a link (state in the URL hash, no backend); receiver gets an editable copy
- [ ] Paste exported targets into `data/targets.json` to keep them in the repo
- [ ] Table is wide; consider column groups or a compact mode

## Public version (see `PRODUCT_NOTES.md`)
- [ ] Replace `claude -p` with API calls: Haiku 4.5 for news stance, Opus 5 for the monthly research pass
- [x] GitHub Actions: daily market + news, rebuild, commit, deploy to Pages (`.github/workflows/refresh.yml`)
- [ ] Create the GitHub repo, push, enable Pages (Settings > Pages > Source: GitHub Actions)
- [x] Static hosting via GitHub Pages (workflow ready)
- [x] Disclaimer + about section + educational wording
- [ ] Notifications (Telegram bot first, no account system needed) when price crosses a user's entry / target / stop
- [ ] Pricing: one-time €9.99 for alerts + share + pro features; use a merchant of record (Paddle / Lemon Squeezy) for EU VAT
- [ ] Optional "verified on-chain holdings" badge via wallet signature; defer, privacy and shilling risk
- [ ] Monetize with exchange affiliates and a newsletter before display ads

## Brainstorm log
- 2026-09-10: portfolio planner framing, price following + notifications, show planned "x", L1 revenue per day/month, shareable portfolio, proof of holdings, €9.99 forever. Assessment in `PRODUCT_NOTES.md`.
