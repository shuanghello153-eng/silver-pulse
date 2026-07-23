# -*- coding: utf-8 -*-
import json, os
ROOT="G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
DB=os.path.join(ROOT,"data/enterprise/all_enterprises.json")
data=json.load(open(DB,encoding="utf-8"))
by={e["serial"]:e for e in data}

# 锚定 4 个已联网核实的事实到 highlights（可追溯，不删推荐理由）
anchor={
 "#0866": "独立研究认证：每投入$1为健康计划省$2.20（2.2x ROI）",
 "#0886": "完成 Accolade 并购后估值约 22 亿美元",
 "#0872": "临床实证：总医疗成本降 20%、住院降 41%",
 "#1152": "2025 年股价年初至今涨约 49%",
}
for s,note in anchor.items():
    e=by[s]
    hl=e.get("highlights") or []
    if note not in hl:
        hl.append(note); e["highlights"]=hl
        print(f"anchored {s}: {note}")

# 成立年修正（权威结论）
fixes={"#1158":1984,"#1170":1989}
for s,yr in fixes.items():
    e=by[s]
    old=e.get("founded"); e["founded"]=yr
    print(f"founded {s}: {old} -> {yr}")

json.dump(data,open(DB,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("FIXED & SAVED")
