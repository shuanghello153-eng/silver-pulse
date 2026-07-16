# -*- coding: utf-8 -*-
"""V20 真实落库：SSoT 重打标 + 派生一级 + 同步 _l2_l1 / tag_synonyms / config.py 三块。
原子脚本：先备份再写。"""
import json, os, shutil, re, collections, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data/enterprise/all_enterprises.json')
L2L1_FILE = os.path.join(ROOT, 'data/enterprise/_l2_l1.json')
SYN_FILE = os.path.join(ROOT, 'data/enterprise/tag_synonyms.json')
CONFIG = os.path.join(ROOT, 'config.py')
BAK_DIR = os.path.join(ROOT, 'data/enterprise/backups')
os.makedirs(BAK_DIR, exist_ok=True)

stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# ---- 唯一 L2->L1 映射（每个 L2 仅属 1 个一级） ----
L2L1 = {
 '居家护理':'养老服务','陪伴服务':'文娱社交','助听器':'康复辅具','助行器':'康复辅具',
 '养老机构':'养老服务','可穿戴监测':'康复辅具','兴趣社群':'文娱社交','适老化':'养老服务',
 '认知训练':'养老服务','轮椅':'康复辅具','金融理财':'金融保险','药品':'消费品','保健品':'食品营养',
 '健身':'文娱社交','康复器械':'康复辅具','慢病管理':'养老服务','文娱':'文娱社交','智能硬件':'消费品',
 '陪伴机器人':'文娱社交','营养食品':'食品营养','零售':'消费品','保险':'金融保险','诊所':'养老服务',
 '护士上门':'养老服务','睡眠监测':'康复辅具','产业基金':'投资机构','美妆护肤':'消费品','安宁疗护':'养老服务',
 '远程医疗':'养老服务','体检筛查':'消费品','护理协调':'养老服务','远程护理':'养老服务','认知筛查':'养老服务',
 'VC':'投资机构','跌倒监测':'康复辅具','AI医疗':'行业服务','远程监护':'养老服务','更年期':'消费品',
 '旅游':'文娱社交','外骨骼':'康复辅具','康复医疗':'养老服务','居家医疗':'养老服务','护工平台':'养老服务',
 '行业媒体':'行业服务','电商':'消费品','CCRC':'养老服务','护理床':'康复辅具','维生素矿物质':'食品营养',
 '心理健康':'养老服务','教育':'文娱社交','用药提醒':'康复辅具','康养地产':'养老服务','眼镜':'消费品',
 '资讯门户':'行业服务','个人护理':'消费品','服装鞋帽':'消费品','养老咨询':'行业服务','养老信息平台':'行业服务',
 '糖尿病':'食品营养','机器人':'康复辅具','养老REIT':'投资机构','人形机器人':'康复辅具','认知症':'养老服务',
 '保险科技':'金融保险','尿失禁':'消费品','SDOH':'养老服务','专业护理':'养老服务','家政':'养老服务',
 '智能药盒':'康复辅具','膳食配送':'食品营养','紧急呼叫':'康复辅具','助听辅具':'康复辅具','医疗器械':'康复辅具',
 '个性化营养':'食品营养','药品配送':'消费品','陪伴社交':'文娱社交','相亲':'文娱社交','视觉辅助':'消费品',
 'AI':'消费品','垂直电商':'消费品','用药管理':'康复辅具','社区':'文娱社交','居家康复':'养老服务',
 '智能家居':'消费品','功能性食品':'食品营养','养老膳食':'食品营养','膳食补充剂':'食品营养','照护支持':'养老服务',
 '遗产规划':'金融保险','就业':'文娱社交','护士派遣':'养老服务','行业研究':'行业服务','陪诊':'养老服务',
 '纸尿裤':'消费品','短视频':'文娱社交','长护险':'金融保险','心血管':'消费品','中医养生':'养老服务',
 '邻里社交':'文娱社交','呼吸':'康复辅具','护工培训':'养老服务','特医食品':'食品营养','肾病':'养老服务',
 '出行':'养老服务','殡葬':'养老服务','中药滋补':'食品营养','抗衰':'食品营养','养老':'行业服务',
}
MERGE = {
 '助听辅具':'助听器','陪伴社交':'陪伴服务','养老':'养老信息平台',
 '呼吸':'康复器械','特医食品':'营养食品','肾病':'慢病管理','出行':'适老化',
 '中药滋补':'保健品','抗衰':'保健品',
}
REMOVE_L2 = {'SaaS','AI'}
REMOVE_HEARING = {'瑞尔齿科','美呀植牙','鼎植口腔','通策医疗','谊安医疗','维达','豪悦','美丽岛'}

def infer_l2(c):
    txt = ((c.get('description') or '')+(c.get('desc_cn') or '')+(c.get('name') or '')+(c.get('business_model_cn') or '')).lower()
    if any(k in txt for k in ['基金','投资','资本','venture','capital']): return '产业基金'
    if any(k in txt for k in ['媒体','资讯','研究','report','新闻']): return '行业研究'
    if any(k in txt for k in ['保险','insurance']): return '保险'
    if any(k in txt for k in ['软件','系统','平台','saas','tech','工具','数据','data']): return '养老咨询'
    if any(k in txt for k in ['护理','照护','care']): return '居家护理'
    if any(k in txt for k in ['健康','医疗','health','medical','药']): return '慢病管理'
    return '养老咨询'

