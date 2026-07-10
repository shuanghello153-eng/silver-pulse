# -*- coding: utf-8 -*-
"""
selection/tagger.py — 资讯交叉维度标签引擎（T34 重构核心）

设计目标
--------
资讯标签只承载「横切维度」，绝不与分类重复：
  * event_type（融资/收购并购/产品发布/政策法规/行业趋势/人事变动/其他事件）
    → 由 generator.classify_event_type 承担，存 article["event_type"]
  * domains（养老地产/居家养老/认知症/失智老人赛道…）
    → 由 generator.classify_domain 承担，存 article["domains"]
  * 本模块只产出「资本性质 / 反常识 / 政策·支付方 / 技术 / 市场 / 模式」这类
    能帮选题/写稿二次筛选的交叉维度标签，词表见 config.ARTICLE_TAG_POOL。

为什么独立成模块
----------------
score_and_merge.detect_tags 与 selection/recommend.run_daily_step 以前各自维护
一套标签逻辑，且 recommend 会把 event_type 塞进 tags 首位 —— 这正是「标签与分类
重复、太泛」的根因。现在两处都调用本模块的 detect_cross_tags，单一事实来源。

反常识自动标签
--------------
novelty >= config.ARTICLE_NOVELTY_TAG_THRESHOLD(=6) 时，自动追加「反常识」标签，
不依赖关键词。

约束
----
每条资讯标签数严格 2~5：
  - 规则命中 + 反常识，可能 >5 → 按 ARTICLE_TAG_RULES 顺序（=优先级）截断到 5；
  - 命中不足 2 → 用 event_type 兜底（仅兜底，避免空标签；会在日志提示），
    若仍不足 2 则补一个「常规资讯」占位（极少见）。
"""
import re

import config


# 复用 signal_strength 的金额解析（避免重复实现）。若未来拆分，这里会 fallback。
try:
    from selection.signal_strength import _parse_amount
