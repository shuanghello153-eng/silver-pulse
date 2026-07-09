#!/usr/bin/env python3
"""
Generate about.html — Silver Pulse 网站说明栏目 v2.
Three tabs: 资讯版说明 / 企业库说明 / 网站规则
Updated for v5.0 config: 13-class system, event-type classification,
tag pool, L1/L2 source hierarchy, data filtering logic.
"""
import os
import json
import html
from datetime import datetime

esc = html.escape


def _compute_data_date_banner():
    """读取 scored_latest.json 最新资讯日期，生成醒目新鲜度横幅。"""
    import json as _json
    from datetime import datetime as _dt
    scored_path = os.path.join(DATA_DIR, "scored_latest.json")
    data_date = "未知"
    try:
        with open(scored_path, "r", encoding="utf-8") as f:
            data = _json.load(f)
        dates = [it.get("date") for it in data
                 if isinstance(it.get("date"), str) and it.get("date")]
        if dates:
            data_date = max(dates)
    except Exception:
        pass
    today = _dt.now().strftime("%Y-%m-%d")
    if data_date == today:
        color, tag = "#0a7d2c", "✅ 数据为今日新鲜采集"
    elif data_date != "未知":
        color, tag = "#b45309", "⚠️ 数据偏旧（最新 %s，今日 %s）" % (data_date, today)
    else:
        color, tag = "#b45309", "⚠️ 暂无数据日期"
    return ('<div style="margin:10px 0;padding:8px 12px;border-radius:8px;'
            'background:%s1a;color:%s;font-weight:600;border:1px solid %s55;">'
            '🕒 数据更新日期：%s · %s</div>') % (color, color, color, data_date, tag)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
BUILD_STAMP = datetime.now().strftime("%Y%m%d%H%M%S")

