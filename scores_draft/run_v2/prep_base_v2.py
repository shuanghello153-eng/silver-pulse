# -*- coding: utf-8 -*-
"""
确定性基线：把全部 1502 家企业按新质量标准做一次"不联网"的字段落地。
- 合并 in-flight 旧产物（batches 45-59 的 legacy out）进库
- stage 白名单化（融资中/未披露 -> 从 funding 推导或"未搜到"）
- 占位词统一（未披露/待补充/N/A -> 未搜到；无融资 -> 未融资）
- research_value 当场重算
- payor_model 规则化推导（缺失时）
- desc_cn 坏值改写 / 缺失生成
- recommend 三版字典 -> 单字符串（基线融合版）
- update_time = 2026-07-17

写库前先备份 before_v2.json（可回滚）。只写"我的键"，绝不碰 tag_l1/l2/category/tags。
"""
import json, os, re, copy

BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
RUN = os.path.join(BASE, "scores_draft/run")
RUNV2 = os.path.join(BASE, "scores_draft/run_v2")
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")

WHITELIST_STAGE = {"种子期","天使","Pre-A","A轮","B轮","C轮","成长期","已上市","被收购","未搜到"}
PLACEHOLDER_BAD = {"", "未披露", "待补充", "待定", "N/A", "n/a", "NA", "null", "None", "无", "暂无", "—", "-"}
TODAY = "2026-07-17"

db = json.load(open(DB_PATH, encoding="utf-8"))
by = {e["serial"]: e for e in db}

