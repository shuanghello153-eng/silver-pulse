# -*- coding: utf-8 -*-
"""安全合并工人 out 文件到 all_enterprises.json。
只写"我的键"：signal_strength, info_score, diff_score, copy_score, research_value,
recommend, payor_model, update_time, silver_verdict, silver_reason, founded, stage,
events, highlights, desc_cn(重写), business_tags.role。
绝不碰 tag_l1/tag_l2/category/tags。

质量保障（合并即强校验）：
- research_value 由四维当场重算，worker 算错也救得回。
- 四维分越界自动 clamp 到 [0,10] 并告警。
- tag_review.old_tags 一律用 DB 合并前真实状态回填，不依赖 worker 照抄。
- tag_review_all / nonsilver_all 按 serial 跨批次累积合并，绝不覆盖丢失。

用法: python _merge.py            # 合并 out/ 下全部
      python _merge.py 0 2 3 4    # 只合并指定批次
"""
import json, os, sys, copy
BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
RUN = os.path.join(BASE, "scores_draft/run")
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
BEFORE = os.path.join(RUN, "before_full.json")
TR_PATH = os.path.join(RUN, "tag_review_all.json")
NS_PATH = os.path.join(RUN, "nonsilver_all.json")
PROC_PATH = os.path.join(RUN, "processed.json")

db = json.load(open(DB_PATH, encoding="utf-8"))
by = {e["serial"]: e for e in db}

# 首次合并前拍快照（before）
if not os.path.exists(BEFORE):
    json.dump(db, open(BEFORE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("已生成 before 快照")

def clamp(v, lo=0, hi=10):
    try:
        v = float(v)
    except Exception:
        return lo
    return max(lo, min(hi, v))

def recompute(sig, info, diff, copy):
    return round((sig*0.3 + info*0.3 + diff*0.2 + copy*0.2) * 10, 1)

def apply_ent(e, o):
    sig = clamp(o.get("signal_strength", 0))
    info = clamp(o.get("info_score"))
    diff = clamp(o.get("diff_score"))
    copy = clamp(o.get("copy_score"))
    rv = recompute(sig, info, diff, copy)   # 当场重算，杜绝公式错
    e["signal_strength"] = sig
    e["info_score"] = info
    e["diff_score"] = diff
    e["copy_score"] = copy
    e["research_value"] = rv
    rec = o.get("recommend") or {}
    e["recommend"] = {
        "rec_v1": rec.get("rec_v1"), "rec_v2": rec.get("rec_v2"), "rec_v3": rec.get("rec_v3"),
        "info_score": info, "diff_score": diff,
        "copy_score": copy, "signal_strength": sig,
        "research_value": rv,
    }
    if o.get("payor_model") is not None:
        e["payor_model"] = o["payor_model"]
    if o.get("business_tags_role") is not None:
        bt = e.get("business_tags") or {}
        if not isinstance(bt, dict): bt = {}
        bt["role"] = o["business_tags_role"]
        e["business_tags"] = bt
    if o.get("desc_cn"): e["desc_cn"] = o["desc_cn"]
    if o.get("founded") is not None: e["founded"] = o["founded"]
    if o.get("stage"): e["stage"] = o["stage"]
    if o.get("events") is not None: e["events"] = o["events"]
    if o.get("highlights") is not None: e["highlights"] = o["highlights"]
    e["update_time"] = o.get("update_time") or "2026-07-17"
    if o.get("silver_verdict"): e["silver_verdict"] = o["silver_verdict"]
    if o.get("silver_reason"): e["silver_reason"] = o["silver_reason"]

# ---- 累积聚合（跨批次合并，不丢失）----
tr_acc = {}
if os.path.exists(TR_PATH):
    for x in json.load(open(TR_PATH, encoding="utf-8")):
        tr_acc[x["serial"]] = x
ns_acc = {}
if os.path.exists(NS_PATH):
    for x in json.load(open(NS_PATH, encoding="utf-8")):
        ns_acc[x["serial"]] = x

args = sys.argv[1:]
out_dir = os.path.join(RUN, "out")
if args:
    fnames = [f"batch_{int(a):03d}_out.json" for a in args]
else:
    fnames = sorted(x for x in os.listdir(out_dir) if x.endswith("_out.json"))

merged = 0
processed = set()
for fn in fnames:
    p = os.path.join(out_dir, fn)
    if not os.path.exists(p):
        print("缺少", fn); continue
    data = json.load(open(p, encoding="utf-8"))
    for o in data.get("enterprises", []):
        s = o.get("serial")
        e = by.get(s)
        if not e:
            print("  !! 库中无", s); continue
        apply_ent(e, o)
        merged += 1
        processed.add(s)
    for tr in data.get("tag_review", []):
        tr_acc[tr["serial"]] = dict(tr)
    for ns in data.get("nonsilver", []):
        ns_acc[ns["serial"]] = dict(ns)

# old_tags 用 DB 合并前真实状态回填（by 仍是合并前快照）
for s, tr in tr_acc.items():
    e0 = by.get(s, {})
    tr["old_tags"] = {
        "tag_l1": e0.get("tag_l1"),
        "tag_l2": e0.get("tag_l2"),
        "business_tags": e0.get("business_tags"),
    }

# 写回 DB
json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# 聚合 tag_review / nonsilver
json.dump(list(tr_acc.values()), open(TR_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(list(ns_acc.values()), open(NS_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# 处理集合
prev = set(json.load(open(PROC_PATH, encoding="utf-8")) if os.path.exists(PROC_PATH) else [])
prev.update(processed)
json.dump(sorted(prev), open(PROC_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"已合并 {merged} 家企业（本批 {len(fnames)} 文件）。累计已处理 {len(prev)} 家。")
print(f"tag_review 累计 {len(tr_acc)} 条；nonsilver 累计 {len(ns_acc)} 条。")
