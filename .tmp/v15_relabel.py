#!/usr/bin/env python3
"""
v15 标签整改（2026-07-15 晚 · 小爽逐条指令）
=====================================
执行内容：
1. Carewell → 养老 + 电商
2. 删除6个二级标签：养老运营(65)、认知数字疗法(23)、健康服务平台(22)、健康管理(12)、神经调控(12)、文娱短视频(56)
3. 拆分2个标签：抗衰老药物→抗衰+药品(11)、认知症药品→认知症+药品(5)
4. 改名：长护险经办→长护险(5)
5. 认知训练(30)重新走查
6. 不删除任何企业，全部分配到其他标签
7. 清理 _l2_l1.json / tag_synonyms.json 中已删标签
"""

import json, re, copy
from collections import Counter

DATA_DIR = 'data/enterprise'
ENTERPRISE_FILE = f'{DATA_DIR}/all_enterprises.json'
L2L1_FILE = f'{DATA_DIR}/_l2_l1.json'
SYNONYMS_FILE = f'{DATA_DIR}/tag_synonyms.json'

d = json.load(open(ENTERPRISE_FILE))
l2l1 = json.load(open(L2L1_FILE))
synonyms = json.load(open(SYNONYMS_FILE))

original = copy.deepcopy(d)
changelog = []

def relabel(e, old_tags, new_tags, reason):
    """替换企业标签，记录变更"""
    e['tag_l2'] = new_tags
    # 重建 tag_l1
    new_l1 = set()
    for t in new_tags:
        if t in l2l1:
            for parent in l2l1[t]:
                new_l1.add(parent)
    e['tag_l1'] = sorted(new_l1)
    changelog.append(f"{e['name']} | {old_tags} → {new_tags} | {reason}")

# ============================================================
# 1. Carewell → 养老 + 电商
# ============================================================
for e in d:
    if 'carewell' in e['name'].lower() or 'Carewell' in e['name']:
        old = list(e.get('tag_l2', []))
        relabel(e, old, ['养老', '电商'], '小爽指令: Carewell=养老+电商')
        print(f"[1] Carewell → 养老+电商")

# ============================================================
# 2. 拆分标签：抗衰老药物→抗衰+药品, 认知症药品→认知症+药品
# ============================================================
SPLIT_MAP = {
    '抗衰老药物': ['抗衰', '药品'],
    '认知症药品': ['认知症', '药品'],
}

for label, new_labels in SPLIT_MAP.items():
    # 注册新标签到 l2l1 和 synonyms
    for nl in new_labels:
        if nl not in l2l1:
            if nl == '抗衰':
                l2l1[nl] = ['食品营养']
            elif nl == '药品':
                l2l1[nl] = ['医疗健康']
            elif nl == '认知症':
                l2l1[nl] = ['医疗健康']
            print(f"  [注册新标签] {nl} → {l2l1[nl]}")
        if nl not in synonyms:
            if nl == '抗衰':
                synonyms[nl] = ['抗衰老', '抗老化', '长寿科技', 'longevity']
            elif nl == '认知症':
                synonyms[nl] = ['认知障碍', '阿尔茨海默', '痴呆', '失智', '阿尔兹海默症', 'dementia', 'Alzheimer']
            print(f"  [注册同类词] {nl} → {synonyms[nl]}")

    count = 0
    for e in d:
        if label in e.get('tag_l2', []):
            old = list(e['tag_l2'])
            new = [nl if t == label else t for t in old]
            # 去重并保持顺序
            seen = set()
            deduped = []
            for t in new:
                if t not in seen:
                    deduped.append(t)
                    seen.add(t)
            relabel(e, old, deduped, f'拆分{label}→{"+".join(new_labels)}')
            count += 1
    print(f"[2] {label} → {'+'.join(new_labels)} ({count}家)")

    # 从 l2l1/synonyms 删除旧标签
    if label in l2l1:
        del l2l1[label]
    if label in synonyms:
        del synonyms[label]