# ---- 备份 ----
shutil.copy(DATA, os.path.join(BAK_DIR, f'all_enterprises_{stamp}_pre_v20.json'))
print('备份:', os.path.join(BAK_DIR, f'all_enterprises_{stamp}_pre_v20.json'))

# ---- 读取 SSoT（顶层是 list） ----
data = json.load(open(DATA, encoding='utf-8'))
comps = data if isinstance(data, list) else data['enterprises']

fallback_pending = []
for c in comps:
    name = c.get('name','')
    l2 = list(c.get('tag_l2') or [])
    new = []
    for t in l2:
        if t in REMOVE_L2: continue
        if t in MERGE: t = MERGE[t]
        if t == '助听器' and name in REMOVE_HEARING: continue
        if t not in L2L1: continue
        new.append(t)
    new = list(dict.fromkeys(new))
    if not new:
        fb = infer_l2(c)
        new = [fb]
        fallback_pending.append({'name': name, 'fallback_l2': fb, 'reason': '原仅含 SaaS/AI 或信息缺失，关键词兜底，待核实'})
    c['tag_l2'] = new
    c['tag_l1'] = sorted({L2L1[t] for t in new})

# ---- 回写 SSoT ----
with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(comps, f, ensure_ascii=False, indent=1)

# ---- 收集实际出现的 L2 并归组到一级 ----
FINAL_L2 = set()
for c in comps:
    FINAL_L2.update(c['tag_l2'])
L2_by_L1 = collections.defaultdict(list)
for t in FINAL_L2:
    L2_by_L1[L2L1[t]].append(t)
ORDER = ['养老服务','康复辅具','消费品','文娱社交','食品营养','行业服务','金融保险','投资机构']
for k in L2_by_L1: L2_by_L1[k].sort()

# ---- 重写 _l2_l1.json（L2->[唯一一级]） ----
l2l1_new = {t: [L2L1[t]] for t in sorted(FINAL_L2)}
json.dump(l2l1_new, open(L2L1_FILE,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('_l2_l1.json 重写: %d 个二级' % len(l2l1_new))

# ---- 重写 tag_synonyms.json（折叠合并 + 删除 SaaS/AI） ----
syn = json.load(open(SYN_FILE, encoding='utf-8'))
MERGE_TARGET = MERGE  # 9 项
for old, new in MERGE_TARGET.items():
    if old in syn:
        syn.setdefault(new, [])
        syn[new] = list(dict.fromkeys(syn[new] + [old] + syn.pop(old)))
for k in ('SaaS','AI'):
    syn.pop(k, None)
json.dump(syn, open(SYN_FILE,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('tag_synonyms.json 折叠合并完成; 现存二级键:', len(syn))

# ---- 重写 config.py 三块 ----
CENT = {'养老服务':10,'康复辅具':10,'消费品':7,'文娱社交':7,'食品营养':7,'行业服务':4,'金融保险':7,'投资机构':4}
src = open(CONFIG, encoding='utf-8').read()

def block(header, body):
    return header + ' {\n' + body + '}\n'

cats = block('ENTERPRISE_CATEGORIES',
    ''.join(f'  "{l1}": [\n' + ''.join(f'    "{l2}",\n' for l2 in L2_by_L1[l1]) + '  ],\n' for l1 in ORDER if L2_by_L1.get(l1)))
codes = block('ENTERPRISE_CATEGORY_CODES',
    ''.join(f'    "{l1}": "{i:02d}",\n' for i,l1 in enumerate(ORDER,1)))
cent = block('CATEGORY_CENTRALITY',
    ''.join(f'    "{l1}": {CENT[l1]},\n' for l1 in ORDER))

src = re.sub(r'ENTERPRISE_CATEGORIES = \{.*?\n\}', cats.rstrip('\n'), src, count=1, flags=re.S)
src = re.sub(r'ENTERPRISE_CATEGORY_CODES = \{.*?\n\}', codes.rstrip('\n'), src, count=1, flags=re.S)
src = re.sub(r'CATEGORY_CENTRALITY = \{.*?\n\}', cent.rstrip('\n'), src, count=1, flags=re.S)
open(CONFIG,'w',encoding='utf-8').write(src)
print('config.py 三块已重写 (8 一级)')

# ---- 兜底待核实清单落盘 ----
json.dump(fallback_pending, open(os.path.join(ROOT,'data/enterprise/_v20_fallback_pending.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('兜底待核实企业数:', len(fallback_pending))

# ---- 汇总 ----
l1c = collections.Counter(); l2c = collections.Counter()
for c in comps:
    for x in c['tag_l1']: l1c[x]+=1
    for x in c['tag_l2']: l2c[x]+=1
print('\n=== 落库后汇总 ===')
print('企业总数:', len(comps))
print('一级种类:', len(l1c), '二级种类:', len(l2c))
for k,v in l1c.most_common(): print(f'  {k}: {v}')
print('助听器:', l2c.get('助听器'),' 陪伴服务:', l2c.get('陪伴服务'),' SaaS存在:', 'SaaS' in l2c,' AI存在:', 'AI' in l2c)