except Exception:  # pragma: no cover
    def _parse_amount(text):
        if not text:
            return 0, None
        m = re.search(r"\$\s?([\d.]+)\s*(b|bn|billion|m|mn|million)",
                      text, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            unit = m.group(2).lower()
            val *= 1_000_000_000 if unit.startswith("b") else 1_000_000
            return val, "USD"
        m = re.search(r"([\d.]+)\s*(亿|万)\s*(元|美元|人民币|￥|¥)?", text)
        if m:
            val = float(m.group(1))
            cur = "USD" if (m.group(3) and "美元" in m.group(3)) else "CNY"
            val *= 100_000_000 if m.group(2) == "亿" else 10_000
            return val, cur
        return 0, None


# 大额融资金额阈值（人民币等价）：单笔 >= 1 亿即「大额融资」
_BIG_FUNDING_CNY = 100_000_000
# 海外美元阈值：>= 5000 万美元视作大额（对应「亿」量级近似）
_BIG_FUNDING_USD = 50_000_000


def _is_big_funding(blob):
    val, cur = _parse_amount(blob)
    if val <= 0:
        return False
    if cur == "USD":
        return val >= _BIG_FUNDING_USD
    return val >= _BIG_FUNDING_CNY


def detect_cross_tags(title, summary, event_type="", novelty=0, region="", domains=None):
    """返回一条资讯的「交叉维度标签」列表（长度 2~5）。

    Args:
        title / summary: 文本来源（优先中文 title_cn / summary_cn，调用方负责传入）
        event_type:      已分类的事件类型（融资/收购并购/产品发布…），
                        仅作「最后兜底」（极少见，正常由 rules 命中 >=2）。
        novelty:         novelty 分数（0~10），>=阈值自动加「反常识」
        region:          "domestic" / "overseas" / ""，可用于市场维度微调
        domains:         子赛道主题列表（generator.classify_domain 产出，如
                        ["养老地产","认知症"]）。当交叉维度规则命中不足 2 个时，
                        优先用 domains 补足 —— domains 与 event_type 是**不同轴**，
                        作为次级交叉标签可接受，且比把 event_type 本身塞回 tags
                        更符合「不与分类重复」原则。
    """
    blob = f"{title or ''} {summary or ''}"
    blob_low = blob.lower()

    tags = []
    for tag_name, kws in config.ARTICLE_TAG_RULES:
        if tag_name in tags:
            continue
        # 「大额融资」特殊处理：除了关键词，还要金额达标，避免「数千万」被误判
        if tag_name == "大额融资":
            hit = any(k in blob_low for k in kws) and _is_big_funding(blob)
            if hit:
                tags.append(tag_name)
            continue
        if any(k in blob_low for k in kws):
            tags.append(tag_name)

    # 反常识自动标签
    try:
        nov = float(novelty)
    except Exception:
        nov = 0
    if nov >= config.ARTICLE_NOVELTY_TAG_THRESHOLD and "反常识" not in tags:
        tags.append("反常识")

    # 强制 2~5
    tags = tags[:5]
    if len(tags) < 2:
        # 兜底：用「横切维度」官方标签池补足，绝不把领域名/事件类型塞回标签。
        # 标签只承载交叉维度（资本/技术/市场/模式/政策·支付方…），与 domains /
        # event_type 彻底解耦，避免卡片上「同一词既是领域徽章又是标签」的双显问题。
        _GENERIC_PAD = ["资本", "技术", "市场", "模式", "政策·支付方"]
        for g in _GENERIC_PAD:
            if g not in tags:
                tags.append(g)
            if len(tags) >= 2:
                break
    if len(tags) < 2:
        # 极罕见占位
        tags.append("常规资讯")
    return tags[:5]


def retag_article(article):
    """就地重算 article["tags"] 为交叉维度标签，返回新 tags。

    读取 article 已有字段：event_type / novelty / region / domains，
    优先用 title_cn+summary_cn，缺失时回退 title+summary。
    """
    title = (article.get("title_cn") or article.get("title") or "")
    summary = (article.get("summary_cn") or article.get("summary") or "")
    event_type = article.get("event_type") or ""
    try:
        novelty = float(article.get("novelty") or 0)
    except Exception:
        novelty = 0
    region = article.get("region") or ""
    domains = article.get("domains") or []
    new_tags = detect_cross_tags(title, summary, event_type, novelty, region, domains)
    article["tags"] = new_tags
    return new_tags


def retag_file(path):
    """对整份 scored_latest.json 重打标签，返回 (总数, 反常识数, 分布统计)。

    仅改 tags 字段（外加保证 event_type/domains 存在），不触碰其余字段，
    可安全重复运行。
    """
    import json
    with open(path, "r", encoding="utf-8") as f:
        arts = json.load(f)

    from collections import Counter
    dist = Counter()
    novel_cnt = 0
    for art in arts:
        # 保证 event_type / domains 已存在（collector/score_and_merge 流程内会填，
        # 但手动重跑时可能缺失 → 用 generator 兜底）
        if not art.get("event_type"):
            try:
                from generator import classify_event_type
                art["event_type"] = classify_event_type(
                    art.get("title_cn") or art.get("title", ""),
                    art.get("summary_cn") or art.get("summary", ""),
                    art.get("tags", []),
                )
            except Exception:
                art["event_type"] = "其他事件"
        if not art.get("domains"):
            try:
                from generator import classify_domain
                art["domains"] = classify_domain(
                    art.get("title_cn") or art.get("title", ""),
                    art.get("summary_cn") or art.get("summary", ""),
                    art.get("tags", []),
                )
            except Exception:
                art["domains"] = []
        tags = retag_article(art)
        for t in tags:
            dist[t] += 1
        if "反常识" in tags:
            novel_cnt += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(arts, f, ensure_ascii=False, indent=2)

    return len(arts), novel_cnt, dist


if __name__ == "__main__":
    import os
    p = os.path.join(config.DATA_DIR, "scored_latest.json")
    n, nov, dist = retag_file(p)
    print(f"[tagger] 重打标签完成：{n} 条，反常识 {nov} 条")
    print("[tagger] 标签分布：")
    for t, c in dist.most_common():
        print(f"  {c:3}  {t}")