# ============================================================
# 3. 改名：长护险经办 → 长护险
# ============================================================
RENAME_MAP = {'长护险经办': '长护险'}
for old_name, new_name in RENAME_MAP.items():
    # 更新 l2l1
    if old_name in l2l1:
        l2l1[new_name] = l2l1.pop(old_name)
    # 更新 synonyms
    if old_name in synonyms:
        synonyms[new_name] = synonyms.pop(old_name)
    # 更新所有企业的 tag_l2
    count = 0
    for e in d:
        if old_name in e.get('tag_l2', []):
            old = list(e['tag_l2'])
            new = [new_name if t == old_name else t for t in old]
            relabel(e, old, new, f'改名:{old_name}→{new_name}')
            count += 1
    print(f"[3] {old_name} → {new_name} ({count}家)")

# ============================================================
# 4. 删除标签 & 企业重分配
# ============================================================

# --- 4a. 养老运营 (65家) 重分配 ---
def redistribute_养老运营(e):
    """根据企业描述和现有标签，分配新标签"""
    name = e['name']
    desc = (e.get('desc_cn') or e.get('description') or '').lower()
    others = [t for t in e.get('tag_l2', []) if t != '养老运营']

    # 已有其他好标签的，直接去掉养老运营
    if others:
        return others

    # 真正的养老机构运营商
    operator_keywords = ['养老机构', '康养服务', '连锁养老', '护理型养老', '医养结合',
                         '养老社区', '养老院', '敬老院', 'assisted living', 'nursing home',
                         '养老产业平台', '养老运营商']
    for kw in operator_keywords:
        if kw in desc:
            return ['养老机构']

    # SaaS / 信息化
    saas_keywords = ['saas', '信息化', '管理系统', '智慧养老', '数字化解决方案',
                     '运营平台', '物联网平台', '智慧养老平台', '一体化智慧']
    for kw in saas_keywords:
        if kw in desc:
            return ['SaaS']

    # 康复/医疗器械
    rehab_keywords = ['康复', '训练设备', '医疗器械']
    for kw in rehab_keywords:
        if kw in desc:
            return ['康复医疗']

    # 跌倒监测/安全
    safety_keywords = ['跌倒', '毫米波雷达', '无感', '报警', '监测硬件', '传感']
    for kw in safety_keywords:
        if kw in desc:
            return ['跌倒监测']

    # 居家护理/照护
    homecare_keywords = ['居家', '上门', '社区托管', '照护服务']
    for kw in homecare_keywords:
        if kw in desc:
            return ['居家护理']

    # 适老化/家居
    agefriendly_keywords = ['适老化', '无障碍改造', '家居', '配套产品']
    for kw in agefriendly_keywords:
        if kw in desc:
            return ['适老化']

    # 老博会/媒体
    if '博览会' in desc or '展会' in desc or '老博会' in name:
        return ['行业媒体']

    # CCRC / 高端社区
    ccrc_keywords = ['ccrc', '退休社区', 'retirement community', '高端客群']
    for kw in ccrc_keywords:
        if kw in desc:
            return ['CCRC']

    # 护工/人力
    hr_keywords = ['护工', '人才培训', '护理人员匹配']
    for kw in hr_keywords:
        if kw in desc:
            return ['护工培训']

    # 护理协调/管理工具
    coord_keywords = ['护理协调', '活动组织', '综合管理', '运营平台', '护理自动化']
    for kw in coord_keywords:
        if kw in desc:
            return ['护理协调']

    # 机器人
    robot_keywords = ['机器人', '配送机器人', '消毒']
    for kw in robot_keywords:
        if kw in desc:
            return ['机器人']

    # 陪伴机器人
    companion_bot = ['治疗机器人', '海豹', '缓解焦虑']
    for kw in companion_bot:
        if kw in desc:
            return ['陪伴机器人']

    # 物联网/传感
    iot_keywords = ['物联网', 'lorawan', '传感', '雷达检测']
    for kw in iot_keywords:
        if kw in desc:
            return ['智能家居']

    # 默认归养老机构（大部分养老运营确实是机构）
    return ['养老机构']


count = 0
for e in d:
    if '养老运营' in e.get('tag_l2', []):
        old = list(e['tag_l2'])
        new = redistribute_养老运营(e)
        relabel(e, old, new, f'删除养老运营→重分配({"+".join(new)})')
        count += 1
print(f'[4a] 养老运营→删除+重分配 ({count}家)')

