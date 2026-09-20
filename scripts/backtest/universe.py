#!/usr/bin/env python3
"""Universe for the 2022 backtest: top 60 by market cap on 2022-11-13 (CMC snapshot), excluding
stablecoins, wrapped/staked wrappers. End prices from the 2025-01-12 snapshot matched by CMC id.
Writes data/backtest/universe.json."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; B = ROOT/"data"/"backtest"
start = json.loads((B/"cmc_20221113.json").read_text())["rows"]; end = {r["id"]: r for r in json.loads((B/"cmc_20250112.json").read_text())["rows"]}
EXCLUDE_TAGS = {"stablecoin","stablecoin-asset-backed","stablecoin-algorithmically-stabilized","wrapped-tokens","liquid-staking-derivatives"}
EXCLUDE_SYM = {"USDT","USDC","BUSD","DAI","TUSD","USDP","USDD","GUSD","FRAX","USDN","WBTC","STETH","HBTC","WTRX","BTCB","CETH","CDAI","CUSDC","FEI","LUSD","XAUT","PAXG"}
uni = []
for r in start:
    if r["symbol"] in EXCLUDE_SYM or (set(r.get("tags") or []) & EXCLUDE_TAGS): continue
    e = end.get(r["id"])
    uni.append({"tk": r["symbol"], "name": r["name"], "cmc_id": r["id"], "slug": r["slug"], "rank_2022": r["rank"],
                "price_2022": r["price"], "mcap_2022": r["mcap"], "circ_2022": r["circ"], "total_2022": r["total"], "max_2022": r["max"],
                "circ_pct_2022": round(r["circ"]/r["total"]*100,1) if r["circ"] and r["total"] else None,
                "price_2025": e["price"] if e else None, "rank_2025": e["rank"] if e else None, "mcap_2025": e["mcap"] if e else None})
    if len(uni) == 60: break
(B/"universe.json").write_text(json.dumps({"start":"2022-11-13","end":"2025-01-12","tokens":uni}, indent=1))
print(len(uni), "tokens;", "missing 2025 price:", [t["tk"] for t in uni if t["price_2025"] is None])
for t in uni: print(f'{t["rank_2022"]:3} {t["tk"]:6} {t["name"][:22]:22} ${t["price_2022"]:<12.6g} -> {("$%.6g" % t["price_2025"]) if t["price_2025"] else "?":12} circ {t["circ_pct_2022"]}%')
