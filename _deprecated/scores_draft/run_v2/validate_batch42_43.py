# -*- coding: utf-8 -*-
import json, os, re

OUT = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run_v2/out"

NAMES = ["江南米道","沐恒","泰一健康","泰康","泰心","泽普","海之声","海森林","深纳普思","添康","温州康宁",
         "爱侬","爱可声","爱普雷德","爱牵挂","爱舒乐","爱风尚","玖益","玛士撒拉","环球捕手","瑞光康泰","瑞尔","瑞贝卡"]

STAGE_OK = {"种子期","天使","Pre-A","A轮","B轮","C轮","成长期","已上市","被收购","未搜到"}

# forbidden template phrases (substring checks)
FORBID = ["切入X赛道","切入X市场","切入X领域","结合本地资源","结合国内资源","结合本土资源",
          "部分环节可借鉴","部分环节可参考","有一定差异点","有一定亮点","有一定特色",
          "复制需结合本地资源","值得关注","且轻模式易复制","易复制","其[某行业]有一定前景"]

ROUND_TOKENS = ["天使轮","Pre-A","A轮","B轮","C轮","种子期","成长期","已上市"]

def has_year(s):
    return bool(re.search(r"(19|20)\d{2}年", s))

problems = []
def check(batch):
    path = os.path.join(OUT, "batch_%03d_out.json" % batch)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for e in data["enterprises"]:
        s = e["serial"]
        rec = e["recommend"]
        dc = e["desc_cn"]
        rl = len(rec)
        dl = len(dc)
        # length
        if not (80 <= rl <= 200):
            problems.append(f"[{s}] recommend长度={rl} (需80-200)")
        if not (50 <= dl <= 150):
            problems.append(f"[{s}] desc_cn长度={dl} (需50-150)")
        # four dims
        if "信号" not in rec:
            problems.append(f"[{s}] recommend缺信号组词")
        if not re.search(r"信息|资料|披露|数据|透明度|公开", rec):
            problems.append(f"[{s}] recommend缺信息组词")
        if not re.search(r"差异|独特|打法|模式|定位|反常识|壁垒|亮点", rec):
            problems.append(f"[{s}] recommend缺差异组词")
        if not re.search(r"复制|借鉴|可学|照搬|落地|国内|抄", rec):
            problems.append(f"[{s}] recommend缺复制组词")
        # forbidden template
        for fb in FORBID:
            if fb in rec:
                problems.append(f"[{s}] recommend含禁用模板'{fb}'")
        # name in recommend (company name)
        for n in NAMES:
            if n in rec:
                problems.append(f"[{s}] recommend含企业名'{n}'")
        # founding year / round in recommend
        if has_year(rec):
            problems.append(f"[{s}] recommend含年份/可能含成立年份: {rec}")
        if any(tok in rec for tok in ROUND_TOKENS):
            problems.append(f"[{s}] recommend含融资轮次词")
        # stage whitelist
        if e.get("stage") not in STAGE_OK:
            problems.append(f"[{s}] stage不在白名单: {e.get('stage')}")
        # payor non-empty
        if not e.get("payor_model"):
            problems.append(f"[{s}] payor_model为空")
        # desc_cn no name / no 成立于 / no founding year
        for n in NAMES:
            if n in dc:
                problems.append(f"[{s}] desc_cn含企业名'{n}'")
        if "成立于" in dc:
            problems.append(f"[{s}] desc_cn含'成立于'")
        if has_year(dc):
            problems.append(f"[{s}] desc_cn含年份(可能成立年份): {dc}")
        # all fields non-empty-ish
        for k in ["recommend","desc_cn","payor_model","business_tags_role","stage","silver_verdict","silver_reason","数据来源"]:
            if not e.get(k):
                problems.append(f"[{s}] 字段{k}为空")
    # tag_review / nonsilver sanity
    print(f"batch {batch}: enterprises={len(data['enterprises'])} tag_review={len(data.get('tag_review',[]))} nonsilver={len(data.get('nonsilver',[]))}")
    for ns in data.get("nonsilver",[]):
        print("   nonsilver:", ns["serial"], ns["name"], ns["verdict"])

for b in (42,43):
    check(b)

if problems:
    print("\n=== PROBLEMS ===")
    for p in problems:
        print(p)
    print(f"\n共 {len(problems)} 个问题")
else:
    print("\nALL OK ✅ 全部通过V3自检")
