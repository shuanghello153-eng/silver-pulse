import json, os
BASE = r"g:\workbuddy\2026-06-28-23-34-20\silver-pulse\data\enterprise"
ent = json.load(open(os.path.join(BASE, "all_enterprises.json"), encoding="utf-8"))
byname = { (e.get("name") or ""): e for e in ent }
bycn = { (e.get("name_cn") or ""): e for e in ent }

suspects = ["Meela","Mend","RapidClaims","SiftWell Analytics","Thoughtful AI","SeniorSafetyAdvice",
            "美呀植牙","通策医疗","鼎植口腔","谊安医疗","鱼跃",
            "上品折扣","家有购物","享佳健康"]

for s in suspects:
    e = byname.get(s) or bycn.get(s)
    if not e:
        print(f"### {s}: 未找到\n"); continue
    print(f"### {s} (cn={e.get('name_cn')})")
    for k in ["name","name_cn","tag_l1","tag_l2","description","desc_cn","business_model_cn","country","category_l1","category_l2"]:
        v = e.get(k)
        if v is not None:
            sv = str(v)
            if len(sv)>160: sv=sv[:160]+"…"
            print(f"   {k}: {sv}")
    print()
