# 2022 backtest — v1 framework scored as of 2022-11-13, returns to 2025-01-12

Universe: top 60 by market cap on 2022-11-13 (CoinMarketCap snapshot), stablecoins and wrappers excluded, 60 scored. Judgment cells were researched by Claude agents with web search under `research/BACKTEST_RUBRIC.md` (information cutoff 2022-11-15, pre-cutoff sources only). Mechanical cells (FC2, FA2 correction, FB2/FC5 materiality) come from CoinMarketCap, Yahoo Finance and DeFiLlama data as of the cutoff. **Hindsight caveat:** the researchers know what happened afterwards; the cutoff instruction limits but cannot eliminate leakage, so treat judgment-cell results as indicative.

## Findings

**1. The framework avoids losers; it does not pick winners.** Median return rises by tier (Core 323%, Watch 110%, Avoid 53%) and the
top 20 by score were 95% positive with no token below -50%, while the bottom 20 were 55% positive. Nine of the ten worst performers
scored Avoid; MATIC (9.5, -49%) is the only high-scoring loser. But rank correlation between score and return is only 0.16, and all four
tokens that beat BTC scored Avoid: SOL 4.5 (+1332%), BIT 5.0 (+1069%), XRP 4.0 (+637%), HBAR 5.5 (+513%). The biggest winners were exactly the
dealbreaker cases: FTX-estate overhang, escrow selling, insider-heavy supply. That is why the Avoid basket's mean (145%) beats Watch (131%)
while its median is far lower.

**2. Beating BTC was nearly impossible.** 4 of 60 did. BTC returned +478% and was the fifth-best asset in the universe. Any framework that
did not reduce to "hold BTC" underperformed, and BTC plus ETH were the only two Core holds, so the framework did say that, at the cost of
holding almost nothing else.

**3. The Core threshold is unreachable at a bear-market bottom.** Only 2 of 60 scored 10 or more. The Context filters are pro-cyclical: at
the cutoff only 23% passed "growing narrative", 20% "real revenue", 17% "catalysts", 7% "revenue trajectory". The framework penalises the
exact moment it exists for. Thresholds should be relative (top quartile of the universe) rather than absolute.

**4. Filters that carried signal** (median return, pass minus fail): low dilution +97, growing narrative +94, real revenue +90, team known
and solid +89, supply dynamics +69, moat +53, can't be rugged +53. Foundation-only weights had the best rank correlation (0.25), the
fundamentals preset next (0.21), dealbreakers-only the worst (0.13). Value accrual predicted recovery better than "nothing is wrong".

**5. Two filters pointed the wrong way.** "Team doesn't dump" (-52): tokens flagged for foundation selling in 2022 (XRP, XLM, SOL, LINK,
TON, NEAR) recovered strongly, because insiders were selling into businesses that survived; the filter as written measures selling, not
survival. "Far from ATH" (-40): tokens that were NOT 75% down (BNB, TRX, LEO, OKB, TON, APT, XMR) had a median return of 109% versus 69%
for the rest. Relative strength persisted through the bottom. "Cheap" was not a quality signal and should leave the quality score.

**6. Hard gates trade upside for safety.** Tokens with no dealbreaker fail were 92% positive (median +133%); tokens with two or more fails
were 64% positive (median +53%). But gating would also have excluded all four BTC-beaters. Gates are a loss-avoidance tool, not a return tool.

**Implications for v2** (recorded in `FRAMEWORK_v2.md`): drop FC2 from the quality score and keep it only as an entry signal, or invert it into
a relative-strength filter; narrow FA1 to undisclosed or deceptive insider selling; raise the weight of value accrual, revenue and supply health;
make tiers relative; keep BTC as the benchmark every basket must beat; treat gates as a risk setting the user can switch on.

**v2 on the same data** (section at the end): rank correlation 0.20 vs 0.16, relative tiers give a 15-token Core basket that was 93% positive with a median of +133%, versus +43% for the bottom half. Value accrual (median +159% vs -19%), revenue level (P/S) and supply health separate outcomes most.

