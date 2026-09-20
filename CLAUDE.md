# CLAUDE.md — CryptoTokenFramework

Bear-market token scoring framework plus a scorecard page. Research is model-generated
(Opus 4.6 by the user, Claude with web search via this repo's pipeline); the page renders stored
JSON and never calls a model per visitor.

## Layout

| Path | What |
|---|---|
| `FRAMEWORK_v2.md` | Proposed v2 filter set: gates + Quality/10 + Entry/4, backtest plan, tokens to add |
| `PRODUCT_NOTES.md` | Public-product assessment, monetization, architecture, refresh chain |
| `TODO.md` | Open work, ordered |
| `research/RUBRIC.md` | Strict definitions of the 13 v1 filters used for the Claude research pass. Edit here, never in prompts |
| `research/NEWS_OPINION_PROMPT.md` | Prompt for the news stance step |
| `research/batch_*_input.txt`, `research/batch_*.json` | Per-batch research inputs and agent outputs (raw) |
| `research/news_batch_*` | Same for news opinions |
| `scripts/fetch_market.py` | CoinGecko + DeFiLlama -> `data/market.json` (+ top-100 ladder) |
| `scripts/fetch_news.py` | Outlet RSS (8 feeds), rolling 14-day store -> `data/news.json`; `--google` for personal use |
| `scripts/news_opinion.py` | Builds news inputs; `--api` runs claude-haiku-4-5 (CI), default runs `claude -p` on the user's plan |
| `scripts/research_run.py` | `--prepare` writes batch inputs from market data; `--api` runs claude-opus-5 + web search per batch (monthly CI) |
| `scripts/model_api.py` | Shared API helper: streamed request, pause_turn loop, refusal check, JSON extraction, cost estimate |
| `data/site.json` | Public-site config: newsletter link, PostHog key/host (EU), affiliates. Injected as `__SITE_JSON__` |
| `.github/workflows/research.yml` | Monthly: market + research pass + merge + build + commit (the daily workflow deploys it) |
| `scripts/merge_research.py` | `research/batch_*.json` -> `data/research.json`, applies consistency rules |
| `scripts/merge_news.py` | `research/news_batch_*.json` -> opinions folded into `data/news.json` |
| `scripts/build.py` | Snapshots data, runs `diff_history.py`, injects JSON into the templates -> `scorecard/{index,ledger}.html` (bare, for the artifact) and `site/{index,ledger}.html` (full documents, for Pages) |
| `scripts/diff_history.py` | `data/history/*` -> `data/changes.json` (this-week panel) and `data/ledger.json` (public ledger) |
| `scorecard/ledger_template.html` | Ledger page source; placeholder `__LEDGER_JSON__` |
| `scorecard/template.html` | THE source of the page. Placeholders `__MARKET_JSON__`, `__RESEARCH_JSON__`, `__NEWS_JSON__`, `__TARGETS_JSON__` |
| `scorecard/index.html` | Build output. Never edit by hand |
| `data/*.json` | market, research, news, targets. `data/history/<date>/` holds daily snapshots |
| `.github/workflows/refresh.yml` | Daily: fetch market + news, build, commit, deploy to GitHub Pages |
| `scripts/backtest/` | `cmc_snapshot.py` (CMC weekly snapshot -> JSON), `universe.py`, `enrich.py` (pre-cutoff ATH via CoinGecko/Yahoo verified, DeFiLlama historical fees), `analyze.py` (merge, baskets, per-filter signal, weight sweep -> `BACKTEST.md`) |
| `research/BACKTEST_RUBRIC.md` | Same 13 filters with the 2022-11-15 information cutoff rules |
| `data/backtest/` | snapshots, universe, batch inputs/outputs, results.json |

Published artifact: https://claude.ai/artifact/9dygq8VEnSkatpDq6xiZag (older link form: https://claude.ai/code/artifact/45f2d1c6-5ac6-4f85-83bf-c3d73b53ca19)
(republish `scorecard/index.html` with that `url` to update in place).

## Refresh chain

```bash
python3 scripts/fetch_market.py && python3 scripts/fetch_news.py && python3 scripts/news_opinion.py \
  && python3 scripts/merge_news.py && python3 scripts/build.py
```
Research re-run: agents score `research/batch_N_input.txt` under `research/RUBRIC.md` into
`research/batch_N.json`, then `python3 scripts/merge_research.py && python3 scripts/build.py`.

## Conventions and gotchas

- HTTP goes through `curl` subprocess: the python.org Python 3.14 on this Mac has no root certs.
- CoinGecko symbol collisions: pin ids in `ID_OVERRIDES` (TON, VVV, PUMP, ARB, LEO, ETC).
- `circ_pct` = circulating / total EXISTING supply. Stale max caps (BNB 200M) are not dilution;
  future emission is `unminted_pct` and judged as inflation.
- Merge rules in `merge_research.py`: FC2 mechanical from ATH distance; FA2 corrected for stale
  caps; FB2 fails if only block subsidy/hashrate is cited; FC5 needs >= $1M/30d revenue.
- The page rescales every score to /12 so weight presets stay comparable.
- "Correct Opus FA2 & FC2 with live data" only touches Opus cells. Claude cells already use
  today's data plus judgment; never override them mechanically.
- Non-ASCII in the templates: `&#x...;` entities in markup, `\uXXXX` escapes inside `<script>` (canvas text
  cannot use entities). A local `python -m http.server` preview mis-decodes raw UTF-8 otherwise.
- Image cards (token, plan) are drawn on a 1200x675 canvas in the browser; download/copy work on the public site, not inside the artifact sandbox.
- Ledger and this-week panel always use v1 weights, Claude verdicts, thresholds 10/8, no gates, so they are stable regardless of visitor settings.
- Tokens without Opus bits (BTC and the 15 added 2026-09-09) show "Not scored" under the Opus rater.
- Targets/allocations are per-browser (`localStorage` key `cs.targets`); `data/targets.json` holds defaults.
- Share links encode the whole plan in `#p=<base64url JSON>`; `loadHash()` imports it and clears the hash.
- News is a rolling 14-day store per token (union by URL across runs); opinions carry `cited_items` so headline indices never drift. `fetch_news.py --google` is personal-use only.
- Keep each day's JSON (commit, don't overwrite) once public: verdict history is the backtest.
- Both model steps exit 0 and keep stored output when `ANTHROPIC_API_KEY` is absent; the site never breaks on a missing secret.
- PostHog is EU cloud, memory persistence, no recording, no autocapture: no consent banner needed. Only loads when `site.json` has a key.
- Pushes made with `GITHUB_TOKEN` do not trigger other workflows, so the monthly research commit is deployed by the next daily refresh.
- Backtest data sources: CoinGecko free tier refuses history > 365 days; CMC weekly snapshots (Sundays) embed the top-200 listing as an escaped JSON string; Yahoo tickers collide (APE, MATIC), so every Yahoo series is verified against the CMC price on the cutoff date before use.
- This is research tooling, not advice. Keep wording educational on anything public.
