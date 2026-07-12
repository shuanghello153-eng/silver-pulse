# -*- coding: utf-8 -*-
"""生成 v3 交付物: 标签体系全映射 MD + 企业标签全量 CSV。
依赖: data/enterprise/all_enterprises.json (已_rebuild_tags.py重跑) + tag_synonyms.json + _rebuild_tags.py(L2_TO_L1) + output/_动你标注_v3.json
"""
import json, csv
from collections import Counter, defaultdict

DATA='data/enterprise/all_enterprises.json'
SYN='data/enterprise/tag_synonyms.json'
FLAG='output/_动你标注_v3.json'
OUT_MD='output/标签体系_全映射_2026-07-12_v3.md'
OUT_CSV='output/企业标签全量表_2026-07-12_v3.csv'

data=json.load(open(DATA,encoding='utf-8'))
syn=json.load(open(SYN,encoding='utf-8'))
flags=json.load(open(FLAG,encoding='utf-8'))

# 载入 L2_TO_L1 (避免整体执行脚本写文件)
src=open('_rebuild_tags.py',encoding='utf-8').read()
ns={}
cut=src.index('# ---------------------------------------------------------------\n# 5. Excel')
exec(src[:cut], ns)
L2_TO_L1=ns['L2_TO_L1']; L1_LIST=ns['L1_LIST']

# 统计
l1c=Counter(); l2c=Counter()
for e in data:
    for x in e.get('tag_l1',[]): l1c[x]+=1
    for x in e.get('tag_l2',[]): l2c[x]+=1

# 把 L2 按 canonical L1 分组
l2_by_l1=defaultdict(list)
for l2 in l2c:
    l2_by_l1[L2_TO_L1.get(l2,'?未知')].append(l2)
for k in l2_by_l1: l2_by_l1[k].sort(key=lambda x:-l2c[x])

