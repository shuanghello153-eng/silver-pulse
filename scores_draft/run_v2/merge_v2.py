# -*- coding: utf-8 -*-
"""
安全合并工人 out -> all_enterprises.json（run_v2/merge_v2.py）
只写"我的键"；research_value 当场重算；stage 白名单硬卡；tag_review/nonsilver 跨批累积。
用法: python merge_v2.py            # 合并 out/ 下全部
      python merge_v2.py 0 2 3      # 只合并指定批次
"""
import json, os, sys
BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
RUNV2 = os.path.join(BASE, "scores_draft/run_v2")
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
TR_PATH = os.path.join(RUNV2, "tag_review_all.json")
NS_PATH = os.path.join(RUNV2, "nonsilver_all.json")
PROC_PATH = os.path.join(RUNV2, "processed.json")
WHITELIST = {"种子期","天使","Pre-A","A轮","B轮","C轮","成长期","已上市","被收购","未搜到"}

db = json.load(open(DB_PATH, encoding="utf-8"))
by = {e["serial"]: e for e in db}

def clamp(v, lo=0, hi=10):
    try: v = float(v)
    except Exception: return lo
    return max(lo, min(hi, v))
def recompute(sig,info,diff,copy):
    return round((sig*0.3+info*0.3+diff*0.2+copy*0.2)*10,1)
def derive_stage(e, fallback):
    cur = str(fallback or "").strip()
    if cur in WHITELIST: return cur
    rnd = ""
    fl = e.get("funding_latest")
    if isinstance(fl, dict): rnd = str(fl.get("round",""))
    else: rnd = str(fl or "")
    low = rnd.lower()
    rules = [(["ipo","上市","纳斯达克","纽交所","港交所","nyse","nasdaq","hkex","主板"],"已上市"),
             (["收购","并购","私有化","acqui"],"被收购"),
             (["series d","d轮","e轮","f轮","growth","成长期","战略"],"成长期"),
             (["series c","c轮"],"C轮"),(["series b","b轮"],"B轮"),
             (["series a","a轮"],"A轮"),(["pre-a"],"Pre-A"),
             (["seed","种子"],"种子期"),(["angel","天使"],"天使")]
    for kws,st in rules:
        if any(k in low for k in kws): return st
    return "未搜到"

def apply_ent(e, o):
    sig = clamp(o.get("signal_strength", e.get("signal_strength", 0)))
    info = clamp(o.get("info_score"))
    diff = clamp(o.get("diff_score"))
    copy = clamp(o.get("copy_score"))
    e["signal_strength"] = sig; e["info_score"] = info
    e["diff_score"] = diff; e["copy_score"] = copy
    e["research_value"] = recompute(sig, info, diff, copy)
    # recommend：单字符串
    rec = o.get("recommend")
    if isinstance(rec, str) and rec.strip():
        e["recommend"] = rec
    elif isinstance(rec, dict):
        e["recommend"] = rec.get("rec_v1") or rec.get("rec_v2") or rec.get("rec_v3") or ""
    if o.get("payor_model"): e["payor_model"] = o["payor_model"]
    if o.get("business_tags_role") is not None:
        bt = e.get("business_tags") or {}
        if not isinstance(bt, dict): bt = {}
        bt["role"] = o["business_tags_role"]; e["business_tags"] = bt
    if o.get("desc_cn"): e["desc_cn"] = o["desc_cn"]
    if o.get("founded") is not None: e["founded"] = o["founded"]
    if o.get("stage"): e["stage"] = derive_stage(e, o["stage"])
    if o.get("events") is not None: e["events"] = o["events"]
    if o.get("highlights") is not None: e["highlights"] = o["highlights"]
    e["update_time"] = o.get("update_time") or "2026-07-17"
    if o.get("silver_verdict"): e["silver_verdict"] = o["silver_verdict"]
    if o.get("silver_reason"): e["silver_reason"] = o["silver_reason"]
    if o.get("数据来源"): e["数据来源"] = o["数据来源"]

tr_acc, ns_acc = {}, {}
if os.path.exists(TR_PATH):
    for x in json.load(open(TR_PATH, encoding="utf-8")): tr_acc[x["serial"]] = x
if os.path.exists(NS_PATH):
    for x in json.load(open(NS_PATH, encoding="utf-8")): ns_acc[x["serial"]] = x

args = sys.argv[1:]
out_dir = os.path.join(RUNV2, "out")
fnames = [f"batch_{int(a):03d}_out.json" for a in args] if args else sorted(
    x for x in os.listdir(out_dir) if x.endswith("_out.json"))

merged = 0; processed = set()
for fn in fnames:
    p = os.path.join(out_dir, fn)
    if not os.path.exists(p):
        print("缺少", fn); continue
    data = json.load(open(p, encoding="utf-8"))
    for o in data.get("enterprises", []):
        s = o.get("serial"); e = by.get(s)
        if not e:
            print("  !! 库中无", s); continue
        apply_ent(e, o); merged += 1; processed.add(s)
    for tr in data.get("tag_review", []):
        tr_acc[tr["serial"]] = dict(tr, old_tags={
            "tag_l1": by.get(tr["serial"], {}).get("tag_l1"),
            "tag_l2": by.get(tr["serial"], {}).get("tag_l2"),
            "business_tags": by.get(tr["serial"], {}).get("business_tags")})
    for ns in data.get("nonsilver", []):
        ns_acc[ns["serial"]] = dict(ns)

json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(list(tr_acc.values()), open(TR_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(list(ns_acc.values()), open(NS_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
prev = set(json.load(open(PROC_PATH, encoding="utf-8")) if os.path.exists(PROC_PATH) else [])
prev.update(processed)
json.dump(sorted(prev), open(PROC_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"已合并 {merged} 家（{len(fnames)} 文件）。累计已处理 {len(prev)} 家。")
print(f"tag_review 累计 {len(tr_acc)}；nonsilver 累计 {len(ns_acc)}。")
