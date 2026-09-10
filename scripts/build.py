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
for ph in ("__MARKET_JSON__","__RESEARCH_JSON__","__NEWS_JSON__","__TARGETS_JSON__"): assert ph in tpl, ph
# versioned outputs: one folder per day, so verdict history accumulates for a later backtest
import datetime, shutil
hist = ROOT/"data"/"history"/datetime.date.today().isoformat(); hist.mkdir(parents=True, exist_ok=True)
for name in ("market.json","research.json","news.json"):
    if (ROOT/"data"/name).exists(): shutil.copy(ROOT/"data"/name, hist/name)
(ROOT/"scorecard"/"index.html").write_text(tpl.replace("__MARKET_JSON__", data).replace("__RESEARCH_JSON__", research).replace("__NEWS_JSON__", news).replace("__TARGETS_JSON__", targets))
print("built scorecard/index.html")
