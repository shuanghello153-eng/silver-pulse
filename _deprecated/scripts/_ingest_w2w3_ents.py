# -*- coding: utf-8 -*-
"""W2/W3 头部企业入库（7家去重后新企业）。
分类用现有词表（不新增分类）；tag_l1/tag_l2 留空待标签AI填；新增 ingest_time 元数据。
"""
import json, copy
EP = "data/enterprise/all_enterprises.json"
ents = json.load(open(EP, encoding="utf-8"))
template = ents[0]
existing = {e.get("name", "").strip().lower() for e in ents}
maxserial = max(int(str(e.get("serial", "#0")).replace("#", "")) for e in ents if str(e.get("serial", "")).startswith("#"))

NEW = [
 {"name":"红松 Hongsong","region":"国内","category_l1":"文娱社交","category_l2":"兴趣社群",
  "description":"国内退休人群文娱直播课社区头部，提供兴趣课程+社交直播，模式反常识标杆；已完成A+轮。",
  "funding_latest":{"date":"未披露","amount":"数千万人民币","round":"A+轮","display":"A+轮 数千万人民币 (贝塔斯曼亚洲/创世伙伴/蓝驰)"},
  "funding_total":{"amount":"未披露","display":"累计未披露"},"investors":"贝塔斯曼亚洲/创世伙伴/蓝驰",
  "founded":"未披露","website_url":"https://hongsong.tuixiu.com","stage":"成长期","source":"信源治理入库(W2文娱) 2026-07-16",
  "business_model":"B2C社区","business_model_cn":"B2C银发文娱社区","tags":["银发文娱","有融资"]},
 {"name":"携程老友会","region":"国内","category_l1":"文娱社交","category_l2":"旅游",
  "description":"国内银发旅游头部品牌（携程旗下），“老有意思旅行团”六大主题游；450万+会员、7000+线路，携程增长最快业务模块之一。",
  "funding_latest":{"date":"未披露","amount":"未披露(携程旗下)","round":"未披露","display":"未披露(携程旗下)"},
  "funding_total":{"amount":"未披露","display":"未披露"},"investors":"携程","founded":"未披露",
  "website_url":"https://www.ctrip.com","stage":"成长期","source":"信源治理入库(W2文娱) 2026-07-16",
  "business_model":"B2C平台","business_model_cn":"B2C银发旅游","tags":["银发旅游"]},
 {"name":"Silversurfers","region":"海外","category_l1":"文娱社交","category_l2":"社区",
  "description":"英国最大50+在线社区，30万+注册、社媒100万+关注，UGC活力老人内容（论坛/展示/交友）。",
  "funding_latest":{"date":"未披露","amount":"未披露","round":"未披露","display":"未披露"},
  "funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露",
  "website_url":"https://www.silversurfers.com","stage":"成熟","source":"信源治理入库(W2文娱) 2026-07-16",
  "business_model":"UGC社区","business_model_cn":"UGC活力老人社区","tags":["社区"]},
 {"name":"Intuition Robotics","region":"海外","category_l1":"文娱社交","category_l2":"陪伴机器人",
  "description":"陪伴AI机器人ElliQ制造商，面向独居老人情感陪伴与日常提醒；纽约州老龄办B2G免费发放。",
  "funding_latest":{"date":"2026","amount":"新轮$25M","round":"近期","display":"新轮$25M (Woven/Toyota领投);累计约$83-88M"},
  "funding_total":{"amount":"约$83-88M","display":"累计约$83-88M"},"investors":"Woven Capital/Toyota等",
  "founded":"2015","website_url":"https://www.intuitionrobotics.com","stage":"成长期","source":"信源治理入库(W3 AIGC) 2026-07-16",
  "business_model":"B2C硬件","business_model_cn":"B2C陪伴机器人","tags":["陪伴AI","有融资"]},
 {"name":"Tombot","region":"海外","category_l1":"文娱社交","category_l2":"陪伴机器人",
  "description":"认知症陪伴机器狗Jennie制造商，提供拟人化情感陪伴；23,000+预定。",
  "funding_latest":{"date":"2026-06-22","amount":"$7M","round":"Series A3","display":"Series A3 $7M"},
  "funding_total":{"amount":"约$7M+","display":"累计约$7M+"},"investors":"Caduceus Capital Partners等",
  "founded":"未披露","website_url":"https://www.tombot.com","stage":"A轮","source":"信源治理入库(W3 AIGC) 2026-07-16",
  "business_model":"B2C硬件","business_model_cn":"B2C陪伴机器狗","tags":["陪伴机器人","有融资"]},
 {"name":"Hippocratic AI","region":"海外","category_l1":"行业服务","category_l2":"AI医疗",
  "description":"医疗垂直大模型/患者Agent，非诊断用途，面向就医导航与健康问答；50+医疗系统部署。",
  "funding_latest":{"date":"2026","amount":"$404M(累计)","round":"多轮","display":"累计$404M,估值$3.5B"},
  "funding_total":{"amount":"$404M","display":"累计$404M"},"investors":"未披露","founded":"未披露",
  "website_url":"https://www.hippocratic.ai","stage":"成长期","source":"信源治理入库(W3 AIGC) 2026-07-16",
  "business_model":"B2B SaaS","business_model_cn":"B2B医疗大模型","tags":["AI医疗","有融资"]},
 {"name":"Whispp","region":"海外","category_l1":"行业服务","category_l2":"AI医疗",
  "description":"语音重建AI，助言语障碍老人恢复自然声音；2026-07-07获LUMO Labs领投融资。",
  "funding_latest":{"date":"2026-07-07","amount":"$5.7M","round":"早期","display":"$5.7M (LUMO Labs领投)"},
  "funding_total":{"amount":"约$5.7M","display":"累计约$5.7M"},"investors":"LUMO Labs等","founded":"未披露",
  "website_url":"https://www.whispp.com","stage":"早期","source":"信源治理入库(W3 AIGC) 2026-07-16",
  "business_model":"B2C/B2B App","business_model_cn":"B2C语音重建AI","tags":["AI医疗","有融资"]},
]

added=0; skipped=0
for e in NEW:
    nm=e["name"].strip().lower()
    if nm in existing:
        skipped+=1; continue
    maxserial+=1
    ne=copy.deepcopy(template)
    ne["serial"]=f"#{maxserial:04d}"
    for k,v in e.items(): ne[k]=v
    ne["tag_l1"]=[]
    ne["tag_l2"]=[]
    ne["news_coverage"]={"news_count":0,"news_quality":"unscored","latest_news":None}
    ne["value_score"]=0
    ne["recommend"]=""
    ne["name_cn"]=""
    ne["highlights"]=(f"成立于{e['founded']}年" if e.get("founded") and e["founded"]!="未披露" else "")
    ne["payor_model"]="未披露"
    ne["desc_cn"]=e["description"]
    ne["ingest_time"]="2026-07-16"
    ents.append(ne); existing.add(nm); added+=1

json.dump(ents,open(EP,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(f"W2/W3 企业入库：新增 {added} 家，跳过已存在 {skipped} 家；现有总数 {len(ents)}")
