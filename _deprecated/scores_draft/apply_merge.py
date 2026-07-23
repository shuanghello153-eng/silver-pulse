# -*- coding: utf-8 -*-
"""合并本轮评分+信息补全结果到 all_enterprises.json（只写"我的键"，绝不碰 tag_l1/l2/category）。
同时产出 before_snapshot.json / after_snapshot.json 供 Excel 用。
"""
import json, re, copy, os, sys

BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
SD = os.path.join(BASE, "scores_draft")
TODAY = "2026-07-16"

def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def save(p, o):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1)

db = load(DB_PATH)
db_by = {e["serial"]: e for e in db}

new30 = load(os.path.join(SD, "new30_serials.json"))
pilot = load(os.path.join(SD, "pilot25_serials.json"))
all_signals = load(os.path.join(SD, "all_signals.json"))
pilot_before = load(os.path.join(SD, "pilot25_before.json"))

# ---- 收集研究结果 ----
def load_ents(p):
    d = load(p)
    return {e["serial"]: e for e in d["enterprises"]}

research_map = {}
for fn in ["research_part1.json", "research_part4.json", "research_part5.json"]:
    p = os.path.join(SD, fn)
    if os.path.exists(p):
        research_map.update(load_ents(p))

rec30_map = {}
for fn in ["rec_results/rec30_pack0.json", "rec_results/rec30_pack1.json", "rec_results/rec30_pack3.json"]:
    p = os.path.join(SD, fn)
    if os.path.exists(p):
        rec30_map.update(load_ents(p))

rec_pilot_map = {}
for i in range(5):
    p = os.path.join(SD, f"rec_results/rec_pilot{i}.json")
    if os.path.exists(p):
        rec_pilot_map.update(load_ents(p))

# ---- before 快照（当前 DB 状态，30-new 的原始态）----
before_snap = {s: copy.deepcopy(db_by[s]) for s in (new30 + pilot) if s in db_by}
save(os.path.join(SD, "before_snapshot.json"), before_snap)

def derive_stage(r):
    rnd = ((r.get("funding_latest_corrected") or {}).get("round", "")) or ""
    if any(k in rnd for k in ["上市", "IPO", "纽交所", "港交所", "纳斯达克", "NYSE", "HKEX", "Nasdaq"]):
        return "已上市"
    if any(k in rnd for k in ["收购", "并购", "私有化"]):
        return "被收购"
    if any(k in rnd for k in ["轮", "Pre", "天使", "种子"]):
        return "融资中"
    return "未披露"

def year_from(s):
    m = re.search(r"(19|20)\d{2}", str(s or ""))
    return int(m.group()) if m else (s or "")

def apply_research(e, r):
    # founded / hq
    e["founded"] = year_from(r.get("founded_verified"))
    if r.get("hq"):
        e["hq"] = r["hq"]
    if r.get("one_liner"):
        e["desc_cn"] = r["one_liner"]
    if r.get("key_products"):
        e["highlights"] = r["key_products"]
    if r.get("events"):
        e["events"] = r["events"]
    fl = r.get("funding_latest_corrected")
    if fl:
        fl2 = dict(fl)
        disp = f"{fl.get('amount','')} {fl.get('round','')} ({fl.get('date','')})".strip()
        fl2["display"] = disp
        e["funding_latest"] = fl2
    ft = r.get("funding_total_corrected")
    if ft:
        ft2 = dict(ft)
        ft2["display"] = ft.get("amount", "")
        e["funding_total"] = ft2
    if r.get("investors"):
        e["investors"] = r["investors"]
    if r.get("payor_model"):
        e["payor_model"] = r["payor_model"]
    if r.get("business_tags_suggest"):
        bt = e.get("business_tags") or {}
        if not isinstance(bt, dict):
            bt = {}
        bt["role"] = r["business_tags_suggest"].get("role")
        e["business_tags"] = bt
    ln = r.get("latest_news") or []
    if ln:
        nc = e.get("news_coverage") or {}
        if not isinstance(nc, dict):
            nc = {}
        lst = nc.get("latest_news") or []
        seen = {x.get("url") for x in lst}
        for n in ln:
            if n.get("url") and n["url"] not in seen:
                lst.append(n); seen.add(n["url"])
        nc["latest_news"] = lst
        e["news_coverage"] = nc
    if r.get("silver_verdict"):
        e["silver_verdict"] = r["silver_verdict"]
    if r.get("silver_reason"):
        e["silver_reason"] = r["silver_reason"]
    e["stage"] = derive_stage(r)
    e["update_time"] = TODAY

