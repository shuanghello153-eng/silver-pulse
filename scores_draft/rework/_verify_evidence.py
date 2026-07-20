# -*- coding: utf-8 -*-
"""证据脚本：企业库返工核验（小白可复现）
用法：PYTHONIOENCODING=utf-8 python _verify_evidence.py
输出全为磁盘实测，无记忆/无估算。
"""
import json, re, glob, collections, os

BASE = "../../data/enterprise/all_enterprises.json"
DB = json.load(open(BASE, encoding="utf-8"))
by = {e["serial"]: e for e in DB}

# 读草稿
dv = {}
for f in glob.glob("drafts_v4/*.json"):
    try:
        j = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    ser = j.get("serial") or j.get("企业序号")
    if ser:
        dv[ser] = j

def cl(s):
    return len(re.sub(r"\s", "", s or "")) if isinstance(s, str) else 0

# ─────────────────────────────────────────────
# 1) 草稿推荐理由硬指标（我自己跑的，不是上一个AI的结论）
# ─────────────────────────────────────────────
print("=" * 60)
print("【证据1】草稿推荐理由文本质量（覆盖 %d 家，磁盘实测）" % len(dv))
TEMPLATE_SIGS = ["信号偏弱、信息量一般", "复制需结合本地资源", "轻模式易复制，国内创业者可直接借鉴落地",
                 "切入行业媒体赛道", "国内宜学其思路而非形态", "信息量一般", "信号偏弱", "整体信号偏弱"]
n_num = n_ref = n_diff = n_tmpl = 0
lens = []
for ser, j in dv.items():
    r = j.get("recommend") or j.get("推荐理由")
    if isinstance(r, str) and r.strip():
        lens.append(cl(r))
        if re.search(r"\d", r): n_num += 1
        if re.search(r"对标|借鉴|国内|对比|差异|参考", r): n_ref += 1
        if re.search(r"差异|独特|壁垒|模式|不同于|而非|护城河", r): n_diff += 1
        if any(t in r for t in TEMPLATE_SIGS): n_tmpl += 1