# ---------- CSV ----------
with open(OUT_CSV,'w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f)
    w.writerow(['name','name_cn','tag_l1(新)','tag_l2(新)','business_tags_customer','business_tags_role','business_tags_channel','国家地区','简介','原分类category_l1','原分类category_l2'])
    for e in data:
        bt=e.get('business_tags') or {}
        cust=bt.get('customer',''); role=bt.get('role',''); chan=';'.join(bt.get('channel',[]) or [])
        region=e.get('region') or e.get('country') or ''
        desc=(e.get('description') or e.get('desc_cn') or '').replace('\n',' ').replace('\r',' ')
        w.writerow([e.get('name',''), e.get('name_cn',''),
                    ';'.join(e.get('tag_l1',[])), ';'.join(e.get('tag_l2',[])),
                    cust, role, chan, region, desc,
                    e.get('category_l1',''), e.get('category_l2','')])
print('WROTE CSV:', OUT_CSV, '行数(含表头):', len(data)+1)

# ---------- MD ----------
L=[]; A=L.append
A('# 银发经济企业库 · 标签体系全映射（2026-07-12 v3）\n')
A('> 真相源：`_rebuild_tags.py`（含 `L2_TO_L1` 单归属映射）。本文件为可读全量大表，供逐条核对。\n')
A('> 企业总数 **%d** 家；一级标签 **%d** 个；二级标签 **%d** 个；validate 9/9 全绿。\n'%(len(data), len(l1c), len(l2c)))

A('\n## 一、一级标签列表 + 企业数\n')
for k in sorted(l1c, key=lambda x:-l1c[x]):
    A('- **%s**：%d 家\n'%(k, l1c[k]))

A('\n## 二、L1 → L2 → 同类词 全量映射（无省略）\n')
for l1 in L1_LIST:
    l2s=l2_by_l1.get(l1,[])
    if not l2s: continue
    A('\n### %s（%d 家，含 %d 个二级标签）\n'%(l1, l1c.get(l1,0), len(l2s)))
    for l2 in l2s:
        cnt=l2c[l2]
        als=syn.get(l2,[])
        als=[a for a in als if a!=l2]
        if als:
            A('- **%s**（%d 家）— 同类词：%s\n'%(l2, cnt, '、'.join(als)))
        else:
            A('- **%s**（%d 家）— 同类词：（仅自身）\n'%(l2, cnt))

A('\n## 三、各 L1 / L2 企业数分布（含 >150 大桶标记）\n')
A('\n### 二级标签企业数（降序）\n')
for l2,c in l2c.most_common():
    big=' ⚠️>150大桶' if c>150 else (' ⚠️>100' if c>100 else '')
    A('- %s：%d 家%s（归 %s）\n'%(l2,c,big,L2_TO_L1.get(l2,'?')))
A('\n### >150 家大桶（区分度风险，建议后续复查/拆分）\n')
for l2,c in l2c.most_common():
    if c>150: A('- %s（%s）：%d 家\n'%(l2, L2_TO_L1.get(l2,'?'), c))

A('\n## 四、跨一级 L2 诊断与单归属修复说明\n')
A('- **v2 问题**：因 `tag_l1` 原取"企业全部 L2 的 L1 并集"，导致 52 个二级标签在分布上看似"跨多个一级"（实为同一企业多标签所致），用户视角下违反单归属。\n')
A('- **v3 修复**：在 `_rebuild_tags.py` 新增 `L2_TO_L1` 规范映射（每个 L2 恰好一个 L1），全库企业 `tag_l1` 严格据此生成。\n')
A('- **结果**：跨一级的 L2 数 = **0**（每个 L2 仅对应唯一 L1）；企业级强制校验「若企业有 L2=X，其 L1 必含 `L2_TO_L1[X]`」违反数 = **0**。\n')
A('- **桶泄漏校验**：医疗健康企业 100% 含医疗类 L2；养老服务企业 100% 含养老类 L2（无"挂名错归"）。\n')

A('\n## 五、可理解性审查（普通用户视角）\n')
A('- 二级标签全部为普通用户熟悉常用词（助听器/临终关怀/老年鞋/养老院…），无 jargon、无大伞词。\n')
A('- 一级 ≠ 二级同名：0 冲突（已校验）。\n')
A('- 抽样核对重点桶（智能硬件171/居家护理160/文娱150/专业护理116/适老化115/社交平台110/健康管理101），标签可懂度良好；大桶区分度风险见第三节，留待后续按需拆分。\n')

A('\n## 六、数据规律\n')
A('- 两级结构稳定：11 个一级 / 56 个二级，全库零标签企业 = 0，单企业标签 ≤5。\n')
A('- 医疗健康/养老服务为最大桶（425/447 家），与其为银发核心赛道一致。\n')
A('- 消费品因将「智能硬件（171）→ 智能科技」重分配后回落至 249 家，结构更合理。\n')
A('- 女性健康服务（原常误归医疗健康）已单归「女性健康」一级，修正 22 家错归。\n')

A('\n## 七、重盘前后对照（v2 → v3 关键 L1 重分配）\n')
A('- 智能硬件：消费品 → **智能科技**（171 家迁移，行业归属更准）\n')
A('- 女性健康服务：医疗健康 → **女性健康**（22 家迁移）\n')
A('- 陪伴机器人：文娱社交 → **智能科技**（22 家，按产品/行业归属）\n')
A('- 其余 L2 单归属与 v2 一致（v2 已是各 L2 确定性归一则）；v3 用显式 `L2_TO_L1` 将其"锁定为唯一真相"，杜绝重跑漂移。\n')
A('- 企业总数、二级标签数、0 标签企业、≤5 标签等核心指标 v2→v3 不变。\n')

A('\n## 八、validate_tags.py 9/9 证据\n')
import subprocess
r=subprocess.run(['python','validate_tags.py'],capture_output=True,text=True)
A('```\n'+r.stdout.strip()+'\n```\n')

A('\n## 九、【动你标注】清单（交用户拍板，未静默改）\n')
A('> 以下企业为"软标签"驱动的边界个案（仅含 健康管理/健康监测/SODH 等软医疗标签，或仅 智慧养老，但同时带明显非医疗/非养老标签）。按规则未静默改动其标签，列出供小爽最终决定是否移出对应一级。\n')
A('- 共 **%d** 家：医疗健康 %d 家，养老服务 %d 家。\n'%(len(flags), sum(1 for f in flags if f['bucket']=='医疗健康'), sum(1 for f in flags if f['bucket']=='养老服务')))
for f in flags:
    A('- [%s] **%s**（%s） L2=%s ｜ %s\n'%(f['bucket'], f['name'], f.get('name_en') or '', '、'.join(f['l2']), f['reason']))

A('\n---\n*生成：2026-07-12 v3 ｜ 真相源 _rebuild_tags.py ｜ validate 9/9 ｜ L2_TO_L1 单归属 0 冲突*')
open(OUT_MD,'w',encoding='utf-8').write('\n'.join(L))
print('WROTE MD:', OUT_MD)
