# -*- coding: utf-8 -*-
import json, re, os
from collections import Counter

BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
d = json.load(open(DB, encoding='utf-8'))
n = len(d)

def has(e, k):
    v = e.get(k)
    if isinstance(v, str):
        return v.strip() not in ('', '待补充', 'N/A', 'nan', 'None', '无')
    return v not in (None, [], {})

fields = ['research_value','desc_cn','payor_model','founded','stage',
          'events','highlights','update_time','silver_verdict','silver_reason',
          'business_tags','tag_l1','tag_l2']
print("=" * 60)
print("DB 总企业数:", n)
print("=" * 60)
print("【字段覆盖率】")
for f in fields:
    c = sum(1 for e in d if has(e, f))
    print(f"  {f:16s} {c:5d}  {100*c/n:5.1f}%")

print("\n【recommend 三版本完整度】")
def rec_full(e):
    r = e.get('recommend')
    if not isinstance(r, dict): return False
    return all(r.get(f) for f in ('rec_v1','rec_v2','rec_v3'))
rf = sum(1 for e in d if rec_full(e))
print("  三版齐全:", rf, f"{100*rf/n:.1f}%")

print("\n【payor_model 分布】")
print(" ", Counter(e.get('payor_model','<空>') for e in d))

print("\n【silver_verdict 分布】")
print(" ", Counter(e.get('silver_verdict','<空>') for e in d))

print("\n【research_value 区间分布】")
rvs = [e['research_value'] for e in d if isinstance(e.get('research_value'),(int,float))]
import statistics
if rvs:
    print(f"  已评分 {len(rvs)} 家; min={min(rvs)} max={max(rvs)} mean={statistics.mean(rvs):.1f}")
    buckets = Counter()
    for v in rvs:
        b = int(v//10)*10
        buckets[b]+=1
    for b in sorted(buckets):
        print(f"  [{b:3d}-{b+9:3d}] {buckets[b]}")

# 公式复核
def recompute(sig,info,diff,copy):
    return round((sig*0.3+info*0.3+diff*0.2+copy*0.2)*10,1)
print("\n【research_value 公式复核（抽查不匹配）】")
bad=0
for e in d:
    r=e.get('research_value')
    if not isinstance(r,(int,float)): continue
    rec=e.get('recommend') or {}
    sig=rec.get('signal_strength'); info=rec.get('info_score'); diff=rec.get('diff_score'); cp=rec.get('copy_score')
    if None in (sig,info,diff,cp):
        # 兼容平铺
        sig=e.get('signal_strength'); info=e.get('info_score'); diff=e.get('diff_score'); cp=e.get('copy_score')
    if None in (sig,info,diff,cp): continue
    exp=recompute(sig,info,diff,cp)
    if abs(exp-r)>0.15:
        bad+=1
        if bad<=10:
            print(f"  serial={e.get('serial')} 记录={r} 期望={exp} (sig={sig},info={info},diff={diff},cp={cp})")
print("  公式不匹配条数:", bad)

# 模板/雷同检测
print("\n【描述/理由质量扫描】")
GEN_DESC = ['是一家','致力于','专注于','成立于','提供','打造','旨在','专注于为']
templated_desc=0
short_desc=0
for e in d:
    desc=e.get('desc_cn') or ''
    if len(desc)<40: short_desc+=1
    if any(desc.startswith(g) for g in GEN_DESC): templated_desc+=1
print(f"  desc_cn<40字（偏短）: {short_desc}")
print(f"  desc_cn 以通用套话开头（一家/致力于/专注于…）: {templated_desc}")

# 三版理由雷同检测：字符重合率
def overlap(a,b):
    if not a or not b: return 0
    sa,sb=set(a),set(b)
    return len(sa&sb)/len(sa|sb)
dup_rec=0
for e in d:
    r=e.get('recommend')
    if not isinstance(r,dict): continue
    v1,v2,v3=r.get('rec_v1'),r.get('rec_v2'),r.get('rec_v3')
    if not(v1 and v2 and v3): continue
    ov=max(overlap(v1,v2),overlap(v2,v3),overlap(v1,v3))
    if ov>0.55:
        dup_rec+=1
        if dup_rec<=15:
            print(f"  serial={e.get('serial')} 三版字符重合率={ov:.2f}")
            print(f"    v1={v1}")
            print(f"    v2={v2}")
            print(f"    v3={v3}")
print("  三版理由高重合(>0.55)条数:", dup_rec)

# 抽样 tier-C 描述质量（research_value<40）
print("\n【低分企业抽样（research_value<40）描述质量】")
low=[e for e in d if isinstance(e.get('research_value'),(int,float)) and e['research_value']<40]
print("  低分企业数:", len(low))
for e in low[:6]:
    print(f"  --- serial={e.get('serial')} name={e.get('name')} rv={e.get('research_value')}")
    print(f"      desc_cn={ (e.get('desc_cn') or '')[:120]}")
    r=e.get('recommend') or {}
    print(f"      rec_v1={ (r.get('rec_v1') or '')[:120]}")
