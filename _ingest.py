# -*- coding: utf-8 -*-
"""2026-07-15 信源治理入库：企业36家 + 资讯32条 写入数据库；恢复3个误判死源。
字段以现有企业库模板复制，保证结构兼容；只填可获取的事实字段，标签留给标签AI。
"""
import json, copy

# ========== 1) 恢复 3 个误判死源（清 source_health 死标）==========
HP = "data/source_health.json"
h = json.load(open(HP, encoding="utf-8"))
for k in ["agetech_com", "vcbeat_aging", "third_act"]:
    if k in h:
        h[k]["status"] = "active"
        h[k]["action"] = "monitor"
        h[k]["consecutive_zero"] = 0
        h[k]["last_ok_run"] = "2026-07-15"
        h[k]["last_raw"] = 1
        h[k]["last_new"] = 1
        h[k]["notes"] = "2026-07-15 研究员实查：站点活着，原suspected_dead为采集失败误判，已恢复"
json.dump(h, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("死源恢复：agetech_com / vcbeat_aging / third_act -> active")

# ========== 2) 企业入库 ==========
EP = "data/enterprise/all_enterprises.json"
ents = json.load(open(EP, encoding="utf-8"))
template = ents[0]
existing = {e.get("name", "").strip().lower() for e in ents}
maxserial = max(int(str(e.get("serial", "#0")).replace("#", "")) for e in ents if str(e.get("serial", "")).startswith("#"))

# 每个企业：name, region, category_l1, category_l2, description, funding_latest{date,amount,round,display},
# funding_total{amount,display}, investors, founded, website_url, stage, source, business_model, business_model_cn, tags
NEW_ENTS = [
 # ---- 第一梯队：高融资/知名头部 ----
 {"name":"Pearl Health","region":"海外","category_l1":"医疗健康","category_l2":"医疗服务","description":"基于价值的医疗（value-based care）平台，聚焦 Medicare 初级保健与风险协调。","funding_latest":{"date":"2026-07-08","amount":"1.1亿美元","round":"Series C","display":"Series C $110M (a16z领投)"},"funding_total":{"amount":"约$2亿+","display":"累计约$2亿+"},"investors":"a16z等","founded":"2019","website_url":"https://www.pearlhealth.com","stage":"成长期","source":"信源治理入库(动脉网/Seedtable) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 医疗平台","tags":["有融资","高融资"]},
 {"name":"Empathy","region":"海外","category_l1":"金融服务","category_l2":"遗产规划","description":"丧亲/身后事支持与遗产管理数字平台，帮助用户处理遗嘱、继承与情感支持。","funding_latest":{"date":"2026","amount":"1.62亿美元","round":"Series C","display":"Series C $162M"},"funding_total":{"amount":"约$2亿","display":"累计约$2亿"},"investors":"未披露","founded":"2018","website_url":"https://www.empathy.com","stage":"成长期","source":"信源治理入库(Tracxn) 2026-07-15","business_model":"B2C/B2B","business_model_cn":"B2C 遗产服务平台","tags":["有融资","高融资"]},
 {"name":"Trust & Will","region":"海外","category_l1":"金融服务","category_l2":"遗产规划","description":"在线遗嘱与遗产规划平台，面向适老/退休人群的 estate planning。","funding_latest":{"date":"2026","amount":"7500万美元","round":"Series C","display":"Series C $75M"},"funding_total":{"amount":"约$1亿","display":"累计约$1亿"},"investors":"未披露","founded":"2017","website_url":"https://trustandwill.com","stage":"成长期","source":"信源治理入库(Tracxn) 2026-07-15","business_model":"B2C","business_model_cn":"B2C 遗嘱平台","tags":["有融资"]},
 {"name":"AltoIRA","region":"海外","category_l1":"金融服务","category_l2":"养老金融","description":"自建 IRA 个人退休账户平台，支持含另类资产的退休储蓄。","funding_latest":{"date":"2026","amount":"7310万美元","round":"Series B","display":"Series B $73.1M"},"funding_total":{"amount":"约$1亿","display":"累计约$1亿"},"investors":"未披露","founded":"2018","website_url":"https://www.altoira.com","stage":"成长期","source":"信源治理入库(Tracxn) 2026-07-15","business_model":"B2C","business_model_cn":"B2C 退休账户平台","tags":["有融资"]},
 {"name":"Vestwell","region":"海外","category_l1":"金融服务","category_l2":"养老金融","description":"退休储蓄/401(k) 平台，企业级养老金融基础设施。","funding_latest":{"date":"2026","amount":"未披露(付费墙遮挡)","round":"Series E","display":"Series E (Seedtable评分87)"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"2016","website_url":"https://www.vestwell.com","stage":"成长期","source":"信源治理入库(Seedtable) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 养老金融平台","tags":["有融资"]},
 {"name":"Papa","region":"海外","category_l1":"养老服务","category_l2":"居家护理","description":"面向老年家庭的同伴照护/就医陪同社会支持平台，连接老年人与兼职陪伴者。","funding_latest":{"date":"2026","amount":"未披露(付费墙遮挡)","round":"未公开","display":"金额未披露"},"funding_total":{"amount":"约$2.4亿","display":"累计约$2.4亿"},"investors":"未披露","founded":"2017","website_url":"https://www.papa.com","stage":"成长期","source":"信源治理入库(Tracxn) 2026-07-15","business_model":"B2C2B","business_model_cn":"B2C2B 陪伴照护平台","tags":["有融资"]},
 {"name":"Honor","region":"海外","category_l1":"养老服务","category_l2":"居家护理","description":"居家照护运营平台与护理员网络，赋能家政机构数字化。","funding_latest":{"date":"2026","amount":"未披露(付费墙遮挡)","round":"未公开","display":"金额未披露"},"funding_total":{"amount":"约$1.5亿","display":"累计约$1.5亿"},"investors":"未披露","founded":"2014","website_url":"https://www.honor.com","stage":"成长期","source":"信源治理入库(Tracxn) 2026-07-15","business_model":"B2B平台","business_model_cn":"B2B 居家照护平台","tags":["有融资"]},
 {"name":"SafelyYou","region":"海外","category_l1":"智能科技","category_l2":"跌倒监测","description":"AI 视频跌倒检测，专注养老/照护机构防跌与事故预防。","funding_latest":{"date":"2026","amount":"未披露(付费墙遮挡)","round":"未公开","display":"金额未披露"},"funding_total":{"amount":"约$5000万+","display":"累计约$5000万+"},"investors":"未披露","founded":"2013","website_url":"https://www.safely-you.com","stage":"成长期","source":"信源治理入库(Tracxn) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B AI跌倒检测","tags":["有融资"]},
 {"name":"The Helper Bees","region":"海外","category_l1":"金融服务","category_l2":"保险","description":"Medicare Advantage 会员参与与保险福利导航平台。","funding_latest":{"date":"2026","amount":"未披露(付费墙遮挡)","round":"未公开","display":"金额未披露"},"funding_total":{"amount":"约$6000万","display":"累计约$6000万"},"investors":"未披露","founded":"2016","website_url":"https://www.thehelperbees.com","stage":"成长期","source":"信源治理入库(Tracxn) 2026-07-15","business_model":"B2B2C","business_model_cn":"B2B2C 保险导航","tags":["有融资"]},
 {"name":"A Place for Mom","region":"海外","category_l1":"养老服务","category_l2":"养老运营","description":"养老社区转介与咨询服务，连接家庭与养老社区。","funding_latest":{"date":"2026","amount":"未披露(付费墙遮挡)","round":"未公开","display":"金额未披露"},"funding_total":{"amount":"约$1亿+","display":"累计约$1亿+"},"investors":"未披露","founded":"2000","website_url":"https://www.aplaceformom.com","stage":"成长期","source":"信源治理入库(Tracxn) 2026-07-15","business_model":"B2B2C","business_model_cn":"B2B2C 养老转介","tags":["有融资"]},
 {"name":"Seniorly","region":"海外","category_l1":"养老服务","category_l2":"养老运营","description":"养老社区/老年公寓搜索匹配平台（2025 被 CareScout 收购）。","funding_latest":{"date":"2025","amount":"被收购(未披露额)","round":"被收购","display":"2025被CareScout收购"},"funding_total":{"amount":"约$4000万","display":"累计约$4000万"},"investors":"CareScout","founded":"2014","website_url":"https://www.seniorly.com","stage":"被收购","source":"信源治理入库(Tracxn) 2026-07-15","business_model":"B2C平台","business_model_cn":"B2C 养老搜索平台","tags":["有融资","被收购"]},
 {"name":"DUOS","region":"海外","category_l1":"医疗服务","category_l2":"健康管理","description":"帮老年人管理健康与生活事务的平台（2022 被 Walmart 收购）。","funding_latest":{"date":"2022","amount":"被收购(未披露额)","round":"被收购","display":"2022被Walmart收购"},"funding_total":{"amount":"约$4000万","display":"累计约$4000万"},"investors":"Walmart","founded":"2017","website_url":"https://www.duos.com","stage":"被收购","source":"信源治理入库(Tracxn) 2026-07-15","business_model":"B2B2C","business_model_cn":"B2B2C 健康管理","tags":["有融资","被收购"]},
 {"name":"Ekso Bionics","region":"海外","category_l1":"康复辅具","category_l2":"康复器械","description":"康复外骨骼，用于中风/神经康复与行动恢复；2014 年上市。","funding_latest":{"date":"2014","amount":"IPO上市","round":"上市","display":"NASDAQ上市(EKSO)"},"funding_total":{"amount":"上市","display":"上市公司"},"investors":"—","founded":"2005","website_url":"https://www.eksobionics.com","stage":"上市","source":"信源治理入库(Tracxn) 2026-07-15","business_model":"B2B设备","business_model_cn":"B2B 康复外骨骼","tags":["上市"]},
 # ---- 第二梯队：近期有融资 ----
 {"name":"Lys Therapeutics","region":"海外","category_l1":"医疗健康","category_l2":"神经/抗衰老","description":"抗衰老脑疗法（神经科学），推进神经退行性疾病管线。","funding_latest":{"date":"2026-07-11","amount":"2900万美元","round":"近期","display":"$29M (2026-07)"},"funding_total":{"amount":"约$3000万","display":"累计约$3000万"},"investors":"未披露","founded":"未披露","website_url":"","stage":"早期","source":"信源治理入库(agetech.com) 2026-07-15","business_model":"Biotech","business_model_cn":"生物科技","tags":["有融资","近期融资"]},
 {"name":"Hera","region":"海外","category_l1":"智能科技","category_l2":"照护平台","description":"AI 养老照护协同平台，连接家庭、照护者与机构。","funding_latest":{"date":"2026-06-26","amount":"2700万美元","round":"Series A","display":"Series A $27M"},"funding_total":{"amount":"约$3000万","display":"累计约$3000万"},"investors":"未披露","founded":"未披露","website_url":"","stage":"A轮","source":"信源治理入库(agetech.com) 2026-07-15","business_model":"B2B平台","business_model_cn":"B2B AI照护平台","tags":["有融资","近期融资"]},
 {"name":"Rejuvenate Bio","region":"海外","category_l1":"医疗健康","category_l2":"神经/抗衰老","description":"抗衰老基因疗法公司，携手默克推进研发。","funding_latest":{"date":"2026-06-24","amount":"新融资(未披露额)","round":"近期","display":"新融资(携手默克)"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"默克等","founded":"未披露","website_url":"https://www.rejuvenatebio.com","stage":"早期","source":"信源治理入库(agetech.com) 2026-07-15","business_model":"Biotech","business_model_cn":"生物科技","tags":["有融资"]},
 {"name":"Vali Health","region":"海外","category_l1":"智能科技","category_l2":"照护平台","description":"将 AI Agent 用于居家照护场景的健康管理工具。","funding_latest":{"date":"2026-06-19","amount":"600万美元","round":"近期","display":"$6M"},"funding_total":{"amount":"约$600万","display":"累计约$600万"},"investors":"未披露","founded":"未披露","website_url":"","stage":"早期","source":"信源治理入库(agetech.com) 2026-07-15","business_model":"B2C App","business_model_cn":"B2C 健康App","tags":["有融资","近期融资"]},
 {"name":"BedHub","region":"海外","category_l1":"养老服务","category_l2":"养老运营","description":"养老照护机构搜索匹配平台，帮助家庭寻找优质机构。","funding_latest":{"date":"2026-07-09","amount":"全国上线(未披露)","round":"初创","display":"全国上线"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露","website_url":"","stage":"初创","source":"信源治理入库(agetech.com) 2026-07-15","business_model":"B2C平台","business_model_cn":"B2C 机构搜索","tags":["未披露融资"]},
 # ---- 第三梯队：认知症/脑健康头部 ----
 {"name":"Linus Health","region":"海外","category_l1":"医疗健康","category_l2":"认知症","description":"数字脑健康平台，时钟绘制+AI 早筛认知障碍。","funding_latest":{"date":"2021","amount":"5490万美元","round":"Series B","display":"Series B $55M (Morningside领投)"},"funding_total":{"amount":"约$6490万","display":"累计约$64.9M"},"investors":"Morningside","founded":"2017","website_url":"https://www.linushealth.com","stage":"B轮","source":"信源治理入库(ADDF/CB) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 脑健康平台","tags":["有融资","认知症"]},
 {"name":"Neurotrack","region":"海外","category_l1":"医疗健康","category_l2":"认知症","description":"眼动+数字认知筛查（FDA 注册），MCI/痴呆早筛。","funding_latest":{"date":"未披露","amount":"NIA/盖茨基金会资助","round":"早期","display":"NIA/盖茨资助"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"NIA,盖茨基金会","founded":"2011","website_url":"https://www.neurotrack.com","stage":"早期","source":"信源治理入库(ADDF) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 认知筛查","tags":["有融资","认知症"]},
 {"name":"BrainCheck","region":"海外","category_l1":"医疗健康","category_l2":"认知症","description":"FDA Class II 数字认知评估与护理平台。","funding_latest":{"date":"2026","amount":"1300万美元 A轮","round":"Series A","display":"$15M(2024)+$13M(2026)"},"funding_total":{"amount":"约$2800万+","display":"累计约$2800万+"},"investors":"Next Coast/UPMC","founded":"2015","website_url":"https://www.braincheck.com","stage":"A轮","source":"信源治理入库(官网) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 认知评估","tags":["有融资","认知症"]},
 {"name":"Altoida","region":"海外","category_l1":"医疗健康","category_l2":"认知症","description":"AR+AI 数字生物标志物，平板 10 分钟预测 AD 风险。","funding_latest":{"date":"2022","amount":"1400万美元","round":"Series A","display":"Series A $14M (默克领投)"},"funding_total":{"amount":"约$2000万","display":"累计约$2000万"},"investors":"M Ventures(默克)","founded":"2016","website_url":"https://www.altoida.com","stage":"A轮","source":"信源治理入库(ADDF) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 数字生物标记","tags":["有融资","认知症"]},
 {"name":"Winterlight Labs","region":"海外","category_l1":"医疗健康","category_l2":"认知症","description":"语音数字生物标志物检测认知障碍（已被 Cambridge Cognition 收购）。","funding_latest":{"date":"2019","amount":"420万美元","round":"Series A(被收购)","display":"Series A $4.2M;后被Cambridge Cognition收购"},"funding_total":{"amount":"约$600万","display":"累计约$600万"},"investors":"Hikma Ventures","founded":"2015","website_url":"https://www.winterlightlabs.com","stage":"被收购","source":"信源治理入库(BioTechScope) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 语音生物标记","tags":["有融资","认知症","被收购"]},
 {"name":"MyndYou","region":"海外","category_l1":"医疗健康","category_l2":"认知症","description":"AI 语音+活动分析远程监测认知变化。","funding_latest":{"date":"未披露","amount":"BIRD基金90万美元","round":"早期","display":"BIRD基金$0.9M"},"funding_total":{"amount":"约$200万","display":"累计约$200万"},"investors":"BIRD基金","founded":"2016","website_url":"https://www.myndyou.com","stage":"早期","source":"信源治理入库(以色列经部) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 远程监测","tags":["有融资","认知症"]},
 {"name":"MapHabit","region":"海外","category_l1":"医疗健康","category_l2":"认知症","description":"视觉映射辅助，支持 AD/痴呆日常认知训练。","funding_latest":{"date":"未披露","amount":"未披露大额","round":"成长","display":"营收约$5.1M(未披露大额融资)"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"2016","website_url":"https://www.maphabit.com","stage":"成长","source":"信源治理入库(AgeTech) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 认知辅助","tags":["有融资","认知症"]},
 {"name":"SingFit","region":"海外","category_l1":"医疗健康","category_l2":"认知症","description":"治疗性音乐/歌唱数字疗法，非药物改善痴呆认知。","funding_latest":{"date":"未披露","amount":"早期/孵化","round":"早期","display":"孵化器阶段"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"2014","website_url":"https://www.singfit.com","stage":"早期","source":"信源治理入库(CB/AgeTech) 2026-07-15","business_model":"B2B2C","business_model_cn":"B2B2C 音乐疗法","tags":["早期","认知症"]},
 {"name":"Optina Diagnostics","region":"海外","category_l1":"医疗健康","category_l2":"认知症","description":"视网膜高光谱成像检测脑淀粉样蛋白，AD 早筛。","funding_latest":{"date":"未披露","amount":"超3000万美元","round":"成长","display":">$30M"},"funding_total":{"amount":"超$3000万","display":"累计>$30M"},"investors":"未披露","founded":"未披露","website_url":"https://www.optinadiagnostics.com","stage":"成长","source":"信源治理入库(ADDF) 2026-07-15","business_model":"B2B设备","business_model_cn":"B2B 影像诊断","tags":["有融资","认知症"]},
 # ---- 第四梯队：法国本土 ----
 {"name":"MonSenior","region":"海外","category_l1":"养老服务","category_l2":"居家护理","description":"老年人生活辅助与良好老龄化服务平台（法国）。","funding_latest":{"date":"未披露","amount":"未披露","round":"未披露","display":"未披露"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露","website_url":"","stage":"早期","source":"信源治理入库(Silvereco) 2026-07-15","business_model":"B2C平台","business_model_cn":"B2C 生活辅助","tags":["未披露融资"]},
 {"name":"Agely Care","region":"海外","category_l1":"养老服务","category_l2":"居家护理","description":"老年人护理与陪伴服务（法国）。","funding_latest":{"date":"未披露","amount":"未披露","round":"未披露","display":"未披露"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露","website_url":"","stage":"早期","source":"信源治理入库(Silvereco) 2026-07-15","business_model":"B2C服务","business_model_cn":"B2C 护理陪伴","tags":["未披露融资"]},
 {"name":"Assystel","region":"海外","category_l1":"智能科技","category_l2":"远程监护","description":"远程协助与家庭安全警报（法国）。","funding_latest":{"date":"未披露","amount":"未披露","round":"未披露","display":"未披露"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露","website_url":"","stage":"早期","source":"信源治理入库(Silvereco) 2026-07-15","business_model":"B2C设备","business_model_cn":"B2C 安全警报","tags":["未披露融资"]},
 {"name":"Xray Moov","region":"海外","category_l1":"医疗服务","category_l2":"上门医疗","description":"上门医疗影像/放射检查移动服务（法国）。","funding_latest":{"date":"未披露","amount":"未披露","round":"未披露","display":"未披露"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露","website_url":"","stage":"早期","source":"信源治理入库(Silvereco) 2026-07-15","business_model":"B2C服务","business_model_cn":"B2C 上门影像","tags":["未披露融资"]},
 {"name":"Swissvoice","region":"海外","category_l1":"智能科技","category_l2":"适老硬件","description":"老年人易用通信终端/电话设备（瑞士）。","funding_latest":{"date":"未披露","amount":"未披露","round":"未披露","display":"未披露"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露","website_url":"https://www.swissvoice.net","stage":"成熟","source":"信源治理入库(Silvereco) 2026-07-15","business_model":"B2B设备","business_model_cn":"B2B 适老通信","tags":["未披露融资"]},
 {"name":"Livana Connect","region":"海外","category_l1":"智能科技","category_l2":"远程监护","description":"老年人连接与远程关怀技术方案（法国）。","funding_latest":{"date":"未披露","amount":"未披露","round":"未披露","display":"未披露"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露","website_url":"","stage":"早期","source":"信源治理入库(Silvereco) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 远程关怀","tags":["未披露融资"]},
 # ---- 早期投资组合 ----
 {"name":"Trusty.Care","region":"海外","category_l1":"金融服务","category_l2":"保险","description":"Medicare 方案比对与防医疗账单破产导航。","funding_latest":{"date":"未披露","amount":"种子","round":"种子","display":"种子轮"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露","website_url":"https://www.trusty.care","stage":"种子","source":"信源治理入库(thirdact.vc) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 保险导航","tags":["早期"]},
 {"name":"Caspar.AI","region":"海外","category_l1":"智能科技","category_l2":"智能家居","description":"养老社区智能家居照护平台。","funding_latest":{"date":"未披露","amount":"种子","round":"种子","display":"种子轮"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露","website_url":"https://www.caspar.ai","stage":"种子","source":"信源治理入库(thirdact.vc) 2026-07-15","business_model":"B2B SaaS","business_model_cn":"B2B 智能家居","tags":["早期"]},
 {"name":"Third Eye Health","region":"海外","category_l1":"医疗服务","category_l2":"远程医疗","description":"为养老社区提供一键式远程急诊。","funding_latest":{"date":"未披露","amount":"种子","round":"种子","display":"种子轮"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露","website_url":"https://www.thirdeyehealth.com","stage":"种子","source":"信源治理入库(thirdact.vc) 2026-07-15","business_model":"B2B平台","business_model_cn":"B2B 远程急诊","tags":["早期"]},
 {"name":"Ome","region":"海外","category_l1":"智能科技","category_l2":"适老硬件","description":"防厨房火灾、助力居家养老的厨房安全产品。","funding_latest":{"date":"未披露","amount":"种子","round":"种子","display":"种子轮"},"funding_total":{"amount":"未披露","display":"未披露"},"investors":"未披露","founded":"未披露","website_url":"","stage":"种子","source":"信源治理入库(thirdact.vc) 2026-07-15","business_model":"B2C硬件","business_model_cn":"B2C 厨房安全","tags":["早期"]},
]

added = 0; skipped = 0
for e in NEW_ENTS:
    nm = e["name"].strip().lower()
    if nm in existing:
        skipped += 1
        continue
    maxserial += 1
    ne = copy.deepcopy(template)
    ne["serial"] = f"#{maxserial:04d}"
    for k, v in e.items():
        ne[k] = v
    ne["tag_l1"] = []
    ne["tag_l2"] = []
    ne["news_coverage"] = {"news_count": 0, "news_quality": "unscored", "latest_news": None}
    ne["value_score"] = 0
    ne["recommend"] = ""
    ne["name_cn"] = ""
    ne["highlights"] = (f"成立于{found}年" if (found := e.get("founded")) and found != "未披露" else "")
    ne["payor_model"] = "未披露"
    ne["desc_cn"] = e["description"]
    ents.append(ne)
    existing.add(nm)
    added += 1

json.dump(ents, open(EP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"企业入库：新增 {added} 家，跳过已存在 {skipped} 家；现有总数 {len(ents)}")

# ========== 3) 资讯入库（manual_news.json）==========
MP = "data/manual_news.json"
news = json.load(open(MP, encoding="utf-8"))
existing_titles = {n.get("title", "").strip().lower() for n in news}

NEWS = [
 # agetech.com (source_id agetech_com)
 ("Lys Therapeutics 募 2900 万美元","推进抗衰老脑疗法管线，面向老年神经退行性疾病治疗。","agetech_com","https://www.agetech.com/news/","2026-07-11",["融资","抗衰老"]),
 ("长寿资本聚首 Gstaad","抗衰老生物科技获主流资本加持，银发长寿赛道受关注。","agetech_com","https://www.agetech.com/news/","2026-07-10",["抗衰老","资本"]),
 ("BedHub 全国上线","解决家庭寻找优质养老照护机构的难题，养老照护匹配平台。","agetech_com","https://www.agetech.com/news/","2026-07-09",["养老运营","平台"]),
 ("居家养老需求推动老年照护可穿戴设备成核心品类","居家养老场景带动照护可穿戴设备需求增长。","agetech_com","https://www.agetech.com/news/","2026-07-08",["可穿戴","居家护理"]),
 ("华盛顿州 AI 驱动 Medicare 审查致老人就医被拒/延误","行业警示：AI 自动审查影响老年人医疗可及性。","agetech_com","https://www.agetech.com/news/","2026-07-07",["政策","AI","Medicare"]),
 ("SeniorCRE 警告：孤岛式 AI 无法成为养老社区运营智能","养老社区运营需整合型 AI 而非孤岛方案。","agetech_com","https://www.agetech.com/news/","2026-06-29",["养老运营","AI"]),
 ("Hera 获 2700 万美元 A 轮","扩张 AI 养老照护协同平台。","agetech_com","https://www.agetech.com/news/","2026-06-26",["融资","AI照护"]),
 ("Rejuvenate Bio 获新融资并携手默克","推进抗衰老基因疗法研发。","agetech_com","https://www.agetech.com/news/","2026-06-24",["融资","抗衰老"]),
 ("Futurewave 可穿戴智能系统欲重塑养老院居民-员工沟通","养老院内部沟通效率提升方案。","agetech_com","https://www.agetech.com/news/","2026-06-22",["可穿戴","养老运营"]),
 ("Vali Health 募 600 万美元","将 AI Agent 用于居家照护场景。","agetech_com","https://www.agetech.com/news/","2026-06-19",["融资","AI照护"]),
 # Being Patient (being_patient)
 ("阿尔茨海默血液检测在真实世界准不准？","评估血液生物标志物检测在临床真实世界的准确度。","being_patient","https://beingpatient.com/alzheimers-disease/","2026-07-15",["认知症","诊断"]),
 ("FDA 批准早期阿尔茨海默病居家注射 Leqembi","早期 AD 患者可在家自行注射 Leqembi，治疗可及性提升。","being_patient","https://beingpatient.com/alzheimers-disease/","2026-07-14",["认知症","FDA","政策"]),
 ("THC/CBD 缓解晚期阿尔茨海默躁动显潜力","大麻素成分对晚期痴呆躁动症状的缓解研究。","being_patient","https://beingpatient.com/alzheimers-disease/","2026-07-14",["认知症","非药物"]),
 ("患者借临床试验与 AI 音乐重塑生活","临床试验结合 AI 音乐疗法改善患者生活。","being_patient","https://beingpatient.com/alzheimers-disease/","2026-05-04",["认知症","疗法"]),
 ("两位女性推动改变痴呆症社会叙事","倡导者推动社会对痴呆症认知转变。","being_patient","https://beingpatient.com/alzheimers-disease/","2026-04-09",["认知症","倡导"]),
 ("一家人对抗后皮质萎缩（痴呆相关）的经历","家庭照护后皮质萎缩患者的真实经历。","being_patient","https://beingpatient.com/alzheimers-disease/","2026-04-02",["认知症","照护"]),
 ("2026 年 FDA 批准的阿尔茨海默疗法全景","盘点 2026 年 FDA 批准的 AD 疗法。","being_patient","https://beingpatient.com/alzheimers-disease/","2026-06-22",["认知症","FDA"]),
 # Silvereco (silvereco)
 ("Stannah 爬楼机获红点设计奖","适老化无障碍设计获红点奖认可。","silvereco","https://www.silvereco.fr/actualites/","2026-07-15",["适老硬件","设计"]),
 ("斯洛伐克推出首个银发经济创新生态系统","国家级银发经济生态建设。","silvereco","https://www.silvereco.fr/actualites/","2026-07-15",["政策","生态"]),
 ("法国游泳联合会发起防溺水宣传，覆盖老年群体","老年防溺水公益宣传。","silvereco","https://www.silvereco.fr/actualites/","2026-07-15",["安全","公益"]),
 ("Arcadie 老年公寓向长者开放避暑降温空间","极端高温下老年公寓开放避暑。","silvereco","https://www.silvereco.fr/actualites/","2026-07-15",["养老运营","高温"]),
 ("高温下长者与照护团队告急，AD-PA 提养老诉求","高温天气暴露养老照护短板。","silvereco","https://www.silvereco.fr/actualites/","2026-07-15",["养老运营","高温"]),
 ("Lanton 建秸秆老年住宅以隔热护长者","绿色适老建筑实践。","silvereco","https://www.silvereco.fr/actualites/","2026-07-15",["适老硬件","建筑"]),
 ("银发创新实验室如何支持健康老龄化","创新实验室助力健康老龄化。","silvereco","https://www.silvereco.fr/actualites/","2026-07-15",["创新","健康"]),
 ("高温期间 Synerpa 机构向居家老人开放","机构高温期开放给居家老人。","silvereco","https://www.silvereco.fr/actualites/","2026-07-15",["养老运营","高温"]),
 ("欧洲百岁老人榜法国居首，长寿主题","欧洲长寿人口分布。","silvereco","https://www.silvereco.fr/actualites/","2026-07-15",["长寿","数据"]),
 ("长者住院管理凸显居家照护缺失环节","住院管理暴露居家照护缺口。","silvereco","https://www.silvereco.fr/actualites/","2026-07-15",["居家护理","痛点"]),
 # vcbeat.top (vcbeat_aging)
 ("国家卫健委发布《老年合理用药促进行动（2026—2030年）》","国内老年用药安全政策出台。","vcbeat_aging","https://vcbeat.top/","2026-07-15",["政策","用药"]),
 ("Pearl Health 完成 1.1 亿美元融资","扩展 Medicare/价值医疗业务。","vcbeat_aging","https://vcbeat.top/","2026-07-08",["融资","价值医疗"]),
 # thirdact.vc (third_act)
 ("Third Act Ventures 入选 2025 顶级健康科技种子基金","专注 aging 的早期 VC 获行业认可。","third_act","https://thirdact.vc/","2025-12-01",["VC","荣誉"]),
 ("MedCity News 探讨 AgeTech 投融资前景","含 Third Act 合伙人的 AgeTech 投融资观点。","third_act","https://thirdact.vc/","2025-04-15",["VC","AgeTech"]),
 # Alzheimers.net (alzheimers_net)
 ("解析记忆照护（长期照护）服务/成本/收益","记忆照护服务内容、成本与获益分析。","alzheimers_net","https://www.alzheimers.net/","2026-07-15",["认知症","长期照护"]),
]

n_added = 0; n_skip = 0
for title, summary, sid, url, date, tags in NEWS:
    if title.strip().lower() in existing_titles:
        n_skip += 1
        continue
    src_name = {"agetech_com":"AgeTech.com","being_patient":"Being Patient","silvereco":"Silvereco","vcbeat_aging":"动脉网","third_act":"Third Act Ventures","alzheimers_net":"Alzheimers.net"}[sid]
    news.append({
        "title": title,
        "summary": summary,
        "source_id": sid,
        "source": src_name,
        "url": url,
        "date": date,
        "tags": tags,
        "ingest_time": "2026-07-15",
    })
    existing_titles.add(title.strip().lower())
    n_added += 1

json.dump(news, open(MP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"资讯入库：新增 {n_added} 条，跳过已存在 {n_skip} 条；现有总数 {len(news)}")
