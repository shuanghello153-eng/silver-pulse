# -*- coding: utf-8 -*-
"""V20 第二批修正：基于 A/B/C 三份只读走查报告，对点名的错标企业做修正。
原则：
- 新建 L2「养老软件」(行业服务) 承接 B2B 养老 SaaS/运营系统（A/B/C 三方一致认为缺此标签）。
- 把"养老咨询/养老机构/居家护理/陪伴服务"里被错打的 SaaS/平台/技术/跨赛道企业，迁到正确标签。
- 移除康复辅具模板污染（牙科/呼吸机/纸品）。
- 仅改被点名的企业；未点名企业不动。
均来自三份报告的显式点名，非盲分类器。
"""
import json, os, re, collections, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data/enterprise/all_enterprises.json')
L2L1_FILE = os.path.join(ROOT, 'data/enterprise/_l2_l1.json')
SYN_FILE = os.path.join(ROOT, 'data/enterprise/tag_synonyms.json')
CONFIG = os.path.join(ROOT, 'config.py')
BAK_DIR = os.path.join(ROOT, 'data/enterprise/backups')
os.makedirs(BAK_DIR, exist_ok=True)

# ---- 读取现行映射（含 V20 的 98 L2）并加「养老软件」 ----
l2l1 = json.load(open(L2L1_FILE, encoding='utf-8'))
L2L1 = {k: (v[0] if isinstance(v, list) else v) for k, v in l2l1.items()}
L2L1['养老软件'] = '行业服务'
ALL_L2 = set(L2L1.keys())

stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy(DATA, os.path.join(BAK_DIR, f'all_enterprises_{stamp}_pre_v20b.json'))
print('备份:', os.path.join(BAK_DIR, f'all_enterprises_{stamp}_pre_v20b.json'))