# --- 4b. 认知数字疗法 (23家) → 并入认知训练 ---
count = 0
for e in d:
    if '认知数字疗法' in e.get('tag_l2', []):
        old = list(e['tag_l2'])
        new = [t if t != '认知数字疗法' else '认知训练' for t in old]
        # 去重
        seen, deduped = set(), []
        for t in new:
            if t not in seen:
                deduped.append(t)
                seen.add(t)
        relabel(e, old, deduped, '删除认知数字疗法→并入认知训练')
        count += 1
print(f'[4b] 认知数字疗法→并入认知训练 ({count}家)')
if '认知数字疗法' in l2l1: del l2l1['认知数字疗法']
if '认知数字疗法' in synonyms: del synonyms['认知数字疗法']

# --- 4c. 健康服务平台 (22家) 重分配 ---
def redistribute_健康服务平台(e):
    desc = (e.get('desc_cn') or e.get('description') or '').lower()
    name = e['name'].lower()
    others = [t for t in e.get('tag_l2', []) if t != '健康服务平台']

    if others:
        return others

    # 医疗用车
    if any(kw in desc for kw in ['用车', '接送', 'lyft health', 'uber health', '非紧急医疗']):
        return ['出行服务']

    # 保险相关
    if any(kw in desc for kw in ['保险计划', 'medicare advantage', '会员激活', '福利执行',
                                  '按价值付费', '责任医疗', '医保']):
        return ['保险']

    # SaaS/平台
    if any(kw in desc for kw in ['saas', '平台', 'api', '数据层', '数字化']):
        return ['SaaS']

    # 居家护理/专业护理
    if any(kw in desc for kw in ['护理', '居家', '临床级', '机构级', '专业老年护理']):
        return ['居家护理']

    # 慢病/健康
    if any(kw in desc for kw in ['慢病', '健康管理', '健康服务', '就医管理']):
        return ['慢病管理']

    # 医疗导航/协调
    if any(kw in desc for kw in ['导航', '资源对接', '匹配医疗', '福利导航']):
        return ['护理协调']

    # AI通信/辅助
    if any(kw in desc for kw in ['ai通信', '字幕', '转录', '耳聋', '重听']):
        return ['助听器']

    # 默认 SaaS（大多数"健康服务平台"本质是给医疗机构用的 SaaS）
    return ['SaaS']


count = 0
for e in d:
    if '健康服务平台' in e.get('tag_l2', []):
        old = list(e['tag_l2'])
        new = redistribute_健康服务平台(e)
        relabel(e, old, new, f'删除健康服务平台→重分配({"+".join(new)})')
        count += 1
print(f'[4c] 健康服务平台→删除+重分配 ({count}家)')
if '健康服务平台' in l2l1: del l2l1['健康服务平台']
if '健康服务平台' in synonyms: del synonyms['健康服务平台']

# --- 4d. 健康管理 (12家) 重分配 ---
def redistribute_健康管理(e):
    desc = (e.get('desc_cn') or e.get('description') or '').lower()
    others = [t for t in e.get('tag_l2', []) if t != '健康管理']

    if others:
        return others

    # 体检筛查类
    if any(kw in desc for kw in ['体检', '筛查', '早筛', 'mri', '血液生物标志物',
                                  '诊断', '健康指标', '健康测评', 'aging diagnostics',
                                  '纵向数据', '年度体检']):
        return ['体检筛查']

    # 预立指示/临终关怀
    if any(kw in desc for kw in ['预立医疗指示', '临终关怀']):
        return ['临终关怀']

    # 慢病管理
    if any(kw in desc for kw in ['慢病', '健康路径', '福祉改善', '个性化健康']):
        return ['慢病管理']

    # 数字健康
    if any(kw in desc for kw in ['数字健康', '健康养生', '专科养生']):
        return ['慢病管理']

    return ['体检筛查']  # 大部分健康管理公司都是做体检/筛查的


count = 0
for e in d:
    if '健康管理' in e.get('tag_l2', []):
        old = list(e['tag_l2'])
        new = redistribute_健康管理(e)
        relabel(e, old, new, f'删除健康管理→重分配({"+".join(new)})')
        count += 1
