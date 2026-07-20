# -*- coding: utf-8 -*-
"""抽取前 200 家高优先企业（按 research_value 降序），拆 10 批×20，预计算国内竞品，写 batches200/。"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _domestic_comp import DomesticComp

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
OUT = os.path.join(HERE, "batches200")
N = 200
PER = 20

d = json.load(open(DB, encoding="utf-8"))
d.sort(key=lambda e: float(e.get("research_value", 0) or 0), reverse=True)
top = d[:N]
dc = DomesticComp()
os.makedirs(OUT, exist_ok=True)

for i in range(0, N, PER):
    chunk = top[i:i + PER]
    recs = []
    for e in chunk:
        r = dict(e)
        comps = dc.find(e.get("serial"), top=5)
        r["domestic_competitors"] = [
            {"serial": "#" + c[0], "name": c[2], "overlap_l2": c[3]} for c in comps
        ]
        recs.append(r)
    fn = os.path.join(OUT, f"batch_src_{i // PER:03d}.json")
    json.dump(recs, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"已写出 {len(top)} 家 -> {N // PER} 个批次文件于 {OUT}")
print("top3 serials:", [e.get('serial') for e in top[:3]])
print("最低 rv 入选:", top[-1].get('research_value'))
