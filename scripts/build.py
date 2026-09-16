#!/usr/bin/env python3
"""Inject data/market.json into scorecard/template.html -> scorecard/index.html"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
tpl = (ROOT/"scorecard"/"template.html").read_text()
data = json.dumps(json.loads((ROOT/"data"/"market.json").read_text()), separators=(",",":"))
research = json.dumps(json.loads((ROOT/"data"/"research.json").read_text()), separators=(",",":")) if (ROOT/"data"/"research.json").exists() else '{"as_of":"","rater":"","tokens":{}}'
def load(name, default):
    f = ROOT/"data"/name
    return json.dumps(json.loads(f.read_text()), separators=(",",":")) if f.exists() else default
news = load("news.json", '{"as_of":"","source":"","tokens":{}}'); targets = load("targets.json", '{"tokens":{}}')
site = load("site.json", '{}')
for ph in ("__MARKET_JSON__","__RESEARCH_JSON__","__NEWS_JSON__","__TARGETS_JSON__","__SITE_JSON__","__CHANGES_JSON__"): assert ph in tpl, ph
# versioned outputs: one folder per day, so verdict history accumulates for a later backtest
import datetime, shutil
hist = ROOT/"data"/"history"/datetime.date.today().isoformat(); hist.mkdir(parents=True, exist_ok=True)
for name in ("market.json","research.json","news.json"):
    if (ROOT/"data"/name).exists(): shutil.copy(ROOT/"data"/name, hist/name)
# derived: this-week changes and the public ledger, both from the snapshots
import subprocess, sys
subprocess.run([sys.executable, str(ROOT/"scripts"/"diff_history.py")], check=True)
changes = load("changes.json", '{"to":"","from":null,"movers":[],"verdicts":[],"tiers":[],"stances":[],"new_tokens":[]}')
ledger = load("ledger.json", '{"tokens":{},"baskets":{},"calls":[]}')
ltpl = (ROOT/"scorecard"/"ledger_template.html").read_text(); assert "__LEDGER_JSON__" in ltpl
ledger_html = ltpl.replace("__LEDGER_JSON__", ledger)
(ROOT/"scorecard"/"ledger.html").write_text(ledger_html)
(ROOT/"scorecard"/"index.html").write_text(tpl.replace("__MARKET_JSON__", data).replace("__RESEARCH_JSON__", research).replace("__NEWS_JSON__", news).replace("__TARGETS_JSON__", targets).replace("__SITE_JSON__", site).replace("__CHANGES_JSON__", changes))
# public site: full documents (the bare files above are for the claude.ai artifact wrapper)
site_dir = ROOT/"site"; site_dir.mkdir(exist_ok=True)
def wrap(body, desc):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="description" content="{desc}"><meta name="robots" content="index,follow"></head><body>' + body + '</body></html>')
index_html = (ROOT/"scorecard"/"index.html").read_text()
(site_dir/"index.html").write_text(wrap(index_html, "Bear-market crypto planner: 62 tokens scored on 13 filters by two research passes, your own targets and allocations, shareable plans. Research tooling, not advice."))
(site_dir/"ledger.html").write_text(wrap(ledger_html, "Public ledger of every verdict, dated and graded as prices move. Misses included."))
(site_dir/".nojekyll").write_text("")
print("built scorecard/{index,ledger}.html (artifact) and site/{index,ledger}.html (public)")
