import json, collections, random

ROOT = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
data = json.load(open(f"{ROOT}/data/enterprise/all_enterprises.json", encoding="utf-8"))

def is_done(e):
    rv = e.get("research_value") is not None
    rec = e.get("recommend")
    rec_ok = isinstance(rec, dict) and any(k in rec for k in ("rec_v1","v1","rec1"))
    return rv or rec_ok

done = [e for e in data if is_done(e)]
print("总企业:", len(data), " 已完成(541判定):", len(done))

PLACE = {"","未披露","未知","暂无","n/a","na","none","null","待补充","无","—","-","未找到","未搜到","未明确","tbd","N/A","undefined","没有查到"}

info_fields = ["name_cn","region","founded","stage","website_url","crunchbase_url",
               "description","desc_cn","business_model","business_model_cn","business_tags",
               "payor_model","funding_latest","funding_total","investors","highlights",
               "tags","tag_l1","tag_l2","category_l1","category_l2"]

def fill_stats(subset):
    out={}
    for f in info_fields:
        empty=place=real=0
        for e in subset:
            v=e.get(f)
            if v is None or (isinstance(v,str) and v.strip()=="") or (isinstance(v,(list,dict)) and len(v)==0):
                empty+=1
            elif isinstance(v,str) and v.strip().lower() in PLACE:
                place+=1
            else:
                real+=1
        out[f]=(real,place,empty)
    return out

print("\n=== 信息补全字段填充率 (已完成541内) ===")
for f,(real,place,empty) in fill_stats(done).items():
    print(f"  {f:18s} 实填={real:3d}  占位={place:3d}  空={empty:3d}  (实填率 {real/len(done)*100:.0f}%)")

print("\n=== 信息补全字段填充率 (全库1502) ===")
for f,(real,place,empty) in fill_stats(data).items():
    print(f"  {f:18s} 实填={real:4d}  占位={place:3d}  空={empty:4d}  (实填率 {real/len(data)*100:.0f}%)")

print("\n=== stage 值分布 (已完成内, 非空) ===")
sc=collections.Counter(str(e.get("stage")) for e in done if e.get("stage") not in (None,""))
for k,v in sc.most_common(25): print(f"  {k}: {v}")

print("\n=== recommend 结构分布 (已完成内) ===")
rc=collections.Counter()
for e in done:
    r=e.get("recommend")
    if isinstance(r,dict):
        k=set(r.keys())
        if {"rec_v1","rec_v2","rec_v3"}<=k: rc["dict三版"]+=1
        elif "rec_v1" in k: rc["dict单版"]+=1
        else: rc["dict其他"]+=1
    elif isinstance(r,str): rc["字符串"]+=1
    elif r is None: rc["None"]+=1
    else: rc[type(r).__name__]+=1
for k,v in rc.most_common(): print(f"  {k}: {v}")

print("\n=== payor_model / role 现状 ===")
for f in ["payor_model","role"]:
    c_all=sum(1 for e in data if e.get(f) not in (None,"",[]))
    c_done=sum(1 for e in done if e.get(f) not in (None,"",[]))
    print(f"  {f}: 全库有值 {c_all}/{len(data)}; 已完成内 {c_done}/{len(done)}")

# 重复/啰嗦 量化
name_in_desc=sum(1 for e in done if e.get("name") and e.get("desc_cn") and str(e.get("name")) in str(e.get("desc_cn")))
name_in_desce=sum(1 for e in done if e.get("name") and e.get("description") and str(e.get("name")) in str(e.get("description")))
rec_fund=sum(1 for e in done if isinstance(e.get("recommend"),dict) and any(("融资" in str(e["recommend"].get(k,"")) or "万美元" in str(e["recommend"].get(k,"")) or "轮" in str(e["recommend"].get(k,""))) for k in ("rec_v1","rec_v2","rec_v3")))
print(f"\n=== 重复指标 ===")
print(f"  desc_cn 含企业名: {name_in_desc}/{len(done)}")
print(f"  description 含企业名: {name_in_desce}/{len(done)}")
print(f"  推荐理由含融资/万美元/轮(与funding字段重复): {rec_fund}/{len(done)}")

print("\n=== 抽样内容 (8家) ===")
random.seed(7)
for e in random.sample(done,8):
    print("="*70)
    print(f"[{e.get('serial')}] {e.get('name')} / {e.get('name_cn')}")
    print(f"  stage={e.get('stage')} | founded={e.get('founded')} | region={e.get('region')}")
    print(f"  funding_latest={e.get('funding_latest')} | funding_total={e.get('funding_total')} | investors={str(e.get('investors'))[:70]}")
    print(f"  description[:240]={str(e.get('description'))[:240]}")
    print(f"  desc_cn[:240]={str(e.get('desc_cn'))[:240]}")
    r=e.get('recommend')
    if isinstance(r,dict):
        print(f"  rec_v1[:180]={str(r.get('rec_v1'))[:180]}")
        print(f"  rec_v2[:180]={str(r.get('rec_v2'))[:180]}")
    else:
        print(f"  recommend={str(r)[:180]}")
    print(f"  tags={e.get('tags')} | tag_l1={e.get('tag_l1')} tag_l2={e.get('tag_l2')}")
    print(f"  payor_model={e.get('payor_model')} | business_model={str(e.get('business_model'))[:60]}")
