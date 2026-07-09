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
_NOW = datetime.now()  # 用于"近期有动态"窗口判定（与 BUILD_STAMP 同进程，偏差可忽略）

# Import from config
import sys
from ui_common import COMMON_CSS, SIDEBAR, THEME_JS, FEEDBACK_CSS, FEEDBACK_JS
sys.path.insert(0, BASE_DIR)
from config import ENTERPRISE_CATEGORIES, ENT_RV_HIGH, ENT_RV_MID, NEWS_RECENT_DAYS, SOURCES

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


_FUND_UNIT = {"b": 1000.0, "bn": 1000.0, "亿": 100.0, "m": 1.0, "mn": 1.0,
              "万": 0.01, "k": 0.001, "w": 0.01, "美元": 1.0, "元": 1.0,
              "$": 1.0, "¥": 1.0, "€": 1.0, "£": 1.0}


def _score_class(score):
    """企业研究价值分专用色阶：s-high(≥ENT_RV_HIGH) / s-mid(≥ENT_RV_MID) / s-low(<ENT_RV_MID)。
    企业分量纲 0–61，不能用资讯的 ≥7/4–6.9 阈值（否则 88% 全绿失效）。"""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return "s-low"
    if s >= ENT_RV_HIGH:
        return "s-high"
    elif s >= ENT_RV_MID:
        return "s-mid"
    return "s-low"


def _extract_fund_num(display):
    """把 '$106M' / '1.2亿' / '¥5000万' / '57B' 解析成「百万美元」量级数值（用于排序）。"""
    if not display or not isinstance(display, str):
        return 0.0
    import re
    m = re.search(r"(\d+(?:\.\d+)?)\s*([a-zA-Z¥$€£亿万千百万字]*)", display)
    if not m:
        return 0.0
    try:
        val = float(m.group(1))
    except Exception:
        return 0.0
    unit = (m.group(2) or "").lower().strip()
    # 取单位里能识别的最大量级
    mult = 1.0
    for u, f in _FUND_UNIT.items():
        if u.lower() in unit:
            mult = max(mult, f)
    # 亿/万 中文组合特殊处理
    if "亿" in unit and "万" in unit:
        mult = 100.0  # 1亿=100M 已覆盖
    return val * mult


