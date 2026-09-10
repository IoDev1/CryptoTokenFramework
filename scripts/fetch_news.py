#!/usr/bin/env python3
"""Free news feed per token via Google News RSS (no API key). Writes data/news.json.

Each item keeps its source and link so the page can show where a claim came from.
Query: "<project name>" crypto, last 14 days. Google News aggregates most crypto outlets
(CoinDesk, The Block, Cointelegraph, Decrypt, DL News) plus mainstream press.
"""
import json, pathlib, subprocess, sys, time, datetime, urllib.parse, xml.etree.ElementTree as ET, email.utils, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
market = json.loads((ROOT/"data"/"market.json").read_text())["tokens"]
# search names that disambiguate better than the CoinGecko name
QUERY = {"HBAR":"Hedera HBAR","STX":"Stacks STX bitcoin","RENDER":"Render Network RENDER","AAVE":"Aave","QNT":"Quant Network QNT",
 "SOL":"Solana","TAO":"Bittensor TAO","ETH":"Ethereum","SKY":"Sky Protocol SKY MakerDAO","XMR":"Monero","INJ":"Injective INJ",
 "NEAR":"NEAR Protocol","UNI":"Uniswap UNI","HYPE":"Hyperliquid HYPE","LINK":"Chainlink LINK","FET":"Fetch.ai FET ASI",
 "BNB":"BNB Chain Binance coin","Canton":"Canton Network CC token","AVAX":"Avalanche AVAX","KAS":"Kaspa KAS","VET":"VeChain VET",
 "TRX":"Tron TRX","CVX":"Convex Finance CVX","LTC":"Litecoin","SUI":"Sui blockchain SUI","SNX":"Synthetix SNX","ADA":"Cardano ADA",
 "DOT":"Polkadot DOT","POL":"Polygon POL","CRV":"Curve DAO CRV","Sonic":"Sonic Labs S token","ICP":"Internet Computer ICP",
 "YFI":"Yearn Finance YFI","COMP":"Compound COMP DeFi","DASH":"Dash cryptocurrency","JUP":"Jupiter JUP Solana","XRP":"XRP Ripple",
 "MORPHO":"Morpho MORPHO DeFi","SEI":"Sei Network SEI","ZEC":"Zcash ZEC","TON":"Toncoin TON Telegram","EGLD":"MultiversX EGLD",
 "WLD":"Worldcoin WLD","PLUME":"Plume Network PLUME","KAITO":"Kaito KAITO","VIRTUAL":"Virtuals Protocol VIRTUAL","BTC":"Bitcoin",
 "VVV":"Venice AI VVV token","PENDLE":"Pendle PENDLE","AERO":"Aerodrome AERO Base","RAY":"Raydium RAY","PUMP":"pump.fun PUMP token",
 "LDO":"Lido DAO LDO","ENA":"Ethena ENA USDe","ONDO":"Ondo Finance ONDO","LEO":"UNUS SED LEO Bitfinex","OKB":"OKB OKX",
 "ARB":"Arbitrum ARB","XLM":"Stellar XLM","BCH":"Bitcoin Cash","ETC":"Ethereum Classic","XTZ":"Tezos XTZ"}

def rss(q):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": f"{q} when:14d", "hl":"en-US","gl":"US","ceid":"US:en"})
    r = subprocess.run(["curl","-s","-m","30","-A","Mozilla/5.0",url], capture_output=True, text=True)
    if not r.stdout.strip(): return []
    try: root = ET.fromstring(r.stdout)
    except ET.ParseError: return []
    out = []
    for it in root.iter("item"):
        title = it.findtext("title") or ""; src = it.find("source"); srcname = src.text if src is not None else ""
        title = re.sub(r"\s+-\s+[^-]+$", "", title) if srcname and title.endswith(srcname) else title
        try: dt = email.utils.parsedate_to_datetime(it.findtext("pubDate")).strftime("%Y-%m-%d")
        except Exception: dt = ""
        out.append({"title": title.strip(), "source": srcname, "date": dt, "url": it.findtext("link") or ""})
    return out[:6]

# Public mode (default): the outlets' own RSS feeds, matched by token name/ticker. Headlines and
# links only. Google mode (--google) has better recall for small tokens but no commercial terms.
OUTLETS = {"CoinDesk":"https://www.coindesk.com/arc/outboundfeeds/rss","Cointelegraph":"https://cointelegraph.com/rss",
 "Decrypt":"https://decrypt.co/feed","The Block":"https://www.theblock.co/rss.xml","DL News":"https://www.dlnews.com/arc/outboundfeeds/rss/",
 "The Defiant":"https://thedefiant.io/api/feed","CryptoSlate":"https://cryptoslate.com/feed/","BeInCrypto":"https://beincrypto.com/feed/"}
