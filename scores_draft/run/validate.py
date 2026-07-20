# -*- coding: utf-8 -*-
import json, os, re

out_dir = os.path.join(os.path.dirname(__file__), "out")
SIG = 0.55

signal_kw = ["信号"]
info_kw = ["信息","资料","披露","数据","销量","粉丝","年份","成立","资质","背景","合作","融资","排名","始创","创立","落地","产能","认证","投资"]
diff_kw = ["差异化","亮点","定位","切","模式","角度","新","首创","壁垒","独特","强","清晰","定位新","避开","标杆","排名"]
copy_kw = ["复制","借鉴","可学","学其","抄","可借鉴","可抄"]

problems = []
for b in ["39","40","41"]:
    fp = os.path.join(out_dir, f"batch_{b}_out.json")
    with open(fp, encoding="utf-8") as f:
        o = json.load(f)
    assert o["batch"] == int(b)
    for e in o["enterprises"]:
        s = e["serial"]
        for k in ["info_score","diff_score","copy_score"]:
            v = e[k]
            assert isinstance(v,(int,float)) and 0<=v<=10, f"{s} {k}={v} out of range"
        assert 0<=e["signal_strength"]<=10
        rv = round((SIG*0.3 + e["info_score"]*0.3 + e["diff_score"]*0.2 + e["copy_score"]*0.2)*10,1)
        if abs(rv - e["research_value"]) > 1e-9:
            problems.append(f"{s}: research_value mismatch calc={rv} got={e['research_value']}")
        rc = e["recommend"]
        for kk in ["info_score","diff_score","copy_score","signal_strength"]:
            if rc[kk] != e[kk]:
                problems.append(f"{s}: recommend.{kk} mismatch")
        if abs(rc["research_value"]-e["research_value"])>1e-9:
            problems.append(f"{s}: recommend.research_value mismatch")
        recs = [rc["rec_v1"], rc["rec_v2"], rc["rec_v3"]]
        if len(set(recs))<3:
            problems.append(f"{s}: 3 recs not distinct")
        for i,r in enumerate(recs,1):
            if not r or not r.strip():
                problems.append(f"{s}: rec_v{i} empty")
                continue
            L = len(r)
            if L<40 or L>90:
                problems.append(f"{s}: rec_v{i} length {L} (need 40-90): {r}")
            # dimension coverage
            has_sig = any(w in r for w in signal_kw)
            has_info = any(w in r for w in info_kw)
            has_diff = any(w in r for w in diff_kw)
            has_copy = any(w in r for w in copy_kw)
            missing = [n for n,ok in [("信号",has_sig),("信息",has_info),("差异",has_diff),("复制",has_copy)] if not ok]
            if missing:
                problems.append(f"{s}: rec_v{i} missing dims {missing} -> {r}")
        # required non-empty
        for fld in ["payor_model","business_tags_role","silver_verdict","update_time"]:
            if not e[fld]:
                problems.append(f"{s}: {fld} empty")
        if e["update_time"] != "2026-07-17":
            problems.append(f"{s}: update_time={e['update_time']}")
        if e["silver_verdict"] not in ("核心银发","泛医疗擦边","非银发"):
            problems.append(f"{s}: bad verdict {e['silver_verdict']}")
        if not isinstance(e["highlights"],list) or not (2<=len(e["highlights"])<=4):
            problems.append(f"{s}: highlights count {len(e.get('highlights',[]))}")
        if e["stage"] != "未披露":
            problems.append(f"{s}: stage={e['stage']} (expected 未披露)")
    # nonsilver consistency
    ns = {x["serial"] for x in o["nonsilver"]}
    for e in o["enterprises"]:
        if e["silver_verdict"] in ("非银发","泛医疗擦边"):
            if e["serial"] not in ns:
                problems.append(f"{s if (s:=e['serial']) else e['serial']}: verdict nonsilver but missing in nonsilver list")
        else:
            if e["serial"] in ns:
                problems.append(f"{e['serial']}: core silver but in nonsilver list")

print("PROBLEMS:", len(problems))
for p in problems:
    print(" -", p)
print("OK" if not problems else "HAS ISSUES")
