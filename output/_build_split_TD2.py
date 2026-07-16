# -*- coding: utf-8 -*-
import json

SRC = 'G:/workbuddy/2026-06-28-23-34-20/silver-pulse/output/_v12_bigtags.json'
OUT = 'G:/workbuddy/2026-06-28-23-34-20/silver-pulse/output/_v12_split_TD2.json'

data = json.load(open(SRC, encoding='utf-8'))

# umbrella -> list of member keys (from data)
UMB = ['居家护理', '康复设备', '保健品', '养老社区', '投资机构']

# DECISIONS: key(=name_cn or name) -> [specific L2 tags]
DEC = {
 # ---------- 居家护理 (70) ----------
 '安护通': ['护理平台'], '易得康': ['专业护理'], '福寿康': ['专业护理'],
 '颐家': ['专业护理'], 'OKCS': ['护理平台'], '一家依': ['上门'],
 '三替护理': ['专业护理'], '乐陪护': ['护理平台'], '南京携才': ['专业护理'],
 '天壹智慧': ['智慧养老'], '阳光大姐': ['社交'], '璞缘照护': ['专业护理'],
 '颐家养老': ['护理平台'], '二毛照护': ['专业护理'], '清檬养老': ['护理人力'],
 'Amedisys': ['专业护理'], 'Vesta Healthcare': ['护理平台'], 'CareAcademy': ['护理人力'],
 'Lively': ['护理平台'], 'GE医疗': ['医疗器械'], 'Angels on Call Homecare': ['专业护理'],
 'CareBridge': ['远程护理'], 'CareCentrix': ['专业护理'], 'Clara Home Care': ['护理平台'],
 'Compassus': ['专业护理'], 'Concerto Care': ['专业护理'], 'GeoH': ['护理平台'],
 'Homeage': ['护理平台'], 'HomeCare.com': ['护理平台'], 'InHome Therapy': ['专业护理'],
 'Marta': ['护理平台'], 'Monogram Health': ['专业护理'], 'Sensi.AI': ['护理平台'],
 'Sharecare': ['护理平台'], 'Tomorrow Health': ['护理平台'], 'VitalTech': ['远程护理'],
 'Optum (Home & Community)': ['专业护理'], 'DispatchHealth': ['上门'], 'Medically Home': ['护理平台'],
 'AccentCare': ['专业护理'], 'Right At Home': ['专业护理'], 'InnovAge': ['专业护理'],
 '爱德斯家庭护理': ['专业护理'], 'The Pennant Group': ['专业护理'], 'BelleVie': ['专业护理'],
 'Homage': ['护理平台'], 'Elder': ['护理平台'], 'Emoha': ['专业护理'],
 'Cuideo': ['护理平台'], 'Senniors': ['上门'], 'Herewith': ['护理平台'],
 'CareConnectMD': ['专业护理'], 'AvevoRx': ['上门'], 'Complete Care Management Services': ['专业护理'],
 'Anytime Home Care': ['专业护理'], 'HomeWell Franchising': ['专业护理'], 'Zingage': ['护理平台'],
 'Gladys': ['护理平台'], 'Visiting Angels｜上门照护加盟': ['专业护理'], 'Age Care Labs': ['护理平台'],
 'AlayaCare': ['护理平台'], 'ClearCare': ['护理平台'], 'Medflyt': ['护理平台'],
 'CareJoy': ['护理平台'], 'Hometeam': ['护理平台'], 'Hometouch': ['护理平台'],
 'SuperCarers': ['护理平台'], 'Amada Senior Care': ['专业护理'], 'Cuidum': ['护理平台'],
 '小橙集团': ['智慧养老'],
 # ---------- 康复设备 (57) ----------
 '一康': ['康复设备'], '亿芃健康': ['适老化'], '倍益康': ['康复设备'],
 '凌晴翔': ['适老化'], '博音': ['适老化'], '夕阳红': ['适老化'],
 '奥特顺咽': ['适老化'], '如身机器人': ['康复机器人'], '安泰康成': ['康复设备'],
 '家瑞康': ['适老化'], '富伯医疗': ['康复设备'], '小飞哥': ['适老化'],
 '巨贸康万家': ['适老化'], '康乐龄': ['适老化'], '康力元': ['适老化'],
 '康德宝': ['适老化'], '康政': ['适老化'], '得印科技': ['适老化'],
 '德林': ['适老化'], '怡和嘉业': ['医疗器械'], '恩德莱': ['适老化'],
 '护卫神': ['轮椅'], '振邦': ['适老化'], '斯维驰': ['轮椅'],
 '易乐车业': ['轮椅'], '正奇智能': ['适老化'], '永福康': ['适老化'],
 '添康': ['适老化'], '爱舒乐': ['适老化'], '玖益': ['适老化'],
 '百年红': ['适老化'], '皮皮熊': ['适老化'], '盈康生命': ['康复设备'],
 '祥和': ['适老化'], '福仕得': ['适老化'], '福佑': ['适老化'],
 '维达': ['适老化'], '美瑞德': ['适老化'], '联谛信息': ['适老化'],
 '臻行科技': ['适老化'], '舒莱适': ['适老化'], '若创科技': ['适老化'],
 '英洛华': ['轮椅'], '豪悦': ['适老化'], '足步医疗': ['助行器'],
 '迈德斯特': ['适老化'], '钰民': ['适老化'], '德林假肢': ['假肢矫形'],
 '一康医疗': ['康复设备'], '小咖云': ['行业媒体'], 'Cala Health': ['医疗器械'],
 'reev.care': ['康复设备'], '萨瓦瑞亚': ['适老化改造'], 'Accelera': ['康复设备'],
 '卓道医疗': ['康复机器人'], '蓓明医疗': ['康复设备'], '纽聆氪医疗': ['医疗器械'],
 # ---------- 保健品 (54) ----------
 'VTN': ['渠道零售'], '乐力': ['保健品'], '享佳健康': ['渠道零售'],
 '今旭面业': ['营养食品'], '仙乐健康': ['保健品'], '优生活': ['营养食品'],
 '元气家族': ['保健品'], '卓牧': ['营养食品'], '国科优选': ['保健品'],
 '天合人康': ['保健品'], '天天好': ['保健品'], '太爱肽': ['保健品'],
 '好孝心': ['保健品'], '孝当先': ['保健品'], '孝心坊': ['保健品'],
 '寿仙谷': ['保健品'], '康林仁和': ['渠道零售'], '康比特': ['保健品'],
 '慢糖家': ['营养食品'], '方家铺子': ['保健品'], '时光派': ['保健品'],
 '月神': ['保健品'], '森美': ['保健品'], '楼上': ['保健品'],
 '每日的菌': ['保健品'], '江南米道': ['营养食品'], '泰一健康': ['保健品'],
 '玛士撒拉': ['营养食品'], '瑞光康泰': ['保健品'], '瑞邦': ['保健品'],
 '百合康': ['保健品'], '百合生物': ['保健品'], '益生康健': ['渠道零售'],
 '盛美诺': ['保健品'], '知识矩阵': ['行业媒体'], '神探伍伍': ['保健品'],
 '福东海': ['保健品'], '粤嘉康': ['渠道零售'], '糖友饱饱': ['营养食品'],
 '纽崔莱': ['保健品'], '绿瘦': ['保健品'], '老来寿': ['保健品'],
 '肌肉科技': ['保健品'], '臻牧': ['营养食品'], '艾兰得': ['保健品'],
 '苏立康': ['保健品'], '莎浓羊奶': ['营养食品'], '蒙佩尔兰': ['保健品'],
 '蓝力': ['保健品'], '远方好物': ['渠道零售'], '阿尔发': ['营养食品'],
 '鲲鱼健康': ['保健品'], '麦孚': ['营养食品'], 'HealthKart': ['渠道零售'],
 # ---------- 养老社区 (53) ----------
 '乐湾': ['康养地产'], '一家依': ['上门'], '乐成养老': ['养老社区'],
 '九如城': ['养老机构'], '光大养老': ['养老机构'], '初新养老': ['养老机构'],
 '华润维麟': ['养老机构'], '哺恩': ['养老机构'], '嘉堡护理': ['养老机构'],
 '复星保德信': ['养老社区'], '太平养老': ['养老社区'], '安养养老': ['养老机构'],
 '安养帮': ['养老机构'], '平安臻颐年': ['养老社区'], '悦心安颐': ['养老机构'],
 '招商观颐': ['养老社区'], '春树养老': ['养老机构'], '昱言养老': ['咨询研究'],
 '智杰教育': ['养老机构'], '水印中国': ['养老机构'], '泰康之家': ['养老社区'],
 '绿城康养': ['康养地产'], '绿康': ['养老机构'], '远洋椿萱茂': ['养老社区'],
 '迪马常青社': ['养老机构'], '锦欣福星': ['养老机构'], '颐佳康': ['养老机构'],
 '太平梧桐人家': ['养老社区'], '安养养老（安养帮）': ['行业媒体'], '绿康医养': ['养老机构'],
 '哺恩养老': ['养老机构'], 'Habitat Health': ['护理平台'], 'Silvernest': ['社交'],
 'Nesterly': ['社交'], 'Seniorly': ['咨询研究'], 'UpsideHōM': ['养老社区'],
 '村庄网络': ['社交'], 'The Villages': ['养老社区'], '美国退休人员协会': ['行业媒体'],
 'Better Coliving': ['社交'], 'Bridge Group': ['养老机构'], 'Dwellr': ['咨询研究'],
 'LifeLoop': ['智慧养老'], 'SeniorCare.com': ['咨询研究'], 'Upsidehom': ['康养地产'],
 '茑屋书店': ['社交'], 'Ashiana Housing': ['康养地产'], 'Sodalis Senior Living': ['养老机构'],
 'Sonida Senior Living': ['养老社区'], 'Front Porch｜CCRC': ['养老社区'], '兴业控股': ['养老机构'],
 'Portever': ['养老社区'], 'Qida': ['养老机构'],
 # ---------- 投资机构 (46) ----------
 'BAI资本': ['投资机构'], '千骥资本': ['投资机构'], '国寿大健康': ['投资机构'],
 '普健济康': ['投资机构'], '栈道资本': ['投资机构'], '达晨财智': ['投资机构'],
 '达风投资': ['投资机构'], '金鼎资本': ['投资机构'], '铱创投资': ['投资机构'],
 '银创资本': ['投资机构'], '长岭资本': ['投资机构'], '高樟资本': ['投资机构'],
 'AARP Innovation Labs / AgeTech Collaborative': ['行业媒体'], 'Apax Partners': ['投资机构'],
 'Greycroft Partners': ['投资机构'], 'Humana / Aetna / UnitedHealth / Cigna': ['保险'],
 'Primetime Partners': ['投资机构'], 'Techstars Future of Longevity Accelerator': ['投资机构'],
 'a16z': ['投资机构'], 'Battery Ventures': ['投资机构'], 'Blue Venture Fund': ['投资机构'],
 'Canaan': ['投资机构'], 'Comcast Ventures': ['投资机构'], 'Magnify Ventures': ['投资机构'],
 '软银愿景基金': ['投资机构'], 'Tiger Global': ['投资机构'], 'Emerson Collective': ['投资机构'],
 'Generator Ventures': ['投资机构'], 'Kaiser Permanente Ventures': ['投资机构'],
 'Oak HC/FT': ['投资机构'], 'Rethink Impact': ['投资机构'], 'Ziegler长寿基金': ['投资机构'],
 'Imperative Care': ['医疗器械'], 'Thrive AI Health': ['AI'], 'Wesper': ['医疗器械'],
 'Aveanna Healthcare': ['临终关怀'], 'Enhabit': ['临终关怀'], 'Ready Responders': ['专业护理'],
 'Google Gemini AI 健康教练': ['AI'], 'Welltower｜医疗地产信托': ['康养地产'],
 'CareTrust REIT': ['康养地产'], '国家医疗投资者': ['康养地产'], '医疗地产信托': ['康养地产'],
 '医疗地产信托(MPT)': ['康养地产'], '多元医疗信托': ['康养地产'], 'WHILL': ['轮椅'],
}

# validate coverage
missing = []
for t in UMB:
    for m in data[t]:
        key = m.get('name_cn') if m.get('name_cn') else m.get('name')
        if key not in DEC:
            missing.append((t, key))
if missing:
    print('MISSING DECISIONS:', missing)
    raise SystemExit(1)

REASSIGN = {}
per_source = {t: 0 for t in UMB}
for t in UMB:
    for m in data[t]:
        key = m.get('name_cn') if m.get('name_cn') else m.get('name')
        tags = DEC[key]
        # only include if actually moved off the umbrella
        if not (len(tags) == 1 and tags[0] == t):
            REASSIGN[key] = tags
            per_source[t] += 1

NEW_TAGS = {}  # no new tags needed; all fit existing L2 tags

out = {'REASSIGN': REASSIGN, 'NEW_TAGS': NEW_TAGS}
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print('OK written', OUT)
print('REASSIGN unique keys:', len(REASSIGN))
print('per-source reassigned:', per_source)
print('new tags:', len(NEW_TAGS))

# quick distribution of target tags
from collections import Counter
cnt = Counter()
for v in REASSIGN.values():
    for tg in v:
        cnt[tg] += 1
print('target tag distribution:', dict(cnt))
