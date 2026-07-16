import json, sys

path = r"G:\workbuddy\2026-06-28-23-34-20\silver-pulse\.tmp\results\result_7.json"
with open(path, encoding="utf-8") as f:
    data = json.load(f)

new_entries = [
  {
    "name": "Daughterhood",
    "desc_cn": "Daughterhood 是由 Anne Tumlinson 于 2014 年创立的非营利组织（501c3），为照顾年迈父母等家庭成员的家庭照护者（尤其女性）提供情感与实务支持。通过线上'Circle'互助小组、播客、博客与精选资源帮助照护者缓解孤独、焦虑与倦怠，并于 2025 年参与 CMS 痴呆照护(GUIDE)模型试点合作。",
    "tag_l2": ["社区", "照护支持"],
    "confidence": "high",
    "note": "非科技平台，而是照护者互助社区/非营利组织"
  },
  {
    "name": "DigitalOwl",
    "desc_cn": "DigitalOwl（已并入 Datavant）是面向保险与法律行业的 InsurTech 平台，用专有生成式 AI 与医学知识库将非结构化的病历转化为结构化摘要、时间线与洞察，辅助核保与理赔决策。可识别治疗进展、病情稳定/恶化、用药不符等，处理速度提升最高 72%、准确率 97%+，2026 年入选 Everest Group 寿险科技 Top 50。",
    "tag_l2": ["AI医疗"],
    "confidence": "high",
    "note": ""
  },
  {
    "name": "DiningRD",
    "desc_cn": "DiningRD（1993/1994 年成立，总部圣路易斯）是面向养老与长期照护社区的营养咨询与菜单技术公司，拥有 800+ 注册营养师网络，服务全美 49 州 8,500+ 社区。其 DiningManager 软件（PlateFul 菜单规划、MealCard 居民营养管理、TableSide 数字点餐）帮助社区合规供餐、个性化膳食并提升就餐体验，2023-2024 连续入选 Inc. 5000 高增长榜。",
    "tag_l2": ["养老膳食"],
    "confidence": "high",
    "note": "B2B 养老膳食/营养软件+咨询，非 C 端餐饮配送品牌"
  },
  {
    "name": "Elektra Health",
    "desc_cn": "Elektra Health 是专注更年期女性的虚拟照护平台，提供经绝经学会认证的医生视频问诊、1:1 健康教练、循证教育与私密社群，覆盖潮热、睡眠、情绪等症状管理。已与 Aetna、United、Medicare、Medicaid 等保险网络内合作，2024 年成为首个接受 Medicare/Medicaid 的虚拟更年期照护机构，主打降低雇主与医保计划的照护成本。",
    "tag_l2": ["更年期"],
    "confidence": "high",
    "note": ""
  },
  {
    "name": "Family First",
    "desc_cn": "Family First（原 VillagePlan，波士顿）是面向雇主与保险公司的照护者福利平台，将 AI 与注册护士、社工、医师等跨学科专家团队结合，为平衡工作与照护患病/年迈家人的员工提供个性化照护规划、资源对接与实时支持。2023 年完成 1,100 万美元 A 轮，自称可降低缺勤与离职、带来约 2.8:1 的投资回报。",
    "tag_l2": ["照护支持"],
    "confidence": "high",
    "note": "服务家庭照护者的 B2B 福利平台，非直接上门照护"
  },
  {
    "name": "Foodsmart",
    "desc_cn": "Foodsmart 是美国最大的远程营养(Foodcare)与食品福利管理平台，由 Jason Langheier 于 2010 年创立，通过全美最大注册营养师网络提供视频营养咨询，并整合 FoodsMART 食品商城、SNAP/WIC 申请、个性化餐食规划与杂货/定制餐配送。服务 Medicaid、Medicare Advantage、商业保险及 1,000+ 雇主，覆盖超 220 万会员，2024 年获 TPG Rise Fund 超 2 亿美元投资。",
    "tag_l2": ["营养食品", "膳食配送"],
    "confidence": "high",
    "note": "食品即药物(Food is Medicine)平台，非保健品/补剂品牌"
  },
  {
    "name": "Foundation Partners Group",
    "desc_cn": "Foundation Partners Group（2010 年成立，总部佛州 Winter Park）是美国第二大殡葬服务集团，旗下拥有 250+ 殡仪馆、火化中心与墓园，覆盖 21 个州，年服务超 15 万家庭。以'Altogether'品牌网络整合独立殡葬业主，提供临终前中后的个性化殡葬、缅怀与 succession 规划服务，2025 年完成新一轮机构投资与重组。",
    "tag_l2": ["殡葬"],
    "confidence": "high",
    "note": ""
  },
  {
    "name": "Friendi.fi",
    "desc_cn": "Friendi.fi 成立于 2024 年 9 月，获 1,000 万美元以上融资承诺，由 care.coach 原班团队创办，训练并部署专有对话式 AI'朋友'模型，通过短信等文本渠道与老年人、自闭症青年等群体建立陪伴关系，并巧妙融入由持照专业人员设计的健康教练内容。通过与照护机构及医保(Medicare/Medicaid)支付方合作，以社交关系撬动健康获益。",
    "tag_l2": ["陪伴机器人"],
    "confidence": "high",
    "note": "对话式 AI 陪伴（非实体机器人），词表无'AI陪伴'故取最接近项"
  }
]

existing_names = {e["name"] for e in data}
added = 0
for e in new_entries:
    if e["name"] not in existing_names:
        data.append(e)
        added += 1

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Existing entries: {len(data)-added}, New added: {added}, Total: {len(data)}")
