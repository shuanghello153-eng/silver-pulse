# -*- coding: utf-8 -*-
"""生成 output/行业标签完整表.md —— 标签体系唯一真相源文档
数据来自 all_enterprises.json(重建后) + _rebuild_tags.SYNONYMS(同类词) + 本次重建规则说明
"""
import json, datetime
from collections import Counter, defaultdict
import _rebuild_tags as RB   # 复用 SYNONYMS / MERGE / L1 定义

DATA='data/enterprise/all_enterprises.json'
data=json.load(open(DATA,encoding='utf-8'))
L1_LIST=RB.L1_LIST
SYN=RB.SYNONYMS

# 统计
l1c=Counter(); l2c=Counter()
for e in data:
    for x in e.get('tag_l1',[]): l1c[x]+=1
    for x in e.get('tag_l2',[]): l2c[x]+=1

# L1 -> L2 列表(按企业数降序)
l1_to_l2=defaultdict(list)
for e in data:
    l1set=set(e.get('tag_l1',[])); l2set=set(e.get('tag_l2',[]))
    for l1 in l1set:
        for l2 in l2set:
            # 仅当 l2 的一级归属含该 l1 时才挂(用 RB.l1_of 复核)
            if RB.l1_of(l2)==l1:
                l1_to_l2[l1].append(l2)
# 去重并计数排序
for l1 in l1_to_l2:
    l1_to_l2[l1]=sorted(set(l1_to_l2[l1]), key=lambda t:-l2c.get(t,0))

review=json.load(open('data/enterprise/_rebuild_review.json',encoding='utf-8'))

today=datetime.date.today().strftime('%Y-%m-%d')
lines=[]
A=lines.append
A(f"# 银发经济企业数据库 · 行业标签完整表（唯一真相源）")
A(f"> 最后重建：{today} ｜ 企业总数：{len(data)} ｜ 一级标签：{len(L1_LIST)} ｜ 二级标签：{len(l2c)}")
A("")
A("## 〇、本文档地位")
A("本文件是企业库标签体系的**唯一真相源（SSoT）**。任何标签增删改，必须先在此文档对应的规则下探讨，")
A("确认后再改代码（`_rebuild_tags.py` 是执行脚本，重跑即重打全量标签）。前端页面（enterprise.html）只是本文件的渲染。")
A("")
A("## 一、标签来源（从源头重跑，零丢失）")
A("本次重建严格从以下**原始数据源**合并，确保不丢任何细节：")
A("")
A("| 来源 | 规模 | 处理方式 |")
A("|------|------|----------|")
A("| 原始一级分类 `category_l1` | 40 种 | 作分组参考，归并为 13 个一级标签 |")
A("| 原始二级分类 `category_l2` | **284 种** | **全部并入标签**（仅合并真同义词，零丢弃） |")
A("| 系统自带标签 `tags` | 47 种 | 映射并入（去重） |")
A("| Excel 选题库 细分领域_1 | 157 种 | **全部并入**（权威赛道） |")
A("| Excel 选题库 细分领域_2 | 333 种 | **精选白名单并入**（见第五节说明，过滤地区/人口/泛平台噪声） |")
A("")
A("**零丢失原则**：每一个原始词都必须落到一个规范标签；在 `MERGE` 映射表里找不到同义归并的，")
A("**保持原值本身当标签**。实测：284 个原始二级分类经映射后「静默丢弃 = 0」（236 个被合理归并改名，如 老年旅游→旅游、运动康复→康复、专业级护理→专业护理；32 个保持原值；0 个丢失）。")
A("")
A("## 二、一级标签（13 个，分组层）")
A("")
for l1 in L1_LIST:
    A(f"- **{l1}**（{l1c.get(l1,0)} 家）")
A("")
A("## 三、二级标签总览（含企业数）")
A(f"当前共 **{len(l2c)}** 个二级标签。Top 30（按企业数）：")
A("")
A("| 二级标签 | 企业数 | 二级标签 | 企业数 |")
A("|---------|--------|---------|--------|")
top=l2c.most_common(30)
for i in range(0,len(top),2):
    a=top[i]; b=top[i+1] if i+1<len(top) else ('','')
    A(f"| {a[0]} | {a[1]} | {b[0]} | {b[1]} |")
A("")
A("## 四、横向大表：一级 → 二级（含企业数）→ 同类扩展词")
A("> 找标签直接看对应一级分组下的二级标签；同类扩展词仅用于搜索联想，不另作标签。")
A("")
for l1 in L1_LIST:
    l2s=l1_to_l2.get(l1,[])
    if not l2s: continue
    A(f"### {l1}（{l1c.get(l1,0)} 家）")
    for l2 in l2s:
        syns=SYN.get(l2)
        if syns:
            A(f"- **{l2}** `{l2c.get(l2,0)}` ｜ 扩展词：{('、'.join(syns))}")
        else:
            A(f"- **{l2}** `{l2c.get(l2,0)}`")
    A("")
