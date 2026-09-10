#!/usr/bin/env python3
"""Merge research/batch_*.json into data/research.json and validate shape."""
import json, glob, pathlib, datetime, sys, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
F = ["FA1","FA2","FA3","FA4","FB1","FB2","FB3","FC1","FC2","FC3","FC4","FC5","FC6"]
market = json.loads((ROOT/"data"/"market.json").read_text())["tokens"]
out, problems = {}, []
for f in sorted(glob.glob(str(ROOT/"research"/"batch_*.json"))):
    try: d = json.loads(pathlib.Path(f).read_text())
    except Exception as e: problems.append(f"{f}: {e}"); continue
    for tk, r in d.get("tokens", {}).items():
        bits = r.get("bits")
        if not (isinstance(bits, list) and len(bits)==13 and all(b in (0,1) for b in bits)):
            problems.append(f"{tk}: bad bits {bits}"); continue
        m = market.get(tk, {}); ev = dict(r.get("evidence", {}))
        # FC2 is mechanical: enforce from market data
        if m.get("fc2_live") is not None: bits[8] = 1 if m["fc2_live"] else 0
        # FA2 mechanical leg uses the corrected denominator (circ / existing supply); stale max caps
        # made BNB/DASH read <70%. Flip to pass only when existing-supply circ >= 70% and future
        # emission is small, and the agent's fail cites only the supplied percentage.
        if bits[1] == 0 and (m.get("circ_pct") or 0) >= 70 and (m.get("unminted_pct") or 0) <= 35 and re.search(r"(66\.6|67\.8|supplied circ|below 70)", ev.get("FA2","")):
            bits[1] = 1; ev["FA2"] = f"Corrected: {m['circ_pct']}% of existing supply circulating (stale max-supply cap ignored); future emission is judged under FB3. Was: " + ev.get("FA2","")
        # FB2: block subsidy / hashrate is emission, not demand
        fees, rev = m.get("fees30d") or 0, m.get("rev30d") or 0
        if bits[5] == 1 and fees < 1e6 and rev < 1e6 and re.search(r"(hashrate|miner|subsidy|security spend)", ev.get("FB2",""), re.I):
            bits[5] = 0; ev["FB2"] = "Overridden: block subsidy/hashrate is emission, not paid demand; fees < $1M/30d. Was: " + ev.get("FB2","")
        # FC5 needs material revenue
        if bits[11] == 1 and fees < 1e6 and rev < 1e6:
            bits[11] = 0; ev["FC5"] = "Overridden: revenue immaterial (< $1M/30d), trend is noise. Was: " + ev.get("FC5","")
        out[tk] = {"bits": bits, "evidence": {k: str(ev.get(k, "")) for k in F},
                   "key_risk": str(r.get("key_risk","")), "confidence": r.get("confidence","L"),
                   "sources": [s for s in r.get("sources", []) if isinstance(s, str)][:8]}
(ROOT/"data"/"research.json").write_text(json.dumps({
    "as_of": datetime.date.today().isoformat(), "rater": "Claude Fable 5.1 with web search",
    "rubric": "research/RUBRIC.md", "tokens": out}, indent=1))
print(f"merged {len(out)} tokens", file=sys.stderr)
for p in problems: print("  !!", p, file=sys.stderr)
for tk, r in out.items(): print(f"{tk:8} {''.join(map(str,r['bits']))} {sum(r['bits'])!s:3} {r['confidence']} {r['key_risk'][:70]}")
