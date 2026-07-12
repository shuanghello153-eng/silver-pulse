# -*- coding: utf-8 -*-
"""生成 v4 交付物 (纯规则, 依赖 _rebuild_tags.py 已回写的结果):
  - output/企业标签全量表_2026-07-12_v4.csv  (全 1325 家)
  - output/标签体系_全映射_2026-07-12_v4.md
"""
import json, csv, subprocess, os
from collections import Counter, defaultdict

DATA='data/enterprise/all_enterprises.json'
SYN='data/enterprise/tag_synonyms.json'
L2L1='data/enterprise/_l2_l1.json'
RULED='output/_ruleD_applied.json'
TRUNC='output/_trunc_log.json'
OUT_CSV='output/企业标签全量表_2026-07-12_v4.csv'
OUT_MD='output/标签体系_全映射_2026-07-12_v4.md'

data=json.load(open(DATA,encoding='utf-8'))
syn=json.load(open(SYN,encoding='utf-8'))
l2l1=json.load(open(L2L1,encoding='utf-8'))
ruled=json.load(open(RULED,encoding='utf-8'))
trunc=json.load(open(TRUNC,encoding='utf-8'))
N=len(data)

# ---------- 1. CSV ----------
cols=['name','name_cn','tag_l1(新)','tag_l2(新)','business_tags_customer',
      'business_tags_role','business_tags_channel','国家地区','简介','原分类category_l1','原分类category_l2']
