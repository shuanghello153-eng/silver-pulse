# -*- coding: utf-8 -*-
import json
from collections import Counter

DATA='data/enterprise/all_enterprises.json'
data=json.load(open(DATA,encoding='utf-8'))
tags_map=json.load(open('data/enterprise/_vague_media_tags.json',encoding='utf-8'))

# 二级->一级 (同 _build_tags)
CANON_L1 = {
 '慢病管理':'医疗健康','认知症':'医疗健康','临终关怀':'医疗健康','医疗器械':'医疗健康',
 '远程医疗':'医疗健康','健康监测':'医疗健康','健康管理':'医疗健康','陪诊':'医疗健康','AI医疗':'医疗健康',
 '居家护理':'生活照护','护理平台':'生活照护','专业护理':'生活照护','家政助老':'生活照护','长护险':'生活照护','养老社区':'养老住房',
 '适老化改造':'养老住房',
 '保健品':'食品营养','特医食品':'食品营养','营养食品':'食品营养',
 '鞋服':'消费品','个护':'消费品','眼镜':'消费品','辅具':'消费品','助听器':'消费品','智能硬件':'消费品',
 '老年旅游':'文娱社交','老年教育':'文娱社交','文娱社交':'文娱社交','健身':'文娱社交',
 '保险':'金融保险','养老金融':'金融保险','产业资本':'金融保险',
 'AI科技':'智能科技','机器人':'智能科技','数字化':'智能科技',
 '康复':'康复辅具','康复设备':'康复辅具','养老用品':'康复辅具',
 '行业媒体':'行业服务','咨询研究':'行业服务','照护系统':'行业服务',
 '女性健康':'女性健康','精神健康':'精神健康','渠道':'渠道零售',
}

by_serial={e.get('serial'):e for e in data}
n_ok=0; n_missing=0
for item in tags_map:
    e=by_serial.get(item['serial'])
    if not e:
        n_missing+=1; continue
    new_l2=item.get('tags') or []
    # 仅保留在受控词表内的
    new_l2=[t for t in new_l2 if t in CANON_L1]
    e['tag_l2']=sorted(set(new_l2))
    e['tag_l1']=sorted(set(CANON_L1[x] for x in e['tag_l2']))
    n_ok+=1

json.dump(data,open(DATA,'w',encoding='utf-8'),ensure_ascii=False,indent=1)

zero=sum(1 for e in data if not e.get('tag_l2'))
print(f'merged {n_ok} (missing {n_missing}); now 0-tag={zero}')