print(f'[4d] 健康管理→删除+重分配 ({count}家)')
if '健康管理' in l2l1: del l2l1['健康管理']
if '健康管理' in synonyms: del synonyms['健康管理']

# --- 4e. 神经调控 (12家) 重分配 ---
def redistribute_神经调控(e):
    desc = (e.get('desc_cn') or e.get('description') or '').lower()
    others = [t for t in e.get('tag_l2', []) if t != '神经调控']

    if others:
        return others

    # 康复设备/医疗器械
    if any(kw in desc for kw in ['医疗设备', '脑起搏器', 'dbs', '经颅磁刺激', 'tms',
                                  '植入式', '康复机器人', '康复设备', 'fes', '功能性电刺激',
                                  '神经康复', '感知觉修复']):
        return ['康复器械']

    # BCI/脑机接口
    if any(kw in desc for kw in ['脑机接口', 'bci', '脑电']):
        return ['智能硬件']

    # 可穿戴
    if any(kw in desc for kw in ['可穿戴', '穿戴式', '前庭系统', '平衡']):
        return ['可穿戴监测']

    # 认知训练
    if any(kw in desc for kw in ['认知障碍', '认知反馈', '脑认知']):
        return ['认知训练']

    # 尿失禁（已有尿失禁标签的企业）
    if '尿失禁' in others:
        return others

    return ['康复器械']


count = 0
for e in d:
    if '神经调控' in e.get('tag_l2', []):
        old = list(e['tag_l2'])
        new = redistribute_神经调控(e)
        relabel(e, old, new, f'删除神经调控→重分配({"+".join(new)})')
        count += 1
print(f'[4e] 神经调控→删除+重分配 ({count}家)')
if '神经调控' in l2l1: del l2l1['神经调控']
if '神经调控' in synonyms: del synonyms['神经调控']

# --- 4f. 文娱短视频 (56家) 重分配（重点：模板污染清理）---
def redistribute_文娱短视频(e):
    """
    文娱短视频是模板污染重灾区。
    大量企业被统一模板描述错标为 文娱社交+文娱短视频+兴趣社群+陪伴服务+陪伴社交。
    策略：
      - 已有具体标签的(文娱/短视频/教育/健身/旅游/相亲)→ 直接去掉文娱短视频
      - 模板污染组(只有兴趣社群+陪伴服务的)→ 去掉文娱短视频，保留已有的兴趣社群/陪伴服务
      - 纯文娱短视频且无其他标签的 → 给文娱
    """
    desc = (e.get('desc_cn') or e.get('description') or '').lower()
    others = [t for t in e.get('tag_l2', []) if t not in ('文娱短视频',)]

    if others:
        # 已有其他标签，只删文娱短视频
        return list(others)

    # 无其他标签的具体判断
    if any(kw in desc for kw in ['k歌', '影集', '图文创作', '短视频制作', '广场舞']):
        return ['短视频']
    if any(kw in desc for kw in ['社交', '社区平台', '社群', '陪伴']):
        return ['兴趣社群']
    if any(kw in desc for kw in ['时尚ip', '旗袍', '直播带货']):
        return ['文娱']
    if any(kw in desc for kw in ['遗产记录', '记忆']):
        return ['文娱']

    return ['文娱']  # 默认归文娱


count = 0
for e in d:
    if '文娱短视频' in e.get('tag_l2', []):
        old = list(e['tag_l2'])
        new = redistribute_文娱短视频(e)
        relabel(e, old, new, f'删除文娱短视频→重分配({"+".join(new)})')
        count += 1
print(f'[4f] 文娱短视频→删除+重分配 ({count}家)')
if '文娱短视频' in l2l1: del l2l1['文娱短视频']
if '文娱短视频' in synonyms: del synonyms['文娱短视频']

# ============================================================
# 5. 认知训练 (30家) 重新走查
# ============================================================
def walk_认知训练(e):
    """走查认知训练企业：确认标签是否合理"""
    desc = (e.get('desc_cn') or e.get('description') or '').lower()
    current = list(e.get('tag_l2', []))

    # 认知训练保留（这是核心业务）
    if '认知训练' not in current:
        current.insert(0, '认知训练')

    # 补充细分：有筛查能力的加认知筛查
    if '认知筛查' not in current:
        screen_kw = ['筛查', '评估', '评估工具', '早期筛查', '诊断', '检测', '眼动追踪',
                      '生物标记']
        if any(kw in desc for kw in screen_kw):
            current.append('认知筛查')

    # 去重保序
    seen, deduped = set(), []
    for t in current:
        if t not in seen:
            deduped.append(t)
            seen.add(t)

    # cap at 3
    return deduped[:3]


