# Bear-Market Token Framework — v2 proposal

Goal: identify tokens that can be held through a bear market with high confidence of recovering,
and separately identify whether *now* is a good entry. v1 mixed those two questions in one score.

## 1. Gates (pass/fail, no points). Any fail = "Avoid", regardless of score.

| ID | Gate | Pass definition (must be evidenced) |
|----|------|-------------------------------------|
| G1 | Not ruggable | No freeze/mint authority, no unilateral supply change, admin/upgrade keys (if any) behind a >=5-of-N multisig or timelock >=48h |
| G2 | No deceptive insider selling | Fails only on UNDISCLOSED or deceptive selling: unreported transfers to exchanges, treasury reports that contradict on-chain flows, founder loans liquidated, sales timed against public statements. Scheduled, disclosed foundation sales (even large ones) do not fail this gate: the 2022 backtest showed they did not predict underperformance |
| G3 | Stewardship | Identifiable, accountable core stewards **or** proven leaderless decentralization (BTC/XMR clause: >=2 independent client teams, no single point of failure) |
| G4 | Treasury runway | Foundation/lab holds >= 3 years of runway at current burn in non-native assets (stables, BTC, ETH). Unknown = fail |
| G5 | Listing / regulatory | Listed on >= 2 of Coinbase, Kraken, Binance; no active enforcement action alleging the token is a security |

## 2. Quality score (/10). Each cell is 1 / 0.5 / 0 (pass / partial / fail) x weight. Unknown = 0.

| ID | W | Filter | Pass | Partial |
|----|---|--------|------|---------|
| S1 | 2.0 | Prior-cycle survivorship | Lived through >=1 full bear and made a new USD ATH (or >=70% of prior ATH) in the next cycle | Recovered 40–70% |
| S2 | 1.5 | Value accrual to token | Fees reach holders (burn, buyback, fee-funded staking) or token is mandatory gas with fee burn | Governance-only but revenue exists and a fee switch is live/scheduled |
| S3 | 1.0 | Revenue level | Annualized protocol revenue / FDV: P/S < 50 | P/S 50–200 |
| S4 | 1.0 | Revenue trend | 12-month revenue up | Flat |
| S5 | 1.5 | Supply health | All three: circ >= 70%, next-12m unlocks < 10% of circ, net inflation < 3%/yr | Two of three |
| S6 | 1.5 | Moat | Top-2 in category by a usage metric (TVL, fees, tx, DAU) with >= 2 years lead | Top-5 |
| S7 | 1.0 | Holder concentration | Top-10 non-exchange, non-contract wallets < 40% of supply | 40–60% |
| S8 | 0.5 | Usage/narrative growth | Active addresses or TVL trend up over 12 months (measured, not vibes) | Flat |

## 3. Entry score (/4). Reported separately. Never mixed into Quality.

| ID | W | Filter |
|----|---|--------|
| E1 | 1 | >= 75% below USD ATH (cheapness; note the 2022 backtest found this had NEGATIVE signal for recovery, it is an entry-timing input only) |
| E2 | 1 | Relative strength: drawdown from ATH better than the median of the scored universe (in 2022 this group had a median return of +109% vs +69%) |
| E3 | 1 | FDV/revenue at or below its own prior-cycle low |
| E4 | 1 | Known risks already public and priced (news is old, not breaking) |

## 4. Classification

Tiers are RELATIVE to the scored universe, because context and revenue filters are pro-cyclical (at the
November 2022 bottom only 2 of 60 tokens reached an absolute Core threshold):

- **Core hold**: Quality in the top quartile of the universe
- **Watch**: second quartile
- **Avoid**: bottom half
- **Gates** are a user setting, off by default: when on, any gate fail moves the token to Avoid regardless of
  Quality. In 2022 gates would have cut losers (no-fail tokens 92% positive vs 64%) but also excluded every
  token that beat BTC.
- Entry score decides *when*, not *whether*. It never enters the Quality score.
- **BTC is the benchmark.** Every basket is reported against holding BTC over the same period.

## 4b. What the framework claims

An informed, structured way to choose what to hold through a bear market, with the evidence attached. The
2022 backtest supports one claim: high-Quality tokens rarely blew up (top 20 by score: 95% positive, none below
-50%). It does not support picking the biggest winners, and the product must never claim that. Results belong
to users; the platform gives them the structure, the sources and a way to share their own plans and outcomes.

## 5. Research rules for the model

1. Every cell needs: value, one-line evidence, source URL, date checked, confidence (H/M/L).
2. Unknown or unverifiable = 0, never a pass.
3. No token may finish with "None identified". The model must state the strongest bear case for every token.
4. After scoring, run an adversarial pass: "For every pass cell, find evidence that would make it a fail."
5. Same standard for the same behaviour (e.g. foundation selling: ETH, LINK, SOL, HBAR judged by the same G2 number).

## 6. Validation before using real money

1. **Backtest**: score the top 60 by market cap as of 2022-11-15 using only information available then. Compare "Core hold" vs "Avoid" against USD return to 2025-01-15. If Core hold did not clearly beat Avoid, reweight.
2. **Anchors**: BTC and ETH must land in Core hold. If BTC scores like "high risk", the framework penalizes decentralization and G3/S2 need fixing.
3. **Controls**: include known non-recoverers (EOS, XTZ, IOTA, BCH, NEO, ALGO, FTT, LUNC, ETC) — they must land in Avoid.

## 7. Tokens to add to the next run

Anchors: BTC, ETH (already), XMR (already)
L2/unlock heavy: ARB, OP, MNT, STRK
DeFi with fee capture: PENDLE, LDO, ENA, ONDO, GMX, RPL
Infra: ATOM, TIA, FIL, AR, GRT, ALGO, XLM, XTZ
Exchange tokens vs BNB: OKB, LEO, CRO
Memes as control: DOGE, PEPE
Historical failure controls: EOS, IOTA, BCH, NEO, ETC, LUNC

## 8. Evidence from the 2022 backtest (2026-09-20, see BACKTEST.md)

Top 60 on 2022-11-13, scored as of the cutoff, returns to 2025-01-12. What it changes in this proposal:

- **FC2 leaves the Quality score.** "Far from ATH" had negative signal (median edge -40). It stays in Entry only, and E2 (token/BTC
  ratio at a low) should be replaced by a relative-strength check: drawdown better than the universe median is a positive.
- **G2 / FA1 is narrowed.** Disclosed foundation selling did not predict underperformance (edge -52). The gate should catch undisclosed
  transfers, deceptive reporting and founder-loan liquidations, not scheduled sales.
- **S2, S3, S5 carry the weight.** Real revenue (+90), low dilution (+97) and supply dynamics (+69) were the strongest quality signals;
  foundation-only weights had the best rank correlation (0.25 vs 0.16 for v1).
- **Tiers become relative.** Only 2 of 60 reached the absolute Core threshold at the bottom because context filters are pro-cyclical.
  Core = top quartile of the scored universe, Avoid = bottom half, or equivalent percentile cut.
- **Gates are a risk setting, not a default.** No-dealbreaker-fail tokens were 92% positive versus 64% for two-plus fails, but gates
  would have excluded every token that beat BTC (SOL, XRP, HBAR, BIT).
- **BTC is the benchmark.** 4 of 60 beat it. A basket that does not beat BTC is not a reason to hold anything else.
- **Loss avoidance is the product.** Top 20 by score: 95% positive, none below -50%. That is the claim the framework can support today.
