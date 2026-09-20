#!/usr/bin/env python3
"""Enrich data/backtest/universe.json with:
  - ath_pre: all-time high before 2022-11-13 (CoinGecko ATH if its date is before the cutoff, else Yahoo
    daily history 2013..cutoff, accepted only if Yahoo's 2022-11-13 close matches the CMC price within 15%)
  - fees30d / fees30d_prev / fees1y as of 2022-11-15 from DeFiLlama historical charts (protocol or chain slug)
  - price_2025 for successors / dropouts (MNT for BIT at 3.14:1, KAIA for KLAY 1:1, Yahoo verified for the rest)
"""
import json, pathlib, subprocess, time, datetime, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]; B = ROOT/"data"/"backtest"
U = json.loads((B/"universe.json").read_text()); T = U["tokens"]
CUT = datetime.date(2022,11,13); CUT_TS = int(datetime.datetime(2022,11,15,tzinfo=datetime.timezone.utc).timestamp())
def get(url, tries=4):
    for i in range(tries):
        r = subprocess.run(["curl","-sL","-m","60","-A","Mozilla/5.0","-w","\n%{http_code}",url], capture_output=True, text=True)
        body,_,code = r.stdout.rpartition("\n")
        if code=="200":
            try: return json.loads(body)
            except Exception: return None
        if code=="429": time.sleep(25*(i+1)); continue
        return None
    return None

# ---- 1. CoinGecko ATH (ids pinned for collisions)
CG = {"BTC":"bitcoin","ETH":"ethereum","BNB":"binancecoin","XRP":"ripple","ADA":"cardano","DOGE":"dogecoin","MATIC":"polygon-ecosystem-token","DOT":"polkadot","SHIB":"shiba-inu","SOL":"solana","TRX":"tron","UNI":"uniswap","LTC":"litecoin","AVAX":"avalanche-2","LEO":"leo-token","LINK":"chainlink","ATOM":"cosmos","ETC":"ethereum-classic","XMR":"monero","XLM":"stellar","TON":"the-open-network","BCH":"bitcoin-cash","ALGO":"algorand","NEAR":"near","CRO":"crypto-com-chain","VET":"vechain","FIL":"filecoin","QNT":"quant-network","FLOW":"flow","CHZ":"chiliz","LUNC":"terra-luna","ICP":"internet-computer","OKB":"okb","XCN":"chain-2","HBAR":"hedera-hashgraph","EGLD":"elrond-erd-2","EOS":"eos","XTZ":"tezos","SAND":"the-sandbox","APE":"apecoin","THETA":"theta-token","MANA":"decentraland","AAVE":"aave","TWT":"trust-wallet-token","BSV":"bitcoin-cash-sv","HT":"huobi-token","KCS":"kucoin-shares","AXS":"axie-infinity","MKR":"maker","BTT":"bittorrent","BIT":"mantle","ZEC":"zcash","MIOTA":"iota","CAKE":"pancakeswap-token","APT":"aptos","XEC":"ecash","KLAY":"kaia","SNX":"havven","NEO":"neo","FTM":"fantom"}
ids = ",".join(CG.values())
print("CoinGecko ATH...", file=sys.stderr)
cg = {}
for chunk in (list(CG.values())[:30], list(CG.values())[30:]):
    for m in get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=100&ids="+",".join(chunk)) or []: cg[m["id"]] = m
    time.sleep(3)
# ---- 2. Yahoo history (pre-cutoff max) with verification
YH = {"BTC":"BTC-USD","ETH":"ETH-USD","BNB":"BNB-USD","XRP":"XRP-USD","ADA":"ADA-USD","DOGE":"DOGE-USD","DOT":"DOT-USD","SOL":"SOL-USD","TRX":"TRX-USD","UNI":"UNI7083-USD","LTC":"LTC-USD","AVAX":"AVAX-USD","LEO":"LEO-USD","LINK":"LINK-USD","XMR":"XMR-USD","XLM":"XLM-USD","TON":"TON11419-USD","BCH":"BCH-USD","OKB":"OKB-USD","HBAR":"HBAR-USD","XCN":"XCN18679-USD","HT":"HT-USD","AAVE":"AAVE-USD","MKR":"MKR-USD","NEO":"NEO-USD","ICP":"ICP-USD","NEAR":"NEAR-USD","CRO":"CRO-USD","AXS":"AXS-USD","MIOTA":"MIOTA-USD","XEC":"XEC-USD","BTT":"BTT-USD","THETA":"THETA-USD","SHIB":"SHIB-USD","MATIC":"MATIC-USD","ATOM":"ATOM-USD","ETC":"ETC-USD","ALGO":"ALGO-USD","VET":"VET-USD","FIL":"FIL-USD","QNT":"QNT-USD","FLOW":"FLOW-USD","CHZ":"CHZ-USD","LUNC":"LUNC-USD","EGLD":"EGLD-USD","EOS":"EOS-USD","XTZ":"XTZ-USD","SAND":"SAND-USD","APE":"APE18876-USD","MANA":"MANA-USD","TWT":"TWT-USD","BSV":"BSV-USD","KCS":"KCS-USD","BIT":"BIT11221-USD","ZEC":"ZEC-USD","CAKE":"CAKE-USD","APT":"APT21794-USD","KLAY":"KLAY-USD","SNX":"SNX-USD","FTM":"FTM-USD"}
def yahoo(sym, p1, p2):
    d = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1={p1}&period2={p2}&interval=1d")
    try: r = d["chart"]["result"][0]; return list(zip(r["timestamp"], r["indicators"]["quote"][0]["close"]))
    except Exception: return None
