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
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
BUILD_STAMP = datetime.now().strftime("%Y%m%d%H%M%S")

# Import from config
import sys
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


def build_card(ent):
    """Build a compact horizontal card for one enterprise.
    All fields directly visible, empty fields hidden."""
    name = esc(ent.get("name", ""))
    region = ent.get("region", "")
    cat_l1 = esc(ent.get("category_l1", ""))
    cat_l2 = esc(ent.get("category_l2", ""))
    tags = ent.get("tags", [])
    description = esc(ent.get("description", ""))
    highlights = esc(ent.get("highlights", ""))

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

    # Data attributes for filtering
    search_text = (ent.get("name", "") or "").lower()
    # Also include description and tags in search data
    desc_lower = (ent.get("description", "") or "").lower()
    tags_lower = " ".join((t or "").lower() for t in tags) if isinstance(tags, list) else ""
    full_search = f"{search_text} {desc_lower} {tags_lower}"
    cat_attr = cat_l1 if cat_l1 else ""
    region_attr = "1" if region == "国内" else "2"
    curated_attr = "1" if curated else "0"

    return (
        f'<div class="ent-card" data-region="{region_attr}" '
        f'data-cat="{esc(cat_attr)}" '
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

    # Category distribution
    cat_counts = {}
    for e in enterprises:
        l1 = e.get("category_l1", "")
        cat_counts[l1] = cat_counts.get(l1, 0) + 1

    # Build cards
    cards_html = "\n".join(build_card(e) for e in enterprises)

    # L1 filter buttons (no numbering)
    cat_buttons = "\n".join(
        f'<button class="f-btn" data-cat="{esc(l1)}">{esc(l1)}<span class="cnt">{cat_counts.get(l1, 0)}</span></button>'
        for l1 in L1_CATS
    )

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
<style>
:root {{
  --bg: #f5f5f5;
  --sidebar-bg: #ffffff;
  --card-bg: #ffffff;
  --text: #1a1a1a;
  --text-secondary: #555;
  --text-muted: #999;
  --border: #e8e8e8;
  --accent: #0891b2;
  --accent-light: #ecfeff;
  --radius: 8px;
  --tag-bg: #e0f2fe;
  --tag-text: #0369a1;
  --cat-bg: #ecfdf5;
  --cat-text: #065f46;
  --fund-bg: #fef3c7;
  --fund-text: #92400e;
  --fund-total-bg: #f0fdf4;
  --fund-total-text: #166534;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif; background:var(--bg); color:var(--text); line-height:1.5; display:flex; min-height:100vh; }}

/* Sidebar */
.sidebar {{ width:200px; background:var(--sidebar-bg); border-right:1px solid var(--border); position:fixed; top:0; left:0; height:100vh; overflow-y:auto; padding:20px 0; flex-shrink:0; z-index:10; }}
.sidebar-logo {{ padding:0 16px 16px; border-bottom:1px solid var(--border); margin-bottom:12px; }}
.sidebar-logo h1 {{ font-size:18px; font-weight:700; color:var(--accent); }}
.sidebar-logo .logo-sub {{ font-size:11px; color:var(--text-muted); margin-top:2px; }}
.nav-section {{ padding:4px 0; }}
.nav-label {{ font-size:11px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; padding:6px 16px 4px; font-weight:600; }}
.nav-item {{ display:block; padding:8px 16px 8px 24px; font-size:13px; color:var(--text-secondary); text-decoration:none; cursor:pointer; border-left:3px solid transparent; transition:all 0.15s; }}
.nav-item:hover {{ background:#fafafa; color:var(--text); }}
.nav-item.active {{ background:var(--accent-light); color:var(--accent); border-left-color:var(--accent); font-weight:600; }}

/* Main */
.main {{ flex:1; margin-left:200px; max-width:980px; width:calc(100% - 200px); padding:24px 32px 60px; }}
.header {{ margin-bottom:16px; }}
.header h2 {{ font-size:20px; font-weight:700; }}
.header-stats {{ font-size:12px; color:var(--text-muted); margin-top:4px; }}

/* Search + filter row */
.toolbar {{ margin-bottom:14px; }}
.filter-row {{ display:flex; flex-wrap:wrap; gap:5px; margin-bottom:8px; align-items:center; }}
.f-label {{ font-size:11px; color:var(--text-muted); font-weight:600; margin-right:4px; min-width:36px; }}
.f-btn {{ padding:3px 10px; border-radius:14px; border:1px solid var(--border); background:var(--card-bg); font-size:11px; cursor:pointer; color:var(--text-secondary); white-space:nowrap; transition:all 0.15s; }}
.f-btn:hover {{ border-color:var(--accent); color:var(--accent); }}
.f-btn.active {{ background:var(--accent); color:white; border-color:var(--accent); }}
.f-btn .cnt {{ font-size:10px; opacity:0.7; margin-left:2px; }}
.search-inline {{ width:200px; padding:4px 12px; border:1px solid var(--border); border-radius:14px; font-size:12px; outline:none; background:var(--card-bg); color:var(--text); }}
.search-inline:focus {{ border-color:var(--accent); box-shadow:0 0 0 2px rgba(8,145,178,0.1); }}

/* View toggle */
.view-toggle {{ display:inline-flex; gap:0; margin-left:8px; border:1px solid var(--border); border-radius:14px; overflow:hidden; }}
.view-btn {{ padding:3px 12px; border:none; background:var(--card-bg); font-size:11px; cursor:pointer; color:var(--text-secondary); transition:all 0.15s; }}
.view-btn:hover {{ background:#f5f5f5; }}
.view-btn.active {{ background:var(--accent); color:white; }}

/* Result count */
.result-count {{ font-size:11px; color:var(--text-muted); margin-bottom:8px; padding-left:2px; }}

/* Enterprise cards */
.ent-card {{ background:var(--card-bg); border:0.5px solid var(--border); border-radius:var(--radius); padding:10px 16px; margin-bottom:5px; }}
.ent-card:hover {{ border-color:#ccc; background:#fcfcfc; }}

.ent-header {{ display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin-bottom:3px; }}
.ent-name {{ font-weight:500; font-size:14px; color:var(--text); }}
.ent-badge {{ font-size:10px; padding:1px 7px; border-radius:3px; font-weight:400; white-space:nowrap; }}
.badge-cat {{ background:var(--cat-bg); color:var(--cat-text); }}
.badge-region {{ font-size:9px; color:var(--text-muted); background:transparent; padding:0 4px; font-weight:400; }}

.ent-tags {{ display:inline-flex; gap:3px; flex-wrap:wrap; }}
.ent-tag {{ font-size:10px; color:var(--tag-text); background:var(--tag-bg); padding:1px 7px; border-radius:3px; font-weight:500; }}

.ent-desc {{ font-size:12px; color:var(--text-secondary); line-height:1.5; margin:2px 0; }}
.ent-highlights {{ font-size:11px; color:var(--accent); line-height:1.4; margin:2px 0; font-style:italic; }}

.ent-meta {{ display:flex; gap:10px; font-size:11px; color:var(--text-muted); flex-wrap:wrap; align-items:center; margin-top:3px; }}
.meta-item {{ white-space:nowrap; }}
.meta-fund {{ color:var(--fund-text); font-weight:500; background:var(--fund-bg); padding:1px 6px; border-radius:3px; }}
.meta-fund-total {{ color:var(--fund-total-text); font-weight:500; background:var(--fund-total-bg); padding:1px 6px; border-radius:3px; }}
.meta-source {{ font-size:10px; opacity:0.7; }}
.meta-links {{ margin-left:auto; }}
.ent-link {{ font-size:11px; color:var(--accent); text-decoration:underline; }}

.footer {{ text-align:center; padding:24px 0 16px; font-size:12px; color:var(--text-muted); border-top:1px solid var(--border); margin-top:24px; }}
.hidden {{ display:none !important; }}

@media (max-width:768px) {{
  .sidebar {{ display:none; }}
  .main {{ margin-left:0; width:100%; padding:16px; max-width:100%; }}
  .search-inline {{ width:100%; }}
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
    <a href="enterprise.html" class="nav-item active">企业库</a>
    <a href="about.html" class="nav-item">网站说明</a>
  </div>
</div>

<div class="main">

<div class="header">
  <h2>银发经济企业数据库</h2>
  <p class="header-stats">共 {total} 家企业 · 国内 {domestic} 家 · 海外 {overseas} 家 · 精选 {curated_count} 家 · 13 个一级分类</p>
</div>

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
  </div>
  <div class="filter-row" id="cat-filter">
    <span class="f-label">分类</span>
    <button class="f-btn active" data-cat="all">全部</button>
    {cat_buttons}
  </div>
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
let activeView = 'curated';

function filterEnt() {{
  const q = document.getElementById('search').value.toLowerCase();
  const cards = document.querySelectorAll('.ent-card');
  let visible = 0;
  const catVisCounts = {{}};

  cards.forEach(card => {{
    const reg = card.dataset.region;
    const cat = card.dataset.cat;
    const name = (card.dataset.name || '').toLowerCase();
    const curated = card.dataset.curated === '1';

    const regMatch = activeReg === 'all' || reg === activeReg;
    const searchMatch = !q || name.includes(q);
    const catMatch = activeCat === 'all' || cat === activeCat;
    const viewMatch = activeView === 'all' || curated;

    if (regMatch && searchMatch && viewMatch) {{
      if (cat) catVisCounts[cat] = (catVisCounts[cat] || 0) + 1;
      if (catMatch) {{
        card.style.display = '';
        visible++;
      }} else {{
        card.style.display = 'none';
      }}
    }} else {{
      card.style.display = 'none';
    }}
  }});

  // Update category counts
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

  // Update result count
  const rc = document.getElementById('result-count');
  if (rc) {{
    const viewLabel = activeView === 'curated' ? '精选' : '全量';
    const regLabel = activeReg === 'all' ? '全部地区' : (activeReg === '1' ? '国内' : '海外');
    const catLabel = activeCat === 'all' ? '全部分类' : activeCat;
    rc.textContent = `展示 ${{visible}} 家企业 · ${{viewLabel}} · ${{regLabel}} · ${{catLabel}}`;
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
    document.querySelectorAll('#cat-filter [data-cat]').forEach(b => b.classList.toggle('active', b.dataset.cat === 'all'));
    filterEnt();
  }});
}});

// Category filter
document.querySelectorAll('#cat-filter [data-cat]').forEach(btn => {{
  btn.addEventListener('click', function() {{
    document.querySelectorAll('#cat-filter [data-cat]').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    activeCat = this.dataset.cat;
    filterEnt();
  }});
}});

filterEnt();
</script>
</body>
</html>"""

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


if __name__ == "__main__":
    generate()
