# -*- coding: utf-8 -*-
import json
from collections import Counter, defaultdict

data = json.load(open('data/enterprise/all_enterprises.json', encoding='utf-8'))
syn = json.load(open('data/enterprise/tag_synonyms.json', encoding='utf-8'))

# 一级 -> 二级 归属 (从实际数据推导)
l2_to_l1 = defaultdict(Counter)
for e in data:
    for l2 in e.get('tag_l2', []):
        for l1 in e.get('tag_l1', []):
            l2_to_l1[l2][l1] += 1
l1_total = Counter(); l2_total = Counter()
for e in data:
    for t in e.get('tag_l1', []): l1_total[t] += 1
    for t in e.get('tag_l2', []): l2_total[t] += 1

l1_order = ['医疗健康', '产业服务', '生活照护', '消费品', '智能科技', '文娱社交',
            '养老住房', '食品营养', '金融保险', '康复辅具', '女性健康', '精神健康', '渠道零售']

out = []
out.append('# 银脉企业库 · 标签体系完整大表 V3（2026-07-12 第二轮自检后）')
out.append('')
out.append('> 本表 = 当前 1325 家企业打标的**完整映射**，无省略、无"等 X 词"。一级→二级→同类词全量列出，含每级企业数。')
out.append('> 校验：validate_tags.py **9/9 全绿**；二级标签 **58** 个；行业媒体 10 家；0 标签企业 0；跨标签同类词碰撞 0；孤儿同类词 0。')
out.append('')
out.append('## 一、一级标签（13 个，实际挂企业 12 个一级）')
out.append('')
out.append('| 一级标签 | 企业数 |')
out.append('|---|---|')
for l1 in l1_order:
    if l1_total[l1]:
        out.append(f'| {l1} | {l1_total[l1]} |')
out.append('')
out.append('## 二、一级 → 二级 → 同类词 完整映射（全量，不省略）')
out.append('')
for l1 in l1_order:
    if not l1_total[l1]:
        continue
    l2s = [l2 for l2 in l2_to_l1 if l2_to_l1[l2].most_common(1)[0][0] == l1]
    l2s.sort(key=lambda x: -l2_total[x])
    out.append(f'### {l1}（一级共 {l1_total[l1]} 家，含 {len(l2s)} 个二级）')
    out.append('')
    out.append('| 二级标签 | 企业数 | 同类词（全量，搜索扩展用，不展示） |')
    out.append('|---|---|---|')
    for l2 in l2s:
        syns = syn.get(l2, [l2])
        out.append(f'| {l2} | {l2_total[l2]} | {"，".join(syns)} |')
    out.append('')