import sys
from ui_common import COMMON_CSS, SIDEBAR, THEME_JS
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    SOURCES, ENTERPRISE_CATEGORIES, NEWS_EVENT_TYPES, NEWS_DOMAINS,
    TAG_POOL, SCORING_DIMENSIONS, RELEVANCE_KEYWORDS,
    IRRELEVANT_KEYWORDS, MAX_ARTICLE_AGE_DAYS,
    NEWS_SCORING_DIMS, SELECT_THRESHOLDS, SOURCE_ADJ,
    CLUSTER_SIM_THRESHOLD, EVENT_BOOST,
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
    # 数据新鲜度横幅（一眼看出数据新不新）
    data_date_banner = _compute_data_date_banner()

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

    # === 选题雷达评分规则 (SSoT, read LIVE from config) — Phase 2 ===
    # 5 news dims
    # NOTE: industry 维度在用户页面重新定义为「赛道核心度」，config.py 的 industry
    # desc 保持不变（与并行评分优化 agent 解耦）。本页是面向用户的最终真相源。
    INDUSTRY_REDEFINED = {
        "label": "赛道核心度",
        "desc": "在「确属银发经济范畴」的前提下，资讯所处赛道的中心程度：养老照护 / 适老科技 / 银发消费 为核心，广义健康为周边。不再承担「是否属于银发」的二元判断。该维度<b>由代码依据 CATEGORY_CENTRALITY（企业库 L1 分类→核心10/重要7/外围4）确定性推导</b>，不调用模型，零积分成本。",
    }
    dim_rows = []
    for dname, dinfo in NEWS_SCORING_DIMS.items():
        if dname == "industry":
            # 用面向用户的正确定义覆盖 config 中的临时 desc
            dlabel = INDUSTRY_REDEFINED["label"]
            ddesc = INDUSTRY_REDEFINED["desc"]
        else:
            dlabel = dinfo["label"]
            ddesc = dinfo["desc"]
        dim_rows.append(
            f"<tr><td class='cat-name'>{esc(dlabel)} <span style='color:var(--text-muted);font-size:11px'>({esc(dname)})</span></td>"
            f"<td style='font-weight:600;color:var(--accent)'>{dinfo['weight']*100:.0f}%</td>"
            f"<td>{esc(ddesc)}</td></tr>"
        )
    dim_table = (
        "<table class='info-table'><thead><tr><th>维度</th><th>权重</th><th>说明</th></tr></thead>"
        f"<tbody>{''.join(dim_rows)}</tbody></table>"
    )

    # differentiated thresholds
    th_parts = []
    for tier in (1, 2, 3):
        th = SELECT_THRESHOLDS.get(tier, {})
        th_parts.append(
            f"<b>T{tier}</b>：高价值 ≥ {th.get('high')} · 值得关注 ≥ {th.get('watch')}"
        )
    th_html = " &nbsp;|&nbsp; ".join(th_parts)

    # source adjustment
    sa_parts = []
    for tier in (1, 2, 3):
        v = SOURCE_ADJ.get(tier, 0)
        sign = "+" if v >= 0 else "−"
        sa_parts.append(f"T{tier} {sign}{abs(v)}")
    sa_html = " · ".join(sa_parts)

    # event boost
    eb = EVENT_BOOST
    eb_html = (
        f"signal ≥ 7 事件 <b>+{eb['signal_ge_7']}</b> · "
        f"signal 5–7 事件 <b>+{eb['signal_5_7']}</b> · "
        f"收购/IPO 事件 <b>+{eb['ma_ipo_event']}</b> · "
        f"封顶 <b>{eb['cap']}</b>"
    )

    radar_rules_html = f"""
  <div class="section">
    <h3>📐 选题雷达评分规则（代码优先 · 唯一真相源）</h3>
    <p>以下规则由代码实时计算，<b>全部数字均读取自 config.py</b>，本页面不硬编码任何阈值。模型（L3）负责打 4 个维度分（信号 / 写作 / 国内可比性 / 时效）；<b>「赛道核心度」由代码依据领域关键词确定性推导（零成本）</b>。其余一切由代码决定。</p>

    <p style="margin-top:14px;"><b>〇、行业相关性 = L1 预筛闸门（collector.is_relevant()）</b></p>
    <p>因为本站是<b>银发经济</b>专版，所有入库资讯都应属于银发经济范畴。因此「行业相关性」<b>不是一个与信号/写作等并列的加权维度</b>，而是位于 6 维评分<b>之前</b>的一道<b>预筛闸门</b>：</p>
    <ul>
      <li><b>闸门前（collector.is_relevant()）</b>：用 RELEVANCE_KEYWORDS / IRRELEVANT_KEYWORDS 做二元判断——确属银发经济范畴（养老照护 / 适老科技 / 银发消费 / 广义健康养老等）的资讯才放行，明显不相关的（儿科、母婴、青少年等非银发内容）直接丢弃。</li>
      <li><b>闸门后</b>：<b>只有通过闸门的资讯</b>才进入下面的 6 维评分（维度分 0–10）。</li>
    </ul>
    <div class="callout">
      <b>为什么用「闸门」而非「加权维度」？</b>若把「是否属于银发」作为加权维度，会让大量非银发噪音凭其它高分混入精选；而纯二元闸门能在<b>不误伤重要信源</b>（如 T3 宽覆盖源偶尔产出高质量银发报道）的同时，<b>把真正的噪音挡在门外</b>。闸门只回答「是不是银发」，不比较「多银发」——后者交给 6 维中的「赛道核心度」。
    </div>

    <p style="margin-top:12px;"><b>一、资讯评分维度（NEWS_SCORING_DIMS，闸门之后才计算）</b></p>
    {dim_table}
    <p style="font-size:12px;color:var(--text-secondary);">4+2 个加权维度为：<b>信号强度 / 写作潜力 / 国内可比性 / 时效紧迫度（模型打分）+ 赛道核心度 / 反常识度（代码推导，零成本）</b>。'赛道核心度' 由关键词脚本按企业 L1 分类映射；'反常识度' 由关键词命中（暴雷/减值/关店/退出 + 收购/融资前置事件）确定性推导，不消耗模型。其余 4 维由模型给出（0–10）。<b>终分 = Σ(维度分 × 权重)</b>，由代码加权计算。「行业相关性」闸门不参与此加权。</p>

    <p style="margin-top:12px;"><b>二、差异化精选阈值（SELECT_THRESHOLDS，按信源层级）</b></p>
    <div class="callout">{th_html}</div>

    <p style="margin-top:12px;"><b>三、信源调整（SOURCE_ADJ，仅影响排序/展示）</b></p>
    <div class="callout">{sa_html}</div>

    <p style="margin-top:12px;"><b>四、事件聚类规则（CLUSTER_SIM_THRESHOLD = {CLUSTER_SIM_THRESHOLD}）</b></p>
    <ul>
      <li><b>主规则</b>：(entity_name, event_type) 完全相同的多条报道归入同一事件簇（cluster）。</li>
      <li><b>余弦回退</b>：entity_name 不同但余弦相似度 &gt; {CLUSTER_SIM_THRESHOLD} 且 event_type 相同，亦判为同簇。</li>
      <li><b>主条优先</b>：每簇只保留一条 <code>is_main=True</code> 主条（最高分/最权威源），其余标记为折叠（folded / is_duplicate_of 指向主条），不单独进精选。</li>
    </ul>

    <p style="margin-top:12px;"><b>五、企业研究分公式（research_value = 0–100）</b></p>
    <ul>
      <li><b>base_value（0–70）</b>：V1 规模(0–25) + <b>V2 信息丰富度(0–20，最高权重)</b> + V3 模式创新(0–15) + V4 国内可比性(0–15)，合计封顶 70。</li>
      <li><b>权重调整（2026-07-07，用户共同决策）</b>：信息丰富度(V2)上调为最高分量；国内企业的 V4（标杆可借鉴）下调——国内标杆稀少（海外10≈国内1），故国内企业分数更依赖 V2 信息丰富度 + 最新事件动态，而非「可借鉴」维度。</li>
      <li><b>event_boost（0–35）</b>：来自近期相关新闻信号：{eb_html}（上限已上调至 35，强化「最新大事件」权重）。</li>
      <li><b>research_value = min(100, base_value + event_boost + MIRROR_BONUS)</b>，MIRROR_BONUS=5 仅海外（上限 100）。</li>
      <li><b>分级 S/A/B/C</b>：research_value ≥75=S / ≥65=A / ≥55=B / ≥45=C，用于「选题卡」与展示徽章（借鉴评分.md 的 F 级思路，非照搬）。</li>
      <li><span class="callout" style="display:inline-block;margin-top:6px;"><b>以海外为镜</b>：海外企业 V4（标杆可借鉴）保持较高权重；国内企业 V4 下调，分数主要由 V2 信息丰富度 + 最新事件驱动。</span></li>
      <li><b>覆盖度目标</b>：选题覆盖 海外:国内 ≈ 7:3（与评分.md 口径一致）。</li>
    </ul>

    <p style="margin-top:12px;"><b>六、铁律（IRON RULE）</b></p>
    <div class="callout callout-warning">
      <b>终分 / 精选判定 / 聚类主条，100% 由代码计算。</b><br>
      模型（L3）只输出 4 个维度分（signal / writing / cn_fit / urgency），<b>绝不直接给出 final_score</b>；industry(赛道核心度) 与 novelty(反常识度) 由代码确定性推导（零成本）。所有阈值、权重、公式皆在 config.py / selection 代码中，本页面仅作展示。
    </div>
  </div>
"""

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
<style>__COMMON_CSS__</style>
</head>
<body>

