# -*- coding: utf-8 -*-
"""W2/W3 信源入库：将 34 个新源注入 config.py 的 SOURCES 字典。
采用括号深度定位 SOURCES 闭合处，在闭合前插入；带 key 冲突保护。
仅 commit main，不部署。ingest_time 记录在 notes 中（源级别无独立字段）。
"""
import re

CFG = "config.py"
src = open(CFG, encoding="utf-8").read()
lines = src.split("\n")

# 定位 SOURCES = {
start = None
for i, l in enumerate(lines):
    if re.match(r"^SOURCES\s*=\s*\{", l):
        start = i
        break
assert start is not None, "SOURCES not found"

# 括号深度定位闭合 }
depth = 0
close_idx = None
for j in range(start, len(lines)):
    depth += lines[j].count("{") - lines[j].count("}")
    if depth == 0 and j > start:
        close_idx = j
        break
assert close_idx is not None, "SOURCES close not found"

# 现有 keys（防冲突）
existing_keys = set(re.findall(r'^\s*"([a-z0-9_]+)"\s*:\s*\{', "\n".join(lines[start:close_idx]), re.M))
existing_domains = set(re.findall(r'"l1_domain"\s*:\s*"([^"]+)"', "\n".join(lines[start:close_idx])))

# ---- 新源定义: (key, name, l1_domain, channel_name, url, method, tier, region, notes) ----
NEW = [
    # ===== W2 文娱社交（20 个，已剔除 The Ethel 在库 + 携程不入库）=====
    ("seniorplanet", "Senior Planet", "seniorplanet.org", "articles", "https://seniorplanet.org/articles/", "manual", 1, "overseas", "美国活力老人科技/旅行/兴趣/反诈一手内容社区"),
    ("getsetup", "GetSetUp", "getsetup.io", "blog", "https://blog.getsetup.io/", "manual", 1, "overseas", "全球最大老年直播课平台，适老在线教育+社交标杆"),
    ("roadscholar", "Road Scholar", "roadscholar.org", "blog", "https://www.roadscholar.org/blog", "manual", 1, "overseas", "全美最大老年教育旅行机构，银发游学/旅居标杆"),
    ("stitch", "Stitch", "stitch.net", "blog", "https://www.stitch.net/blog", "manual", 1, "overseas", "全球50+交友/活动社区，先交友后恋爱模式"),
    ("sixtyandme", "Sixty and Me", "sixtyandme.com", "health_fitness", "https://sixtyandme.com/health-and-fitness-over-60/", "manual", 2, "overseas", "全球女性活力老人(60+)生活/旅行/健康社区"),
    ("brainhq", "BrainHQ", "brainhq.com", "news", "https://www.brainhq.com/news", "manual", 3, "overseas", "适老脑力/认知训练科学内容"),
    ("papa_src", "Papa", "papa.com", "resources", "https://www.papa.com/resources", "manual", 2, "overseas", "伴老/companion care 平台，代际社交内容（企业作源偏PR）"),
    ("cogenerate", "CoGenerate (原 Encore.org)", "cogenerate.org", "stories", "https://cogenerate.org/stories/", "manual", 2, "overseas", "退休再就业/第二职业/代际共创，老有所为标杆"),
    ("restless", "Rest Less", "restless.co.uk", "home", "https://restless.co.uk/", "manual", 1, "overseas", "英国50+一站式门户（工作/旅行/理财/交友）"),
    ("silversurfers", "Silversurfers", "silversurfers.com", "home", "https://www.silversurfers.com/", "manual", 2, "overseas", "英国最大50+在线社区，UGC活力老人内容"),
    ("silvertraveladvisor", "Silver Travel Advisor", "silvertraveladvisor.com", "reviews", "https://www.silvertraveladvisor.com/escorted-tour-reviews", "manual", 2, "overseas", "专做50+独立旅行评测，用户真实点评模式"),
    ("primewomen", "Prime Women", "primewomen.com", "entertainment", "https://primewomen.com/category/entertainment/", "manual", 2, "overseas", "美国成熟女性时尚/旅行/理财媒体"),
    ("halmek", "ハルメク Halmek", "halmek.co.jp", "magazine", "https://magazine.halmek.co.jp/", "manual", 1, "overseas", "日本50+女性杂志标杆，订阅制+活动+旅行会员生态"),
    ("zsjc", "全国シルバー人材センター (zsjc)", "zsjc.or.jp", "oshirase", "https://www.zsjc.or.jp/oshirase/old", "manual", 2, "overseas", "日本老有所为官方协会，再就业/志愿一手数据"),
    ("laoren", "快乐老人报/枫网", "laoren.com", "home", "http://www.laoren.com/", "manual", 1, "domestic", "国内老年门户标杆，八大频道+论坛+旅游+大学"),
    ("hongsong", "红松 Hongsong", "hongsong.tuixiu.com", "about", "https://hongsong.tuixiu.com/about", "manual", 1, "domestic", "国内退休文娱直播课社区头部"),
    ("tangdou", "糖豆", "tangdou.com", "home", "https://www.tangdou.com/", "manual", 1, "domestic", "国内最大中老年运动/广场舞社区"),
    ("meipian", "美篇", "meipian.cn", "home", "https://www.meipian.cn/", "manual", 2, "domestic", "国内中老年图文创作/兴趣社群"),
    ("caua", "中国老年大学协会 (CAUA)", "caua1988.com", "home", "http://www.caua1988.com/", "manual", 2, "domestic", "国内老年教育官方协会，政策+会员动态一手源"),
    ("silversneakers", "SilverSneakers", "silversneakers.com", "blog", "https://www.silversneakers.com/blog", "manual", 2, "overseas", "美国老年运动健身社区标杆，健身即社交"),
    # ===== W3 AIGC 高科技（14 个）=====
    ("venturebeat_ai", "VentureBeat – AI", "venturebeat.com", "ai", "https://venturebeat.com/ai/", "manual", 3, "overseas", "通用大模型在医疗/养老场景落地报道，可反查OpenAI/Google银发栏目"),
    ("mit_tr_ai", "MIT Technology Review – AI", "technologyreview.com", "ai", "https://www.technologyreview.com/topic/artificial-intelligence/", "manual", 3, "overseas", "LLM/具身智能前沿与伦理深度文，反常识素材密度高"),
    ("aging2", "Aging2.0 (Global Healthcare Innovation)", "aging2.com", "news_gn", "https://news.google.com/rss/search?q=site:aging2.com+aging+OR+senior+OR+agetech&hl=en-US", "rss", 2, "overseas", "全球AgeTech创新者社区，一手创业/政策信号；GN代理列表页"),
    ("therobotreport", "The Robot Report", "therobotreport.com", "robotics_news", "https://www.therobotreport.com/robotics-news/", "manual", 2, "overseas", "养老/护理/人形机器人一手新闻与融资M&A"),
    ("wearabletech", "Wearable Technologies", "wearable-technologies.com", "news", "https://wearable-technologies.com/news-list", "manual", 2, "overseas", "AI眼镜/可穿戴/助听硬件一手产品与融资"),
    ("agewell", "AGE-WELL", "agewell-nce.ca", "news", "https://agewell-nce.ca/news", "manual", 2, "overseas", "加拿大技术适老研究网络，AI跌倒/认知症/语音银行一手研究"),
    ("marktechpost", "MarkTechPost", "marktechpost.com", "ai", "https://marktechpost.com/category/artificial-intelligence/", "manual", 3, "overseas", "医疗/养老垂直大模型、Agent技术进展译介"),
    ("ieee_spectrum_robotics", "IEEE Spectrum – Robotics", "spectrum.ieee.org", "robotics", "https://spectrum.ieee.org/robotics", "manual", 3, "overseas", "具身智能/人形机器人学术+产业（含日本护理机器人）"),
    ("robohub", "Robohub", "robohub.org", "home", "https://robohub.org/", "manual", 3, "overseas", "机器人社区聚合，老年护理机器人研究/观点"),
    ("thedecoder", "The Decoder", "the-decoder.com", "home", "https://the-decoder.com/", "manual", 3, "overseas", "欧洲视角AI大模型/代理新闻，可反查healthcare LLM落地"),
    ("medicalfuturist", "The Medical Futurist", "medicalfuturist.com", "ai", "https://medicalfuturist.com/category/artificial-intelligence", "manual", 3, "overseas", "AI医疗（诊断/早筛/数字疗法/手术机器人）深度解读"),
    ("statnews", "STAT News – Health Tech", "statnews.com", "healthtech_gn", "https://news.google.com/rss/search?q=site:statnews.com+AI+OR+healthcare+technology&hl=en-US", "rss", 2, "overseas", "医疗AI政策/支付/FDA一手报道；GN代理列表页"),
    ("magnifyventures", "Magnify Ventures", "magnifyventures.com", "home", "https://magnifyventures.com/", "manual", 2, "overseas", "早期VC，care-economy基金；⚠️入库前需复核实际投资主题（公开站现强调online education）"),
    ("counterpoint", "Counterpoint Research", "counterpointresearch.com", "insights", "https://counterpointresearch.com/en/insights/", "manual", 3, "overseas", "可穿戴/边缘AI市场量化数据，反常识数据素材"),
]

