# -*- coding: utf-8 -*-
"""诊断当前 all_enterprises.json 的 tag_l1/tag_l2 真实分布"""
import json
from collections import Counter
DATA='data/enterprise/all_enterprises.json'
data=json.load(open(DATA,encoding='utf-8'))

L1_LIST=sorted({l1 for e in data for l1 in e.get('tag_l1',[])})
l1c=Counter(); l2c=Counter()
for e in data:
    for x in e.get('tag_l1',[]): l1c[x]+=1
    for x in e.get('tag_l2',[]): l2c[x]+=1

print('=== 企业总数:',len(data))
print('=== 一级标签(去重):',len(L1_LIST),L1_LIST)
print('=== 二级标签(去重)数:',len(l2c))
print()
print('=== 一级分布 ===')
for k,v in l1c.most_common(): print(f'  {k}: {v}')
print()
print('=== 一级=二级同名 (违反规则) ===')
same=0
for k,v in l2c.most_common():
    if k in L1_LIST:
        print(f'  [同名] {k}: {v} 家')
        same+=1
print('  同名数:',same)
print()
print('=== 幽灵标签(<=2家) ===')
gh=0
for k,v in sorted(l2c.items(),key=lambda x:x[1]):
    if v<=2:
        print(f'  {k}: {v}')
        gh+=1
print('  幽灵数:',gh)
print()
print('=== 超大伞词(>100家) ===')
for k,v in l2c.most_common():
    if v>100: print(f'  {k}: {v}')
print()
print('=== 二级标签完整计数(降序) ===')
for k,v in l2c.most_common(): print(f'  {k}: {v}')
print()
print('=== 0标签企业:',sum(1 for e in data if not e.get('tag_l2')))
print('=== 单企业标签>5:',sum(1 for e in data if len(e.get('tag_l2',[]))>5))
