#!/usr/bin/env python3
"""Pull mechanical market data for the token list.

Sources (no API keys needed at this volume):
  - CoinGecko  /coins/list + /coins/markets  -> price, mcap, FDV, supply, ATH
  - DeFiLlama  /overview/fees                -> 30d fees and revenue, previous 30d, 1y

Writes data/market.json. Mechanical filter values derived:
  FA2 (low dilution)  = circulating / total (existing) supply >= 70%; unminted future supply reported as unminted_pct
  FC2 (far from ATH)  = price <= 25% of ATH
"""
import json, sys, time, urllib.request, urllib.parse, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "market.json"

# ticker -> (coingecko symbol, DeFiLlama matcher)
# matcher: ("chain", [names]) | ("parent", "parent#x") | ("protocol", [names]) | None
TOKENS = {
 "HBAR":("hbar",("chain",["Hedera"])),          "STX":("stx",("chain",["Stacks"])),
 "RENDER":("render",("protocol",["Render Network BME"])), "AAVE":("aave",("parent","parent#aave")),
 "QNT":("qnt",None),                             "SOL":("sol",("chain",["Solana"])),
 "TAO":("tao",None),                             "ETH":("eth",("chain",["Ethereum"])),
 "SKY":("sky",("parent","parent#maker")),        "XMR":("xmr",("chain",["Monero"])),
 "INJ":("inj",("chain",["Injective"])),          "NEAR":("near",("chain",["Near"])),
 "UNI":("uni",("parent","parent#uniswap")),      "HYPE":("hype",("parent","parent#hyperliquid")),
 "LINK":("link",("parent","parent#chainlink")),  "FET":("fet",None),
 "BNB":("bnb",("chain",["BSC","opBNB"])),        "Canton":("cc",("chain",["Canton"])),
 "AVAX":("avax",("chain",["Avalanche"])),        "KAS":("kas",None),
 "VET":("vet",None),                             "TRX":("trx",("chain",["Tron"])),
 "CVX":("cvx",("protocol",["Convex Finance"])),  "LTC":("ltc",None),
 "SUI":("sui",("chain",["Sui"])),                "SNX":("snx",("parent","parent#synthetix")),
 "ADA":("ada",("chain",["Cardano"])),            "DOT":("dot",("chain",["Polkadot"])),
 "POL":("pol",("chain",["Polygon","Polygon zkEVM"])), "CRV":("crv",("parent","parent#curve-finance")),
 "Sonic":("s",("chain",["Sonic"])),              "ICP":("icp",("chain",["ICP"])),
 "YFI":("yfi",("parent","parent#yearn")),        "COMP":("comp",("parent","parent#compound-finance")),
 "DASH":("dash",("chain",["Dash"])),             "JUP":("jup",("parent","parent#jupiter")),
 "XRP":("xrp",("protocol",["XRPL"])),            "MORPHO":("morpho",("parent","parent#morpho")),
 "SEI":("sei",("chain",["Sei"])),                "ZEC":("zec",("chain",["Zcash"])),
 "TON":("ton",("chain",["TON"])),                "EGLD":("egld",("chain",["MultiversX"])),
 "WLD":("wld",None),                             "PLUME":("plume",None),
 "KAITO":("kaito",None),                         "VIRTUAL":("virtual",("protocol",["Virtuals Protocol"])),
 "BTC":("btc",("chain",["Bitcoin"])),
 # --- added 2026-09-09: fee-capturing candidates + controls
 "VVV":("vvv",("protocol",["Venice"])),                             "PENDLE":("pendle",("parent","parent#pendle")),
 "AERO":("aero",("parent","parent#aerodrome")),  "RAY":("ray",("parent","parent#raydium")),
 "PUMP":("pump",("parent","parent#pump")),       "LDO":("ldo",("protocol",["Lido"])),
 "ENA":("ena",("parent","parent#ethena")),       "ONDO":("ondo",("parent","parent#ondo-finance")),
 "LEO":("leo",None),                             "OKB":("okb",("chain",["X Layer"])),
 "ARB":("arb",("parent","parent#arbitrum-foundation")),           "XLM":("xlm",("chain",["Stellar"])),
 "BCH":("bch",("chain",["Bitcoincash"])),        "ETC":("etc",None),
 "XTZ":("xtz",("chain",["Tezos"])),
}

# symbols shared by several coins: pin the CoinGecko id explicitly
ID_OVERRIDES = {"TON": "the-open-network", "VVV": "venice-token", "PUMP": "pump-fun", "ARB": "arbitrum", "LEO": "leo-token", "ETC": "ethereum-classic"}

def get(url, tries=5):
    """HTTP GET via curl (the python.org build on this Mac has no root certs)."""
    import subprocess
    for i in range(tries):
        r = subprocess.run(["curl","-s","-m","60","-w","\n%{http_code}","-H","Accept: application/json","-A","token-framework/0.1",url],
                           capture_output=True, text=True)
        body, _, code = r.stdout.rpartition("\n")
        if code == "200":
            return json.loads(body)
        if code == "429":
            wait = 20 * (i + 1); print(f"  429 rate limited, waiting {wait}s", file=sys.stderr); time.sleep(wait); continue
        raise RuntimeError(f"HTTP {code} for {url}: {body[:200]}")
    raise RuntimeError("gave up: " + url)

