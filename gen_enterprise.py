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
- 精选/全量切换 (curated = 研究分 rv >= ENT_RV_MID 的高分优质企业；与资讯"精选=高分"统一规则)
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
from ui_common import sp_card_actions, sp_note_placeholder
sys.path.insert(0, BASE_DIR)
from config import ENTERPRISE_CATEGORIES, ENT_RV_HIGH, ENT_RV_MID, NEWS_RECENT_DAYS, SOURCES

# 13 L1 categories (no numbering in display)
L1_CATS = list(ENTERPRISE_CATEGORIES.keys())

# 13 L1 categories (no numbering in display)
L1_CATS = list(ENTERPRISE_CATEGORIES.keys())

# 模块级缓存：generate() 内填充企业研究分，供 is_curated 统一按分数阈值判定。
_ENT_SCORES = {}

# 事件簇对照：cluster_id -> 同事件其他来源链接（module-level，generate 内填充）
CLUSTER_SOURCES = {}


def load_enterprises():
    path = os.path.join(DATA_DIR, "enterprise/all_enterprises.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def esc(text):
    """HTML escape"""
    if not text:
        return ""
    return html.escape(str(text))


def is_curated(ent, rv=None):
    """Determine if an enterprise is 'curated' (精选).

    与资讯页统一规则：精选 = 高分优质，按各自分数阈值切分。
    企业库以「研究分」(research_value, 0–100) 为阈值，
    rv >= ENT_RV_MID（约前 50% 高分企业）即入选精选。
    rv 由调用方传入（build_card 内已算好），缺省时从 _ENT_SCORES 缓存读取，
    再缺省回退到 ent 自身 value_score。
    """
    if rv is None:
        sc = _ENT_SCORES.get(ent.get("serial", "")) if ent.get("serial") else None
        rv = (sc or {}).get("research_value")
    if rv is None:
        rv = ent.get("value_score") or 0
    try:
        rv = float(rv)
    except (TypeError, ValueError):
        rv = 0.0
    return rv >= ENT_RV_MID


_FUND_UNIT = {"b": 1000.0, "bn": 1000.0, "亿": 100.0, "m": 1.0, "mn": 1.0,
              "万": 0.01, "k": 0.001, "w": 0.01, "美元": 1.0, "元": 1.0,
              "$": 1.0, "¥": 1.0, "€": 1.0, "£": 1.0}


def _score_class(score):
    """企业研究分专用色阶：s-high(≥ENT_RV_HIGH) / s-mid(≥ENT_RV_MID) / s-low(<ENT_RV_MID)。
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


def build_card(ent, ent_scores_map=None, news_map=None, competitors=None, news_by_entity=None, last_news_date=None, news_count=0):
    """Build a compact horizontal card for one enterprise.
    All fields directly visible, empty fields hidden."""
    name = esc(ent.get("name", ""))
    region = ent.get("region", "")
    cat_l1 = esc(ent.get("category_l1", ""))
    cat_l2 = esc(ent.get("category_l2", ""))
    tags = ent.get("tag_l2") or ent.get("tags") or []
    tag_l1 = ent.get("tag_l1") or []
    description = esc(ent.get("description", ""))
    highlights = esc(ent.get("highlights", ""))
    business_model = esc(ent.get("business_model", ""))
    biz_tags = ent.get("business_tags") or {}
    stage = ent.get("stage", "")
    recommend = esc(ent.get("recommend", ""))

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
                        _u = n.get("url", "")
                        recent_news.append({
                            "title": n.get("title_cn") or n.get("title", ""),
                            "date": n.get("date", ""),
                            "url": _u,
                            "sources": CLUSTER_SOURCES.get(_u, []),
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
                        "title": n.get("title_cn") or n.get("title", ""),
                        "date": n.get("date", ""),
                        "url": u,
                        "sources": CLUSTER_SOURCES.get(u, []),
                    })
                    if len(recent_news) >= 3:
                        break

    # === 关联动态角色判定：区分"被报道主体(subject)"与"发布方(publisher)" ===
    # 媒体类企业(行业媒体)作为发布方出现的新闻，不应算作"自身动态"；
    # 非媒体企业作为发布方的新闻亦排除出"近期动态"，仅保留真正关于它的新闻。
    _ent_n_low = (ent.get("name") or "").strip().lower()
    _ent_nc_low = (ent.get("name_cn") or "").strip().lower()
    is_media = (cat_l2 == "行业媒体") or ("行业媒体" in (tags or []))
    def _news_role(n):
        _src = (n.get("source") or "").strip().lower()
        _en = (n.get("entity_name") or "").strip().lower()
        if _ent_n_low and _src and _src == _ent_n_low:
            return "publisher"
        if _ent_nc_low and _src and _src == _ent_nc_low:
            return "publisher"
        return "subject"
    _subj_news = [x for x in recent_news if _news_role(x) == "subject"]
    _pub_news = [x for x in recent_news if _news_role(x) == "publisher"]
    if is_media:
        _show_news = (_subj_news + _pub_news)[:3]
        _recent_label = "📰 近期报道" if _show_news else None
    else:
        _show_news = _subj_news[:3]
        _recent_label = "🔥 近期动态" if _show_news else None

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
    curated = is_curated(ent, rv)

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

    # 一级标签 tag_l1（行业大类，与 tag_l2 是两个独立字段，描边灰底区分）
    if tag_l1 and isinstance(tag_l1, list):
        l1_html = "".join(
            f'<span class="ent-tag-l1">{esc(t)}</span>' for t in tag_l1 if t
        )
        if l1_html:
            header_parts.append(f'<span class="ent-tags-l1">{l1_html}</span>')

    # Tags (展示全量 tag_l2，不限制数量)
    if tags and isinstance(tags, list):
        visible_tags = [t for t in tags if t]
        if visible_tags:
            tags_html = "".join(
                f'<span class="ent-tag">{esc(t)}</span>' for t in visible_tags
            )
            header_parts.append(f'<span class="ent-tags">{tags_html}</span>')

    # Business tags (业务标签: 客户对象/角色/渠道) — 新维度, 暂停原始 business_model 展示
    if biz_tags:
        _bt = []
        _cust = biz_tags.get("customer")
        if _cust and _cust != "未标注":
            _bt.append(f'<span class="ent-biz-tag biz-customer">{esc(_cust)}</span>')
        _role = biz_tags.get("role")
        if _role:
            _bt.append(f'<span class="ent-biz-tag biz-role">{esc(_role)}</span>')
        for _ch in (biz_tags.get("channel") or []):
            _bt.append(f'<span class="ent-biz-tag biz-channel">{esc(_ch)}</span>')
        if _bt:
            header_parts.append(f'<span class="ent-biz-tags">{" ".join(_bt)}</span>')

    # Region (低调，放最后)
    if region:
        header_parts.append(f'<span class="ent-badge badge-region">{esc(region)}</span>')

    # Stage badge (阶段)
    if stage:
        header_parts.append(f'<span class="ent-badge badge-stage">阶段·{esc(stage)}</span>')

    # Research-value badge — 加"研究分"标签 + hover 解释（避免裸数字看不懂）
    if rv is not None:
        header_parts.append(f'<span class="badge-rv {_score_class(rv)}" title="研究价值分：综合规模/信息密度/商业模式/国内可比性打分（0-100），越高越值得深写">研究分 {esc(str(rv))}</span>')

    # "近期有动态"徽标：仅当企业是新闻的"被报道主体(subject)"且近期有动态才显示；
    # 媒体类企业(行业媒体)即使发布了大量资讯，也不标"近期有动态"（改用"近期报道"）。
    is_recent = False
    if not is_media:
        _rdates = []
        for _x in _subj_news:
            try:
                _rdates.append(datetime.strptime(_x.get("date", ""), "%Y-%m-%d"))
            except (TypeError, ValueError):
                pass
        if _rdates:
            _ld = max(_rdates)
            is_recent = (_NOW - _ld).days <= NEWS_RECENT_DAYS
    if is_recent:
        header_parts.append('<span class="ent-badge badge-recent">🔥 近期有动态</span>')
    # 收藏按钮（localStorage 反馈）
    if serial:
        header_parts.append(f'<button class="fav-btn" data-type="ent" data-id="{esc(serial)}"><span class="ico">☆</span><span class="lbl">收藏</span></button>')
        # 列表内操作：不再显示 / 备注 / 已读（A8：企业库也支持已读未读）
        header_parts.append(sp_card_actions("ent", esc(serial), with_read=True))

    parts.append(f'<div class="ent-header">{" ".join(header_parts)}</div>')

    # Description line
    if description:
        parts.append(f'<div class="ent-desc">{description}</div>')

    # Highlights (小字)
    if highlights:
        parts.append(f'<div class="ent-highlights">★ {highlights}</div>')

    # Recommend (推荐理由: 规则占位版, 待 AI 精修)
    if recommend:
        parts.append(f'<div class="ent-reco">💡 推荐理由: {recommend}</div>')

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

    # Business model: 已暂停原始 business_model 展示(改由上方业务标签 chips 替代)

    # Source
    if source:
        meta_parts.append(f'<span class="meta-item meta-source">{source}</span>')

    # Links (small, right-aligned) — 点击复制链接，停留在当前列表页（不开新标签）
    link_parts = []
    if crunchbase_url:
        link_parts.append(f'<a href="{esc(crunchbase_url)}" class="ent-link" onclick="return spCopyLink(event,\'{esc(crunchbase_url)}\',\'Crunchbase\')" title="点击复制链接（原地不动）">Crunchbase</a>')
    if website_url:
        link_parts.append(f'<a href="{esc(website_url)}" class="ent-link" onclick="return spCopyLink(event,\'{esc(website_url)}\',\'官网\')" title="点击复制链接（原地不动）">官网</a>')
    if link_parts:
        meta_parts.append(f'<span class="meta-links">{" · ".join(link_parts)}</span>')

    if meta_parts:
        parts.append(f'<div class="ent-meta">{" ".join(meta_parts)}</div>')

    # 近期动态 / 近期报道 — related news (Phase 2), omitted if none.
    # 媒体企业显示"近期报道"（其发布的新闻），非媒体显示"近期动态"（关于它的新闻）。
    if _show_news:
        rec_items = []
        for rn in _show_news:
            if rn["url"]:
                link = "index.html#news-" + _url_hash(rn["url"])
            else:
                link = "index.html"
            t = esc(rn["title"])
            d = f' <span class="ent-recent-date">({esc(rn["date"])})</span>' if rn["date"] else ""
            # 同事件多来源对照（事件簇对照卡：直接附多个渠道链接，点击跳转）
            src_html = ""
            srcs = rn.get("sources") or []
            if srcs:
                src_links = " · ".join(
                    f'<a href="{esc(s["url"])}" target="_blank" rel="noopener" class="ent-src-link">{esc(s["source"] or "来源")}</a>'
                    for s in srcs if s.get("url")
                )
                src_html = f' <span class="ent-cluster-srcs">〔同事件：{src_links}〕</span>'
            rec_items.append(
                f'<a href="{esc(link)}" class="ent-recent-link">{t}</a>{d}{src_html}'
            )
        parts.append(f'<div class="ent-recent">{esc(_recent_label or "🔥 近期动态")}: {" · ".join(rec_items)}</div>')

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

    # 卡片底部备注占位（点击编辑，仅存本机）
    if serial:
        parts.append(sp_note_placeholder("ent", esc(serial)))

    # Data attributes for filtering
    search_text = (ent.get("name", "") or "").lower()
    # Also include description and tags in search data
    desc_lower = (ent.get("description", "") or "").lower()
    tags_lower = " ".join((t or "").lower() for t in tags) if isinstance(tags, list) else ""
    # Enhanced: include L1/L2 category + business_model so search is broader
    cat_lower = (cat_l1 or "").lower()
    l2_lower = (cat_l2 or "").lower()
    bm_lower = (business_model or "").lower()
    _biz_search = " ".join([str(biz_tags.get("customer", "")), str(biz_tags.get("role", "")),
                             " ".join(biz_tags.get("channel") or [])]).lower()
    full_search = f"{search_text} {desc_lower} {tags_lower} {cat_lower} {l2_lower} {bm_lower} {_biz_search} {stage} {recommend}"
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
        f'<div class="ent-card" id="{ent_anchor}" data-card-id="{esc(serial)}" data-region="{region_attr}" '
        f'data-cat="{esc(cat_attr)}" '
        f'data-l2="{esc(cat_l2)}" '
        f'data-tags="{esc(" ".join(ent.get("tag_l2") or ent.get("tags") or []))}" '
        f'data-name="{esc(full_search)}" '
        f'data-search="{esc(" ".join([full_search, description, highlights, " ".join(tags), " ".join(tag_l1)]).lower())}" '
        f'data-curated="{curated_attr}" '
        f'data-serial="{esc(serial)}" '
        f'data-rv="{esc(str(rv if rv is not None else 0))}" '
        f'data-news="{news_count}" '
        f'data-fund="{fund_val:.4f}" '
        f'data-hasfund="{has_fund}" '
        f'data-ipo="{is_ipo}" '
        f'data-recent="{1 if is_recent else 0}" '
        f'data-lastnews="{esc(last_news_date or "")}">\n'
        + "\n".join(parts) + "\n"
        + '</div>'
    )


def _fold_label(n):
    """格式化折叠数字：>=100取整百，>=20取整十，否则原样。"""
    if n >= 100:
        return f"~{n//100*100}+"
    elif n >= 20:
        return f"~{n//10*10}+"
    return f"+{n}"


def generate():
    enterprises = load_enterprises()

    # 同类词表（canonical 二级标签 -> 同义词/别名），用于搜索扩展
    # 与 _build_tags.py / _gen_scheme_doc.py 的 SYN 保持一致（单一事实来源见那两处）
    # 同义词表（canonical 二级标签 -> 同义词/别名），用于搜索扩展
    # 精简原则（2026-07-11 优化）：
    #  1) 删掉「老年/银发」前缀（如 老年文娱->文娱，已可被 文娱社交 子串命中）
    #  2) 删掉「可被二级标签子串命中」的冗余词（护理/资本/营养/食品/居家/机器人/AI/硬件 等）
    #  3) 删掉「复合概念」同义词（高科技眼镜/AI健康/失禁护理/适老硬件/虚拟临终关怀/神经退行性疾病），
    #     其组成零件本就是二级标签、子串即可命中；拆到最细 -> 命中率更高 -> 同类词更少
    #  4) 生僻词用常见词替代（神经退行性疾病->神经退化；适老->适老化已并入 适老化改造）
    SYNONYMS = {
        '眼镜': ['老花镜', '老花眼', '视觉障碍'],
        '产业资本': ['医疗REIT', '科技巨头', '行业巨头', '相关上市公司', '消费背景', '严肃医疗背景', '国资背景', '种子投资背景', '对标标的', '政府支持'],
        '女性健康': ['更年期'],
        '营养食品': ['膳食'],
        'AI科技': ['具身智能', '脑机接口', '神经科技'],
        '数字化': ['智慧养老软件'],
        '助听器': ['听力训练', '听觉障碍', '听力评估'],
        '辅具': ['辅助设备', '轮椅', '外骨骼', '肢体障碍', '无障碍'],
        '专业护理': ['尿失禁', '吞咽障碍', '咀嚼障碍', '呼吸障碍'],
        '临终关怀': ['姑息治疗', '安宁疗护', '殡葬服务'],
        '养老社区': ['养老地产', '养老院中介', '养老住宅', '租房', '运营商', 'PACE计划', '会员制'],
        '养老机构': ['养老院', '护理院', '养护院', '托老院', '敬老院', '机构养老'],
        '鞋服': ['服装', '鞋子', '老年鞋', '老年服饰'],
        '个护': ['护肤', '染发剂', '假发'],
        '健康管理': ['综合医疗', '初级保健', '微型诊所', '医疗服务商', '医疗编码', '疾病预测', '服药管理', '物理治疗', '肌肉骨骼护理', '诊所', '医保', '处方药', '中医'],
        'SODH': ['社会决定因素', '社会护理网络', '健康社会因素', '支持性护理'],
        '慢病管理': ['糖尿病'],
        '认知症': ['痴呆症', '神经退化', '阿尔茨海默', '病情早筛', '音乐疗法', '回忆疗法'],
        '行业媒体': ['B2C媒体'],
        '咨询研究': ['行业展会', '护工培训', '医疗人员培训'],
        '旅游': ['旅居养老', '跨境养老', '无障碍旅游'],
        '教育': ['再就业', '就业', '老年大学', '老年教育', '老年学校'],
        '保险': ['医疗保险', '保险科技', '保险经纪', 'Medicare Advantage'],
        '养老金融': ['养老金', '退休理财', '退休规划'],
        '保健品': ['中式养生', '益生菌', '小分子肽', '蛋白粉', '无糖&低GI', '成人羊奶'],
        '特医食品': ['吞咽困难'],
        '适老化改造': ['住宅改造', '综合供应链'],
        '康复': ['精神&神经'],
        '家政助老': ['传统家政', '民政服务', '助餐', '助浴助洁', '家政服务'],
        '远程医疗': ['远程监控', '远程营养', '上门医疗', '医养结合', '虚拟'],
        '健康监测': ['血压血糖', '跌倒检测', '步态检测', '咳嗽检测', '防跌倒', '紧急呼叫', '医疗警报'],
        '精神健康': ['心理咨询', '抑郁'],
        '渠道': ['线上渠道', '线下渠道', '电视购物', '会员营销', '私域渠道', '特殊渠道', '代工厂'],
        '文娱社交': ['老年社交', '社交平台', '兴趣社群', '短视频', '直播'],
        '相亲': ['婚恋', '老年相亲', '老人相亲', '银发相亲', '老年婚恋', '交友'],
        '护理平台': ['寻找护理', '护理员支持', '护理匹配', '护理协调', '护理管理'],
        '陪伴机器人': ['仿生陪伴', 'AI机器宠物', 'AI伴侣', '虚拟陪伴', '社交机器人'],
        '机器人': ['养老机器人', '康复机器人', '医疗机器人', '服务机器人', '人形机器人'],
    }
    # 反向展开：每个词(含同义词与规范词) -> 规范词；以及 规范词 -> 全部可匹配词
    SYN_FLAT = {}
    CANON_SYN = {}
    for canon, syns in SYNONYMS.items():
        CANON_SYN[canon] = [canon] + list(syns)
        for t in [canon] + list(syns):
            SYN_FLAT[t] = canon
    syn_js = ("const SYN_FLAT = " + json.dumps(SYN_FLAT, ensure_ascii=False) +
              ";\nconst CANON_SYN = " + json.dumps(CANON_SYN, ensure_ascii=False) + ";")

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
    # 同步到模块级缓存，供 is_curated 按研究分阈值统一判定精选
    _ENT_SCORES.clear()
    _ENT_SCORES.update(ent_scores_map)

    # 事件簇对照：按 cluster_id 聚合，记录每条新闻的"同事件其他来源"
    CLUSTER_SOURCES.clear()
    _cluster_map = {}
    for _n in scored_list:
        _cid = _n.get("cluster_id")
        if _cid:
            _cluster_map.setdefault(_cid, []).append(_n)
    for _cid, _grp in _cluster_map.items():
        if len(_grp) <= 1:
            continue
        for _n in _grp:
            _u = _n.get("url")
            if not _u:
                continue
            _others = [
                {"source": _o.get("source", ""),
                 "title": _o.get("title", "") or _o.get("title_cn", ""),
                 "url": _o.get("url", "")}
                for _o in _grp if _o.get("url") and _o.get("url") != _u
            ]
            if _others:
                CLUSTER_SOURCES[_u] = _others

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
    _ent_by_serial = {e.get("serial"): e for e in enterprises}
    def _is_media_ent(e):
        if not e:
            return False
        return (e.get("category_l2") == "行业媒体") or ("行业媒体" in (e.get("tags") or []))
    _fallback_date = {}  # serial -> date（标题子串兜底命中）
    _fallback_count = {}  # serial -> 兜底匹配到的资讯条数
    for n in scored_list:
        _title = ((n.get("title") or "") + " " + (n.get("title_cn") or "")).lower()
        _nd = _pdate(n.get("date"))
        if not _nd:
            continue
        _nsrc = (n.get("source") or "").strip().lower()
        for _serial, _nm, _nmc in _name_variants:
            _hit = False
            if _nmc and len(_nmc) >= 2 and _nmc in _title and _nmc not in _NOISE_TOKENS:
                _hit = True
            elif _nm and len(_nm) >= 4 and _nm in _title and _nm not in _src_names:
                _hit = True
            if _hit:
                # 媒体企业：作为发布方出现在新闻里，不应标"自身动态"
                if _is_media_ent(_ent_by_serial.get(_serial)):
                    continue
                # 仅作为发布方（信源==企业名）：不算企业自身动态
                if _nsrc and (_nsrc == _nm or _nsrc == _nmc):
                    continue
                if _serial not in _fallback_date or _nd > _fallback_date[_serial]:
                    _fallback_date[_serial] = _nd
                _fallback_count[_serial] = _fallback_count.get(_serial, 0) + 1

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

    # === 匹配到的资讯文章数量（用于默认排序主键）===
    # 来源：enterprise_scores 的 related_news_ids（管道权威匹配）+ 标题子串兜底命中数
    news_count_map = {}
    for _serial, _sc in ent_scores_map.items():
        if not isinstance(_sc, dict):
            continue
        _rids = _sc.get("related_news_ids") or []
        news_count_map[_serial] = len(_rids)
    for _serial, _c in _fallback_count.items():
        news_count_map[_serial] = news_count_map.get(_serial, 0) + _c

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
                for rv, o in cands[:3]
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
        build_card(e, ent_scores_map, news_map, competitors_map.get(e.get("serial", "")), news_by_entity, last_news_map.get(e.get("serial", "")), news_count_map.get(e.get("serial", ""), 0))
        for e in enterprises_sorted
    )

    # --- 研究价值 TOP 15 不再单独成块：精选视图默认按研究价值降序，
    #     融资金额/研究价值排序通过工具栏箭头按钮实现（见 setEntSort）。---

    # Tag filter options — 全展示不折叠
    from collections import Counter
    tag_counter = Counter(t for e in enterprises for t in (e.get("tag_l2") or e.get("tags") or []) if t)
    TAG_SHOW_LIMIT = 12  # 筛选栏展示最高频的 N 个标签，其余折叠（避免全屏爆炸）
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
            f'<button class="f-btn f-btn-more" id="ent-toggle-tags" onclick="toggleEntTags()">{_fold_label(len(more_tags))}</button>'
            f'<div id="ent-more-tags" style="display:none;margin-top:6px" class="ent-more-tags-wrap">'
            + "".join(
                f'<button class="f-btn" data-tag="{esc(t)}">{esc(t)}<span class="cnt">{tag_counter[t]}</span></button>' for t in more_tags
            )
            + '</div>'
        )

    # L1 filter buttons — 全部展示不折叠，点击展开L2子类
    sorted_l1 = sorted(L1_CATS, key=lambda c: cat_counts.get(c, 0), reverse=True)

    cat_buttons = (
        '<button class="f-btn active" data-cat="all">全部</button>'
        + "".join(
            f'<button class="f-btn" data-cat="{esc(l1)}" onclick="toggleL2Cat(\'{esc(l1)}\')">{esc(l1)}<span class="cnt">{cat_counts.get(l1, 0)}</span></button>'
            for l1 in sorted_l1
        )
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

<div class="header">
  <h2>银发经济企业数据库</h2>
  <p class="header-stats">共 {total} 家企业 · 国内 {domestic} 家 · 海外 {overseas} 家 · 精选 {curated_count} 家 · {len(L1_CATS)} 个一级分类</p>
</div>

<div class="toolbar">
  <!-- 第1行：视图 / 地区 / 排序 / 搜索(内联, 输入框缩短, 按钮常驻) -->
  <div class="filter-row filter-main">
    <span class="f-label">视图</span>
    <div class="view-toggle">
      <button class="view-btn active" data-view="curated">精选 ({curated_count})</button>
      <button class="view-btn" data-view="all">全量 ({total})</button>
    </div>
    <span class="f-label">地区</span>
    <div class="btn-group">
      <button class="f-btn active" data-reg="all">全部</button>
      <button class="f-btn" data-reg="1">国内</button>
      <button class="f-btn" data-reg="2">海外</button>
    </div>
    <span class="f-label">排序</span>
    <div class="sort-group">
      <button class="sort-arrow active" data-sort="news" onclick="setEntSort('news')">资讯相关</button>
      <button class="sort-arrow" data-sort="rv" onclick="setEntSort('rv')">研究分</button>
      <button class="sort-arrow" data-sort="fund" onclick="setEntSort('fund')">融资金额</button>
    </div>
    <span class="f-label">搜索</span>
    <div class="search-inline-group">
      <input type="text" class="search-inline" id="search" placeholder="老年鞋/响午/SODH/相亲" onkeydown="if(event.key==='Enter'){{filterEnt();}}">
      <button type="button" class="search-btn" onclick="filterEnt()">搜索</button>
    </div>
  </div>

  <!-- 第2行：分类（L1全展示，点击展开L2子类） -->
  <div class="filter-row" id="cat-filter">
    <span class="f-label">分类</span>
    <div class="filter-btns">{cat_buttons}</div>
  </div>
  {l2_filter_html}

  <!-- 第3行：标签（全展示不折叠） -->
  <div class="filter-row">
    <span class="f-label">标签</span>
    <div class="filter-btns ent-tag-pills">{tag_pills_html}</div>
  </div>

  <!-- 第4行：时间[左] + 辅助按钮[右] -->
  <div class="filter-row filter-last">
    <span class="f-label">时间</span>
    <div class="filter-btns" id="ent-time-pills">
      <button class="f-btn active" data-enttime="all">全部</button>
      <button class="f-btn" data-enttime="1w">近1周</button>
      <button class="f-btn" data-enttime="2w">近2周</button>
      <button class="f-btn" data-enttime="1m">近1月</button>
      <button class="f-btn" data-enttime="3m">近3月</button>
    </div>
    <div class="aux-group">
      <button class="recent-filter-btn" onclick="spToggleRecentFilter()" title="只看近期有资讯动态的企业">🔥 近期动态</button>
      <button class="fav-filter-btn" title="只看已收藏">🔖 已收藏<span class="fav-cnt">0</span></button>
      <button class="toolbar-filter-btn" id="unread-toggle" title="只看未读企业">👁 未读</button>
      <button class="toolbar-filter-btn" id="hide-toggle" title="显示被隐藏的企业">🙈 已隐藏</button>
    </div>
  </div>

  <!-- 收藏标签筛选条（仅 fav-mode 下显示） -->
  <div class="filter-row fav-tag-filter" id="fav-tag-filter" style="display:none;">
    <span class="f-label">收藏标签</span>
    <div class="filter-btns" id="fav-tag-pills"></div>
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
let activeL2 = 'all';
let activeView = 'curated';
let activeTag = 'all';
let entSortMode = 'news';
let entSortDir = 'desc';
let activeRecent = false;
let activeEntTime = 'all';
window.spReapply = filterEnt;

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
    b.textContent = (m === 'news' ? '匹配资讯 ' : (m === 'rv' ? '评分 ' : '融资金额 ')) + arrow;
  }});
  filterEnt();
}}

function sortEnt() {{
  const mode = entSortMode;
  const list = document.getElementById('ent-list');
  if (!list) return;
  const cards = Array.from(list.querySelectorAll('.ent-card'));
  if (mode === 'news') {{
    // 默认排序：主键=匹配到的资讯文章数量降序；次键=近期有动态的企业上浮；再次=研究价值降序
    cards.sort(function(a, b) {{
      const ca = parseInt(a.dataset.news || '0', 10);
      const cb = parseInt(b.dataset.news || '0', 10);
      let cmp = cb - ca;
      if (cmp === 0) {{
        cmp = (b.dataset.recent === '1' ? 1 : 0) - (a.dataset.recent === '1' ? 1 : 0);
      }}
      if (cmp === 0) {{
        cmp = (parseFloat(b.dataset.rv) || 0) - (parseFloat(a.dataset.rv) || 0);
      }}
      return cmp;
    }});
    cards.forEach(function(c) {{ list.appendChild(c); }});
    return;
  }}
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
  const qRaw = (document.getElementById('search').value || '').trim().toLowerCase();
  const q = qRaw;
  // 同类词扩展：把搜索词扩展到其规范词及全部同义词（如 老花镜→眼镜+视觉障碍+高科技眼镜…）
  let qTerms = q ? [q] : [];
  if (q && typeof SYN_FLAT !== 'undefined' && SYN_FLAT[q]) {{
    const canon = SYN_FLAT[q];
    if (CANON_SYN[canon]) qTerms = qTerms.concat(CANON_SYN[canon].map(function(t){{ return t.toLowerCase(); }}));
  }}
  const cards = Array.from(document.querySelectorAll('.ent-card'));
  let visible = 0;
  const catVisCounts = {{}};
  const l2VisCounts = {{}};
  const matched = [];

  cards.forEach(card => {{
    const reg = card.dataset.region;
    const cat = card.dataset.cat;
    const l2 = card.dataset.l2 || '';
    const curated = card.dataset.curated === '1';

    // 搜索打分：3=标签精确命中(含扩展同义词) 2=标签子串命中(最小颗粒度, 如 护理⊂专业护理/硬件⊂智能硬件) 1=仅在名称/描述/推荐理由 0=不命中
    let score = 0;
    if (q) {{
      const tags = (card.dataset.tags || '').split(' ').filter(Boolean).map(function(t){{ return t.toLowerCase(); }});
      const blob = (card.dataset.search || '').toLowerCase();
      for (const qt of qTerms) {{ if (tags.indexOf(qt) >= 0) {{ score = 3; break; }} }}
      if (score < 3) {{
        for (const qt of qTerms) {{
          for (const t of tags) {{ if (t.indexOf(qt) >= 0 || qt.indexOf(t) >= 0) {{ score = 2; break; }} }}
          if (score === 2) break;
        }}
      }}
      if (score < 2 && blob.indexOf(q) >= 0) score = 1;
    }}
    card._score = score;

    const regMatch = activeReg === 'all' || reg === activeReg;
    const searchMatch = !q || score > 0;
    const catMatch = activeCat === 'all' || cat === activeCat;
    const l2Match = activeL2 === 'all' || l2 === activeL2;
    const viewMatch = activeView === 'all' || curated;
    const tag = (card.dataset.tags || '').split(' ').filter(Boolean);
    const tagMatch = activeTag === 'all' || (activeTag === '__funded__' ? (card.dataset.hasfund === '1') : tag.includes(activeTag));
    const recentMatch = !activeRecent || card.dataset.recent === '1';
    const hiddenMatch = (window.spShowHidden === true) || (card.dataset.hide !== '1');
    const readMatch = (window.spUnreadOnly !== true) || (card.dataset.read !== '1');
    const favMatch = !document.body.classList.contains('fav-mode') || card.dataset.fav === '1';
    const timeMatch = (activeEntTime === 'all') ? true : (function() {{
      const d = card.dataset.lastnews || '';
      if (!d) return false;
      const days = {{'1w':7,'2w':14,'1m':30,'3m':90}}[activeEntTime] || 0;
      const cut = new Date(); cut.setDate(cut.getDate() - days);
      const dd = new Date(d.replace(/-/g, '/'));
      return dd >= cut;
    }})();

    if (regMatch && searchMatch && viewMatch && tagMatch && recentMatch && hiddenMatch && readMatch && favMatch && timeMatch) {{
      if (cat) catVisCounts[cat] = (catVisCounts[cat] || 0) + 1;
      if (cat && l2) {{
        if (!l2VisCounts[cat]) l2VisCounts[cat] = {{}};
        l2VisCounts[cat][l2] = (l2VisCounts[cat][l2] || 0) + 1;
      }}
      if (catMatch && l2Match) {{
        card.style.display = '';
        visible++;
        matched.push(card);
      }} else {{
        card.style.display = 'none';
      }}
    }} else {{
      card.style.display = 'none';
    }}
  }});

  // 搜索命中时重排：精确标签命中最前，再按研究分、资讯数，让最贴切的排最前
  if (q && matched.length) {{
    matched.sort(function(a, b) {{
      const ds = (b._score || 0) - (a._score || 0);
      if (ds !== 0) return ds;
      const dr = (parseFloat(b.dataset.rv) || 0) - (parseFloat(a.dataset.rv) || 0);
      if (dr !== 0) return dr;
      return (parseInt(b.dataset.news || '0', 10)) - (parseInt(a.dataset.news || '0', 10));
    }});
    const list = document.getElementById('ent-list');
    matched.forEach(function(c) {{ list.appendChild(c); }});
  }}

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

// 时间筛选（按近期有动态的资讯日期过滤）
document.querySelectorAll('#ent-time-pills [data-enttime]').forEach(btn => {{
  btn.addEventListener('click', function() {{
    document.querySelectorAll('#ent-time-pills [data-enttime]').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    activeEntTime = this.dataset.enttime;
    try{{localStorage.setItem('sp_ent_time_filter', activeEntTime);}}catch(e){{}}
    filterEnt();
  }});
}});
(function() {{
  var st = null; try{{st = localStorage.getItem('sp_ent_time_filter');}}catch(e){{}}
  if (st) {{
    activeEntTime = st;
    document.querySelectorAll('#ent-time-pills [data-enttime]').forEach(function(b) {{ b.classList.toggle('active', b.dataset.enttime === st); }});
  }}
}})();

function hideAllL2Rows() {{
  document.querySelectorAll('.l2-row').forEach(row => row.style.display = 'none');
}}

filterEnt();

/* L1分类点击 → 展开/收起L2子类 */
function toggleL2Cat(l1Name) {{
  const row = document.getElementById('l2-' + l1Name);
  if (!row) return;
  if (row.style.display === 'none') {{
    // 先关闭其他所有L2
    document.querySelectorAll('.l2-row').forEach(function(r) {{ r.style.display = 'none'; }});
    row.style.display = '';
  }} else {{
    row.style.display = 'none';
  }}
}}

function toggleEntTags() {{
  const box = document.getElementById('ent-more-tags');
  const btn = document.getElementById('ent-toggle-tags');
  if (!box || !btn) return;
  box.style.display = box.style.display === 'none' ? '' : 'none';
}}

function toggleEntCats() {{
  const box = document.getElementById('ent-more-cats');
  if (!box) return;
  box.style.display = box.style.display === 'none' ? '' : 'none';
}}
</script>
</body>
</html>"""

    html_content = html_content.replace("__COMMON_CSS__", COMMON_CSS + FEEDBACK_CSS).replace("__SIDEBAR__", SIDEBAR("enterprise"))

    RECENT_CSS = """
/* 近期有动态徽标 + 筛选按钮（与统一按钮高度28px对齐） */
.ent-badge.badge-recent { background:#fff1e6; color:#e8590c; border:1px solid #ffd8a8; font-weight:600; white-space:nowrap; }
.ent-cluster-srcs { font-size:12px; color:#868e96; margin-left:4px; }
.ent-src-link { color:#1c7ed6; text-decoration:none; }
.ent-src-link:hover { text-decoration:underline; }
.recent-filter-btn { margin-left:0; padding:4px 11px; border:1.5px solid #e3e3e8; border-radius:14px; background:#fff; color:#555; cursor:pointer; font-size:11.5px; transition:.15s; height:28px; line-height:1; display:inline-flex; align-items:center; gap:3px; box-sizing:border-box; font-weight:600; }
.recent-filter-btn:hover { border-color:#ffa94d; }

/* 业务标签 chips（客户对象/角色/渠道）+ 阶段徽标 + 推荐理由 */
.ent-biz-tags { display:inline-flex; gap:4px; flex-wrap:wrap; margin-left:2px; }
.ent-biz-tag { font-size:11px; padding:1px 7px; border-radius:10px; border:1px solid #c5d8f0; color:#2b5a9c; background:#eef4fc; white-space:nowrap; }
.ent-biz-tag.biz-customer { border-color:#b2e2c4; color:#1c7a43; background:#e9f8ef; }
.ent-biz-tag.biz-role { border-color:#f0d9b5; color:#9a6b16; background:#fdf6e8; }
.ent-biz-tag.biz-channel { border-color:#e0c2ef; color:#7a2b9c; background:#f7eefc; }
.ent-tags-l1 { display:inline-flex; gap:4px; flex-wrap:wrap; align-items:center; margin-right:2px; }
.ent-tag-l1 { font-size:10.5px; color:#6b7280; background:#f3f4f6; border:1px solid #d1d5db; padding:2px 8px; border-radius:6px; font-weight:600; letter-spacing:.3px; }
.ent-badge.badge-stage { background:#eef0ff; color:#3b3b8f; border:1px solid #c5c8f0; font-weight:600; white-space:nowrap; }
.ent-reco { font-size:12px; color:#555; margin-top:4px; line-height:1.55; }
.ent-reco::first-letter { font-weight:600; }
.recent-filter-btn.active { background:#e8590c; color:#fff; border-color:#e8590c; }
"""
    html_content = html_content.replace("__RECENT_CSS__", RECENT_CSS)
    html_content = html_content.replace("window.spReapply = filterEnt;", "window.spReapply = filterEnt;\n" + syn_js)
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
