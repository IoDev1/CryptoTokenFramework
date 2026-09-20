#!/usr/bin/env python3
"""Merge data/backtest/batch_*.json with universe.json, apply the same consistency rules as the live
merge, score with v1 weights, and measure what the tiers predicted.

Outputs data/backtest/results.json and BACKTEST.md.

Measures:
  - basket returns 2022-11-13 -> 2025-01-12, equal weight, for Core (>=10) / Watch (8-10) / Avoid (<8)
  - benchmarks: BTC, ETH, equal-weight top 20, equal-weight whole universe
  - gates variant: any Tier A fail -> Avoid regardless of score
  - per-filter signal: mean return of tokens passing vs failing each filter, and the hit rate
    (share beating BTC) for pass vs fail
  - rank correlation between score and return (Spearman)
  - weight sweep: the same for a few alternative weight sets
"""
import json, glob, pathlib, re, math, datetime
ROOT = pathlib.Path(__file__).resolve().parents[2]; B = ROOT/"data"/"backtest"
F = ["FA1","FA2","FA3","FA4","FB1","FB2","FB3","FC1","FC2","FC3","FC4","FC5","FC6"]
U = json.loads((B/"universe.json").read_text()); T = {t["tk"]: t for t in U["tokens"]}

def load_batches():
    out, problems = {}, []
    for f in sorted(glob.glob(str(B/"batch_*.json"))):
        try: d = json.loads(pathlib.Path(f).read_text())
        except Exception as e: problems.append(f"{f}: {e}"); continue
        for tk, r in d.get("tokens", {}).items():
            bits = r.get("bits")
            if not (isinstance(bits, list) and len(bits)==13 and all(b in (0,1) for b in bits)): problems.append(f"{tk}: bad bits"); continue
            t = T.get(tk)
            if not t: problems.append(f"{tk}: not in universe"); continue
            ev = dict(r.get("evidence", {}))
            # consistency rules, same as the live merge
            if t.get("ath_change_pct_2022") is not None: bits[8] = 1 if t["ath_change_pct_2022"] <= -75 else 0
            if bits[1] == 0 and (t.get("circ_pct_2022") or 0) >= 70 and re.search(r"(supplied circ|below 70)", ev.get("FA2",""), re.I): bits[1] = 1; ev["FA2"] = "Corrected: circ >= 70% of existing supply. Was: " + ev.get("FA2","")
            fees = t.get("fees30d") or 0
            if bits[5] == 1 and fees < 1e6 and re.search(r"(hashrate|miner|subsidy|security spend)", ev.get("FB2",""), re.I): bits[5] = 0; ev["FB2"] = "Overridden: block subsidy is emission, not demand. Was: " + ev.get("FB2","")
            if bits[11] == 1 and fees < 1e6: bits[11] = 0; ev["FC5"] = "Overridden: revenue immaterial (< $1M/30d). Was: " + ev.get("FC5","")
            out[tk] = {"bits": bits, "evidence": ev, "key_risk": r.get("key_risk",""), "confidence": r.get("confidence","L"), "sources": r.get("sources", [])[:8]}
    return out, problems

def score(bits, W): return sum(w*b for w, b in zip(W, bits))
def tier(s, thr=(10, 8)): return "core" if s >= thr[0] else "watch" if s >= thr[1] else "avoid"
def mean(xs): xs = [x for x in xs if x is not None]; return round(sum(xs)/len(xs), 1) if xs else None
def median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return None
    n = len(xs); return round((xs[n//2] if n % 2 else (xs[n//2-1]+xs[n//2])/2), 1)
def spearman(pairs):
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
    if len(pairs) < 3: return None
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i]); r = [0]*len(v)
        i = 0
        while i < len(order):
            j = i
            while j+1 < len(order) and v[order[j+1]] == v[order[i]]: j += 1
            for k in range(i, j+1): r[order[k]] = (i+j)/2 + 1
            i = j+1
        return r
    ra, rb = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs]); n = len(pairs)
    ma, mb = sum(ra)/n, sum(rb)/n
    num = sum((x-ma)*(y-mb) for x, y in zip(ra, rb)); den = math.sqrt(sum((x-ma)**2 for x in ra)*sum((y-mb)**2 for y in rb))
    return round(num/den, 3) if den else None

