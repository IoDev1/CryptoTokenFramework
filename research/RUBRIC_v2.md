# Research rubric v2 — gates, Quality, Entry

Apply the SAME standard to every token. Unknown or unverifiable = 0 (or gate fail), never a pass.
Every cell needs one line of evidence with a dated source. Market numbers (price, circulating %,
distance from ATH, DeFiLlama fees and revenue) are supplied; use them, do not re-estimate.
Block subsidy, hashrate and miner revenue are emission, not demand. Company revenue is not the
token's revenue.

## Gates (pass/fail). Reported separately; the page decides whether they exclude.

**G1 Not ruggable.** PASS if no freeze / mint / blacklist authority over the token and no
upgradeable core contract or validator set controlled by a small multisig or the foundation.
Permissionless L1s pass. A chain whose validator set is foundation-run, or that has frozen
balances before, FAILS.

**G2 No deceptive insider selling.** FAIL only on UNDISCLOSED or deceptive selling in the last 24
months: unreported transfers from team/foundation wallets to exchanges, treasury reports that
contradict on-chain flows, founder loans against the token that were liquidated, sales timed
against public denials. Scheduled, disclosed foundation or investor sales PASS even if large; they
are handled by S5.

**G3 Stewardship.** PASS if EITHER (a) identifiable, accountable core leadership with a multi-year
record still shipping, OR (b) proven leaderless decentralization: >= 2 independent client or dev
teams, multi-year continuity, no single point of failure. FAIL if key founders left unreplaced,
leadership is under prosecution or sanction that impairs the project, or development has stalled.

**G4 Treasury runway.** PASS if the foundation or lab has >= 3 years of runway at current burn in
NON-native assets (stables, BTC, ETH) per a disclosed report or verifiable on-chain holdings.
Unknown = FAIL. Leaderless projects with no treasury (BTC) PASS: there is nothing to run out of.

**G5 Listing and enforcement.** PASS if listed on >= 2 of Coinbase, Kraken, Binance and there is
no active regulatory enforcement action alleging the token itself is a security. FAIL otherwise.

## Quality (/10). Each cell is 1 / 0.5 / 0 times its weight.

| ID | W | Filter | 1 (pass) | 0.5 (partial) |
|----|---|--------|----------|---------------|
| S1 | 2.0 | Prior-cycle survivorship | Lived through >= 1 full bear (listed >= 4 years before the current bear) and set a new USD ATH in the following cycle, or reached >= 70% of the prior ATH | Recovered 40–70% of prior ATH |
| S2 | 1.5 | Value accrual | Fees reach holders today: burn, buyback, fee-funded staking, or mandatory gas with fee burn | Governance-only but protocol revenue exists and a fee switch is live or scheduled with a date |
| S3 | 1.0 | Revenue level | Annualised protocol revenue (supplied rev30d x 12) / FDV: P/S < 50 | P/S 50–200 |
| S4 | 1.0 | Revenue trend | rev30d vs prior 30d up > 15% AND 1y trend not clearly down | Within +/- 15% |
| S5 | 1.5 | Supply health | All three: circulating >= 70% of existing supply, next-12-month unlocks < 10% of circulating, net inflation < 3%/yr | Two of three |
| S6 | 1.5 | Moat | Top-2 in category by a usage metric (fees, TVL, tx, active users) with >= 2 years' lead, or structural lock-in | Top-5 |
| S7 | 1.0 | Holder concentration | Top-10 non-exchange, non-contract wallets hold < 40% of supply | 40–60% |
| S8 | 0.5 | Usage growth | Active addresses, TVL or fees up over 12 months (measured, not narrative) | Flat |

Revenue cells (S3, S4) use the supplied DeFiLlama figures; if none exist, they are 0. S5 uses the
supplied circulating %; unlock and inflation legs need a dated source.

## Entry (/4). Reported separately. Never enters Quality.

| ID | W | Filter |
|----|---|--------|
| E1 | 1 | >= 75% below USD ATH (supplied; mechanical) |
| E2 | 1 | Relative strength: drawdown from ATH better than the median of the scored universe (supplied; mechanical) |
| E3 | 1 | FDV / annualised revenue at or below its own prior-cycle low, per a dated source |
| E4 | 1 | Known risks public for >= 6 months and no binary event (lawsuit ruling, cliff unlock > 10% of circulating, fork, delisting) inside the next 6 months |

## Output

Return STRICT JSON, no prose:
{
 "tokens": {
  "TICKER": {
   "gates": {"G1": 0|1, "G2": 0|1, "G3": 0|1, "G4": 0|1, "G5": 0|1},
   "quality": {"S1": 0|0.5|1, "S2": ..., "S3": ..., "S4": ..., "S5": ..., "S6": ..., "S7": ..., "S8": ...},
   "entry": {"E1": 0|1, "E2": 0|1, "E3": 0|1, "E4": 0|1},
   "evidence": {"G1": "...", ..., "E4": "..."},        // one line each, <= 140 chars
   "key_risk": "one line, the strongest bear case",
   "confidence": "H|M|L",
   "sources": ["url", ...]                              // 3-8 urls actually consulted
  }
 }
}
