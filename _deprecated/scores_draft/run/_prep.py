# -*- coding: utf-8 -*-
"""生成运行批次 inbox（优先级：new30 最前，其余按信号强度降序）。
用法: python _prep.py
输出: run/inbox/batch_NNN.json, run/MANIFEST.json
"""
import json, os
BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
RUN = os.path.join(BASE, "scores_draft/run")
INB = os.path.join(RUN, "inbox")
OUT = os.path.join(RUN, "out")
VAL = os.path.join(RUN, "val")
for d in (INB, OUT, VAL):
    os.makedirs(d, exist_ok=True)

db = json.load(open(os.path.join(BASE, "data/enterprise/all_enterprises.json"), encoding="utf-8"))
sig = json.load(open(os.path.join(BASE, "scores_draft/all_signals.json"), encoding="utf-8"))
by = {e["serial"]: e for e in db}

# ---- new30 数据包（已抓好的资料，优先用）----
n = json.load(open(os.path.join(BASE, "scores_draft/new30_packets.json"), encoding="utf-8"))
flat = []
for pkt in n:
    if isinstance(pkt, list):
        flat.extend(pkt)
    elif isinstance(pkt, dict) and "enterprises" in pkt:
        flat.extend(pkt["enterprises"])
pkt_by = {e["serial"]: e for e in flat}
new30 = [e["serial"] for e in flat if e["serial"] in by]

# ---- 排序：new30 在前，其余按信号降序 ----
rest = [s for s in by if s not in set(new30)]
rest.sort(key=lambda s: float(sig.get(s, 0) or 0), reverse=True)

def tier_of(sv):
    if sv >= 6: return "A"
    if sv >= 3: return "B"
    return "C"

BATCH = 12
order = new30 + rest
batches = [order[i:i+BATCH] for i in range(0, len(order), BATCH)]

manifest = {"total": len(order), "batches": []}
for i, b in enumerate(batches):
    ents = []
    for s in b:
        rec = dict(by[s])  # 当前库全部字段
        rec["signal_strength"] = float(sig.get(s, 0) or 0)
        if s in pkt_by:
            rec["_packet"] = pkt_by[s]  # 前车已抓资料
        ents.append(rec)
    sv0 = rec.get("signal_strength") if rec else 0
    # 批次 tier 取最高（new30 固定 A）
    is_new30 = all(x in new30 for x in b)
    tier = "A" if is_new30 else tier_of(max(rec.get("signal_strength",0) for rec in ents))
    inbox = {"batch": i, "tier": tier, "enterprises": ents}
    fn = os.path.join(INB, f"batch_{i:03d}.json")
    json.dump(inbox, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    manifest["batches"].append({"batch": i, "file": f"inbox/batch_{i:03d}.json",
                                "tier": tier, "count": len(b),
                                "serials": b, "status": "pending"})

json.dump(manifest, open(os.path.join(RUN, "MANIFEST.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"inbox 批次: {len(batches)}  企业总数: {len(order)} (new30={len(new30)}, rest={len(rest)})")
print("tier 分布 A/B/C =>",
      sum(1 for m in manifest['batches'] if m['tier']=='A'),
      sum(1 for m in manifest['batches'] if m['tier']=='B'),
      sum(1 for m in manifest['batches'] if m['tier']=='C'))
