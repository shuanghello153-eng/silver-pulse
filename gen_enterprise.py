#!/usr/bin/env python3
"""
gen_enterprise.py — v5 compact card layout
New schema: name, region, category_l1, category_l2, tags, description, highlights,
            funding_latest, funding_total, investors, founded, value_score,
            source, crunchbase_url, website_url
13-class system, no P0/P1/P2, no numbering in display.
All fields directly visible — no click-to-expand.
Empty fields are hidden (not displayed).
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
        if display:
            meta_parts.append(f'<span class="meta-item meta-fund">{esc(display)}</span>')

    # Total funding
    if fund_total and isinstance(fund_total, dict):
        display = fund_total.get("display", "")
        if display and display != "累计未披露":
            meta_parts.append(f'<span class="meta-item">{esc(display)}</span>')

    # Investors
    if investors:
        inv_str = investors if isinstance(investors, str) else ", ".join(investors)
        if inv_str:
            meta_parts.append(f'<span class="meta-item">投资方: {esc(inv_str)}</span>')

    # Founded
    if founded:
        meta_parts.append(f'<span class="meta-item">成立: {founded}</span>')

    # Source
    if source:
        meta_parts.append(f'<span class="meta-item">{source}</span>')

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
    cat_attr = cat_l1 if cat_l1 else ""
    region_attr = "1" if region == "国内" else "2"

    return (
        f'<div class="ent-card" data-region="{region_attr}" '
        f'data-cat="{esc(cat_attr)}" '
        f'data-name="{esc(search_text)}" '
        f'data-serial="{esc(serial)}">\n'
        + "\n".join(parts) + "\n"
        + '</div>'
    )


def generate():
    enterprises = load_enterprises()
    total = len(enterprises)

    domestic = sum(1 for e in enterprises if e.get("region") == "国内")
    overseas = sum(1 for e in enterprises if e.get("region") == "海外")

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

/* Enterprise cards */
.ent-card {{ background:var(--card-bg); border:0.5px solid var(--border); border-radius:var(--radius); padding:12px 16px; margin-bottom:6px; }}
.ent-card:hover {{ border-color:#ccc; background:#fcfcfc; }}

.ent-header {{ display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin-bottom:4px; }}
.ent-name {{ font-weight:500; font-size:14px; color:var(--text); }}
.ent-badge {{ font-size:10px; padding:1px 7px; border-radius:3px; font-weight:400; white-space:nowrap; }}
.badge-cat {{ background:var(--cat-bg); color:var(--cat-text); }}
.badge-region {{ font-size:9px; color:var(--text-muted); background:transparent; padding:0 4px; font-weight:400; }}

.ent-tags {{ display:inline-flex; gap:3px; flex-wrap:wrap; }}
.ent-tag {{ font-size:10px; color:var(--tag-text); background:var(--tag-bg); padding:1px 7px; border-radius:3px; font-weight:500; }}

.ent-desc {{ font-size:12px; color:var(--text-secondary); line-height:1.5; margin:2px 0; }}
.ent-highlights {{ font-size:11px; color:var(--accent); line-height:1.4; margin:2px 0; font-style:italic; }}

.ent-meta {{ display:flex; gap:12px; font-size:11px; color:var(--text-muted); flex-wrap:wrap; align-items:center; margin-top:3px; }}
.meta-item {{ white-space:nowrap; }}
.meta-fund {{ color:var(--fund-text); font-weight:500; background:var(--fund-bg); padding:1px 6px; border-radius:3px; }}
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
  <p class="header-stats">共 {total} 家企业 · 国内 {domestic} 家 · 海外 {overseas} 家 · 13 个一级分类</p>
</div>

<div class="toolbar">
  <div class="filter-row">
    <span class="f-label">地区</span>
    <button class="f-btn active" data-reg="all">全部</button>
    <button class="f-btn" data-reg="1">国内</button>
    <button class="f-btn" data-reg="2">海外</button>
  </div>
  <div class="filter-row" id="cat-filter">
    <span class="f-label">分类</span>
    <button class="f-btn active" data-cat="all">全部</button>
    {cat_buttons}
  </div>
  <div class="filter-row">
    <input type="text" class="search-inline" id="search" placeholder="搜索企业名称..." oninput="filterEnt()">
  </div>
</div>

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

function filterEnt() {{
  const q = document.getElementById('search').value.toLowerCase();
  const cards = document.querySelectorAll('.ent-card');
  let visible = 0;

  cards.forEach(card => {{
    const reg = card.dataset.region;
    const cat = card.dataset.cat;
    const name = (card.dataset.name || '').toLowerCase();

    const regMatch = activeReg === 'all' || reg === activeReg;
    const catMatch = activeCat === 'all' || cat === activeCat;
    const searchMatch = !q || name.includes(q);

    if (regMatch && catMatch && searchMatch) {{
      card.style.display = '';
      visible++;
    }} else {{
      card.style.display = 'none';
    }}
  }});

  const stats = document.getElementById('ent-count');
  if (stats) stats.textContent = visible;
}}

document.querySelectorAll('[data-reg]').forEach(btn => {{
  btn.addEventListener('click', function() {{
    document.querySelectorAll('[data-reg]').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    activeReg = this.dataset.reg;
    filterEnt();
  }});
}});

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
    print(f"Total: {total} | Domestic: {domestic} | Overseas: {overseas}")

    for l1 in L1_CATS:
        print(f"  {l1}: {cat_counts.get(l1, 0)}")

    return out_path


if __name__ == "__main__":
    generate()
