# -*- coding: utf-8 -*-
"""把 74 个批次的 AI 评分结果合并回 all_enterprises.json。
只写"评分相关键"，绝不碰 tag_l1/l2/category/标签。
- current_recommend -> recommend（清洗后的推荐理由文本）
- current_info/diff/copy -> info_score/diff_score/copy_score
- signal_strength / research_value 保持真相源原值（批次与真相源一致，未改动）
- total_score = 信号强度×0.3 + 信息量×0.3 + 差异化×0.2 + 可复制×0.2
  四维加权（小爽 2026-07-24 确认：信号也要乘权重，无"综合"元维度）
合并前自动备份。
"""
import json, os, glob, shutil, datetime

BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
BATCH_DIR = os.path.join(BASE, "scores_draft/rework/batches_score")

def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def save(p, o):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1)

# ---- 载入 ----
raw = load(DB)
if isinstance(raw, dict):
    enterprises = raw.get("enterprises", raw)
    wrapper = "dict"
else:
    enterprises = raw
    wrapper = "list"
by = {e["serial"]: e for e in enterprises}

# ---- 收集批次 ----
bt = {}
for f in sorted(glob.glob(os.path.join(BATCH_DIR, "batch_*.json"))):
    for e in load(f):
        s = e.get("serial")
        if s:
            bt[s] = e
print("批次覆盖企业数:", len(bt), " | 真相源企业数:", len(enterprises))

# ---- 备份 ----
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bak = DB + ".bak_premerge_" + ts
shutil.copy2(DB, bak)
print("已备份:", bak)

# ---- 合并 ----
merged = 0
for s, e in by.items():
    b = bt.get(s)
    if not b:
        continue
    rec = (b.get("current_recommend") or "").strip()
    if rec:
        e["recommend"] = rec
    for src, dst in [("current_info", "info_score"), ("current_diff", "diff_score"), ("current_copy", "copy_score")]:
        v = b.get(src)
        if v is not None:
            try:
                e[dst] = float(v)
            except Exception:
                pass
    # total_score = 信号强度×30% + 信息量×30% + 差异化×20% + 可复制×20%
    # （小爽 2026-07-24 确认公式：四维加权，无"综合"元维度）
    # 每维防御性封顶 0~10；total_score 封顶 0~10（前端展示时 ×10 → 0~100）
    sig = max(0.0, min(10.0, float(e.get("signal_strength") or 0)))
    info = max(0.0, min(10.0, float(e.get("info_score") or 0)))
    diff = max(0.0, min(10.0, float(e.get("diff_score") or 0)))
    copy = max(0.0, min(10.0, float(e.get("copy_score") or 0)))
    e["total_score"] = round(max(0.0, min(10.0, sig * 0.3 + info * 0.3 + diff * 0.2 + copy * 0.2)), 1)
    merged += 1

# ---- 写回 ----
if wrapper == "dict":
    raw["enterprises"] = enterprises
save(DB, raw)
print("合并完成:", merged, "家")

# ---- 校验 ----
n_rec = sum(1 for e in enterprises if (e.get("recommend") or "").strip())
n_info = sum(1 for e in enterprises if e.get("info_score") is not None)
n_ts = sum(1 for e in enterprises if e.get("total_score") is not None)
print("校验 -> recommend非空:", n_rec, "/", len(enterprises))
print("校验 -> info_score有值:", n_info, "/", len(enterprises))
print("校验 -> total_score有值:", n_ts, "/", len(enterprises))
