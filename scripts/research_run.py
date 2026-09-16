#!/usr/bin/env python3
"""Monthly research pass on the Claude API (Opus 5 + web search), one batch of ~6 tokens per request.

  python3 scripts/research_run.py --prepare        # write research/batch_N_input.txt from data/market.json
  python3 scripts/research_run.py --api            # run every batch (overwrites research/batch_N.json)
  python3 scripts/research_run.py --api --batch 3  # one batch
Then: python3 scripts/merge_research.py && python3 scripts/build.py

Cost guard: each batch caps web searches (MAX_SEARCHES) and output tokens; the script prints the
estimated cost per batch and in total. Without ANTHROPIC_API_KEY the --api mode exits 0 and does
nothing, so a CI run without the secret leaves the last stored verdicts in place.
"""
import json, pathlib, sys, datetime
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import model_api as M

ROOT = pathlib.Path(__file__).resolve().parent.parent
BATCH = 6
MAX_SEARCHES = 45          # ~7 per token
MAX_TOKENS = 24000

def market_line(tk, d):
    return (f'{tk}: price ${d.get("price")}, mcap {d.get("mcap")}, FDV {d.get("fdv")}, circ {d.get("circ_pct")}% of existing supply '
            f'(unminted {d.get("unminted_pct")}%, max supply {"capped" if d.get("max") else "UNCAPPED"}), from ATH {d.get("ath_change_pct")}% '
            f'(ATH {d.get("ath_date")}), fees30d {d.get("fees30d")}, rev30d {d.get("rev30d")}, rev prior30d {d.get("rev30d_prev")}, '
            f'rev1y {d.get("rev1y")}, llama source: {d.get("llama_src")}')

def prepare():
    m = json.loads((ROOT/"data"/"market.json").read_text())["tokens"]
    tks = [t for t, d in m.items() if not d.get("error")]
    n = 0
    for i in range(0, len(tks), BATCH):
        n += 1
        (ROOT/"research"/f"batch_{n}_input.txt").write_text("\n".join(market_line(t, m[t]) for t in tks[i:i+BATCH]))
    print(f"wrote {n} batch inputs for {len(tks)} tokens")
    return n

def run(batch_ids):
    if not M.have_key():
        print("ANTHROPIC_API_KEY not set: skipping research pass, keeping stored verdicts"); return
    rubric = (ROOT/"research"/"RUBRIC.md").read_text()
    today = datetime.date.today().isoformat()
    system = (f"You are a crypto fundamentals researcher. Today is {today}. Apply the rubric below literally and identically to every token. "
              "Unknown or unverifiable = 0. Use the supplied market figures; do not re-estimate them. Block subsidy, hashrate and miner revenue are "
              "emission, not demand. FC5 requires material revenue (>= $1M per 30 days). Verify judgment cells with web search (recent sources, "
              "2025-2026): insider selling and treasury moves; inflation, unlocks, admin or freeze authority; usage and revenue trend and dated "
              "catalysts. Reply with the JSON object only, no prose.\n\n" + rubric)
    total = 0.0
    for b in batch_ids:
        inp = ROOT/"research"/f"batch_{b}_input.txt"; out = ROOT/"research"/f"batch_{b}.json"
        if not inp.exists(): continue
        user = "Score these tokens:\n" + inp.read_text()
        tools = [{"type": "web_search_20260318", "name": "web_search", "max_uses": MAX_SEARCHES}]
        obj, usage = M.run_json(system, user, model=M.OPUS, max_tokens=MAX_TOKENS, tools=tools, effort="high")
        if "tokens" not in obj: raise RuntimeError(f"batch {b}: unexpected shape {list(obj)[:5]}")
        out.write_text(json.dumps(obj, indent=1))
        c = M.cost_usd(M.OPUS, usage); total += c
        print(f"batch {b}: {len(obj['tokens'])} tokens, {usage['web_search_requests']} searches, ~${c:.2f}")
    print(f"research pass total ~${total:.2f}")

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--prepare" in args: prepare()
    if "--api" in args:
        ids = [int(args[args.index("--batch")+1])] if "--batch" in args else sorted(int(p.stem.split("_")[1]) for p in (ROOT/"research").glob("batch_*_input.txt"))
        run(ids)
