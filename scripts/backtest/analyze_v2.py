#!/usr/bin/env python3
"""Approximate v2 scoring of the 2022 universe from the existing v1 cells plus mechanical data,
so the v2 design can be compared with v1 before paying for a fresh research pass.

v2 Quality (see FRAMEWORK_v2.md), mapped from what exists:
  S1 survivorship 2.0  listed <= 2018-06 AND pre-cutoff ATH set in the 2020-22 cycle (mechanical)
  S2 value accrual 1.5 FB1 and FB2 -> 1; one of them -> 0.5
  S3 revenue level 1.0 P/S = mcap / annualised fees (fees30d*12): <50 -> 1, 50-200 -> 0.5 (mechanical)
  S4 revenue trend 1.0 fees30d vs prior 30d: up >15% -> 1, within 15% -> 0.5, down -> 0 (mechanical)
  S5 supply health 1.5 FA2 and FB3 -> 1; one -> 0.5
  S6 moat 1.5         FA3
  S7 concentration 1.0 not available for 2022 -> excluded, score rescaled to /10
  S8 usage growth 0.5 FC3
Gates (optional): G1 = FC1; G2 narrowed = FA1 fail whose evidence mentions undisclosed/opaque/deceptive/liquidation; G3 = FA4.
Entry (separate): E1 = FC2 (<= -75%), E2 relative strength = drawdown better than the universe median.
Tiers are RELATIVE: Core = top quartile, Watch = second quartile, Avoid = bottom half.
"""
import json, pathlib, re, math
ROOT = pathlib.Path(__file__).resolve().parents[2]; B = ROOT/"data"/"backtest"
R = json.loads((B/"results.json").read_text()); U = {t["tk"]: t for t in json.loads((B/"universe.json").read_text())["tokens"]}
ev = {}
import glob
for f in glob.glob(str(B/"batch_*.json")):
    for tk, r in json.loads(pathlib.Path(f).read_text()).get("tokens", {}).items(): ev[tk] = r.get("evidence", {})
ATH_DATE = {"BTC":"2021-11","ETH":"2021-11","BNB":"2021-05","XRP":"2018-01","SOL":"2021-11","TRX":"2018-01","LEO":"2022-02","XMR":"2021-05","OKB":"2021-05","APT":"2022-10","BIT":"2021-11","KLAY":"2021-03","MATIC":"2021-12","TON":"2021-11","TWT":"2022-11"}
def ath_date(t): return ATH_DATE.get(t["tk"]) or (t.get("ath_now_date") or "")[:7]
F = ["FA1","FA2","FA3","FA4","FB1","FB2","FB3","FC1","FC2","FC3","FC4","FC5","FC6"]; I = {f: i for i, f in enumerate(F)}
def spearman(pairs):
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]; n = len(pairs)
    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i]); r = [0]*n; i = 0
        while i < n:
            j = i
            while j+1 < n and v[order[j+1]] == v[order[i]]: j += 1
            for k in range(i, j+1): r[order[k]] = (i+j)/2+1
            i = j+1
        return r
    ra, rb = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs]); ma, mb = sum(ra)/n, sum(rb)/n
    num = sum((x-ma)*(y-mb) for x, y in zip(ra, rb)); den = math.sqrt(sum((x-ma)**2 for x in ra)*sum((y-mb)**2 for y in rb)); return round(num/den, 3) if den else None