**Hindsight caveat, again.** The judgment cells were researched by models that know 2023-2025. The cutoff instruction was followed (several agents
reported finding and excluding post-cutoff facts), but leakage cannot be ruled out, and the mechanical cells are the only fully clean ones. The
daily verdict history started 2026-09-10 is the leak-free version of this test.

## Headline

| Basket | n | Mean return | Median | Beat BTC |
|---|---|---|---|---|
| Core (v1 weights) | 2 | 322.6% | 322.6% | 0% |
| Watch (v1 weights) | 15 | 130.5% | 110.3% | 0% |
| Avoid (v1 weights) | 43 | 145.3% | 53.4% | 9% |
| Core (hard gates) | 2 | 322.6% | 322.6% | 0% |
| Watch (hard gates) | 11 | 108.9% | 110.3% | 0% |
| Avoid (hard gates) | 47 | 149.1% | 53.4% | 9% |
| BTC | 1 | 477.8% | | |
| ETH | 1 | 167.3% | | |
| Top 20 equal weight | 20 | 244.8% | | |
| Whole universe equal weight | 60 | 147.5% | 73.5% | 7% |

Spearman rank correlation, v1 score vs return: **0.159** (1 = perfect ordering, 0 = none).

## Which filters carried signal

Median return of tokens that passed vs failed each filter, and the share that beat BTC.

| Filter | Pass n | Pass median | Pass beat BTC | Fail n | Fail median | Fail beat BTC | Edge (median) |
|---|---|---|---|---|---|---|---|
| FA2 Low dilution | 32 | 116.7% | 0% | 28 | 20.0% | 14% | **96.7** |
| FC3 Growing narrative | 14 | 156.6% | 14% | 46 | 63.1% | 4% | **93.5** |
| FB2 Real revenue | 12 | 144.8% | 8% | 48 | 55.1% | 6% | **89.7** |
| FA4 Team known & solid | 52 | 93.4% | 6% | 8 | 4.4% | 12% | **89.0** |
| FB3 Supply dynamics | 16 | 116.5% | 0% | 44 | 47.4% | 9% | **69.1** |
| FA3 Moat | 29 | 110.3% | 7% | 31 | 57.2% | 6% | **53.1** |
| FC1 Can't be rugged | 23 | 110.3% | 9% | 37 | 57.2% | 5% | **53.1** |
| FC6 Catalysts | 10 | 85.2% | 0% | 50 | 73.5% | 8% | **11.7** |
| FC5 Revenue trajectory | 4 | 81.7% | 0% | 56 | 73.5% | 7% | **8.2** |
| FB1 Token required | 50 | 73.5% | 6% | 10 | 81.8% | 10% | **-8.3** |
| FC4 Risks priced in | 40 | 73.5% | 2% | 20 | 83.0% | 15% | **-9.5** |
| FC2 Far from ATH | 49 | 69.1% | 8% | 11 | 108.8% | 0% | **-39.7** |
| FA1 Team doesn't dump | 41 | 57.2% | 5% | 19 | 108.8% | 11% | **-51.6** |

## Weight sets

| Weights | Spearman | Core mean (n) | Watch mean (n) | Avoid mean (n) |
|---|---|---|---|---|
| v1 (A1.5 B1.0 C0.5) | 0.159 | 322.6% (2) | 130.5% (15) | 145.3% (43) |
| flat (all 1) | 0.199 | None% (0) | 173.1% (11) | 141.7% (49) |
| risk-averse (A2.5 B1 C.25) | 0.163 | 160.3% (10) | 140.2% (8) | 145.8% (42) |
| fundamentals (A1 B2 C.5) | 0.211 | 322.6% (2) | 154.0% (10) | 138.8% (48) |
| dealbreakers only | 0.132 | 141.7% (13) | 155.7% (19) | 144.5% (28) |
| foundation only | 0.247 | 322.6% (2) | 188.2% (18) | 120.4% (40) |

## Every token

