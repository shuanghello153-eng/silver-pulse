"""
Generate enterprise.html — v3 compact table layout + unified categories.
Default shows P0+P1 (curated), toggle to show all 485.
Category consolidation: 115 raw -> ~12 top-level groups.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# === Category Consolidation Map ===
# Maps 115 granular categories to ~12 top-level groups
# Format: top_level_name -> (display_label, list of source categories that map here)
CATEGORY_MAP = {
    "consumer_goods": ("养老用品", [
        "养老用品", "日常用品", "厨房家居用品", "消费电子",
        "眼镜零售、视光服务", "运动服饰", "运动服饰、鞋履、健身",
        "药品配送", "线上药房", "照护用品电商与服务",
        "零售、适老化科技", "电商、智能语音",
    ]),
    "health_food": ("健康食品", [
        "健康食品",
    ]),
    "entertainment": ("老年文娱/社交", [
        "老年文娱", "社交陪伴/上门服务", "科技、社交平台",
        "VR 老年娱乐", "老年在线健身、防跌倒",
        "终身学习、人生转型", "直播学习、数字会员", "老年教育旅行",
        "银发再就业、代际公益", "老年旅游",
    ]),
    "care_service": ("养老服务/护理", [
        "养老服务", "居家养老/护理平台", "居家养老/连锁",
        "居家养老/收购", "居家护理/数字化", "居家护理/数据驱动",
        "居家护理/价值医疗", "全品类照护平台", "居家照护匹配平台",
        "居家照护服务", "PACE全包护理", "初级保健/社会护理",
        "社会护理/SDOH", "非营利养老机构", "养老社区运营",
        "上门移动医疗", "远程医疗", "专科远程医疗",
        "互联健康服务", "整合医疗系统",
        "护工培训", "护工培训",
    ]),
    "real_estate": ("养老地产/居住", [
        "养老地产", "养老住房/跨代合住", "代际住房匹配",
        "养老居住中介", "养老居住搜索平台", "养老居住服务",
        "社区互助养老",
    ]),
    "health_service": ("健康服务/医疗", [
        "健康服务", "临终关怀", "姑息治疗、临终规划", "临终医疗规划",
        "临终规划平台", "临终财务与法律规划",
        "顶级医疗机构", "商业医保", "健康保险",
    ]),
    "tech_digital": ("智慧养老/AI/数字疗法", [
        "数字疗法/MSK", "智慧养老/AI", "智慧养老/监测",
        "远程患者监测", "慢性病数字管理", "保险科技",
        "金融科技", "金融理财", "金融理财/防欺诈",
        "资产管理、退休规划", "财富管理、长寿金融规划",
        "退休金融科技", "老年金融防护", "老年资金管理",
        "遗产规划、公益慈善", "遗产与数字继承",
    ]),
    "rehab_device": ("康复辅具/设备", [
        "康复设备", "机器人/医疗", "认知症/机器人", "医疗出行",
        "老年通讯与应急设备", "适老化创新研究",
    ]),
    "dementia_care": ("认知症/脑健康", [
        "认知症", "认知症/心理健康", "认知症/数字疗法" if False else "认知症",
    ]),
    "aging_renovation": ("适老化改造", [
        "适老化改造",
    ]),
    "retail_channel": ("购物渠道/平台", [
        "购物渠道", "老年账单代付服务",
    ]),
    "ecosystem_support": ("产业生态/投资/媒体", [
        "投资机构", "私募股权", "风险投资", "长寿专项风投",
        "影响力投资与孵化", "创业加速器", "长寿科技加速器",
        "全球长寿创新网络", "产业创新平台",
        "行业媒体", "行业展会", "上市公司", "学术研究",
        "人力资源咨询", "汽车制造", "综合金融服务",
        "保险、资产管理", "金融、雇主品牌",
        "医药健康、雇主品牌",
    ]),
}


def categorize(raw_category):
    """Map a raw category to its top-level group."""
    raw = (raw_category or "").strip()
    for top_key, (label, sources) in CATEGORY_MAP.items():
        if raw in sources or raw == label:
            return top_key, label
    # Fallback — try fuzzy match
    for top_key, (label, sources) in CATEGORY_MAP.items():
        for s in sources:
            if s in raw or raw in s:
                return top_key, label
    # Last resort: put in ecosystem
    return "ecosystem_support", "其他"


def load_enterprises():
    path = os.path.join(DATA_DIR, "enterprise/all_enterprises.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate():
    enterprises = load_enterprises()

    # Assign top-level category to each enterprise
    for e in enterprises:
        raw_cat = e.get("category", "")
        top_key, top_label = categorize(raw_cat)
        e["_top_cat"] = top_key
        e["_top_label"] = top_label
        # Keep original as sub-category
        if raw_cat != top_label and raw_cat:
            e["_sub_cat"] = raw_cat
        else:
            e["_sub_cat"] = ""

    # Stats
    total = len(enterprises)
    p0_count = sum(1 for e in enterprises if e.get("priority") == "P0")
    p1_count = sum(1 for e in enterprises if e.get("priority") == "P1")
    p2_count = sum(1 for e in enterprises if e.get("priority") == "P2")
    china_count = sum(1 for e in enterprises if e.get("region") == "china")
    overseas_count = sum(1 for e in enterprises if e.get("region") == "overseas")
    curated_count = p0_count + p1_count

    # Top-level category stats
    cat_stats = {}
    for e in enterprises:
        c = e.get("_top_cat", "")
        cat_stats[c] = cat_stats.get(c, 0) + 1
    sorted_cats = sorted(CATEGORY_MAP.items(), key=lambda x: -cat_stats.get(x[0], 0))

    def build_row(ent):
        name = ent.get("name", "")
        name_cn = ent.get("name_cn", "")
        display_name = f"{name_cn} / {name}" if name_cn else name
        region = ent.get("region", "")
        priority = ent.get("priority", "P2")
        top_label = ent.get("_top_label", "")
        sub_cat = ent.get("_sub_cat", "")
        desc = (ent.get("description", "") or ent.get("summary", "") or "")[:120]
        funding = ent.get("funding", "")
        is_investor = ent.get("is_investor", False)
        source = ent.get("source", "")

        # Priority badge HTML
        pri_map = {"P0": ('pri-p0', 'P0'), "P1": ('pri-p1', 'P1'), "P2": ('pri-p2', 'P2')}
        pri_cls, pri_txt = pri_map.get(priority, ('pri-p2', 'P2'))

        # Region
        region_cls = "reg-overseas" if region == "overseas" else "reg-china"
        region_txt = "海外" if region == "overseas" else "国内"

        # Funding string
        funding_str = ""
        if isinstance(funding, dict):
            parts = []
            if funding.get("round"): parts.append(funding["round"])
            if funding.get("amount"): parts.append(funding["amount"])
            if funding.get("investors"):
                invs = funding["investors"]
                parts.append(invs if isinstance(invs, str) else ", ".join(invs))
            funding_str = " | ".join(parts)[:100]
        elif isinstance(funding, str) and len(funding) > 2:
            funding_str = funding[:100]

        investor_badge = '<span class="badge badge-invest">投</span>' if is_investor else ""

        data_attrs = (
            f'data-priority="{priority}" data-region="{region}" '
            f'data-cat="{ent.get("_top_cat","")}" '
            f'data-name="{(name+" "+name_cn).lower()}"'
        )

        sub_html = f' <span class="sub-cat">{sub_cat}</span>' if sub_cat else ""
        desc_html = f'<span class="row-desc">{desc}</span>' if desc else ""
        fund_html = f'<span class="row-fund">{funding_str}</span>' if funding_str else ""

        return (
            f'<tr class="data-row {data_attrs}">'
            f'  <td><span class="badge {pri_cls}">{pri_txt}</span>{investor_badge}</td>'
            f'  <td><span class="badge {region_cls}">{region_txt}</span></td>'
            f'  <td class="col-name">{display_name}{sub_html}</td>'
            f'  <td class="col-cat">{top_label}</td>'
            f'  <td class="col-detail">{fund_html}{desc_html}</td>'
            f'</tr>'
        )

    rows = "\n".join(build_row(e) for e in enterprises)

    # Category filter buttons (top-level only, with counts)
    cat_buttons = "\n".join(
        f'<button class="f-btn" data-cat="{key}">{label}<span class="cnt">{cat_stats.get(key,0)}</span></button>'
        for key, (label, _) in sorted_cats
    )

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
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
  --p0: #dc2626; --p1: #f59e0b; --p2: #d1d5db;
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
.nav-divider {{ height:1px; background:var(--border); margin:8px 16px; }}

/* Main */
.main {{ flex:1; margin-left:200px; max-width:980px; width:calc(100% - 200px); padding:24px 32px 60px; }}

.header {{ margin-bottom:16px; }}
.header h2 {{ font-size:20px; font-weight:700; }}
.header-stats {{ font-size:12px; color:var(--text-muted); margin-top:4px; }}

/* View toggle */
.view-pills {{ display:inline-flex; gap:4px; background:var(--bg); padding:3px; border-radius:20px; margin-bottom:14px; }}
.view-pill {{ padding:5px 16px; border-radius:17px; border:none; background:transparent; cursor:pointer; font-size:12px; font-weight:500; color:var(--text-secondary); transition:all 0.15s; }}
.view-pill.active {{ background:var(--card-bg); color:var(--text); box-shadow:0 1px 3px rgba(0,0,0,0.08); font-weight:600; }}

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

/* Badges */
.badge {{ font-size:10px; font-weight:700; padding:2px 7px; border-radius:10px; display:inline-block; white-space:nowrap; vertical-align:middle; }}
.pri-p0 {{ background:#fef2f2; color:#dc2626; }}
.pri-p1 {{ background:#fef3c7; color:#92400e; }}
.pri-p2 {{ background:#f3f4f6; color:#6b7280; }}
.reg-overseas {{ background:#ecfdf5; color:#065f46; }}
.reg-china {{ background:#eff6ff; color:#1e40af; }}
.badge-invest {{ background:#ede9fe; color:#7c3aed; margin-left:3px; }}

.col-name {{ font-weight:600; min-width:160px; }}
.sub-cat {{ font-size:10px; color:var(--text-muted); font-weight:400; margin-left:4px; }}
.col-cat {{ color:var(--text-secondary); font-size:12px; white-space:nowrap; min-width:90px; }}
.col-detail {{ color:var(--text-muted); font-size:11px; max-width:320px; }}
.row-desc {{ display:block; color:var(--text-secondary); margin-top:2px; }}
.row-fund {{ display:inline-block; background:#fffbeb; color:#92400e; padding:1px 6px; border-radius:4px; font-size:10px; margin-right:4px; }}

.footer {{ text-align:center; padding:24px 0 16px; font-size:12px; color:var(--text-muted); border-top:1px solid var(--border); margin-top:24px; }}
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
    <h1>AI · 银脉</h1>
    <p class="logo-sub">Silver Pulse</p>
  </div>
  <div class="nav-section">
    <div class="nav-label">内容</div>
    <a href="index.html" class="nav-item">资讯看板</a>
    <a href="enterprise.html" class="nav-item active">企业库 <span class="count">{total}</span></a>
    <div class="nav-divider"></div>
    <div class="nav-label">筛选视图</div>
    <div class="nav-item" id="nav-curated" onclick="setEntView('curated')">精选({curated_count})</div>
    <div class="nav-item" id="nav-all" onclick="setEntView('all')">全量({total})</div>
  </div>
</div>

<div class="main">

<div class="header">
  <h2>银发经济企业数据库</h2>
  <p class="stats header-stats">共 {total} 家企业 · P0 {p0_count} 家 · P1 {p1_count} 家 · 国内 {china_count} 家 · 海外 {overseas_count} 家</p>

  <div style="margin-top:10px;">
    <div class="view-pills">
      <button class="view-pill active" id="pill-curated" onclick="setEntView('curated')">精选({curated_count})</button>
      <button class="view-pill" id="pill-all" onclick="setEntView('all')">全量({total})</button>
    </div>
  </div>
</div>

<div class="search-wrap">
  <input type="text" id="search" placeholder="搜索企业名称..." oninput="filterEnt()">
</div>

<div class="filter-row">
  <span class="f-label">优先级</span>
  <button class="f-btn active" data-pri="all">全部</button>
  <button class="f-btn" data-pri="P0">P0</button>
  <button class="f-btn" data-pri="P1">P1</button>
  <button class="f-btn" data-pri="P2">P2</button>
  <span class="f-label" style="margin-left:12px;">地区</span>
  <button class="f-btn active" data-reg="all">全部</button>
  <button class="f-btn" data-reg="china">国内</button>
  <button class="f-btn" data-reg="overseas">海外</button>
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
  <th>级别</th>
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
  <p>数据来源：选题库 · Stage (Not Age) · 许之怿行业图谱</p>
</div>
</div>

<script>
let activePri = 'all';
let activeReg = 'all';
let activeCat = 'all';
let activeView = 'curated';

function setEntView(view) {{
  activeView = view;

  // Nav
  document.getElementById('nav-curated').classList.toggle('active', view==='curated');
  document.getElementById('nav-all').classList.toggle('active', view==='all');

  // Pills
  document.getElementById('pill-curated').classList.toggle('active', view==='curated');
  document.getElementById('pill-all').classList.toggle('active', view==='all');

  filterEnt();
}}

function filterEnt() {{
  const q = document.getElementById('search').value.toLowerCase();
  const rows = document.querySelectorAll('.data-row');
  let visible = 0;

  rows.forEach(row => {{
    const pri = row.dataset.priority;
    const reg = row.dataset.region;
    const cat = row.dataset.cat;
    const name = (row.dataset.name || '').toLowerCase();

    // In curated mode, hide P2 rows
    if (activeView === 'curated' && pri === 'P2') {{
      row.style.display = 'none';
      return;
    }}

    const priMatch = activePri === 'all' || pri === activePri;
    const regMatch = activeReg === 'all' || reg === activeReg;
    const catMatch = activeCat === 'all' || cat === activeCat;
    const searchMatch = !q || name.includes(q);

    row.style.display = (priMatch && regMatch && catMatch && searchMatch) ? '' : 'none';
    if (row.style.display !== 'none') visible++;
  }});

  // Update count in nav
  document.querySelector('#nav-ent .count').textContent =
    activeView === 'curated' ? '(' + visible + ')' : '(%s)';
}}

// Priority buttons
document.querySelectorAll('[data-pri]').forEach(btn => {{
  btn.addEventListener('click', function() {{
    document.querySelectorAll('[data-pri]').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    activePri = this.dataset.pri;
    filterEnt();
  }});
}});

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
</script>
</body>
</html>'''

    # Inject total count into JS (replace only the specific placeholder)
    html = html.replace("'%s'", "'" + str(total) + "'")

    out_path = os.path.join(OUTPUT_DIR, "enterprise.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated: {out_path}")
    print(f"Total: {total} | Curated: {curated_count} (P0={p0_count}, P1={p1_count})")
    print(f"Categories: {len(sorted_cats)} top-level groups")


if __name__ == "__main__":
    generate()