def median(xs):
    xs = sorted(xs); n = len(xs); return round(xs[n//2] if n % 2 else (xs[n//2-1]+xs[n//2])/2, 1) if xs else None
rows = []
dd_median = median([t["ath_change_pct_2022"] for t in U.values()])
for x in R["rows"]:
    tk = x["tk"]; b = x["bits"]; t = U[tk]; e = ev.get(tk, {})
    fees = t.get("fees30d") or 0; prev = t.get("fees30d_prev") or 0
    s1 = 1.0 if (t.get("date_added","9999") <= "2018-06-30" and ath_date(t) >= "2020-07") else 0.0
    s2 = 1.0 if (b[I["FB1"]] and b[I["FB2"]]) else 0.5 if (b[I["FB1"]] or b[I["FB2"]]) else 0.0
    ps = t["mcap_2022"] / (fees*12) if fees > 0 else None
    s3 = 0.0 if ps is None else 1.0 if ps < 50 else 0.5 if ps < 200 else 0.0
    s4 = 0.0 if not fees or not prev else 1.0 if fees > prev*1.15 else 0.5 if fees >= prev*0.85 else 0.0
    s5 = 1.0 if (b[I["FA2"]] and b[I["FB3"]]) else 0.5 if (b[I["FA2"]] or b[I["FB3"]]) else 0.0
    s6 = float(b[I["FA3"]]); s8 = float(b[I["FC3"]])
    q = (2.0*s1 + 1.5*s2 + 1.0*s3 + 1.0*s4 + 1.5*s5 + 1.5*s6 + 0.5*s8) / 9.0 * 10
    g2_fail = (not b[I["FA1"]]) and bool(re.search(r"(undisclos|opaque|decept|liquidat|fraud|hidden|unreported|no schedule|unscheduled)", e.get("FA1",""), re.I))
    gates_fail = [g for g, bad in (("G1", not b[I["FC1"]]), ("G2", g2_fail), ("G3", not b[I["FA4"]])) if bad]
    e1 = int(t["ath_change_pct_2022"] <= -75); e2 = int(t["ath_change_pct_2022"] > dd_median)
    rows.append({"tk": tk, "q": round(q, 2), "cells": {"S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5, "S6": s6, "S8": s8}, "ps": round(ps, 1) if ps else None,
                 "gates_fail": gates_fail, "e1": e1, "e2": e2, "ret": x["ret_pct"], "v1": x["score"], "v1_tier": x["tier"], "beat_btc": x["beat_btc"]})
rows.sort(key=lambda r: -r["q"]); n = len(rows)
for i, r in enumerate(rows): r["tier"] = "core" if i < n//4 else "watch" if i < n//2 else "avoid"
for r in rows: r["gated_tier"] = "avoid" if r["gates_fail"] else r["tier"]
btc = R["benchmarks"]["BTC"]
def basket(sel):
    xs = [r for r in rows if sel(r)]; k = len(xs)
    return {"n": k, "median": median([r["ret"] for r in xs]), "mean": round(sum(r["ret"] for r in xs)/k, 1) if k else None, "positive": round(sum(r["ret"] > 0 for r in xs)/k*100) if k else None, "beat_btc": round(sum(r["beat_btc"] for r in xs)/k*100) if k else None}
out = {"spearman_v2": spearman([(r["q"], r["ret"]) for r in rows]), "spearman_v1": R["spearman_score_vs_return"],
       "tiers": {k: basket(lambda r, k=k: r["tier"] == k) for k in ("core","watch","avoid")}, "tiers_gated": {k: basket(lambda r, k=k: r["gated_tier"] == k) for k in ("core","watch","avoid")},
       "entry": {"E1 far from ATH": basket(lambda r: r["e1"] == 1), "not E1": basket(lambda r: r["e1"] == 0), "E2 relative strength": basket(lambda r: r["e2"] == 1), "not E2": basket(lambda r: r["e2"] == 0)},
       "cells": {}, "rows": rows}
for c in ("S1","S2","S3","S4","S5","S6","S8"):
    p = [r["ret"] for r in rows if r["cells"][c] >= 1]; h = [r["ret"] for r in rows if r["cells"][c] == 0.5]; q0 = [r["ret"] for r in rows if r["cells"][c] == 0]
    out["cells"][c] = {"pass_n": len(p), "pass_median": median(p), "half_n": len(h), "half_median": median(h), "fail_n": len(q0), "fail_median": median(q0)}
(B/"results_v2.json").write_text(json.dumps(out, indent=1))
L = ["", "## v2 approximation on the same universe", "",
     "v2 Quality rebuilt from the v1 cells plus mechanical data (survivorship from listing date and ATH cycle, P/S and revenue trend from DeFiLlama, S7 concentration unavailable and excluded), relative tiers (top quartile / second quartile / bottom half), gates optional, entry separate. Details in `scripts/backtest/analyze_v2.py`.", "",
     f"Rank correlation with return: **v2 {out['spearman_v2']}** vs v1 {out['spearman_v1']}.", "",
     "| Basket | n | Median | Mean | Positive | Beat BTC |", "|---|---|---|---|---|---|"]
for k in ("core","watch","avoid"): b = out["tiers"][k]; L.append(f"| v2 {k.title()} (relative) | {b['n']} | {b['median']}% | {b['mean']}% | {b['positive']}% | {b['beat_btc']}% |")
for k in ("core","watch","avoid"): b = out["tiers_gated"][k]; L.append(f"| v2 {k.title()} + gates | {b['n']} | {b['median']}% | {b['mean']}% | {b['positive']}% | {b['beat_btc']}% |")
for k, b in out["entry"].items(): L.append(f"| {k} | {b['n']} | {b['median']}% | {b['mean']}% | {b['positive']}% | {b['beat_btc']}% |")
L += ["", "| v2 cell | Pass n / median | Partial n / median | Fail n / median |", "|---|---|---|---|"]
names = {"S1":"Survivorship","S2":"Value accrual","S3":"Revenue level (P/S)","S4":"Revenue trend","S5":"Supply health","S6":"Moat","S8":"Usage growth"}
for c, v in out["cells"].items(): L.append(f"| {c} {names[c]} | {v['pass_n']} / {v['pass_median']}% | {v['half_n']} / {v['half_median']}% | {v['fail_n']} / {v['fail_median']}% |")
L += ["", "| Token | v2 Q | v2 tier | gates | v1 | v1 tier | Return |", "|---|---|---|---|---|---|---|"]
for r in rows: L.append(f"| {r['tk']} | {r['q']} | {r['tier']} | {','.join(r['gates_fail']) or '-'} | {r['v1']} | {r['v1_tier']} | {r['ret']}% |")
md = (ROOT/"BACKTEST.md").read_text()
if "## v2 approximation" in md: md = md.split("\n## v2 approximation")[0]
(ROOT/"BACKTEST.md").write_text(md.rstrip("\n") + "\n" + "\n".join(L) + "\n")
print("spearman v2", out["spearman_v2"], "v1", out["spearman_v1"]); print("tiers", {k: (v["n"], v["median"], v["positive"]) for k, v in out["tiers"].items()}); print("gated", {k: (v["n"], v["median"], v["positive"]) for k, v in out["tiers_gated"].items()})
print("cells", {c: (v["pass_median"], v["fail_median"]) for c, v in out["cells"].items()}); print("core:", [r["tk"] for r in rows if r["tier"]=="core"])
