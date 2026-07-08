# -*- coding: utf-8 -*-
"""
Silver Pulse 统一设计系统 (UI Common)
v1.0 — 现代视觉 / 深色模式 / 响应式 / 三页面共用

所有页面 (index / enterprise / about) 共用同一套 CSS + 侧栏 + 主题脚本，
保证视觉一致、可维护性、深色模式全局生效。

使用方式（见 generator.py / gen_enterprise.py / gen_about.py）：
  from ui_common import COMMON_CSS, SIDEBAR, THEME_JS
  - HTML 内用 <style>__COMMON_CSS__</style> 占位，生成后 .replace("__COMMON_CSS__", COMMON_CSS)
  - 侧栏用 __SIDEBAR__ 占位，生成后 .replace("__SIDEBAR__", SIDEBAR("index"))
  - 在 </body> 前插入 THEME_JS
"""

# ============================================================
# 1. 统一 CSS 设计系统
# ============================================================
COMMON_CSS = """
/* ===== Silver Pulse 设计系统 v1.0 ===== */
:root{
  --bg:#eef2f7;
  --surface:#ffffff;
  --surface-2:#f8fafc;
  --sidebar-bg:#0f172a;
  --sidebar-text:#cbd5e1;
  --sidebar-text-dim:#7c8aa3;
  --sidebar-active:#22d3ee;
  --text:#1e293b;
  --text-secondary:#51607a;
  --text-muted:#8a94a6;
  --border:#e3e8ef;
  --border-strong:#cdd6e3;
  --accent:#0ea5b7;
  --accent-strong:#0c7e8c;
  --accent-light:#e0f7fa;
  --accent-grad:linear-gradient(135deg,#0ea5b7 0%,#0c7e8c 100%);
  --radius:14px;
  --radius-sm:9px;
  --shadow-sm:0 1px 2px rgba(15,23,42,.05),0 1px 3px rgba(15,23,42,.06);
  --shadow-md:0 4px 14px rgba(15,23,42,.08);
  --shadow-lg:0 10px 30px rgba(15,23,42,.12);
  --tag-bg:#e0f2fe; --tag-text:#0369a1;
  --cat-bg:#ecfdf5; --cat-text:#047857;
  --fund-bg:#fef3c7; --fund-text:#92650e;
  --fund-total-bg:#ecfdf5; --fund-total-text:#166534;
  --good:#16a34a; --warn:#d97706; --bad:#dc2626;
  --maxw:1080px;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei","Hiragino Sans GB",sans-serif;
  background:var(--bg);color:var(--text);line-height:1.62;-webkit-font-smoothing:antialiased;display:flex;min-height:100vh;font-size:14px}

/* ===== Sidebar (固定深色) ===== */
.sidebar{width:212px;background:var(--sidebar-bg);position:fixed;top:0;left:0;height:100vh;overflow-y:auto;
  padding:22px 0 16px;flex-shrink:0;z-index:30;display:flex;flex-direction:column}
.sidebar-logo{padding:0 20px 18px;border-bottom:1px solid rgba(255,255,255,.08);margin-bottom:14px}
.sidebar-logo h1{font-size:17px;font-weight:800;color:#fff;letter-spacing:.3px;line-height:1.3}
.sidebar-logo h1 span{background:linear-gradient(135deg,#22d3ee,#34d399);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.logo-sub{font-size:11px;color:var(--sidebar-text-dim);margin-top:4px;letter-spacing:.5px}
.nav-section{padding:4px 0;flex:1}
.nav-label{font-size:10px;color:var(--sidebar-text-dim);text-transform:uppercase;letter-spacing:1px;padding:8px 20px 6px;font-weight:700}
.nav-item{display:flex;align-items:center;gap:9px;padding:9px 20px;font-size:13.5px;color:var(--sidebar-text);
  text-decoration:none;cursor:pointer;border-left:3px solid transparent;transition:all .16s;font-weight:500}
.nav-item .nav-ico{font-size:15px;width:18px;text-align:center;opacity:.9}
.nav-item:hover{background:rgba(255,255,255,.06);color:#fff}
.nav-item.active{background:linear-gradient(90deg,rgba(34,211,238,.18),transparent);color:#fff;border-left-color:var(--sidebar-active);font-weight:700}
.sidebar-footer{margin-top:auto;padding:14px 20px 0;border-top:1px solid rgba(255,255,255,.08)}
.theme-toggle{width:100%;display:flex;align-items:center;justify-content:center;gap:7px;padding:8px;border-radius:10px;
  border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.05);color:var(--sidebar-text);
  font-size:12.5px;cursor:pointer;transition:all .16s;font-family:inherit}
.theme-toggle:hover{background:rgba(255,255,255,.12);color:#fff}

/* ===== Main ===== */
.main{flex:1;margin-left:212px;width:calc(100% - 212px);max-width:var(--maxw);padding:30px 38px 70px}
.header{margin-bottom:20px}
.header-top{display:flex;justify-content:space-between;align-items:flex-end;gap:14px;flex-wrap:wrap;margin-bottom:6px}
.header h2{font-size:23px;font-weight:800;letter-spacing:.2px}
.header-stats{font-size:12px;color:var(--text-muted);white-space:nowrap}
.header-signal{font-size:11.5px;color:var(--accent-strong);margin-top:3px;font-weight:600}
.dl-btn{font-size:12px;color:var(--accent-strong);text-decoration:none;border:1px solid var(--accent);
  padding:6px 13px;border-radius:10px;white-space:nowrap;font-weight:600;transition:all .15s;background:#fff}
.dl-btn:hover{background:var(--accent);color:#fff}

/* ===== 筛选 / 搜索 ===== */
.filter-bar{display:flex;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:14px}
.view-pills,.region-pills{display:inline-flex;gap:4px;background:var(--surface);padding:3px;border-radius:20px;box-shadow:var(--shadow-sm)}
.view-pill,.region-pill{padding:6px 15px;border-radius:18px;border:none;background:transparent;cursor:pointer;
  font-size:12.5px;font-weight:600;color:var(--text-secondary);transition:all .15s;white-space:nowrap;font-family:inherit}
.view-pill.active,.region-pill.active{background:var(--accent-grad);color:#fff;box-shadow:var(--shadow-sm)}
.search-inline{padding:7px 14px;border:1px solid var(--border);border-radius:12px;font-size:12.5px;outline:none;
  background:var(--surface);color:var(--text);width:180px;transition:all .15s;font-family:inherit}
.search-inline:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(14,165,183,.12);width:230px}

.news-search-row{margin-bottom:16px}
.news-search{width:100%;box-sizing:border-box;padding:11px 17px;border:1.5px solid var(--border);border-radius:14px;
  font-size:13.5px;outline:none;background:var(--surface);color:var(--text);transition:all .15s;font-family:inherit}
.news-search:focus{border-color:var(--accent);box-shadow:0 0 0 4px rgba(14,165,183,.10)}

.filter-section{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:13px 16px;margin-bottom:16px;box-shadow:var(--shadow-sm)}
.filter-row{display:flex;align-items:center;gap:7px;margin-bottom:7px;flex-wrap:wrap}
.filter-row:last-child{margin-bottom:0}
.filter-label{font-size:11.5px;color:var(--text-muted);min-width:34px;font-weight:700}
.filter-btns{display:flex;flex-wrap:wrap;gap:5px;flex:1;justify-content:flex-start}
.filter-btn{padding:4px 12px;border-radius:13px;border:1px solid var(--border);background:var(--surface-2);
  font-size:12px;cursor:pointer;color:var(--text-secondary);white-space:nowrap;transition:all .13s;font-family:inherit}
.filter-btn:hover{border-color:var(--accent);color:var(--accent-strong)}
.filter-btn.active{background:var(--accent-grad);color:#fff;border-color:transparent;font-weight:600}
/* 紧凑筛选行 (T27: 事件·领域·标签合并一行) */
.filter-row-compact{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.filter-divider{color:var(--border-strong);font-size:11px;margin:0 2px;user-select:none}
/* 折叠按钮 */
.filter-btn-more,.f-btn-more{padding:3px 10px;border-radius:13px;border:1px dashed var(--accent);background:var(--accent-light);
  font-size:11.5px;cursor:pointer;color:var(--accent-strong);white-space:nowrap;transition:all .13s;font-family:inherit;font-weight:600}
.filter-btn-more:hover,.f-btn-more:hover{background:var(--accent);color:#fff;border-style:solid}
.filter-btn-more.active,.f-btn-more.active{background:var(--accent);color:#fff;border-style:solid}
#more-tags-box{margin-top:6px;display:flex;flex-wrap:wrap;gap:5px}

/* 排序箭头按钮（替代下拉框，常见 ↑↓ 切换） */
.sort-arrow{display:inline-flex;align-items:center;gap:3px;padding:4px 13px;border:1px solid var(--accent);border-radius:13px;
  background:var(--surface-2);font-size:12px;cursor:pointer;color:var(--accent-strong);white-space:nowrap;
  transition:all .13s;font-family:inherit;font-weight:600}
.sort-arrow:hover{background:var(--accent-light)}
.sort-arrow.active{background:var(--accent-grad);color:#fff;border-color:transparent}

/* ===== 资讯流卡片 ===== */
.feed-item{display:flex;gap:14px;padding:15px 4px;border-bottom:1px solid var(--border);transition:background .12s}
.feed-item:last-child{border-bottom:none}
.feed-item:hover{background:var(--surface)}
.feed-item.is-selected{background:linear-gradient(90deg,var(--accent-light),transparent);border-left:3px solid var(--accent);padding-left:12px;border-radius:0 8px 8px 0}
.feed-time{flex-shrink:0;width:50px;font-size:12px;font-weight:800;color:var(--text-muted);padding-top:2px;text-align:right}
.feed-body{flex:1;min-width:0}
.feed-meta{display:flex;align-items:center;gap:6px;margin-bottom:3px;flex-wrap:wrap}
.feed-source{font-size:11.5px;color:var(--text-muted);font-weight:600}
.feed-class{display:flex;align-items:center;gap:4px;margin-bottom:5px;flex-wrap:wrap}
.feed-title{font-size:14.5px;font-weight:700;line-height:1.45;margin-bottom:3px}
.feed-title a{color:var(--text);text-decoration:none}
.feed-title a:hover{color:var(--accent-strong)}
.feed-summary{font-size:12.5px;color:var(--text-secondary);line-height:1.6;margin-bottom:4px}
.feed-rec{font-size:11.5px;color:var(--accent-strong);line-height:1.5;margin-bottom:4px;font-style:italic}
.feed-tags{display:flex;flex-wrap:wrap;gap:4px;margin-top:5px;justify-content:flex-start}
.date-group-title{font-size:13px;font-weight:800;color:var(--accent-strong);margin:18px 0 9px;padding-left:11px;border-left:3px solid var(--accent)}

/* ===== 徽章 ===== */
.badge-region{font-size:10px;padding:2px 8px;border-radius:10px;font-weight:700}
.badge-region.region-overseas{background:var(--cat-bg);color:var(--cat-text)}
.badge-region.region-domestic{background:#eff6ff;color:#1d4ed8}
.badge-event{font-size:10.5px;padding:2px 9px;border-radius:7px;background:var(--fund-bg);color:var(--fund-text);font-weight:700}
.badge-domain{font-size:10.5px;padding:2px 9px;border-radius:7px;background:var(--surface-2);color:var(--text-secondary);font-weight:600;border:1px solid var(--border)}
.badge-tag{font-size:10.5px;padding:2px 9px;border-radius:7px;background:var(--tag-bg);color:var(--tag-text);font-weight:600}
.badge-rv{font-size:10.5px;font-weight:800;padding:2px 9px;border-radius:10px;white-space:nowrap;color:#fff}
.badge-rv.s-high{background:rgba(16,185,.129,.72)}
.badge-rv.s-mid{background:rgba(14,165,183,.68)}
.badge-rv.s-low{background:rgba(148,163,184,.55)}
.badge-deep{background:var(--fund-bg);color:var(--fund-text);font-size:10.5px;font-weight:800;padding:2px 9px;border-radius:10px;white-space:nowrap;margin-left:4px}
.badge-score{font-size:12px;font-weight:800;padding:3px 10px;border-radius:10px;white-space:nowrap;color:#fff}
/* 评分半透明底色（按分数段区分） */
.badge-score.s-high{background:rgba(16,185,129,.72)}   /* ≥7 绿 */
.badge-score.s-mid{background:rgba(14,165,183,.68)}     /* 4–6.9 蓝 */
.badge-score.s-low{background:rgba(148,163,184,.55)}    /* <4 灰 */
.viral-tag{font-size:14px;font-weight:800;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.55}}


/* ===== 精选卡片增强 ===== */
.sel-scores{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin:5px 0 3px}
.dim-line{display:flex;gap:5px;flex-wrap:wrap}
.dim-chip{font-size:10.5px;color:var(--text-secondary);background:var(--surface-2);padding:2px 8px;border-radius:9px;font-weight:600;border:1px solid var(--border)}
.dim-chip b{color:var(--accent-strong);font-weight:800}
.update-timeline{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px 17px;margin-bottom:17px;box-shadow:var(--shadow-sm)}
.timeline-title{font-size:13.5px;font-weight:800;color:var(--text);margin-bottom:9px}
.timeline-list{display:flex;flex-direction:column;gap:0;position:relative;padding-left:15px}
.timeline-list:before{content:"";position:absolute;left:4px;top:5px;bottom:5px;width:2px;background:var(--border)}
.timeline-entry{position:relative;padding:6px 9px;font-size:12.5px;color:var(--text-secondary);cursor:pointer;border-radius:8px;transition:all .12s}
.timeline-entry:before{content:"";position:absolute;left:-15px;top:11px;width:9px;height:9px;border-radius:50%;background:var(--accent);border:2px solid #fff;box-shadow:0 0 0 1px var(--border)}
.timeline-entry:hover{background:var(--accent-light)}
.timeline-entry.active{background:var(--accent-light);color:var(--accent-strong);font-weight:700}
.timeline-date{font-weight:700}
.timeline-count{color:var(--text-muted);margin-left:7px}

/* ===== 空状态 ===== */
.empty-state{text-align:center;padding:54px 20px;color:var(--text-muted)}
.empty-state .es-ico{font-size:40px;opacity:.5}
.empty-state .es-text{font-size:14px;margin-top:10px}

/* ===== Footer ===== */
.footer{text-align:center;padding:34px 0 18px;font-size:12px;color:var(--text-muted);border-top:1px solid var(--border);margin-top:28px;line-height:1.7}
.hidden{display:none!important}

/* ===== 企业库卡片 ===== */
.toolbar{margin-bottom:15px}
.f-label{font-size:11.5px;color:var(--text-muted);font-weight:700;margin-right:5px;min-width:36px}
.f-btn{padding:4px 12px;border-radius:15px;border:1px solid var(--border);background:var(--surface);font-size:12px;
  cursor:pointer;color:var(--text-secondary);white-space:nowrap;transition:all .15s;font-family:inherit}
.f-btn:hover{border-color:var(--accent);color:var(--accent-strong)}
.f-btn.active{background:var(--accent-grad);color:#fff;border-color:transparent;font-weight:700}
.f-btn .cnt{font-size:10px;opacity:.7;margin-left:3px}
.f-btn-l2{font-size:10.5px;padding:3px 10px}
.l2-row{padding-left:52px;border-left:3px solid var(--accent);background:var(--accent-light);margin-left:14px;padding-top:7px;padding-bottom:7px;border-radius:0 8px 8px 0;margin-top:6px}
.view-toggle{display:inline-flex;gap:0;margin-left:9px;border:1px solid var(--border);border-radius:15px;overflow:hidden;box-shadow:var(--shadow-sm)}
.view-btn{padding:5px 14px;border:none;background:var(--surface);font-size:12px;cursor:pointer;color:var(--text-secondary);transition:all .15s;font-family:inherit}
.view-btn:hover{background:var(--surface-2)}
.view-btn.active{background:var(--accent-grad);color:#fff;font-weight:700}
.result-count{font-size:11.5px;color:var(--text-muted);margin-bottom:10px;padding-left:3px;font-weight:600}

.ent-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:12px 17px;margin-bottom:7px;
  transition:transform .14s,box-shadow .14s,border-color .14s;box-shadow:var(--shadow-sm)}
.ent-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-md);border-color:var(--border-strong)}
.ent-header{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-bottom:4px}
.ent-name{font-weight:700;font-size:14.5px;color:var(--text)}
.ent-badge{font-size:10px;padding:1px 8px;border-radius:5px;font-weight:600;white-space:nowrap}
.badge-cat{background:var(--cat-bg);color:var(--cat-text)}
.badge-region{font-size:10px;color:var(--text-muted);background:transparent;padding:0 5px;font-weight:600}
.ent-tags{display:inline-flex;gap:4px;flex-wrap:wrap}
.ent-tag{font-size:10.5px;color:var(--tag-text);background:var(--tag-bg);padding:2px 8px;border-radius:6px;font-weight:600}
.ent-desc{font-size:12.5px;color:var(--text-secondary);line-height:1.6;margin:3px 0}
.ent-highlights{font-size:11.5px;color:var(--accent-strong);line-height:1.5;margin:3px 0;font-style:italic}
.ent-meta{display:flex;gap:11px;font-size:11.5px;color:var(--text-muted);flex-wrap:wrap;align-items:center;margin-top:4px}
.meta-item{white-space:nowrap}
.meta-fund{color:var(--fund-text);font-weight:700;background:var(--fund-bg);padding:2px 8px;border-radius:6px}
.meta-fund-total{color:var(--fund-total-text);font-weight:700;background:var(--fund-total-bg);padding:2px 8px;border-radius:6px}
.meta-biz{color:var(--text-secondary);font-size:10.5px;font-style:italic;opacity:.88}
.meta-source{font-size:10.5px;opacity:.7}
.meta-links{margin-left:auto}
.ent-link{font-size:11.5px;color:var(--accent-strong);text-decoration:underline}
.ent-recent{font-size:11.5px;color:var(--accent-strong);margin-top:4px;line-height:1.5}
.ent-recent-link{color:var(--accent-strong);text-decoration:underline}
.ent-recent-date{color:var(--text-muted);font-size:10.5px}
.ent-competitors{font-size:11.5px;color:var(--text-secondary);margin-top:4px;line-height:1.55}
.ent-comp-link{color:var(--text);text-decoration:underline;font-weight:600}
.ent-comp-link:hover{color:var(--accent-strong)}
.top-section{background:var(--accent-light);border:1px solid #a5f3fc;border-radius:var(--radius);padding:15px 18px;margin-bottom:18px}
.top-title{font-size:15px;font-weight:800;color:var(--accent-strong);margin-bottom:6px;display:flex;align-items:center;gap:7px}
.top-sub{font-size:11.5px;color:var(--muted);margin:0 0 11px;line-height:1.5}
.top-list{display:flex;flex-direction:column;gap:5px}
.top-row{display:flex;align-items:center;gap:9px;flex-wrap:wrap;font-size:12.5px;padding:4px 0;border-bottom:1px dashed #cffafe}
.top-row:last-child{border-bottom:none}
.top-rank{font-weight:800;color:var(--accent-strong);min-width:20px;text-align:right}
.top-event{font-size:11px;color:var(--fund-text);background:var(--fund-bg);padding:2px 8px;border-radius:6px;font-weight:600}

/* ===== 网站说明页 ===== */
.tab-bar{display:flex;gap:0;margin:22px 0 26px;border-bottom:2px solid var(--border)}
.tab-btn{padding:11px 22px;border:none;background:transparent;font-size:14.5px;font-weight:600;color:var(--text-secondary);
  cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .15s;font-family:inherit;
  white-space:nowrap;flex-shrink:0}
.tab-btn:hover{color:var(--accent-strong)}
.tab-btn.active{color:var(--accent-strong);border-bottom-color:var(--accent);font-weight:800}
.tab-content{display:none}
.tab-content.active{display:block;animation:fade .25s ease}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.section{margin-bottom:34px}
.section h3{font-size:16.5px;font-weight:700;margin-bottom:13px;color:var(--text);padding-left:13px;border-left:3px solid var(--accent)}
.section p{font-size:14px;color:var(--text-secondary);margin-bottom:9px;line-height:1.8}
.section ul{margin:9px 0 13px 22px}
.section li{font-size:14px;color:var(--text-secondary);margin-bottom:5px;line-height:1.75}
.info-table{width:100%;border-collapse:collapse;font-size:13px;margin:13px 0;background:var(--surface);
  border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;table-layout:fixed;box-shadow:var(--shadow-sm)}
.info-table th{background:var(--surface-2);padding:9px 11px;text-align:left;font-size:11px;font-weight:700;color:var(--text-muted);
  text-transform:uppercase;letter-spacing:.3px;border-bottom:1px solid var(--border)}
.info-table td{padding:9px 11px;border-bottom:1px solid #f0f2f6;vertical-align:top;word-wrap:break-word;overflow-wrap:break-word}
.info-table tr:last-child td{border-bottom:none}
.info-table tr:hover{background:var(--surface-2)}
.cat-name{font-weight:700;color:var(--accent-strong);white-space:nowrap}
.src-l1{font-size:10.5px;color:var(--text-muted);margin-top:3px}
.tier-badge{font-size:10.5px;font-weight:800;padding:2px 8px;border-radius:5px;text-align:center;display:inline-block}
.tier-t1{background:#dcfce7;color:#166534}
.tier-t2{background:#dbeafe;color:#1e40af}
.tier-t3{background:#f1f5f9;color:#64748b}
.region-badge{font-size:10.5px;font-weight:600;padding:2px 9px;border-radius:5px;text-align:center}
.region-海外{background:var(--cat-bg);color:var(--cat-text)}
.region-国内{background:#eff6ff;color:#1d4ed8}
.callout{background:var(--accent-light);border:1px solid #a5f3fc;border-radius:var(--radius);padding:13px 17px;margin:13px 0;font-size:13px;color:var(--accent-strong);line-height:1.7}
.callout-warning{background:#fffbeb;border-color:#fcd34d;color:#92650e}
.tag-chip{display:inline-block;font-size:11.5px;padding:3px 9px;border-radius:6px;background:#dbeafe;color:#1e40af;margin:2px;font-weight:600}
.l2-chip{display:inline-block;font-size:10.5px;padding:2px 7px;border-radius:5px;background:var(--surface-2);color:var(--text-secondary);margin:1px;border:1px solid var(--border)}
.l2-method{font-size:10.5px;color:var(--accent-strong);font-weight:600}
.kw-chip{display:inline-block;font-size:11.5px;padding:3px 9px;border-radius:6px;background:var(--cat-bg);color:var(--cat-text);margin:2px;font-weight:600}
.kw-irrelevant{background:#fef2f2;color:#991b1b}
.field-list{margin:13px 0}
.field-item{display:flex;gap:13px;padding:9px 0;border-bottom:1px solid #f1f5f9}
.field-name{font-weight:700;color:var(--text);min-width:150px;font-size:13px;font-family:"SFMono-Regular",Consolas,monospace}
.field-type{color:var(--accent-strong);font-size:12.5px;min-width:64px;font-weight:600}
.field-desc{color:var(--text-secondary);font-size:13px;flex:1}

/* ===== 响应式 ===== */
@media(max-width:860px){
  .sidebar{position:static;width:100%;height:auto;flex-direction:row;align-items:center;overflow-x:auto;padding:12px 16px;gap:6px}
  .sidebar-logo{border-bottom:none;margin-bottom:0;padding:0 14px 0 0;border-right:1px solid rgba(255,255,255,.12)}
  .sidebar-logo h1{font-size:15px}
  .logo-sub{display:none}
  .nav-section{display:flex;align-items:center;gap:4px;flex:initial;padding:0}
  .nav-label{display:none}
  .nav-item{border-left:none;border-radius:9px;padding:8px 13px;white-space:nowrap}
  .nav-item.active{border-left:none;background:linear-gradient(90deg,rgba(34,211,238,.22),rgba(34,211,238,.05))}
  .sidebar-footer{margin-top:0;border-top:none;padding:0 0 0 8px}
  .theme-toggle{width:auto;padding:8px 12px}
  .main{margin-left:0;width:100%;max-width:100%;padding:20px 16px 60px}
  .header h2{font-size:20px}
  .search-inline{width:140px}.search-inline:focus{width:170px}
  .feed-time{width:44px}
}
@media(max-width:480px){
  .main{padding:16px 12px 50px}
}

/* ===== 深色模式 ===== */
@media (prefers-color-scheme: dark){
  :root:not(.light){
    --bg:#0b1120;--surface:#141d2e;--surface-2:#1b2538;--text:#e6edf6;--text-secondary:#9fb0c6;
    --text-muted:#6b7c93;--border:#243044;--border-strong:#33425c;--accent:#22d3ee;--accent-strong:#22d3ee;
    --accent-light:#0c2a33;--tag-bg:#0c2e3a;--tag-text:#5ed4ee;--cat-bg:#0c2a1e;--cat-text:#5eead4;
    --fund-bg:#332a0c;--fund-text:#fcd34d;--fund-total-bg:#0c2a1e;--fund-total-text:#6ee7b7;
    --shadow-sm:0 1px 2px rgba(0,0,0,.3);--shadow-md:0 4px 14px rgba(0,0,0,.4);--shadow-lg:0 10px 30px rgba(0,0,0,.5)
  }
}
:root.dark{
  --bg:#0b1120;--surface:#141d2e;--surface-2:#1b2538;--text:#e6edf6;--text-secondary:#9fb0c6;
  --text-muted:#6b7c93;--border:#243044;--border-strong:#33425c;--accent:#22d3ee;--accent-strong:#22d3ee;
  --accent-light:#0c2a33;--tag-bg:#0c2e3a;--tag-text:#5ed4ee;--cat-bg:#0c2a1e;--cat-text:#5eead4;
  --fund-bg:#332a0c;--fund-text:#fcd34d;--fund-total-bg:#0c2a1e;--fund-total-text:#6ee7b7;
  --shadow-sm:0 1px 2px rgba(0,0,0,.3);--shadow-md:0 4px 14px rgba(0,0,0,.4);--shadow-lg:0 10px 30px rgba(0,0,0,.5)
}
"""