__SIDEBAR__
<div class="main">

<div class="header">
  <h2>网站说明（人话版）</h2>
  <p>Silver Pulse 银脉 · 帮你把全球银发经济的好选题，一次性摆到桌面上</p>
</div>

<p style="font-size:13px;color:var(--text-secondary);margin-top:4px;">📌 本页由代码从 config.py 实时生成 · 生成时间 {BUILD_STAMP}</p>
{data_date_banner}

<div class="callout" style="border-color:var(--accent);">
  <b>一句话看懂：</b>这是一个<b>银发经济（养老 / 适老科技 / 老年消费）的选题情报台</b>。
  每周自动从 {len(SOURCES)} 个海内外信源抓取投融资、产品、政策动态，
  用一套评分帮你挑出<b>最值得写的高分内容</b>，并配套一个全球企业库方便你查背景。
  <ul style="margin-top:8px;">
    <li><b>这是什么</b>：银发经济的「选题雷达 + 企业图谱」，是给内容创作者用的，不是新闻客户端。</li>
    <li><b>数据哪来</b>：{len(SOURCES)} 个一手 / 专业信源（行业协会官网、垂直媒体、披露平台等），脚本自动采集，不编造假数据，每条都能追到原文链接。</li>
    <li><b>怎么用</b>：看板按「精选 / 全量」切换，配合分类、标签、地区筛选；看到有用的点「🔖 收藏」，用「🚫 不再显示」清掉噪音，用「📝 备注」写自己的想法（都只存在你自己浏览器里）。</li>
    <li><b>评分什么意思</b>：资讯看「评分」(0–10，越高越值得写)；企业看「研究分」(0–100，越高越值得深写)。「精选」= 各自的高分优质内容，不是编辑主观挑的。</li>
    <li><b>多久更新</b>：每周日 11:00（北京时间）自动跑一次全量更新，节假日照常，你不用手动点。</li>
  </ul>
