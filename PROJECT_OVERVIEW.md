# Conviction Scorecard — project overview

Written 2026-09-12 for comparison with other projects and a go-live decision.

## What it is

A bear-market portfolio planner for crypto tokens, with the research attached. It answers one
question per token, "can this be held through a bear market and recover", by scoring it against
13 filters in three tiers (dealbreakers, foundation, context). Two independent model-driven
research passes score every token, the page shows where they disagree, and every judgment cell
carries a one-line evidence note and the sources consulted. On top of the scores the user sets
their own weights, entry and exit levels, and allocations, and sees what the plan implies:
required market cap, fully diluted ceiling, rank, and portfolio multiples under three scenarios.
Plans are shareable by link. Recent news per token is shown with source and date, plus a model
opinion that cites the headlines it used.

Positioning: research tooling, not advice. The tool never recommends; every level is the user's.

## Status

- **Framework v1**: 13 filters, written rubric with strict definitions, consistency rules
  applied at merge time. 62 tokens scored: 46 from the original Opus 4.6 run, all 62 by the
  Claude research pass, including BTC as a calibration anchor and BCH, ETC, XTZ as known
  non-recoverer controls.
- **Framework v2**: designed (hard gates, Quality/10, separate Entry/4, survivorship and value
  accrual filters), not yet run. A 2022 backtest is planned to validate weights.
- **Product**: single-page web app, feature-complete for a first public release: scores, evidence,
  weights, plan, share, news, about, disclaimer. Verified in a browser, no console errors.
- **Pipeline**: fully scripted, no API keys required for market data or news. Daily GitHub
  Actions workflow written (fetch, build, commit, deploy to GitHub Pages). Not yet pushed to a
  public repository, so not yet live.
- **Model steps**: currently run through Claude Code sessions. API versions (news stance daily,
  research monthly) are the next engineering step.
- **Monetization**: decided in principle, free core plus a paid tier for alerts, saved plans and
  verdict history; nothing built yet.

## How it is built

Deliberately minimal. No framework, no build tooling beyond Python's standard library, no
database, no server. The site is one static HTML file with the data embedded.

| Layer | Technology | Notes |
|---|---|---|
| Page | Single HTML file, vanilla JS, inline CSS, inline SVG for the spider chart | ~470 lines of template; ~480 KB built with data embedded; light/dark themes; responsive |
| Data fetch | Python 3, standard library only, HTTP via `curl` subprocess | CoinGecko (prices, supply, ATH), DeFiLlama (fees, revenue), outlet RSS feeds (news) |
| Research | Rubric in Markdown; parallel Claude agents with web search write strict JSON per batch | Merge script enforces mechanical cells and consistency rules |
| Build | `build.py` injects four JSON files into the template placeholders | Also snapshots the day's data into `data/history/<date>/` |
| State | Browser `localStorage` for weights, targets, allocations | Share links carry the full plan as base64url JSON in the URL hash; no backend |
| CI/CD | GitHub Actions cron, daily | Fetch, build, commit refreshed data, deploy to GitHub Pages |
| Hosting | Any static host | GitHub Pages configured; Cloudflare Pages or an S3 bucket would work unchanged |

Model use is per token, never per visitor. A model run refreshes stored JSON; the page renders
stored JSON. Running cost is therefore independent of traffic: roughly $0 for data and hosting,
and an estimated ~$20 a month once the model steps move to the API (Haiku-class for daily news
stance, Opus-class for the monthly research pass).

## Repository structure

```
CryptoTokenFramework/
├── scorecard/
│   ├── template.html        # the page source (placeholders for the four JSON files)
│   └── index.html           # build output, deployed as-is
├── scripts/
│   ├── fetch_market.py      # CoinGecko + DeFiLlama -> data/market.json
│   ├── fetch_news.py        # outlet RSS, rolling 14-day store -> data/news.json
│   ├── news_opinion.py      # builds news inputs, runs the stance step
│   ├── merge_research.py    # research/batch_*.json -> data/research.json (+ consistency rules)
│   ├── merge_news.py        # stance JSON -> data/news.json
│   └── build.py             # inject JSON -> scorecard/index.html, snapshot history
├── research/
│   ├── RUBRIC.md            # the 13 filter definitions (single source of truth)
│   ├── NEWS_OPINION_PROMPT.md
│   └── batch_*.json         # raw agent outputs, kept for audit
├── data/
│   ├── market.json  research.json  news.json  targets.json
│   └── history/<date>/      # daily snapshots, committed
├── .github/workflows/refresh.yml
├── FRAMEWORK_v2.md  PRODUCT_NOTES.md  TODO.md  README.md  CLAUDE.md
```

## Deployment requirements

- A public or private GitHub repository with Pages enabled (source: GitHub Actions).
- No secrets for the current pipeline. One secret (`ANTHROPIC_API_KEY`) once the model steps
  move to the API.
- No runtime dependencies on the host. The deployed artifact is a single HTML file.
- Data refresh is a scheduled job; if it fails, the last deployed page keeps serving.

## Size

About 830 lines of Python, one 470-line HTML template, 62 researched tokens, roughly 1 MB of
JSON data including one day of history. One contributor, two working days.
