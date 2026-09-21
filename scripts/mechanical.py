#!/usr/bin/env python3
"""Mechanical v2 scoring: every cell that can be computed from data, no model.

Inputs: data/market.json (today), data/history/*/market.json (inflation), data/backtest/cmc_20221113.json
and cmc_20250112.json (survivorship), DeFiLlama TVL history (usage growth).
Output: data/mechanical.json with per-token cells, evidence lines, mechanical Quality (/6 available,
rescaled to /10), relative tier, entry E1/E2, and which cells are left for judgment (S2, S6, S7, gates).

Cells (RUBRIC_v2.md):
  S1 survivorship 2.0  listed before 2022 AND (new ATH after 2024-01 -> 1 | price at 2025-01-12 >= 70% of pre-2022 ATH -> 1 | >= 40% -> 0.5)
  S3 revenue level 1.0 P/S = FDV / (rev30d*12): < 50 -> 1, 50-200 -> 0.5; no revenue -> 0
  S4 revenue trend 1.0 rev30d >= $1M and vs prior 30d: up > 15% -> 1, within 15% -> 0.5, down -> 0; 1y leg: annualised rev30d >= 70% of rev1y
  S5 supply health 1.5 legs: circ >= 70% of existing; measured net inflation < 3%/yr; unlocks < 10% (provable only when circ >= 90%). 3 legs -> 1, 2 -> 0.5
  S8 usage growth 0.5  TVL now vs 365 days ago: up > 10% -> 1, within 10% -> 0.5, down -> 0; no TVL -> 0
  E1 >= 75% below ATH; E2 drawdown better than the universe median
"""
import json, glob, pathlib, datetime, subprocess, time, statistics, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
M = json.loads((ROOT/"data"/"market.json").read_text()); T = M["tokens"]
# listing year (first public trading), used for S1; static because free APIs do not expose it reliably
LISTED = {"HBAR":2019,"STX":2019,"RENDER":2020,"AAVE":2020,"QNT":2018,"SOL":2020,"TAO":2023,"ETH":2015,"SKY":2017,"XMR":2014,"INJ":2020,"NEAR":2020,
 "UNI":2020,"HYPE":2024,"LINK":2017,"FET":2019,"BNB":2017,"Canton":2025,"AVAX":2020,"KAS":2022,"VET":2018,"TRX":2017,"CVX":2021,"LTC":2013,"SUI":2023,
 "SNX":2018,"ADA":2017,"DOT":2020,"POL":2019,"CRV":2020,"Sonic":2019,"ICP":2021,"YFI":2020,"COMP":2020,"DASH":2014,"JUP":2024,"XRP":2013,"MORPHO":2024,
 "SEI":2023,"ZEC":2016,"TON":2021,"EGLD":2020,"WLD":2023,"PLUME":2025,"KAITO":2025,"VIRTUAL":2024,"BTC":2010,"VVV":2025,"PENDLE":2021,"AERO":2023,
 "RAY":2021,"PUMP":2025,"LDO":2021,"ENA":2024,"ONDO":2024,"LEO":2019,"OKB":2019,"ARB":2023,"XLM":2014,"BCH":2017,"ETC":2016,"XTZ":2018}
