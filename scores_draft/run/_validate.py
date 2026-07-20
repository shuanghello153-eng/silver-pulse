import json

BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run"

def recompute(sig, info, diff, copy):
    return round((sig*0.3+info*0.3+diff*0.2+copy*0.2)*10, 1)

for b in [0, 2, 3]:
    out = json.load(open(f"{BASE}/out/batch_{b:03d}_out.json", encoding="utf-8"))
    inbox = json.load(open(f"{BASE}/inbox/batch_{b:03d}.json", encoding="utf-8"))
    inbox_map = {e["serial"]: e for e in inbox["enterprises"]}
    print(f"\n========== BATCH {b} ==========")
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
            issues.append("三版重复")
        for fld in ["payor_model","business_tags_role","silver_verdict","update_time"]:
            if not str(e.get(fld,"")).strip():
                issues.append(f"{fld} 空")
        if e.get("update_time") != "2026-07-17":
            issues.append(f"update_time={e.get('update_time')}")
        print(f"  {ser}: {'OK' if not issues else issues}")
    # tag_review old_tags vs inbox
    print("  -- tag_review old_tags 核对 --")
    for t in out.get("tag_review", []):
        ser = t["serial"]
        ib = inbox_map.get(ser, {})
        old = t.get("old_tags", {})
        for key in ["tag_l1","tag_l2"]:
            if old.get(key) != ib.get(key):
                print(f"    {ser}: old_tags.{key} 不符 out={old.get(key)} inbox={ib.get(key)}")
        ob = old.get("business_tags", {})
        ibb = ib.get("business_tags", {})
        for bk in ["customer","role","channel"]:
            if ob.get(bk) != ibb.get(bk):
                print(f"    {ser}: old_tags.bt.{bk} 不符 out={ob.get(bk)} inbox={ibb.get(bk)}")
    # nonsilver
    print("  -- nonsilver 核对 --")
    for n in out.get("nonsilver", []):
        if n.get("verdict") not in ("非银发","泛医疗擦边"):
            print(f"    {n['serial']}: verdict非法={n.get('verdict')}")
        else:
            print(f"    {n['serial']}: {n.get('verdict')} OK")
    # also flag 核心银发 appearing in nonsilver
    for n in out.get("nonsilver", []):
        if n.get("verdict") == "核心银发":
            print(f"    {n['serial']}: 核心银发不得出现在nonsilver!")
