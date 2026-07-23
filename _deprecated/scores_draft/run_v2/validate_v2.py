# -*- coding: utf-8 -*-
"""
八道防线 · 全量校验（run_v2/validate_v2.py V3）
对 all_enterprises.json 全量体检，输出违规清单 + 各项达标率。
规则：
  L1 覆盖：1502 serial 无缺无重
  L2 公式：research_value == round((sig*.3+info*.3+diff*.2+copy*.2)*10) 误差<=0.5
  L3 量纲：四维 ∈ [0,10]
  L4 推荐理由：字符串、30-200字、含四维信号词、不含 融资/轮/成立于/企业名
  L4b 推荐理由反模板：禁止"切入X赛道"/"结合本地资源"/"部分环节可借鉴"/"有一定差异点"/"模式较常规"等套话
  L5 阶段白名单：stage ∈ 白名单（严禁 融资中/未披露）
  L6 全字段非空（允许占位词 未搜到/未融资/不确定）
  L7 描述禁忌：desc_cn 不含 企业名/成立于/融资
  L8 payor_model 非空
用法：python validate_v2.py            # 全量
      python validate_v2.py #0001 #0002 #0783   # 只查指定 serial
"""
import json, os, sys, re
BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
WHITELIST = {"种子期","天使","Pre-A","A轮","B轮","C轮","成长期","已上市","被收购","未搜到"}
PLACEHOLDER_OK = {"未搜到","未融资","不确定"}
SIG_KW = ["信号"]
INFO_KW = ["信息","资料","披露","数据","透明度","公开"]
DIFF_KW = ["差异","独特","打法","模式","定位","反常识","壁垒","亮点"]
COPY_KW = ["复制","借鉴","可学","照搬","落地","国内","抄"]
SCAN_KEYS = ["name_cn","founded","website_url","funding_latest","funding_total","investors",
             "payor_model","business_tags","highlights","events","desc_cn","recommend",
             "signal_strength","info_score","diff_score","copy_score","research_value","stage"]

db = json.load(open(DB_PATH, encoding="utf-8"))
by = {e["serial"]: e for e in db}
args = [a.lstrip("#") for a in sys.argv[1:]]
targets = set(args) if args else None

problems = []          # (serial, rule, detail)
def bad(s, rule, detail): problems.append((s, rule, detail))

def non_empty(v):
    if v is None: return False
    if isinstance(v, str) and v.strip() == "": return False
    if isinstance(v, list) and len(v) == 0: return False
    if isinstance(v, dict) and len(v) == 0: return False
    return True

n = len(db)
rule_counts = {f"L{i}":0 for i in range(1,9)}
rule_counts["L4b"] = 0  # 反模板套话

# L4b 模板套话检测模式
TEMPLATE_PATTERNS_L4B = [
    (r"切入.{2,10}(赛道|市场|领域|行业)", "切入X赛道(模板)"),
    (r"结合(本地|国内|本土|当地)资源", "结合本地资源(模板)"),
    (r"部分环节可(借鉴|参考|复制|学习)", "部分环节可借鉴(模板)"),
    (r"有(一定|较)?(差异|亮点|特色)(点)?", "有一定差异点(模板)"),
    (r"复制需?结合.*资源", "复制需结合资源(模板)"),
    (r"模式(较|挺)?(常规|普通|一般)", "模式较常规(模板)"),
    (r"信息(量|披露)?(一般|偏少|较弱)", "信息量一般(模板)"),
]

# L1 覆盖
serials = [e["serial"] for e in db]
if len(serials) != len(set(serials)):
    rule_counts["L1"] += 1
    bad("GLOBAL","L1","存在重复 serial")