# 备份
json.dump(db, open(os.path.join(RUNV2, "before_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- 合并 in-flight legacy out（45-59）----
def clamp(v, lo=0, hi=10):
    try: v = float(v)
    except Exception: return lo
    return max(lo, min(hi, v))

def recompute(sig, info, diff, copy):
    return round((sig*0.3 + info*0.3 + diff*0.2 + copy*0.2) * 10, 1)

legacy_merged = 0
for b in range(45, 60):
    fp = os.path.join(RUN, "out", f"batch_{b:03d}_out.json")
    if not os.path.exists(fp):
        fp = os.path.join(RUN, "out", f"batch_{b}_out.json")
    if not os.path.exists(fp):
        continue
    o = json.load(open(fp, encoding="utf-8"))
    for ent in o.get("enterprises", []):
        s = ent.get("serial"); e = by.get(s)
        if not e: continue
        sig = clamp(ent.get("signal_strength", e.get("signal_strength", 0)))
        info = clamp(ent.get("info_score"))
        diff = clamp(ent.get("diff_score"))
        copy = clamp(ent.get("copy_score"))
        rv = recompute(sig, info, diff, copy)
        e["signal_strength"] = sig; e["info_score"] = info; e["diff_score"] = diff
        e["copy_score"] = copy; e["research_value"] = rv
        if ent.get("payor_model"): e["payor_model"] = ent["payor_model"]
        if ent.get("desc_cn"): e["desc_cn"] = ent["desc_cn"]
        if ent.get("founded") is not None: e["founded"] = ent["founded"]
        if ent.get("stage"): e["stage"] = ent["stage"]
        if ent.get("highlights") is not None: e["highlights"] = ent["highlights"]
        if ent.get("events") is not None: e["events"] = ent["events"]
        if ent.get("silver_verdict"): e["silver_verdict"] = ent["silver_verdict"]
        if ent.get("silver_reason"): e["silver_reason"] = ent["silver_reason"]
        # legacy recommend 字典 -> 暂存，后面统一融合为字符串
        e["_legacy_rec"] = ent.get("recommend")
        legacy_merged += 1
print("legacy inflight 合并:", legacy_merged)

# ---- 工具函数 ----
def is_bad(v):
    if v is None: return True
    if isinstance(v, str) and v.strip() in PLACEHOLDER_BAD: return True
    if isinstance(v, list) and len(v) == 0: return True
    if isinstance(v, dict) and not v: return True
    return False

def get_round(e):
    fl = e.get("funding_latest")
    if isinstance(fl, dict):
        return str(fl.get("round", "") or "")
    return str(fl or "")

def derive_stage(e):
    cur = e.get("stage")
    if isinstance(cur, str) and cur.strip() in WHITELIST_STAGE:
        return cur.strip()
    rnd = get_round(e)
    rules = [
        (["ipo","上市","纳斯达克","纽交所","港交所","nyse","nasdaq","hkex","主板","敲钟"], "已上市"),
        (["收购","并购","私有化","acqui","m&a","ma "], "被收购"),
        (["series d","d轮","d+","e轮","f轮","growth","成长期","战略融资","战略投资"], "成长期"),
        (["series c","c轮","c+"], "C轮"),
        (["series b","b轮","b+"], "B轮"),
        (["series a","a轮","a+"], "A轮"),
        (["pre-a","prea"], "Pre-A"),
        (["seed","种子"], "种子期"),
        (["angel","天使"], "天使"),
    ]
    low = rnd.lower()
    for kws, st in rules:
        if any(k in low for k in kws):
            return st
    # 有融资但认不出阶段词 -> 成长期（常见默认）
    if rnd and rnd.strip() not in ("", "未融资", "未搜到"):
        return "成长期"
    return "未搜到"

def has_funding(e):
    fl = e.get("funding_latest")
    if isinstance(fl, dict):
        return bool(fl.get("round") or fl.get("amount"))
    return bool(fl) and str(fl).strip() not in ("", "未融资", "未搜到")

def infer_payor(e):
    cur = e.get("payor_model")
    if not is_bad(cur):
        return cur
    text = " ".join(str(x) for x in [
        e.get("category_l1"), e.get("category_l2"), e.get("business_model"),
        e.get("business_model_cn"), e.get("tags"), e.get("description"), e.get("name_cn")
    ] if x)
    low = text.lower()
    if any(k in low for k in ["保险","insurance","medicare","商保","医保","payer","reimburs"]):
        return "政府医保/商业保险支付"
    if any(k in low for k in ["医院","机构","养老院","护理院","b2b","诊所","health system","provider"]):
        return "B端机构采购/政府买单"
    if any(k in low for k in ["电商","消费品","产品","硬件","device","retail","d2c"]):
        return "个人自费/家庭自费"
    if any(k in low for k in ["居家","陪诊","护理","服务","platform","平台","saas"]):
        return "个人自费+部分政府补贴"
    return "未搜到"

def desc_is_bad(e):
    dc = e.get("desc_cn")
    if is_bad(dc):
        return True
    name = str(e.get("name") or "")
    nmcn = str(e.get("name_cn") or "")
    s = str(dc)
    if name and name in s: return True
    if nmcn and nmcn in s: return True
    if "成立于" in s or "创立于" in s: return True
    if re.search(r"(融资|轮|\$|\d+万|万美元|亿)", s): return True
    if len(s) > 34: return True
    return False

def gen_desc_cn(e):
    # 优先 business_model_cn 做精准短定位
    bmc = e.get("business_model_cn")
    if not is_bad(bmc) and len(str(bmc)) <= 30 and "成立于" not in str(bmc):
        base = str(bmc)
    else:
        cat = e.get("category_l2") or e.get("category_l1") or ""
        bm = e.get("business_model_cn") or e.get("business_model") or ""
        base = f"聚焦{cat}的{bm}" if cat else str(bm)
    base = re.sub(r"(融资|轮|\$|\d+万).*", "", base)
    if "成立于" in base: base = base.split("成立于")[0]
    base = base.strip(" ，,。.")
    if len(base) > 30:
        base = base[:30]
    if not base:
        base = "银发经济相关企业（定位待补充）"
    return base

def level_word(v, hi, mid, lo):
    if v >= 7: return hi
    if v >= 4: return mid
    return lo

def fuse_recommend(e):
    """基线融合：把四维融进一句读者视角的话，指向国内落地。"""
    sig = e.get("signal_strength") or 0
    info = e.get("info_score") or 0
    diff = e.get("diff_score") or 0
    copy = e.get("copy_score") or 0
    bm = e.get("business_model_cn") or e.get("business_model") or e.get("category_l2") or "其模式"
    cat = e.get("category_l2") or e.get("category_l1") or "银发"
    s_sig = level_word(sig, "信号强", "信号中等", "信号偏弱")
    s_info = level_word(info, "信息透明度高", "信息量一般", "公开信息较少")
    s_diff = level_word(diff, f"其「{bm}」打法差异化突出", f"其「{bm}」有一定差异点", f"「{bm}」模式较常规")
    if copy >= 7:
        s_copy = "且轻模式易复制，国内创业者可直接借鉴落地"
    elif copy >= 4:
        s_copy = "复制需结合本地资源，部分环节可借鉴"
    else:
        s_copy = "但受支付体系/牌照/文化约束，照搬难，国内宜学其思路而非形态"
    return f"{s_sig}、{s_info}，{s_diff}；{s_copy}（切入{cat}赛道）。"

# ---- 主循环：全部 1502 ----
for e in db:
    s = e.get("serial")
    # 分数：已评的保留；未评的先做规则化基线估算
    sig = e.get("signal_strength")
    if sig is None:
        sig = 0.55
        e["signal_strength"] = sig
    sig = clamp(sig)
    info = e.get("info_score"); diff = e.get("diff_score"); copy = e.get("copy_score")
    if info is None or diff is None or copy is None:
        # 规则化估算（基线，质量波次会精修高价值批）
        f = has_funding(e)
        fl_amt = ""
        if isinstance(e.get("funding_latest"), dict):
            fl_amt = str(e.get("funding_latest", {}).get("amount", ""))
        big = bool(re.search(r"(亿|亿美|亿美|100.?万|series [c-z]|c轮|d轮|ipo|上市)", fl_amt.lower() + " " + get_round(e).lower()))
        if e.get("stage") in ("已上市",) or big:
            info = 8.5
        elif f:
            info = 6.0
        elif e.get("website_url") and not is_bad(e.get("website_url")):
            info = 5.0
        else:
            info = 3.5
        bm_low = " ".join(str(x) for x in [e.get("business_model"), e.get("business_model_cn"), e.get("category_l1"), e.get("category_l2")]).lower()
        if any(k in bm_low for k in ["ai","平台","闭环","保险","机器人","陪伴","首","unique","platform"]):
            diff = 7.5
        elif any(k in bm_low for k in ["养老","辅具","常规","standard"]):
            diff = 4.5
        else:
            diff = 5.5
        if any(k in bm_low for k in ["产品","消费","d2c","电商","saas","平台"]):
            copy = 7.5
        elif any(k in bm_low for k in ["保险","医保","医院","机构","重资产","regulat"]):
            copy = 3.5
        else:
            copy = 5.5
        e["info_score"] = info; e["diff_score"] = diff; e["copy_score"] = copy
    e["research_value"] = recompute(sig, clamp(info), clamp(diff), clamp(copy))

    # stage 白名单化
    e["stage"] = derive_stage(e)

    # 占位词统一
    if is_bad(e.get("name_cn")):
        e["name_cn"] = e.get("name") or "未搜到"
    if is_bad(e.get("website_url")):
        e["website_url"] = "未搜到"
    if is_bad(e.get("founded")):
        e["founded"] = "未搜到"
    # funding
    if not has_funding(e):
        if isinstance(e.get("funding_latest"), dict):
            e["funding_latest"] = "未融资"
        elif is_bad(e.get("funding_latest")):
            e["funding_latest"] = "未融资"
        if is_bad(e.get("funding_total")):
            e["funding_total"] = "未融资"
        if is_bad(e.get("investors")):
            e["investors"] = ["未融资"]
    else:
        # 有融资但投资方/总额未知 -> 诚实占位
        if is_bad(e.get("investors")):
            e["investors"] = ["未搜到"]
        if is_bad(e.get("funding_total")):
            e["funding_total"] = "未搜到"
    # payor
    e["payor_model"] = infer_payor(e)
    # business_tags.role 兜底
    bt = e.get("business_tags")
    if not isinstance(bt, dict): bt = {}
    if is_bad(bt.get("role")):
        bml = str(e.get("business_model_cn") or e.get("business_model") or "").lower()
        if any(k in bml for k in ["平台","platform"]): bt["role"] = "平台"
        elif any(k in bml for k in ["产品","硬件","device"]): bt["role"] = "产品商"
        elif any(k in bml for k in ["服务","护理","care"]): bt["role"] = "服务商"
        elif any(k in bml for k in ["运营","operator"]): bt["role"] = "运营商"
        else: bt["role"] = "未搜到"
        e["business_tags"] = bt
    # highlights 兜底
    if is_bad(e.get("highlights")):
        e["highlights"] = ["未搜到"]
    # events 兜底（非空，诚实占位）
    if is_bad(e.get("events")):
        e["events"] = ["未搜到"]
    # desc_cn 坏值改写
    if desc_is_bad(e):
        e["desc_cn"] = gen_desc_cn(e)
    # recommend 单字符串：强制按新标准重生成（覆盖一切旧格式/字典）
    e["recommend"] = fuse_recommend(e)
    # silver_verdict 基线默认（保留已有；无则默认核心银发，质量波次修正）
    if is_bad(e.get("silver_verdict")):
        e["silver_verdict"] = "核心银发"
    if is_bad(e.get("silver_reason")):
        e["silver_reason"] = "基线默认判定，待质量波次复核"
    e["update_time"] = TODAY

# 写回
json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("基线落地完成。企业总数:", len(db))