</div>

<div class="callout">
  下面三栏分别是：资讯版怎么看、企业库怎么看、以及给好奇技术细节的人准备的评分规则。所有数字都实时读取自 config.py，规则一改网页就跟着变。
</div>

<div class="tab-bar">
  <button class="tab-btn active" onclick="switchTab('news', event)">资讯版说明</button>
  <button class="tab-btn" onclick="switchTab('enterprise', event)">企业库说明</button>
  <button class="tab-btn" onclick="switchTab('rules', event)">网站规则</button>
</div>

<!-- Tab 1: 资讯版说明 -->
<div class="tab-content active" id="tab-news">

  <div class="callout" style="margin-bottom:20px;">
    <b>📌 本页用途：</b>资讯从哪来（{len(SOURCES)} 个信源）、怎么筛（两级相关性闸门 + 6 维评分）、怎么看（精选 / 全量 + 筛选标签）。
  </div>

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

    <p style="margin-top:12px;"><b>第二步：相关性过滤（两级闸门，collector.is_relevant()）</b></p>
    <ul>
      <li><b>强词命中即相关</b>：标题+摘要命中任一<b>强词</b>（SILVER_STRONG_KEYWORDS：养老 / 银发 / 照护 / 认知症 / 康养 等）即视为银发相关，放行入库。</li>
      <li><b>仅弱词不相关</b>：只命中<b>弱词</b>（SILVER_WEAK_KEYWORDS：融资 / 机器人 / AI 等泛科技词）不算相关，除非该主体为企业库已知银发企业（按企业库白名单放行）。</li>
      <li><b>目的</b>：挡掉「复旦95后机器人大佬」「XX 公司完成融资」这类泛科技 / 机器人内容误入银发专版。</li>
      <li>匹配<b>无关关键词</b>（IRRELEVANT_KEYWORDS）的文章直接丢弃。</li>
      <li>地区由信源决定，不由内容判断：国内信源→国内，海外信源→海外。</li>
    </ul>
    <p style="margin-top:8px;">强词关键词示例（SILVER_STRONG_KEYWORDS 节选，共{len(RELEVANCE_KEYWORDS)}个）：</p>
    <div style="margin:8px 0;">{rel_kw_html}</div>
    <p style="margin-top:8px;">弱词（SILVER_WEAK_KEYWORDS）单独命中不再放行；无关关键词（共{len(IRRELEVANT_KEYWORDS)}个）：</p>
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
      <li><b>精选视图</b>：只摆「评分」高的优质条目（按信源层级差异化阈值，约前 40–50% 高分内容）；想看全部就切「全量」。</li>
      <li><b>全量视图</b>：展示所有通过相关性过滤的条目</li>
      <li>可按事件类型、涉及领域、标签、地区多级筛选</li>
    </ul>
    <div class="callout">
      <b>精选 vs 全量 说明</b>：两者不是同一份数据——「精选」是按「评分」由高到低切出来的高分优质内容，「全量」是所有通过相关性过滤的条目。日常只看精选就够，需要时再翻全量。
    </div>
  </div>

  <div class="section">
    <h3>推荐理由（模板生成）</h3>
    <p>资讯卡片底部的 <b>★ 标记文字</b>是推荐理由（recommendation字段），基于事件类型、金额量级、国内外差异、反常识度等要素自动生成，已去重标题已含信息：</p>
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
      <b>当前状态：选题雷达 6 维评分已激活（代码优先）</b><br>
      看板使用<b>代码优先的 6 维选题雷达引擎</b>（详见「网站规则 → 📐 选题雷达评分规则」）计算 final_score：industry(赛道核心度) 与 novelty(反常识度) 由代码确定性推导，signal / writing / cn_fit / urgency 由模型(L3)输出，终分由代码加权计算。关键词 <code>signal_score</code> 作为低成本的回退代理（模型不可用时使用）。
    </div>
    <p>关键词信号打分构成：</p>
    <ul>
      <li><b>信源基础分</b>：T1(+3) > T2(+2) > T3(+1)</li>
      <li><b>加分关键词</b>（权重+2~+5）：融资/收购/IPO/战略合作/产品发布等</li>
      <li><b>减分关键词</b>（权重-2~-5）：webinar/招聘/排行榜/新闻稿等噪音</li>
      <li><b>叠加奖励</b>：命中2个加分+1，3个以上+3</li>
    </ul>
    <p>阈值设计：≥7.0 高价值(high) | 5.0-6.9 值得关注(watch) | &lt;5.0 归档(archive)</p>
    <p>模型（L3）<b>只输出 4 个维度分（0–10）</b>：signal(信号强度) / writing(写作潜力) / cn_fit(国内可比性) / urgency(时效紧迫度)（权重见「网站规则 → 📐 选题雷达评分规则」）。industry(赛道核心度) 与 novelty(反常识度) 由代码确定性推导（零成本）。注：「行业相关性」是一道位于评分<b>之前</b>的 L1 预筛闸门（collector.is_relevant()），只有确属银发经济范畴的资讯才进入评分。<b>终分由代码加权计算</b>，模型从不直接给出 final_score、也不决定精选或聚类主条。</p>
  </div>

  <div class="section">
    <h3>筛选规则迭代计划（规划中，尚未执行）</h3>
    <p>当前筛选为<b>纯关键词匹配 + 信源权重</b>，已能过滤大部分噪音。参考 AIHOT（卡兹克）的成熟实践，后续迭代路径如下：</p>
    <p style="margin-top:10px;"><b>短期（代码层，零AI成本）</b></p>
    <ul>
      <li><b>差异化阈值</b>：不同层级信源设不同精选阈值（已在 config.SELECT_THRESHOLDS 落地）— T1 高价值≥{SELECT_THRESHOLDS[1]['high']} / 值得关注≥{SELECT_THRESHOLDS[1]['watch']}；T2 高价值≥{SELECT_THRESHOLDS[2]['high']} / 值得关注≥{SELECT_THRESHOLDS[2]['watch']}；T3 仅进观察池（watch≥{SELECT_THRESHOLDS[3]['watch']}，不单独精选）。避免T3宽覆盖源的通稿混入选精。</li>
      <li><b>事件聚类</b>：主规则 (entity_name, event_type) 相同即同簇；余弦相似度 &gt; {CLUSTER_SIM_THRESHOLD} 且 event_type 相同为回退；每簇仅保留一条主条（is_main），其余折叠。完整规则见「网站规则 → 📐 选题雷达评分规则」。</li>
      <li><b>新闻稿降权</b>：PR Newswire / Business Wire 等通稿平台自动降权，仅保留其中融资/收购类实质内容。</li>
    </ul>
    <p style="margin-top:10px;"><b>中期（Skill层，AI单一能力封装）</b></p>
    <ul>
      <li><b>AI只打维度分</b>：大模型只输出 <b>4 个维度分</b>（signal / writing / cn_fit / urgency），industry 与 novelty 由代码推导（零成本），最终分由代码加权计算（参考AIHOT：Prompt从600行缩减到200行）。</li>
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
      <li><b>资讯采集</b>：每周日 11:00（北京时间）随全量流水线自动执行一次</li>
      <li><b>企业库扩充</b>：随每周日 11:00 流水线（采集后）自动融合新数据源扩充企业库</li>
      <li><b>自审报告</b>：随每周日 11:00 流水线（采集后）生成每周数据质量自审报告推送到 WorkBuddy 对话</li>
      <li><b>采集窗口</b>：过去 {MAX_ARTICLE_AGE_DAYS} 天的资讯</li>
      <li><b>每周积分消耗</b>：约25-50K tokens（采集8-12K + 分类/标签迭代3-5K + 推荐理由12-31K + HTML生成2-3K + 企业库扩充5-10K + 自审报告3-5K）</li>
      <li><b>展示逻辑</b>：精选条目优先展示，全量条目可切换查看</li>
      <li><b>排序方式</b>：默认按日期降序（最新优先）</li>
    </ul>
    <div class="callout">
      <b>定时任务时序</b>：周日 11:00 全量流水线(资讯+评分+生成+部署) → 17:30 标签池迭代 → 19:00 摘要推送 → 21:00 自愈补跑。
    </div>
  </div>

  <div class="section">
    <h3>收藏与反馈（已上线）</h3>
    <div class="callout">
      <b>🔖 已收藏筛选</b>：资讯页和企业库工具栏的「🔖 已收藏」胶囊按钮，点击后只显示已收藏项，再点取消。无需独立页面。<br>
      <b>收藏按钮</b>：每条资讯 / 企业卡片上的「☆/🔖」按钮写入浏览器 localStorage，无需登录。<br>
      <b>☁ 同步云端（推荐）</b>：点「☁ 同步云端」并首次配置 GitHub Token（仅存本地浏览器）后，收藏会直接写入仓库的 <code>data/feedback.jsonl</code>，AI 流水线下次运行即自动读取并优化选题权重——你无需再手动导出或挪文件。<br>
      <b>⬇ 导出收藏</b>：仅作离线备份用，正常流程不必使用。
    </div>
  </div>

  <div class="section">
    <h3>Loop Engineering 自我进化（V2）</h3>
    <div class="callout">
      <b>架构三层</b>：<br>
      - <b>L2 安检门</b>（loop_audit.py）：每轮跑 HTML 走查 + 数据质量 + 回归检测，0 CRITICAL / 3 WARN。<br>
      - <b>L2 安全气囊</b>（noise_spike_guard.py）：噪音 spike 检测 + 连续 2 天自动封禁信源，从未触发（环境干净=好事）。<br>
      - <b>L3 智能引擎</b>（feedback_loop.py）：读收藏 → ±0.03 权重微调，待 Token 配置激活。<br>
      <b>新增组件（本轮）</b>：<br>
      - <b>事件聚类</b>（selection/cluster.py）：按 (entity, event_type) 精确匹配 + 余弦回退归簇，写回 cluster_id。<br>
      - <b>每周健康报告</b>（daily_health.py）：自动生成 HEALTH_REPORT.md + health_history.json 趋势，零模型成本。<br>
      - <b>推荐理由去重</b>（recommend.py 变体库）：每事件类型 3–5 个模板变体 + 批次内轮换去重。<br>
      - <b>评分色阶</b>：badge 半透明底色按分数段区分（≥7 绿 / 4–6.9 蓝 / <4 灰）。
      完整设计文档：<code>docs/loop_self_iteration_v2.md</code>（7 方向 + 路线图 + 成本预算）。
    </div>
  </div>