# ---- 修正集：match_key -> 新 tag_l2 列表（仅含合法 L2） ----
CORR = {
 # === C 报告显式（养老软件 / AI医疗 / 保险 / 其它）===
 'Habitat Health': ['养老软件'],
 'Hello Sage': ['养老软件'],
 'American HealthTech': ['养老软件'],
 'GeoH': ['养老软件'],
 'ExaCare AI': ['养老软件'],
 'Nila': ['养老软件'],
 'Aline': ['养老软件'],          # Aline (Sherpa)
 'Smartcare': ['养老软件'],
 'Mon Ami': ['养老软件'],
 'Eldermark': ['养老软件'],
 'CareFlick': ['养老软件'],
 'WellSky': ['养老软件'],
 'Jubo': ['养老软件'],
 'PointClickCare': ['养老软件'],
 '沐之爱': ['养老软件'],
 'Sage Inc.': ['养老软件'],
 'MatrixCare': ['养老软件'],
 'Cubigo': ['养老软件'],
 'ECP': ['养老软件'],
 'CareMerge': ['养老软件'],
 'CareVision': ['养老软件'],
 'Person Centred Software': ['养老软件'],
 'August Health': ['养老软件'],
 '医家通': ['养老软件'],
 '爱普雷德': ['养老软件'],
 'Voize': ['养老软件'],
 '百善九号': ['养老软件'],
 'Altek Corporation': ['养老软件'],
 'Kinesense': ['养老软件'],
 '杭州微脉': ['养老软件'],
 'Infinitus Systems': ['AI医疗'],
 'SpinSci': ['AI医疗'],
 'Abridge': ['AI医疗'],
 'Transcarent': ['保险'],
 'Rylo': ['助听器'],
 '锣钹科技': ['兴趣社群'],
 'BrightSpring Health': ['居家护理'],
 'Saber Healthcare': ['养老机构'],
 # === A 报告：居家护理 错标迁出 ===
 '安养帮': ['养老机构'],
 '唯艾': ['个人护理'],
 '甲子科技': ['助行器', '适老化'],
 'AdaptHealth': ['助行器', '医疗器械'],
 'Homeage': ['护工平台'],
 'Clara Home Care': ['行业服务'],
 'Angels on Call Homecare': ['行业服务'],
 'Caring.com': ['养老信息平台'],
 'Helper bees': ['护工平台'],
 'The Helper Bees': ['护工平台'],
 'HomeCare.com': ['护工平台'],
 'NurseBuddy': ['养老软件'],
 'eCaring': ['养老软件'],
 'AlayaCare': ['养老软件'],
 'ClearCare': ['养老软件'],
 'Medflyt': ['养老软件'],
 'CareJoy': ['养老软件'],
 'Zingage': ['养老软件'],
 'Gladys': ['养老软件'],
 'Log my Care': ['养老软件'],
 'CareCentrix': ['养老软件'],
 'Careforth': ['养老软件'],
 'Family First': ['行业服务'],
 'Grayce': ['行业服务'],
 'HealthArc': ['行业服务'],
 'HealthSnap': ['养老软件'],
 'Vytalize Health': ['养老软件'],
 'Koda Health': ['养老软件'],
 'Concerto Care': ['养老软件'],
 'Compassus': ['安宁疗护'],
 'Lively': ['中医养生'],
 # === A 报告：陪伴服务 / 兴趣社群 跨赛道 ===
 'Adonis': ['行业服务'],
 'Ellipsis Health': ['行业服务'],   # 非老年，暂留行业服务待你确认是否移出库
 'CareBridge': ['远程医疗'],
 'Sollis Health': ['远程医疗'],
 'Cityblock Health': ['远程医疗'],
 'Cohere Health': ['AI医疗'],
 'DigitalOwl': ['AI医疗'],
 'Friendi.fi': ['AI医疗'],
 'In-House Health': ['远程护理'],
 'Kinto': ['远程护理'],
 'Auxa Health': ['远程护理'],
 'Daughterhood': ['行业服务'],
 'RapidClaims': ['AI医疗'],
 'Thoughtful AI': ['AI医疗'],
 'Voiceitt': ['康复辅具'],
 'Hyfe AI': ['慢病管理'],
 'Nourish Care': ['养老软件'],
 # === A 报告：助听器/助行器 模板污染（牙科/呼吸机/纸品）===
 '瑞尔齿科': ['诊所'],
 '美呀植牙': ['诊所'],
 '鼎植口腔': ['诊所'],
 '通策医疗': ['诊所'],
 '谊安医疗': ['医疗器械'],
 '怡和嘉业': ['医疗器械'],
 '维达': ['消费品'],
 # === A 报告：养老机构 错标迁出 ===
 '麦麦养老': ['适老化'],
 '一康': ['康复器械'],
 '东方华康': ['康复医疗'],
 '盈康生命': ['康复医疗'],
 '101 Mobility': ['适老化'],
 'Kins': ['康复医疗'],
 'Sage': ['养老软件'],
 'MonSenior': ['行业服务'],
 'Agely Care': ['居家护理'],
 # === A 报告：可穿戴监测 非穿戴雷达/紧急呼叫 ===
 'Caspar.AI': ['智能家居'],
 'Ome': ['智能家居'],
 'Philips': ['紧急呼叫'],         # Philips (Lifeline)
 '清澜技术': ['跌倒监测', '睡眠监测'],
 '清雷': ['跌倒监测'],
 '百芝龙': ['跌倒监测'],
 '苗米': ['跌倒监测', '睡眠监测'],
 'Cherish': ['跌倒监测'],
 'Lifted': ['跌倒监测'],
 '星纵物联': ['跌倒监测'],
 # === A 报告：适老化 出行错标 ===
 'GoGoGrandparent': ['出行'],
 'Lyft Health': ['出行'],
 'Uber Health': ['出行'],
 'Modivcare': ['出行'],
 # === A 报告：养老咨询（仅迁被点名且非真咨询者；真咨询维持）===
 'Advosense': ['尿失禁'],          # 信息不足，先归最可能
 'AssistMe': ['尿失禁'],
 'Axle Health': ['行业服务'],
 'Apree': ['行业服务'],
 'flyte': ['尿失禁'],
 'Arbital Health': ['行业研究'],   # 维持
 'Bridge Group': ['行业服务'],
 'K4Connect': ['适老化'],
 'SpinSci': ['AI医疗'],
 'ExaCare AI': ['养老软件'],
 'Nila': ['养老软件'],
 'Aline': ['养老软件'],
 'Smartcare': ['养老软件'],
 'Mon Ami': ['养老软件'],
 'Eldermark': ['养老软件'],
 'Rylo': ['助听器'],
 'CareFlick': ['养老软件'],
 '杭州微脉': ['养老软件'],
 '智医慧云': ['养老咨询'],         # 维持（数字营销服务）
 'WellSky': ['养老软件'],
 'Jubo': ['养老软件'],
 'PointClickCare': ['养老软件'],
 '沐之爱': ['养老软件'],
 'MatrixCare': ['养老软件'],
 'Abridge': ['AI医疗'],
 'Hello Sage': ['养老软件'],
 'Season Health': ['膳食配送'],
 'Habitat Health': ['养老软件'],
 'American HealthTech': ['养老软件'],
 'GeoH': ['养老软件'],
 'Infinitus Systems': ['AI医疗'],
 'Sage Inc.': ['养老软件'],
 'Transcarent': ['保险'],
 '锣钹科技': ['兴趣社群'],
 'BrightSpring Health': ['居家护理'],
 'Saber Healthcare': ['养老机构'],
 'Caring.com': ['养老信息平台'],
 'Compassus': ['安宁疗护'],
}

