# -*- coding: utf-8 -*-
import json, re, os
from collections import Counter

BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
d = json.load(open(DB, encoding='utf-8'))
n = len(d)

print("===== 原始记录结构抽样（前3家 + 1家低分）=====")
for idx in [0, 1, 2]:
    e = d[idx]
    print(f"\n----- d[{idx}] serial={e.get('serial')} name={e.get('name')} -----")
    print("  顶层键:", sorted(e.keys()))
    rec = e.get('recommend')
    print("  recommend 类型:", type(rec).__name__)
    if isinstance(rec, dict):
        print("  recommend 子键:", sorted(rec.keys()))
        for k in ('rec_v1','rec_v2','rec_v3'):
            print(f"    {k} = {(rec.get(k) or '')[:80]}")
    else:
        print("  recommend 值 =", repr(rec)[:200])
    # 四维分位置探查
    for k in ('signal_strength','info_score','diff_score','copy_score','research_value'):
        print(f"  顶层 {k} = {e.get(k)}")
    print("  desc_cn =", (e.get('desc_cn') or '')[:200])
    print("  silver_reason =", (e.get('silver_reason') or '')[:150])
    print("  highlights =", (e.get('highlights') or '')[:200])
    print("  payor_model =", (e.get('payor_model') or '')[:120])

print("\n===== recommend 字段类型统计 =====")
types = Counter(type(e.get('recommend')).__name__ for e in d)
print("  recommend 类型分布:", types)
# 是否有顶层 rec_v1/v2/v3
toprec = sum(1 for e in d if e.get('rec_v1') or e.get('rec_v2') or e.get('rec_v3'))
print("  顶层有 rec_v1/v2/v3 的企业数:", toprec)
# dict 里有几版
dict_ok = 0
for e in d:
    r=e.get('recommend')
    if isinstance(r,dict) and r.get('rec_v1') and r.get('rec_v2') and r.get('rec_v3'):
        dict_ok+=1
print("  recommend 为 dict 且三版齐全:", dict_ok)

print("\n===== 四维分存储位置与范围 =====")
def locate(k):
    top = sum(1 for e in d if isinstance(e.get(k),(int,float)))
    inrec = sum(1 for e in d if isinstance(e.get('recommend'),dict) and isinstance(e['recommend'].get(k),(int,float)))
    print(f"  {k}: 顶层{top} / recommend内{inrec}")
for k in ('signal_strength','info_score','diff_score','copy_score'):
    locate(k)

print("\n===== research_value 公式复核（四维分取顶层或recommend内）=====")
def getscore(e,k):
    v=e.get(k)
    if isinstance(v,(int,float)): return v
    r=e.get('recommend')
    if isinstance(r,dict):
        v=r.get(k)
        if isinstance(v,(int,float)): return v
    return None
def recompute(sig,info,diff,cp):
    return round((sig*0.3+info*0.3+diff*0.2+cp*0.2)*10,1)
mismatch=0; checked=0
for e in d:
    rv=e.get('research_value')
    if not isinstance(rv,(int,float)): continue
    s=getscore(e,'signal_strength'); i=getscore(e,'info_score'); df=getscore(e,'diff_score'); c=getscore(e,'copy_score')
    if None in (s,i,df,c): continue
    checked+=1
    exp=recompute(s,i,df,c)
    if abs(exp-rv)>0.15:
        mismatch+=1
        if mismatch<=8:
            print(f"  serial={e.get('serial')} 记录rv={rv} 期望={exp} (s={s},i={i},df={df},c={c})")
print(f"  可校验条数={checked}, 公式不匹配={mismatch}")

print("\n===== 内容质量扫描 =====")
GEN=['是一家','致力于','专注于','成立于','提供','打造','旨在','专注于为','总部位于']
templ=0; short=0
for e in d:
    desc=e.get('desc_cn') or ''
    if len(desc)<60: short+=1
    if any(desc.startswith(g) for g in GEN): templ+=1
print(f"  desc_cn<60字(偏短): {short} ({100*short/n:.1f}%)")
print(f"  desc_cn 通用套话开头: {templ} ({100*templ/n:.1f}%)")

# silver_reason 模板检测
sr_templ=0
for e in d:
    sr=e.get('silver_reason') or ''
    if len(sr)<30: sr_templ+=1
print(f"  silver_reason<30字(偏短): {sr_templ}")

# highlights 废话检测
hl_filler=0
for e in d:
    hls=e.get('highlights')
    if isinstance(hls,list):
        for h in hls:
            if re.search(r'成立于\d{4}年', str(h)): hl_filler+=1; break
    elif isinstance(hls,str) and re.search(r'成立于\d{4}年', hls):
        hl_filler+=1
print(f"  highlights 含'成立于YYYY年'废话的企业数: {hl_filler}")

# recommend 字符串重复度（跨企业相似）
print("\n===== recommend(字符串) 跨企业重复/雷同 =====")
str_recs=[e.get('recommend') for e in d if isinstance(e.get('recommend'),str) and e.get('recommend')]
print(f"  字符串型 recommend 总数: {len(str_recs)}")
uniq=set(str_recs)
print(f"  去重后唯一值: {len(uniq)}")
from collections import Counter as C
c=C(str_recs)
print("  出现≥5次的最常见 recommend(前10):")
for txt,cnt in c.most_common(10):
    print(f"    [{cnt}次] {txt[:90]}")
