#!/usr/bin/env python3
"""
Generate about.html — Silver Pulse 网站说明栏目 v2.
Three tabs: 资讯版说明 / 企业库说明 / 网站规则
Updated for v5.0 config: 13-class system, event-type classification,
tag pool, L1/L2 source hierarchy, data filtering logic.
"""
import os
import json
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
BUILD_STAMP = datetime.now().strftime("%Y%m%d%H%M%S")

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    SOURCES, ENTERPRISE_CATEGORIES, NEWS_EVENT_TYPES, NEWS_DOMAINS,
    TAG_POOL, SCORING_DIMENSIONS, RELEVANCE_KEYWORDS,
    IRRELEVANT_KEYWORDS, MAX_ARTICLE_AGE_DAYS,
)

# Enterprise data sources
ENTERPRISE_SOURCES = [
    {"name": "选题库（手动精选）", "count": "30家", "desc": "手动精选的高优先级企业，含详细融资信息和选题建议"},
    {"name": "Stage (Not Age) 书籍", "count": "108家", "desc": "来自Keren Etkin著作中提及的海外银发科技企业"},
    {"name": "中国企业图谱（许之怿）", "count": "382家", "desc": "国内银发经济企业行业图谱"},
    {"name": "选题库V4（xlsx）", "count": "504条", "desc": "选题库Excel版本中的企业信息表"},
    {"name": "中国银发经济行业mapping", "count": "374家", "desc": "国内银发经济行业mapping，含三级分类"},
    {"name": "2025 AgeTech Market Map", "count": "322家", "desc": "The AgeTech Revolution发布的2025 AgeTech市场地图PDF"},
    {"name": "The AgeTech Revolution 书籍", "count": "8家", "desc": "深度企业案例（ElliQ/Apple/Elder等）"},
]

# Enterprise new schema fields
ENTERPRISE_FIELDS = [
    ("name", "str", "企业名称（中文名写中文，英文名保留英文不翻译）"),
    ("region", "str", "地区：国内 / 海外"),
    ("category_l1", "str", "一级分类（13类之一）"),
    ("category_l2", "str", "二级分类（70个子类之一）"),
    ("tags", "list", "标签（来自TAG_POOL，最多5个）"),
    ("description", "str", "一句话业务描述"),
    ("highlights", "str", "亮点（关键数据/里程碑/特色）"),
    ("funding_latest", "str", "最新融资轮次信息"),
    ("funding_total", "str", "累计融资总额"),
    ("investors", "list", "投资方列表"),
    ("founded", "str", "成立时间"),
    ("business_model", "str", "商业模式特点（基于描述和分类自动推断）"),
    ("value_score", "int", "企业价值评分（0-100），暂未启用"),
    ("source", "str", "数据来源标识"),
    ("crunchbase_url", "str", "Crunchbase搜索链接（点击跳转搜索页校验）"),
    ("website_url", "str", "企业官网链接（可选）"),
    ("serial", "str", "序号（#0001-#0999）"),
]