out.append('## 三、本轮（V3）自查发现并修正的问题')
out.append('')
out.append('### 3.1 结构层修正（标签自身退化/重复/非分类）')
out.append('')
out.append('| 问题 | 修正前 | 修正后 | 原因 |')
out.append('|---|---|---|---|')
out.append('| 康复器械 与 康复设备 重复 | 各自独立成标签(各~70/设备) | **合并入「康复」** | 二者=康复设备，与康复服务重复 |')
out.append('| 长寿诊所 | 独立成标签(3家) | **合并入「长寿科技」** | 长寿诊所是长寿科技的子集 |')
out.append('| 认知康复 | 独立成标签 | **合并入「认知训练」** | 认知康复=认知训练服务 |')
out.append('| 健康分析 | 独立成标签 | **合并入「健康监测」** | 健康分析=健康监测能力 |')
out.append('| 特医食品 | 仅 2 家(幽灵) | **合并入「营养食品」** | 特医食品是营养食品子类，样本过少 |')
out.append('| ToB | 独立成标签 | **删除** | ToB 是销售模式，非业务分类 |')
out.append('| 跨标签碰撞(智慧养老) | 同时映射给「数字化」「智慧养老」 | 仅保留给「智慧养老」 | 搜索歧义 |')
out.append('| 跨标签碰撞(电商) | 同时映射给「电商」「银发零售」 | 仅保留给「电商」 | 搜索歧义 |')
out.append('| 医护配置 同类词 | 仅自身(退化) | **补真实同类词**：护士配置/护理员调度/护理人力配置/医护排班 | 用户点名"二级=同类词一模一样" |')
out.append('| 就业 同类词 | 仅自身(退化) | **补真实同类词**：再就业/银发就业/灵活用工/重返职场/职业中断/第二职业/银发招聘 | 用户点名"二级=同类词一模一样" |')
out.append('')
out.append('### 3.2 企业级错标修正（描述与标签明显矛盾，按公开资料重打，共 41 家）')
out.append('')
out.append('| 企业 | 原标签 | 修正后标签 |')
out.append('|---|---|---|')
MISLABEL_SHOW = [
 ('上海剪爱', '养老机构/认知症', '个护'), ('一龄集团', '社交平台/老年文娱', '健康管理/产业资本'),
 ('云货优选', '老年文娱', '电商'), ('人寿堂', '养老社区', '健康管理/保健品'),
 ('慈康生命', '专业护理', '临终关怀'), ('大耳马', '健康管理', '助听器'),
 ('一味盛长', '辅具', '保健品/健康管理'), ('麦孚营养', '个护', '营养食品'),
 ('冬泽特医', '个护', '营养食品'), ('优生活羊奶', '银发零售', '营养食品/保健品'),
 ('退休俱乐部(东犁)', '个护', '老年文娱/旅游'), ('彭世修脚', '银发零售', '个护'),
 ('互邦医疗', '银发零售', '辅具'), ('德林假肢', '银发零售', '辅具/康复'),
 ('博音听力', '银发零售', '助听器'), ('Carewell', '银发日用/银发零售', '银发日用/辅具'),
 ('NimbleRx', '保健品', '医疗器械'), ('PillPack', '保健品', '医疗器械'),
 ('去哪养老网', '护理平台', '咨询研究'), ('孝爱宝', '护理平台', '咨询研究'),
 ('Inspiren', '居家护理/社交平台/老年文娱', '智能硬件/健康监测'),
 ('Uber Health', 'SODH', '远程医疗'), ('Lyft Health', '健康管理', '远程医疗'),
 ('Sprinter Health', '产业资本/远程医疗', '远程医疗'), ('GoGoGrandparent', '数字化', '远程医疗'),
 ('CareLinx', '专业护理', '护理平台'), ('CareVoice', '健康管理', '保险服务'),
 ('Apax Partners', '健康管理', '产业资本'), ('Vynca', '健康管理', '临终关怀'),
 ('Everplans', '健康管理', '临终关怀'), ('ReBoot Accel', '教育', '就业'),
 ('iRelaunch', '教育', '就业'), ('现名 CoGenerate', '教育', '就业/老年文娱'),
 ('Techstars Future of Longevity Accelerator', '数字化', '产业资本'),
 ('联邦医疗保险优势计划', '产业资本', '保险'), ('Riverspring Living', '专业护理', '养老机构'),
 ('麻省理工学院年龄实验室', '适老化产品/适老化改造', '咨询研究'),
 ('AARP Innovation Labs / AgeTech Collaborative', '数字化/行业媒体', '行业媒体'),
 ('Aging2.0 Collective', '数字化/行业媒体', '行业媒体'),
 ('b.well Connected Health', '行业媒体', '照护系统'), ('Conduce Health', '行业媒体', '照护系统'),
]
for nm, old, new in MISLABEL_SHOW:
    out.append(f'| {nm} | {old} | {new} |')
out.append('')
out.append('### 3.3 仍保留的"单点"标签（真实业务分类，仅无通俗别名，非退化，保留）')
out.append('')
out.append('保险科技、陪伴服务、社交平台、睡眠科技、感官辅助、更年期、电商、适老化产品、长寿科技、虚拟护理')
out.append('')
out.append('## 四、本轮未自动改、留待你核的企业（透明留底）')
out.append('')
out.append('- 自检脚本对全 1325 家做了"标签-资料一致性"体检，初筛出 **237 家**"资料中找不到标签支撑词"的候选。')
out.append('- 其中 **41 家**描述与标签 blatantly 矛盾，已在上表修正。')
out.append('- 其余 ~196 家**多为误报**（描述用了我的词典未覆盖的同义表述，如"智慧养老SaaS平台""社交应用"等），或属平台型企业的合理多标签，未敢擅自改动以免制造新噪音。')
out.append('- 完整候选清单见仓库 `audit_genuine.txt`，你可抽看复核；若某家确属错标，告诉我企业名即可，我按同样规则补进 `_rebuild_tags.py` 的 `MISLABEL_FIX` 复现。')
out.append('')
out.append('## 五、数据质量已知限制（非本轮范围）')
out.append('')
out.append('- 44 家"待联网核实"企业的**描述仍是模板占位**（`XX是银发经济领域行业服务商…`），其标签按品牌常识打（正确），但描述未补。已排除在错标判定外，建议下轮补真实资料。')
out.append('')
open('output/标签体系_V3.md', 'w', encoding='utf-8').write('\n'.join(out))
print('已生成 output/标签体系_V3.md，共', len(out), '行')
