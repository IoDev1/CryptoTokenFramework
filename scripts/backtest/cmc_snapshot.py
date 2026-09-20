#!/usr/bin/env python3
"""Extract a CoinMarketCap weekly historical snapshot (Sundays) into JSON.
usage: cmc_snapshot.py YYYYMMDD -> data/backtest/cmc_YYYYMMDD.json  (top 200 by rank)
The listing is embedded in the page as an escaped JSON string; no API key needed."""
import sys, json, re, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
date = sys.argv[1]
html = subprocess.run(["curl","-sL","-m","60","-A","Mozilla/5.0",f"https://coinmarketcap.com/historical/{date}/"], capture_output=True, text=True).stdout
# find the escaped array of listings: objects with \"cmcRank\"
start = html.find('\\"cmcRank\\"')
if start < 0: raise SystemExit("no listing in page")
# walk back to the start of the escaped array containing these objects
arr_start = html.rfind('[{\\"id\\"', 0, start)
depth = 0; i = arr_start; s = html
while i < len(s):
    c = s[i]
    if c == '[': depth += 1
    elif c == ']':
        depth -= 1
        if depth == 0: break
    i += 1
raw = s[arr_start:i+1]
listing = json.loads(json.loads('"' + raw.replace('"', '\\"').replace('\\\\"', '\\"') + '"')) if False else json.loads(raw.encode().decode('unicode_escape').encode('latin-1').decode('utf-8', 'ignore'))
out = []
for c in listing:
    q = (c.get("quote") or {}).get("USD") or {}
    out.append({"rank": c.get("cmcRank"), "id": c.get("id"), "symbol": c.get("symbol"), "name": c.get("name"), "slug": c.get("slug"),
                "price": q.get("price"), "mcap": q.get("marketCap"), "circ": c.get("circulatingSupply"), "total": c.get("totalSupply"), "max": c.get("maxSupply"),
                "tags": c.get("tags", []), "platform": (c.get("platform") or {}).get("symbol")})
out.sort(key=lambda r: r["rank"] or 9999)
p = ROOT/"data"/"backtest"/f"cmc_{date}.json"; p.write_text(json.dumps({"date": date, "rows": out}, indent=1))
print(f"{date}: {len(out)} rows; top: {[r['symbol'] for r in out[:12]]}")
