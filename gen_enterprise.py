#!/usr/bin/env python3
"""
gen_enterprise.py — v6 compact card layout
New schema: name, region, category_l1, category_l2, tags, description, highlights,
            funding_latest, funding_total, investors, founded, value_score,
            source, crunchbase_url, website_url
13-class system, no P0/P1/P2, no numbering in display.
All fields directly visible — no click-to-expand.
Empty fields are hidden (not displayed).

v6 changes:
- 精选/全量切换 (curated = has funding or has real highlights; all = everything)
- 搜索范围扩展到 name + description + tags
- 结果计数显示
- 更紧凑的布局
- 融资信息更醒目
"""
import json
import os
import html
import hashlib
from datetime import datetime


def _url_hash(s):
    """Stable short hash of a string for use as an HTML anchor id."""
    return hashlib.md5((s or "").encode("utf-8")).hexdigest()[:10]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
BUILD_STAMP = datetime.now().strftime("%Y%m%d%H%M%S")

# Import from config
import sys
from ui_common import COMMON_CSS, SIDEBAR, THEME_JS, FEEDBACK_CSS, FEEDBACK_JS
sys.path.insert(0, BASE_DIR)
from config import ENTERPRISE_CATEGORIES

# 13 L1 categories (no numbering in display)
L1_CATS = list(ENTERPRISE_CATEGORIES.keys())


