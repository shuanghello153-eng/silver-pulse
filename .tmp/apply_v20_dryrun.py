# -*- coding: utf-8 -*-
"""Dry-run V20 cleanup. No file write."""
import json, collections
DATA='data/enterprise/all_enterprises.json'
data=json.load(open(DATA,encoding='utf-8'))
comps = data['enterprises'] if isinstance(data,dict) else data

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

zero_after=[]; unknown=set(); kept_h=0; removed_h=0; merged=0; rm_sa=0
for c in comps:
    name=c.get('name',''); l2=list(c.get('tag_l2') or []); new=[]
    for t in l2:
        if t in REMOVE_L2: rm_sa+=1; continue
        if t in MERGE: t=MERGE[t]; merged+=1
        if t=='助听器' and name in REMOVE_HEARING: removed_h+=1; continue
        if t=='助听器' and name not in REMOVE_HEARING: kept_h+=1
        if t not in L2L1: unknown.add(t); continue
        new.append(t)
    new=list(dict.fromkeys(new))
    if not new:
        fb=infer_l2(c); new=[fb]; zero_after.append((name,fb))
    c['_n2']=new; c['_n1']=sorted({L2L1[t] for t in new})
print("REMOVE_SaaS/AI:",rm_sa," MERGE:",merged," 助听器 保留:",kept_h," 移除(P0):",removed_h)
print("0-L2 兜底:",len(zero_after),[z for z in zero_after[:20]])
print("未知L2:",unknown or "无")
l1c=collections.Counter(); l2c=collections.Counter()
for c in comps:
    for x in c['_n1']: l1c[x]+=1
    for x in c['_n2']: l2c[x]+=1
print("\n一级分布:"); [print(f"  {k}: {v}") for k,v in l1c.most_common()]
print("二级种类:",len(l2c))
# correct cross-L1 dup: each L2 should map to exactly 1 L1
bad=[t for t in l2c if L2L1.get(t) is None]
print("映射缺失的L2:",bad or "无")
over3=[c.get('name') for c in comps if len(c['_n2'])>3]
zero=[c.get('name') for c in comps if not c['_n2']]
print(">3标签:",len(over3)," 0标签:",len(zero))
gh={k:v for k,v in l2c.items() if v<3}
print("幽灵(<3):",len(gh),{k:v for k,v in gh.items()})
print("助听器 最终:",l2c.get('助听器')," 陪伴服务:",l2c.get('陪伴服务')," SaaS存在:", 'SaaS' in l2c, " AI存在:", 'AI' in l2c)