P_2013 = 1356998400; P_CUT = CUT_TS; P_END1 = 1736553600; P_END2 = 1736812800  # 2025-01-11..14
print("Yahoo...", file=sys.stderr)
for t in T:
    tk = t["tk"]; m = cg.get(CG.get(tk,""), {})
    t["cg_id"] = CG.get(tk); t["ath_now"] = m.get("ath"); t["ath_now_date"] = (m.get("ath_date") or "")[:10]
    t["ath_pre"] = None; t["ath_src"] = None
    if t["ath_now"] and t["ath_now_date"] and t["ath_now_date"] < "2022-11-13":
        t["ath_pre"] = t["ath_now"]; t["ath_src"] = "coingecko (ATH before cutoff)"
    need_end = t["price_2025"] is None and tk not in ("BIT","KLAY")
    if (t["ath_pre"] is None or need_end) and tk in YH:
        series = yahoo(YH[tk], P_2013, P_END2 + 86400*3); time.sleep(0.6)
        if series:
            pre = [(ts,c) for ts,c in series if c and ts < P_CUT]
            near = [c for ts,c in series if c and abs(ts - (P_CUT-86400*2)) < 86400*2]
            ok = bool(near) and abs(near[0]/t["price_2022"] - 1) < 0.15
            if ok:
                if t["ath_pre"] is None and pre: t["ath_pre"] = max(c for _,c in pre); t["ath_src"] = f"yahoo {YH[tk]} (verified vs CMC)"
                if need_end:
                    endc = [c for ts,c in series if c and P_END1 <= ts <= P_END2]
                    if endc: t["price_2025"] = endc[0]; t["price_2025_src"] = f"yahoo {YH[tk]}"
            else: t["yahoo_reject"] = f"{YH[tk]} close {near[0] if near else None} vs CMC {t['price_2022']}"
    t["ath_change_pct_2022"] = round((t["price_2022"]/t["ath_pre"] - 1)*100, 1) if t.get("ath_pre") else None
# successors from the 2025 snapshot
end = {r["symbol"]: r for r in json.loads((B/"cmc_20250112.json").read_text())["rows"]}
for t in T:
    if t["tk"]=="BIT" and end.get("MNT"): t["price_2025"] = end["MNT"]["price"]*3.14; t["price_2025_src"] = "MNT x 3.14 (BitDAO->Mantle conversion)"
    if t["tk"]=="KLAY" and end.get("KAIA"): t["price_2025"] = end["KAIA"]["price"]; t["price_2025_src"] = "KAIA 1:1 (Klaytn->Kaia)"
# ---- 3. DeFiLlama historical fees as of 2022-11-15
LL = {"ETH":"ethereum","BNB":"bsc","SOL":"solana","TRX":"tron","AVAX":"avalanche","MATIC":"polygon","FTM":"fantom","NEAR":"near","ATOM":"cosmoshub","DOT":"polkadot","ADA":"cardano","XTZ":"tezos","ALGO":"algorand","EOS":"eos","FIL":"filecoin","FLOW":"flow","HBAR":"hedera","ICP":"icp","EGLD":"multiversx","KLAY":"klaytn","CRO":"cronos","XLM":"stellar","BTC":"bitcoin","LTC":"litecoin","DOGE":"dogecoin","BCH":"bitcoincash","XMR":"monero","ZEC":"zcash","ETC":"ethereum-classic","BSV":"bitcoin-sv","APT":"aptos","THETA":"theta",
      "UNI":"uniswap","AAVE":"aave","MKR":"makerdao","CAKE":"pancakeswap","SNX":"synthetix","LINK":"chainlink","AXS":"axie-infinity","SAND":"the-sandbox","MANA":"decentraland","APE":"apecoin","QNT":"quant","VET":"vechain","CHZ":"chiliz","SHIB":"shibaswap","OKB":"okb","LEO":"bitfinex","KCS":"kucoin","HT":"huobi","TWT":"trust-wallet","BTT":"bittorrent","XEC":"ecash","MIOTA":"iota","NEO":"neo","TON":"ton","LUNC":"terra-classic","XCN":"chain","BIT":"bitdao"}
print("DeFiLlama...", file=sys.stderr)
for t in T:
    slug = LL.get(t["tk"]); t["llama_slug"] = slug; t["fees30d"] = t["fees30d_prev"] = t["fees1y"] = None
    if not slug: continue
    d = get(f"https://api.llama.fi/summary/fees/{slug}?dataType=dailyFees"); time.sleep(0.4)
    ch = (d or {}).get("totalDataChart") or []
    if not ch: t["llama_slug"] = None; continue
    w = lambda a,b: round(sum(v for ts,v in ch if a<=ts<b))
    t["fees30d"] = w(CUT_TS-30*86400, CUT_TS); t["fees30d_prev"] = w(CUT_TS-60*86400, CUT_TS-30*86400); t["fees1y"] = w(CUT_TS-365*86400, CUT_TS)
(B/"universe.json").write_text(json.dumps(U, indent=1))
for t in T: print(f'{t["tk"]:6} ath_pre {str(t.get("ath_pre"))[:10]:10} {t.get("ath_change_pct_2022")!s:7} src={str(t.get("ath_src"))[:34]:34} p2025 {str(t.get("price_2025"))[:10]:10} fees30d {t.get("fees30d")} llama={t.get("llama_slug")} {t.get("yahoo_reject","")}')