# renamed / migrated tokens: (symbol in the 2022 snapshot for the pre-2022 ATH, symbol in the 2025 snapshot, old units per new unit)
# their CoinGecko ATH date is the new token's, so the "new ATH after 2024" shortcut must not apply
RENAMED = {"POL": ("MATIC", "POL", 1.0), "SKY": ("MKR", "MKR", 1.0), "Sonic": ("FTM", "S", 1.0), "RENDER": ("RNDR", "RENDER", 1.0)}
CMC_SYM = {k: v[1] for k, v in RENAMED.items()}
# DeFiLlama TVL: ("chain", name) or ("protocol", slug)
TVL = {"HBAR":("chain","Hedera"),"STX":("chain","Stacks"),"AAVE":("protocol","aave"),"SOL":("chain","Solana"),"ETH":("chain","Ethereum"),"SKY":("protocol","sky-lending"),
 "INJ":("chain","Injective"),"NEAR":("chain","Near"),"UNI":("protocol","uniswap"),"HYPE":("chain","Hyperliquid L1"),"LINK":("protocol","chainlink"),"BNB":("chain","BSC"),
 "Canton":("chain","Canton"),"AVAX":("chain","Avalanche"),"TRX":("chain","Tron"),"CVX":("protocol","convex-finance"),"SUI":("chain","Sui"),"SNX":("protocol","synthetix"),
 "ADA":("chain","Cardano"),"DOT":("chain","Polkadot"),"POL":("chain","Polygon"),"CRV":("protocol","curve-dex"),"Sonic":("chain","Sonic"),"ICP":("chain","ICP"),
 "YFI":("protocol","yearn-finance"),"COMP":("protocol","compound-v3"),"JUP":("protocol","jupiter-aggregator"),"XRP":("chain","XRPL"),"MORPHO":("protocol","morpho-blue"),
 "SEI":("chain","Sei"),"TON":("chain","TON"),"EGLD":("chain","MultiversX"),"VIRTUAL":("protocol","virtuals-protocol"),"BTC":("chain","Bitcoin"),"PENDLE":("protocol","pendle"),
 "AERO":("protocol","aerodrome-slipstream"),"RAY":("protocol","raydium"),"PUMP":("protocol","pumpswap"),"LDO":("protocol","lido"),"ENA":("protocol","ethena-usde"),
 "ONDO":("protocol","ondo-finance"),"OKB":("chain","X Layer"),"ARB":("chain","Arbitrum"),"XLM":("chain","Stellar"),"BCH":("chain","Bitcoincash"),"ETC":("chain","Ethereum Classic"),"XTZ":("chain","Tezos"),"KAS":("chain","Kaspa"),"FET":None,"QNT":None,"TAO":None,"XMR":None,"VET":None,"LTC":None,"DASH":None,"ZEC":None,"WLD":None,"PLUME":("chain","Plume Mainnet"),"KAITO":None,"VVV":None,"LEO":None,"RENDER":None,"DOGE":("chain","Doge")}

def get(url):
    r = subprocess.run(["curl","-s","-m","40",url], capture_output=True, text=True)
    try: return json.loads(r.stdout)
    except Exception: return None

# ---------- inflation from daily snapshots (oldest vs newest, annualised)
hist = sorted(glob.glob(str(ROOT/"data"/"history"/"*"/"market.json")))
first = json.loads(pathlib.Path(hist[0]).read_text()) if hist else None
d0 = pathlib.Path(hist[0]).parent.name if hist else None; d1 = M["as_of"][:10]
days = (datetime.date.fromisoformat(d1) - datetime.date.fromisoformat(d0)).days if first else 0

# ---------- survivorship inputs
def cmc(name): return {r["symbol"]: r for r in json.loads((ROOT/"data"/"backtest"/name).read_text())["rows"]}
c22, c25 = cmc("cmc_20221113.json"), cmc("cmc_20250112.json")
bt = {t["tk"]: t for t in json.loads((ROOT/"data"/"backtest"/"universe.json").read_text())["tokens"]}

# ---------- TVL history
tvl_cache = {}
def tvl_series(kind, key):
    ck = (kind, key)
    if ck in tvl_cache: return tvl_cache[ck]
    if kind == "chain":
        d = get("https://api.llama.fi/v2/historicalChainTvl/" + key.replace(" ", "%20")); s = [(x["date"], x["tvl"]) for x in d] if isinstance(d, list) else []
    else:
        d = get("https://api.llama.fi/protocol/" + key); s = [(x["date"], x["totalLiquidityUSD"]) for x in (d or {}).get("tvl", [])] if isinstance(d, dict) else []
    tvl_cache[ck] = s; time.sleep(0.3); return s

