"""
HTML generator for Silver Pulse daily brief — v3 clean UI.
Left sidebar nav + right content stream (AI-HOT inspired).
Supports: curated/full views, domestic/overseas filter, viral tag.
"""
import json
import os
import glob
import re
from datetime import datetime

from config import (
    SITE_TITLE, SITE_SUBTITLE, OUTPUT_DIR, DATA_DIR,
    INDUSTRY_TAGS, EVENT_TAGS, HIGH_VALUE_THRESHOLD, WATCH_THRESHOLD,
    OVERSEAS_SOURCES, SILVER_FINANCE_ACCOUNTS,
)

OVERSEAS_SOURCE_NAMES = {
    "FierceHealthcare", "Crunchbase News", "TheGerontechnologist",
    "Senior Housing News", "Home Health Care News",
    "McKnight's Senior Living", "MobiHealthNews",
    "Bloomberg Law News", "Aging in Place Technology News",
    "Forbes", "TechCrunch",
}


def load_raw_articles():
    raw_files = sorted(glob.glob(os.path.join(DATA_DIR, "raw_*.json")), reverse=True)
    if not raw_files:
        return []
    with open(raw_files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def title_match(t1, t2):
    t1_clean = re.sub(r'\s+', '', t1.lower())[:50]
    t2_clean = re.sub(r'\s+', '', t2.lower())[:50]
    return t1_clean == t2_clean or (len(t1_clean) > 20 and t1_clean[:30] == t2_clean[:30])


def is_overseas_source(source_name):
    s = source_name.strip()
    if s in OVERSEAS_SOURCE_NAMES:
        return True
    return False


def merge_articles(scored, raw):
    scored_urls = {}
    scored_titles = {}
    for s in scored:
        url = (s.get('url', '') or '').split('?')[0].rstrip('/')
        if url:
            scored_urls[url] = s
        title = (s.get('title', '') or '').strip()
        if title:
            scored_titles[re.sub(r'\s+', '', title.lower())] = s

    merged = []
    seen_raw_urls = set()

    for s in scored:
        s['view'] = 'curated'
        src = s.get('source', '')
        s['region'] = 'overseas' if is_overseas_source(src) else ('domestic' if src else 'unknown')
        merged.append(s)
        url = (s.get('url', '') or '').split('?')[0].rstrip('/')
        if url:
            seen_raw_urls.add(url)

    for r in raw:
        url = (r.get('url', '') or '').split('?')[0].rstrip('/')
        if url and url in scored_urls:
            continue
        if url and url in seen_raw_urls:
            continue
        title = (r.get('title', '') or '').strip()
        title_key = re.sub(r'\s+', '', title.lower())
        if title_key in scored_titles:
            continue
        duplicate = False
        for st_key, st in scored_titles.items():
            if title_match(title, st.get('title', '')):
                duplicate = True
                break
        if duplicate:
            continue

        r['view'] = 'raw'
        r['final_score'] = 0
        r['category'] = 'raw'
        r['tags'] = []
        r['recommendation'] = ''
        r['viral'] = False
        src = r.get('source', '')
        r['region'] = 'overseas' if is_overseas_source(src) else ('domestic' if src else 'unknown')
        merged.append(r)
        if url:
            seen_raw_urls.add(url)

    return merged


def build_card_html(art):
    score = art.get("final_score", 0)
    title = art.get("title", "Untitled")
    url = art.get("url", "#")
    source = art.get("source", "Unknown")
    date = art.get("date", "")
    summary = art.get("summary", art.get("raw_content", ""))[:300]
    recommendation = art.get("recommendation", art.get("suggestion", ""))
    tags = art.get("tags", [])
    view = art.get("view", "curated")
    region = art.get("region", "unknown")
    is_viral = art.get("viral", False)

    if view == "raw":
        score_badge = ""
        quality_class = "quality-raw"
    elif score >= HIGH_VALUE_THRESHOLD:
        score_badge = '<span class="score-badge quality-high">%s</span>' % score
        quality_class = "quality-high"
    elif score >= WATCH_THRESHOLD:
        score_badge = '<span class="score-badge quality-watch">%s</span>' % score
        quality_class = "quality-watch"
    else:
        score_badge = '<span class="score-badge quality-low">%s</span>' % score
        quality_class = "quality-low"

    viral_badge = '<span class="viral-tag">🔥 爆款</span>' if is_viral else ''

    region_tag = ""
    if region == "overseas":
        region_tag = '<span class="region-tag region-overseas">海外</span>'
    elif region == "domestic":
        region_tag = '<span class="region-tag region-domestic">国内</span>'

    tags_html = "".join(
        '<span class="tag">%s</span>' % t for t in tags[:4]
    ) if tags else ""

    suggestion_html = ""
    if recommendation and view == "curated":
        rec_text = recommendation.replace(chr(10), "<br>")
        suggestion_html = '<div class="rec-box">%s</div>' % rec_text

    card = (
        '<div class="feed-item" data-view="%s" data-score="%s" '
        'data-date="%s" data-tags="%s" data-region="%s">\n'
        '  <div class="feed-time">%s</div>\n'
        '  <div class="feed-body">\n'
        '    <div class="feed-meta">'
        '      <span class="feed-source">%s</span>'
        '      %s %s %s\n'
        '    </div>\n'
        '    <h3 class="feed-title"><a href="%s" target="_blank" rel="noopener">%s</a></h3>\n'
        '%s'
        '%s'
        '%s\n'
        '  </div>\n'
        '</div>'
    ) % (
        view, str(score), date, ",".join(tags), region,
        date or "",
        source, region_tag, score_badge, viral_badge,
        url, title,
        '<p class="feed-summary">%s</p>\n' % summary if summary else "",
        '<div class="feed-tags">%s</div>\n' % tags_html if tags_html else "",
        suggestion_html,
    )
    return card


# === CSS Stylesheet (static) ===
CSS_STYLES = """
:root{--bg:#f5f5f5;--sidebar-bg:#fff;--card-bg:#fff;--text:#1a1a1a;
--text-secondary:#666;--text-muted:#999;--border:#e8e8e8;--accent:#0891b2;
--accent-light:#ecfeff;--star:#f59e0b;--watch:#3b82f6;--low:#d1d5db;
--rec-bg:#f0fdf4;--rec-border:#bbf7d0;--radius:8px}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.6;display:flex;min-height:100vh}
.sidebar{width:200px;background:var(--sidebar-bg);border-right:1px solid var(--border);position:fixed;top:0;left:0;height:100vh;overflow-y:auto;padding:20px 0;flex-shrink:0;z-index:10}
.sidebar-logo{padding:0 16px 16px;border-bottom:1px solid var(--border);margin-bottom:12px}
.sidebar-logo h1{font-size:18px;font-weight:700;color:var(--accent)}
.logo-sub{font-size:11px;color:var(--text-muted);margin-top:2px}
.nav-section{padding:4px 0}
.nav-label{font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.5px;padding:6px 16px 4px;font-weight:600}
.nav-item{display:block;padding:8px 16px 8px 24px;font-size:13px;color:var(--text-secondary);text-decoration:none;cursor:pointer;border-left:3px solid transparent;transition:all .15s;position:relative}
.nav-item:hover{background:#fafafa;color:var(--text)}
.nav-item.active{background:var(--accent-light);color:var(--accent);border-left-color:var(--accent);font-weight:600}
.nav-item .count{float:right;font-size:11px;color:var(--text-muted);font-weight:400}
.nav-divider{height:1px;background:var(--border);margin:8px 16px}
.main{flex:1;margin-left:200px;max-width:980px;width:calc(100% - 200px);padding:24px 32px 60px}
.header{margin-bottom:20px}
.header-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.header h2{font-size:20px;font-weight:700}
.header-stats{font-size:12px;color:var(--text-muted)}
.view-pills{display:inline-flex;gap:4px;background:var(--bg);padding:3px;border-radius:20px;margin-bottom:16px}
.view-pill{padding:5px 16px;border-radius:17px;border:none;background:transparent;cursor:pointer;font-size:12px;font-weight:500;color:var(--text-secondary);transition:all .15s}
.view-pill.active{background:var(--card-bg);color:var(--text);box-shadow:0 1px 3px rgba(0,0,0,.08);font-weight:600}
.region-pills{display:inline-flex;gap:4px;margin-left:12px;vertical-align:middle}
.region-pill{padding:5px 14px;border-radius:17px;border:1px solid var(--border);background:var(--card-bg);cursor:pointer;font-size:11px;color:var(--text-secondary);transition:all .15s;white-space:nowrap}
.region-pill.active{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
.tag-bar{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:16px;align-items:center}
.tag-bar-label{font-size:11px;color:var(--text-muted);margin-right:4px}
.tag-btn{padding:3px 10px;border-radius:14px;border:1px solid var(--border);background:var(--card-bg);font-size:11px;cursor:pointer;color:var(--text-secondary);white-space:nowrap;transition:all .15s}
.tag-btn:hover{border-color:var(--accent);color:var(--accent)}
.tag-btn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.feed-item{display:flex;gap:14px;padding:16px 0;border-bottom:1px solid var(--border)}
.feed-item:last-child{border-bottom:none}
.feed-time{flex-shrink:0;width:52px;font-size:13px;font-weight:700;color:var(--text-muted);padding-top:2px;text-align:right}
.feed-body{flex:1;min-width:0}
.feed-meta{display:flex;align-items:center;gap:6px;margin-bottom:5px;flex-wrap:wrap}
.feed-source{font-size:12px;color:var(--text-muted);font-weight:500}
.region-tag{font-size:10px;padding:1px 7px;border-radius:10px;font-weight:600}
.region-overseas{background:#ecfdf5;color:#065f46}
.region-domestic{background:#eff6ff;color:#1e40af}
.score-badge{font-size:11px;font-weight:700;padding:1px 8px;border-radius:10px}
.quality-high{background:#fef3c7;color:#92400e}
.quality-watch{background:#dbeafe;color:#1e40af}
.quality-low{background:#f3f4f6;color:#6b7280}
.quality-raw{background:#f9fafb;color:#9ca3af;font-weight:400}
.viral-tag{font-size:11px;font-weight:700;color:#dc2626;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
.feed-title{font-size:15px;font-weight:600;line-height:1.45;margin-bottom:4px}
.feed-title a{color:var(--text);text-decoration:none}
.feed-title a:hover{color:var(--accent)}
.feed-summary{font-size:13px;color:var(--text-secondary);line-height:1.55;margin-bottom:6px}
.feed-tags{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:6px}
.tag{font-size:10px;padding:2px 8px;border-radius:4px;background:#f0f0f0;color:var(--text-secondary);font-weight:500}
.rec-box{background:var(--rec-bg);border:1px solid var(--rec-border);border-radius:6px;padding:10px 12px;font-size:12px;color:#166534;line-height:1.6;margin-top:4px;word-break:break-word}
.sort-row{display:flex;gap:6px;margin-bottom:16px;font-size:12px;align-items:center;color:var(--text-muted)}
.sort-btn{padding:4px 12px;border-radius:6px;border:1px solid var(--border);background:var(--card-bg);cursor:pointer;font-size:12px;color:var(--text-secondary)}
.sort-btn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.footer{text-align:center;padding:32px 0 16px;font-size:12px;color:var(--text-muted);border-top:1px solid var(--border);margin-top:24px}
.hidden{display:none!important}
@media(max-width:768px){.sidebar{display:none}.main{margin-left:0;width:100%;padding:16px;max-width:100%}.feed-time{width:42px;font-size:11px}.feed-title{font-size:14px}}
"""


JS_SCRIPT = """
let activeView='curated';
let activeRegion='all';
let activeTag='all';
let activeSort='time';
const items=document.querySelectorAll('.feed-item');

function updateDisplay(){
  let visible=0;
  items.forEach(item=>{
    const v=item.dataset.view;
    const tags=item.dataset.tags||'';
    const reg=item.dataset.region||'';
    const sc=parseFloat(item.dataset.score)||0;
    const vm=activeView==='all'||v==='curated';
    const rm=activeRegion==='all'||reg===activeRegion||(activeView==='all');
    const tm=activeView==='all'||activeTag==='all'||tags.includes(activeTag);
    const isArc=activeView==='curated'&&sc>0&&sc<%s;
    if(vm&&rm&&tm){
      if(isArc){item.style.opacity='.35';item.style.pointerEvents='none';visible++}
      else{item.style.opacity='';item.style.pointerEvents='';visible++}
    }else{item.style.display='none'}
  });
  const s=document.getElementById('header-stats');
  s.textContent=activeView==='all'
    ?'更新于 %s · 全量 %s 条'
    :'更新于 %s · 精选 '+visible+' 条 · 高价值 %s 条';
  document.getElementById('tag-bar').style.display=activeView==='all'?'none':'flex';
  document.getElementById('region-pills').style.display=activeView==='all'?'none':'flex';
  document.getElementById('sort-bar').style.display=activeView==='all'?'none':'flex';
}

function sortItems(){
  const c=document.getElementById('feed-container');
  Array.from(items).sort((a,b)=>{
    if(activeSort==='score')return parseFloat(b.dataset.score)-parseFloat(a.dataset.score);
    return(b.dataset.date||'').localeCompare(a.dataset.date||'');
  }).forEach(el=>c.appendChild(el));
}

function setView(view){
  activeView=view;activeTag='all';
  document.getElementById('pill-curated').classList.toggle('active',view==='curated');
  document.getElementById('pill-all').classList.toggle('active',view==='all');
  document.querySelectorAll('.tag-btn').forEach(b=>b.classList.toggle('active',b.dataset.tag==='all'));
  document.querySelectorAll('.region-pill').forEach(b=>b.classList.toggle('active',b.dataset.region==='all'));
  document.querySelectorAll('.sort-btn').forEach(b=>b.classList.toggle('active',b.dataset.sort==='time'));
  activeRegion='all';activeSort='time';sortItems();updateDisplay();
}

document.querySelectorAll('.region-pill').forEach(btn=>{
  btn.addEventListener('click',function(){
    document.querySelectorAll('.region-pill').forEach(b=>b.classList.remove('active'));
    this.classList.add('active');activeRegion=this.dataset.region;updateDisplay();
  });
});
document.querySelectorAll('.sort-btn').forEach(btn=>{
  btn.addEventListener('click',function(){
    document.querySelectorAll('.sort-btn').forEach(b=>b.classList.remove('active'));
    this.classList.add('active');activeSort=this.dataset.sort;sortItems();updateDisplay();
  });
});
document.querySelectorAll('.tag-btn').forEach(btn=>{
  btn.addEventListener('click',function(){
    document.querySelectorAll('.tag-btn').forEach(b=>b.classList.remove('active'));
    this.classList.add('active');activeTag=this.dataset.tag;updateDisplay();
  });
});
updateDisplay();
"""


def generate_html(scored_articles=None, output_path=None):
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "index.html")

    if scored_articles is None:
        from scorer import load_scored
        scored_articles = load_scored()

    raw_articles = load_raw_articles()
    merged = merge_articles(scored_articles, raw_articles)
    merged.sort(key=lambda a: a.get("date", "0000-00-00"), reverse=True)

    all_tags = set()
    for art in merged:
        if art.get("view") == "curated":
            for tag in art.get("tags", []):
                all_tags.add(tag)
    sorted_tags = sorted(all_tags)

    curated_count = sum(1 for a in merged if a.get("view") == "curated")
    total_count = len(merged)
    high_count = sum(1 for a in merged if a.get("view") == "curated" and a.get("final_score", 0) >= HIGH_VALUE_THRESHOLD)

    domestic_curated = sum(1 for a in merged if a.get("view") == "curated" and a.get("region") == "domestic")
    overseas_curated = sum(1 for a in merged if a.get("view") == "curated" and a.get("region") == "overseas")

    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build parts
    cards_html = "".join(build_card_html(art) for art in merged)

    tag_buttons = "".join(
        '<button class="tag-btn" data-tag="%s">%s</button>' % (t, t) for t in sorted_tags
    )

    # Inject values into JS template
    js = JS_SCRIPT % (str(WATCH_THRESHOLD), today_str, str(total_count), today_str, str(high_count))

    # Assemble full HTML using string concatenation (no giant f-string)
    parts = [
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<title>%s</title>' % SITE_TITLE,
        '<style>%s</style>' % CSS_STYLES,
        '</head>\n<body>',

        # Sidebar
        '<div class="sidebar">',
        '<div class="sidebar-logo">',
        '<h1>Silver Pulse 银脉</h1>',
        '<p class="logo-sub">Silver Pulse</p>',
        '</div>',
        '<div class="nav-section">',
        '<div class="nav-label">内容</div>',
        '<a href="index.html" class="nav-item active">资讯看板</a>',
        '<a href="enterprise.html" class="nav-item">企业库</a>',
        '</div>',

        # Main content
        '<div class="main">',
        '<div class="header">',
        '<div class="header-top">',
        '<h2>银发经济每日速览</h2>',
        '<div class="header-stats" id="header-stats">更新于 %s · 精选 %s 条 · 高价值 %s 条</div>' % (today_str, curated_count, high_count),
        '</div>',
        '<div style="display:flex;align-items:center;flex-wrap:wrap;">',
        '<div class="view-pills">',
        '<button class="view-pill active" id="pill-curated" onclick="setView(\'curated\')">精选(%s)</button>' % curated_count,
        '<button class="view-pill" id="pill-all" onclick="setView(\'all\')">全量(%s)</button>' % total_count,
        '</div>',
        '<div class="region-pills" id="region-pills">',
        '<button class="region-pill active" data-region="all">全部</button>',
        '<button class="region-pill" data-region="domestic">国内(%s)</button>' % domestic_curated,
        '<button class="region-pill" data-region="overseas">海外(%s)</button>' % overseas_curated,
        '</div></div></div>',

        # Tag bar
        '<div class="tag-bar" id="tag-bar">',
        '<span class="tag-bar-label">标签:</span>',
        '<button class="tag-btn active" data-tag="all">全部</button>',
        tag_buttons,
        '</div>',

        # Sort bar
        '<div class="sort-row" id="sort-bar">排序:',
        '<button class="sort-btn active" data-sort="time">最新优先</button>',
        '<button class="sort-btn" data-sort="score">评分降序</button>',
        '</div>',

        # Feed container
        '<div id="feed-container">',
        cards_html,
        '</div>',

        # Footer
        '<div class="footer">',
        '<p>Silver Pulse 银脉 · 银发经济投融资每日速览</p>',
        '<p>Powered by WorkBuddy · 海外 + 中文双源覆盖</p>',
        '</div>',

        # About section
        '<div id="about" class="hidden" style="margin-top:24px;padding:16px;background:var(--card-bg);border-radius:var(--radius);">',
        '<p style="font-size:13px;color:var(--text-secondary);line-height:1.8;"><b>关于 Silver Pulse 银脉</b></p>',
        '<p style="font-size:13px;color:var(--text-secondary);line-height:1.8;">面向银发经济创业者的全球投融资资讯聚合看板。<br>以海外为镜，照中国之路。</p>',
        '</div>',

        # Close main + body
        '</div>',
        '\n<script>\n%s\n</script>\n</body>\n</html>' % js,
    ]

    html = "\n".join(parts)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Generated: %s" % output_path)
    print("Articles: %s total (%s curated, %s high-value)" % (total_count, curated_count, high_count))
    return output_path


if __name__ == "__main__":
    from scorer import load_scored
    articles = load_scored()
    if articles:
        generate_html(articles)
    else:
        print("No scored articles found.")
