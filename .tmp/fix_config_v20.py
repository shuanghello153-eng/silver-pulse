# -*- coding: utf-8 -*-
import json, re, collections, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT,'data/enterprise/all_enterprises.json')
CONFIG = os.path.join(ROOT,'config.py')

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
ORDER = ['养老服务','康复辅具','消费品','文娱社交','食品营养','行业服务','金融保险','投资机构']
CENT = {'养老服务':10,'康复辅具':10,'消费品':7,'文娱社交':7,'食品营养':7,'行业服务':4,'金融保险':7,'投资机构':4}

d = json.load(open(DATA,encoding='utf-8'))
comps = d if isinstance(d,list) else d['enterprises']
L2_by_L1 = collections.defaultdict(list)
for c in comps:
    for t in c.get('tag_l2',[]):
        L2_by_L1[L2L1[t]].append(t)
for k in L2_by_L1: L2_by_L1[k].sort()

def block(name, body):
    return name + ' = {\n' + body + '}\n'

cats = block('ENTERPRISE_CATEGORIES',
    ''.join(f'  "{l1}": [\n' + ''.join(f'    "{l2}",\n' for l2 in L2_by_L1[l1]) + '  ],\n' for l1 in ORDER if L2_by_L1.get(l1)))
codes = block('ENTERPRISE_CATEGORY_CODES',
    ''.join(f'    "{l1}": "{i:02d}",\n' for i,l1 in enumerate(ORDER,1)))
cent = block('CATEGORY_CENTRALITY',
    ''.join(f'    "{l1}": {CENT[l1]},\n' for l1 in ORDER))

src = open(CONFIG,encoding='utf-8').read()
src = re.sub(r'ENTERPRISE_CATEGORIES\s*=?\s*\{.*?\n\}', cats.rstrip('\n'), src, count=1, flags=re.S)
src = re.sub(r'ENTERPRISE_CATEGORY_CODES\s*=?\s*\{.*?\n\}', codes.rstrip('\n'), src, count=1, flags=re.S)
src = re.sub(r'CATEGORY_CENTRALITY\s*=?\s*\{.*?\n\}', cent.rstrip('\n'), src, count=1, flags=re.S)
open(CONFIG,'w',encoding='utf-8').write(src)
print('config.py 三块已修正 (= 已补回)')
# sanity
import ast
m = ast.parse(src)
print('语法检查通过' if m else 'ERR')