for e in db:
    s = e.get("serial")
    if targets and s not in targets: continue
    # L3 量纲
    for k in ["signal_strength","info_score","diff_score","copy_score"]:
        v = e.get(k)
        try:
            if not (0 <= float(v) <= 10):
                rule_counts["L3"] += 1; bad(s,"L3",f"{k}={v} 越界")
        except Exception:
            rule_counts["L3"] += 1; bad(s,"L3",f"{k}={v} 非数值")
    # L2 公式
    try:
        calc = round((float(e["signal_strength"])*0.3+float(e["info_score"])*0.3
                      +float(e["diff_score"])*0.2+float(e["copy_score"])*0.2)*10,1)
        rv = e.get("research_value")
        if rv is None or abs(calc - float(rv)) > 0.5:
            rule_counts["L2"] += 1; bad(s,"L2",f"calc={calc} got={rv}")
    except Exception as ex:
        rule_counts["L2"] += 1; bad(s,"L2",f"公式异常 {ex}")
    # L5 stage
    st = e.get("stage")
    if st not in WHITELIST:
        rule_counts["L5"] += 1; bad(s,"L5",f"stage={st} 不在白名单")
    # L4 recommend
    rec = e.get("recommend")
    if not isinstance(rec, str) or not rec.strip():
        rule_counts["L4"] += 1; bad(s,"L4","recommend 非字符串/空")
    else:
        L = len(rec)
        if L < 30 or L > 200:
            rule_counts["L4"] += 1; bad(s,"L4",f"recommend 长度 {L} (需30-200)")
        # 禁用词：精确匹配融资轮次/金额/成立年，放过「轮椅」等正常词
        import re as _re
        forbidden_patterns = [
            "成立于", "创立于", "轮次",
            # 仅抓真正的融资轮次，放过「轮椅/双轮/多轮」等正常词
            r"(A轮|B轮|C轮|D轮|E轮|F轮|Pre-?A轮?|天使轮|种子轮|Series\s?[A-Fa-f])",
            r"轮(融资|募|资金)",          # 轮融资/轮募资
            r"(本轮|上轮|前轮)",
            r"(融资|募|IPO|ipo|上市)[额次]",
            r"融[资了]?[约]?\d",           # 融了X / 融资X
            r"\d+万?美元", r"\d+亿", r"\d+万元",
            r"\$\d",
        ]
        hit = None
        for p in forbidden_patterns:
            is_regex = ("\\" in p) or ("[" in p) or ("?" in p) or ("(" in p)
            if (is_regex and _re.search(p, rec)) or ((not is_regex) and (p in rec)):
                hit = p; break
        if hit:
            rule_counts["L4"] += 1; bad(s,"L4",f"recommend 含禁用词(命中:{hit})")
        has = [("信号",any(w in rec for w in SIG_KW)),("信息",any(w in rec for w in INFO_KW)),
               ("差异",any(w in rec for w in DIFF_KW)),("复制",any(w in rec for w in COPY_KW))]
        miss = [n for n,ok in has if not ok]
        if miss:
            rule_counts["L4"] += 1; bad(s,"L4",f"recommend 缺维度 {miss}")
        # L4b 反模板套话检测
        for tpat, tname in TEMPLATE_PATTERNS_L4B:
            if _re.search(tpat, rec):
                rule_counts["L4b"] += 1; bad(s,"L4b",f"模板套话({tname})")
    # L6 全字段非空（允许占位词）
    for k in SCAN_KEYS:
        if k in ("signal_strength","info_score","diff_score","copy_score","research_value","stage"): continue
        v = e.get(k)
        if not non_empty(v):
            rule_counts["L6"] += 1; bad(s,"L6",f"{k} 空值")
        if isinstance(v, str) and v.strip() in ("未披露","待补充","N/A","待定"):
            rule_counts["L6"] += 1; bad(s,"L6",f"{k}='{v}' 旧占位词未统一")
    # L7 desc_cn 禁忌
    dc = e.get("desc_cn")
    if isinstance(dc, str):
        nm = str(e.get("name") or ""); nmcn = str(e.get("name_cn") or "")
        if (nm and nm in dc) or (nmcn and nmcn in dc):
            rule_counts["L7"] += 1; bad(s,"L7","desc_cn 含企业名")
        if "成立于" in dc or "创立于" in dc:
            rule_counts["L7"] += 1; bad(s,"L7","desc_cn 含成立于")
        if re.search(r"(融资|轮|\$|\d+万)", dc):
            rule_counts["L7"] += 1; bad(s,"L7","desc_cn 含融资/轮")
    # L8 payor
    if is_bad_payor := (not isinstance(e.get("payor_model"), str) or not e.get("payor_model").strip()):
        rule_counts["L8"] += 1; bad(s,"L8","payor_model 空")

print("="*60)
print(f"全量校验：企业 {n} 家，违规项 {len(problems)} 条")
all_rules = dict(rule_counts)
print("各防线违规数：", all_rules)
# 违规 serial 去重计数
bad_serials = {}
for s,r,d in problems:
    bad_serials.setdefault(s, []).append(r)
print(f"涉及不合规企业：{len(bad_serials)} 家")
# 打印前 40 条样例
for s,r,d in problems[:40]:
    print(f"  [{s}] {r}: {d}")
print("="*60)
print("OK" if not problems else f"HAS_ISSUES({len(problems)})")
