# -*- coding: utf-8 -*-
"""检查 drafts_v4/ 草稿：用主库上下文跑门禁，看有多少能过、合并后主库能救到多少。"""
import json, os, sys, glob, collections
sys.path.insert(0, '.')
from check_single import validate

DB='../../data/enterprise/all_enterprises.json'
d=json.load(open(DB,encoding='utf-8'))
by_serial={str(e.get('serial')):e for e in d}

drafts=glob.glob('drafts_v4/*.json')
print(f"drafts_v4 文件数: {len(drafts)}")

draft_serials=set()
draft_pass=0
draft_fail=0
fail_rules=collections.Counter()
no_ctx=0
merged_recs={}

for fp in drafts:
    try:
        dr=json.load(open(fp,encoding='utf-8'))
    except: continue
    s=str(dr.get('serial'))
    rec=dr.get('recommend')
    if not s or not isinstance(rec,str): continue
    draft_serials.add(s)
    ctx=by_serial.get(s)
    if not ctx:
        no_ctx+=1; continue
    # 用草稿的 recommend 覆盖主库上下文
    tmp=dict(ctx); tmp['recommend']=rec
    merged_recs[s]=rec
    iss=validate(tmp,None,skip={"R10"})
    if iss:
        draft_fail+=1
        for i in iss: fail_rules[i.split(':')[0]]+=1
    else:
        draft_pass+=1

print(f"草稿覆盖 serial 数: {len(draft_serials)}")
print(f"草稿无主库上下文: {no_ctx}")
print(f"[草稿单跑门禁] 过 {draft_pass} / 不过 {draft_fail}")
print("--- 草稿失败规则分布 ---")
for k,v in fail_rules.most_common(): print(f"   {k}:{v}")

# 模拟合并：主库现状 + 草稿覆盖后,整库通过数
sim_pass=0
for e in d:
    s=str(e.get('serial'))
    tmp=dict(e)
    if s in merged_recs: tmp['recommend']=merged_recs[s]
    iss=validate(tmp,None,skip={"R10"})
    if not iss: sim_pass+=1
print(f"\n[模拟合并后] 整库1502家通过(不含R10): {sim_pass}  (当前是25)")

# 主库中哪些serial 还没有草稿覆盖
db_serials={str(e.get('serial')) for e in d}
uncovered=db_serials - draft_serials
print(f"主库有但草稿未覆盖的 serial 数: {len(uncovered)}")