# ============================================================
# 2. 统一侧栏组件
# ============================================================
def SIDEBAR(active):
    """返回侧栏 HTML。active ∈ {index, enterprise, about}。
    顺序：资讯看板 → 企业库 → 我的收藏 → 网站说明。"""
    items = [
        ("index", "📡", "资讯看板", "index.html"),
        ("enterprise", "🏢", "企业库", "enterprise.html"),
        ("about", "📖", "网站说明", "about.html"),
    ]
    nav = []
    for key, ico, label, href in items:
        cls = "nav-item active" if key == active else "nav-item"
        nav.append('<a href="%s" class="%s"><span class="nav-ico">%s</span>%s</a>' % (href, cls, ico, label))
    return (
        '<div class="sidebar">'
        '<div class="sidebar-logo">'
        '<h1>Silver Pulse <span>银脉</span></h1>'
        '<p class="logo-sub">全球银发经济选题情报台</p>'
        '</div>'
        '<div class="nav-section">'
        '<div class="nav-label">导航</div>'
        + "".join(nav)
        + '</div>'
        '<div class="sidebar-footer">'
        '<button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" title="切换深浅色">🌓 主题</button>'
        '</div>'
        '</div>'
    )


# ============================================================
# 3. 主题切换脚本
# ============================================================
THEME_JS = """<script>
function toggleTheme(){
  var r=document.documentElement;
  if(r.classList.contains('dark')){r.classList.remove('dark');localStorage.setItem('theme','light');}
  else{r.classList.add('dark');localStorage.setItem('theme','dark');}
}
(function(){
  var s=localStorage.getItem('theme');
  if(s==='dark'){document.documentElement.classList.add('dark');}
  else if(s==='light'){document.documentElement.classList.remove('dark');}
})();
</script>
"""