def generate():
    # Build source list HTML — compact format
    source_rows = []
    for key, src in SOURCES.items():
        tier = src.get("tier", 3)
        tier_label = f"T{tier}"
        region = "海外" if src.get("region") == "overseas" else "国内"
        l1 = src.get("l1_domain", "")
        # L2 channels — compact display
        l2_list = src.get("l2_channels", [])
        l2_parts = []
        for ch in l2_list:
            l2_parts.append(f'<span class="l2-chip">{ch[0]}</span> <span class="l2-method">{ch[2]}</span>')
        l2_html = " ".join(l2_parts) if l2_parts else '<span class="l2-method">直接采集</span>'
        source_rows.append(
            f"<tr><td class='tier-badge tier-{tier_label.lower()}'>{tier_label}</td>"
            f"<td><b>{src['name']}</b><div class='src-l1'>{l1}</div></td>"
            f"<td class='region-badge region-{region}'>{region}</td>"
            f"<td>{l2_html}</td></tr>"
        )
    source_table = "\n".join(source_rows)

    # Build 13-category list with L2
    cat_rows = []
    for cat_key, cat_info in ENTERPRISE_CATEGORIES.items():
        l2_list = cat_info.get("l2", [])
        l2_html = " ".join(f'<span class="l2-chip">{l2}</span>' for l2 in l2_list)
        cat_rows.append(
            f"<tr><td class='cat-name'>{cat_info['label']}</td><td>{len(l2_list)}</td><td>{l2_html}</td></tr>"
        )
    cat_table = "\n".join(cat_rows)

    # Event types
    event_rows = []
    for evt_key, evt_info in NEWS_EVENT_TYPES.items():
        event_rows.append(
            f"<tr><td class='cat-name'>{evt_info['label']}</td><td>{evt_info['desc']}</td></tr>"
        )
    event_table = "\n".join(event_rows)

    # Tag pool grouped by type
    tag_groups = {}
    for tag_name, tag_info in TAG_POOL.items():
        t_type = tag_info.get("type", "other")
        if t_type not in tag_groups:
            tag_groups[t_type] = []
        tag_groups[t_type].append((tag_name, tag_info.get("desc", "")))

    tag_type_labels = {
        "capital": "资本信号",
        "endorsement": "背书信号",
        "stage": "发展阶段",
        "special": "特殊标记",
        "geo": "地理标记",
    }
    tag_pool_html = ""
    for t_type, tags in tag_groups.items():
        label = tag_type_labels.get(t_type, t_type)
        chips = " ".join(
            f'<span class="tag-chip" title="{desc}">{name}</span>'
            for name, desc in tags
        )
        tag_pool_html += f'<p style="margin:6px 0;"><b>{label}</b>（{len(tags)}个）：</p><div style="margin:4px 0 12px;">{chips}</div>'

    # Enterprise source list
    ent_src_rows = []
    for s in ENTERPRISE_SOURCES:
        ent_src_rows.append(
            f"<tr><td><b>{s['name']}</b></td><td>{s['count']}</td><td>{s['desc']}</td></tr>"
        )
    ent_src_table = "\n".join(ent_src_rows)

    # Enterprise fields
    field_rows = []
    for fname, ftype, fdesc in ENTERPRISE_FIELDS:
        field_rows.append(
            f'<div class="field-item"><span class="field-name">{fname}</span>'
            f'<span class="field-type">{ftype}</span>'
            f'<span class="field-desc">{fdesc}</span></div>'
        )
    field_html = "\n".join(field_rows)

    # Relevance keywords (sample)
    rel_kw_sample = RELEVANCE_KEYWORDS[:20]
    rel_kw_html = " ".join(f'<span class="kw-chip">{kw}</span>' for kw in rel_kw_sample)

    # Irrelevant keywords
    irrel_kw_html = " ".join(f'<span class="kw-chip kw-irrelevant">{kw}</span>' for kw in IRRELEVANT_KEYWORDS)

    # Load enterprise count
    ent_path = os.path.join(DATA_DIR, "enterprise/all_enterprises.json")
    ent_count = 0
    if os.path.exists(ent_path):
        with open(ent_path, "r", encoding="utf-8") as f:
            ent_count = len(json.load(f))

    # Count sources by tier
    t1_count = sum(1 for s in SOURCES.values() if s.get("tier") == 1)
    t2_count = sum(1 for s in SOURCES.values() if s.get("tier") == 2)
    t3_count = sum(1 for s in SOURCES.values() if s.get("tier") == 3)

    html = f'''<!-- build:{BUILD_STAMP} -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<title>Silver Pulse 银脉 · 网站说明</title>
<style>
:root {{
  --bg: #f5f5f5;
  --sidebar-bg: #ffffff;
  --card-bg: #ffffff;
  --text: #1a1a1a;
  --text-secondary: #666;
  --text-muted: #999;
  --border: #e8e8e8;
  --accent: #0891b2;
  --accent-light: #ecfeff;
  --radius: 8px;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif; background:var(--bg); color:var(--text); line-height:1.6; display:flex; min-height:100vh; }}

.sidebar {{ width:200px; background:var(--sidebar-bg); border-right:1px solid var(--border); position:fixed; top:0; left:0; height:100vh; overflow-y:auto; padding:20px 0; flex-shrink:0; z-index:10; }}
.sidebar-logo {{ padding:0 16px 16px; border-bottom:1px solid var(--border); margin-bottom:12px; }}
.sidebar-logo h1 {{ font-size:18px; font-weight:700; color:var(--accent); }}
.sidebar-logo .logo-sub {{ font-size:11px; color:var(--text-muted); margin-top:2px; }}
.nav-section {{ padding:4px 0; }}
.nav-label {{ font-size:11px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; padding:6px 16px 4px; font-weight:600; }}
.nav-item {{ display:block; padding:8px 16px 8px 24px; font-size:13px; color:var(--text-secondary); text-decoration:none; cursor:pointer; border-left:3px solid transparent; transition:all 0.15s; }}
.nav-item:hover {{ background:#fafafa; color:var(--text); }}
.nav-item.active {{ background:var(--accent-light); color:var(--accent); border-left-color:var(--accent); font-weight:600; }}

.main {{ flex:1; margin-left:200px; max-width:980px; width:calc(100% - 200px); padding:24px 32px 60px; }}
.header h2 {{ font-size:20px; font-weight:700; margin-bottom:4px; }}
.header p {{ font-size:12px; color:var(--text-muted); }}

.tab-bar {{ display:flex; gap:0; margin:20px 0 24px; border-bottom:2px solid var(--border); }}
.tab-btn {{ padding:10px 20px; border:none; background:transparent; font-size:14px; font-weight:500; color:var(--text-secondary); cursor:pointer; border-bottom:2px solid transparent; margin-bottom:-2px; transition:all 0.15s; }}
.tab-btn:hover {{ color:var(--accent); }}
.tab-btn.active {{ color:var(--accent); border-bottom-color:var(--accent); font-weight:600; }}
.tab-content {{ display:none; }}
.tab-content.active {{ display:block; }}

.section {{ margin-bottom:32px; }}
.section h3 {{ font-size:16px; font-weight:600; margin-bottom:12px; color:var(--text); padding-left:12px; border-left:3px solid var(--accent); }}
.section p {{ font-size:14px; color:var(--text-secondary); margin-bottom:8px; line-height:1.8; }}
.section ul {{ margin:8px 0 12px 20px; }}
.section li {{ font-size:14px; color:var(--text-secondary); margin-bottom:4px; line-height:1.7; }}

.info-table {{ width:100%; border-collapse:collapse; font-size:13px; margin:12px 0; background:var(--card-bg); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; table-layout:fixed; }}
.info-table th {{ background:#fafafa; padding:8px 10px; text-align:left; font-size:11px; font-weight:600; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.3px; border-bottom:1px solid var(--border); }}
.info-table td {{ padding:8px 10px; border-bottom:1px solid #f0f0f0; vertical-align:top; word-wrap:break-word; overflow-wrap:break-word; }}
.info-table tr:last-child td {{ border-bottom:none; }}
.info-table tr:hover {{ background:#fafbfc; }}
.cat-name {{ font-weight:600; color:var(--accent); white-space:nowrap; }}
.src-l1 {{ font-size:10px; color:var(--text-muted); margin-top:2px; }}
.tier-badge {{ font-size:10px; font-weight:700; padding:2px 6px; border-radius:3px; text-align:center; display:inline-block; }}
.tier-t1 {{ background:#dcfce7; color:#166534; }}
.tier-t2 {{ background:#dbeafe; color:#1e40af; }}
.tier-t3 {{ background:#f3f4f6; color:#6b7280; }}
.region-badge {{ font-size:10px; font-weight:500; padding:2px 8px; border-radius:3px; text-align:center; }}
.region-海外 {{ background:#ecfdf5; color:#065f46; }}
.region-国内 {{ background:#eff6ff; color:#1e40af; }}

.callout {{ background:var(--accent-light); border:1px solid #a5f3fc; border-radius:var(--radius); padding:12px 16px; margin:12px 0; font-size:13px; color:#0e7490; }}
.callout-warning {{ background:#fef3c7; border-color:#fcd34d; color:#92400e; }}

.tag-chip {{ display:inline-block; font-size:11px; padding:3px 8px; border-radius:4px; background:#dbeafe; color:#1e40af; margin:2px; font-weight:500; }}
.l2-chip {{ display:inline-block; font-size:10px; padding:2px 6px; border-radius:3px; background:#f0f0f0; color:var(--text-secondary); margin:1px; }}
.l2-method {{ font-size:10px; color:var(--accent); font-weight:500; }}
.kw-chip {{ display:inline-block; font-size:11px; padding:2px 8px; border-radius:3px; background:#ecfdf5; color:#065f46; margin:2px; }}
.kw-irrelevant {{ background:#fef2f2; color:#991b1b; }}

.field-list {{ margin:12px 0; }}
.field-item {{ display:flex; gap:12px; padding:8px 0; border-bottom:1px solid #f5f5f5; }}
.field-name {{ font-weight:600; color:var(--text); min-width:140px; font-size:13px; font-family:monospace; }}
.field-type {{ color:var(--accent); font-size:12px; min-width:60px; }}
.field-desc {{ color:var(--text-secondary); font-size:13px; flex:1; }}

.footer {{ text-align:center; padding:24px 0 16px; font-size:12px; color:var(--text-muted); border-top:1px solid var(--border); margin-top:24px; }}

@media (max-width:768px) {{
  .sidebar {{ display:none; }}
  .main {{ margin-left:0; width:100%; padding:16px; max-width:100%; }}
}}
</style>
</head>
<body>

<div class="sidebar">
  <div class="sidebar-logo">
    <h1>Silver Pulse 银脉</h1>
    <p class="logo-sub">Silver Pulse</p>
  </div>
  <div class="nav-section">
    <div class="nav-label">内容</div>
    <a href="index.html" class="nav-item">资讯看板</a>
    <a href="enterprise.html" class="nav-item">企业库</a>
    <a href="about.html" class="nav-item active">网站说明</a>
  </div>
</div>

<div class="main">

<div class="header">
  <h2>网站说明</h2>
  <p>Silver Pulse 银脉 · 银发经济投融资资讯聚合 + 企业数据库</p>
</div>

<div class="tab-bar">
  <button class="tab-btn active" onclick="switchTab('news', event)">资讯版说明</button>
  <button class="tab-btn" onclick="switchTab('enterprise', event)">企业库说明</button>
  <button class="tab-btn" onclick="switchTab('rules', event)">网站规则</button>
</div>

<!-- Tab 1: 资讯版说明 -->
<div class="tab-content active" id="tab-news">

  <div class="section">
    <h3>资讯版定位</h3>
    <p>Silver Pulse 资讯看板是一个<b>全球银发经济投融资信息聚合器</b>，每天自动从海外和国内的核心信源采集银发经济相关新闻资讯，为内容创作者提供选题发现服务。</p>
    <p>核心价值：<b>以海外为镜，照中国之路</b>。追踪海外银发经济企业的融资、收购、产品发布动态，为中国银发经济创业者提供路书。</p>
  </div>

  <div class="section">
    <h3>信源体系（{len(SOURCES)} 个源 · T1={t1_count} T2={t2_count} T3={t3_count}）</h3>
    <p>信源采用<b>L1/L2分级结构</b>：L1为官网域名，L2为具体频道/栏目。每个信源标注层级（T1/T2/T3）、地区、采集方式。</p>
    <table class="info-table">
      <thead>
        <tr><th style="width:40px;">层级</th><th>信源名称 / L1域名</th><th style="width:50px;">地区</th><th>L2频道 + 采集方式</th></tr>
      </thead>
      <tbody>
        {source_table}
      </tbody>
    </table>
    <div class="callout">
      <b>T1</b>（{t1_count}个）= 海外核心专业媒体，银发经济垂直领域权威来源，总是采集，尽量获取全文<br>
      <b>T2</b>（{t2_count}个）= 国内银发经济媒体 + 海外扩展覆盖，采集摘要<br>
      <b>T3</b>（{t3_count}个）= 宽覆盖辅助源，仅用于相关性预过滤<br>
      <br>
      <b>采集方式</b>：rss = RSS直连 | google_news = Google News RSS代理 | manual = 手动入库 | api = API调用
    </div>
  </div>

  <div class="section">
    <h3>分类体系（事件类型L1 + 涉及领域L2）</h3>
    <p>每条资讯会被自动分类为<b>一个事件类型（L1）</b>和<b>一个或多个涉及领域（L2）</b>。分类与标签严格分开。</p>

    <p style="margin-top:12px;"><b>事件类型 L1</b>（{len(NEWS_EVENT_TYPES)} 类）：</p>
    <table class="info-table">
      <thead><tr><th>事件类型</th><th>说明</th></tr></thead>
      <tbody>{event_table}</tbody>
    </table>

    <p style="margin-top:16px;"><b>涉及领域 L2</b>（复用企业库13个一级分类名称）：</p>
    <p style="font-size:13px;color:var(--text-secondary);">{", ".join(NEWS_DOMAINS)}</p>
    <div class="callout">
      <b>分类逻辑</b>：事件类型通过关键词匹配自动判定（融资/收购/政策/产品/趋势/人事/其他）。<br>
      涉及领域通过领域关键词匹配，一篇文章可涉及多个领域。
    </div>
  </div>

  <div class="section">
    <h3>标签池（TAG_POOL）</h3>
    <p>标签是与分类独立的自由标记，用于标注资本信号、背书、阶段、特殊模式等。每条资讯最多5个标签，所有标签来自预定义的标签池。</p>
    {tag_pool_html}
    <div class="callout">
      <b>标签池迭代规则</b>：标签池每周迭代一次。每次迭代时，AI会扫描近一周的资讯数据，识别高频出现但尚未纳入标签池的概念、赛道、模式，自动补充到TAG_POOL中。迭代后重新标注所有已入库资讯。<br>
      <b>迭代成本</b>：每周约消耗5-10K tokens（数据扫描 + 新标签识别 + 配置文件更新）。
    </div>
  </div>

  <div class="section">
    <h3>数据筛选逻辑</h3>
    <p><b>为什么展示这些数据而不是其它？</b>资讯看板的筛选策略分三步：</p>

    <p style="margin-top:12px;"><b>第一步：信源采集</b></p>
    <ul>
      <li>T1信源：总是采集，尽量获取全文</li>
      <li>T2信源：采集，获取摘要（summary）</li>
      <li>T3信源：采集，仅用于相关性预过滤，不直接展示</li>
    </ul>

    <p style="margin-top:12px;"><b>第二步：相关性过滤</b></p>
    <ul>
      <li>文章标题+摘要必须匹配至少一个<b>相关性关键词</b>（RELEVANCE_KEYWORDS）</li>
      <li>匹配<b>无关关键词</b>（IRRELEVANT_KEYWORDS）的文章直接丢弃</li>
      <li>地区由信源决定，不由内容判断：国内信源→国内，海外信源→海外</li>
    </ul>
    <p style="margin-top:8px;">相关性关键词示例（共{len(RELEVANCE_KEYWORDS)}个，展示前20个）：</p>
    <div style="margin:8px 0;">{rel_kw_html}</div>
    <p style="margin-top:8px;">无关关键词（共{len(IRRELEVANT_KEYWORDS)}个）：</p>
    <div style="margin:8px 0;">{irrel_kw_html}</div>

    <p style="margin-top:12px;"><b>第三步：信号打分（关键词+权重）</b></p>
    <ul>
      <li>通过相关性过滤的文章进入<b>信号打分</b>环节</li>
      <li><b>加分关键词</b>（权重+3~+5）：acquires/acquisition、raises Series、IPO、valued at、partners with、launches、expands into、融资/收购/并购/上市/A轮/B轮/C轮等</li>
      <li><b>减分关键词</b>（权重-2~-5）：webinar、award、top 10 list、招聘/获奖/排行榜等噪音内容</li>
      <li><b>信源权重</b>：T1垂直媒体（+3）> T2综合媒体（+2）> T3宽覆盖（+1）</li>
      <li><b>叠加奖励</b>：一篇文章命中多个加分关键词时额外加分（2个+1，3个以上+3）</li>
      <li>最终只保留<b>信号分最高的Top 20条</b>推送至AI评分环节，大幅降低token消耗</li>
    </ul>
    <div class="callout">
      <b>为什么这样设计？</b>全量抓取再人工看效率太低。脚本内置关键词+权重打分，自动过滤噪音（webinar/award/排行榜），优先推送融资/收购/上市等高价值信号。从原来全量30条精简到Top 20条，每次采集节省约30%的AI评分token。
    </div>

    <p style="margin-top:12px;"><b>第四步：展示排序</b></p>
    <ul>
      <li>默认按日期降序（最新优先）</li>
      <li><b>精选视图</b>：展示评分≥5.0或人工精选的条目（当前评分暂停，精选=全量，恢复评分后两者会不同）</li>
      <li><b>全量视图</b>：展示所有通过相关性过滤的条目</li>
      <li>可按事件类型、涉及领域、标签、地区多级筛选</li>
    </ul>
    <div class="callout">
      <b>精选 vs 全量 说明</b>：当前评分功能暂停中，所以精选和全量显示的数据完全一样。未来恢复评分后，精选只展示高价值条目（≥7.0）和值得关注条目（5.0-6.9），全量则展示所有通过过滤的条目。
    </div>
  </div>

  <div class="section">
    <h3>推荐理由（模板生成）</h3>
    <p>资讯卡片底部的<b>蓝色文字</b>是推荐理由（recommendation字段），基于关键词检测自动生成，内容包括：</p>
    <ul>
      <li>事件类型判断（融资/收购/IPO/政策等）</li>
      <li>涉及金额提取（如有）</li>
      <li>对中国市场的参照意义（按事件类型匹配模板）</li>
    </ul>
    <div class="callout">
      <b>积分消耗</b>：模板生成零AI成本。如需更高洞察的推荐理由，可对Top高价值条目触发AI增强（可选，按需）。<br>
      <b>低成本方案</b>：当前默认模板生成，每次采集约节省12-31K tokens（相比全量AI生成推荐理由）。
    </div>
  </div>

  <div class="section">
    <h3>评分机制</h3>
    <div class="callout">
      <b>当前状态：关键词信号打分已激活（低成本版）</b><br>
      看板使用 <code>signal_score</code>（关键词+信源权重）作为 <code>final_score</code> 代理，自动分级并生成模板化推荐理由。<br>
      <b>AI深度评分（四维加权）</b>为可选增强：对Top高价值条目生成更具洞察的推荐理由，按需触发，不每次运行。
    </div>
    <p>关键词信号打分构成：</p>
    <ul>
      <li><b>信源基础分</b>：T1(+3) > T2(+2) > T3(+1)</li>
      <li><b>加分关键词</b>（权重+2~+5）：融资/收购/IPO/战略合作/产品发布等</li>
      <li><b>减分关键词</b>（权重-2~-5）：webinar/招聘/排行榜/新闻稿等噪音</li>
      <li><b>叠加奖励</b>：命中2个加分+1，3个以上+3</li>
    </ul>
    <p>阈值设计：≥7.0 高价值(high) | 5.0-6.9 值得关注(watch) | &lt;5.0 归档(archive)</p>
    <p>AI四维加权评分（可选增强）：行业相关度(35%) + 信号强度(30%) + 写作潜力(20%) + 时效紧迫度(15%)</p>
  </div>

  <div class="section">
    <h3>筛选规则迭代计划（规划中，尚未执行）</h3>
    <p>当前筛选为<b>纯关键词匹配 + 信源权重</b>，已能过滤大部分噪音。参考 AIHOT（卡兹克）的成熟实践，后续迭代路径如下：</p>
    <p style="margin-top:10px;"><b>短期（代码层，零AI成本）</b></p>
    <ul>
      <li><b>差异化阈值</b>：不同层级信源设不同精选阈值 — T1≥6.0、T2≥7.0、T3≥8.0。避免T3宽覆盖源的通稿混入选精。</li>
      <li><b>事件聚类</b>：用 embedding 相似度（&gt;0.85）将同一事件的多次报道折叠，仅保留最高分来源（官网&gt;官方推特&gt;KOL），消除重复展示。</li>
      <li><b>新闻稿降权</b>：PR Newswire / Business Wire 等通稿平台自动降权，仅保留其中融资/收购类实质内容。</li>
    </ul>
    <p style="margin-top:10px;"><b>中期（Skill层，AI单一能力封装）</b></p>
    <ul>
      <li><b>AI只打维度分</b>：大模型只输出4个维度分，最终分用代码计算（参考AIHOT：Prompt从600行缩减到200行）。</li>
      <li><b>零AI成本日报</b>：入库时完成所有AI处理（打分+翻译+摘要），周报只需分桶排序，1秒生成。</li>
    </ul>
    <p style="margin-top:10px;"><b>长期（Agent层，动态规划）</b></p>
    <ul>
      <li><b>新信源自动发现</b>：Agent扫描相关领域，推荐新信源。</li>
      <li><b>趋势预测报告</b>：基于累积数据生成季度趋势分析。</li>
    </ul>
    <div class="callout">
      <b>核心原则（来自AIHOT经验）</b>：能用代码处理的，一律不用模型处理。预筛用关键词（已最优），最终分与精选判断用代码，只有维度打分需要AI泛化能力时用Skill封装。
    </div>
  </div>

  <div class="section">
    <h3>更新机制</h3>
    <ul>
      <li><b>资讯采集</b>：每周一 01:00 北京时间自动执行</li>
      <li><b>标签池迭代</b>：每周一 03:00，AI扫描近一周数据自动补充新标签</li>
      <li><b>摘要推送</b>：每周一 06:00，生成本周资讯摘要推送到WorkBuddy对话</li>
      <li><b>采集窗口</b>：过去 {MAX_ARTICLE_AGE_DAYS} 天的资讯</li>
      <li><b>每周积分消耗</b>：约25-50K tokens（采集8-12K + 分类3-5K + 推荐理由12-31K + HTML生成2-3K + 标签迭代5-10K + 摘要推送3-5K）</li>
      <li><b>展示逻辑</b>：精选条目优先展示，全量条目可切换查看</li>
      <li><b>排序方式</b>：默认按日期降序（最新优先）</li>
    </ul>
    <div class="callout">
      <b>定时任务时序</b>：每周一 01:00 资讯采集 → 03:00 标签池迭代（基于最新数据） → 06:00 摘要推送（一切就绪后推送到WorkBuddy对话窗口）。
    </div>
  </div>

</div>

<!-- Tab 2: 企业库说明 -->
<div class="tab-content" id="tab-enterprise">

  <div class="section">
    <h3>企业库定位</h3>
    <p>Silver Pulse 企业数据库是一个<b>全球银发经济企业图谱</b>，收录国内外银发经济相关企业，为内容创作者提供企业背景信息和选题参考。</p>
    <p>当前收录：<b>{ent_count} 家企业</b>（国内 + 海外）</p>
  </div>

  <div class="section">
    <h3>数据来源</h3>
    <table class="info-table">
      <thead>
        <tr><th>来源</th><th>数量</th><th>说明</th></tr>
      </thead>
      <tbody>
        {ent_src_table}
      </tbody>
    </table>
    <p style="font-size:12px; color:var(--text-muted); margin-top:8px;">注：各来源间有去重，最终融合后总数少于各来源之和。</p>
  </div>

  <div class="section">
    <h3>13 分类体系（{len(ENTERPRISE_CATEGORIES)} 个一级 + {sum(len(c.get("l2",[])) for c in ENTERPRISE_CATEGORIES.values())} 个二级）</h3>
    <p>企业库采用 13 个一级分类，每个分类下设若干二级子类。企业按原始分类自动映射到对应类别。展示时<b>不显示编码</b>，直接显示分类名称。</p>
    <table class="info-table">
      <thead>
        <tr><th>一级分类</th><th>二级数</th><th>二级子类</th></tr>
      </thead>
      <tbody>
        {cat_table}
      </tbody>
    </table>
  </div>

  <div class="section">
    <h3>字段定义（{len(ENTERPRISE_FIELDS)} 字段统一 Schema）</h3>
    <div class="field-list">
      {field_html}
    </div>
    <div class="callout">
      <b>空字段处理</b>：如果某个字段为空，前端直接不展示该字段，不显示占位符。<br>
      <b>名称规则</b>：企业名称保留原始语言——中文名写中文，英文名保留英文不翻译。<br>
      <b>标签规则</b>：标签来自TAG_POOL，最多5个，与分类（L1/L2）独立。<br>
      <b>价值评分</b>：value_score 字段已预留，暂不计算不展示。
    </div>
  </div>

  <div class="section">
    <h3>展示规则</h3>
    <ul>
      <li><b>布局</b>：紧凑横条布局，所有字段直接可见，不需要点击展开</li>
      <li><b>标签</b>：蓝色背景，稍醒目</li>
      <li><b>地区</b>：灰色小字，低调展示在标签后面</li>
      <li><b>亮点</b>：小字蓝色展示</li>
      <li><b>链接</b>：Crunchbase和官网链接小而低调</li>
      <li><b>空字段</b>：为空的字段不展示，不留空白</li>
      <li><b>搜索</b>：搜索框与地区筛选放在同一行，不单独占行</li>
      <li><b>分类筛选</b>：分类按钮上的数字随地区筛选动态更新（选"国内"后分类数字只显示国内企业数）</li>
      <li><b>切换地区</b>：切换地区筛选时自动重置分类为"全部"</li>
    </ul>
  </div>

</div>

<!-- Tab 3: 网站规则 -->
<div class="tab-content" id="tab-rules">

  <div class="section">
    <h3>整体架构</h3>
    <p>Silver Pulse 银脉由三个核心模块组成：</p>
    <ul>
      <li><b>资讯看板</b>（index.html）：每周银发经济投融资新闻聚合</li>
      <li><b>企业数据库</b>（enterprise.html）：全球银发经济企业图谱</li>
      <li><b>网站说明</b>（about.html）：本页面，规则与字段说明</li>
    </ul>
  </div>

  <div class="section">
    <h3>语言规则</h3>
    <ul>
      <li><b>UI文字</b>：全部中文</li>
      <li><b>企业名称</b>：保留原始语言——中文名写中文，英文名保留英文不翻译</li>
      <li><b>信源名称</b>：常见英文信源名称翻译为中文显示（如 Home Health Care News → 家庭健康护理新闻），保留原英文名在括号外</li>
      <li><b>数字</b>：中文格式（如"5000万"而非"50 million"）</li>
      <li><b>日期</b>：YYYY-MM-DD 格式</li>
      <li><b>标签</b>：中文，2-6字，每条最多5个</li>
      <li><b>推荐理由</b>：全部中文，2-3句言之有物，说明对中国市场的具体参照</li>
    </ul>
  </div>

  <div class="section">
    <h3>分类与标签的区分</h3>
    <div class="callout">
      <b>分类</b>是结构化的层级体系，每条资讯/企业必须归属一个分类。<br>
      <b>标签</b>是自由标记，用于补充分类无法表达的维度（如资本信号、背书、阶段、模式特征）。<br>
      <br>
      两者在UI上<b>分开展示</b>：分类用独立行展示，标签用蓝色badge展示，不混在同一行。
    </div>
    <ul>
      <li><b>资讯分类</b>：事件类型L1（7类）+ 涉及领域L2（复用企业库13类名称）</li>
      <li><b>企业分类</b>：一级分类L1（13类）+ 二级分类L2（70子类）</li>
      <li><b>标签池</b>：资本信号 / 背书信号 / 发展阶段 / 特殊标记 / 地理标记</li>
    </ul>
  </div>

  <div class="section">
    <h3>更新频率与积分</h3>
    <table class="info-table">
      <thead>
        <tr><th>模块</th><th>频率</th><th>时间</th><th>积分消耗</th><th>方式</th></tr>
      </thead>
      <tbody>
        <tr><td>RSS采集</td><td>每周</td><td>周一 01:00 北京时间</td><td>约8-12K tokens</td><td>自动化（feedparser解析 + 内容提取）</td></tr>
        <tr><td>分类+标签</td><td>每周</td><td>采集后</td><td>约3-5K tokens</td><td>自动化（关键词匹配，无AI调用）</td></tr>
        <tr><td>推荐理由生成</td><td>每周</td><td>采集后</td><td>约12-31K tokens</td><td>AI生成（仅精选条目，约62条×200-500 tokens/条）</td></tr>
        <tr><td>HTML生成</td><td>每周</td><td>采集后</td><td>约2-3K tokens</td><td>自动化（模板渲染）</td></tr>
        <tr><td>标签池迭代</td><td>每周</td><td>周一 03:00</td><td>约5-10K tokens</td><td>AI扫描+更新TAG_POOL</td></tr>
        <tr><td>每周摘要推送</td><td>每周</td><td>周一 06:00</td><td>约3-5K tokens</td><td>AI读取数据生成摘要推送到WorkBuddy对话</td></tr>
        <tr><td>企业库</td><td>不定期</td><td>—</td><td>手动</td><td>新数据源融合时更新</td></tr>
        <tr><td>评分</td><td>暂停中</td><td>—</td><td>—</td><td>规则优化后恢复</td></tr>
      </tbody>
    </table>
    <div class="callout">
      <b>每周总消耗</b>：约25-50K tokens（采集8-12K + 分类3-5K + 推荐理由12-31K + HTML生成2-3K + 标签迭代5-10K + 摘要推送3-5K）。<br>
      <b>采集窗口</b>：每次采集过去 {MAX_ARTICLE_AGE_DAYS} 天的资讯，非"当天"。
    </div>
    <div class="callout callout-warning">
      <b>低成本方案</b>（积分紧张时使用）：<br>
      1. <b>关闭推荐理由生成</b> → 节省12-31K tokens/次（最大节省项）<br>
      2. <b>缩短采集窗口</b> → 从{MAX_ARTICLE_AGE_DAYS}天降至3天，减少采集量<br>
      3. <b>暂停T3信源</b> → 只保留T1+T2核心信源，减少采集量<br>
      4. <b>跳过分类关键词匹配</b> → 不分类，只做相关性过滤（不推荐，影响筛选体验）<br>
      <b>推荐策略</b>：优先关闭推荐理由生成（方案1），可节省约50%的每周积分消耗。
    </div>
  </div>

  <div class="section">
    <h3>技术架构</h3>
    <ul>
      <li><b>前端</b>：纯静态 HTML + CSS + JavaScript，无后端依赖</li>
      <li><b>托管</b>：GitHub Pages</li>
      <li><b>采集</b>：Python + feedparser（RSS-first 策略，0个403错误）</li>
      <li><b>自动化</b>：WorkBuddy 定时任务（3个）：周一 01:00 资讯更新 / 03:00 标签池迭代 / 06:00 摘要推送</li>
      <li><b>数据格式</b>：JSON（结构化存储） → HTML（展示层生成）</li>
    </ul>
  </div>

  <div class="section">
    <h3>数据流</h3>
    <p>资讯看板的数据流：</p>
    <ul>
      <li>RSS 信源（L1域名→L2频道）→ collector.py 采集 → raw_YYYYMMDD.json</li>
      <li>原始数据 → 相关性过滤（RELEVANCE/IRRELEVANT关键词）→ 分类（事件类型+涉及领域）</li>
      <li>分类数据 → generator.py → index.html</li>
    </ul>
    <p style="margin-top:12px;">企业库的数据流：</p>
    <ul>
      <li>多源数据（书籍/PDF/xlsx/mapping）→ 提取脚本 → *_companies.json</li>
      <li>多源 JSON → merge_v2.py 融合去重 → all_enterprises.json（17字段统一schema）</li>
      <li>融合数据 → gen_enterprise.py → enterprise.html</li>
    </ul>
  </div>

  <div class="section">
    <h3>规则维护原则</h3>
    <div class="callout">
      <b>本页面是网站所有规则的唯一真相源（Single Source of Truth）。</b><br>
      所有展示规则、筛选逻辑、推送机制、定时任务频率、字段定义、分类体系变更均在此页面维护。<br>
      每次网站有任何规则变更（筛选渠道调整、展示规则修改、推送逻辑变更、频率调整等），<b>必须同步更新本页面</b>并重新生成 about.html。
    </div>
  </div>

  <div class="section">
    <h3>关于我们</h3>
    <p>Silver Pulse 银脉由<b>艾年</b>公众号主理人小爽运营，专注于银发经济领域的投融资资讯和企业研究。</p>
    <p>使命：<b>以海外为镜，照中国之路</b>。每一篇分析的终点都是回答——看懂这家企业，中国的银发经济创业者能学到什么？</p>
  </div>

</div>

<div class="footer">
  <p>Silver Pulse 银脉 · 银发经济投融资资讯聚合 + 企业数据库</p>
  <p>© 2026 艾年 · 以海外为镜，照中国之路</p>
</div>

</div>

<script>
function switchTab(tabName, event) {{
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('tab-' + tabName).classList.add('active');
}}
</script>

</body>
</html>'''

    out_path = os.path.join(OUTPUT_DIR, "about.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Also write to root for GitHub Pages
    root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "about.html")
    with open(root_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated: {out_path}")
    print(f"Enterprise count: {ent_count}")
    print(f"Sources: {len(SOURCES)} (T1={t1_count} T2={t2_count} T3={t3_count})")
    return out_path


if __name__ == "__main__":
    generate()