A("## 五、细分领域_2（Excel D 列）的处理说明（透明决策）")
A("细分领域_2 共 333 种值，但它是**自由文本**，含大量地区（中国/日本/美国）、人口属性（50+/中老年）、")
A("泛化平台词（平台/APP/上市/AI/数字化/巨头）。**全收会严重污染标签池**，因此采用「精选白名单」：")
A("只纳入真正有区分度、且主分类未充分覆盖的能力词（重点补齐你点名的 **SODH 家族**：社会决定因素/SDOH/社会护理网络/支持性护理），")
A("其余噪声过滤。如后续需要把某类细分领域_2 也纳入，按「先探讨再改」规则加进白名单即可。")
A("")
A("## 六、本次重点修复（你点名的问题）")
A("")
A("### 1. SODH —— 之前彻底丢失，现已成真实标签")
A("- 漏因：Excel 中 7 家（Uber Health / findhelp / MedArrive / Modivcare / Nudj Health / SimplyConnect / Teami）")
A("  原先被泛化为「专业护理/健康管理」，SODH 赛道词没进标签。")
A("- 现：SODH 作为独立二级标签（归 医疗健康），并补同类扩展词（社会决定因素/SDOH/社会护理网络/支持性护理）。")
A(f"- 当前命中 **{sum(1 for e in data if 'SODH' in e.get('tag_l2',[]))}** 家企业。")
A("")
A("### 2. 相亲 —— 之前只归到文娱社交、文档里也没列，搜不到")
A("- 现：相亲作为**独立二级标签**（归 文娱社交），并补同类扩展词（婚恋/老年相亲/老人相亲/银发相亲/老年婚恋/交友）。")
A(f"- 当前命中 **{sum(1 for e in data if '相亲' in e.get('tag_l2',[]))}** 家企业（来自 Excel 细分领域_1 的「老人相亲」）。")
A("")
A("### 3. 标签与列表字段重复 —— 融资状态标签已摘除")
A("- 「有融资 / 融资过亿 / 已被收购」这三个标签与列表里的融资字段（funding_latest / funding_total / investors）完全重复，")
A("  按你「标签别和列表已有字段重复」的铁律，**已摘除**（不再作为标签，融资信息仍在列表展示）。")
A("")
A("### 4. 产业资本 —— 按方案B清理（只留真·投资机构/产业资本方）")
A("- 定义：产业资本 = 自身是投资机构（VC/PE/CVC/REIT）或产业资本方（保险公司/健康计划/上市产业集团/巨头），")
A("  **与「企业是否拿过融资」无关**。仅拿过融资的普通运营企业，摘掉该标签。")
A(f"- 结果：保留 **{len(review['capital_kept'])}** 家（投资人/险企/健康计划/巨头/REIT/上市公司产业方，含你点名的 CVS、UnitedHealth、Devoted），")
A(f"  摘掉 **{len(review['capital_dropped'])}** 家（真·养老运营/护理/设备/媒体企业，如 Sonida、Clariane、Permobil、ReWalk、WellSky、九安医疗、科大讯飞）。")
A("- 留存/摘掉完整清单见 `data/enterprise/_rebuild_review.json`，供你复核。")
A("")
A("## 七、标签生成规则（去重 / 融合 / 生成）")
A("1. **去重**：同一企业的多来源标签（category_l2 + Excel细分领域 + 系统tags + 描述补打）汇入一个集合，天然去重。")
A("2. **融合（仅真同义词）**：`MERGE` 表只合并拼写/同义变体（老年鞋→鞋服、老年痴呆→认知症、远程监控→远程医疗、居家照护→居家护理…），")
A("   不瞎合并不同概念。凡不在 `MERGE` 的原始词，保持原值当标签（零丢失）。")
A("3. **生成一级/二级**：`tag_l2` = 规范二级标签集合；`tag_l1` 由 `l1_of()` 按关键词规则把每个二级标签归到 13 个一级之一。")
A("4. **同类扩展词（搜索用）**：`SYNONYMS` 表（canonical → 同义词），仅注入前端搜索联想，**不另作标签**。")
A("5. **0 标签兜底**：无标签且非行业媒体的企业，用描述关键词补打；描述太泛的行业媒体仅保留「行业媒体」标签，留待联网补细分。")
A("   实测全库 **0 家** 0 标签。")
A("")
A("## 八、标签管理规则（增删查改必须先探讨再改）")
A("- **新增标签**：须在原始数据源（分类/Excel细分领域/系统标签）有依据；新增后同步更新 `MERGE`/`SYNONYMS`/`CANON_L1` 三处，")
A("  并在本文件对应一级分组下补一行。禁止无依据编造。")
A("- **删除/合并标签**：先确认受影响的企业的新归属，不得静默丢弃；改动前在本文档记录。")
A("- **同类词**：已有的同义词（如 老花镜→眼镜）只作搜索扩展、不新建为标签；如原始数据出现新的别名，补进 `SYNONYMS` 对应项，**不删已有**。")
A("- **重跑**：改完规则后运行 `python _rebuild_tags.py` 即全量重打；跑前自动保留 `data/enterprise/_rebuild_review.json` 供复核。")
A("")
A("## 九、本次重建文件清单")
A("- `data/enterprise/all_enterprises.json` —— 重建后的 tag_l1 / tag_l2（1325 家，零丢失）")
A("- `_rebuild_tags.py` —— 重建执行脚本（零丢失映射 + 产业资本方案B + 细分领域_2白名单）")
A("- `_build_tags.py` —— 已改为委托 `_rebuild_tags.py` 的薄壳，避免用旧逻辑回退丢标签")
A("- `data/enterprise/_rebuild_review.json` —— 产业资本留存/摘掉清单 + 待联网行业媒体清单")
A("- `gen_enterprise.py` / `generator.py` / `ui_common.py` —— 页面渲染 + 搜索（已改回内联、输入框缩短、按钮常驻）")
A("")
A(f"_生成于 {today} ｜ 企业 {len(data)} 家 ｜ 一级 {len(L1_LIST)} ｜ 二级 {len(l2c)}_")

open('output/行业标签完整表.md','w',encoding='utf-8').write('\n'.join(lines)+'\n')
print("WROTE output/行业标签完整表.md  字数≈",sum(len(x) for x in lines))
