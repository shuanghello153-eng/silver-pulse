"""
Silver Pulse configuration — sources, classification, scoring weights, thresholds.
v5.0: 13-class enterprise categorization, event-type news classification,
     L1/L2 source hierarchy, tag pool, data filtering logic docs.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================================================================
# 1. ENTERPRISE CATEGORIZATION (13 L1 + 70 L2)
# ================================================================
# Enterprise L1 categories (no numbering in display)
# L2 subcategories map to each L1
# 企业研究价值分色阶阈值。注意：企业库徽章实际渲染的是 enterprise_scores.json
# 的 research_value（量纲 ~13–68，P50=26 / P75=35 / P90=43），并非 all_enterprises.json
# 的 value_score（量纲 0–61，均值 24）。两者量纲不同，必须用 research_value 的分位数定阈值。
# 阈值依据 data/enterprise/enterprise_scores.json 分位数：P50=26 / P75=35 / P90=43 / max=68。
ENT_RV_HIGH = 48   # ≥ 此值 → s-high（绿，研究价值高，约 Top 6%，真正值得深写）
ENT_RV_MID = 26    # ≥ 此值且 < HIGH → s-mid（蓝，研究价值中，约 44%）；< 此值 → s-low（灰，约 50%）

# 企业库"近期有动态"判定窗口（天）。last_news_date 距今 ≤ 此值 → 卡片显示
# "🔥 近期有动态"标签，并支持"只看近期有动态"筛选聚焦。
# 来源优先级：企业 news_coverage.latest_news 最大日期 > enterprise_scores.last_event_date
#   > scored_latest 按 entity_name 匹配 > 企业名在资讯标题子串兜底匹配。
NEWS_RECENT_DAYS = 30
ENTERPRISE_CATEGORIES = {
  "养老服务": [
    "CCRC",
    "CCRC",
    "CCRC",
    "CCRC",
    "CCRC",
    "CCRC",
    "CCRC",
    "CCRC",
    "CCRC",
    "CCRC",
    "CCRC",
    "CCRC",
    "CCRC",
    "CCRC",
    "SDOH",
    "SDOH",
    "SDOH",
    "SDOH",
    "SDOH",
    "SDOH",
    "SDOH",
    "SDOH",
    "SDOH",
    "SDOH",
    "SDOH",
    "专业护理",
    "专业护理",
    "专业护理",
    "专业护理",
    "专业护理",
    "专业护理",
    "专业护理",
    "专业护理",
    "专业护理",
    "专业护理",
    "中医养生",
    "中医养生",
    "中医养生",
    "中医养生",
    "中医养生",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "养老机构",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "安宁疗护",
    "家政",
    "家政",
    "家政",
    "家政",
    "家政",
    "家政",
    "家政",
    "家政",
    "家政",
    "家政",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家医疗",
    "居家康复",
    "居家康复",
    "居家康复",
    "居家康复",
    "居家康复",
    "居家康复",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "居家护理",
    "康养地产",
    "康养地产",
    "康养地产",
    "康养地产",
    "康养地产",
    "康养地产",
    "康养地产",
    "康养地产",
    "康养地产",
    "康养地产",
    "康养地产",
    "康养地产",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "康复医疗",
    "心理健康",
    "心理健康",
    "心理健康",
    "心理健康",
    "心理健康",
    "心理健康",
    "心理健康",
    "心理健康",
    "心理健康",
    "心理健康",
    "心理健康",
    "心理健康",
    "心理健康",
    "心理健康",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "慢病管理",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士上门",
    "护士派遣",
    "护士派遣",
    "护士派遣",
    "护士派遣",
    "护士派遣",
    "护士派遣",
    "护工培训",
    "护工培训",
    "护工培训",
    "护工培训",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护工平台",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "护理协调",
    "殡葬",
    "殡葬",
    "殡葬",
    "殡葬",
    "照护支持",
    "照护支持",
    "照护支持",
    "照护支持",
    "照护支持",
    "照护支持",
    "认知症",
    "认知症",
    "认知症",
    "认知症",
    "认知症",
    "认知症",
    "认知症",
    "认知症",
    "认知症",
    "认知症",
    "认知症",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知筛查",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "认知训练",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "诊所",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程医疗",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程护理",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "远程监护",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "适老化",
    "陪诊",
    "陪诊",
    "陪诊",
    "陪诊",
    "陪诊",
  ],
  "康复辅具": [
    "人形机器人",
    "人形机器人",
    "人形机器人",
    "人形机器人",
    "人形机器人",
    "人形机器人",
    "人形机器人",
    "人形机器人",
    "人形机器人",
    "人形机器人",
    "人形机器人",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助听器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "助行器",
    "医疗器械",
    "医疗器械",
    "医疗器械",
    "医疗器械",
    "医疗器械",
    "医疗器械",
    "医疗器械",
    "医疗器械",
    "医疗器械",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "可穿戴监测",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "外骨骼",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "康复器械",
    "护理床",
    "护理床",
    "护理床",
    "护理床",
    "护理床",
    "护理床",
    "护理床",
    "护理床",
    "护理床",
    "护理床",
    "护理床",
    "护理床",
    "护理床",
    "护理床",
    "智能药盒",
    "智能药盒",
    "智能药盒",
    "智能药盒",
    "智能药盒",
    "智能药盒",
    "智能药盒",
    "智能药盒",
    "智能药盒",
    "智能药盒",
    "机器人",
    "机器人",
    "机器人",
    "机器人",
    "机器人",
    "机器人",
    "机器人",
    "机器人",
    "机器人",
    "机器人",
    "机器人",
    "机器人",
    "用药提醒",
    "用药提醒",
    "用药提醒",
    "用药提醒",
    "用药提醒",
    "用药提醒",
    "用药提醒",
    "用药提醒",
    "用药提醒",
    "用药提醒",
    "用药提醒",
    "用药提醒",
    "用药提醒",
    "用药管理",
    "用药管理",
    "用药管理",
    "用药管理",
    "用药管理",
    "用药管理",
    "用药管理",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "睡眠监测",
    "紧急呼叫",
    "紧急呼叫",
    "紧急呼叫",
    "紧急呼叫",
    "紧急呼叫",
    "紧急呼叫",
    "紧急呼叫",
    "紧急呼叫",
    "紧急呼叫",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "跌倒监测",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
    "轮椅",
  ],
  "消费品": [
    "个人护理",
    "个人护理",
    "个人护理",
    "个人护理",
    "个人护理",
    "个人护理",
    "个人护理",
    "个人护理",
    "个人护理",
    "个人护理",
    "个人护理",
    "个人护理",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "体检筛查",
    "垂直电商",
    "垂直电商",
    "垂直电商",
    "垂直电商",
    "垂直电商",
    "垂直电商",
    "垂直电商",
    "尿失禁",
    "尿失禁",
    "尿失禁",
    "尿失禁",
    "尿失禁",
    "尿失禁",
    "尿失禁",
    "尿失禁",
    "尿失禁",
    "尿失禁",
    "尿失禁",
    "心血管",
    "心血管",
    "心血管",
    "心血管",
    "心血管",
    "智能家居",
    "智能家居",
    "智能家居",
    "智能家居",
    "智能家居",
    "智能家居",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "智能硬件",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "更年期",
    "服装鞋帽",
    "服装鞋帽",
    "服装鞋帽",
    "服装鞋帽",
    "服装鞋帽",
    "服装鞋帽",
    "服装鞋帽",
    "服装鞋帽",
    "服装鞋帽",
    "服装鞋帽",
    "服装鞋帽",
    "服装鞋帽",
    "电商",
    "电商",
    "电商",
    "电商",
    "电商",
    "电商",
    "电商",
    "电商",
    "电商",
    "电商",
    "电商",
    "电商",
    "电商",
    "电商",
    "眼镜",
    "眼镜",
    "眼镜",
    "眼镜",
    "眼镜",
    "眼镜",
    "眼镜",
    "眼镜",
    "眼镜",
    "眼镜",
    "眼镜",
    "眼镜",
    "纸尿裤",
    "纸尿裤",
    "纸尿裤",
    "纸尿裤",
    "纸尿裤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "美妆护肤",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品",
    "药品配送",
    "药品配送",
    "药品配送",
    "药品配送",
    "药品配送",
    "药品配送",
    "药品配送",
    "药品配送",
    "药品配送",
    "视觉辅助",
    "视觉辅助",
    "视觉辅助",
    "视觉辅助",
    "视觉辅助",
    "视觉辅助",
    "视觉辅助",
    "视觉辅助",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
    "零售",
  ],
  "文娱社交": [
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "健身",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "兴趣社群",
    "就业",
    "就业",
    "就业",
    "就业",
    "就业",
    "就业",
    "教育",
    "教育",
    "教育",
    "教育",
    "教育",
    "教育",
    "教育",
    "教育",
    "教育",
    "教育",
    "教育",
    "教育",
    "教育",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "文娱",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "旅游",
    "相亲",
    "相亲",
    "相亲",
    "相亲",
    "相亲",
    "相亲",
    "相亲",
    "相亲",
    "短视频",
    "短视频",
    "短视频",
    "短视频",
    "短视频",
    "社区",
    "社区",
    "社区",
    "社区",
    "社区",
    "社区",
    "社区",
    "邻里社交",
    "邻里社交",
    "邻里社交",
    "邻里社交",
    "邻里社交",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴服务",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
    "陪伴机器人",
  ],
  "食品营养": [
    "个性化营养",
    "个性化营养",
    "个性化营养",
    "个性化营养",
    "个性化营养",
    "个性化营养",
    "个性化营养",
    "个性化营养",
    "个性化营养",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "保健品",
    "养老膳食",
    "养老膳食",
    "养老膳食",
    "养老膳食",
    "养老膳食",
    "养老膳食",
    "功能性食品",
    "功能性食品",
    "功能性食品",
    "功能性食品",
    "功能性食品",
    "功能性食品",
    "糖尿病",
    "糖尿病",
    "糖尿病",
    "糖尿病",
    "糖尿病",
    "糖尿病",
    "糖尿病",
    "糖尿病",
    "糖尿病",
    "糖尿病",
    "糖尿病",
    "糖尿病",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "维生素矿物质",
    "膳食补充剂",
    "膳食补充剂",
    "膳食补充剂",
    "膳食补充剂",
    "膳食补充剂",
    "膳食补充剂",
    "膳食配送",
    "膳食配送",
    "膳食配送",
    "膳食配送",
    "膳食配送",
    "膳食配送",
    "膳食配送",
    "膳食配送",
    "膳食配送",
    "膳食配送",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
    "营养食品",
  ],
  "行业服务": [
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "AI医疗",
    "养老信息平台",
    "养老信息平台",
    "养老信息平台",
    "养老信息平台",
    "养老信息平台",
    "养老信息平台",
    "养老信息平台",
    "养老信息平台",
    "养老信息平台",
    "养老信息平台",
    "养老信息平台",
    "养老信息平台",
    "养老信息平台",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "养老咨询",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业媒体",
    "行业研究",
    "行业研究",
    "行业研究",
    "行业研究",
    "行业研究",
    "行业研究",
    "行业研究",
    "行业研究",
    "资讯门户",
    "资讯门户",
    "资讯门户",
    "资讯门户",
    "资讯门户",
    "资讯门户",
    "资讯门户",
    "资讯门户",
    "资讯门户",
    "资讯门户",
    "资讯门户",
    "资讯门户",
  ],
  "金融保险": [
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险",
    "保险科技",
    "保险科技",
    "保险科技",
    "保险科技",
    "保险科技",
    "保险科技",
    "保险科技",
    "保险科技",
    "保险科技",
    "保险科技",
    "保险科技",
    "遗产规划",
    "遗产规划",
    "遗产规划",
    "遗产规划",
    "遗产规划",
    "遗产规划",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "金融理财",
    "长护险",
    "长护险",
    "长护险",
    "长护险",
    "长护险",
  ],
  "投资机构": [
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "VC",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "产业基金",
    "养老REIT",
    "养老REIT",
    "养老REIT",
    "养老REIT",
    "养老REIT",
    "养老REIT",
    "养老REIT",
    "养老REIT",
    "养老REIT",
    "养老REIT",
    "养老REIT",
    "养老REIT",
  ],
}

ENTERPRISE_CATEGORY_CODES = {
    "养老服务": "01",
    "康复辅具": "02",
    "消费品": "03",
    "文娱社交": "04",
    "食品营养": "05",
    "行业服务": "06",
    "金融保险": "07",
    "投资机构": "08",
}

# 中心度：领域重要性权重（用于资讯/企业评分的领域匹配）
CATEGORY_CENTRALITY = {
    "养老服务": 10,
    "康复辅具": 10,
    "消费品": 7,
    "文娱社交": 7,
    "食品营养": 7,
    "行业服务": 4,
    "金融保险": 7,
    "投资机构": 4,
}

CATEGORY_CENTRALITY_DEFAULT = 6  # 未命中任何领域时的中性分
NEWS_EVENT_TYPES = {
    "融资": {"label": "融资", "desc": "企业获得新一轮融资"},
    "收购并购": {"label": "收购并购", "desc": "企业被收购或并购交易"},
    "政策法规": {"label": "政策法规", "desc": "政府政策、监管法规出台"},
    "产品发布": {"label": "产品发布", "desc": "新产品或新服务上线"},
    "行业趋势": {"label": "行业趋势", "desc": "行业报告、数据研究、趋势分析"},
    "人事变动": {"label": "人事变动", "desc": "高管加入/离职、创始人动态"},
    "其他事件": {"label": "其他事件", "desc": "不属于以上类型的重要事件"},
}

# L2: domain involved (reuse enterprise L1 names)
NEWS_DOMAINS = list(ENTERPRISE_CATEGORIES.keys())

# ================================================================
# 3. TAG POOL
# ================================================================
# Tags are free-form but maintained in a pool for consistency.
# Max 5 tags per enterprise/article.
# Tag types: capital signal, endorsement, stage, special markers
TAG_POOL = {
    # Capital signals
    "融资过亿": {"type": "capital", "desc": "累计融资超过1亿人民币或等值美元"},
    "已被收购": {"type": "capital", "desc": "企业已被收购"},
    "IPO上市": {"type": "capital", "desc": "企业已上市"},
    "已退市": {"type": "capital", "desc": "企业已退市"},
    # Endorsement
    "AARP旗下": {"type": "endorsement", "desc": "AARP体系内企业或合作方"},
    "Khosla投资": {"type": "endorsement", "desc": "Khosla Ventures投资企业"},
    "YC孵化": {"type": "endorsement", "desc": "Y Combinator孵化"},
    "政府支持": {"type": "endorsement", "desc": "获得政府资金或政策支持"},
    # Stage
    "种子轮": {"type": "stage", "desc": "处于种子轮阶段"},
    "成长期": {"type": "stage", "desc": "处于成长期"},
    "成熟期": {"type": "stage", "desc": "处于成熟期"},
    "已倒闭": {"type": "stage", "desc": "企业已停止运营"},
    # Special markers
    "对标标的": {"type": "special", "desc": "值得中国创业者深度参考的企业"},
    "模式创新": {"type": "special", "desc": "商业模式有独特创新"},
    "中国市场已有同类": {"type": "special", "desc": "中国已有类似企业/产品"},
    "订阅制": {"type": "special", "desc": "商业模式为订阅制"},
    "B2B2C": {"type": "special", "desc": "商业模式为B2B2C"},
    "硬件+服务": {"type": "special", "desc": "硬件+服务结合模式"},
    # Emerging sub-tracks / business models (2026-07-08 标签池迭代补充)
    "养老金融": {"type": "special", "desc": "养老/退休金融服务赛道（养老金、养老理财、投顾），国内个人养老金制度落地后高频出现"},
    "按效付费": {"type": "special", "desc": "基于价值/效果的付费模式（value-based / outcome-based），与按服务量付费相对"},
    # Geographic (for overseas enterprises)
    "日本": {"type": "geo", "desc": "日本企业"},
    "以色列": {"type": "geo", "desc": "以色列企业"},
    "欧洲": {"type": "geo", "desc": "欧洲企业"},
}

# ================================================================
# 3b. ARTICLE_TAG_POOL / ARTICLE_TAG_RULES
# ================================================================
# 【T34 标签体系重构 2026-07-10】
# 资讯(article)标签与企业(enterprise)标签解耦：
#   - 上段 TAG_POOL 实际被 generator.py / scorer.py / gen_about.py 当作
#     「UI 标签徽章 + 强模 industry prompt 词表」在用（属 UI/SRC 地盘，不触碰），
#     所以此处另起 ARTICLE_TAG_POOL，专门承载「资讯交叉维度标签」。
#   - 设计原则：标签只放「横切维度」，绝不与分类重复——
#       * event_type（融资/收购并购/产品发布/政策法规/行业趋势/人事变动/其他事件）
#         由 generator.classify_event_type 承担；
#       * domains（养老地产/居家养老/认知症/失智老人赛道…）由
#         generator.classify_domain 承担；
#       * 本池只放「资本性质 / 反常识 / 政策·支付方 / 技术 / 市场 / 模式」这类
#         横跨多个分类、能帮选题/写稿做「二次筛选」的维度。
#   - 反常识 为「自动标签」：novelty>=6 时由 selection/tagger.py 自动打上，
#     不靠关键词命中。
#   - 每条资讯标签数严格 2~5（selection/tagger.detect_cross_tags 强制约束）。
ARTICLE_TAG_POOL = {
    # 资本性质（强调「特殊」资本事件；普通融资不入此列，由 event_type=融资 表达）
    "IPO":          {"type": "capital",  "desc": "已上市/递交招股书/公开募股（巨头，信息量丰富）"},
    "收购":          {"type": "capital",  "desc": "发生并购/被收购（资本整合信号）"},
    "大额融资":       {"type": "capital",  "desc": "单笔融资过亿（量级信号，资本加码）"},
    "战略投资":       {"type": "capital",  "desc": "战略投资/产业资本/CVC 入股"},
    # 反常识 / 信号强度
    "反常识":         {"type": "novelty",  "desc": "novelty≥6：角度稀缺、反直觉、打破常识（自动标签）"},
    # 政策 / 支付方
    "政策利好":       {"type": "tailwind", "desc": "政策/法规带来的正面催化"},
    "支付方创新":      {"type": "tailwind", "desc": "Medicare/Medicaid/商业保险/长护险等支付端创新"},
    # 技术维度
    "AI应用":        {"type": "tech",     "desc": "AI/大模型/机器人落地应用"},
    "数字疗法":       {"type": "tech",     "desc": "软件驱动的治疗/干预"},
    "远程医疗":       {"type": "tech",     "desc": "远程/虚拟照护"},
    "智能硬件":       {"type": "tech",     "desc": "可穿戴/传感器/硬件+服务"},
    # 市场维度
    "中国对标":       {"type": "market",   "desc": "对中国创业者/市场有深度参照价值"},
    "银发出海":       {"type": "market",   "desc": "面向海外/跨境扩张"},
    # 模式维度
    "订阅制":         {"type": "model",    "desc": "订阅制商业模式"},
    "按效付费":       {"type": "model",    "desc": "value-based / outcome-based 付费"},
    "B2B2C":        {"type": "model",    "desc": "B2B2C 渠道结构"},
}

# 自动打标规则：detect_cross_tags 时按「顺序=优先级」逐条匹配，命中即加标签，
# 最终受 2~5 上限约束。反常识单独由 novelty 触发（见下）。
# 关键词同时覆盖中英文（scored_latest 含大量中文 AgeClub/36Kr 与英文海外源）。
ARTICLE_TAG_RULES = [
    # —— 资本性质 ——
    ("IPO",     ["ipo", "ipo filing", "goes public", "上市", "敲钟", "挂牌",
                 "公开募股", "nasdaq", "nyse", "港交所", "向 sec 递交", "debut on"]),
    ("收购",     ["acquires", "acquisition", "acquired", "收购", "并购", "merger",
                 "买下", "被收购", "takeover", "buyout"]),
    ("战略投资",   ["strategic investment", "战略投资", "产业资本", "corporate venture",
                 "cvc", "战略入股", "领投"]),
    # 大额融资：由金额解析兜底（见 detect_cross_tags 内 _big_funding），此处只兜关键词
    ("大额融资",   ["亿", "billion", "十亿", "亿元", "series c", "series d", "c轮", "d轮",
                 "mega round", "超大轮", "9-figure", "8-figure"]),
    # 融资活跃：所有融资/投资类事件的「横切」标记（与 event_type=融资 不同轴，
    # 表达「资本正在加码该赛道」这一视角，避免把 event_type 本身塞回 tags）
    ("融资活跃",   ["融资", "raises", "funding", "获投", "获融", "series", "round of",
                 "investment", "本轮", "invests", "capital"]),
    # 新品上线：产品/服务发布类事件的「横切」标记（与 event_type=产品发布 不同轴）
    ("新品上线",   ["发布", "推出", "launch", "上线", "新品", "debut", "unveil", "首发",
                 "released", "rollout", "announces"]),
    # —— 政策 / 支付方 ——
    ("政策利好",   ["medicare", "medicaid", "cms", "fda", "政策", "法规", "长护险", "津贴",
                 "补贴", "法案", "指导意见", "管理办法", "条例", "利好", "国务院", "民政部",
                 "卫健委", "rule", "regulation", "bill", "legislation", "reform"]),
    ("支付方创新",  ["medicare advantage", "medicaid", "long-term care insurance", "长护险",
                 "commercial insurance", "insurtech", "保险科技", "value-based", "按效付费",
                 "支付方", "payer", "reimbursement", "报销", "商保"]),
    # —— 技术维度 ——
    ("AI应用",   ["ai", "人工智能", "大模型", "机器人", "gpt", "machine learning", "算法",
                 "智能", "robot", "algorithm", "generative"]),
    ("数字疗法",   ["digital therapeutics", "数字疗法", "digital health", "软件医疗", "samd",
                 "digital therapeutic"]),
    ("远程医疗",   ["telehealth", "remote patient", "远程医疗", "虚拟照护", "远程康复",
                 "virtual care", "remote monitoring"]),
    ("智能硬件",   ["wearable", "可穿戴", "传感器", "智能床垫", "电子皮肤", "硬件", "辅具",
                 "rehab device", "康复设备", "sensor", "device"]),
    # —— 市场维度 ——
    ("中国对标",   ["中国", "国内", "china", "chinese", "对标", "参照", "可复制", "银发",
                 "养老", "老龄化", "民政部", "卫健委"]),
    ("银发出海",   ["出海", "global", "overseas expansion", "国际市场", "东南亚", "日本市场",
                 "欧洲市场", "美国市场", "expand to", "enters", "launches in"]),
    # —— 模式维度 ——
    ("订阅制",    ["订阅", "subscription", "saas", "按月付费", "membership model"]),
    ("按效付费",   ["value-based", "outcome-based", "按效付费", "按效果付费", "绩效付费",
                 "pay-for-performance"]),
    ("B2B2C",   ["b2b2c", "平台型", "marketplace", "渠道方", "聚合平台"]),
]

# 反常识自动标签阈值（selection/tagger 使用）。novelty>=该值即打「反常识」。
ARTICLE_NOVELTY_TAG_THRESHOLD = 6

# ================================================================
# 4. SOURCES — L1 (domain) + L2 (channel URL)
# ================================================================
# Each source has:
#   name:       display name
#   l1_domain:  primary website domain (for display)
#   l2_channels: list of (channel_name, channel_url, collection_method)
#   tier:       1=T1核心 2=T2扩展 3=T3参考
#   region:     "overseas" / "domestic"
#   notes:      optional notes
#
# collection_method: "rss" / "google_news" / "manual" / "api"
# ================================================================

SOURCES = {
    # === T1 Overseas Core ===
    "homehealthcarenews": {
        "name": "Home Health Care News",
        "l1_domain": "homehealthcarenews.com",
        "l2_channels": [
            ("funding", "https://homehealthcarenews.com/feed/", "rss"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "居家护理行业核心媒体，有专门funding频道",
    },
    "mcknightssenior": {
        "name": "McKnight's Senior Living",
        "l1_domain": "mcknightsseniorliving.com",
        "l2_channels": [
            ("daily_briefing", "https://www.mcknightsseniorliving.com/home/news/daily-briefing/", "google_news"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "",
    },
    "mcknightshomecare": {
        "name": "McKnight's Home Care",
        "l1_domain": "mcknightshomecare.com",
        "l2_channels": [
            ("news", "https://www.mcknightshomecare.com/", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "",
    },
    "hospicenews": {
        "name": "Hospice News",
        "l1_domain": "hospicenews.com",
        "l2_channels": [
            ("home", "https://hospicenews.com/", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "",
    },
    "seniorhousingnews": {
        "name": "Senior Housing News",
        "l1_domain": "seniorhousingnews.com",
        "l2_channels": [
            ("feed", "https://seniorhousingnews.com/feed/", "rss"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "",
    },
    "thegerontechnologist": {
        "name": "The Gerontechnologist",
        "l1_domain": "thegerontechnologist.com",
        "l2_channels": [
            ("feed", "https://thegerontechnologist.com/feed/", "rss"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "AgeTech Map来源，RSS聚合文章+播客（/feed/ 实测可用，整站google_news查询为0需直连）",
    },
    "fiercehealthcare": {
        "name": "FierceHealthcare",
        "l1_domain": "fiercehealthcare.com",
        "l2_channels": [
            ("venture_capital", "https://www.fiercehealthcare.com/keyword/venture-capital-vc", "google_news"),
            ("funding_round", "https://www.fiercehealthcare.com/keyword/funding-round", "google_news"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "VC和funding两个频道分开监控",
    },
    "crunchbase_news": {
        "name": "Crunchbase News",
        "l1_domain": "news.crunchbase.com",
        "l2_channels": [
            ("health_wellness_biotech", "https://news.crunchbase.com/feed/", "rss"),
        ],
        "tier": 2,  # 用户指定T2（二手/专业平台）2026-07-09
        "region": "overseas",
        "notes": "Crunchbase官方融资资讯，专注health/wellness/biotech",
    },
    # === T1/T2 Overseas — RSS works ===
    "mobihealthnews": {
        "name": "MobiHealthNews",
        "l1_domain": "mobihealthnews.com",
        "l2_channels": [
            ("investor", "https://www.mobihealthnews.com/categories/investor", "google_news"),
            ("news", "https://www.mobihealthnews.com/news", "google_news"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "数字健康核心媒体，investor频道专门报道融资",
    },
    # === T2 Overseas — Google News proxy ===
    "startuphealth": {
        "name": "StartUp Health",
        "l1_domain": "startuphealth.com",
        "l2_channels": [
            ("blog", "https://www.startuphealth.com/startup-health-blog?format=rss", "rss"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "每周投融资资讯，关注health transformation企业",
    },
    "agetechnews": {
        "name": "AgeTech News",
        "l1_domain": "agetech.news",
        "l2_channels": [
            ("home", "https://www.agetech.news/", "google_news"),
        ],
        "tier": 2,  # 用户提"AgeTech"指代不明确，保守维持T2（agetech.news已断更）；若指agetech.com请告知
        "region": "overseas",
        "notes": "已断更，保留在信源库做历史参考；unreliable: proxy dependent（仅经Google News代理，已断更）",
        "unreliable": "proxy dependent",
    },
    "agetech_com": {
        "name": "AgeTech.com",
        "l1_domain": "agetech.com",
        "l2_channels": [
            ("news", "https://www.agetech.com/news/", "google_news"),
        ],
        "tier": 1,  # 用户指定T1（AgeTech）2026-07-09
        "region": "overseas",
        "notes": "AgeTech企业+融资+新闻综合平台；unreliable: proxy dependent（经Google News代理，无稳定直连RSS，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    "agetech_space": {
        "name": "AgeTech.space",
        "l1_domain": "agetech.space",
        "l2_channels": [
            ("problem_domains", "https://www.agetech.space/", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "结构化问题域分类资源，手动参考",
    },
    "agetechcollaborative": {
        "name": "AgeTech Collaborative",
        "l1_domain": "agetechcollaborative.org",
        "l2_channels": [
            ("feed", "https://agetechcollaborative.org/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "AARP旗下AgeTech企业库/资讯，2026-07-09 实测直连RSS可用（原manual改直连）",
        "kind": "primary",
    },
    "maryfurlong": {
        "name": "Mary Furlong",
        "l1_domain": "maryfurlong.com",
        "l2_channels": [
            ("shop", "https://www.maryfurlong.com/shop-2/", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "企业库+高管访谈，手动入库",
    },
    "inc5000": {
        "name": "INC.5000",
        "l1_domain": "inc.com",
        "l2_channels": [
            ("inc5000_2024", "https://www.inc.com/inc5000/2024", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "每年8月出结果，健康产品/健康服务赛道",
    },
    "a2collective": {
        "name": "A2 Collective",
        "l1_domain": "a2collective.ai",
        "l2_channels": [
            ("awardees", "https://www.a2collective.ai/awardees", "manual"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "往届获奖者，已放弃，保留参考",
    },
    # === T2 Overseas — no RSS, Google News proxy ===
    "creatinganewhealthcare": {
        "name": "Creating A New Healthcare",
        "l1_domain": "creatinganewhealthcare.com",
        "l2_channels": [
            ("podcast", "https://www.creatinganewhealthcare.com/", "google_news"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "Dr. Zeev Neuwirth播客；unreliable: proxy dependent（经Google News代理，无稳定直连RSS，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    "finsmes": {
        "name": "FinSMEs",
        "l1_domain": "finsmes.com",
        "l2_channels": [
            ("home", "https://www.finsmes.com/", "google_news"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09（虽为aggregator，按用户意图升T1）
        "region": "overseas",
        "notes": "泛科技融资聚合（噪音重灾区），降级为T3仅进观察池；备胎直连RSS finsmes.com/feed",
        "kind": "aggregator",
        "fallback_rss": "https://www.finsmes.com/feed/",
    },
    "prnewswire": {
        "name": "PR Newswire",
        "l1_domain": "prnewswire.com",
        "l2_channels": [
            ("healthcare", "https://www.prnewswire.com/news-releases/healthcare-hospital-management/", "google_news"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "新闻稿平台，无RSS",
    },
    "femtechinsider": {
        "name": "FemTech Insider",
        "l1_domain": "femtechinsider.com",
        "l2_channels": [
            ("home", "https://femtechinsider.com/", "google_news"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "女性健康科技，与银发女性健康相关",
    },
    "axios_health": {
        "name": "Axios Pro Health Tech Deals",
        "l1_domain": "axios.com",
        "l2_channels": [
            ("health_tech_deals", "https://www.axios.com/pro/health-tech-deals", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "需付费，Google News代理采集摘要；unreliable: proxy dependent（经Google News代理，无稳定直连RSS，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    "hitconsultant": {
        "name": "HIT Consultant",
        "l1_domain": "hitconsultant.net",
        "l2_channels": [
            # 自主推进(2026-07-09): 原 google_news 模式在生产跑2次0条；
            # 实测站点直连RSS https://hitconsultant.net/feed/ 可达(200/rss+xml)，
            # 故改直连RSS去单点故障、稳定产数。下游行业相关度闸门仍会过滤非银发内容。
            ("feed", "https://hitconsultant.net/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "医疗IT媒体；直连RSS(原google_news代理0产出已弃)",
    },
    "pulse2": {
        "name": "Pulse 2.0",
        "l1_domain": "pulse2.com",
        "l2_channels": [
            ("home", "https://pulse2.com/", "google_news"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "泛科技创业媒体（噪音重灾区），降级为T3仅进观察池；备胎直连RSS pulse2.com/feed",
        "kind": "aggregator",
        "fallback_rss": "https://pulse2.com/feed/",
    },
    "businesswire": {
        "name": "Business Wire",
        "l1_domain": "businesswire.com",
        "l2_channels": [
            ("healthcare", "https://www.businesswire.com/portal/en/newsroom/healthcare/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "新闻稿平台，无RSS；unreliable: proxy dependent（经Google News代理，无稳定直连RSS，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    "techcrunch": {
        "name": "TechCrunch",
        "l1_domain": "techcrunch.com",
        "l2_channels": [
            ("health_biotech", "https://techcrunch.com/category/healthcare-biotech/", "google_news"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "泛科技媒体（噪音风险），降级为T3仅进观察池；备胎直连RSS techcrunch.com/feed",
        "kind": "aggregator",
        "fallback_rss": "https://techcrunch.com/feed/",
    },
    "betakit": {
        "name": "BetaKit",
        "l1_domain": "betakit.com",
        "l2_channels": [
            ("home", "https://betakit.com/", "google_news"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "加拿大泛科技媒体（噪音风险），降级为T3仅进观察池；备胎直连RSS betakit.com/feed",
        "kind": "aggregator",
        "fallback_rss": "https://betakit.com/feed/",
    },
    "coverager": {
        "name": "Coverager",
        "l1_domain": "coverager.com",
        "l2_channels": [
            ("home", "https://coverager.com/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "保险科技媒体；备胎直连RSS coverager.com/feed",
        "fallback_rss": "https://coverager.com/feed/",
    },
    "yahoofinance": {
        "name": "Yahoo Finance",
        "l1_domain": "finance.yahoo.com",
        "l2_channels": [
            ("markets", "https://finance.yahoo.com/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "雅虎财经，覆盖上市银发企业",
    },
    "modernhealthcare": {
        "name": "Modern Healthcare",
        "l1_domain": "modernhealthcare.com",
        "l2_channels": [
            ("home", "https://www.modernhealthcare.com/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "现代医疗杂志；unreliable: proxy dependent（经Google News代理，无稳定直连RSS，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    "homecaremag": {
        "name": "HomeCare Magazine",
        "l1_domain": "homecaremag.com",
        "l2_channels": [
            ("news", "https://www.homecaremag.com/news", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "居家护理杂志；unreliable: proxy dependent（经Google News代理，无稳定直连RSS，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    # === T2 Chinese sources via Google News ===
    "ageclub": {
        "name": "AgeClub",
        "l1_domain": "ageclub.net",
        "l2_channels": [
            ("google_news", "https://news.google.com/rss/search?q=site:ageclub.net+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 1,  # 用户指定T1（国内最大银发财经，相当于筛选过一次）2026-07-09
        "region": "domestic",
        "notes": "国内银发经济头部媒体；unreliable: proxy dependent（经Google News代理，无稳定直连RSS，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    "36kr_silver": {
        "name": "36氪-银发经济",
        "l1_domain": "36kr.com",
        "l2_channels": [
            ("google_news", "https://news.google.com/rss/search?q=site:36kr.com+银发+OR+养老+OR+老年+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 2,  # 用户指定T2（二手/专业平台）2026-07-09
        "region": "domestic",
        "notes": "36氪银发经济板块；unreliable: proxy dependent（经Google News代理，无稳定直连RSS，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    "vcbeat_aging": {
        "name": "动脉网-养老医疗",
        "l1_domain": "vcbeat.top",
        "l2_channels": [
            ("google_news", "https://news.google.com/rss/search?q=site:vcbeat.top+养老+OR+银发+OR+老年+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 2,
        "region": "domestic",
        "notes": "动脉网养老医疗板块，域名索引问题导致采集量低；unreliable: proxy dependent（经Google News代理，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    "silver_economy_cn": {
        "name": "Google News - 银发经济",
        "l1_domain": "news.google.com",
        "l2_channels": [
            ("silver_economy", "https://news.google.com/rss/search?q=银发经济+OR+养老+OR+老年产业+OR+健康养老+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 2,
        "region": "domestic",
        "notes": "Google News中文银发经济关键词聚合；unreliable: proxy dependent（本身即GN聚合，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    # === T3 Broad overseas ===
    "silver_economy_news": {
        "name": "Google News - Silver Economy",
        "l1_domain": "news.google.com",
        "l2_channels": [
            ("broad", "https://news.google.com/rss/search?q=%22senior+care%22+OR+%22home+health%22+OR+%22aging+technology%22+OR+%22AgeTech%22+OR+%22elderly+care%22+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "宽覆盖海外银发经济新闻；unreliable: proxy dependent（本身即GN聚合，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    "aging_tech_news": {
        "name": "Google News - Aging Tech",
        "l1_domain": "news.google.com",
        "l2_channels": [
            ("broad", "https://news.google.com/rss/search?q=%22aging+in+place%22+OR+%22senior+living%22+OR+%22elderly+care%22+OR+%22long-term+care%22+OR+%22assisted+living%22+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "宽覆盖Aging Tech新闻；unreliable: proxy dependent（本身即GN聚合，仅靠Bing News二级兜底）",
        "unreliable": "proxy dependent",
    },
    # === 一手/原始信源补充（2026-07-08 深挖）===
    # 行业协会 / 政府 / 监管原始发布：直接监控其域名，经 Google News 代理，
    # 拿到"一手"原文而非二手编译。覆盖 AgeClub 等二手媒体常引用的原始出处。
    "leadingage": {
        "name": "LeadingAge",
        "l1_domain": "leadingage.org",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:leadingage.org+senior+OR+aging+OR+%22long-term+care%22+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "美国老年服务行业协会，一手行业动态/政策/研究",
        "news_window_days": 30,
        "kind": "primary",
    },
    "argentum": {
        "name": "Argentum",
        "l1_domain": "argentum.org",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:argentum.org+senior+living+OR+%22assisted+living%22+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "美国养老社区协会，一手行业资讯",
        "news_window_days": 30,
        "kind": "primary",
    },
    "nic_seniors": {
        "name": "NIC (Seniors Housing & Care)",
        "l1_domain": "nic.org",
        "l2_channels": [
            ("research", "https://news.google.com/rss/search?q=site:nic.org+%22senior+housing%22+OR+%22seniors+housing%22+OR+care+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "美国养老地产与投资研究中心，一手数据与报告；unreliable: proxy dependent（直连RSS未验证，经Google News代理，仅靠Bing News二级兜底）",
        "news_window_days": 30,
        "kind": "primary",
        "unreliable": "proxy dependent",
    },
    "ncoa": {
        "name": "NCOA",
        "l1_domain": "ncoa.org",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:ncoa.org+older+adult+OR+%22aging+well%22+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "美国国家老龄化委员会，一手政策与倡导；unreliable: proxy dependent（直连RSS未验证，经Google News代理，仅靠Bing News二级兜底）",
        "news_window_days": 30,
        "kind": "primary",
        "unreliable": "proxy dependent",
    },
    "mca_gov": {
        "name": "民政部",
        "l1_domain": "mca.gov.cn",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:mca.gov.cn+养老+OR+老年+OR+老龄+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 1,
        "region": "domestic",
        "notes": "民政部一手政策/通知（养老/老龄一手源）；unreliable: proxy dependent（gov.cn直连RSS受限，经Google News代理，仅靠Bing News二级兜底）",
        "news_window_days": 30,
        "kind": "primary",
        "unreliable": "proxy dependent",
    },
    "gov_policy": {
        "name": "国务院政策(银发)",
        "l1_domain": "gov.cn",
        "l2_channels": [
            ("zhengce", "https://news.google.com/rss/search?q=site:gov.cn+%22银发经济%22+OR+%22养老服务%22+OR+%22老龄%22+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 1,
        "region": "domestic",
        "notes": "国务院政策文件一手源（银发经济/养老）；unreliable: proxy dependent（gov.cn直连RSS受限，经Google News代理，仅靠Bing News二级兜底）",
        "news_window_days": 30,
        "kind": "primary",
        "unreliable": "proxy dependent",
    },
    "cncaprc": {
        "name": "中国老龄协会",
        "l1_domain": "cncaprc.gov.cn",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:cncaprc.gov.cn+老龄+OR+老年+OR+养老+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 2,
        "region": "domestic",
        "notes": "中国老龄协会一手资讯；unreliable: proxy dependent（gov.cn直连RSS受限，经Google News代理，仅靠Bing News二级兜底）",
        "news_window_days": 30,
        "kind": "primary",
        "unreliable": "proxy dependent",
    },
    # === 新增：一手 VC 博客 + YouTube 热门视频（2026-07-08 补全缺口）===
    "third_act": {
        "name": "Third Act Ventures",
        "l1_domain": "thirdact.vc",
        "l2_channels": [
            ("insights", "https://news.google.com/rss/search?q=site:thirdact.vc+when:30d&hl=en-US", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "专注 aging 的早期 VC，一手投资逻辑；unreliable: proxy dependent（经Google News代理，仅靠Bing News二级兜底）",
        "kind": "vc",
        "unreliable": "proxy dependent",
    },
    "sevenwire": {
        "name": "7Wire Ventures",
        "l1_domain": "7wireventures.com",
        "l2_channels": [
            ("perspectives", "https://app.sandhill.io/feeds/7wire-ventures", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "医疗/老龄化 VC，perspectives 一手洞察(RSS)",
        "kind": "vc",
    },
    "khosla": {
        "name": "Khosla Ventures",
        "l1_domain": "khoslaventures.com",
        "l2_channels": [
            ("insights", "https://news.google.com/rss/search?q=site:khoslaventures.com+when:30d&hl=en-US", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "重仓 longevity/healthspan 的头部 VC；备胎直连RSS khoslaventures.com/feed",
        "kind": "vc",
        "fallback_rss": "https://www.khoslaventures.com/feed/",
    },
    "youtube_silver": {
        "name": "YouTube - 银发热门视频",
        "l1_domain": "youtube.com",
        "l2_channels": [
            ("the_villages", "https://news.google.com/rss/search?q=The+Villages+OR+senior+living+OR+retirement+community+site:youtube.com+when:1y&hl=en-US", "google_news"),
            ("aging_tech", "https://news.google.com/rss/search?q=aging+tech+OR+age+tech+site:youtube.com+when:30d&hl=en-US", "google_news"),
            ("home_health", "https://news.google.com/rss/search?q=Home+Health+Care+News+OR+homecare+OR+fiercehealthcare+site:youtube.com+when:30d&hl=en-US", "google_news"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "监控银发相关 YouTube 热门视频(含 The Villages C端爆款)；unreliable: proxy dependent（经Google News代理，仅靠Bing News二级兜底）",
        "kind": "video",
        "unreliable": "proxy dependent",
    },
    # === 新增：已验证直连 RSS 一手源（消除 Google News 单点依赖，2026-07-09）===
    # 这些源整站 feed，经 is_relevant 两级闸门过滤泛噪音。
    "longevity_tech": {
        "name": "Longevity Technology",
        "l1_domain": "longevity.technology",
        "l2_channels": [
            ("feed", "https://www.longevity.technology/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "长寿/老龄化科技/融资，2026-07-09 实测直连RSS可用（最对口长寿经济源）",
        "kind": "primary",
    },
    "fierce_biotech": {
        "name": "Fierce Biotech",
        "l1_domain": "fiercebiotech.com",
        "l2_channels": [
            ("feed", "https://www.fiercebiotech.com/rss/xml", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "生物科技融资一线媒体，整站RSS直连（银发生物科技强补充）",
    },
    "eu_startups": {
        "name": "EU-Startups",
        "l1_domain": "eu-startups.com",
        "l2_channels": [
            ("feed", "https://www.eu-startups.com/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "欧洲创业/融资一线媒体，直连RSS（欧洲银发创业补充）",
    },
    "silicon_canals": {
        "name": "Silicon Canals",
        "l1_domain": "siliconcanals.com",
        "l2_channels": [
            ("feed", "https://siliconcanals.com/feed/", "rss"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "欧洲科技/融资媒体，直连RSS（补充，降级T3仅进观察池）",
    },
    # === 新增：2026-07-09 增量信源发现（已验证直连 RSS 6 源）===
    "weekly_source_au": {
        "name": "The Weekly Source",
        "l1_domain": "theweeklysource.com.au",
        "l2_channels": [
            ("feed", "https://www.theweeklysource.com.au/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "澳大利亚养老/老年护理行业媒体，直连RSS（含并购、运营商扩张交易稿）",
        "news_window_days": 30,
        "kind": "primary",
    },
    "care_england": {
        "name": "Care England",
        "l1_domain": "careengland.org.uk",
        "l2_channels": [
            ("feed", "https://www.careengland.org.uk/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "英国成人社会照护头部协会官方源，直连RSS",
        "news_window_days": 30,
        "kind": "primary",
    },
    "care_provider_alliance": {
        "name": "Care Provider Alliance",
        "l1_domain": "careprovideralliance.org.uk",
        "l2_channels": [
            ("feed", "https://careprovideralliance.org.uk/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "英国照护提供者联盟官方源，直连RSS（与Care England互补）",
        "news_window_days": 30,
        "kind": "primary",
    },
    "koureisha_jutaku": {
        "name": "週刊 高齢者住宅新聞 Online",
        "l1_domain": "koureisha-jutaku.com",
        "l2_channels": [
            ("feed", "https://www.koureisha-jutaku.com/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "日本老年住宅/养老地产/照护经营报纸，直连RSS（日语源，需确认中日混排处理）",
        "lang": "ja",
        "news_window_days": 30,
        "kind": "primary",
    },
    "lifespan_io": {
        "name": "Lifespan.io",
        "l1_domain": "lifespan.io",
        "l2_channels": [
            ("feed", "https://www.lifespan.io/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "长寿科技研究媒体（LEV基金会），直连RSS（与Longevity.Technology研究视角互补）",
        "kind": "primary",
    },
    "tech_eu": {
        "name": "Tech.eu",
        "l1_domain": "tech.eu",
        "l2_channels": [
            ("feed", "https://tech.eu/feed/", "rss"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "泛欧科技/VC融资媒体，直连RSS（噪音偏大，仅进观察池T3）",
    },
    # === 新增：2026-07-10 一手信源补充（T39，C2）===
    # 均为"一手/原始发布"机构（协会/政府科研/慈善），区别于二手媒体。
    # 沙箱对其直连RSS验证失败（AARP 307跳转HTML、alz.org 404、nia.nih.gov 000被拦截、
    # ageuk.org.uk 404），故先按现有 primary 源惯例经 Google News 代理接入；
    # 生产环境待验证直连 feed（标注"待生产验证"）。
    "aarp": {
        "name": "AARP",
        "l1_domain": "aarp.org",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:aarp.org+aging+OR+senior+OR+%22older+adult%22+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "美国最大老龄非营利组织，一手研究/倡导/媒体；直连RSS沙箱未验证(307→HTML)，先经Google News代理接入，生产环境待验证直连feed",
        "news_window_days": 30,
        "kind": "primary",
    },
    "alz_association": {
        "name": "Alzheimer's Association",
        "l1_domain": "alz.org",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:alz.org+Alzheimer+OR+dementia+OR+caregiving+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "阿尔茨海默协会，一手痴呆研究/政策/照护；直连RSS沙箱404未验证，先经Google News代理接入，生产环境待验证直连feed",
        "news_window_days": 30,
        "kind": "primary",
    },
    "nia_nih": {
        "name": "NIA (NIH)",
        "l1_domain": "nia.nih.gov",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:nia.nih.gov+aging+OR+%22older+adult%22+OR+geriatric+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "美国国家衰老研究所，一手科研/临床指南；直连feed沙箱000(被拦截)未验证，先经Google News代理接入，生产环境待验证直连feed",
        "news_window_days": 30,
        "kind": "primary",
    },
    "age_uk": {
        "name": "Age UK",
        "l1_domain": "ageuk.org.uk",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:ageuk.org.uk+older+people+OR+ageing+OR+care+when:7d&hl=en-GB", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "英国最大老龄慈善机构，一手研究/倡导；直连RSS沙箱404未验证，先经Google News代理接入，生产环境待验证直连feed",
        "news_window_days": 30,
    # === 新增：2026-07-15 信源治理批次（研究员实查+入库）===
    },
    "silvereco": {
        "name": "Silvereco",
        "l1_domain": "silvereco.fr",
        "l2_channels": [
            ("actualites", "https://www.silvereco.fr/actualites/", "google_news"),
            ("acteurs", "https://www.silvereco.fr/acteurs-silver-economie/", "google_news"),
            ("feed", "https://www.silvereco.fr/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "法国银发经济垂直门户；有直采RSS(actualites新闻/acteurs企业名录)；反查AGECLUB得来",
        "lang": "fr",
        "kind": "primary",
    },
    "tracxn_age_tech": {
        "name": "Tracxn Age Tech",
        "l1_domain": "tracxn.com",
        "l2_channels": [
            ("us", "https://tracxn.com/d/explore/age-tech-startups-in-united-states/__F1W7P9wFbrSgBBr3Gz5jcFFD5jxsRPSVQv_u10Oa4I0", "google_news"),
            ("germany", "https://tracxn.com/d/explore/age-tech-startups-in-germany/__hdRFJQR2d3H7Z_B_ZXB9MWAQ3q_JvQ91qSIGRIeB5yY/companies", "google_news"),
        ],
        "tier": 2,  # 企业数据库非媒体+付费墙遮金额，按T2入库；作头部公司发现器
        "region": "overseas",
        "notes": "全球银发科技企业数据库(按地区分榜,美国1165家);金额被付费墙遮$*****;点开深链可能弹双标签页(站点重定向),关掉一个即可",
        "kind": "database",
    },
    "seedtable_elder": {
        "name": "Seedtable Elder Tech",
        "l1_domain": "seedtable.com",
        "l2_channels": [
            ("elder_technology", "https://seedtable.com/startups-elder-technology", "google_news"),
            ("elder_care", "https://www.seedtable.com/best-elder-care-startups", "google_news"),
        ],
        "tier": 3,  # 噪音偏大(混长寿biotech)，仅宽覆盖
        "region": "overseas",
        "notes": "老年科技排名榜;ageing子榜混长寿biotech噪音,只用前两个干净子榜",
        "kind": "ranking",
    },
    "being_patient": {
        "name": "Being Patient",
        "l1_domain": "beingpatient.com",
        "l2_channels": [
            ("alzheimers", "https://beingpatient.com/alzheimers-disease/", "google_news"),
        ],
        "tier": 2,  # 认知症垂直高质量媒体
        "region": "overseas",
        "notes": "认知症/脑健康垂直媒体(前WSJ编辑创办);认知症赛道高质量入口",
        "kind": "primary",
    },
    "addf_portfolio": {
        "name": "ADDF Diagnostics Accelerator",
        "l1_domain": "alzdiscovery.org",
        "l2_channels": [
            ("portfolio", "https://www.alzdiscovery.org/research-and-grants/diagnostics-accelerator/portfolio", "google_news"),
        ],
        "tier": 2,  # 认知症投融资反查利器
        "region": "overseas",
        "notes": "阿尔茨海默药物发现基金会诊断加速器被投组合;认知症投融资反查利器/企业发现器",
        "kind": "database",
    },
    "dementia_care_central": {
        "name": "Dementia Care Central",
        "l1_domain": "dementiacarecentral.com",
        "l2_channels": [
            ("aboutdementia", "https://www.dementiacarecentral.com/aboutdementia", "google_news"),
        ],
        "tier": 3,  # 偏工具/资源，非新闻流
        "region": "overseas",
        "notes": "照护者向认知症知识库/资源指南",
        "kind": "guide",
    },
    "alzheimers_net": {
        "name": "Alzheimers.net",
        "l1_domain": "alzheimers.net",
        "l2_channels": [
            ("home", "https://www.alzheimers.net/", "google_news"),
        ],
        "tier": 3,  # 含机构导流，噪音中
        "region": "overseas",
        "notes": "阿尔茨海默资讯+记忆照护机构目录(含商业导流,噪音中)",
        "kind": "primary",
    },
    "hearingtracker": {
        "name": "HearingTracker",
        "l1_domain": "hearingtracker.com",
        "l2_channels": [
            ("rechargeable", "https://hearingtracker.com/rechargeable-hearing-aids", "google_news"),
        ],
        "tier": 3,  # 助听细分产品发现器
        "region": "overseas",
        "notes": "助听器实验室声学测评+年度榜单;助听细分产品发现器",
        "kind": "ranking",
    },
    # ===== W1 北美 × 医疗健康+养老服务 候选源（2026-07-16 入库，研究员判断档位）=====
    "seniorcare_investor": {
        "name": "Irving Levin Associates – The SeniorCare Investor",
        "l1_domain": "levinassociates.com",
        "l2_channels": [
            ("seniorcare", "https://seniorcare.levinassociates.com/", "manual"),
        ],
        "tier": 1,  # 北美养老/护理 M&A 最权威一手交易情报源
        "region": "overseas",
        "notes": "追踪自1993年 35,000+ 笔长期护理 M&A；直接产出收购并购事件+估值/交易量数据（T1 一手交易源）",
        "kind": "transaction",
    },
    "braff_group": {
        "name": "The Braff Group",
        "l1_domain": "thebraffgroup.com",
        "l2_channels": [
            ("transaction", "https://thebraffgroup.com/transaction/", "manual"),
        ],
        "tier": 1,  # 居家护理/临终关怀 M&A 一手源
        "region": "overseas",
        "notes": "专注 home health/care/hospice M&A，已完成近 400 笔；强收购信号（T1 一手交易源）",
        "kind": "transaction",
    },
    "skilled_nursing_news": {
        "name": "Skilled Nursing News – Finance",
        "l1_domain": "skillednursingnews.com",
        "l2_channels": [
            ("finance", "https://skillednursingnews.com/category/finance/", "manual"),
        ],
        "tier": 1,  # SNF 并购/融资高频频道
        "region": "overseas",
        "notes": "日更 SNF 垂直媒体，含 Dealbook 专栏；补齐库内缺失的专业护理院并购/融资频道（T1）",
        "kind": "media",
    },
    "behavioral_health_business": {
        "name": "Behavioral Health Business – M&A",
        "l1_domain": "bhbusiness.com",
        "l2_channels": [
            ("ma", "https://bhbusiness.com/category/finance/ma/", "manual"),
        ],
        "tier": 1,  # 行为健康并购事件源
        "region": "overseas",
        "notes": "行为健康 exec 媒体，M&A 专栏周更（含 ABA/心理/物质使用治疗并购），库内该细分空白（T1）",
        "kind": "media",
    },
    "rock_health": {
        "name": "Rock Health – Insights",
        "l1_domain": "rockhealth.com",
        "l2_channels": [
            ("insights", "https://rockhealth.com/insights/", "manual"),
        ],
        "tier": 1,  # 数字健康融资第一手研究
        "region": "overseas",
        "notes": "数字健康融资权威；半年度 funding overview，AI/远程/临床 workflow 细分（T1 一手研究源）",
        "kind": "research",
    },
    "medcity_news": {
        "name": "MedCity News – Health Tech",
        "l1_domain": "medcitynews.com",
        "l2_channels": [
            ("health_tech", "https://medcitynews.com/category/health-tech/", "manual"),
        ],
        "tier": 2,  # 数字健康初创融资/并购快讯
        "region": "overseas",
        "notes": "健康科技创新媒体，Health Tech 频道日更（初创/融资/并购），与 age-tech 交叉（T2）",
        "kind": "media",
    },
    "healthcare_it_news": {
        "name": "Healthcare IT News – News",
        "l1_domain": "healthcareitnews.com",
        "l2_channels": [
            ("news", "https://www.healthcareitnews.com/news", "manual"),
        ],
        "tier": 2,  # 老年护理科技政策与产品
        "region": "overseas",
        "notes": "医疗 IT 媒体（EHR/互操作/远程/AI），日更；老年护理科技政策与产品动态（T2）",
        "kind": "media",
    },
    "massdevice": {
        "name": "MassDevice – Mergers & Acquisitions",
        "l1_domain": "massdevice.com",
        "l2_channels": [
            ("ma", "https://www.massdevice.com/category/business_financial_news/mergers_acquisitions/", "manual"),
        ],
        "tier": 1,  # 康复辅具/听力/器械并购源
        "region": "overseas",
        "notes": "医疗器械商业媒体，M&A 归档 300+ 页；康复辅具/听力/器械并购事件源（T1）",
        "kind": "media",
    },
    "medtech_dive": {
        "name": "MedTech Dive – Digital Health",
        "l1_domain": "medtechdive.com",
        "l2_channels": [
            ("digital_health", "https://www.medtechdive.com/topic/digital-health/", "manual"),
        ],
        "tier": 2,  # 数字健康融资/并购
        "region": "overseas",
        "notes": "Industry Dive 旗下，Digital Health 频道日更，覆盖融资与 M&A（可穿戴、CMS 支付、IPO）（T2）",
        "kind": "media",
    },
    "hearing_review": {
        "name": "The Hearing Review – Industry News",
        "l1_domain": "hearingreview.com",
        "l2_channels": [
            ("industry_news", "https://www.hearingreview.com/inside-hearing/industry-news/", "manual"),
        ],
        "tier": 2,  # 助听器/听力细分
        "region": "overseas",
        "notes": "听力行业贸易杂志，行业新闻档案含 M&A/销售数据；助听器/听力细分并购与产品动态（T2）",
        "kind": "media",
    },
    "dtx_alliance": {
        "name": "Digital Therapeutics Alliance – Public Newsletter",
        "l1_domain": "dtxalliance.org",
        "l2_channels": [
            ("newsletter", "https://dtxalliance.org/category/public-newsletter", "manual"),
        ],
        "tier": 2,  # 数字疗法一手协会
        "region": "overseas",
        "notes": "全球数字疗法非营利贸易协会，成员 17 国；支付方/CMS 编码/认证，反查头部生态（T2 协会）",
        "kind": "association",
    },
    "nahc": {
        "name": "National Alliance for Care at Home (NAHC) – Newsroom",
        "l1_domain": "nahc.org",
        "l2_channels": [
            ("newsroom", "https://nahc.org/newsroom", "manual"),
        ],
        "tier": 1,  # 美居家照护最大协会一手源
        "region": "overseas",
        "notes": "美居家照护最大协会（原 NAHC+NHPCO 合并），10,000+ 机构会员；居家护理/临终关怀一手政策与交易动态（T1）",
        "kind": "association",
    },
    "carp": {
        "name": "CARP – Advocacy/News",
        "l1_domain": "carp.ca",
        "l2_channels": [
            ("advocacy", "https://www.carp.ca/advocacy/", "manual"),
        ],
        "tier": 2,  # 加拿大银发政策一手源
        "region": "overseas",
        "notes": "加拿大最大退休者倡导组织，250,000+ 会员；加拿大银发政策/长期护理一手源，补北美加拿大视角（T2）",
        "kind": "association",
    },
    "hcaoa": {
        "name": "Home Care Association of America (HCAOA) – News Releases",
        "l1_domain": "hcaoa.org",
        "l2_channels": [
            ("news_releases", "https://www.hcaoa.org/news-releases.html", "manual"),
        ],
        "tier": 2,  # 家庭照护一手政策/会员并购动态（W1 候选时 Cloudflare 拦截，研究员判断 T2 入库）
        "region": "overseas",
        "notes": "美家庭照护机构协会；家庭照护一手政策/会员并购动态（T2 协会；URL 经搜索确认存在，直连待复核）",
        "kind": "association",
    },
    "seniorplanet": {
        "name": "Senior Planet",
        "l1_domain": "seniorplanet.org",
        "l2_channels": [
            ("articles", "https://seniorplanet.org/articles/", "manual"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "美国活力老人科技/旅行/兴趣/反诈一手内容社区",
        "ingest_time": "2026-07-16",
    },
    "getsetup": {
        "name": "GetSetUp",
        "l1_domain": "getsetup.io",
        "l2_channels": [
            ("blog", "https://blog.getsetup.io/", "manual"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "全球最大老年直播课平台，适老在线教育+社交标杆",
        "ingest_time": "2026-07-16",
    },
    "roadscholar": {
        "name": "Road Scholar",
        "l1_domain": "roadscholar.org",
        "l2_channels": [
            ("blog", "https://www.roadscholar.org/blog", "manual"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "全美最大老年教育旅行机构，银发游学/旅居标杆",
        "ingest_time": "2026-07-16",
    },
    "stitch": {
        "name": "Stitch",
        "l1_domain": "stitch.net",
        "l2_channels": [
            ("blog", "https://www.stitch.net/blog", "manual"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "全球50+交友/活动社区，先交友后恋爱模式",
        "ingest_time": "2026-07-16",
    },
    "sixtyandme": {
        "name": "Sixty and Me",
        "l1_domain": "sixtyandme.com",
        "l2_channels": [
            ("health_fitness", "https://sixtyandme.com/health-and-fitness-over-60/", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "全球女性活力老人(60+)生活/旅行/健康社区",
        "ingest_time": "2026-07-16",
    },
    "brainhq": {
        "name": "BrainHQ",
        "l1_domain": "brainhq.com",
        "l2_channels": [
            ("news", "https://www.brainhq.com/news", "manual"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "适老脑力/认知训练科学内容",
        "ingest_time": "2026-07-16",
    },
    "papa_src": {
        "name": "Papa",
        "l1_domain": "papa.com",
        "l2_channels": [
            ("resources", "https://www.papa.com/resources", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "伴老/companion care 平台，代际社交内容（企业作源偏PR）",
        "ingest_time": "2026-07-16",
    },
    "cogenerate": {
        "name": "CoGenerate (原 Encore.org)",
        "l1_domain": "cogenerate.org",
        "l2_channels": [
            ("stories", "https://cogenerate.org/stories/", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "退休再就业/第二职业/代际共创，老有所为标杆",
        "ingest_time": "2026-07-16",
    },
    "restless": {
        "name": "Rest Less",
        "l1_domain": "restless.co.uk",
        "l2_channels": [
            ("home", "https://restless.co.uk/", "manual"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "英国50+一站式门户（工作/旅行/理财/交友）",
        "ingest_time": "2026-07-16",
    },
    "silversurfers": {
        "name": "Silversurfers",
        "l1_domain": "silversurfers.com",
        "l2_channels": [
            ("home", "https://www.silversurfers.com/", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "英国最大50+在线社区，UGC活力老人内容",
        "ingest_time": "2026-07-16",
    },
    "silvertraveladvisor": {
        "name": "Silver Travel Advisor",
        "l1_domain": "silvertraveladvisor.com",
        "l2_channels": [
            ("reviews", "https://www.silvertraveladvisor.com/escorted-tour-reviews", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "专做50+独立旅行评测，用户真实点评模式",
        "ingest_time": "2026-07-16",
    },
    "primewomen": {
        "name": "Prime Women",
        "l1_domain": "primewomen.com",
        "l2_channels": [
            ("entertainment", "https://primewomen.com/category/entertainment/", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "美国成熟女性时尚/旅行/理财媒体",
        "ingest_time": "2026-07-16",
    },
    "halmek": {
        "name": "ハルメク Halmek",
        "l1_domain": "halmek.co.jp",
        "l2_channels": [
            ("magazine", "https://magazine.halmek.co.jp/", "manual"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "日本50+女性杂志标杆，订阅制+活动+旅行会员生态",
        "ingest_time": "2026-07-16",
    },
    "zsjc": {
        "name": "全国シルバー人材センター (zsjc)",
        "l1_domain": "zsjc.or.jp",
        "l2_channels": [
            ("oshirase", "https://www.zsjc.or.jp/oshirase/old", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "日本老有所为官方协会，再就业/志愿一手数据",
        "ingest_time": "2026-07-16",
    },
    "laoren": {
        "name": "快乐老人报/枫网",
        "l1_domain": "laoren.com",
        "l2_channels": [
            ("home", "http://www.laoren.com/", "manual"),
        ],
        "tier": 1,
        "region": "domestic",
        "notes": "国内老年门户标杆，八大频道+论坛+旅游+大学",
        "ingest_time": "2026-07-16",
    },
    "hongsong": {
        "name": "红松 Hongsong",
        "l1_domain": "hongsong.tuixiu.com",
        "l2_channels": [
            ("about", "https://hongsong.tuixiu.com/about", "manual"),
        ],
        "tier": 1,
        "region": "domestic",
        "notes": "国内退休文娱直播课社区头部",
        "ingest_time": "2026-07-16",
    },
    "tangdou": {
        "name": "糖豆",
        "l1_domain": "tangdou.com",
        "l2_channels": [
            ("home", "https://www.tangdou.com/", "manual"),
        ],
        "tier": 1,
        "region": "domestic",
        "notes": "国内最大中老年运动/广场舞社区",
        "ingest_time": "2026-07-16",
    },
    "meipian": {
        "name": "美篇",
        "l1_domain": "meipian.cn",
        "l2_channels": [
            ("home", "https://www.meipian.cn/", "manual"),
        ],
        "tier": 2,
        "region": "domestic",
        "notes": "国内中老年图文创作/兴趣社群",
        "ingest_time": "2026-07-16",
    },
    "caua": {
        "name": "中国老年大学协会 (CAUA)",
        "l1_domain": "caua1988.com",
        "l2_channels": [
            ("home", "http://www.caua1988.com/", "manual"),
        ],
        "tier": 2,
        "region": "domestic",
        "notes": "国内老年教育官方协会，政策+会员动态一手源",
        "ingest_time": "2026-07-16",
    },
    "silversneakers": {
        "name": "SilverSneakers",
        "l1_domain": "silversneakers.com",
        "l2_channels": [
            ("blog", "https://www.silversneakers.com/blog", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "美国老年运动健身社区标杆，健身即社交",
        "ingest_time": "2026-07-16",
    },
    "venturebeat_ai": {
        "name": "VentureBeat – AI",
        "l1_domain": "venturebeat.com",
        "l2_channels": [
            ("ai", "https://venturebeat.com/ai/", "manual"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "通用大模型在医疗/养老场景落地报道，可反查OpenAI/Google银发栏目",
        "ingest_time": "2026-07-16",
    },
    "mit_tr_ai": {
        "name": "MIT Technology Review – AI",
        "l1_domain": "technologyreview.com",
        "l2_channels": [
            ("ai", "https://www.technologyreview.com/topic/artificial-intelligence/", "manual"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "LLM/具身智能前沿与伦理深度文，反常识素材密度高",
        "ingest_time": "2026-07-16",
    },
    "aging2": {
        "name": "Aging2.0 (Global Healthcare Innovation)",
        "l1_domain": "aging2.com",
        "l2_channels": [
            ("news_gn", "https://news.google.com/rss/search?q=site:aging2.com+aging+OR+senior+OR+agetech&hl=en-US", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "全球AgeTech创新者社区，一手创业/政策信号；GN代理列表页",
        "ingest_time": "2026-07-16",
    },
    "therobotreport": {
        "name": "The Robot Report",
        "l1_domain": "therobotreport.com",
        "l2_channels": [
            ("robotics_news", "https://www.therobotreport.com/robotics-news/", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "养老/护理/人形机器人一手新闻与融资M&A",
        "ingest_time": "2026-07-16",
    },
    "wearabletech": {
        "name": "Wearable Technologies",
        "l1_domain": "wearable-technologies.com",
        "l2_channels": [
            ("news", "https://wearable-technologies.com/news-list", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "AI眼镜/可穿戴/助听硬件一手产品与融资",
        "ingest_time": "2026-07-16",
    },
    "agewell": {
        "name": "AGE-WELL",
        "l1_domain": "agewell-nce.ca",
        "l2_channels": [
            ("news", "https://agewell-nce.ca/news", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "加拿大技术适老研究网络，AI跌倒/认知症/语音银行一手研究",
        "ingest_time": "2026-07-16",
    },
    "marktechpost": {
        "name": "MarkTechPost",
        "l1_domain": "marktechpost.com",
        "l2_channels": [
            ("ai", "https://marktechpost.com/category/artificial-intelligence/", "manual"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "医疗/养老垂直大模型、Agent技术进展译介",
        "ingest_time": "2026-07-16",
    },
    "ieee_spectrum_robotics": {
        "name": "IEEE Spectrum – Robotics",
        "l1_domain": "spectrum.ieee.org",
        "l2_channels": [
            ("robotics", "https://spectrum.ieee.org/robotics", "manual"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "具身智能/人形机器人学术+产业（含日本护理机器人）",
        "ingest_time": "2026-07-16",
    },
    "robohub": {
        "name": "Robohub",
        "l1_domain": "robohub.org",
        "l2_channels": [
            ("home", "https://robohub.org/", "manual"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "机器人社区聚合，老年护理机器人研究/观点",
        "ingest_time": "2026-07-16",
    },
    "thedecoder": {
        "name": "The Decoder",
        "l1_domain": "the-decoder.com",
        "l2_channels": [
            ("home", "https://the-decoder.com/", "manual"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "欧洲视角AI大模型/代理新闻，可反查healthcare LLM落地",
        "ingest_time": "2026-07-16",
    },
    "medicalfuturist": {
        "name": "The Medical Futurist",
        "l1_domain": "medicalfuturist.com",
        "l2_channels": [
            ("ai", "https://medicalfuturist.com/category/artificial-intelligence", "manual"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "AI医疗（诊断/早筛/数字疗法/手术机器人）深度解读",
        "ingest_time": "2026-07-16",
    },
    "statnews": {
        "name": "STAT News – Health Tech",
        "l1_domain": "statnews.com",
        "l2_channels": [
            ("healthtech_gn", "https://news.google.com/rss/search?q=site:statnews.com+AI+OR+healthcare+technology&hl=en-US", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "医疗AI政策/支付/FDA一手报道；GN代理列表页",
        "ingest_time": "2026-07-16",
    },
    "magnifyventures": {
        "name": "Magnify Ventures",
        "l1_domain": "magnifyventures.com",
        "l2_channels": [
            ("home", "https://magnifyventures.com/", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "早期VC，care-economy基金；⚠️入库前需复核实际投资主题（公开站现强调online education）",
        "ingest_time": "2026-07-16",
    },
    "counterpoint": {
        "name": "Counterpoint Research",
        "l1_domain": "counterpointresearch.com",
        "l2_channels": [
            ("insights", "https://counterpointresearch.com/en/insights/", "manual"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "可穿戴/边缘AI市场量化数据，反常识数据素材",
        "ingest_time": "2026-07-16",
    },
}

# ================================================================
# 5. DATA COLLECTION & FILTERING LOGIC
# ================================================================
# (Documented here, rendered in about.html)
#
# === What gets collected ===
# T1 sources (tier=1): always collected, full text when possible
# T2 sources (tier=2): collected, summary only
# T3 sources (tier=3): collected, used for relevance pre-filter only
#
# === Why these articles (not others) ===
# Relevance pre-filter: article must match RELEVANCE_KEYWORDS (English or Chinese)
# Irrelevance filter: article matching IRRELEVANT_KEYWORDS is discarded
# Geographic filter: articles tagged "domestic" come from Chinese sources;
#   "overseas" from overseas sources. Region is determined by source, not content.
#
# === Scoring (paused, field reserved) ===
# Score dimensions: industry(35%) + signal(30%) + writing(20%) + timeliness(15%)
# Currently PAUSED — score fields exist in data but are not displayed.
# Once re-enabled: >=7.0 -> star(high-value), 5.0-6.9 -> watch
#
# === Update frequency ===
# Scheduled: daily at 07:00 (Asia/Shanghai)
# Lookback window: past 7 days
# Estimated token cost per run: ~15-25K tokens (collector ~10K + scorer ~5-15K)

# === Overseas source names (for region detection in UI) ===
OVERSEAS_SOURCE_NAMES = set(
    s["name"] for s in SOURCES.values() if s.get("region") == "overseas"
)

# === Relevance keywords ===
RELEVANCE_KEYWORDS = [
    "senior", "elderly", "aging", "age tech", "agetech", "older adult",
    "older adults", "aging population", "silver economy",
    "home care", "home health", "hospice", "assisted living",
    "long-term care", "long term care", "nursing home",
    "caregiver", "caregiving", "cognitive", "dementia", "alzheimer",
    "medicare", "medicaid", "retirement", "pace program",
    "value-based care", "social determinants",
    # Funding keywords
    "funding", "raises", "raises series", "investment", "acquisition",
    "acquires", "merger", "ipo", "seed round", "series a", "series b",
    "series c", "venture", "startup",
    # Chinese
    "银发", "养老", "老年", "老龄化", "长者", "退休",
    "居家护理", "居家照护", "康复", "慢病", "认知症", "痴呆",
    "阿尔茨海默", "失智", "失能", "适老", "长寿",
    "护理院", "养老院", "敬老院", "养老社区",
    "康养", "医养", "助老", "陪护", "康护",
    "融资", "收购", "并购", "投资", "IPO", "上市",
    "A轮", "B轮", "C轮", "天使轮", "种子轮",
]

CN_RELEVANCE_KEYWORDS = [
    "银发", "养老", "老年", "老龄化", "长者", "退休",
    "居家护理", "居家照护", "康复", "慢病", "认知症",
    "康养", "医养", "助老", "陪护",
]

# === 反向词（初筛强剔除）===
# 2026-07-09 用户建议"反向词删掉（可能有老年游戏/老年消费/老年平板）"：
# 原列表含 child/children/teen/adolescent/infant 等【泛词】，会误杀
#   "老年游戏/老年平板/老年消费" 这类正经银发选题 —— 故删除。
# 只保留【明确儿科/孕产】词（与老年人群硬冲突、绝不会是银发选题）：
#   pediatric/pediatrics/pregnancy/maternity/neonatal。
# 注意：这些词仍被 IRRELEVANT_KEYWORDS 在 is_relevant 中强剔除；
# 老年游戏/老年平板/老年消费 现在能正常进入（它们不含上述儿科词）。
IRRELEVANT_KEYWORDS = [
    "pediatric", "pediatrics", "pregnancy", "maternity", "neonatal",
]


# ================================================================
# 5b. 跨源 / 跨周零成本去重（在"模型之前"拦截重复文章）
# ----------------------------------------------------------------
# 目的：同一篇文章被多个 RSS/Google News 源重复收录时，只让第一条进入
#       后续流程（含最强模型调用），其余直接拦截 —— 0 模型成本去重。
# 做法：归一化标题（去空格/标点/大小写）+ URL 哈希 作为签名，存到
#       data/dedup_store.json（跨运行持久化，2 周滑动窗口）。
# 与 is_relevant 的关系：先 is_relevant 做银发相关性初筛，再去重，
#       最后才进模型 —— 去重是相关性之后的第二道 0 成本闸门。
# ================================================================
class DedupStore:
    PATH = os.path.join(DATA_DIR, "dedup_store.json")
    WINDOW_DAYS = 14  # 2 周内同一篇文章视为重复

    def __init__(self):
        self.seen = {}  # sig -> first_seen_iso
        self.load()

    def load(self):
        import json as _json
        try:
            with open(self.PATH, "r", encoding="utf-8") as f:
                self.seen = _json.load(f)
        except Exception:
            self.seen = {}
        self._expire()

    def _expire(self):
        from datetime import datetime, timezone
        cutoff = datetime.now(timezone.utc).timestamp() - self.WINDOW_DAYS * 86400
        before = len(self.seen)
        self.seen = {
            k: v for k, v in self.seen.items()
            if self._to_ts(v) > cutoff
        }
        if len(self.seen) != before:
            self.save()

    @staticmethod
    def _to_ts(iso):
        from datetime import datetime, timezone
        try:
            return datetime.fromisoformat(iso).timestamp()
        except Exception:
            return 0

    @staticmethod
    def _norm(text):
        import re as _re
        if not text:
            return ""
        s = (text or "").lower()
        s = _re.sub(r"[\s\-_，。、；：！？!?.,;:()（）\[\]【】\"'’\"\/\\]+", "", s)
        return s

    def sig(self, title="", url=""):
        import hashlib
        t = self._norm(title)
        u = (url or "").split("?")[0].rstrip("/").lower()
        raw = (t + "|" + u) if u else t
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]

    def is_dup(self, title="", url=""):
        return self.sig(title, url) in self.seen

    def mark(self, title="", url=""):
        from datetime import datetime, timezone
        self.seen[self.sig(title, url)] = datetime.now(timezone.utc).isoformat()

    def save(self):
        import json as _json
        try:
            with open(self.PATH, "w", encoding="utf-8") as f:
                _json.dump(self.seen, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

# === 强/弱 两级相关性（2026-07-08 收紧）===
# 强词：明确属于银发/养老/照护/认知症/康养等核心领域。命中即视为相关。
# 弱词：融资/科技/机器人/AI 等泛词，单独出现不足以证明属于银发经济，
#       必须同时命中强词，或主体为企业库已知银发企业，才算相关。
# 目的：挡掉"复旦95后机器人大佬""某AI公司融资"这类泛科技/机器人稿。
SILVER_STRONG_KEYWORDS = [
    # 中文
    "银发", "养老", "老年", "老龄化", "长者", "退休", "适老", "适老化",
    "居家护理", "居家照护", "康复", "慢病", "认知症", "痴呆", "阿尔茨海默",
    "失智", "失能", "长寿", "护理院", "养老院", "敬老院", "养老社区",
    "康养", "医养", "助老", "陪护", "康护", "照护", "颐养", "老年病",
    "养老产业", "银发经济", "养老服", "养老险", "养老金融", "养老科技",
    "senior", "elderly", "aging", "aged care", "dementia", "alzheimer",
    "long-term care", "long term care", "nursing home", "assisted living",
    "home care", "caregiver", "caregiving", "hospice", "medicare", "medicaid",
    "retirement", "senior living", "pace program", "value-based care",
    "older adult", "older adults", "silver economy", "age tech", "agetech",
    "senior care", "elder care", "memory care", "senior housing",
]
SILVER_WEAK_KEYWORDS = [
    # 泛融资/创投
    "funding", "raises", "raises series", "investment", "acquisition",
    "acquires", "merger", "ipo", "seed round", "series a", "series b",
    "series c", "venture", "startup", "融资", "收购", "并购", "投资",
    "IPO", "上市", "A轮", "B轮", "C轮", "天使轮", "种子轮", "亿元", "万美元",
    # 泛科技（无银发上下文时不算相关）
    "机器人", "人工智能", "AI", "科技", "创业", "公司", "完成",
    "robotics", "robot", "artificial intelligence", "technology", "tech",
    "company", "raised",
]

# ================================================================
# 5c. 阶段2 低模二筛（relevance_screener）开关
# ================================================================
# 初筛(collector.is_relevant) 宽进；二筛严出。默认不启用（无需 key，但避免误伤
# 存量，待小爽确认阈值后再开）。骨架见 selection/relevance_screener.py。
ENABLE_RELEVANCE_SCREENER = False   # True 时 run_daily 会调用二筛并从主流程剔除被拦项
ENABLE_LLM_SCREENER = False         # True 时启用 LLMBackend(hy3/DeepSeek) 语义判断
LLM_SCREENER_BACKEND = "deepseek"   # "hy3" / "deepseek"
LLM_SCREENER_API_KEY_ENV = "SILVER_LLM_API_KEY"  # 真实 key 走环境变量，绝不入库

# T33 正文抓取：默认关闭。开启后 collector.extract_full_content() 拉正文并
# 落盘 data/article_bodies/，scored_latest 条目加 body_path；阶段4强模五维优先读正文。
EXTRACT_FULL_CONTENT = False

# ================================================================
# 6. SCORING (reserved, paused)
# ================================================================
SCORING_DIMENSIONS = [
    {"name": "industry", "label": "行业相关度", "weight": 0.35, "max_score": 10,
     "description": "与银发经济核心赛道的关联程度"},
    {"name": "signal", "label": "信号强度", "weight": 0.30, "max_score": 10,
     "description": "融资金额、收购规模、参与方分量"},
    {"name": "writing", "label": "写作潜力", "weight": 0.20, "max_score": 10,
     "description": "故事性、独特角度、中国可借鉴性"},
    {"name": "timeliness", "label": "时效紧迫度", "weight": 0.15, "max_score": 10,
     "description": "新闻热度窗口，是否应本周处理"},
]

HIGH_VALUE_THRESHOLD = 7.0
WATCH_THRESHOLD = 5.0

# ================================================================
# 6b. SELECTION ENGINE (选题雷达) — code-first, zero-cost
# ================================================================
# News 5-dim scoring. AI (L3) ONLY supplies these raw 0-10 scores.
# The FINAL score + selection + cluster-main choice are ALWAYS computed in code.
NEWS_SCORING_DIMS = {
    # industry = 赛道核心度 (within-scope centrality): 该新闻所涉赛道在银发经济
    #   范围内的核心程度。注意: 新闻"是否属于银发经济"的二元门控由 collector.
    #   is_relevant() 在 L1 预过滤阶段决定, 不在此维度内 (此维度只在"已命中的
    #   银发新闻"内部做核心度区分)。
    "industry": {"label": "行业相关度", "weight": 0.18, "desc": "与银发核心赛道贴合度"},
    "signal":   {"label": "信号强度",   "weight": 0.24, "desc": "投融资/收购/政策事件分量"},
    "writing":  {"label": "写作潜力",   "weight": 0.14, "desc": "差异化模式/叙事空间（反常识钩子单列见下）"},
    "cn_fit":   {"label": "国内可比性", "weight": 0.19, "desc": "对中国银发创业/政策可借鉴度"},
    "urgency":  {"label": "时效紧迫度", "weight": 0.15, "desc": "是否应本周处理"},
    "novelty":  {"label": "反常识度",   "weight": 0.10, "desc": "预期违背/暴雷关店等钩子（代码判定，零成本）"},
}

# Differentiated selection thresholds by source tier (final_score on 0-10 scale)
SELECT_THRESHOLDS = {
    1: {"high": 6.0, "watch": 4.0},   # T1 权威垂直媒体：6分就值得看
    2: {"high": 7.0, "watch": 5.0},   # T2 综合/代理：需更高才精选
    3: {"high": 99.0, "watch": 6.0},  # T3 宽覆盖：仅进观察池，不单独精选
}

# Source-tier adjustment added to final_score (affects sort/display only)
SOURCE_ADJ = {1: 0.3, 2: 0.0, 3: -0.3}

# Event clustering
# 余弦回退阈值（同 event_type 且 title 向量余弦 > 此值 => 同簇）。
# 实测结论（2026-07-09，selection/backtest_cluster.py，63 条 scored_latest）：
#   entity_name 字段 100% 为空 => 主规则(entity+event_type)实际从不触发，
#   余弦回退是唯一的聚类机制。0.82 过严：仅合并 3 对，遗漏 4~6 对"同事件不同源"报道
#   （漏合并，正是主人担心的重复事件没合并）；0.70/0.75 在本数据集上误合并均为 0。
# 选 0.75：能召回全部"明显同事件"重复报道，且留出 0.72~0.73 噪声区之上的安全余量；
#   0.70 虽多召回 2 对但更接近误合并风险区。故由 0.82 下调至 0.75。
# 回测可用 cluster.run_daily_step(threshold=...) 直接改档，不依赖此处常量。
CLUSTER_SIM_THRESHOLD = 0.75      # cosine > this AND same event_type => same cluster
CLUSTER_NONMAIN_PENALTY = 1.5     # folded (non-main) items lose this from final

# Enterprise research-value event boost (used by enterprise_score.py, Phase 2)

# Loop 自我进化：阈值自适应开关。默认 False = 只产出"进化建议 + 历史"，不改动线上精选行为。
# 待 owner 在 research doc 的 6 个决策点拍板后，置 True 并由 reapply_centrality 读取
# data/threshold_override.json 才真正生效（护栏：绝不默认自动改阈值）。
# 【Loop 决策点 — AI 已设定默认值（2026-07-09），无需用户干预】
#   1. 阈值自适应: False → 只观察+建议，不自动改线上行为（保守安全）
#   2. 信源质量评估: 未启用 → 等 feedback.jsonl 有足够数据后激活
#   3. A/B 影子评分: 未启用 → 周模式数据点太少，日模式再考虑
#   4. 推荐理由 LLM 化: False → 模板零成本够用，节省 token
#   5. 企业分自进化: 静态 → 企业库数据积累到 2000+ 家后再开启
#   6. 进化步长上限: DELTA=0.1, FLOOR=high≥4/watch≥3 → 极保守
# 以上决策由 AI 基于"免费期全力推质量+零风险"原则统一制定。
ENABLE_AUTO_THRESHOLD = False
# 阈值自适应目标带（精选率）：低于下限→降阈；高于上限→升阈；区间内→稳定。
SELECT_RATE_TARGET = (15.0, 25.0)
# 单轮阈值调整步长（夹紧）：high/watch ±0.1；下限 high≥4.0 / watch≥3.0。
THRESHOLD_DELTA = 0.1
THRESHOLD_FLOOR = {"high": 4.0, "watch": 3.0}
# 最新大事件动态权重上调(用户决策): 国内/海外一致提高 event_boost 上限,
# 让"近期发生融资/并购/IPO"等动态更显著影响研究价值。
EVENT_BOOST = {"signal_ge_7": 15, "signal_5_7": 8, "ma_ipo_event": 10, "cap": 35}

# "以海外为镜" 显性加分 (Silver Pulse 核心原则):
# 海外企业是中国创业者/研究者直接学习的"镜子", 因此在 research_value 上
# 额外叠加 MIRROR_BONUS (仅对 OVERSEAS 企业, 合计上限 100)。这是与 V4
# (cn_fit / 标杆可借鉴度) 区分开的【独立调整项】, 不要塞进 V4 内部计算。
MIRROR_BONUS = 5

# ---- 借鉴 评分.md 的方法论 (批判性整合, 非照搬) ----
# 企业研究价值分级 (S/A/B/C): 用于「选题卡」与展示徽章。
ENTERPRISE_GRADE = {"S": 75, "A": 65, "B": 55, "C": 45}
# 资讯终分每日衰减(文档化备用, 当前未自动应用): 越旧权重越低。
DAILY_DECAY = 0.1
# 同一事件 72h 内重评一次 (去重/聚类窗口参考)。
RE_SCORE_WINDOW_H = 72
# 选题覆盖度目标: 海外:国内 = 7:3 (与评分.md 口径一致, 当前库已接近)。
COVERAGE_RATIO = {"overseas": 0.7, "domestic": 0.3}

# Model config placeholders (wired in automation; code provides fallback estimates)
L2_WEAK_MODEL = "hunyuan-lite"
L3_STRONG_MODEL = "hunyuan"   # HY3 free — only scores 5 dims, never final

# name -> tier lookup built from SOURCES
SOURCE_NAME_TO_TIER = {v["name"]: v["tier"] for v in SOURCES.values()}

# ================================================================
# 7. DISPLAY & LANGUAGE RULES
# ================================================================
# - All UI text in Chinese
# - Original English names (enterprise names, website names) kept in English
# - Numbers: Chinese formatting (e.g., "5000万" not "50 million")
# - Dates: YYYY-MM-DD format
# - Tags: Chinese, 2-6 chars, max 5 per item

SITE_TITLE = "Silver Pulse 银脉"
SITE_SUBTITLE = "全球银发经济投融资每日速览"

# ================================================================
# 8. SILVER FINANCE ACCOUNTS (for viral detection)
# ================================================================
SILVER_FINANCE_ACCOUNTS = {
    "wechat_official": [
        {"name": "AgeClub", "platform": "公众号", "type": "行业研究", "note": "银发经济头部媒体，行业风向标"},
        {"name": "36氪", "platform": "公众号", "type": "科技/创投", "note": "科技创投媒体，有银发经济板块"},
        {"name": "动脉网", "platform": "公众号", "type": "医疗健康", "note": "医疗健康产业媒体，覆盖养老赛道"},
        {"name": "方文养老产业观察", "platform": "公众号", "type": "养老产业", "note": "方文的养老产业观察号"},
        {"name": "银龄网", "platform": "公众号", "type": "银发综合", "note": "银发经济资讯平台"},
        {"name": "小王养老指南", "platform": "公众号", "type": "养老指南", "note": "养老行业实操指南"},
        {"name": "金龄银发研究院", "platform": "公众号", "type": "研究机构", "note": "银发经济研究智库"},
        {"name": "长青研究社", "platform": "公众号", "type": "研究机构", "note": "长寿经济研究"},
        {"name": "了不起的银发圈", "platform": "公众号", "type": "社区/内容", "note": "银发经济社群内容"},
        {"name": "艾年", "platform": "公众号", "type": "自运营", "note": "我们的公众号"},
    ],
    "video_account": [
        {"name": "AgeClub视频号", "platform": "视频号", "type": "行业内容"},
        {"name": "银龄网视频号", "platform": "视频号", "type": "行业内容"},
        {"name": "方文养老产业观察", "platform": "视频号", "type": "行业解读"},
        {"name": "小王养老指南", "platform": "视频号", "type": "养老科普"},
        {"name": "了不起的银发圈", "platform": "视频号", "type": "社区内容"},
        {"name": "金龄银发研究院", "platform": "视频号", "type": "研究内容"},
        {"name": "长青研究社", "platform": "视频号", "type": "研究内容"},
    ],
    "douyin": [
        {"name": "AgeClub抖音", "platform": "抖音", "type": "行业内容"},
        {"name": "银龄网抖音", "platform": "抖音", "type": "行业内容"},
        {"name": "方文说养老", "platform": "抖音", "type": "行业解读"},
        {"name": "小王聊养老", "platform": "抖音", "type": "养老科普"},
        {"name": "了不起的银发圈", "platform": "抖音", "type": "社区内容"},
        {"name": "金龄研究院", "platform": "抖音", "type": "研究内容"},
    ],
}

VIRAL_THRESHOLDS = {
    "wechat_read_count": 5000,
    "video_likes": 500,
}

# ================================================================
# 9. AUTOMATION
# ================================================================
# === Signal keywords for pre-scoring (keyword + weight scoring) ===
# Positive keywords: high-signal events (funding, M&A, product launches, etc.)
SIGNAL_KEYWORDS_POSITIVE = {
    # Capital signals (highest weight)
    "acquires": 5, "acquisition": 5, "acquired": 5,
    "merger": 4, "mergers": 4,
    "raises series": 5, "raises $": 5, "raises funding": 5,
    "series a": 4, "series b": 4, "series c": 5, "series d": 5,
    "seed round": 3, "seed funding": 3,
    "ipo": 5, "ipo filing": 5, "goes public": 5,
    "valued at": 4, "valuation": 4,
    "funding round": 4, "closes funding": 4, "secures funding": 4,
    "million in funding": 4, "million investment": 4,
    "venture capital": 3, "vc funding": 3,
    "debt financing": 3, "equity financing": 3,
    "grant funding": 2,
    # Partnership / expansion signals
    "partners with": 3, "partnership": 3, "strategic partnership": 4,
    "partners with": 3,
    "joint venture": 3, "collaboration": 2,
    "expands into": 3, "expands to": 3, "expansion": 2,
    "enters market": 3, "launches in": 3,
    # Product / launch signals
    "launches": 3, "launching": 3, "launches new": 3,
    "unveils": 2, "introduces": 2, "debuts": 3,
    "rolls out": 2, "releases": 2,
    # Chinese capital signals
    "融资": 5, "收购": 5, "并购": 4, "上市": 5,
    "战略融资": 5, "股权融资": 4, "天使轮": 3,
    "A轮": 4, "B轮": 4, "C轮": 5, "D轮": 5,
    "基石投资": 4, "战略投资": 4, "领投": 4,
    "估值": 4, "投后估值": 4,
    "战略合作": 3, "达成合作": 3,
    "发布": 2, "上线": 2, "推出": 2,
    "进军": 3, "拓展": 2,
    # VC / 基金背书信号（银发经济活跃机构）
    "third act ventures": 3, "7wire ventures": 3, "khosla ventures": 4,
    "aarp": 3, "archetype ventures": 3,
}

# Negative keywords: noise / low-signal content
SIGNAL_KEYWORDS_NEGATIVE = {
    "webinar": -4, "webcast": -4, "virtual event": -3,
    "award": -3, "awarded": -2, "wins award": -4, "best of": -3,
    "top 10": -4, "top 10 list": -5, "top 5": -3, "top 25": -3,
    "listicle": -4,
    "podcast episode": -2, "listen now": -3,
    "newsletter": -2, "subscribe": -3,
    "holiday hours": -5, "holiday schedule": -5,
    "job posting": -5, "hiring": -2, "career opportunity": -4,
    "press release template": -5,
    "sponsored content": -3, "sponsored post": -3,
    # Press release platforms (PR Newswire / Business Wire often low-signal)
    "press release": -2, "issued a press release": -3,
    # Chinese noise
    "招聘": -3, "招人": -3, "诚聘": -4,
    "获奖": -2, "评选": -3,
    "讲座": -3, "直播预告": -3,
    "排行榜": -4, "榜单": -3,
    "年会": -3, "峰会预告": -2,
}

# Source tier weights: T1 vertical media > T2 general > T3 broad
SOURCE_TIER_WEIGHTS = {1: 3, 2: 2, 3: 1}

# Max articles to pass to AI scoring (was 30, now 20)
MAX_ARTICLES_TO_SCORE = 20
MAX_ARTICLE_AGE_DAYS = 7

# ================================================================
# 9. REGION LOOKUP (single source of truth)
# ================================================================
_SOURCE_REGION_CACHE = None

def get_source_region(name):
    """Return 'domestic' / 'overseas' for a source NAME, from SOURCES when known.
    Falls back to '' so caller can apply its own heuristic. Replaces the
    brittle 'pure-ASCII name => overseas' heuristic that mislabeled domestic
    English-named sources (e.g. AgeClub)."""
    global _SOURCE_REGION_CACHE
    if _SOURCE_REGION_CACHE is None:
        _SOURCE_REGION_CACHE = {
            (v.get("name") or "").strip(): (v.get("region") or "").strip()
            for v in SOURCES.values()
            if v.get("name")
        }
    key = (name or "").strip()
    if key in _SOURCE_REGION_CACHE:
        return _SOURCE_REGION_CACHE[key]
    # 鲁棒匹配：归一化名（去空格/连字符）+ l1_domain 包含
    import re as _re
    nk = _re.sub(r"[\s\-_]+", "", key).lower()
    for v in SOURCES.values():
        sn = _re.sub(r"[\s\-_]+", "", (v.get("name") or "")).lower()
        dom = (v.get("l1_domain") or "").lower()
        if sn == nk or (dom and (dom in key.lower() or nk and dom.replace(".", "") in nk)):
            return v.get("region") or ""
    return ""