dd = [t["ath_change_pct"] for t in T.values() if t.get("ath_change_pct") is not None]; dd_med = statistics.median(dd)
out = {}
for tk, m in T.items():
    if m.get("error"): continue
    cells, ev = {}, {}
    # S1
    ly = LISTED.get(tk); sym = CMC_SYM.get(tk, tk)
    ath_date = (m.get("ath_date") or "")
    if ly is None or ly >= 2022:
        cells["S1"] = 0.0; ev["S1"] = f"Listed {ly or 'unknown'}: has not been through a full bear market yet"
    elif tk in RENAMED:
        old, new, unit = RENAMED[tk]; pre = (bt.get(old) or {}).get("ath_pre"); p25 = (c25.get(new) or {}).get("price")
        if pre and p25:
            r = p25 * unit / pre; cells["S1"] = 1.0 if r >= 0.7 else 0.5 if r >= 0.4 else 0.0
            ev["S1"] = f"Listed {ly} as {old}; Jan-2025 price was {r*100:.0f}% of the pre-2022 {old} ATH ${pre:.4g}"
        elif ath_date >= "2024-01-01" and old == "RNDR":
            cells["S1"] = 1.0; ev["S1"] = f"Listed {ly} as {old}; new all-time high {ath_date[:10]} after the 2022 bear"
        else:
            cells["S1"] = 0.0; ev["S1"] = f"Listed {ly} as {old}; recovery vs the {old} ATH could not be verified"
    elif ath_date >= "2024-01-01":
        cells["S1"] = 1.0; ev["S1"] = f"Listed {ly}; new all-time high {ath_date[:10]} after the 2022 bear"
    else:
        pre = (bt.get(tk) or bt.get(sym or "") or {}).get("ath_pre") or (m.get("ath") if ath_date < "2022-01-01" else None)
        p25 = (c25.get(sym) or {}).get("price") if sym else None
        if pre and p25:
            r = p25 / pre; cells["S1"] = 1.0 if r >= 0.7 else 0.5 if r >= 0.4 else 0.0
            ev["S1"] = f"Listed {ly}; Jan-2025 price ${p25:.4g} was {r*100:.0f}% of the pre-2022 ATH ${pre:.4g}"
        else:
            cells["S1"] = 0.0; ev["S1"] = f"Listed {ly}; ATH {ath_date[:10]} not exceeded and no 2025 recovery price in the top 200"
    # S3
    fdv = m.get("fdv") or m.get("mcap"); rev = m.get("rev30d") or 0
    if rev > 0 and fdv:
        ps = fdv / (rev * 12); cells["S3"] = 1.0 if ps < 50 else 0.5 if ps < 200 else 0.0; ev["S3"] = f"FDV / annualised revenue = {ps:.0f}x (rev30d ${rev:,.0f})"
    else:
        cells["S3"] = 0.0; ev["S3"] = "No protocol revenue on DeFiLlama" if not m.get("llama_src") else f"Revenue $0 (source {m.get('llama_src')})"
    # S4
    prev = m.get("rev30d_prev") or 0; r1y = m.get("rev1y") or 0
    if rev >= 1e6 and prev > 0:
        ch = rev / prev - 1; yr_ok = (rev * 12) >= 0.7 * r1y if r1y else True
        base = 1.0 if ch > 0.15 else 0.5 if ch >= -0.15 else 0.0
        cells["S4"] = base if yr_ok else min(base, 0.5); ev["S4"] = f"rev30d ${rev:,.0f} vs prior ${prev:,.0f} ({ch*100:+.0f}%); annualised {'>=' if yr_ok else '<'} 70% of 1y ${r1y:,.0f}"
    else:
        cells["S4"] = 0.0; ev["S4"] = f"Revenue ${rev:,.0f}/30d below the $1M materiality bar" if rev else "No revenue data"
    # S5
    legs = []; circ = m.get("circ_pct")
    legs.append(("circ >= 70%", circ is not None and circ >= 70, f"{circ}% of existing supply circulating" if circ is not None else "no supply data"))
    infl = None
    if first and days >= 7 and tk in first["tokens"] and first["tokens"][tk].get("circ") and m.get("circ"):
        infl = (m["circ"] / first["tokens"][tk]["circ"] - 1) * 365 / days * 100
    legs.append(("inflation < 3%/yr", infl is not None and infl < 3, f"measured {infl:+.1f}%/yr from {days} days of snapshots" if infl is not None else "not enough snapshots yet"))
    legs.append(("unlocks < 10%", circ is not None and circ >= 90, "provable: <10% of supply is non-circulating" if circ is not None and circ >= 90 else "unlock schedule not verified mechanically"))
    n = sum(1 for _, ok, _ in legs if ok); cells["S5"] = 1.0 if n == 3 else 0.5 if n == 2 else 0.0
    ev["S5"] = "; ".join(f"{'ok' if ok else 'fail'} {name} ({why})" for name, ok, why in legs)
    m["inflation_pct_yr"] = round(infl, 2) if infl is not None else None
    # S8
    tv = TVL.get(tk); series = tvl_series(*tv) if tv else []
    if series and len(series) > 30:
        now_ts = series[-1][0]; past = [v for ts, v in series if ts <= now_ts - 365*86400]
        if past and past[-1] > 0:
            g = series[-1][1] / past[-1] - 1; cells["S8"] = 1.0 if g > 0.10 else 0.5 if g >= -0.10 else 0.0
            ev["S8"] = f"TVL ${series[-1][1]/1e6:,.0f}M vs ${past[-1]/1e6:,.0f}M a year ago ({g*100:+.0f}%), DeFiLlama {tv[1]}"
        else: cells["S8"] = 0.0; ev["S8"] = f"TVL series shorter than a year ({tv[1]})"
    else: cells["S8"] = 0.0; ev["S8"] = "No TVL series on DeFiLlama for this token"
    # entry
    a = m.get("ath_change_pct")
    e1 = int(a is not None and a <= -75); e2 = int(a is not None and a > dd_med)
    q = (2.0*cells["S1"] + 1.0*cells["S3"] + 1.0*cells["S4"] + 1.5*cells["S5"] + 0.5*cells["S8"]) / 6.0 * 10
    out[tk] = {"cells": cells, "evidence": ev, "q_mech": round(q, 1), "entry": {"E1": e1, "E2": e2},
               "entry_evidence": {"E1": f"{a}% from ATH ({'>=' if e1 else '<'} 75% down)", "E2": f"drawdown {a}% vs universe median {dd_med:.1f}% ({'better' if e2 else 'worse'})"},
               "judgment_cells": ["S2 value accrual", "S6 moat", "S7 holder concentration", "G1-G5 gates"]}
ranked = sorted(out, key=lambda k: -out[k]["q_mech"]); n = len(ranked)
for i, tk in enumerate(ranked): out[tk]["tier"] = "core" if i < n//4 else "watch" if i < n//2 else "avoid"; out[tk]["rank"] = i + 1
(ROOT/"data"/"mechanical.json").write_text(json.dumps({"as_of": M["as_of"], "rubric": "research/RUBRIC_v2.md", "available_weight": 6.0, "total_weight": 10.0,
    "inflation_window_days": days, "drawdown_median": dd_med, "tokens": out}, indent=1))
(ROOT/"data"/"market.json").write_text(json.dumps(M, indent=1))
print(f"{n} tokens; inflation window {days}d; drawdown median {dd_med:.1f}%", file=sys.stderr)
for tk in ranked: c = out[tk]["cells"]; print(f'{tk:8} Q {out[tk]["q_mech"]:4} {out[tk]["tier"]:5} S1 {c["S1"]} S3 {c["S3"]} S4 {c["S4"]} S5 {c["S5"]} S8 {c["S8"]}  E{out[tk]["entry"]["E1"]}{out[tk]["entry"]["E2"]}  infl {T[tk].get("inflation_pct_yr")}')