# words that identify a token in a headline (case-insensitive, whole word); tickers alone are too ambiguous for some
MATCH = {"HBAR":["hedera","hbar"],"STX":["stacks","stx"],"RENDER":["render network","render token","rndr"],"AAVE":["aave"],"QNT":["quant network","qnt"],
 "SOL":["solana","sol"],"TAO":["bittensor","tao"],"ETH":["ethereum","ether"],"SKY":["sky protocol","makerdao","sky token"],"XMR":["monero","xmr"],
 "INJ":["injective"],"NEAR":["near protocol","near foundation"],"UNI":["uniswap"],"HYPE":["hyperliquid"],"LINK":["chainlink"],"FET":["fetch.ai","artificial superintelligence alliance","fet token"],
 "BNB":["bnb","binance coin","bnb chain"],"Canton":["canton network","canton coin"],"AVAX":["avalanche","avax"],"KAS":["kaspa"],"VET":["vechain"],
 "TRX":["tron","trx"],"CVX":["convex"],"LTC":["litecoin"],"SUI":["sui"],"SNX":["synthetix"],"ADA":["cardano","ada"],"DOT":["polkadot"],
 "POL":["polygon"],"CRV":["curve"],"Sonic":["sonic labs","sonic chain"],"ICP":["internet computer","dfinity","icp"],"YFI":["yearn"],"COMP":["compound finance","compound dao"],
 "DASH":["dash"],"JUP":["jupiter"],"XRP":["xrp","ripple"],"MORPHO":["morpho"],"SEI":["sei network","sei"],"ZEC":["zcash","zec"],"TON":["toncoin","ton blockchain","the open network"],
 "EGLD":["multiversx","egld"],"WLD":["worldcoin","world network","wld"],"PLUME":["plume"],"KAITO":["kaito"],"VIRTUAL":["virtuals"],"BTC":["bitcoin","btc"],
 "VVV":["venice"],"PENDLE":["pendle"],"AERO":["aerodrome"],"RAY":["raydium"],"PUMP":["pump.fun","pumpfun"],"LDO":["lido"],"ENA":["ethena"],"ONDO":["ondo"],
 "LEO":["bitfinex","leo token","unus sed leo"],"OKB":["okb","okx"],"ARB":["arbitrum"],"XLM":["stellar","xlm"],"BCH":["bitcoin cash"],"ETC":["ethereum classic"],"XTZ":["tezos"]}

def outlet_items():
    items = []; cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)
    for name, url in OUTLETS.items():
        r = subprocess.run(["curl","-sL","-m","30","-A","Mozilla/5.0",url], capture_output=True, text=True)
        try: root = ET.fromstring(r.stdout)
        except ET.ParseError: print(f"  {name}: parse error", file=sys.stderr); continue
        n = 0
        for it in root.iter("item"):
            try: dt = email.utils.parsedate_to_datetime(it.findtext("pubDate"))
            except Exception: continue
            if dt.tzinfo is None: dt = dt.replace(tzinfo=datetime.timezone.utc)
            if dt < cutoff: continue
            items.append({"title": (it.findtext("title") or "").strip(), "source": name, "date": dt.strftime("%Y-%m-%d"), "url": it.findtext("link") or "", "_dt": dt}); n += 1
        print(f"  {name}: {n} items", file=sys.stderr)
    return items

def match_outlets(items):
    out = {}
    for tk, words in MATCH.items():
        pat = re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")\b", re.I)
        hits = sorted([i for i in items if pat.search(i["title"])], key=lambda i: i["_dt"], reverse=True)[:6]
        out[tk] = [{k: v for k, v in i.items() if k != "_dt"} for i in hits]
    return out

mode = "google" if "--google" in sys.argv else "outlets"
prev = {}
try: prev = json.loads((ROOT/"data"/"news.json").read_text()).get("tokens", {})
except Exception: pass
if mode == "outlets":
    news = match_outlets(outlet_items()); source = "Outlet RSS (CoinDesk, Cointelegraph, Decrypt, The Block, DL News, The Defiant, CryptoSlate, BeInCrypto), last 14 days"
else:
    news = {}
    for tk in market:
        if tk not in QUERY: continue
        news[tk] = rss(QUERY[tk]); time.sleep(1.2)
    source = "Google News RSS, last 14 days"
tokens = {}
cutoff_day = (datetime.date.today() - datetime.timedelta(days=14)).isoformat()
for tk, items in news.items():
    old = prev.get(tk); old_items = (old.get("items") if isinstance(old, dict) else old) or []
    old_op = old.get("opinion") if isinstance(old, dict) else None
    # rolling store: union with what we already had (feeds only expose a few days), drop > 14 days
    merged = {i["url"]: i for i in old_items if i.get("date","") >= cutoff_day}
    for i in items: merged[i["url"]] = i
    keep = sorted(merged.values(), key=lambda i: i.get("date",""), reverse=True)[:8]
    # keep the last opinion until a new one is produced; the page shows its date and its own cited items
    tokens[tk] = {"items": keep, "opinion": old_op}
    print(f"{tk:8} {len(keep)} items ({len(items)} new)", file=sys.stderr)
(ROOT/"data"/"news.json").write_text(json.dumps({"as_of": datetime.date.today().isoformat(), "source": source, "tokens": tokens}, indent=1))
print("wrote data/news.json", file=sys.stderr)
