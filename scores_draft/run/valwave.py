# -*- coding: utf-8 -*-
"""批量自动校验工人 out 文件（替代人工校验员，零模型成本）。
检查：四维区间、research_value 公式、3版理由非空/不超90字/不雷同、
必须字段非空、nonsilver verdict 合法。
用法: python valwave.py 5 6 7 8 9
"""
import json, sys, os
BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run"

def recompute(sig, info, diff, copy):
    return round((sig*0.3 + info*0.3 + diff*0.2 + copy*0.2) * 10, 1)

def validate_batch(b):
    out_p = f"{BASE}/out/batch_{b:03d}_out.json"
    if not os.path.exists(out_p):
        return {"batch": b, "checks": [], "overall_pass": False, "missing": True}
    out = json.load(open(out_p, encoding="utf-8"))
    checks = []
    for e in out["enterprises"]:
        ser = e["serial"]
        issues = []
        sig, info, diff, copy = e["signal_strength"], e["info_score"], e["diff_score"], e["copy_score"]
        for nm, v in [("signal", sig), ("info", info), ("diff", diff), ("copy", copy)]:
            try:
                if not (0 <= float(v) <= 10):
                    issues.append(f"{nm}_score 越界:{v}")
            except Exception:
                issues.append(f"{nm}_score 非法:{v}")
        calc = recompute(float(sig), float(info), float(diff), float(copy))
        if abs(calc - float(e["research_value"])) > 0.06:
            issues.append(f"research_value 不符 out={e['research_value']} calc={calc}")
        rec = e.get("recommend", {})
        vs = []
        for k in ["rec_v1", "rec_v2", "rec_v3"]:
            t = rec.get(k, "") or ""
            vs.append(t)
            if not t.strip():
                issues.append(f"{k} 空")
            elif len(t) > 90:
                issues.append(f"{k} 超90字({len(t)})")
        if len(set(vs)) < 3:
            issues.append("三版推荐理由重复")
        for fld in ["payor_model", "business_tags_role", "silver_verdict", "update_time"]:
            if not str(e.get(fld, "")).strip():
                issues.append(f"{fld} 空")
        if e.get("update_time") != "2026-07-17":
            issues.append(f"update_time={e.get('update_time')}")
        # 必须有 tag_review 记录
        if not any(t.get("serial") == ser for t in out.get("tag_review", [])):
            issues.append("缺少 tag_review 记录")
        checks.append({"serial": ser, "pass": len(issues) == 0, "issues": issues})
    # nonsilver verdict 合法性
    for n in out.get("nonsilver", []):
        if n.get("verdict") not in ("非银发", "泛医疗擦边"):
            # 找对应企业 check 追加
            for c in checks:
                if c["serial"] == n.get("serial"):
                    c["issues"].append(f"nonsilver verdict 非法:{n.get('verdict')}")
                    c["pass"] = False
    overall = all(c["pass"] for c in checks)
    res = {"batch": b, "checks": checks, "overall_pass": overall}
    with open(f"{BASE}/val/batch_{b:03d}_val.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    fails = [c["serial"] for c in checks if not c["pass"]]
    print(f"batch_{b:03d}: overall_pass={overall}, fails={fails}")
    return res

if __name__ == "__main__":
    bs = [int(x) for x in sys.argv[1:]]
    all_fail = []
    for b in bs:
        r = validate_batch(b)
        if not r["overall_pass"]:
            all_fail.extend([(b, c["serial"], c["issues"]) for c in r["checks"] if not c["pass"]])
    print(f"\n总计失败 {len(all_fail)} 项")
    for b, s, iss in all_fail:
        print(f"  batch_{b:03d} {s}: {iss}")
