# Backtest rubric — score as of 2022-11-15

You are scoring tokens AS OF 15 NOVEMBER 2022, four days after FTX filed for bankruptcy. Apply the
13 filters from RUBRIC.md (reproduced below) exactly as written, with one change of date: every
"today", "last 30 days", "last 12 months", "next 6 months" is relative to 2022-11-15.

## Information cutoff, strictly enforced

- Use ONLY facts that were public on or before 2022-11-15. Search with date-restricted queries
  (e.g. add "2022" or "before:2022-11-16"), prefer sources dated 2021-2022, and cite only sources
  published on or before the cutoff. If a source is dated after the cutoff, do not use it.
- You know what happened afterwards. You must not let that leak. Concretely: do not score a token
  on outcomes (price recovery, later collapses, later lawsuits, later unlocks, later ETFs, later
  rebrands). Score on what a careful analyst could verify in November 2022.
- Unknown or unverifiable as of the cutoff = 0, never a pass.
- The supplied market numbers (price, circulating %, distance from ATH, DeFiLlama fees) are exact
  as of the cutoff. Use them; do not re-estimate. FC2 is mechanical: pass only if <= -75% from ATH.
  Where DeFiLlama has "no data" for a chain or protocol that clearly had on-chain fees in 2022
  (e.g. Litecoin, Dogecoin, XRP), FB2 still needs verifiable paid demand >= ~$1M/30d from a
  pre-cutoff source; otherwise fail.
- Block subsidy, hashrate and miner revenue are emission, not demand. Company revenue is not the
  token's revenue. FC5 requires material revenue (>= $1M per 30 days) or it fails.

## Output

Same schema as RUBRIC.md: strict JSON, {"tokens": {"TICKER": {"bits": [13 ints], "evidence": {FA1..FC6, one
line each, <= 140 chars, each line should name the pre-cutoff fact}, "key_risk": "...", "confidence": "H|M|L",
"sources": [3-8 urls published on or before 2022-11-15]}}}. Ticker keys exactly as in the input.

---
## Tier A — Dealbreakers

**FA1 Team doesn't dump.** PASS if, over the last 24 months, foundation + labs + founders + top
insiders have NOT net-sold or unlocked-and-sold more than ~2% of circulating supply per year into
the market, and there is no documented pattern of treasury dumps timed to pumps. Routine small
foundation sales for operations (<1%/yr) are a pass. FAIL on documented insider dumping, large
undisclosed transfers to exchanges, or founder loans-against-token that were liquidated.

**FA2 Low dilution.** PASS if circulating / total EXISTING supply >= 70% (locked, vesting and
escrowed tokens are dilution) AND net inflation from future emissions is not above ~5%/yr. An
uncapped token with net inflation <= 3%/yr (after burns) passes on the inflation leg. Unminted
future supply (PoW emission tails, "max supply" caps) is judged as an inflation RATE, not as
dilution: a stale max-supply cap (e.g. BNB's pre-burn 200M) must not fail a deflationary token.
A token showing "100% circulating" only because it has no cap must be judged on inflation.

**FA3 Competitive moat.** PASS if the project is top-2 in its category by a usage metric (fees,
TVL, transactions, active users, hashrate, enterprise integrations) with a lead that has held
for >= 2 years, or has a structural lock-in (network effects, regulatory positioning, exclusive
integrations). FAIL if it is one of many interchangeable competitors or has lost share steadily.

**FA4 Team is known & solid.** PASS if EITHER (a) identifiable, accountable core leadership with a
multi-year track record still actively shipping, OR (b) proven leaderless decentralization: >= 2
independent client/dev teams, multi-year continuity, no single point of failure (the Bitcoin /
Monero clause). FAIL if key founders left and were not replaced, leadership is under
prosecution/sanction that impairs the project, or development has visibly stalled.

## Tier B — Foundation

**FB1 Token required for usage.** PASS if the core use of the network is impossible without the
token: gas, staking that secures the chain, or fees payable only in the token. Governance-only
tokens FAIL even if the protocol is great. A fee switch or buyback that returns value to holders
counts as a PARTIAL (score 0.5 — encode as 1 only if fees actually flow to the token today).

**FB2 Real revenue / demand.** PASS if verifiable protocol/chain fees >= ~$1M in the last 30 days
(DeFiLlama figure supplied) OR verifiable organic demand of comparable scale that users PAY for
(enterprise transaction volume with named counterparties, fee-paying usage off DeFiLlama). Block
subsidy / miner revenue / hashrate is EMISSION, not demand, and never satisfies FB2. FAIL if fees
are trivial, no data exists, or "revenue" belongs to a company rather than the protocol (Ripple's
revenue is not XRP's).

**FB3 Effective supply dynamics.** PASS if net inflation <= 3%/yr (after burns / buybacks) AND no
cliff unlock > 10% of circulating supply in the next 12 months AND emissions are on a fixed,
published schedule. FAIL if inflation is high, unlocks are large, or the schedule can be changed
by a small group.

## Tier C — Context

**FC1 Can't be rugged.** PASS if there is no freeze / mint / blacklist authority and no
upgradeable contract or validator set controlled by a small multisig or the foundation.
Permissionless L1s pass. A chain whose validator set is foundation-controlled or that has
frozen balances before FAILS.

**FC2 Far from ATH.** Mechanical: PASS if price is >= 75% below the USD all-time high (supplied).
Do not override.

**FC3 Growing narrative.** PASS if a measurable usage metric (active addresses, TVL, fees,
developers) is UP over the last 12 months, or the sector has a demonstrable, funded tailwind
(not just Twitter attention). FAIL if usage is flat or down.

**FC4 Known risks priced in.** PASS if the main risks have been public for >= 6 months and there
is no pending binary event (unresolved lawsuit, large cliff unlock, fork, delisting) inside the
next 6 months. FAIL if a known negative event is still ahead.

**FC5 Revenue trajectory.** PASS if 30-day revenue vs prior 30 days is flat-to-up AND the 1-year
trend is not clearly down (figures supplied) AND the revenue is material (>= $1M fees or revenue
in 30 days, i.e. FB2-scale). A +14% move on $8k/month is noise, not a trajectory. If no revenue
data exists, FAIL.

**FC6 Upcoming catalysts.** PASS only for a concrete, dated catalyst in the next 6 months
(mainnet upgrade with a date, ETF decision, tokenomics change with a vote passed, major
listing/integration announced). Vague roadmap items FAIL.

