import json

BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run"

def recompute(sig, info, diff, copy):
    return round((sig*0.3+info*0.3+diff*0.2+copy*0.2)*10, 1)

for b in [0, 2, 3]:
    out = json.load(open(f"{BASE}/out/batch_{b:03d}_out.json", encoding="utf-8"))
    inbox = json.load(open(f"{BASE}/inbox/batch_{b:03d}.json", encoding="utf-8"))
    inbox_map = {e["serial"]: e for e in inbox["enterprises"]}
    checks = []
    for e in out["enterprises"]:
        ser = e["serial"]
        issues = []
        sig, info, diff, copy = e["signal_strength"], e["info_score"], e["diff_score"], e["copy_score"]
        rv = e["research_value"]
        for nm, v in [("signal",sig),("info",info),("diff",diff),("copy",copy)]:
            if not (0 <= v <= 10):
                issues.append(f"{nm}_score 越界:{v}")
        calc = recompute(sig, info, diff, copy)
        if abs(calc - rv) > 0.06:
            issues.append(f"research_value 不符 out={rv} calc={calc}")
        rec = e.get("recommend", {})
        vs = []
        for k in ["rec_v1","rec_v2","rec_v3"]:
            t = rec.get(k,"")
            vs.append(t)
            if not t or not t.strip():
                issues.append(f"{k} 空")
            elif len(t) > 90:
                issues.append(f"{k} 超90字({len(t)})")
        if len(set(vs)) < 3:
            issues.append("三版推荐理由重复")
        for fld in ["payor_model","business_tags_role","silver_verdict","update_time"]:
            if not str(e.get(fld,"")).strip():
                issues.append(f"{fld} 空")
        if e.get("update_time") != "2026-07-17":
            issues.append(f"update_time={e.get('update_time')}")
        # tag_review old_tags vs inbox
        tr = next((t for t in out.get("tag_review",[]) if t["serial"]==ser), None)
        if tr:
            old = tr.get("old_tags", {})
            ib = inbox_map.get(ser, {})
            if old.get("tag_l1") != ib.get("tag_l1"):
                issues.append(f"tag_review.old_tags.tag_l1 与 inbox 不符: out={old.get('tag_l1')} inbox={ib.get('tag_l1')}")
            if old.get("tag_l2") != ib.get("tag_l2"):
                issues.append(f"tag_review.old_tags.tag_l2 与 inbox 不符: out={old.get('tag_l2')} inbox={ib.get('tag_l2')}")
            ob = old.get("business_tags", {})
            ibb = ib.get("business_tags", {})
            for bk in ["customer","role","channel"]:
                if ob.get(bk) != ibb.get(bk):
                    issues.append(f"tag_review.old_tags.business_tags.{bk} 与 inbox 不符: out={ob.get(bk)} inbox={ibb.get(bk)}")
        else:
            issues.append("缺少 tag_review 记录")
        checks.append({"serial": ser, "pass": len(issues)==0, "issues": issues})
    overall = all(c["pass"] for c in checks)
    result = {"batch": b, "checks": checks, "overall_pass": overall}
    with open(f"{BASE}/val/batch_{b:03d}_val.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    fails = [c["serial"] for c in checks if not c["pass"]]
    print(f"batch_{b:03d}: overall_pass={overall}, fails={fails}")