| # 2022 | Token | Score | Tier | A fails | From ATH 2022 | Return | Beat BTC | Conf | Key risk (as of 2022) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | BTC | 10.5 | core | - | -75.8% | 477.8% | no | H | Post-FTX contagion (exchange/lender insolvencies) and a bear-market decline in on-chain fee demand; usage metr |
| 2 | ETH | 10.0 | core | - | -74.6% | 167.3% | no | H | Regulatory: SEC chair suggested PoS staking may make ETH a security (Sep 2022) and OFAC sanctions raised valid |
| 10 | MATIC | 9.5 | watch | - | -69.6% | -49.4% | no | M | Team/foundation hold a large share and core contracts sit behind a multisig; MATIC not yet -75% from ATH |
| 24 | XMR | 9.5 | watch | - | -73.6% | 56.8% | no | H | Exchange delistings/regulatory pressure on privacy coins; fee revenue negligible. |
| 31 | VET | 9.5 | watch | - | -93.2% | 132.8% | no | M | Enterprise narrative has never converted into fee demand; the chain is foundation-controlled and has frozen ba |
| 47 | THETA | 9.5 | watch | - | -94.4% | 141.7% | no | M | Value accrual flows to TFUEL not THETA, validators are Theta Labs-selected, and no fee revenue backs the netwo |
| 58 | MKR | 9.5 | watch | - | -89.2% | 110.3% | no | M | Revenue and DAI supply shrinking through 2022 while founder-driven Endgame adds future MKR emissions. |
| 16 | UNI | 9.0 | watch | - | -87.1% | 134.7% | no | M | Governance-only token with ~13%/yr vesting supply; value accrual depends on a fee switch not yet on |
| 44 | XTZ | 9.0 | watch | FA3 | -88.9% | 24.4% | no | M | Falling account activity and no category lead; positive score rests on the supplied fee figure and the upgrade |
| 49 | MANA | 9.0 | watch | - | -92.3% | 7.0% | no | M | Usage is tiny relative to a ~$0.8B valuation and the token contract keeps owner pause/mint powers |
| 50 | AAVE | 9.0 | watch | - | -91.4% | 408.3% | no | H | Protocol usage and fees are down ~60% y/y with no fee flow to the token; AAVE remains a governance/backstop as |
| 4 | BNB | 8.5 | watch | - | -59.1% | 150.6% | no | M | Single point of failure: Binance controls the validator set, burn policy and most supply; ongoing US DOJ/CFTC  |
| 15 | TRX | 8.5 | watch | FA1 | -76.9% | 358.7% | no | M | Governance and supply effectively controlled by Justin Sun; USDD algorithmic peg keeps breaking |
| 17 | LTC | 8.5 | watch | - | -86.0% | 78.0% | no | M | Near-zero fee revenue and shrinking exchange support after MWEB privacy upgrade; value rests on halving narrat |
| 23 | ETC | 8.5 | watch | - | -88.1% | 26.6% | no | M | Hashrate without users: near-zero fee demand, ~$1M DeFi TVL, and 2020 51%-attack history |
| 27 | BCH | 8.5 | watch | FA3 | -97.4% | 349.4% | no | H | Structural loss of relevance: shrinking hashrate and usage relative to BTC, no fee economy. |
| 67 | XEC | 8.0 | watch | FA3 | -92.5% | 27.1% | no | M | Single-client chain with negligible fee demand; value rests on Bitcoin ABC roadmap execution and miner subsidy |
| 70 | NEO | 7.5 | avoid | FA3 | -96.6% | 122.8% | no | M | Foundation-dominated council governance over a shrinking ecosystem with one dapp holding all TVL. |
| 8 | ADA | 7.0 | avoid | FA3 | -89.3% | 193.4% | no | M | Usage far below valuation (TVL rank ~27, fees ~$0.3M/month) while three founding entities still hold the genes |
| 9 | DOGE | 7.0 | avoid | FA4 | -88.4% | 295.7% | no | M | Price driven by Elon Musk attention (Twitter close 2022-10-27) with no fee demand, ~4%/yr perpetual issuance a |
| 11 | DOT | 7.0 | avoid | FA2 | -89.5% | 15.2% | no | M | High inflation and near-zero fee capture while parachain usage has been falling through 2022 |
| 22 | ATOM | 7.0 | avoid | FA2 | -76.8% | -36.5% | no | M | Double-digit inflation with no fee capture, and a just-vetoed tokenomics overhaul leaves direction unresolved |
| 33 | QNT | 7.0 | avoid | FA3 | -76.1% | 2.1% | no | M | Token value rests on undisclosed licence flows; company holds ~17% unlocked and the 2022 rally priced CBDC hop |
| 69 | SNX | 6.5 | avoid | FA2 | -94.5% | 13.3% | no | H | Double-digit SNX inflation persists while atomic-swap fee revenue has fallen ~90% from the June 2022 peak. |
| 32 | FIL | 6.5 | avoid | FA1,FA2 | -98.2% | 18.5% | no | M | Structural sell pressure: PL/Foundation/SAFT vesting plus miner minting add tens of percent of circulating sup |
| 62 | ZEC | 6.5 | avoid | FA2 | -98.7% | 18.0% | no | M | High inflation to 2024 plus unresolved spam attack and negligible fee demand. |
| 63 | MIOTA | 6.5 | avoid | FA3 | -95.9% | 53.4% | no | M | Foundation-controlled Coordinator with no fee demand and repeatedly delayed decentralisation. |
| 71 | FTM | 6.0 | avoid | FA3 | -94.8% | 286.5% | no | M | Alameda's FTM stake becomes a bankruptcy-estate overhang while TVL and fees are down >90% year-on-year. |
| 20 | LEO | 6.0 | avoid | FA3 | -47.7% | 134.6% | no | M | Centralized issuer token with mint/freeze authority; value hinges on iFinex/Tether solvency and disclosure |
| 21 | LINK | 6.0 | avoid | FA1,FA2 | -88.5% | 226.7% | no | M | Half the supply sits in team-controlled wallets released at ~7%/yr; oracle fees are mostly reserve-subsidized |
| 30 | CRO | 6.0 | avoid | FA3 | -92.7% | 110.5% | no | M | Exchange-token contagion four days after FTX: Crypto.com's solvency and disclosure quality (320k ETH mis-send) |
| 34 | FLOW | 6.0 | avoid | FA3 | -97.2% | -38.9% | no | M | Single-app chain whose app (Top Shot) is down 94% YoY, with a permissioned node set and an unresolved securiti |
| 53 | BSV | 6.0 | avoid | FA3,FA4 | -92.1% | 49.2% | no | M | The ecosystem's credibility is tied to Craig Wright's litigation record while low hashrate leaves the chain 51 |
| 60 | BTT | 6.0 | avoid | FA1,FA3 | -80.2% | 69.1% | no | L | Supply and chain controlled by Justin Sun entities with opaque insider holdings and no fee demand. |
| 64 | CAKE | 6.0 | avoid | FA2,FA4 | -90.9% | -42.6% | no | M | Heavy ongoing CAKE emission run by an anonymous team amid falling DEX volume. |
| 13 | SHIB | 5.5 | avoid | FA1,FA3,FA4 | -89.5% | 138.9% | no | M | Anonymous, founder-abandoned meme token with no required utility and collapsing DEX usage |
| 25 | XLM | 5.5 | avoid | FA1,FA2 | -89.9% | 378.5% | no | M | SDF controls ~half of supply and sells at its discretion; on-chain fee demand is negligible. |
| 28 | ALGO | 5.5 | avoid | FA2,FA3 | -92.6% | 37.5% | no | M | Foundation-driven supply growth (governance rewards, grants) and Foundation-controlled relay layer. |
| 29 | NEAR | 5.5 | avoid | FA1,FA3 | -90.4% | 154.4% | no | M | VC-heavy cap table (3AC-led round, Alameda) unwinding into a collapsing DeFi ecosystem; USN failure. |
| 35 | CHZ | 5.5 | avoid | FA1,FA2 | -77.2% | -59.6% | no | M | A third of supply sits in an unscheduled company treasury and the fan-token product cycle is event-driven, not |
| 40 | HBAR | 5.5 | avoid | FA2,FA3 | -92.0% | 513.2% | yes | M | Council-run permissioned network with 54% of supply still in treasury and no fee revenue to speak of. |
| 52 | TWT | 5.5 | avoid | FA2 | -28.2% | -39.5% | no | M | 58% of supply sits with Trust Wallet/Binance on no schedule, the token has discount-only utility, and it trade |
| 18 | AVAX | 5.0 | avoid | FA2,FA3 | -91.0% | 180.1% | no | M | High net emission plus quarterly unlocks into collapsing usage; fresh Crypto Leaks litigation allegations |
| 26 | TON | 5.0 | avoid | FA1,FA2 | -68.7% | 220.6% | no | M | Opaque, highly concentrated supply from the 2020-22 mining phase (76% not circulating) controlled by unknown h |
| 41 | EGLD | 5.0 | avoid | FA2,FA3 | -92.1% | -24.0% | no | M | Alt-L1 with ~7% inflation, shrinking DeFi usage, and a team that can pause and patch the chain. |
| 42 | EOS | 5.0 | avoid | FA1,FA3 | -96.1% | -11.2% | no | M | Chain governed by 21 BPs who have frozen accounts and rewritten token issuance; no fee revenue and steadily sh |
| 45 | SAND | 5.0 | avoid | FA1,FA2 | -93.0% | -1.4% | no | M | Half the supply still locked with a ~23%-of-float cliff due Feb 2023, on top of collapsing land demand |
| 61 | BIT | 5.0 | avoid | FA2 | -89.7% | 1068.5% | yes | M | Continuous large Bybit unlocks into a thinly circulating governance token with no protocol revenue. |
| 14 | SOL | 4.5 | avoid | FA1,FA2,FA3 | -94.9% | 1332.3% | yes | H | FTX/Alameda estate overhang and ecosystem contagion (Serum, 20% of projects FTX-funded) |
| 46 | APE | 4.5 | avoid | FA2,FA3 | -89.2% | -62.2% | no | M | Only 31% floats; Yuga/founder cliff in March 2023 and 100M APE of staking emissions dwarf organic demand |
| 57 | AXS | 4.5 | avoid | FA2,FA3 | -95.7% | -12.6% | no | H | Play-to-earn demand collapsed (fees -99% y/y) while ~22%-of-circulating AXS unlocks keep landing every quarter |
| 7 | XRP | 4.0 | avoid | FA1,FA2,FA4 | -89.9% | 636.5% | yes | H | Binary SEC v. Ripple outcome plus continuous Ripple escrow selling (~$300-400M per quarter) into a market with |
| 38 | OKB | 4.0 | avoid | FA2,FA3 | -58.1% | 169.4% | no | L | Exchange-token contagion four days after FTX, on a token where the issuer holds 80% of supply with no fixed re |
| 55 | KCS | 4.0 | avoid | FA2,FA3 | -74.9% | 57.2% | no | M | Exchange token facing post-FTX solvency rumors with reserves not yet proven, an Ontario regulatory ban and a l |
| 68 | KLAY | 3.5 | avoid | FA1,FA2,FA3 | -96.0% | 21.5% | no | M | Foundation-controlled 72% of supply distributed to grantees who sell; permissioned council can change emission |
| 37 | ICP | 3.5 | avoid | FA1,FA2,FA3 | -99.4% | 158.8% | no | M | Foundation-dominated governance and a documented 2021 insider-dump pattern, with a pending securities class ac |
| 36 | LUNC | 3.0 | avoid | FA1,FA3,FA4 | -100.0% | -40.5% | no | M | Fugitive founder and open prosecutions on a chain whose supply and tax parameters are rewritten by a thin vali |
| 66 | APT | 2.5 | avoid | FA1,FA2,FA3 | -56.7% | 108.8% | no | H | 13% float with 7% inflation and a 2023 insider cliff, plus a bankrupt lead investor (FTX Ventures) holding loc |
| 54 | HT | 1.5 | avoid | FA1,FA2,FA3,FA4 | -87.8% | -75.4% | no | M | Opaque change of control to About Capital/Justin Sun with 74M HT moved from official wallets, on top of a reve |
| 39 | XCN | 0.0 | avoid | FA1,FA2,FA3,FA4 | -73.6% | -94.4% | no | M | Opaque, insider-concentrated supply with thin real demand behind a $1B market cap. |

