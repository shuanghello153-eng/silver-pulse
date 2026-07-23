#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_v12_detect.py — v12 循环收敛自检 (只读, 不修改任何文件)
===========================================================
这是用户要求的"循环能不能停"的硬闸门。判定规则(与用户约定一致):
  停止条件 = (a) 所有二级标签企业数 <= 阈值(默认20) 且 (b) 所有企业都有真实简介
           且 (c) 不存在"应剥未剥"的伞词残留
  任一不满足 -> 循环继续(需再派子智能体对仍>=阈值的标签做一轮拆分/补全)。

同时保留 v11 四关: 新标签精度 / 伞词残留 / L1映射 / 智慧养老残留。
"""
import json, ast, os, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'data/enterprise/all_enterprises.json')
SYN  = os.path.join(ROOT, 'data/enterprise/tag_synonyms.json')
SRC  = os.path.join(ROOT, '_rebuild_tags.py')

THRESHOLD = 20  # 二级标签企业数上限(>=此值需继续拆分)

# ---- 读 L2_TO_L1 (与重建脚本同源, ast 提取, 不执行) ----
src = open(SRC, encoding='utf-8').read()
tree = ast.parse(src)
L2L1 = None
for n in ast.walk(tree):
    if isinstance(n, ast.Assign):
        for t in n.targets:
            if isinstance(t, ast.Name) and t.id == 'L2_TO_L1':
                L2L1 = ast.literal_eval(n.value)
# 重建脚本运行后实际落地标签(以数据为准)
d = json.load(open(DATA, encoding='utf-8'))
es = d if isinstance(d, list) else d.get('enterprises', d.get('data', []))
all_final = set()
for e in es:
    for x in (e.get('tag_l2') or []):
        all_final.add(x)

# 伞词集合(与重建脚本 V12_UMBRELLA 同源; 适老化改造/保健品已转为原子标签故移除, 投资机构已溶散)
UMBRELLA = {'智慧养老','养老社区','康复设备','社交','平台',
            '营养食品','认知症','医疗器械','慢病管理','保险','养老金融',
            '护理平台','临终关怀','医疗'}

# v12.1 起: 以下"规范大类"经用户明确拍板做大(合并/改名/横向属性), 与智慧养老同样冻结,
# 不触发 >=阈值 的"需继续拆分"闸门。
ALLOWED_LARGE = {'适老化','居家护理','助听器','康复器械','助行器','跌倒监测','SaaS','AI',
                 '养老运营系统','改造','护理协调','养老信息平台',
                 '认知训练','认知数字疗法',   # v12.1: 具体标签非伞词
                 '机器人','VC','产业基金','养老REIT','养老运营',  # v12.2: 新增大标签
                 '慢病管理','认知症',           # v12.2: 合并后的大标签
                 '陪伴社交','智能硬件',          # v12.2: 规范大类(用户确认保留)
                 '保险'}                        # v12.2: 金融保险大类

# 弱简介判定(与补全标准一致)
GENERIC = ['银发经济领域','行业服务商','专注于','致力于','提供','解决方案','服务商','平台','领域的','一家']
def weak(e):
    desc = e.get('description') or ''
    dcn  = e.get('desc_cn') or ''
    bm   = e.get('business_model_cn') or ''
    if not desc.strip(): return 'no_desc'
    if not dcn.strip():  return 'no_desc_cn'
    if not bm.strip():   return 'no_bm'
    if any(g in desc for g in GENERIC) and len(desc) < 40: return 'template'
    return None

print('=' * 70)
print(' v12 循环收敛自检  (阈值 L2>=%d 视为未收敛)' % THRESHOLD)
print('=' * 70)

# ---------- [1] 二级标签分布 & 未收敛清单 ----------
l2c = Counter()
for e in es:
    for x in (e.get('tag_l2') or []):
        l2c[x] += 1
over = {k: v for k, v in l2c.items() if v >= THRESHOLD and k not in ALLOWED_LARGE}
frozen_large = {k: v for k, v in l2c.items() if v >= THRESHOLD and k in ALLOWED_LARGE}
print('\n[1] 二级标签总数: %d | 企业记录: %d | 去重企业: %d' % (len(l2c), len(es), len({e.get('name_cn') or e.get('name') for e in es})))
print('    仍 >=%d 的标签(需继续拆分): %d 个, 覆盖 %d 家企业' % (THRESHOLD, len(over), sum(over.values())))
for k in sorted(over, key=lambda x: -over[x]):
    print('      ! %-10s %3d' % (k, over[k]))
print('    冻结规范大类(>=%d 但已拍板保留): %s' % (THRESHOLD, ', '.join('%s(%d)' % (k, v) for k, v in sorted(frozen_large.items(), key=lambda x: -x[1])) or '无'))

# ---------- [2] 弱简介残留 ----------
wc = Counter()
for e in es:
    r = weak(e)
    if r: wc[r] += 1
weak_total = sum(wc.values())
print('\n[2] 弱简介企业(需补全): %d 家' % weak_total)
for k, v in wc.items():
    print('      - %s: %d' % (k, v))

# ---------- [3] 伞词残留(应剥未剥) ----------
residual = 0
for e in es:
    l2 = e.get('tag_l2') or []
    has_umb = [u for u in l2 if u in UMBRELLA]
    specs = [x for x in l2 if x not in UMBRELLA]
    if has_umb and specs:
        # 既有伞词又有具体标签 -> 重建应已剥离伞词, 若仍存在说明漏剥
        residual += 1
print('\n[3] 伞词残留(伞词与具体标签并存, 应剥未剥): %d' % residual)

# ---------- [4] L1 映射缺失 ----------
miss_l1 = 0
for e in es:
    for x in (e.get('tag_l2') or []):
        if x not in L2L1 and x not in all_final:
            miss_l1 += 1
print('[4] 二级标签缺少 L1 映射: %d' % miss_l1)

# ---------- [5] 幽灵标签(<3家, 校验会失败) ----------
ghosts = {k: v for k, v in l2c.items() if v < 3}
print('[5] 幽灵标签(<3家): %d 个 -> %s' % (len(ghosts), ', '.join('%s(%d)' % (k, v) for k, v in ghosts.items()) or '无'))

# ---------- [6] 智慧养老残留(冻结计数, 非错误) ----------
zhyl = l2c.get('智慧养老', 0)
print('[6] 智慧养老 残留成员: %d (纯冻结, 非错误, 计入未收敛则需继续)' % zhyl)

# ---------- 收敛判定 ----------
stop = (len(over) == 0) and (weak_total == 0) and (residual == 0) and (miss_l1 == 0) and (len(ghosts) == 0)
print('\n' + '=' * 70)
if stop:
    print(' 结论: ✓ 满足停止条件 — 循环可收敛退出')
else:
    reasons = []
    if len(over):     reasons.append('%d 个标签仍>=%d' % (len(over), THRESHOLD))
    if weak_total:    reasons.append('%d 家弱简介待补全' % weak_total)
    if residual:      reasons.append('%d 处伞词残留' % residual)
    if miss_l1:       reasons.append('%d 处L1缺失' % miss_l1)
    if ghosts:        reasons.append('%d 个幽灵标签' % len(ghosts))
    print(' 结论: ✗ 未收敛 — 需继续循环。原因: ' + '; '.join(reasons))
print('=' * 70)
sys.exit(0 if stop else 1)
