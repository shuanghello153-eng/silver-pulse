# -*- coding: utf-8 -*-
"""分层统计：把'推荐理由本身'的问题 vs '连带其他字段'的问题分开。"""
import json, sys, collections
sys.path.insert(0, '.')
from check_single import validate

d = json.load(open('../../data/enterprise/all_enterprises.json', encoding='utf-8'))
others = [e.get('recommend', '') for e in d if isinstance(e.get('recommend'), str)]

# 分两类规则
REC_RULES = {"R1","R2","R3","R4","R5","R-name","R-field-dedup","R-integrity","R-novelty","R-jargon","R-filler","R-noabs","R10"}
CTX_RULES = {"R6","R7","R8"}

n=len(d)
rec_only_ok=0        # 推荐理由本身没问题(不含R10)
full_ok=0
dict_cnt=0
fail_rec=0           # 推荐理由本身有问题
fail_ctx_only=0      # 仅其他字段问题(推荐理由本身OK)
rec_issue_counter=collections.Counter()
ctx_issue_counter=collections.Counter()

for e in d:
    r=e.get('recommend')
    if isinstance(r,dict): dict_cnt+=1
    iss=validate(e, None, skip={"R10"})  # 跳过慢的跨企业
    rec_iss=[i for i in iss if i.split(':')[0] in REC_RULES]
    ctx_iss=[i for i in iss if i.split(':')[0] in CTX_RULES]
    if not iss:
        full_ok+=1
    if not rec_iss:
        rec_only_ok+=1
    else:
        fail_rec+=1
        for i in rec_iss: rec_issue_counter[i.split(':')[0]]+=1
    if rec_iss==[] and ctx_iss:
        fail_ctx_only+=1
    for i in ctx_iss: ctx_issue_counter[i.split(':')[0]]+=1

print(f"总数 {n} | dict型 {dict_cnt}")
print(f"[推荐理由本身] 合格 {rec_only_ok} / 不合格 {fail_rec}")
print(f"[完全合格(含其他字段)] {full_ok}")
print(f"[推荐理由OK但其他字段拖累] {fail_ctx_only}")
print("--- 推荐理由本身问题分布 ---")
for k,v in rec_issue_counter.most_common():
    print(f"  {k}: {v}")
print("--- 其他字段(R6/R7/R8)问题分布 ---")
for k,v in ctx_issue_counter.most_common():
    print(f"  {k}: {v}")
