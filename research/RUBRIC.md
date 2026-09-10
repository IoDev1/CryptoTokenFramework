# Research rubric — 13 filters, strict definitions

Date of research: 2026-09-09. Apply the SAME standard to every token. When evidence is missing or
unverifiable, the cell is a FAIL (0), never a pass. Every cell needs one line of evidence.
Market numbers (price, circulating %, distance from ATH, DeFiLlama fees/revenue) are supplied to
you from CoinGecko and DeFiLlama pulled today; use them, do not re-estimate them.

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

## Output

Return STRICT JSON, no prose, matching:
{
 "tokens": {
  "TICKER": {
   "bits": [FA1,FA2,FA3,FA4,FB1,FB2,FB3,FC1,FC2,FC3,FC4,FC5,FC6],   // 13 integers, 0 or 1
   "evidence": {"FA1":"...", ..., "FC6":"..."},                     // one line each, <= 140 chars
   "key_risk": "one line, the strongest bear case",
   "confidence": "H|M|L",
   "sources": ["url", "url"]                                        // 3-8 urls actually consulted
  }
 }
}