lens.sort()
print("  有具体数字        : %d / %d (%.0f%%)" % (n_num, len(lens), 100*n_num/len(lens)))
print("  有'对标/借鉴/国内' : %d / %d (%.0f%%)" % (n_ref, len(lens), 100*n_ref/len(lens)))
print("  有'差异/模式/壁垒' : %d / %d (%.0f%%)" % (n_diff, len(lens), 100*n_diff/len(lens)))
print("  仍命中模板套话签名 : %d / %d" % (n_tmpl, len(lens)))
print("  字数 最小/中位/最大: %d / %d / %d" % (lens[0], lens[len(lens)//2], lens[-1]))

# ─────────────────────────────────────────────
# 2) 把草稿合并进主库上下文后，全部门禁规则逐项统计
#    区分「推荐理由本身的规则」vs「卡片背景字段规则(R6/R7/R8)」
# ─────────────────────────────────────────────
import sys
sys.path.insert(0, ".")
from check_single import validate, CANON

RECOMMEND_RULES = {"R1", "R2", "R3", "R4", "R5", "R-name", "R-field-dedup",
                   "R-integrity", "R-novelty", "R-jargon", "R-noabs"}
BACKGROUND_RULES = {"R6", "R7", "R8"}

rule_counter = collections.Counter()
fail_recommend_only = 0
fail_background_only = 0
fail_both = 0
pass_full = 0
cover = 0
for ser, e in by.items():
    # 用草稿覆盖 recommend（若有）
    if ser in dv:
        r = dv[ser].get("recommend") or dv[ser].get("推荐理由")
        if isinstance(r, str) and r.strip():
            e = dict(e)
            e["recommend"] = r
            cover += 1
    iss = validate(e, None, skip={"R10"})
    if not iss:
        pass_full += 1
        continue
    rec_fail = any(i.split(":")[0] in RECOMMEND_RULES for i in iss)
    bg_fail = any(i.split(":")[0] in BACKGROUND_RULES for i in iss)
    for i in iss:
        rule_counter[i.split(":")[0]] += 1
    if rec_fail and not bg_fail: fail_recommend_only += 1
    elif bg_fail and not rec_fail: fail_background_only += 1
    else: fail_both += 1

print("\n" + "=" * 60)
print("【证据2】草稿合并后全库门禁（跳过R10跨企业，1502家，磁盘实测）")
print("  草稿已覆盖推荐理由家数 : %d" % cover)
print("  全部门禁通过           : %d" % pass_full)
print("  仅'推荐理由规则'不达标 : %d" % fail_recommend_only)
print("  仅'背景字段规则'不达标 : %d" % fail_background_only)
print("  两类都不达标           : %d" % fail_both)
print("  --- 各规则命中家数（一家可命中多规则）---")
for k in ["R1","R2","R3","R4","R5","R-name","R-field-dedup","R-integrity","R-novelty","R-jargon","R-noabs","R6","R7","R8"]:
    if rule_counter.get(k):
        tag = "【推荐理由】" if k in RECOMMEND_RULES else "【背景字段】"
        print("    %s %s : %d" % (tag, k, rule_counter[k]))

# ─────────────────────────────────────────────
# 3) 误杀证据：推荐理由写得好，只被 R-field-dedup / R-integrity 误杀
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("【证据3】误杀案例：推荐理由本身达标，仅被去重/一致性规则误杀")
shown = 0
for ser, e in by.items():
    if ser not in dv: continue
    r = dv[ser].get("recommend") or dv[ser].get("推荐理由")
    if not (isinstance(r, str) and r.strip()): continue
    e2 = dict(e); e2["recommend"] = r
    iss = validate(e2, None, skip={"R10"})
    if not iss: continue
    rules = {i.split(":")[0] for i in iss}
    only_mis = rules <= {"R-field-dedup", "R-integrity"} and rules
    if only_mis and shown < 3:
        shown += 1
        print("\n  ■ 序号 %s | %s" % (ser, e.get("name_cn") or e.get("name")))
        print("    推荐理由(%d字): %s" % (cl(r), r))
        print("    被判: %s" % " / ".join(i for i in iss if i.split(":")[0] in only_mis))
        # 找出雷同的字段
        if "R-field-dedup" in rules:
            for fname, ftext in [("desc_cn", e.get("desc_cn")), ("silver_reason", e.get("silver_reason"))]:
                if ftext:
                    from check_single import lcs_len
                    ov = lcs_len(r, ftext)
                    if ov >= 8:
                        print("    └ 与 %s 雷同 %d字，原文片段: %s" % (fname, ov, ftext[:80]))

# ─────────────────────────────────────────────
# 4) payor_model 真实分布 + 归一化映射提案
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("【证据4】payor_model 真实分布（1502家，磁盘实测）")
pm_counter = collections.Counter()
empty_pm = 0
for e in DB:
    pm = e.get("payor_model", "")
    if pm is None or (isinstance(pm, str) and pm.strip() == ""):
        empty_pm += 1
        pm_counter["（空）"] += 1
    else:
        pm_counter[str(pm)] += 1
print("  非规范值家数 : %d" % sum(v for k,v in pm_counter.items() if k not in CANON))
print("  空值家数     : %d" % empty_pm)
print("  --- Top 20 取值 ---")
for k, v in pm_counter.most_common(20):
    mark = "✓规范" if k in CANON else "✗待归一"
    print("    [%s] %s : %d" % (mark, k, v))

# 归一化提案：把 '/' 换成 '+'，规范化词序
def normalize_pm(pm):
    if not isinstance(pm, str): return None
    s = pm.strip()
    if s == "": return None
    s = s.replace("/", "+")
    parts = [p.strip() for p in s.split("+") if p.strip()]
    order = ["个人自费", "政府补贴", "长护险", "医保", "B端机构采购", "政府付费", "政府/商保支付"]
    def keyf(p):
        for i, o in enumerate(order):
            if o in p: return i
        return 99
    parts = sorted(set(parts), key=keyf)
    norm = "+".join(parts)
    return norm

# 试归一化后能救多少
canon_after = collections.Counter()
salvaged = 0
examples = []
for e in DB:
    pm = e.get("payor_model", "")
    if pm in CANON:
        canon_after[pm] += 1
        continue
    n = normalize_pm(pm)
    if n in CANON:
        salvaged += 1
        canon_after[n] += 1
        if len(examples) < 6:
            examples.append((pm, n))
    else:
        canon_after["(仍不规范)" + str(n)] += 1
print("\n  归一化映射后可救回 : %d 家" % salvaged)
print("  --- 归一化示例（原值 → 规范值）---")
for a, b in examples:
    print("    %s  →  %s" % (a, b))

# ─────────────────────────────────────────────
# 5) before/after 对比：主库 dict 垃圾 vs 草稿推荐理由
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("【证据5】前后对比：主库现状(乱码) → 草稿(真实文案)，各抽1例")
picked = 0
for ser in ["#0001", "#0009", "#0501"]:
    if ser in by and ser in dv:
        e = by[ser]
        old = e.get("recommend")
        new = dv[ser].get("recommend") or dv[ser].get("推荐理由")
        print("\n  ■ %s | %s" % (ser, e.get("name_cn") or e.get("name")))
        print("    改前(主库):", repr(old)[:120])
        print("    改后(草稿):", new)
        picked += 1

print("\n[END] 以上全部为磁盘实测，可复现。")