WEIGHTS = {"v1 (A1.5 B1.0 C0.5)": [1.5]*4+[1.0]*3+[0.5]*6, "flat (all 1)": [1.0]*13, "risk-averse (A2.5 B1 C.25)": [2.5]*4+[1.0]*3+[0.25]*6,
           "fundamentals (A1 B2 C.5)": [1.0]*4+[2.0]*3+[0.5]*6, "dealbreakers only": [1.0]*4+[0]*9, "foundation only": [0]*4+[1.0]*3+[0]*6}

def main():
    R, problems = load_batches()
    btc, eth = T["BTC"]["ret_pct"], T["ETH"]["ret_pct"]
    rows = []
    for tk, r in R.items():
        t = T[tk]; s = score(r["bits"], WEIGHTS["v1 (A1.5 B1.0 C0.5)"]) ; s = round(s, 1)
        afails = [F[i] for i in range(4) if r["bits"][i] == 0]
        rows.append({"tk": tk, "rank_2022": t["rank_2022"], "score": s, "tier": tier(s), "gated": "avoid" if afails else tier(s), "afails": afails,
                     "ret_pct": t["ret_pct"], "beat_btc": (t["ret_pct"] is not None and t["ret_pct"] > btc), "price_2022": t["price_2022"], "price_2025": t["price_2025"],
                     "ath_change_pct_2022": t["ath_change_pct_2022"], "confidence": r["confidence"], "key_risk": r["key_risk"], "bits": r["bits"]})
    rows.sort(key=lambda x: -x["score"])
    def basket(sel):
        rs = [x["ret_pct"] for x in rows if sel(x)]; n = len(rs)
        return {"n": n, "mean_ret_pct": mean(rs), "median_ret_pct": median(rs), "beat_btc_share": round(sum(1 for x in rows if sel(x) and x["beat_btc"])/n*100) if n else None}
    top20 = sorted(rows, key=lambda x: x["rank_2022"])[:20]
    res = {"start": U["start"], "end": U["end"], "n": len(rows), "problems": problems,
           "benchmarks": {"BTC": btc, "ETH": eth, "top20_equal_weight": mean([x["ret_pct"] for x in top20]), "universe_equal_weight": mean([x["ret_pct"] for x in rows]),
                          "universe_median": median([x["ret_pct"] for x in rows]), "share_beating_btc": round(sum(1 for x in rows if x["beat_btc"])/len(rows)*100) if rows else None},
           "baskets": {k: basket(lambda x, k=k: x["tier"] == k) for k in ("core","watch","avoid")},
           "baskets_gated": {k: basket(lambda x, k=k: x["gated"] == k) for k in ("core","watch","avoid")},
           "spearman_score_vs_return": spearman([(x["score"], x["ret_pct"]) for x in rows]),
           "filters": {}, "weights": {}, "rows": rows}
    for i, f in enumerate(F):
        p = [x for x in rows if x["bits"][i]]; q = [x for x in rows if not x["bits"][i]]
        res["filters"][f] = {"pass_n": len(p), "pass_mean": mean([x["ret_pct"] for x in p]), "pass_median": median([x["ret_pct"] for x in p]), "pass_beat_btc": round(sum(1 for x in p if x["beat_btc"])/len(p)*100) if p else None,
                             "fail_n": len(q), "fail_mean": mean([x["ret_pct"] for x in q]), "fail_median": median([x["ret_pct"] for x in q]), "fail_beat_btc": round(sum(1 for x in q if x["beat_btc"])/len(q)*100) if q else None}
        res["filters"][f]["edge_median"] = round((res["filters"][f]["pass_median"] or 0) - (res["filters"][f]["fail_median"] or 0), 1) if p and q else None
    for name, W in WEIGHTS.items():
        mx = sum(W); sc = {x["tk"]: (score(x["bits"], W)/mx*12 if mx else 0) for x in rows}
        thr = (10, 8)
        b = {k: mean([x["ret_pct"] for x in rows if tier(sc[x["tk"]], thr) == k]) for k in ("core","watch","avoid")}
        n = {k: sum(1 for x in rows if tier(sc[x["tk"]], thr) == k) for k in ("core","watch","avoid")}
        res["weights"][name] = {"spearman": spearman([(sc[x["tk"]], x["ret_pct"]) for x in rows]), "core_mean": b["core"], "core_n": n["core"], "watch_mean": b["watch"], "watch_n": n["watch"], "avoid_mean": b["avoid"], "avoid_n": n["avoid"]}
    (B/"results.json").write_text(json.dumps(res, indent=1))
    # ---- report
    L = [f"# 2022 backtest — v1 framework scored as of {res['start']}, returns to {res['end']}", "",
         f"Universe: top 60 by market cap on {res['start']} (CoinMarketCap snapshot), stablecoins and wrappers excluded, {res['n']} scored. "
         "Judgment cells were researched by Claude agents with web search under `research/BACKTEST_RUBRIC.md` (information cutoff 2022-11-15, "
         "pre-cutoff sources only). Mechanical cells (FC2, FA2 correction, FB2/FC5 materiality) come from CoinMarketCap, Yahoo Finance and DeFiLlama data as of the cutoff. "
         "**Hindsight caveat:** the researchers know what happened afterwards; the cutoff instruction limits but cannot eliminate leakage, so treat judgment-cell results as indicative.", "",
         "## Headline", "",
         "| Basket | n | Mean return | Median | Beat BTC |", "|---|---|---|---|---|"]
    for k in ("core","watch","avoid"):
        b = res["baskets"][k]; L.append(f"| {k.title()} (v1 weights) | {b['n']} | {b['mean_ret_pct']}% | {b['median_ret_pct']}% | {b['beat_btc_share']}% |")
    for k in ("core","watch","avoid"):
        b = res["baskets_gated"][k]; L.append(f"| {k.title()} (hard gates) | {b['n']} | {b['mean_ret_pct']}% | {b['median_ret_pct']}% | {b['beat_btc_share']}% |")
    bm = res["benchmarks"]
    L += [f"| BTC | 1 | {bm['BTC']}% | | |", f"| ETH | 1 | {bm['ETH']}% | | |", f"| Top 20 equal weight | 20 | {bm['top20_equal_weight']}% | | |",
          f"| Whole universe equal weight | {res['n']} | {bm['universe_equal_weight']}% | {bm['universe_median']}% | {bm['share_beating_btc']}% |", "",
          f"Spearman rank correlation, v1 score vs return: **{res['spearman_score_vs_return']}** (1 = perfect ordering, 0 = none).", "",
          "## Which filters carried signal", "", "Median return of tokens that passed vs failed each filter, and the share that beat BTC.", "",
          "| Filter | Pass n | Pass median | Pass beat BTC | Fail n | Fail median | Fail beat BTC | Edge (median) |", "|---|---|---|---|---|---|---|---|"]
    names = dict(zip(F, ["Team doesn't dump","Low dilution","Moat","Team known & solid","Token required","Real revenue","Supply dynamics","Can't be rugged","Far from ATH","Growing narrative","Risks priced in","Revenue trajectory","Catalysts"]))
    for f in sorted(F, key=lambda f: -(res["filters"][f]["edge_median"] or -999)):
        x = res["filters"][f]; L.append(f"| {f} {names[f]} | {x['pass_n']} | {x['pass_median']}% | {x['pass_beat_btc']}% | {x['fail_n']} | {x['fail_median']}% | {x['fail_beat_btc']}% | **{x['edge_median']}** |")
    L += ["", "## Weight sets", "", "| Weights | Spearman | Core mean (n) | Watch mean (n) | Avoid mean (n) |", "|---|---|---|---|---|"]
    for name, w in res["weights"].items(): L.append(f"| {name} | {w['spearman']} | {w['core_mean']}% ({w['core_n']}) | {w['watch_mean']}% ({w['watch_n']}) | {w['avoid_mean']}% ({w['avoid_n']}) |")
    L += ["", "## Every token", "", "| # 2022 | Token | Score | Tier | A fails | From ATH 2022 | Return | Beat BTC | Conf | Key risk (as of 2022) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for x in rows: L.append(f"| {x['rank_2022']} | {x['tk']} | {x['score']} | {x['tier']} | {','.join(x['afails']) or '-'} | {x['ath_change_pct_2022']}% | {x['ret_pct']}% | {'yes' if x['beat_btc'] else 'no'} | {x['confidence']} | {x['key_risk'][:110]} |")
    if problems: L += ["", "## Merge problems", ""] + [f"- {p}" for p in problems]
    (ROOT/"BACKTEST.md").write_text("\n".join(L) + "\n")
    print(f"{len(rows)} tokens; core {res['baskets']['core']}; watch {res['baskets']['watch']}; avoid {res['baskets']['avoid']}; BTC {btc}%; spearman {res['spearman_score_vs_return']}")
    for p in problems: print("  !!", p)

if __name__ == "__main__": main()
