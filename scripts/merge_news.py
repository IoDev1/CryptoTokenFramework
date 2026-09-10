#!/usr/bin/env python3
"""Merge research/news_batch_*.json opinions into data/news.json (adds "opinion" per token)."""
import json, glob, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
p = ROOT/"data"/"news.json"; d = json.loads(p.read_text())
n = 0
for f in sorted(glob.glob(str(ROOT/"research"/"news_batch_*.json"))):
    for tk, o in json.loads(pathlib.Path(f).read_text()).get("tokens", {}).items():
        if tk in d["tokens"]:
            items = d["tokens"][tk] if isinstance(d["tokens"][tk], list) else d["tokens"][tk].get("items", [])
            cited = [i for i in o.get("cited", []) if isinstance(i, int) and 0 < i <= len(items)]
            d["tokens"][tk] = {"items": items, "opinion": {"stance": o.get("stance","neutral"), "text": o.get("opinion",""), "cited": cited,
                               "cited_items": [{k: items[i-1].get(k,"") for k in ("title","url","source","date")} for i in cited],
                               "filters": o.get("filters",[]), "as_of": d.get("as_of","")}}; n += 1
for tk, v in d["tokens"].items():
    if isinstance(v, list): d["tokens"][tk] = {"items": v, "opinion": None}
p.write_text(json.dumps(d, indent=1)); print(f"merged opinions for {n} tokens")