# ============================================================
# 4. 收藏 / 反馈机制（localStorage + 导出 JSONL）
# ============================================================
FEEDBACK_CSS = """
/* ===== 收藏 / 反馈 ===== */
.fav-btn{display:inline-flex;align-items:center;gap:4px;font-size:12px;line-height:1;border:1px solid var(--border);background:var(--card);color:var(--muted);border-radius:20px;padding:4px 11px;cursor:pointer;transition:.15s;user-select:none}
.fav-btn:hover{border-color:var(--accent);color:var(--accent-strong)}
.fav-btn.on{border-color:#f59e0b;background:rgba(245,158,11,.12);color:#d97706}
.fav-btn .ico{font-size:13px;transition:transform .15s}
.fav-btn.on .ico{font-size:14px}
.export-fav{margin-left:auto;font-size:12px;border:1px solid var(--accent);color:var(--accent-strong);background:var(--card);border-radius:20px;padding:5px 13px;cursor:pointer;transition:.15s;white-space:nowrap;flex-shrink:0}
.export-fav:hover{background:var(--accent);color:#fff}
.sync-fav{margin-left:8px;font-size:12px;border:1px solid var(--border);color:var(--text-secondary);background:var(--card);border-radius:20px;padding:5px 13px;cursor:pointer;transition:.15s;white-space:nowrap;flex-shrink:0}
.sync-fav:hover{border-color:var(--accent);color:var(--accent-strong)}
.sync-fav.syncing{opacity:.6;cursor:wait}
.sync-set{margin-left:4px;font-size:12px;border:1px solid var(--border);color:var(--text-muted);background:var(--card);border-radius:50%;width:30px;height:30px;cursor:pointer;flex-shrink:0}
.sync-set:hover{border-color:var(--accent);color:var(--accent-strong)}
/* 已收藏筛选胶囊（替代独立抽屉面板） */
.fav-filter-btn{padding:4px 13px;border-radius:15px;border:1.5px dashed #f59e0b;background:transparent;font-size:12px;cursor:pointer;color:#d97706;white-space:nowrap;transition:.15s;font-family:inherit;font-weight:600;display:inline-flex;align-items:center;gap:4px}
.fav-filter-btn:hover{background:rgba(245,158,11,.10);border-style:solid}
.fav-filter-btn.on{background:rgba(245,158,11,.16);border-style:solid;color:#b45309}
.fav-filter-btn .fav-cnt{font-size:10.5px;background:#f59e0b;color:#fff;border-radius:9px;padding:1px 6px;margin-left:2px;font-weight:700}
/* 已收藏模式：仅显示已收藏项 */
body.fav-mode .feed-item:not([data-fav="1"]){display:none !important}
body.fav-mode .ent-card:not([data-fav="1"]){display:none !important}
"""