# 校验冲突
skip = []
block_lines = []
for (key, name, dom, ch, url, method, tier, region, notes) in NEW:
    if key in existing_keys:
        skip.append(f"{key} (key冲突)")
        continue
    if dom in existing_domains:
        skip.append(f"{key} -> {dom} (域名已存在)")
        continue
    block_lines.append(
        f'    "{key}": {{\n'
        f'        "name": "{name}",\n'
        f'        "l1_domain": "{dom}",\n'
        f'        "l2_channels": [\n'
        f'            ("{ch}", "{url}", "{method}"),\n'
        f'        ],\n'
        f'        "tier": {tier},\n'
        f'        "region": "{region}",\n'
        f'        "notes": "{notes}",\n'
        f'        "ingest_time": "2026-07-16",\n'
        f'    }},'
    )

insert_text = "\n".join(block_lines) + "\n"
# 在闭合 } 前插入
new_lines = lines[:close_idx] + [insert_text.rstrip("\n")] + lines[close_idx:]
new_src = "\n".join(new_lines)
open(CFG, "w", encoding="utf-8").write(new_src)

print(f"新增源条数: {len(block_lines)}")
print(f"跳过(冲突): {skip if skip else '无'}")
print(f"SOURCES 闭合行原: {close_idx+1}")