# 规范化：把误用的 一级名/已合并二级 修正为合法二级
CORR = {k: ['养老信息平台' if t == '行业服务' else '个人护理' if t == '消费品' else '适老化' if t == '出行' else t for t in v] for k, v in CORR.items()}

# 归一化匹配
def norm(s): return re.sub(r'[^a-z0-9一-鿿]', '', (s or '').lower())
data = json.load(open(DATA, encoding='utf-8'))
comps = data if isinstance(data, list) else data['enterprises']
by_norm = {}
for i, c in enumerate(comps):
    by_norm.setdefault(norm(c.get('name','')), []).append(i)

applied = 0; unmatched = []
for key, new_l2 in CORR.items():
    nk = norm(key)
    # 精确归一 或 包含匹配
    idxs = by_norm.get(nk)
    if not idxs:
        # 尝试包含
        cand = [i for i,c in enumerate(comps) if nk and nk in norm(c.get('name',''))]
        idxs = cand[:1] if cand else None
    if not idxs:
        unmatched.append(key); continue
    i = idxs[0]
    valid = [t for t in new_l2 if t in ALL_L2]
    comps[i]['tag_l2'] = list(dict.fromkeys(valid))
    comps[i]['tag_l1'] = sorted({L2L1[t] for t in valid})
    applied += 1

print('应用修正:', applied, ' 未匹配:', len(unmatched), unmatched)

# ---- 回写 SSoT ----
with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(comps, f, ensure_ascii=False, indent=1)

# ---- 重写 _l2_l1.json（含 养老软件） ----
FINAL_L2 = set()
for c in comps: FINAL_L2.update(c.get('tag_l2', []))
l2l1_new = {t: [L2L1[t]] for t in sorted(FINAL_L2)}
json.dump(l2l1_new, open(L2L1_FILE,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('_l2_l1.json 重写: %d 个二级' % len(l2l1_new))

# ---- tag_synonyms 增加 养老软件 ----
syn = json.load(open(SYN_FILE, encoding='utf-8'))
if '养老软件' not in syn:
    syn['养老软件'] = ['养老SaaS', '养老系统', '养老软件', '照护SaaS', '养老信息化', '养老运营系统', 'senior care software', 'care management software']
json.dump(syn, open(SYN_FILE,'w',encoding='utf-8'), ensure_ascii=False, indent=2)

# ---- config.py：行业服务 列表增加 养老软件（作为独立二级，非养老咨询子项） ----
src = open(CONFIG, encoding='utf-8').read()
if '"养老软件"' not in src:
    # 行业服务 紧跟 金融保险（ORDER 顺序保证），在其列表末尾(AI医疗)后插入
    src = src.replace('    "AI医疗"\n  ],\n  "金融保险": [',
                     '    "AI医疗",\n    "养老软件"\n  ],\n  "金融保险": [', 1)
    open(CONFIG,'w',encoding='utf-8').write(src)
    print('config.py 行业服务 增加 养老软件')
else:
    print('config.py 已含 养老软件（跳过）')

# ---- 汇总 ----
l1c = collections.Counter(); l2c = collections.Counter()
for c in comps:
    for x in c.get('tag_l1',[]): l1c[x]+=1
    for x in c.get('tag_l2',[]): l2c[x]+=1
print('企业总数:', len(comps), ' 一级:', len(l1c), ' 二级:', len(l2c))
for k,v in l1c.most_common(): print(f'  {k}: {v}')
print('养老软件:', l2c.get('养老软件'), ' 养老咨询:', l2c.get('养老咨询'), ' 居家护理:', l2c.get('居家护理'), ' 养老机构:', l2c.get('养老机构'), ' 陪伴服务:', l2c.get('陪伴服务'))