FEEDBACK_JS = """<script>
function spKey(t,id){return 'sp_fav::'+t+'::'+id;}
function spCardOf(b){return b.closest('.feed-item, .ent-card');}
/* 收藏切换：图标变书签丝带 + 更新 data-fav + 刷新筛选计数 */
function spToggleFav(b){
  var k=spKey(b.dataset.type,b.dataset.id);
  var on=localStorage.getItem(k)==='1';on=!on;
  localStorage.setItem(k,on?'1':'0');
  b.classList.toggle('on',on);
  var ico=b.querySelector('.ico');
  if(ico) ico.textContent=on?'🔖':'☆';
  var l=b.querySelector('.lbl');if(l)l.textContent=on?'已收藏':'收藏';
  var c=spCardOf(b);if(c)c.dataset.fav=on?'1':'0';
  spRenderFavFilter();
}
function spExportFav(){
  var out=[];
  for(var i=0;i<localStorage.length;i++){
    var k=localStorage.key(i);
    if(k.indexOf('sp_fav::')===0 && localStorage.getItem(k)==='1'){
      var p=k.split('::');out.push({type:p[1],id:decodeURIComponent(p[2]),ts:new Date().toISOString()});
    }
  }
  if(!out.length){alert('还没有收藏任何选题 / 企业');return;}
  var blob=new Blob([out.map(function(o){return JSON.stringify(o);}).join('\\n')],{type:'text/plain'});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='feedback.jsonl';a.click();
}
function spFavCount(){
  var n=0;
  for(var i=0;i<localStorage.length;i++){
    var k=localStorage.key(i);
    if(k.indexOf('sp_fav::')===0 && localStorage.getItem(k)==='1') n++;
  }
  return n;
}
/* 已收藏筛选胶囊：渲染计数 + 点击切换 fav-mode */
function spRenderFavFilter(){
  var btns=document.querySelectorAll('.fav-filter-btn');
  var n=spFavCount();
  btns.forEach(function(btn){
    var cntEl=btn.querySelector('.fav-cnt');
    if(cntEl) cntEl.textContent=n;
    /* 如果在 fav-mode 但已无收藏项，自动退出 */
    if(document.body.classList.contains('fav-mode')&&n===0){
      document.body.classList.remove('fav-mode');
      btn.classList.remove('on');
    }
  });
}
function spToggleFavFilter(){
  var on=!document.body.classList.contains('fav-mode');
  document.body.classList.toggle('fav-mode',on);
  var btns=document.querySelectorAll('.fav-filter-btn');
  btns.forEach(function(b){b.classList.toggle('on',on);});
}
/* 评分色阶：根据分数加 CSS 类 */
function spScoreClass(score){
  var s=parseFloat(score)||0;
  if(s>=7) return 's-high';
  if(s>=4) return 's-mid';
  return 's-low';
}
/* GitHub 同步（同前） */
function spB64(str){return btoa(unescape(encodeURIComponent(str)));}
function spGhXhr(url,opts){
  var x=new XMLHttpRequest();x.open(opts.method||'GET',url,false);
  if(opts.headers)for(var h in opts.headers)x.setRequestHeader(h,opts.headers[h]);
  try{x.send(opts.body||null);}catch(e){return {status:0,responseText:String(e)};}
  return {status:x.status,responseText:x.responseText};
}
function spGhSettings(){
  var pat=prompt(
    '【配置 GitHub Token — 同步收藏到云端】\\n\\n'+
    '⚠️ 请粘贴完整的 Token 字符串（不是 Token 名称或描述！）\\n\\n'+
    '✅ 正确示例：github_pat_11CHI357I0s8q10l0fZxpz_iuTopkh3pzhB...（约70位）\\n'+
    '❌ 错误：fine-grained / 我的token / shuanghello153-eng/silver-pulse \\n\\n'+
    '要求：Fine-grained PAT，权限 Contents: Read and Write\\n'+
    '获取：GitHub → Settings → Developer settings → Fine-grained tokens → Generate new token',
    ''
  );
  if(!pat) return;
  pat=pat.trim();
  /* 格式校验 */
  var errs=[];
  if(pat.length<30) errs.push('太短（需≥30位）');
  if(/[\u4e00-\u9fff]/.test(pat)) errs.push('包含中文（Token 应全是英文数字）');
  if(!pat.startsWith('github_pat_')) errs.push('格式不对（应以 github_pat_ 开头）');
  if(errs.length){
    alert('❌ Token 格式错误：\\n\\n• '+errs.join('\\n• ')+'\\n\\n请从 GitHub 页面复制完整 Token（一长串字符），不是名称/描述。');
    return;
  }
  localStorage.setItem('sp_gh_pat',pat);
  localStorage.setItem('sp_gh_repo','shuanghello153-eng/silver-pulse');
  localStorage.setItem('sp_gh_branch','main');
  alert('✅ Token 已保存（仅浏览器本地）。\\n现在点「☁ 同步云端」即可上传收藏。');
}
function spGhSync(){
  var pat=localStorage.getItem('sp_gh_pat');
  if(!pat){ if(!confirm('首次同步需要配置 GitHub PAT（一次性，仅存本地）。\\n点确定开始配置。')){return;} spGhSettings(); pat=localStorage.getItem('sp_gh_pat'); if(!pat){return;} }
  var repo=localStorage.getItem('sp_gh_repo')||'shuanghello153-eng/silver-pulse';
  var branch=localStorage.getItem('sp_gh_branch')||'main';
  var lines=[];
  for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k.indexOf('sp_fav::')===0&&localStorage.getItem(k)==='1'){var p=k.split('::');lines.push(JSON.stringify({type:p[1],id:decodeURIComponent(p[2]),ts:new Date().toISOString()}));}}
  if(!lines.length){alert('还没有收藏任何内容，先去资讯看板或企业库点「🔖」吧。');return;}
  var btn=document.querySelector('.sync-fav');if(btn){btn.classList.add('syncing');btn.textContent='同步中';}
  var NL=String.fromCharCode(10);
  var content=spB64(lines.join(NL)+NL);
  var api='https://api.github.com/repos/'+repo+'/contents/data/feedback.jsonl';
  var headers={'Authorization':'Bearer '+pat,'Accept':'application/vnd.github+json'};
  var sha=null;
  try{var g=spGhXhr(api+'?ref='+branch,{method:'GET',headers:headers});if(g.status===200){try{sha=JSON.parse(g.responseText).sha;}catch(e){}}}catch(e){}
  var body=JSON.stringify({message:'sync favorites from Silver Pulse site',content:content,branch:branch});
  if(sha)body=JSON.stringify({message:'sync favorites from Silver Pulse site',content:content,sha:sha,branch:branch});
  var res=spGhXhr(api,{method:'PUT',headers:headers,body:body});
  if(btn){btn.classList.remove('syncing');btn.textContent='☁ 同步云端';}
  if(res.status===200||res.status===201){alert('✅ 已同步 '+lines.length+' 条收藏到云端！下次流水线会自动读取优化选题。');}
  else{var msg='同步失败（HTTP '+res.status+'）';try{var j=JSON.parse(res.responseText);if(j&&j.message)msg+='：'+j.message;}catch(e){}alert(msg);}
}
/* 初始化：评分色阶 + 收藏状态 + 筛选胶囊 */
function spInitFav(){
  /* 评分徽章加色阶类 */
  document.querySelectorAll('.badge-score').forEach(function(el){
    var s=el.textContent.trim();
    el.classList.add(spScoreClass(s));
  });
  /* 收藏按钮初始化 */
  document.querySelectorAll('.fav-btn').forEach(function(b){
    var k=spKey(b.dataset.type,b.dataset.id);
    var on=localStorage.getItem(k)==='1';
    if(on){
      b.classList.add('on');
      var ico=b.querySelector('.ico');if(ico)ico.textContent='🔖';
      var l=b.querySelector('.lbl');if(l)l.textContent='已收藏';
      var c=spCardOf(b);if(c)c.dataset.fav='1';
    }
    b.addEventListener('click',function(){spToggleFav(b);});
  });
  /* 导出按钮 */
  document.querySelectorAll('.export-fav').forEach(function(b){b.addEventListener('click',spExportFav);});
  /* 已收藏筛选胶囊 */
  document.querySelectorAll('.fav-filter-btn').forEach(function(b){
    b.addEventListener('click',spToggleFavFilter);
  });
  spRenderFavFilter();
}
if(document.readyState!=='loading'){spInitFav();}else{document.addEventListener('DOMContentLoaded',spInitFav);}
</script>
"""