def set_recommend(e, rec, signal, rv):
    e["recommend"] = {
        "rec_v1": rec.get("rec_v1"),
        "rec_v2": rec.get("rec_v2"),
        "rec_v3": rec.get("rec_v3"),
        "info_score": rec.get("info_score"),
        "diff_score": rec.get("diff_score"),
        "copy_score": rec.get("copy_score"),
        "signal_strength": signal,
        "research_value": rv,
    }
    e["update_time"] = TODAY
    if rec.get("silver_verdict"):
        e["silver_verdict"] = rec["silver_verdict"]

# ---- 30-new：research + rec + 重算分 ----
miss_r = [s for s in new30 if s not in research_map]
miss_c = [s for s in new30 if s not in rec30_map]
print("30-new 缺 research:", miss_r)
print("30-new 缺 rec:", miss_c)
for s in new30:
    e = db_by.get(s)
    if not e:
        print("  !! 未找到", s); continue
    r = research_map.get(s)
    rec = rec30_map.get(s)
    if r:
        apply_research(e, r)
    if rec and s in all_signals:
        sig = all_signals[s]
        info = float(rec.get("info_score") or 0)
        diff = float(rec.get("diff_score") or 0)
        copy = float(rec.get("copy_score") or 0)
        rv = round((sig * 0.3 + info * 0.3 + diff * 0.2 + copy * 0.2) * 10, 1)
        e["signal_strength"] = sig
        e["research_value"] = rv
        if rec.get("silver_verdict"):
            e["silver_verdict"] = rec["silver_verdict"]
        if rec.get("silver_reason"):
            e["silver_reason"] = rec["silver_reason"]
        if "recommend" in e and isinstance(e["recommend"], dict):
            e["recommend"].update({
                "rec_v1": rec.get("rec_v1"), "rec_v2": rec.get("rec_v2"), "rec_v3": rec.get("rec_v3"),
                "info_score": info, "diff_score": diff, "copy_score": copy,
                "signal_strength": sig, "research_value": rv,
            })
        else:
            set_recommend(e, rec, sig, rv)

# ---- 25 pilot：只更新 recommend 字典 + 银发判定 + 重算 research_value ----
miss_p = [s for s in pilot if s not in rec_pilot_map]
print("pilot 缺 rec:", miss_p)
for s in pilot:
    e = db_by.get(s)
    if not e:
        print("  !! 未找到", s); continue
    rec = rec_pilot_map.get(s)
    if not rec:
        continue
    sig = e.get("signal_strength")
    if sig is None and s in all_signals:
        sig = all_signals[s]
    info = float(rec.get("info_score") or 0)
    diff = float(rec.get("diff_score") or 0)
    copy = float(rec.get("copy_score") or 0)
    if sig is not None:
        rv = round((sig * 0.3 + info * 0.3 + diff * 0.2 + copy * 0.2) * 10, 1)
        e["research_value"] = rv
    else:
        rv = e.get("research_value")
    if rec.get("silver_verdict"):
        e["silver_verdict"] = rec["silver_verdict"]
    if rec.get("silver_reason"):
        e["silver_reason"] = rec["silver_reason"]
    set_recommend(e, rec, sig, rv)

# ---- after 快照 ----
after_snap = {s: db_by[s] for s in (new30 + pilot) if s in db_by}
save(os.path.join(SD, "after_snapshot.json"), after_snap)

# ---- 写回 DB ----
save(DB_PATH, db)
print("DB 已更新。30-new:", len(new30), "pilot:", len(pilot))
print("research 覆盖:", len([s for s in new30 if s in research_map]), "/30")
print("rec30 覆盖:", len([s for s in new30 if s in rec30_map]), "/30")
print("rec_pilot 覆盖:", len([s for s in pilot if s in rec_pilot_map]), "/25")