count = 0
for e in d:
    if '认知训练' in e.get('tag_l2', []):
        old = list(e['tag_l2'])
        new = walk_认知训练(e)
        reason = '重整' if old != new else '走查通过'
        relabel(e, old, new, f'认知训练走查:{reason}')
        count += 1
print(f'[5] 认知训练走查 ({count}家)')

# ============================================================
# 6. 清理：确保新标签在 l2l1/synonyms 中存在
# ============================================================
# 确保所有实际使用的标签都在 l2l1 中
all_used_l2 = set()
for e in d:
    all_used_l2.update(e.get('tag_l2', []))

for tag in all_used_l2:
    if tag not in l2l1:
        # 自动分配 L1
        auto_map = {
            '体检筛查': '医疗健康', '护理协调': '养老服务', '出行服务': '渠道零售',
            '养老机构': '养老服务', '临终关怀': '医疗健康', '文娱': '文娱社交',
        }
        l1 = auto_map.get(tag, '智能科技')  # default fallback
        l2l1[tag] = [l1]
        print(f"  [自动补录] {tag} → {l1}")

# ============================================================
# 7. 写回文件
# ============================================================
with open(ENTERPRISE_FILE, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
with open(L2L1_FILE, 'w', encoding='utf-8') as f:
    json.dump(l2l1, f, ensure_ascii=False, indent=2)
with open(SYNONYMS_FILE, 'w', encoding='utf-8') as f:
    json.dump(synonyms, f, ensure_ascii=False, indent=2)

# ============================================================
# 8. 输出统计
# ============================================================
c = Counter()
[c.update(set(e.get('tag_l2', []))) for e in d]
zero = [e['name'] for e in d if not e.get('tag_l2')]
over5 = [e['name'] for e in d if len(e.get('tag_l2', [])) > 5]

print(f'\n========== v15 结果 ==========')
print(f'企业总数: {len(d)}')
print(f'二级标签数: {len(c)}')
print(f'零标签企业: {len(zero)} {"⚠️" if zero else "✅"}')
print(f'>5标签企业: {len(over5)} {"⚠️" if over5 else "✅"}')
if over5:
    for n in over5:
        e = next(x for x in d if x['name'] == n)
        print(f'  {n}: {e["tag_l2"]}')

print(f'\n=== Top 20 标签 ===')
for t, n in c.most_common(20):
    print(f'  {t}: {n}')

print(f'\n=== <3 家标签(幽灵) ===')
ghosts = [(t, n) for t, n in c.items() if n < 3]
if ghosts:
    for t, n in ghosts:
        print(f'  ⚠️ {t}: {n}')
else:
    print('  ✅ 无')

print(f'\n=== 变更条目: {len(changelog)} ===')

# 写 changelog
with open('.tmp/v15_changelog.md', 'w', encoding='utf-8') as f:
    f.write('# v15 标签整改 changelog（2026-07-15 晚）\n\n')
    f.write('> 小爽逐条指令执行。不删除任何企业。\n\n')
    f.write('## 变更清单\n\n')
    f.write('| 企业名 | 旧标签 | 新标签 | 原因 |\n|---|---|---|---|\n')
    for line in changelog:
        parts = line.split(' | ')
        f.write(f"| {parts[0]} | {parts[1]} | {parts[2]} | {parts[3]} |\n")

    f.write('\n## 统计汇总\n\n')
    f.write(f'- 总企业: {len(d)}\n')
    f.write(f'- 二级标签: {len(c)}\n')
    f.write(f'- 零标签: {len(zero)}\n')
    f.write(f'- >5标签: {len(over5)}\n')
    if ghosts:
        f.write(f'- 幽灵标签(<3): {len(ghosts)}\n')

print(f'Changelog written: .tmp/v15_changelog.md')
