#!/usr/bin/env python3
"""Turn data/history/<date>/ snapshots into two derived files:

  data/changes.json  "This week": latest snapshot vs the previous one at least MIN_GAP days older
                     (or the earliest one). Price movers, verdict cell flips, tier changes,
                     news stance changes, biggest current disagreement.
  data/ledger.json   Public ledger: every token's verdict per snapshot date with the price then,
                     return since the first verdict, and equal-weight basket returns.

Scores use the original v1 weights (A 1.5, B 1.0, C 0.5) and default thresholds (Core >= 10,
Watch >= 8), Claude verdicts, no gates, so the ledger is stable whatever a visitor sets on the page.
Run after build.py has snapshotted today's data (build.py calls this automatically).
"""
import json, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
HIST = ROOT / "data" / "history"
F = ["FA1","FA2","FA3","FA4","FB1","FB2","FB3","FC1","FC2","FC3","FC4","FC5","FC6"]
W = [1.5]*4 + [1.0]*3 + [0.5]*6
MIN_GAP = 6

def load(date):
    d = HIST / date
    def j(n):
        p = d / n
        return json.loads(p.read_text()) if p.exists() else {}
    return {"market": j("market.json").get("tokens", {}), "research": j("research.json").get("tokens", {}), "news": j("news.json").get("tokens", {})}

def score(bits): return round(sum(w*b for w, b in zip(W, bits)), 1)
def tier(s): return "core" if s >= 10 else "watch" if s >= 8 else "avoid"
def pct(a, b): return round((b - a) / a * 100, 1) if a and b else None

dates = sorted(p.name for p in HIST.iterdir() if p.is_dir() and (p / "market.json").exists())
if not dates:
    raise SystemExit("no history snapshots")
latest = dates[-1]; L = load(latest)
prev = None
for d in reversed(dates[:-1]):
    if (datetime.date.fromisoformat(latest) - datetime.date.fromisoformat(d)).days >= MIN_GAP: prev = d; break
if prev is None and len(dates) > 1: prev = dates[0]

# ---------------- changes.json
ch = {"to": latest, "from": prev, "days": (datetime.date.fromisoformat(latest) - datetime.date.fromisoformat(prev)).days if prev else 0,
      "movers": [], "verdicts": [], "tiers": [], "stances": [], "disagreement": None, "new_tokens": []}
if prev:
    P = load(prev)
    for tk, m in L["market"].items():
        pm = P["market"].get(tk)
        if not pm or not pm.get("price") or not m.get("price"): continue
        ch["movers"].append({"tk": tk, "pct": pct(pm["price"], m["price"]), "price": m["price"]})
    ch["movers"] = sorted([x for x in ch["movers"] if x["pct"] is not None], key=lambda x: -abs(x["pct"]))[:6]
    for tk, r in L["research"].items():
        pr = P["research"].get(tk)
        if not pr: ch["new_tokens"].append(tk); continue
        flips = [{"id": F[i], "from": pr["bits"][i], "to": r["bits"][i]} for i in range(13) if pr["bits"][i] != r["bits"][i]]
        if flips: ch["verdicts"].append({"tk": tk, "from": score(pr["bits"]), "to": score(r["bits"]), "flips": flips})
        t0, t1 = tier(score(pr["bits"])), tier(score(r["bits"]))
        if t0 != t1: ch["tiers"].append({"tk": tk, "from": t0, "to": t1})
    for tk, n in L["news"].items():
        o1 = (n or {}).get("opinion") if isinstance(n, dict) else None
        pn = P["news"].get(tk); o0 = (pn or {}).get("opinion") if isinstance(pn, dict) else None
        if o1 and o0 and o1.get("stance") != o0.get("stance"): ch["stances"].append({"tk": tk, "from": o0["stance"], "to": o1["stance"], "text": o1.get("text", "")})
# biggest current Opus-vs-Claude disagreement needs the Opus bits, which live only in the page; leave None here
(ROOT / "data" / "changes.json").write_text(json.dumps(ch, indent=1))

# ---------------- ledger.json
tokens = {}
for d in dates:
    S = load(d)
    for tk, r in S["research"].items():
        m = S["market"].get(tk, {})
        if not m.get("price"): continue
        s = score(r["bits"]); row = {"date": d, "price": m["price"], "score": s, "tier": tier(s)}
        t = tokens.setdefault(tk, {"series": []})
        if not t["series"] or t["series"][-1]["tier"] != row["tier"] or t["series"][-1]["score"] != row["score"] or d == latest:
            t["series"].append(row)
now_px = {tk: m.get("price") for tk, m in L["market"].items()}
calls = []
for tk, t in tokens.items():
    first = t["series"][0]; t["first"] = first; t["now"] = now_px.get(tk); t["ret_pct"] = pct(first["price"], t["now"])
    t["current"] = t["series"][-1]["tier"]; t["changes"] = max(0, len([1 for a, b in zip(t["series"], t["series"][1:]) if a["tier"] != b["tier"]]))
    for a, b in zip(t["series"], t["series"][1:]):
        if a["tier"] != b["tier"]: calls.append({"date": b["date"], "tk": tk, "from": a["tier"], "to": b["tier"], "score": b["score"], "price": b["price"]})
baskets = {}
for k in ("core", "watch", "avoid"):
    rs = [t["ret_pct"] for t in tokens.values() if t["first"]["tier"] == k and t["ret_pct"] is not None]
    baskets[k] = {"n": len(rs), "avg_ret_pct": round(sum(rs) / len(rs), 1) if rs else None}
btc = tokens.get("BTC", {}).get("ret_pct")
ledger = {"first_date": dates[0], "latest": latest, "days": (datetime.date.fromisoformat(latest) - datetime.date.fromisoformat(dates[0])).days,
          "snapshots": len(dates), "tokens": tokens, "baskets": baskets, "btc_ret_pct": btc, "calls": sorted(calls, key=lambda c: c["date"], reverse=True)}
(ROOT / "data" / "ledger.json").write_text(json.dumps(ledger, indent=1))
print(f"changes: {latest} vs {prev} ({ch['days']}d): {len(ch['movers'])} movers, {len(ch['verdicts'])} verdict changes, {len(ch['stances'])} stance changes; ledger: {len(tokens)} tokens over {ledger['days']} days")