def build_card(ent, ent_scores_map=None, news_map=None, competitors=None, news_by_entity=None, last_news_date=None):
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
            # 兜底：按企业名直接匹配 scored_latest 新闻（去重，最多 3 条）
            if not recent_news and news_by_entity:
                kname = (ent.get("name") or "").strip().lower()
                kname_cn = (ent.get("name_cn") or "").strip().lower()
                cands = news_by_entity.get(kname) or news_by_entity.get(kname_cn) or []
                seen = set()
                for n in cands:
                    u = n.get("url")
                    if u in seen:
                        continue
                    seen.add(u)
                    recent_news.append({
                        "title": n.get("title", "") or n.get("title_cn", ""),
                        "date": n.get("date", ""),
                        "url": u,
                    })
                    if len(recent_news) >= 3:
                        break

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
        header_parts.append(f'<span class="badge-rv {_score_class(rv)}">{esc(str(rv))}</span>')

    # "近期有动态"徽标：最近一次被资讯关联的时间在 NEWS_RECENT_DAYS 窗口内
    is_recent = False
    if last_news_date:
        try:
            _ld = datetime.strptime(last_news_date, "%Y-%m-%d")
            is_recent = (_NOW - _ld).days <= NEWS_RECENT_DAYS
        except (TypeError, ValueError):
            is_recent = False
    if is_recent:
        header_parts.append('<span class="ent-badge badge-recent">🔥 近期有动态</span>')
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
                rv_badge = f'<span class="badge-rv {_score_class(rv)}">{esc(str(rv))}</span>'
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

    # 融资数值（用于排序）：优先 funding_total，其次 funding_latest
    fund_val = 0.0
    has_fund = 0
    _ft = ent.get("funding_total")
    if isinstance(_ft, dict):
        _n = _extract_fund_num(_ft.get("display", ""))
        if _n:
            fund_val = _n
            has_fund = 1
    if not has_fund:
        _fl = ent.get("funding_latest")
        if isinstance(_fl, dict):
            _n = _extract_fund_num(_fl.get("display", ""))
            if _n:
                fund_val = _n
                has_fund = 1

    # 是否上市/IPO：从融资轮次、披露、描述综合判定
    def _safe_dict(x):
        return x if isinstance(x, dict) else {}
    _fl = _safe_dict(ent.get("funding_latest"))
    _ft = _safe_dict(ent.get("funding_total"))
    _desc_blob = " ".join([
        str(_fl.get("round", "")), str(_fl.get("display", "")),
        str(_ft.get("display", "")), ent.get("description", "") or "",
        ent.get("desc_cn", "") or "",
    ]).lower()
    is_ipo = 1 if any(k in _desc_blob for k in
                     ["ipo", "上市", "纳斯达克", "nasdaq", "nyse", "港股",
                      "主板", "挂牌", "公开募股", "public listing", "上市公司"]) else 0

    return (
        f'<div class="ent-card" id="{ent_anchor}" data-region="{region_attr}" '
        f'data-cat="{esc(cat_attr)}" '
        f'data-l2="{esc(cat_l2)}" '
        f'data-tags="{esc(" ".join(ent.get("tags") or []))}" '
        f'data-name="{esc(full_search)}" '
        f'data-curated="{curated_attr}" '
        f'data-serial="{esc(serial)}" '
        f'data-rv="{esc(str(rv if rv is not None else 0))}" '
        f'data-fund="{fund_val:.4f}" '
        f'data-hasfund="{has_fund}" '
        f'data-ipo="{is_ipo}" '
        f'data-recent="{1 if is_recent else 0}" '
        f'data-lastnews="{esc(last_news_date or "")}">\n'
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
            scored_list = json.load(f)
        for n in scored_list:
            u = n.get("url")
            if u:
                news_map[u] = n
    except Exception:
        news_map = {}
        scored_list = []
    # 按主体名建立索引，用于企业卡片"相关资讯"匹配
    news_by_entity = {}
    for n in scored_list:
        en = (n.get("entity_name") or "").strip().lower()
        if en:
            news_by_entity.setdefault(en, []).append(n)

    # === "近期有动态"：为企业计算最近一次被资讯关联的时间 last_news_date ===
    # 来源优先级（取最大日期）：
    #   1) 企业自身 news_coverage.latest_news 的各条日期
    #   2) enterprise_scores[serial].last_event_date（未来管道填充）
    #   3) scored_latest 按 entity_name 精确匹配（当前数据 entity_name 多为空）
    #   4) 兜底：企业名（name/name_cn）在资讯标题子串匹配（带噪音词黑名单，
    #      排除"英国/美国/融资"等泛词，且排除与信源同名误命中），仅补充少量命中。
    _src_names = set((s.get("name") or "").strip().lower() for s in SOURCES.values())
    _NOISE_TOKENS = {"英国", "美国", "中国", "广东", "全国", "全球", "行业",
                     "融资", "上市", "公司", "企业", "集团", "地区", "城市", "香港"}

    def _pdate(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except (TypeError, ValueError):
            return None

    # 预构建企业名变体（小写），用于标题子串兜底匹配
    _name_variants = []
    for e in enterprises:
        _name_variants.append((
            e.get("serial", ""),
            (e.get("name") or "").strip().lower(),
            (e.get("name_cn") or "").strip().lower(),
        ))
    _fallback_date = {}  # serial -> date（标题子串兜底命中）
    for n in scored_list:
        _title = ((n.get("title") or "") + " " + (n.get("title_cn") or "")).lower()
        _nd = _pdate(n.get("date"))
        if not _nd:
            continue
        for _serial, _nm, _nmc in _name_variants:
            _hit = False
            if _nmc and len(_nmc) >= 2 and _nmc in _title and _nmc not in _NOISE_TOKENS:
                _hit = True
            elif _nm and len(_nm) >= 4 and _nm in _title and _nm not in _src_names:
                _hit = True
            if _hit:
                if _serial not in _fallback_date or _nd > _fallback_date[_serial]:
                    _fallback_date[_serial] = _nd

    last_news_map = {}
    for e in enterprises:
        _serial = e.get("serial", "")
        _ds = []
        _nc = e.get("news_coverage")
        if isinstance(_nc, dict):
            for _x in (_nc.get("latest_news") or []):
                _d = _pdate(_x.get("date"))
                if _d:
                    _ds.append(_d)
        _sc = ent_scores_map.get(_serial)
        if _sc:
            _led = _sc.get("last_event_date")
            if _led:
                _d = _pdate(_led)
                if _d:
                    _ds.append(_d)
        if _serial in _fallback_date:
            _ds.append(_fallback_date[_serial])
        if _ds:
            last_news_map[_serial] = max(_ds).strftime("%Y-%m-%d")

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
        build_card(e, ent_scores_map, news_map, competitors_map.get(e.get("serial", "")), news_by_entity, last_news_map.get(e.get("serial", "")))
        for e in enterprises_sorted
    )

    # --- 研究价值 TOP 15 不再单独成块：精选视图默认按研究价值降序，
    #     融资金额/研究价值排序通过工具栏箭头按钮实现（见 setEntSort）。---

    # Tag filter options — TOP-N high-frequency pills + collapsible "more" to avoid explosion
    from collections import Counter
    tag_counter = Counter(t for e in enterprises for t in (e.get("tags") or []) if t)
    TAG_SHOW_LIMIT = 24  # 只展示最高频的 N 个标签，其余折叠
    top_tags = [t for t, _ in tag_counter.most_common(TAG_SHOW_LIMIT)]
    more_tags = [t for t, _ in tag_counter.most_common()[TAG_SHOW_LIMIT:]]

    tag_pills_html = (
        '<button class="f-btn active" data-tag="all">全部</button>'
        '<button class="f-btn" data-tag="__funded__">有融资/IPO</button>'
        + "".join(
            f'<button class="f-btn" data-tag="{esc(t)}">{esc(t)}<span class="cnt">{tag_counter[t]}</span></button>' for t in top_tags
        )
    )
    if more_tags:
        tag_pills_html += (
            f'<button class="f-btn f-btn-more" id="ent-toggle-tags" onclick="toggleEntTags()">+{len(more_tags)}</button>'
            f'<div id="ent-more-tags" style="display:none;margin-top:6px;">'
            + "".join(
                f'<button class="f-btn" data-tag="{esc(t)}">{esc(t)}<span class="cnt">{tag_counter[t]}</span></button>' for t in more_tags
            )
            + '</div>'
        )

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
<style>__RECENT_CSS__</style>
</head>
<body>

__SIDEBAR__
<div class="main">

<!-- 顶部工具条（不常用按钮集中在此） -->
<div class="top-tools" id="top-tools">
  <button class="sync-fav" title="同步收藏到云端仓库（首次需配置Token）" onclick="spGhSync()">☁ 同步云端</button>
  <button class="sync-set" title="配置 GitHub Token" onclick="spGhSettings()">⚙ 设置</button>
</div>

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
    <span class="f-label" style="margin-left:12px;">排序</span>
    <button class="sort-arrow active" data-sort="rv" onclick="setEntSort('rv')">评分 ↓</button>
    <button class="sort-arrow" data-sort="fund" onclick="setEntSort('fund')">融资金额 ↓</button>
    <input type="text" class="search-inline" id="search" placeholder="搜索企业名称/描述/标签..." oninput="filterEnt()">
    <button class="recent-filter-btn" onclick="spToggleRecentFilter()" title="只看近期有资讯动态的企业（按最近动态时间倒序）">🔥 近期有动态</button>
    <button class="fav-filter-btn" onclick="spToggleFavFilter()" title="只看已收藏">🔖 已收藏<span class="fav-cnt">0</span></button>
  </div>
  <div class="filter-row" id="cat-filter">
    <span class="f-label">分类</span>
    <button class="f-btn active" data-cat="all">全部</button>
    {cat_buttons}
  </div>
  <div class="filter-row">
    <span class="f-label">标签</span>
    <div class="filter-btns ent-tag-pills">{tag_pills_html}</div>
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
let activeTag = 'all';
let entSortMode = 'rv';
let entSortDir = 'desc';
let activeRecent = false;

function setEntSort(mode) {{
  if (entSortMode === mode) {{
    entSortDir = entSortDir === 'desc' ? 'asc' : 'desc';
  }} else {{
    entSortMode = mode;
    entSortDir = 'desc';
  }}
  document.querySelectorAll('.sort-arrow[data-sort]').forEach(function(b) {{
    const m = b.dataset.sort;
    b.classList.toggle('active', m === entSortMode);
    const arrow = (m === entSortMode) ? (entSortDir === 'desc' ? '↓' : '↑') : '↓';
    b.textContent = (m === 'rv' ? '评分 ' : '融资金额 ') + arrow;
  }});
  filterEnt();
}}

function sortEnt() {{
  const mode = entSortMode;
  const list = document.getElementById('ent-list');
  if (!list) return;
  const cards = Array.from(list.querySelectorAll('.ent-card'));
  if (activeRecent) {{
    // 聚焦近期：按最近动态时间倒序（无日期的排末尾）
    cards.sort(function(a, b) {{
      const da = a.dataset.lastnews || '';
      const db = b.dataset.lastnews || '';
      if (da && db) return db.localeCompare(da);
      if (da) return -1;
      if (db) return 1;
      return 0;
    }});
    cards.forEach(function(c) {{ list.appendChild(c); }});
    return;
  }}
  cards.sort(function(a, b) {{
    let cmp;
    if (mode === 'fund') {{
      cmp = (parseFloat(b.dataset.fund) || 0) - (parseFloat(a.dataset.fund) || 0);
    }} else {{
      cmp = (parseFloat(b.dataset.rv) || 0) - (parseFloat(a.dataset.rv) || 0);
    }}
    if (entSortDir === 'asc') cmp = -cmp;
    return cmp;
  }});
  cards.forEach(function(c) {{ list.appendChild(c); }});
}}

function spToggleRecentFilter() {{
  activeRecent = !activeRecent;
  const btn = document.querySelector('.recent-filter-btn');
  if (btn) btn.classList.toggle('active', activeRecent);
  filterEnt();
}}

function filterEnt() {{
  sortEnt();
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
    const tag = (card.dataset.tags || '').split(' ').filter(Boolean);
    const tagMatch = activeTag === 'all' || (activeTag === '__funded__' ? (card.dataset.hasfund === '1') : tag.includes(activeTag));
    const recentMatch = !activeRecent || card.dataset.recent === '1';

    if (regMatch && searchMatch && viewMatch && tagMatch && recentMatch) {{
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
    const tagLabel = activeTag === 'all' ? '' : ' · ' + (activeTag === '__funded__' ? '有融资/IPO' : activeTag);
    const recentLabel = activeRecent ? ' · 近期有动态' : '';
    rc.textContent = `展示 ${{visible}} 家企业 · ${{viewLabel}} · ${{regLabel}} · ${{catLabel}}${{l2Label}}${{tagLabel}}${{recentLabel}}`;
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

// Sort toggle is handled via onclick="setEntSort(...)" arrow buttons (see toolbar)

// Tag pill toggle (replaces old <select>)
document.querySelectorAll('.ent-tag-pills [data-tag]').forEach(btn => {{
  btn.addEventListener('click', function() {{
    document.querySelectorAll('.ent-tag-pills [data-tag]').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    activeTag = this.dataset.tag;
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

function toggleEntTags() {{
  const box = document.getElementById('ent-more-tags');
  const btn = document.getElementById('ent-toggle-tags');
  if (!box || !btn) return;
  if (box.style.display === 'none') {{
    box.style.display = '';
    btn.textContent = '收起 ▲';
    btn.classList.add('active');
  }} else {{
    box.style.display = 'none';
    const n = box.querySelectorAll('.f-btn').length;
    btn.textContent = '+' + n;
    btn.classList.remove('active');
  }}
}}
</script>
</body>
</html>"""

    html_content = html_content.replace("__COMMON_CSS__", COMMON_CSS + FEEDBACK_CSS).replace("__SIDEBAR__", SIDEBAR("enterprise"))

    RECENT_CSS = """
/* 近期有动态徽标 + 筛选按钮 */
.ent-badge.badge-recent { background:#fff1e6; color:#e8590c; border:1px solid #ffd8a8; font-weight:600; white-space:nowrap; }
.recent-filter-btn { margin-left:10px; padding:5px 12px; border:1px solid var(--line,#e3e3e8); border-radius:999px; background:#fff; color:#555; cursor:pointer; font-size:13px; transition:.15s; }
.recent-filter-btn:hover { border-color:#ffa94d; }
.recent-filter-btn.active { background:#e8590c; color:#fff; border-color:#e8590c; }
"""
    html_content = html_content.replace("__RECENT_CSS__", RECENT_CSS)
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
