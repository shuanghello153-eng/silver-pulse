#!/usr/bin/env python3
"""
Generate enterprise.html — v4 compact table layout with 16-field unified schema.
Category: 15 groups (01-15) with code+label.
No P0/P1/P2, no view toggle, no scoring.
Default sorted by serial number.
"""
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
BUILD_STAMP = datetime.now().strftime("%Y%m%d%H%M%S")

# ============================================================
# 15-class category system (shared with merge_v2.py)
# ============================================================
CATEGORY_15 = {
    "01": "购物渠道/平台",
    "02": "日常用品/消费",
    "03": "健康食品/营养",
    "04": "老年文娱/社交",
    "05": "健康服务/医疗",
    "06": "适老化改造",
    "07": "行业服务/金融",
    "08": "养老地产/居住",
    "09": "养老服务/护理",
    "10": "养老用品/辅具",
    "11": "康复设备/器械",
    "12": "失智老人/认知症",
    "13": "产业资本/投资",
    "14": "临终关怀",
    "15": "出行/交通",
}


def load_enterprises():
    path = os.path.join(DATA_DIR, "enterprise/all_enterprises.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_funding(funding_latest, funding_total, investors):
    """Format funding info for display cell."""
    parts = []

    if funding_latest and isinstance(funding_latest, dict):
        display = funding_latest.get("display", "")
        if display:
            parts.append(display)

    if funding_total and isinstance(funding_total, dict):
        display = funding_total.get("display", "")
        if display and display not in ("累计未披露",):
            parts.append(display)

    if investors:
        invs_str = investors if isinstance(investors, str) else ", ".join(investors)
        if invs_str:
            parts.append(invs_str)

    return " | ".join(parts)[:150] if parts else ""


def generate():
    enterprises = load_enterprises()
    total = len(enterprises)

    # Stats
    domestic = sum(1 for e in enterprises if e.get("region") == "国内")
    overseas = sum(1 for e in enterprises if e.get("region") == "海外")

    # Category distribution
    cat_counts = {}
    for e in enterprises:
        code = e.get("category_code", "07")
        label = e.get("category_label", "")
        cat_counts[code] = cat_counts.get(code, 0) + 1

    def build_row(ent):
        serial = ent.get("serial", "")
        name = ent.get("name") or ""
        name_cn = ent.get("name_cn") or ""
        display_name = f"{name_cn} / {name}" if name_cn else name

        region = ent.get("region", "国内")
        region_code = ent.get("region_code", 1)
        region_cls = "reg-overseas" if region_code == 2 else "reg-china"

        cat_code = ent.get("category_code", "07")
        cat_label = ent.get("category_label", "")
        cat_raw = ent.get("category", "")

        description = (ent.get("description") or "")[:120]
        funding_str = format_funding(
            ent.get("funding_latest"),
            ent.get("funding_total"),
            ent.get("investors")
        )

        # data attributes for filtering
        search_name = f"{name} {name_cn}".strip().lower()
        data_attrs = (
            f'data-region="{region_code}" '
            f'data-cat="{cat_code}" '
            f'data-name="{search_name}" '
            f'data-serial="{serial}"'
        )

        sub_cat_html = f' <span class="sub-cat">{cat_raw}</span>' if cat_raw and cat_raw != cat_label else ""
        desc_html = f'<span class="row-desc">{description}</span>' if description else ""
        fund_html = f'<span class="row-fund">{funding_str}</span>' if funding_str else ""

        # Build detail row content
        detail_parts = []
        full_desc = ent.get("description", "") or ""
        if full_desc:
            detail_parts.append(f'<b>简介:</b> {full_desc}')
        if cat_raw and cat_raw != cat_label:
            detail_parts.append(f'<b>原始分类:</b> {cat_raw}')
        source = ent.get("source", "")
        if source:
            detail_parts.append(f'<b>来源:</b> {source}')
        source_url = ent.get("source_url", "")
        if source_url:
            detail_parts.append(f'<b>链接:</b> <a href="{source_url}" target="_blank">{source_url}</a>')

        # Funding detail
        fund_latest = ent.get("funding_latest")
        fund_total = ent.get("funding_total")
        investors = ent.get("investors")
        if fund_latest and isinstance(fund_latest, dict):
            fd = []
            if fund_latest.get("round"):
                fd.append(f'轮次: {fund_latest["round"]}')
            if fund_latest.get("amount"):
                fd.append(f'金额: {fund_latest["amount"]}')
            if fund_latest.get("date"):
                fd.append(f'时间: {fund_latest["date"]}')
            if fd:
                detail_parts.append(f'<b>最新融资:</b> {" | ".join(fd)}')
        if fund_total and isinstance(fund_total, dict) and fund_total.get("amount"):
            detail_parts.append(f'<b>累计融资:</b> {fund_total["amount"]}')
        if investors:
            invs_str = investors if isinstance(investors, str) else ", ".join(investors)
            detail_parts.append(f'<b>投资方:</b> {invs_str}')

        detail_html = "<br>".join(detail_parts) if detail_parts else "暂无详细信息"
        ent_id = serial.replace("#", "")

        return (
            f'<tr class="data-row" {data_attrs} style="cursor:pointer" onclick="toggleDetail(\'{ent_id}\')">'
            f'  <td class="col-serial">{serial}</td>'
            f'  <td><span class="badge {region_cls}">{region}</span></td>'
            f'  <td class="col-name">{display_name}{sub_cat_html}</td>'
            f'  <td class="col-cat"><span class="cat-code">{cat_code}</span> {cat_label}</td>'
            f'  <td class="col-detail">{fund_html}{desc_html}</td>'
            f'</tr>'
            f'<tr class="detail-row" id="detail-{ent_id}" style="display:none">'
            f'  <td colspan="5" class="detail-content">{detail_html}</td>'
            f'</tr>'
        )

    rows = "\n".join(build_row(e) for e in enterprises)

    # Category filter buttons (sorted by code)
    cat_buttons = "\n".join(
        f'<button class="f-btn" data-cat="{code}">{code} {label}<span class="cnt">{cat_counts.get(code, 0)}</span></button>'
        for code in sorted(CATEGORY_15.keys())
    )

    html = f'''<!-- build:{BUILD_STAMP} -->
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
  --text-secondary: #666;
  --text-muted: #999;
  --border: #e8e8e8;
  --accent: #0891b2;
  --accent-light: #ecfeff;
  --china: #3b82f6; --overseas: #10b981;
  --radius: 8px;
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
.nav-item {{ display:block; padding:8px 16px 8px 24px; font-size:13px; color:var(--text-secondary); text-decoration:none; cursor:pointer; border-left:3px solid transparent; transition:all 0.15s; position:relative; }}
.nav-item:hover {{ background:#fafafa; color:var(--text); }}
.nav-item.active {{ background:var(--accent-light); color:var(--accent); border-left-color:var(--accent); font-weight:600; }}
.nav-item .count {{ float:right; font-size:11px; color:var(--text-muted); font-weight:400; }}

/* Main */
.main {{ flex:1; margin-left:200px; max-width:980px; width:calc(100% - 200px); padding:24px 32px 60px; }}

.header {{ margin-bottom:16px; }}
.header h2 {{ font-size:20px; font-weight:700; }}
.header-stats {{ font-size:12px; color:var(--text-muted); margin-top:4px; }}

/* Search */
.search-wrap {{ margin-bottom:14px; }}
.search-wrap input {{ width:100%; padding:9px 14px; border:1px solid var(--border); border-radius:var(--radius); font-size:13px; outline:none; background:var(--card-bg); color:var(--text); }}
.search-wrap input:focus {{ border-color:var(--accent); box-shadow:0 0 0 2px rgba(8,145,178,0.1); }}

/* Filters */
.filter-row {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:14px; align-items:center; }}
.f-label {{ font-size:11px; color:var(--text-muted); font-weight:600; margin-right:4px; }}
.f-btn {{ padding:4px 10px; border-radius:14px; border:1px solid var(--border); background:var(--card-bg); font-size:11px; cursor:pointer; color:var(--text-secondary); white-space:nowrap; transition:all 0.15s; }}
.f-btn:hover {{ border-color:var(--accent); color:var(--accent); }}
.f-btn.active {{ background:var(--accent); color:white; border-color:var(--accent); }}
.f-btn .cnt {{ font-size:10px; opacity:0.75; margin-left:3px; }}

/* Table */
.table-wrap {{ background:var(--card-bg); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; }}
.data-table {{ width:100%; border-collapse:collapse; font-size:13px; }}
.data-table th {{ background:#fafafa; padding:8px 12px; text-align:left; font-size:11px; font-weight:600; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.3px; border-bottom:1px solid var(--border); white-space:nowrap; }}
.data-row {{ transition:background 0.1s; }}
.data-row:nth-child(even) {{ background:#fafbfc; }}
.data-row:hover {{ background:#f0f9ff; }}
.data-table td {{ padding:7px 12px; border-bottom:1px solid #f0f0f0; vertical-align:middle; }}

/* Column widths */
.col-serial {{ width:60px; font-size:11px; color:var(--text-muted); font-family:monospace; }}

/* Badges */
.badge {{ font-size:10px; font-weight:700; padding:2px 7px; border-radius:10px; display:inline-block; white-space:nowrap; vertical-align:middle; }}
.reg-overseas {{ background:#ecfdf5; color:#065f46; }}
.reg-china {{ background:#eff6ff; color:#1e40af; }}

.col-name {{ font-weight:600; min-width:160px; }}
.sub-cat {{ font-size:10px; color:var(--text-muted); font-weight:400; margin-left:4px; }}
.col-cat {{ color:var(--text-secondary); font-size:12px; white-space:nowrap; min-width:120px; }}
.cat-code {{ display:inline-block; background:#f3f4f6; color:var(--text-muted); font-size:10px; padding:1px 4px; border-radius:3px; margin-right:3px; font-family:monospace; }}
.col-detail {{ color:var(--text-muted); font-size:11px; max-width:360px; }}
.row-desc {{ display:block; color:var(--text-secondary); margin-top:2px; }}
.row-fund {{ display:inline-block; background:#fffbeb; color:#92400e; padding:1px 6px; border-radius:4px; font-size:10px; margin-right:4px; }}

.footer {{ text-align:center; padding:24px 0 16px; font-size:12px; color:var(--text-muted); border-top:1px solid var(--border); margin-top:24px; }}
.detail-content {{ padding:12px 16px; background:#f9fafb; font-size:12px; color:var(--text-secondary); line-height:1.8; border-bottom:1px solid var(--border); }}
.hidden {{ display:none !important; }}

@media (max-width:768px) {{
  .sidebar {{ display:none; }}
  .main {{ margin-left:0; width:100%; padding:16px; max-width:100%; }}
  .table-wrap {{ overflow-x:auto; }}
  .data-table {{ min-width:600px; }}
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
  <p class="header-stats">共 {total} 家企业 · 国内 {domestic} 家 · 海外 {overseas} 家 · 15 个分类</p>
</div>

<div class="search-wrap">
  <input type="text" id="search" placeholder="搜索企业名称..." oninput="filterEnt()">
</div>

<div class="filter-row">
  <span class="f-label">地区</span>
  <button class="f-btn active" data-reg="all">全部</button>
  <button class="f-btn" data-reg="1">1 国内</button>
  <button class="f-btn" data-reg="2">2 海外</button>
</div>

<div class="filter-row" id="cat-filter">
  <span class="f-label">类别</span>
  <button class="f-btn active" data-cat="all">全部</button>
  {cat_buttons}
</div>

<div class="table-wrap">
<table class="data-table">
<thead>
<tr>
  <th>序号</th>
  <th>地区</th>
  <th>企业名称</th>
  <th>分类</th>
  <th>融资 / 简介</th>
</tr>
</thead>
<tbody id="tbody">
{rows}
</tbody>
</table>
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
  const rows = document.querySelectorAll('.data-row');

  rows.forEach(row => {{
    const reg = row.dataset.region;
    const cat = row.dataset.cat;
    const name = (row.dataset.name || '').toLowerCase();

    const regMatch = activeReg === 'all' || reg === activeReg;
    const catMatch = activeCat === 'all' || cat === activeCat;
    const searchMatch = !q || name.includes(q);

    row.style.display = (regMatch && catMatch && searchMatch) ? '' : 'none';
  }});
}}

// Region buttons
document.querySelectorAll('[data-reg]').forEach(btn => {{
  btn.addEventListener('click', function() {{
    document.querySelectorAll('[data-reg]').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    activeReg = this.dataset.reg;
    filterEnt();
  }});
}});

// Category buttons
document.querySelectorAll('#cat-filter [data-cat]').forEach(btn => {{
  btn.addEventListener('click', function() {{
    document.querySelectorAll('#cat-filter [data-cat]').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    activeCat = this.dataset.cat;
    filterEnt();
  }});
}});

// Initialize
filterEnt();

function toggleDetail(id) {{
  const el = document.getElementById('detail-' + id);
  if (el) {{
    el.style.display = el.style.display === 'none' ? '' : 'none';
  }}
}}
</script>
</body>
</html>'''

    out_path = os.path.join(OUTPUT_DIR, "enterprise.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Also write to root for GitHub Pages
    root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "enterprise.html")
    with open(root_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated: {out_path}")
    print(f"Total: {total} | Domestic: {domestic} | Overseas: {overseas}")

    # Category breakdown
    for code in sorted(CATEGORY_15.keys()):
        print(f"  {code} {CATEGORY_15[code]}: {cat_counts.get(code, 0)}")

    return out_path


if __name__ == "__main__":
    generate()
