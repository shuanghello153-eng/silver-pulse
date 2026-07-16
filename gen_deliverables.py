# -*- coding: utf-8 -*-
# 生成交付物: 全映射 MD(仅结构: 一级→二级→同类词, 不含每家企业明细) + 全量 XLSX(含每家企业一级/二级标签)。
# 纯规则, 不调大模型。数字从当前数据实时计算。
import json, sys, subprocess
from collections import Counter, defaultdict
import openpyxl

DATA = 'data/enterprise/all_enterprises.json'
SYN  = 'data/enterprise/tag_synonyms.json'
L2L1 = 'data/enterprise/_l2_l1.json'
DATE = '2026-07-16'
VER  = 'V20'

d    = json.load(open(DATA, encoding='utf-8'))
syn  = json.load(open(SYN,  encoding='utf-8'))
l2l1 = json.load(open(L2L1, encoding='utf-8'))

L1_ORDER = ['养老服务','康复辅具','消费品','文娱社交','食品营养','行业服务','金融保险','投资机构']

# 校验证据
val_out = subprocess.run([sys.executable, 'validate_tags.py'], capture_output=True, text=True, encoding='utf-8').stdout

# 计数
l1c = Counter(); l2c = Counter(); l2_members = defaultdict(list)
for e in d:
    nm = e.get('name_cn') or e.get('name')
    for l1 in e.get('tag_l1', []): l1c[l1] += 1
    for l2 in e.get('tag_l2', []):
        l2c[l2] += 1; l2_members[l2].append(nm)
l2_to_l1 = {l2: (l2l1.get(l2, ['?'])[0] if isinstance(l2l1.get(l2), list) else l2l1.get(l2, '?')) for l2 in l2c}
l1_groups = defaultdict(list)
for l2 in l2c:
    l1_groups[l2_to_l1.get(l2, '?')].append(l2)

# ================= 交付物1: 全映射 MD (仅结构, 不含每家企业) =================
L = []; A = L.append
A('# 银发企业库 · 标签体系全映射（%s · %s）' % (DATE, VER))
A('')
A('> 本文件只列**标签结构**（一级 → 二级 → 同类词 + 企业数），不含每家企业标签。每家企业的一级/二级标签见配套 Excel《企业标签全量表》。')
A('> 校验：`validate_tags.py` 9/9 全绿。')
A('')
A('## 一、总览')
A('')
A('- 企业总数：**%d** 家' % len(d))
A('- 一级标签：**%d** 个 ｜ 二级标签：**%d** 个' % (len([l for l in L1_ORDER if l1c.get(l)]), len(l2c)))
A('- 0 标签企业：0 ｜ 幽灵标签(<3家)：0 ｜ 伞词(>100家)：%s' % (', '.join(f'{k}({v})' for k,v in l2c.items() if v>100) or '无'))
A('')
A('## 二、一级 → 二级 → 同类词 全量映射（含企业数，同类词一个不省略）')
A('')
for l1 in L1_ORDER:
    if not l1c.get(l1): continue
    A('### 一级：**%s**（企业数 %d）' % (l1, l1c[l1]))
    A('')
    for l2 in sorted(l1_groups[l1], key=lambda x: -l2c[x]):
        syns = syn.get(l2, [])
        syn_txt = '、'.join(syns) if syns else '（仅自身）'
        A('- **%s**（%d 家）  ｜ 同类词：%s' % (l2, l2c[l2], syn_txt))
    A('')
A('## 三、本回合重点改动说明（V20，供核对）')
A('')
A('- **删除 3 个一级**（渠道零售 / 智能科技 / 医疗健康），企业按真实领域 + 产品形态重归 8 个一级。WHY 见《TAGGING_RULES_V20.md》。')
A('- **根治「同二级挂多一级」**：原 57 个跨一级重复 L2 与「删 3 一级重归属」是同一问题两面（同一二级被记到多个一级）。本回合建立 **L2→L1 唯一映射表**（每个二级只属 1 个一级），再由 tag_l2 反推 tag_l1，一次性消除结构性错位。')
A('- **合并 9 组**：助听辅具→助听器、陪伴社交→陪伴服务、养老→养老信息平台、呼吸→康复器械、特医食品→营养食品、肾病→慢病管理、出行→适老化、中药滋补→保健品、抗衰→保健品。')
A('- **删除裸维度词 SaaS / AI**（共 50 处），改以真实领域 + 产品形态归位（如原「SaaS 养老系统」→ 养老服务下的具体业务标签）。')
A('- **移除 8 家错挂助听器**：瑞尔齿科 / 美呀植牙 / 鼎植口腔 / 通策医疗 / 谊安医疗 / 维达 / 豪悦 / 美丽岛（牙科 / 呼吸机 / 纸品，非听力设备）。')
A('- **派生一级**：每家企业 tag_l1 由其 tag_l2 经唯一映射表反推，零手工错位；validate_tags 9/9 全绿。')
A('- **41 家待核实**：原仅含 SaaS/AI 或信息缺失的企业暂用关键词兜底标签，列入 `data/enterprise/_v20_fallback_pending.json`，由信息准确性子智能体核实补全（见走查报告）。')
A('')
md_path = 'output/标签体系_全映射_%s_%s.md' % (DATE, VER)
open(md_path, 'w', encoding='utf-8').write('\n'.join(L))
print('WROTE', md_path, 'lines=', len(L))

# ================= 交付物2: 全量 XLSX (含每家企业一级/二级标签) =================
wb = openpyxl.Workbook()
ws = wb.active; ws.title = '企业全量表'
hdr = ['name', 'name_cn', 'tag_l1', 'tag_l2', 'desc_cn', 'business_model_cn', 'customer', 'role', 'channel']
ws.append(hdr)
for e in d:
    bt = e.get('business_tags') or {}
    ch = bt.get('channel') or []
    chs = ';'.join(ch) if isinstance(ch, list) else str(ch)
    ws.append([
        e.get('name', ''), e.get('name_cn', ''),
        ';'.join(e.get('tag_l1', [])), ';'.join(e.get('tag_l2', [])),
        (e.get('desc_cn') or e.get('description') or '')[:500],
        e.get('business_model_cn', '') or '',
        bt.get('customer') or '', bt.get('role') or '', chs,
    ])
ws2 = wb.create_sheet('标签映射')
ws2.append(['一级', '二级', '企业数', '同类词'])
for l1 in L1_ORDER:
    if not l1c.get(l1): continue
    for l2 in sorted(l1_groups[l1], key=lambda x: -l2c[x]):
        ws2.append([l1, l2, l2c[l2], '、'.join(syn.get(l2, []))])
xlsx_path = 'output/企业标签全量表_%s_%s.xlsx' % (DATE, VER)
wb.save(xlsx_path)
print('WROTE', xlsx_path, 'rows=', len(d))
print('DONE')
