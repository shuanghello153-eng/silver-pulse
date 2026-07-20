# -*- coding: utf-8 -*-
"""生成重做批次清单：全量 1502 家按 signal_strength 降序，每批 12 家，写 inbox/batch_NNN.txt。
高信号先修，让小爽尽早看到高价值企业的正确内容。"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
INBOX = os.path.join(BASE, "scores_draft/rework/inbox")
os.makedirs(INBOX, exist_ok=True)

d = json.load(open(DB, encoding="utf-8"))
def ser(e): return int(str(e["serial"]).lstrip("#"))
def sig(e):
    v = e.get("signal_strength")
    return v if isinstance(v, (int, float)) else 0

order = sorted(d, key=lambda e: -sig(e))
B = 12
batches = [order[i:i+B] for i in range(0, len(order), B)]
for i, b in enumerate(batches):
    path = os.path.join(INBOX, f"batch_{i:03d}.txt")
    with open(path, "w", encoding="utf-8") as f:
        for e in b:
            f.write(f"{ser(e)}\n")
print(f"生成 {len(batches)} 个批次，每批 {B} 家，共 {len(order)} 家")
print("最高信号批次前3家:", [ (e['serial'], e.get('signal_strength')) for e in batches[0][:3] ])
# 写 manifest
mani = {"total": len(order), "batches": len(batches), "per_batch": B,
        "scheme": "每工人处理3个连续批次(36家); 每波5工人=15批; 并发硬卡5"}
json.dump(mani, open(os.path.join(INBOX, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