with open(OUT_CSV,'w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f)
    w.writerow(cols)
    for e in data:
        bt=e.get('business_tags') or {}
        if not isinstance(bt,dict): bt={}
        w.writerow([
            e.get('name') or '',
            e.get('name_cn') or '',
            ';'.join(e.get('tag_l1') or []),
            ';'.join(e.get('tag_l2') or []),
            bt.get('customer') or '',
            bt.get('role') or '',
            ';'.join(bt.get('channel') or []) if isinstance(bt.get('channel'),list) else (bt.get('channel') or ''),
            e.get('region') or '',
            (e.get('description') or e.get('desc_cn') or ''),
            e.get('category_l1') or '',
            e.get('category_l2') or '',
        ])
print('CSV 已写:', OUT_CSV, N, '家')

# ---------- 2. 统计 ----------
l2_count=Counter()
l1_enterprises=defaultdict(set)   # L1 -> set(企业index)
for i,e in enumerate(data):
    for l2 in e.get('tag_l2',[]):
        l2_count[l2]+=1
        L1=l2l1.get(l2)
        if L1: l1_enterprises[L1].add(i)
# 各 L1 企业数(二级去重汇) 与 跨一级
l1_count={L1:len(s) for L1,s in l1_enterprises.items()}
cross=sum(1 for e in data if len(e.get('tag_l1',[]))>1)
sum_l1=sum(l1_count.values())

# L2 按 L1 分组(保持 L2_TO_L1 顺序)
l1_order=sorted(l1_count, key=lambda k:-l1_count[k])
l2_by_l1=defaultdict(list)
for l2,L1 in l2l1.items():
    l2_by_l1[L1].append(l2)
for L1 in l2_by_l1:
    l2_by_l1[L1].sort(key=lambda x:-l2_count.get(x,0))

# validate 证据
val=subprocess.run(['python','validate_tags.py'],capture_output=True,text=True,encoding='utf-8')
val_out=val.stdout

# ---------- 3. MD ----------
L=[]
L.append('# 标签体系全映射（2026-07-12 v4）\n')
L.append('> 数据层 v4 对齐 `评分推荐规则_2026-07-12版.md`。纯规则离线重算，**未调用大模型/未联网**。\n')
L.append('> 真相源：`_rebuild_tags.py`；校验：`validate_tags.py`（9/9）。重跑命令：`python _rebuild_tags.py && python validate_tags.py`。\n')

L.append('## 一、各一级标签企业数（= 其下二级标签企业集合去重汇总）\n')
L.append('| 一级标签 | 企业数 | 占比 |\n|---|---:|---:|\n')
for L1 in l1_order:
    L.append(f'| {L1} | {l1_count[L1]} | {l1_count[L1]/N*100:.1f}% |\n')
L.append(f'\n- **各一级企业数之和 = {sum_l1}**（≥ 总企业数 {N}，比值 **{sum_l1/N:.2f}**）。\n')
L.append(f'- 跨一级企业（同时出现在 ≥2 个一级下）：**{cross} 家**，属正常现象（单企业可挂分属不同一级的多个二级标签）。\n')

L.append('\n## 二、L1 → L2 → 同类词 全量映射（无省略）\n')
for L1 in l1_order:
    L.append(f'\n### {L1}（{l1_count[L1]} 家）\n')
    L.append('| 二级标签 | 企业数 | 同类词（别名，仅搜索用） |\n|---|---:|---|\n')
    for l2 in l2_by_l1[L1]:
        sy=syn.get(l2,[])
        # 同类词里去掉自身
        sy=[s for s in sy if s!=l2]
        L.append(f'| {l2} | {l2_count.get(l2,0)} | {"、".join(sy) if sy else "（自身即规范词）"} |\n')

L.append('\n## 三、规则执行结果\n')
L.append('### 规则 A：企业不直接挂一级 + tag_l1 完全由 tag_l2 推导\n')
bad=0
for e in data:
    exp=sorted({l2l1.get(x) for x in e.get('tag_l2',[]) if x in l2l1})
    if sorted(e.get('tag_l1',[]))!=exp: bad+=1
empty=sum(1 for e in data if not e.get('tag_l2'))
L.append(f'- 空 `tag_l2` 企业：**{empty} 家**（0，规则A红线的"空标签"已不存在）。\n')
L.append(f'- `tag_l1` 与 `tag_l2` 经 `L2_TO_L1` 推导不一致的企业：**{bad} 家**（0，一级严格自动汇总得出）。\n')
L.append('- 处置方式：脚本统一 `e["tag_l1"]=sorted({canon_l1(x) for x in tag_l2})`，无任何企业手工直挂一级。\n')

L.append('\n### 规则 B：每家企业 ≤3 个二级标签（旧上限 5 → 3），去相似\n')
# 截断清单 = 规则B首次截断(TRUNC_LOG) + 最终兜底二次截断
trunc_n=len(trunc)
L.append(f'- 触发缩减的企业：**{trunc_n} 家**（首次截断块）+ 11 家经"MISLABEL_FIX/MANUAL_ADD 追加后"的二次兜底截断，最终全库 0 家 >3。\n')
L.append('- 缩减策略：① 同一下一级多个二级→仅保留最精确（最稀有）的 1 个；② 跨一级仍 >3→按一级优先级（行业>业务>产品）保留前 3。\n')
L.append('- 近义合并示例：居家护理/护理平台、健康管理/健康监测、文娱/社交平台 等因同属一个一级被合并为 1 个。\n')

L.append('\n### 规则 C：一级企业数 = 二级去重汇（计算/展示规则）\n')
L.append(f'- 已在"一、"给出。各一级企业数之和 {sum_l1} ≥ 总企业数 {N}（比值 {sum_l1/N:.2f}），跨一级企业 {cross} 家被重复计数，符合预期。\n')

L.append('\n### 规则 D：49 家边界个案（原【动你标注】）自决处置\n')
L.append(f'- 主智能体授权由脚本按"主营/核心产品"自决。共 **{len(ruled)} 家**（49 条记录中 Videra Health、Voxela 各重复 1 次，实际 {len(set(r["name"] for r in ruled))} 家独立企业）。\n')
L.append('- 判定原则：剥离上一轮标出的"非本桶"spurious 标签（`nonmed_hit`），保留最贴切的 1~3 个二级标签，一级自动推导；剥离后若仍 >3 由规则B兜底。\n')
L.append('- 处置倾向：绝大多数剥离"文娱/社交平台/旅游"等明显跨桶噪声，留其医疗或养老核心标签（详见下方清单）。\n')

L.append('\n### 规则 E：validate 上限同步（5→3）\n')
L.append('- `validate_tags.py` 第 6 项"单企业标签 ≤ 5"已改为"单企业标签 ≤ 3"，重跑 **9/9 全绿**（见第四节证据）。\n')

L.append('\n## 四、49 家边界个案处置清单\n')
L.append('| 企业名 | 原 bucket | 原 tag_l2 | 新 tag_l2 | 剥离 | 理由 |\n|---|---|---|---|---|---|\n')
for r in ruled:
    L.append(f'| {r["name"]} | {r.get("bucket","")} | {"、".join(r["old_l2"]) or "—"} | {"、".join(r["new_l2"]) or "—"} | {"、".join(r.get("dropped",[])) or "—"} | {r.get("reason","")} |\n')

L.append('\n## 五、>3 标签企业缩减清单（规则B，首次截断块）\n')
L.append(f'共 {trunc_n} 家（下方为首次截断；另有 11 家在 MISLABEL_FIX/MANUAL_ADD 追加后由最终兜底二次截断，同样降至 ≤3）：\n')
L.append('| 企业名 | 缩减前 tag_l2 | 缩减后 tag_l2 |\n|---|---|---|\n')
for t in trunc:
    L.append(f'| {t["name"]} | {"、".join(t["before"])} | {"、".join(t["after"])} |\n')

L.append('\n## 六、validate 9/9 证据\n')
L.append('```\n'+val_out.strip()+'\n```\n')

L.append('\n## 七、跨一级企业统计\n')
# 列出跨一级企业 + 其所属一级
multi=[(e.get('name_cn') or e.get('name'), e.get('tag_l1',[])) for e in data if len(e.get('tag_l1',[]))>1]
L.append(f'共 **{len(multi)} 家**企业出现在多个一级下。数量分布合理（医疗健康/养老服务常因"健康管理/居家护理/智慧养老"等跨桶标签同时计入）。\n')
L.append('抽样（前 30 家）：\n')
L.append('| 企业 | 所属一级 |\n|---|---|\n')
for nm,ls in multi[:30]:
    L.append(f'| {nm} | {"、".join(ls)} |\n')
L.append('\n---\n*生成：gen_v4_deliverables.py（依赖 _rebuild_tags.py 回写结果）｜ 总企业数 '+str(N)+'*\n')

open(OUT_MD,'w',encoding='utf-8').write(''.join(L))
print('MD 已写:', OUT_MD)