## v2 approximation on the same universe

v2 Quality rebuilt from the v1 cells plus mechanical data (survivorship from listing date and ATH cycle, P/S and revenue trend from DeFiLlama, S7 concentration unavailable and excluded), relative tiers (top quartile / second quartile / bottom half), gates optional, entry separate. Details in `scripts/backtest/analyze_v2.py`.

Rank correlation with return: **v2 0.204** vs v1 0.159.

| Basket | n | Median | Mean | Positive | Beat BTC |
|---|---|---|---|---|---|
| v2 Core (relative) | 15 | 132.8% | 147.5% | 93% | 0% |
| v2 Watch (relative) | 15 | 138.9% | 161.1% | 80% | 7% |
| v2 Avoid (relative) | 30 | 43.4% | 140.7% | 67% | 10% |
| v2 Core + gates | 7 | 110.3% | 149.9% | 100% | 0% |
| v2 Watch + gates | 5 | 18.5% | 81.0% | 80% | 0% |
| v2 Avoid + gates | 48 | 88.9% | 154.0% | 73% | 8% |
| E1 far from ATH | 49 | 69.1% | 162.6% | 78% | 8% |
| not E1 | 11 | 108.8% | 80.2% | 73% | 0% |
| E2 relative strength | 30 | 93.4% | 128.9% | 77% | 3% |
| not E2 | 30 | 51.3% | 166.0% | 77% | 10% |