def coingecko():
    print("CoinGecko: coins/list", file=sys.stderr)
    coins = get("https://api.coingecko.com/api/v3/coins/list")
    wanted = {sym for sym, _ in TOKENS.values()}
    cands = [c["id"] for c in coins if c["symbol"].lower() in wanted and c["id"] not in ID_OVERRIDES.values()]
    cands += list(ID_OVERRIDES.values())
    print(f"  {len(cands)} candidate ids for {len(wanted)} symbols", file=sys.stderr)
    best = {}
    for i in range(0, len(cands), 250):
        ids = ",".join(cands[i:i+250])
        url = "https://api.coingecko.com/api/v3/coins/markets?" + urllib.parse.urlencode({"vs_currency":"usd","ids":ids,"per_page":250,"page":1})
        print(f"  markets batch {i//250+1}", file=sys.stderr)
        for m in get(url):
            sym = m["symbol"].lower(); mc = m.get("market_cap") or 0
            if m["id"] in ID_OVERRIDES.values():
                best["id:" + m["id"]] = m; continue
            if sym not in best or mc > (best[sym].get("market_cap") or 0):
                best[sym] = m
        time.sleep(3)
    return best

def llama():
    out = {}
    for dtype, key in (("dailyFees","fees"),("dailyRevenue","rev")):
        print(f"DeFiLlama: {dtype}", file=sys.stderr)
        d = get(f"https://api.llama.fi/overview/fees?excludeTotalDataChartBreakdown=true&excludeTotalDataChart=true&dataType={dtype}")
        prots = d["protocols"]
        for tk, (_, m) in TOKENS.items():
            if not m: continue
            kind, sel = m
            if kind == "chain":   rows = [p for p in prots if p.get("protocolType")=="chain" and p["name"] in sel]
            elif kind == "parent": rows = [p for p in prots if p.get("parentProtocol")==sel]
            else:                  rows = [p for p in prots if p["name"] in sel]
            def s(f): return sum((p.get(f) or 0) for p in rows) if rows else None
            o = out.setdefault(tk, {"llama_src": ", ".join(p["name"] for p in rows) or None})
            o[f"{key}30d"] = s("total30d"); o[f"{key}30d_prev"] = s("total60dto30d"); o[f"{key}1y"] = s("total1y")
    return out

def top100():
    print("CoinGecko: top 100 by market cap", file=sys.stderr)
    rows = get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1")
    return [{"sym": r["symbol"].upper(), "mcap": r.get("market_cap") or 0} for r in rows]

def main():
    cg = coingecko(); ll = llama(); ladder = top100()
    tokens = {}
    for tk, (sym, _) in TOKENS.items():
        m = cg.get("id:" + ID_OVERRIDES[tk]) if tk in ID_OVERRIDES else cg.get(sym)
        if not m:
            print(f"  !! no CoinGecko match for {tk}", file=sys.stderr); tokens[tk] = {"error":"no match"}; continue
        circ, total, mx = m.get("circulating_supply"), m.get("total_supply"), m.get("max_supply")
        # circulating vs EXISTING supply (locked tokens count as dilution); unminted future supply is
        # reported separately and judged as inflation (FB3), so PoW emission tails and stale max caps
        # (BNB's pre-burn 200M) do not masquerade as dilution.
        circ_pct = round(circ / total * 100, 1) if circ and total else (round(circ / mx * 100, 1) if circ and mx else None)
        unminted_pct = round((mx - total) / mx * 100, 1) if mx and total and mx > total else 0.0
        ath_chg = m.get("ath_change_percentage")
        row = {
            "id": m["id"], "name": m["name"], "rank": m.get("market_cap_rank"),
            "price": m.get("current_price"), "mcap": m.get("market_cap"), "fdv": m.get("fully_diluted_valuation"),
            "circ": circ, "total": total, "max": mx, "circ_pct": circ_pct, "unminted_pct": unminted_pct,
            "ath": m.get("ath"), "ath_date": (m.get("ath_date") or "")[:10], "ath_change_pct": round(ath_chg, 1) if ath_chg is not None else None,
            "chg_24h_pct": m.get("price_change_percentage_24h"),
            "fa2_live": (circ_pct >= 70) if circ_pct is not None else None,
            "fc2_live": (ath_chg <= -75) if ath_chg is not None else None,
        }
        row.update(ll.get(tk, {}))
        tokens[tk] = row
    OUT.write_text(json.dumps({"as_of": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                               "sources": ["CoinGecko /coins/markets", "DeFiLlama /overview/fees"], "top100": ladder,
                               "tokens": tokens}, indent=1))
    print(f"wrote {OUT}", file=sys.stderr)
    for tk, r in tokens.items():
        print(f"{tk:8} {str(r.get('id')):28} rank={r.get('rank')!s:5} price={r.get('price')!s:12} circ%={r.get('circ_pct')!s:6} athΔ={r.get('ath_change_pct')!s:7} fees30d={r.get('fees30d')!s:14} rev30d={r.get('rev30d')}")

if __name__ == "__main__":
    main()