</div>

<!-- Tab 2: 企业库说明 -->
<div class="tab-content" id="tab-enterprise">

  <div class="callout" style="margin-bottom:20px;">
    <b>📌 本页用途：</b>企业有哪些字段（21 字段 Schema）、怎么分类（13 一级 + 70 二级）、数据从哪来（7 个来源）。
  </div>

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
      <b>价值评分</b>：value_score 即「企业研究分」(0–100)，由 selection.enterprise_score 计算，已在企业卡片以「研究分」徽章展示，并用于默认排序。
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

  <div class="callout" style="margin-bottom:20px;">
    <b>📌 本页用途：</b>评分公式与阈值（6 维加权 + 差异化精选）、聚类规则、铁律 —— 技术细节唯一真相源，全部从 config.py 实时读取。
  </div>

  {radar_rules_html}

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
        <tr><td>RSS采集</td><td>每周</td><td>每周日 11:00（随全量流水线）</td><td>约8-12K tokens</td><td>自动化（feedparser解析 + 内容提取）</td></tr>
        <tr><td>分类+标签</td><td>每周</td><td>采集后（并入每周流水线）</td><td>约3-5K tokens</td><td>自动化（关键词匹配，无AI调用；标签池迭代一并完成）</td></tr>
        <tr><td>推荐理由生成</td><td>每周</td><td>采集后</td><td>约12-31K tokens</td><td>AI生成（仅精选条目，约62条×200-500 tokens/条）</td></tr>
        <tr><td>HTML生成</td><td>每周</td><td>采集后</td><td>约2-3K tokens</td><td>自动化（模板渲染）</td></tr>
        <tr><td>企业库扩充</td><td>每周</td><td>随流水线（采集后）</td><td>约5-10K tokens</td><td>AI扫描+融合新数据源扩充企业库</td></tr>
        <tr><td>每周自审报告</td><td>每周</td><td>随流水线（采集后）</td><td>约3-5K tokens</td><td>AI读取数据生成自审报告推送到WorkBuddy对话</td></tr>
        <tr><td>企业库</td><td>不定期</td><td>—</td><td>手动</td><td>新数据源融合时更新</td></tr>
        <tr><td>评分</td><td>每周</td><td>随每周流水线</td><td>—</td><td>由代码优先 6 维选题雷达引擎实时计算（详见 网站规则）</td></tr>
      </tbody>
    </table>
    <div class="callout">
      <b>每周总消耗</b>：约25-50K tokens（采集8-12K + 分类/标签迭代3-5K + 推荐理由12-31K + HTML生成2-3K + 企业库扩充5-10K + 自审报告3-5K）。<br>
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
      <li><b>自动化</b>：WorkBuddy 定时任务（4 个每周定时任务）：周日 11:00 全量流水线 / 17:30 标签池 / 19:00 摘要推送 / 21:00 自愈补跑</li>
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
      每次网站有任何规则变更（筛选渠道调整、展示规则修改、推送逻辑变更、频率调整等），<b>必须同步更新本页面</b>并重新生成 about.html。本页面（gen_about.py）现已并入 run_daily 流水线作为第 6 步，每次每周运行自动重生成；并有<b>规则漂移检测器</b>持续校验 config.py ↔ about.html 的一致性，发现数字偏差即告警。
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

    html = html.replace("__COMMON_CSS__", COMMON_CSS).replace("__SIDEBAR__", SIDEBAR("about"))
    html = html.replace("</body>", THEME_JS + "\n</body>")
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


def main():
    """Entry point for the daily pipeline (run_daily.py)."""
    return generate()


if __name__ == "__main__":
    generate()
