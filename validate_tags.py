# -*- coding: utf-8 -*-
"""双重校验: 标签维度 + 企业维度。全绿才算过关。"""
import json
from collections import Counter
DATA='data/enterprise/all_enterprises.json'
SYN='data/enterprise/tag_synonyms.json'
data=json.load(open(DATA,encoding='utf-8'))
syn=json.load(open(SYN,encoding='utf-8'))

L1=set(); L2=Counter()
for e in data:
    for x in e.get('tag_l1',[]): L1.add(x)
    for x in e.get('tag_l2',[]): L2[x]+=1

FIELD_DUP={'有融资','融资过亿','已被收购','国内','海外','未披露','IPO','上市','A轮','B轮','并购','并购退出'}

results=[]
def check(name, ok, detail=''):
    results.append((name, ok, detail))
    print(('[PASS] ' if ok else '[FAIL] ')+name+((' -> '+detail) if detail else ''))

# 1. 一级=二级同名
same=L1 & set(L2.keys())
check('一级=二级同名 = 0', len(same)==0, '冲突: '+', '.join(sorted(same)) if same else '无')

# 2. 幽灵(<3)
ghosts={k:v for k,v in L2.items() if v<3}
check('幽灵标签(<3家) = 0', len(ghosts)==0, '剩余: '+', '.join(f'{k}({v})' for k,v in sorted(ghosts.items(),key=lambda x:x[1])) if ghosts else '无')

# 3. 与字段重复
dup=[k for k in L2 if k in FIELD_DUP]
check('与列表字段重复 = 0', len(dup)==0, '冲突: '+', '.join(dup) if dup else '无')

# 4. 无同类词
no_syn=[k for k in L2 if k not in syn or len(syn.get(k,[]))==0]
check('无同类词的二级标签 = 0', len(no_syn)==0, '缺: '+', '.join(no_syn) if no_syn else '全部覆盖')

# 5. 0标签企业
zero=[e.get('name') or e.get('name_cn') for e in data if not e.get('tag_l2')]
check('0标签企业 = 0', len(zero)==0, f'{len(zero)}家: '+', '.join(zero[:5]) if zero else '无')

# 6. 单企业<=5
over5=[(e.get('name_cn') or e.get('name'), len(e.get('tag_l2',[]))) for e in data if len(e.get('tag_l2',[]))>5]
check('单企业标签 <= 5', len(over5)==0, f'{len(over5)}家超限: '+', '.join(f'{n}({c})' for n,c in over5[:8]) if over5 else '无')

# 7. >100 伞词 (报告, 不强制)
big={k:v for k,v in L2.items() if v>100}
print('  [报告] >100家伞词:', ', '.join(f'{k}({v})' for k,v in sorted(big.items(),key=lambda x:-x[1])))

# ---- 企业维度 ----
ent_ok=True; ent_detail=[]
dup_in_ent=0; empty_l1=0; unknown=set()
for e in data:
    t2=e.get('tag_l2',[])
    if len(t2)!=len(set(t2)): dup_in_ent+=1
    if t2 and not e.get('tag_l1'): empty_l1+=1
    for t in t2:
        if t not in L2: unknown.add(t)
check('企业内标签无重复', dup_in_ent==0, f'{dup_in_ent}家重复' if dup_in_ent else '无')
check('有标签企业必有L1', empty_l1==0, f'{empty_l1}家缺L1' if empty_l1 else '无')
check('全部标签在已知canon集合', len(unknown)==0, '异常: '+', '.join(unknown) if unknown else '无')

print('\n=== 汇总 ===')
np=sum(1 for _,ok,_ in results if ok); nf=sum(1 for _,ok,_ in results if not ok)
print(f'通过 {np} / 共 {len(results)} 项' + ('  ✓ 全部通过' if nf==0 else f'  ✗ 有 {nf} 项未通过'))
print('二级标签总数:', len(L2), ' | 一级标签数:', len(L1))
print('一级:', sorted(L1))