| v2 cell | Pass n / median | Partial n / median | Fail n / median |
|---|---|---|---|
| S1 Survivorship | 18 / 94.2% | 0 / None% | 42 / 61.2% |
| S2 Value accrual | 8 / 158.9% | 46 / 93.4% | 6 / -18.7% |
| S3 Revenue level (P/S) | 4 / 246.7% | 9 / 108.8% | 47 / 57.2% |
| S4 Revenue trend | 12 / 136.8% | 7 / 193.4% | 41 / 49.2% |
| S5 Supply health | 16 / 116.5% | 16 / 122.5% | 28 / 20.0% |
| S6 Moat | 29 / 110.3% | 0 / None% | 31 / 57.2% |
| S8 Usage growth | 14 / 156.6% | 0 / None% | 46 / 63.1% |

| Token | v2 Q | v2 tier | gates | v1 | v1 tier | Return |
|---|---|---|---|---|---|---|
| ETH | 8.89 | core | - | 10.0 | core | 167.3% |
| BTC | 8.33 | core | - | 10.5 | core | 477.8% |
| MKR | 8.06 | core | - | 9.5 | watch | 110.3% |
| BNB | 8.06 | core | G1 | 8.5 | watch | 150.6% |
| XMR | 6.94 | core | - | 9.5 | watch | 56.8% |
| TRX | 6.94 | core | G1,G2 | 8.5 | watch | 358.7% |
| MATIC | 6.39 | core | G1 | 9.5 | watch | -49.4% |
| VET | 6.39 | core | G1 | 9.5 | watch | 132.8% |
| THETA | 6.39 | core | G1 | 9.5 | watch | 141.7% |
| XTZ | 6.39 | core | - | 9.0 | watch | 24.4% |
| MANA | 6.39 | core | G1 | 9.0 | watch | 7.0% |
| LTC | 6.11 | core | - | 8.5 | watch | 78.0% |
| AAVE | 5.83 | core | G1 | 9.0 | watch | 408.3% |
| SNX | 5.83 | core | G1 | 6.5 | avoid | 13.3% |
| UNI | 5.56 | core | - | 9.0 | watch | 134.7% |
| ETC | 5.56 | watch | - | 8.5 | watch | 26.6% |
| DOGE | 5.56 | watch | G3 | 7.0 | avoid | 295.7% |
| CAKE | 5.56 | watch | G1,G3 | 6.0 | avoid | -42.6% |
| FIL | 5.28 | watch | - | 6.5 | avoid | 18.5% |
| LINK | 5.28 | watch | G1 | 6.0 | avoid | 226.7% |
| ADA | 5.0 | watch | G1 | 7.0 | avoid | 193.4% |
| ZEC | 3.61 | watch | - | 6.5 | avoid | 18.0% |
| SHIB | 3.61 | watch | G3 | 5.5 | avoid | 138.9% |
| FTM | 3.33 | watch | G1 | 6.0 | avoid | 286.5% |
| ATOM | 3.06 | watch | - | 7.0 | avoid | -36.5% |
| XLM | 3.06 | watch | - | 5.5 | avoid | 378.5% |
| TON | 3.06 | watch | G1 | 5.0 | avoid | 220.6% |
| SAND | 3.06 | watch | G1 | 5.0 | avoid | -1.4% |
| XRP | 3.06 | watch | G3 | 4.0 | avoid | 636.5% |
| KCS | 3.06 | watch | G1 | 4.0 | avoid | 57.2% |
| HT | 3.06 | avoid | G1,G3 | 1.5 | avoid | -75.4% |
| BCH | 2.5 | avoid | - | 8.5 | watch | 349.4% |
| XEC | 2.5 | avoid | - | 8.0 | watch | 27.1% |
| NEO | 2.5 | avoid | G1 | 7.5 | avoid | 122.8% |
| DOT | 2.5 | avoid | - | 7.0 | avoid | 15.2% |
| BSV | 2.5 | avoid | G1,G3 | 6.0 | avoid | 49.2% |
| BTT | 2.5 | avoid | G1 | 6.0 | avoid | 69.1% |
| CHZ | 2.5 | avoid | G1 | 5.5 | avoid | -59.6% |
| CRO | 2.22 | avoid | G1 | 6.0 | avoid | 110.5% |
| NEAR | 2.22 | avoid | - | 5.5 | avoid | 154.4% |
| TWT | 2.22 | avoid | G1 | 5.5 | avoid | -39.5% |
| SOL | 2.22 | avoid | - | 4.5 | avoid | 1332.3% |
| QNT | 1.67 | avoid | - | 7.0 | avoid | 2.1% |
| MIOTA | 1.67 | avoid | G1 | 6.5 | avoid | 53.4% |
| LEO | 1.67 | avoid | G1 | 6.0 | avoid | 134.6% |
| FLOW | 1.67 | avoid | G1 | 6.0 | avoid | -38.9% |
| EOS | 1.67 | avoid | G1 | 5.0 | avoid | -11.2% |
| BIT | 1.67 | avoid | G1 | 5.0 | avoid | 1068.5% |
| LUNC | 1.67 | avoid | G1,G3 | 3.0 | avoid | -40.5% |
| HBAR | 1.39 | avoid | G1 | 5.5 | avoid | 513.2% |
| AXS | 1.39 | avoid | G1 | 4.5 | avoid | -12.6% |
| ICP | 1.39 | avoid | G1 | 3.5 | avoid | 158.8% |
| APT | 1.39 | avoid | G1 | 2.5 | avoid | 108.8% |
| ALGO | 0.83 | avoid | G1 | 5.5 | avoid | 37.5% |
| AVAX | 0.83 | avoid | - | 5.0 | avoid | 180.1% |
| EGLD | 0.83 | avoid | G1 | 5.0 | avoid | -24.0% |
| OKB | 0.83 | avoid | G1 | 4.0 | avoid | 169.4% |
| KLAY | 0.83 | avoid | G1 | 3.5 | avoid | 21.5% |
| APE | 0.0 | avoid | - | 4.5 | avoid | -62.2% |
| XCN | 0.0 | avoid | G1,G2,G3 | 0.0 | avoid | -94.4% |
