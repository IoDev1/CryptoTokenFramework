# CryptoTokenFramework

A scoring framework for picking tokens that can be held through a bear market, and a scorecard
page that shows the verdicts, live market data, news with sources, and your own entry and exit
targets.

**Live page:** https://claude.ai/code/artifact/45f2d1c6-5ac6-4f85-83bf-c3d73b53ca19

## How it works

1. **13 filters in three tiers** (v1): A dealbreakers (team doesn't dump, low dilution, moat,
   solid team), B foundation (token required, real revenue, supply dynamics), C context (can't be
   rugged, far from ATH, narrative, risks priced in, revenue trend, catalysts). Weights 1.5 / 1.0
   / 0.5, total 12. `research/RUBRIC.md` turns each into a testable definition.
2. **Two raters.** Opus 4.6 (the original run, 46 tokens) and Claude with web search (62 tokens,
   evidence and sources per cell). The page shows either, or the consensus where both must pass.
3. **Mechanical cells come from data.** CoinGecko for supply and ATH distance, DeFiLlama for
   fees and revenue. Judgment cells come from the research agents.
4. **Weights are yours.** Presets for risk-averse, fundamentals, and cash-flow investors, or
   set each slider. A "treat dealbreakers as gates" toggle demonstrates the v2 idea.
5. **Targets.** Entry, target, stop per token, with implied market cap at today's float, fully
   diluted value, and where that would rank today.
6. **News.** Google News RSS per token, last 14 days, with a model-written stance that cites
   the headlines it used.

`FRAMEWORK_v2.md` proposes the next version: hard gates, a Quality score, a separate Entry score,
and a 2022 backtest before trusting any weights.

## Run it

```bash
python3 scripts/fetch_market.py      # market data, free APIs, no key
python3 scripts/fetch_news.py        # headlines, Google News RSS, no key
python3 scripts/news_opinion.py      # stance per token via Claude Code (`claude -p`)
python3 scripts/merge_news.py
python3 scripts/build.py             # -> scorecard/index.html
open scorecard/index.html
```

Research re-run: score `research/batch_N_input.txt` under `research/RUBRIC.md` into
`research/batch_N.json` (this repo used parallel Claude agents), then
`python3 scripts/merge_research.py && python3 scripts/build.py`.

## Findings so far (2026-09-09)

- Opus and Claude disagree on about 4 of 13 cells per token. HBAR, STX, RENDER, QNT, TAO drop out
  of the top tier under stricter definitions; BNB and LTC rise.
- BTC scores 10.0 under the rubric, so the top of the scale is calibrated.
- BCH (a known non-recoverer) scores 8.0, close to LTC at 10.0: the v1 filters cannot separate
  "nothing wrong" from "something right". v2 adds prior-cycle survivorship and value accrual.

## Disclaimer

Research output, not investment advice. Verdicts are model-generated from public sources and
can be wrong. Nothing here is a recommendation to buy or sell anything.