def load_enterprises():
    path = os.path.join(DATA_DIR, "enterprise/all_enterprises.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def esc(text):
    """HTML escape"""
    if not text:
        return ""
    return html.escape(str(text))


def is_curated(ent):
    """Determine if an enterprise is 'curated' (精选).
    Curated = has real funding info OR has meaningful highlights."""
    # Has funding_latest with real data
    fl = ent.get("funding_latest")
    if fl and isinstance(fl, dict):
        display = fl.get("display", "")
        if display and "未披露" not in display and "未公开" not in display:
            return True
    # Has funding_total with real data
    ft = ent.get("funding_total")
    if ft and isinstance(ft, dict):
        display = ft.get("display", "")
        if display and "未披露" not in display and "未公开" not in display:
            return True
    # Has investors
    inv = ent.get("investors")
    if inv:
        inv_str = inv if isinstance(inv, str) else ", ".join(inv)
        if inv_str and "未披露" not in inv_str:
            return True
    # Has IPO
    desc = ent.get("description", "")
    if desc and ("上市" in desc or "IPO" in desc):
        return True
    return False


def build_card(ent, ent_scores_map=None, news_map=None, competitors=None):
    """Build a compact horizontal card for one enterprise.
    All fields directly visible, empty fields hidden."""
    name = esc(ent.get("name", ""))
    region = ent.get("region", "")
    cat_l1 = esc(ent.get("category_l1", ""))
    cat_l2 = esc(ent.get("category_l2", ""))
    tags = ent.get("tags", [])
    description = esc(ent.get("description", ""))
    highlights = esc(ent.get("highlights", ""))
    business_model = esc(ent.get("business_model", ""))

    serial = ent.get("serial", "")
    rv = None
    deep = None
    top_event = None
    recent_news = []
    if ent_scores_map:
        sc = ent_scores_map.get(serial)
        if sc:
            rv = sc.get("research_value") or ent.get("value_score")
            deep = bool(sc.get("worth_deep_write"))
            top_event = sc.get("top_event")
            if news_map:
                rids = sc.get("related_news_ids", []) or []
                for rid in rids[:2]:
                    n = news_map.get(rid)
                    if not n:
                        # fallback: prefix match on url
                        key = (rid or "").split("?")[0]
                        for u, n2 in news_map.items():
                            if key and u.startswith(key):
                                n = n2
                                break
                    if n:
                        recent_news.append({
                            "title": n.get("title", "") or n.get("title_cn", ""),
                            "date": n.get("date", ""),
                            "url": n.get("url", ""),
                        })

    # Funding
    fund_latest = ent.get("funding_latest")
    fund_total = ent.get("funding_total")
    investors = ent.get("investors")
    founded = esc(ent.get("founded", ""))

    # Source/links
    source = esc(ent.get("source", ""))
    crunchbase_url = ent.get("crunchbase_url", "")
    website_url = ent.get("website_url", "")

    # Serial for data attribute
    serial = ent.get("serial", "")
    curated = is_curated(ent)

    # --- Build card HTML ---
    parts = []

    # Header line: name + category badge + tags + region
    header_parts = [f'<span class="ent-name">{name}</span>']

    # Category badge (L1 · L2)
    if cat_l1:
        cat_text = cat_l1
        if cat_l2:
            cat_text += f" · {cat_l2}"
        header_parts.append(f'<span class="ent-badge badge-cat">{cat_text}</span>')

    # Tags (醒目颜色)
    if tags and isinstance(tags, list):
        tags_html = "".join(
            f'<span class="ent-tag">{esc(t)}</span>' for t in tags[:5] if t
        )
        if tags_html:
            header_parts.append(f'<span class="ent-tags">{tags_html}</span>')

    # Region (低调，放最后)
    if region:
        header_parts.append(f'<span class="ent-badge badge-region">{esc(region)}</span>')

    # Research-value badge — 只显示数字（删"研究价值"文字 + "值得深写"标签）
    if rv is not None:
        header_parts.append(f'<span class="badge-rv">{esc(str(rv))}</span>')
    # 收藏按钮（localStorage 反馈）
    if serial:
        header_parts.append(f'<button class="fav-btn" data-type="ent" data-id="{esc(serial)}"><span class="ico">☆</span><span class="lbl">收藏</span></button>')

    parts.append(f'<div class="ent-header">{" ".join(header_parts)}</div>')

    # Description line
    if description:
        parts.append(f'<div class="ent-desc">{description}</div>')

    # Highlights (小字)
    if highlights:
        parts.append(f'<div class="ent-highlights">★ {highlights}</div>')

    # Meta line: funding / investors / founded / links
    meta_parts = []

    # Latest funding
    if fund_latest and isinstance(fund_latest, dict):
        display = fund_latest.get("display", "")
        if display and "未披露" not in display and "未公开" not in display:
            meta_parts.append(f'<span class="meta-item meta-fund">{esc(display)}</span>')

    # Total funding
    if fund_total and isinstance(fund_total, dict):
        display = fund_total.get("display", "")
        if display and "未披露" not in display and "未公开" not in display:
            meta_parts.append(f'<span class="meta-item meta-fund-total">{esc(display)}</span>')

    # Investors
    if investors:
        inv_str = investors if isinstance(investors, str) else ", ".join(investors)
        if inv_str and "未披露" not in inv_str:
            meta_parts.append(f'<span class="meta-item">投资方: {esc(inv_str)}</span>')

    # Founded
    if founded:
        meta_parts.append(f'<span class="meta-item">成立: {founded}</span>')

    # Business model
    if business_model:
        meta_parts.append(f'<span class="meta-item meta-biz">{business_model}</span>')

    # Source
    if source:
        meta_parts.append(f'<span class="meta-item meta-source">{source}</span>')

    # Links (small, right-aligned)
    link_parts = []
    if crunchbase_url:
        link_parts.append(f'<a href="{esc(crunchbase_url)}" target="_blank" rel="noopener" class="ent-link">Crunchbase</a>')
    if website_url:
        link_parts.append(f'<a href="{esc(website_url)}" target="_blank" rel="noopener" class="ent-link">官网</a>')
    if link_parts:
        meta_parts.append(f'<span class="meta-links">{" · ".join(link_parts)}</span>')

    if meta_parts:
        parts.append(f'<div class="ent-meta">{" ".join(meta_parts)}</div>')

    # 近期热点 — related news (Phase 2), omitted if none.
    # Link jumps to the corresponding news card on index.html via its anchor.
    if recent_news:
        rec_items = []
        for rn in recent_news:
            if rn["url"]:
                link = "index.html#news-" + _url_hash(rn["url"])
            else:
                link = "index.html"
            t = esc(rn["title"])
            d = f' <span class="ent-recent-date">({esc(rn["date"])})</span>' if rn["date"] else ""
            rec_items.append(
                f'<a href="{esc(link)}" class="ent-recent-link">{t}</a>{d}'
            )
        parts.append(f'<div class="ent-recent">🔥 近期热点: {" · ".join(rec_items)}</div>')

    # 竞争对手 — other enterprises sharing an L1 category (category_l1) or the
    # same normalized business_model, ranked by research_value, top 5. Omitted if none.
    if competitors:
        comp_items = []
        for c in competitors:
            anchor = "ent-" + _url_hash(c.get("serial", "")) if c.get("serial") else ""
            href = "#" + anchor if anchor else "#"
            rv = c.get("rv")
            rv_badge = ""
            if rv is not None:
                rv_badge = f'<span class="badge-rv">{esc(str(rv))}</span>'
            comp_items.append(
                f'<a href="{href}" class="ent-comp-link">{esc(c.get("name", ""))}</a>'
                f'{rv_badge}'
            )
        if comp_items:
            parts.append(
                f'<div class="ent-competitors">🥊 竞争对手: {" · ".join(comp_items)}</div>'
            )

    # Data attributes for filtering
    search_text = (ent.get("name", "") or "").lower()
    # Also include description and tags in search data
    desc_lower = (ent.get("description", "") or "").lower()
    tags_lower = " ".join((t or "").lower() for t in tags) if isinstance(tags, list) else ""
    # Enhanced: include L1/L2 category + business_model so search is broader
    cat_lower = (cat_l1 or "").lower()
    l2_lower = (cat_l2 or "").lower()
    bm_lower = (business_model or "").lower()
    full_search = f"{search_text} {desc_lower} {tags_lower} {cat_lower} {l2_lower} {bm_lower}"
    cat_attr = cat_l1 if cat_l1 else ""
    region_attr = "1" if region == "国内" else "2"
    curated_attr = "1" if curated else "0"
    ent_anchor = "ent-" + _url_hash(serial) if serial else ""

    return (
        f'<div class="ent-card" id="{ent_anchor}" data-region="{region_attr}" '
        f'data-cat="{esc(cat_attr)}" '
        f'data-l2="{esc(cat_l2)}" '
        f'data-name="{esc(full_search)}" '
        f'data-curated="{curated_attr}" '
        f'data-serial="{esc(serial)}">\n'
        + "\n".join(parts) + "\n"
        + '</div>'
    )


def generate():
    enterprises = load_enterprises()
    total = len(enterprises)

    domestic = sum(1 for e in enterprises if e.get("region") == "国内")
    overseas = sum(1 for e in enterprises if e.get("region") == "海外")
    curated_count = sum(1 for e in enterprises if is_curated(e))

    # --- Phase 2: load research-value scores + news map for badges & 近期热点 ---
    ent_scores_map = {}
    news_map = {}
    try:
        with open(os.path.join(DATA_DIR, "enterprise", "enterprise_scores.json"),
                  "r", encoding="utf-8") as f:
            ent_scores_map = json.load(f)
    except Exception:
        ent_scores_map = {}
    try:
        with open(os.path.join(DATA_DIR, "scored_latest.json"),
                  "r", encoding="utf-8") as f:
            for n in json.load(f):
                u = n.get("url")
                if u:
                    news_map[u] = n
    except Exception:
        news_map = {}

    # --- Phase 2: TOP 15 by research_value ---
    top_ranked = []
    for e in enterprises:
        serial = e.get("serial", "")
        sc = ent_scores_map.get(serial)
        if not sc:
            continue
        rv = sc.get("research_value") or e.get("value_score") or 0
        top_ranked.append((rv, e, sc))
    top_ranked.sort(key=lambda t: t[0], reverse=True)
    top_ranked = top_ranked[:15]

    # --- Phase 3: competitors map (guarded) ---
    # For each enterprise, find OTHER enterprises sharing >=1 L1 category
    # (category_l1) OR the same normalized business_model, ranked by
    # research_value, top 5. Omitted when none.
    competitors_map = {}
    try:
        def _rv_of(e):
            sc = ent_scores_map.get(e.get("serial", ""))
            return (sc.get("research_value") if sc else None) or e.get("value_score") or 0

        def _bm_norm(bm):
            return (bm or "").strip().lower().replace(" ", "").replace("/", "")

        for e in enterprises:
            eserial = e.get("serial", "")
            el1 = e.get("category_l1", "")
            ebm = _bm_norm(e.get("business_model", ""))
            cands = []
            for o in enterprises:
                oserial = o.get("serial", "")
                if not oserial or oserial == eserial:
                    continue
                ol1 = o.get("category_l1", "")
                obm = _bm_norm(o.get("business_model", ""))
                share = (el1 and ol1 == el1) or (ebm and obm and ebm == obm)
                if share:
                    cands.append((_rv_of(o), o))
            cands.sort(key=lambda t: t[0], reverse=True)
            competitors_map[eserial] = [
                {
                    "name": o.get("name", ""),
                    "serial": o.get("serial", ""),
                    "rv": rv,
                    "deep": bool((ent_scores_map.get(o.get("serial", "")) or {}).get("worth_deep_write")),
                }
                for rv, o in cands[:5]
            ]
    except Exception:
        competitors_map = {}

    # Category distribution (L1 and L2)
    cat_counts = {}
    l2_counts = {}  # {l1: {l2: count}}
    for e in enterprises:
        l1 = e.get("category_l1", "")
        l2 = e.get("category_l2", "")
        cat_counts[l1] = cat_counts.get(l1, 0) + 1
        if l1 not in l2_counts:
            l2_counts[l1] = {}
        if l2:
            l2_counts[l1][l2] = l2_counts[l1].get(l2, 0) + 1

    # Build cards — 精选优先、研究价值降序（精选视图默认按价值排）
    def _disp_rv(e):
        sc = ent_scores_map.get(e.get("serial", ""))
        return (sc.get("research_value") if sc else None) or e.get("value_score") or 0

    enterprises_sorted = sorted(
        enterprises,
        key=lambda e: (1 if is_curated(e) else 0, _disp_rv(e)),
        reverse=True,
    )
    cards_html = "\n".join(
        build_card(e, ent_scores_map, news_map, competitors_map.get(e.get("serial", "")))
        for e in enterprises_sorted
    )

    # --- Phase 2: 研究价值 TOP 15 企业 ---
    top_html = '<div class="top-section">'
    top_html += '<h3 class="top-title">🏆 研究价值 TOP 15 企业</h3>'
    top_html += '<p class="top-sub">按「研究价值分」排名。与「精选」口径不同：精选=有看点（有融资/亮点），TOP15=价值分最高的 15 家。</p>'
    top_html += '<div class="top-list">'
    for i, (rv, e, sc) in enumerate(top_ranked, start=1):
        region = e.get("region", "")
        name = esc(e.get("name", ""))
        tags_html = " ".join(
            f'<span class="ent-tag">{esc(t)}</span>'
            for t in (e.get("tags") or [])[:5] if t
        )
        te = sc.get("top_event")
        te_html = f'<span class="top-event">近期: {esc(te)}</span>' if te else ""
        top_html += (
            f'<div class="top-row">'
            f'<span class="top-rank">{i}</span>'
            f'<span class="ent-name">{name}</span>'
            f'<span class="badge-rv">{esc(str(rv))}</span>'
            f'<span class="ent-badge badge-region">{esc(region)}</span>'
            f'<span class="ent-tags">{tags_html}</span>'
            f'{te_html}'
            f'</div>'
        )
    top_html += '</div></div>'

    # L1 filter buttons (no numbering)
    cat_buttons = "\n".join(
        f'<button class="f-btn" data-cat="{esc(l1)}">{esc(l1)}<span class="cnt">{cat_counts.get(l1, 0)}</span></button>'
        for l1 in L1_CATS
    )

    # L2 filter buttons grouped by L1 (hidden by default, shown when L1 is selected)
    l2_filter_html = ""
    for l1 in L1_CATS:
        l2_list = ENTERPRISE_CATEGORIES.get(l1, {}).get("l2", [])
        if not l2_list:
            continue
        l2_btns = " ".join(
            f'<button class="f-btn f-btn-l2" data-l2="{esc(l2)}" data-parent="{esc(l1)}">{esc(l2)}<span class="cnt">{l2_counts.get(l1, {}).get(l2, 0)}</span></button>'
            for l2 in l2_list
        )
        l2_filter_html += f'<div class="filter-row l2-row" id="l2-{esc(l1)}" style="display:none;"><span class="f-label">子类</span>{l2_btns}</div>\n'

    html_content = f"""<!-- build:{BUILD_STAMP} -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<title>Silver Pulse 银脉 · 企业库</title>
<style>__COMMON_CSS__</style>
</head>
<body>

__SIDEBAR__
<div class="main">

<div class="header">
  <h2>银发经济企业数据库</h2>
  <p class="header-stats">共 {total} 家企业 · 国内 {domestic} 家 · 海外 {overseas} 家 · 精选 {curated_count} 家 · 13 个一级分类</p>
</div>

{top_html}

<div class="toolbar">
  <div class="filter-row">
    <span class="f-label">视图</span>
    <div class="view-toggle">
      <button class="view-btn active" data-view="curated">精选 ({curated_count})</button>
      <button class="view-btn" data-view="all">全量 ({total})</button>
    </div>
    <span class="f-label" style="margin-left:12px;">地区</span>
    <button class="f-btn active" data-reg="all">全部</button>
    <button class="f-btn" data-reg="1">国内</button>
    <button class="f-btn" data-reg="2">海外</button>
    <input type="text" class="search-inline" id="search" placeholder="搜索企业名称/描述/标签..." oninput="filterEnt()">
    <button class="export-fav" title="导出收藏为 feedback.jsonl">⬇ 导出收藏</button>
  </div>
  <div class="filter-row" id="cat-filter">
    <span class="f-label">分类</span>
    <button class="f-btn active" data-cat="all">全部</button>
    {cat_buttons}
  </div>
  {l2_filter_html}
</div>

<div class="result-count" id="result-count"></div>

<div id="ent-list">
{cards_html}
</div>

<div class="footer">
  <p>Silver Pulse 银脉 · 银发经济企业数据库</p>
  <p>数据来源：选题库 · Stage (Not Age) · 许之怿行业图谱 · 2025 AgeTech Market Map · The AgeTech Revolution</p>
</div>
</div>

<script>
let activeReg = 'all';
let activeCat = 'all';
let activeL2 = 'all';
let activeView = 'curated';

function filterEnt() {{
  const q = document.getElementById('search').value.toLowerCase();
  const cards = document.querySelectorAll('.ent-card');
  let visible = 0;
  const catVisCounts = {{}};
  const l2VisCounts = {{}};

  cards.forEach(card => {{
    const reg = card.dataset.region;
    const cat = card.dataset.cat;
    const l2 = card.dataset.l2 || '';
    const name = (card.dataset.name || '').toLowerCase();
    const curated = card.dataset.curated === '1';

    const regMatch = activeReg === 'all' || reg === activeReg;
    const searchMatch = !q || name.includes(q);
    const catMatch = activeCat === 'all' || cat === activeCat;
    const l2Match = activeL2 === 'all' || l2 === activeL2;
    const viewMatch = activeView === 'all' || curated;

    if (regMatch && searchMatch && viewMatch) {{
      if (cat) catVisCounts[cat] = (catVisCounts[cat] || 0) + 1;
      if (cat && l2) {{
        if (!l2VisCounts[cat]) l2VisCounts[cat] = {{}};
        l2VisCounts[cat][l2] = (l2VisCounts[cat][l2] || 0) + 1;
      }}
      if (catMatch && l2Match) {{
        card.style.display = '';
        visible++;
      }} else {{
        card.style.display = 'none';
      }}
    }} else {{
      card.style.display = 'none';
    }}
  }});

  // Update L1 category counts
  document.querySelectorAll('#cat-filter [data-cat]').forEach(btn => {{
    const c = btn.dataset.cat;
    const cntEl = btn.querySelector('.cnt');
    if (c === 'all') {{
      let allVis = 0;
      Object.values(catVisCounts).forEach(v => allVis += v);
      if (cntEl) cntEl.textContent = allVis;
    }} else {{
      if (cntEl) cntEl.textContent = catVisCounts[c] || 0;
    }}
  }});

  // Update L2 subcategory counts
  document.querySelectorAll('.f-btn-l2').forEach(btn => {{
    const parent = btn.dataset.parent;
    const l2 = btn.dataset.l2;
    const cntEl = btn.querySelector('.cnt');
    if (cntEl) cntEl.textContent = (l2VisCounts[parent] && l2VisCounts[parent][l2]) || 0;
  }});

  // Update result count
  const rc = document.getElementById('result-count');
  if (rc) {{
    const viewLabel = activeView === 'curated' ? '精选' : '全量';
    const regLabel = activeReg === 'all' ? '全部地区' : (activeReg === '1' ? '国内' : '海外');
    const catLabel = activeCat === 'all' ? '全部分类' : activeCat;
    const l2Label = activeL2 === 'all' ? '' : ' · ' + activeL2;
    rc.textContent = `展示 ${{visible}} 家企业 · ${{viewLabel}} · ${{regLabel}} · ${{catLabel}}${{l2Label}}`;
  }}
}}

// View toggle
document.querySelectorAll('.view-btn').forEach(btn => {{
  btn.addEventListener('click', function() {{
    document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    activeView = this.dataset.view;
    filterEnt();
  }});
}});

// Region filter
document.querySelectorAll('[data-reg]').forEach(btn => {{
  btn.addEventListener('click', function() {{
    document.querySelectorAll('[data-reg]').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    activeReg = this.dataset.reg;
    activeCat = 'all';
    activeL2 = 'all';
    document.querySelectorAll('#cat-filter [data-cat]').forEach(b => b.classList.toggle('active', b.dataset.cat === 'all'));
    hideAllL2Rows();
    filterEnt();
  }});
}});

// L1 Category filter
document.querySelectorAll('#cat-filter [data-cat]').forEach(btn => {{
  btn.addEventListener('click', function() {{
    document.querySelectorAll('#cat-filter [data-cat]').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    activeCat = this.dataset.cat;
    activeL2 = 'all';
    // Show/hide L2 subcategory row
    hideAllL2Rows();
    if (activeCat !== 'all') {{
      const l2Row = document.getElementById('l2-' + activeCat);
      if (l2Row) {{
        l2Row.style.display = 'flex';
        // Reset L2 active state
        l2Row.querySelectorAll('.f-btn-l2').forEach(b => b.classList.toggle('active', b.dataset.l2 === 'all'));
      }}
    }}
    filterEnt();
  }});
}});

// L2 Subcategory filter
document.querySelectorAll('.f-btn-l2').forEach(btn => {{
  btn.addEventListener('click', function() {{
    const parent = this.dataset.parent;
    const l2Row = document.getElementById('l2-' + parent);
    if (l2Row) {{
      l2Row.querySelectorAll('.f-btn-l2').forEach(b => b.classList.remove('active'));
    }}
    this.classList.add('active');
    activeL2 = this.dataset.l2;
    filterEnt();
  }});
}});

function hideAllL2Rows() {{
  document.querySelectorAll('.l2-row').forEach(row => row.style.display = 'none');
}}

filterEnt();
</script>
</body>
</html>"""

    html_content = html_content.replace("__COMMON_CSS__", COMMON_CSS + FEEDBACK_CSS).replace("__SIDEBAR__", SIDEBAR("enterprise"))
    html_content = html_content.replace("</body>", THEME_JS + FEEDBACK_JS + "\n</body>")
    out_path = os.path.join(OUTPUT_DIR, "enterprise.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Also write to root for GitHub Pages
    root_path = os.path.join(BASE_DIR, "enterprise.html")
    with open(root_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated: {out_path}")
    print(f"Total: {total} | Domestic: {domestic} | Overseas: {overseas} | Curated: {curated_count}")

    for l1 in L1_CATS:
        print(f"  {l1}: {cat_counts.get(l1, 0)}")

    return out_path


def main():
    """Entry point for the daily pipeline (run_daily.py)."""
    return generate()


if __name__ == "__main__":
    generate()
