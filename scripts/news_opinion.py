#!/usr/bin/env python3
"""Free path for the news opinion step: run it through Claude Code on your plan, no API key.

  python3 scripts/news_opinion.py            # builds research/news_batch_*_input.txt and runs `claude -p` per batch
  python3 scripts/news_opinion.py --prepare  # only builds the inputs (then paste them into a Claude session yourself)

Then: python3 scripts/merge_news.py && python3 scripts/build.py
"""
import json, pathlib, shutil, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
n = json.loads((ROOT/"data"/"news.json").read_text())["tokens"]; r = json.loads((ROOT/"data"/"research.json").read_text())["tokens"]
tks = [t for t in n if (n[t]["items"] if isinstance(n[t], dict) else n[t])]
groups = [tks[i::3] for i in range(3)]
for gi, g in enumerate(groups, 1):
    lines = []
    for tk in g:
        items = n[tk]["items"] if isinstance(n[tk], dict) else n[tk]
        bits = "".join(map(str, r[tk]["bits"])) if tk in r else "n/a"
        lines.append(f"## {tk}  verdict bits {bits}  key risk: {r.get(tk,{}).get('key_risk','')}")
        lines += [f"  [{i}] {it['date']} {it['source']}: {it['title']}" for i, it in enumerate(items, 1)]
    (ROOT/"research"/f"news_batch_{gi}_input.txt").write_text("\n".join(lines))
print("inputs written: research/news_batch_1..3_input.txt")
if "--prepare" in sys.argv: sys.exit(0)
if not shutil.which("claude"):
    print("claude CLI not found; run with --prepare and paste the inputs into a Claude Code session"); sys.exit(1)
prompt = (ROOT/"research"/"NEWS_OPINION_PROMPT.md").read_text()
for gi in range(1, 4):
    inp = (ROOT/"research"/f"news_batch_{gi}_input.txt").read_text()
    out = subprocess.run(["claude", "-p", "--output-format", "text", prompt + "\n\nINPUT:\n" + inp + "\n\nReply with the JSON only."],
                         capture_output=True, text=True).stdout
    s, e = out.find("{"), out.rfind("}")
    (ROOT/"research"/f"news_batch_{gi}.json").write_text(out[s:e+1]); print(f"batch {gi} done")
