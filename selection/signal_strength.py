# -*- coding: utf-8 -*-
"""
selection/signal_strength.py — 信号强度脚本评分（0~10，零模型成本）

这是评分体系"三阶段"的第 3 阶段（脚本层），完全由关键词/规则推导，
不消耗任何 token。设计依据：小爽 2026-07-09 邮件建议。

公式（各分量相加，clamp 到 0~10）：
  source_tier : T1=0.5 / T2=0.3 / T3=0.1
                （注：相关性已由前置闸门过滤，信源等级仅作微弱起点；
                 小爽2026-07-09拍板降权——事件本身分量远比出处重要）
  ipo        : 若事件含 IPO/上市 => +6（巨头，有招股书/年报，信息量丰富）
  funding    : 融资金额分级（海外美元 / 国内元 两套阈值）
  ma         : 收购金额分级（海外美元 / 国内元 两套阈值）
  recency    : 时效（按发布日期动态计算，非存死值）
               近1周=2.5 / 近1月=2.0 / 近2月=1.5 / 近半年=1.0 / 近1年=0.5 / 更久=0.25

下游用法（run_daily / score_and_merge）：
  - 写入每条资讯的 `signal_strength` 字段（不改现有 final_score 行为）。
  - 0722 前（HY3 免费）：所有相关文章都喂给强模做五维判断。
  - 0722 后（低成本模型）：仅 `signal_strength >= 5` 的文章才喂强模，
    其余只保留脚本评分，省 token。
"""
import re
from datetime import datetime, timezone


# ---- 阈值表（小爽指定）----
SOURCE_TIER_START = {1: 0.5, 2: 0.3, 3: 0.1}

# 融资金额：海外美元（>=），(下限, 分值)
FUNDING_OVERSEAS = [
    (1_000_000_000, 5), (100_000_000, 4), (50_000_000, 3),
    (10_000_000, 2), (5_000_000, 1), (1_000_000, 0.5),
]
# 融资金额：国内元（>=），(下限, 分值)
FUNDING_DOMESTIC = [
    (1_000_000_000, 6), (100_000_000, 5), (50_000_000, 4),
    (10_000_000, 3), (5_000_000, 2), (1_000_000, 1), (500_000, 0.5),
]
# 收购金额（海外美元 / 国内元 共用同一套下限，>=），(下限, 分值)
MA_TIERS = [
    (10_000_000_000, 6), (5_000_000_000, 5), (1_000_000_000, 4),
    (100_000_000, 3), (50_000_000, 2), (10_000_000, 1),
]

IPO_KEYWORDS = ["ipo", "ipo filing", "goes public", "上市", "敲钟", "挂牌", "公开募股", "nasdaq", "港交所"]
FUNDING_KEYWORDS = ["raises", "raises series", "series a", "series b", "series c", "series d",
                    "seed round", "funding", "融资", "战略融资", "A轮", "B轮", "C轮", "D轮",
                    "天使轮", "获投", "获融", "本轮", "轮融资"]
MA_KEYWORDS = ["acquires", "acquisition", "acquired", "收购", "并购", "merger", "买下", "被收购"]


def _days_ago(date_str):
    if not date_str:
        return 9999
    try:
        # 兼容 'YYYY-MM-DD' 或带时间的 ISO
        s = date_str[:10]
        d = datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - d).days
    except Exception:
        return 9999


def _recency_score(days):
    if days <= 7:
        return 2.5
    if days <= 30:
        return 2.0
    if days <= 60:
        return 1.5
    if days <= 180:
        return 1.0
    if days <= 365:
        return 0.5
    return 0.25


def _parse_amount(text):
    """返回 (value_float, currency) 或 (0, None)。支持 $Xm/$Xb/数字亿/万。"""
    if not text:
        return 0, None
    # 美元： $1.2B / $50 million / $300M
    m = re.search(r"\$\s?([\d.]+)\s*(b|bn|billion|m|mn|million)", text, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        unit = m.group(2).lower()
        if unit.startswith("b"):
            val *= 1_000_000_000
        else:
            val *= 1_000_000
        return val, "USD"
    # 人民币/元： 1.2亿 / 5000万 / 3亿元 / 10亿人民币
    m = re.search(r"([\d.]+)\s*(亿|万)\s*(元|美元|人民币|￥|¥)?", text)
    if m:
        val = float(m.group(1))
        unit = m.group(2)
        cur = "USD" if (m.group(3) and "美元" in m.group(3)) else "CNY"
        if unit == "亿":
            val *= 100_000_000
        else:  # 万
            val *= 10_000
        return val, cur
    return 0, None


def _tier_for_funding(value, currency):
    table = FUNDING_OVERSEAS if currency == "USD" else FUNDING_DOMESTIC
    for low, score in table:
        if value >= low:
            return score
    return 0


def compute_signal_strength(article, source_tier=2):
    """article: dict with title/summary/date(可选). 返回 0~10 float。"""
    title = (article.get("title_cn") or article.get("title") or "")
    summary = (article.get("summary_cn") or article.get("summary") or "")
    blob = (title + " " + summary)
    blob_low = blob.lower()

    score = 0.0
    breakdown = {}

    # 1) 信源起点
    tier = SOURCE_TIER_START.get(source_tier, 0.5)
    score += tier
    breakdown["source_tier"] = tier

    # 2) IPO
    is_ipo = any(k in blob_low for k in IPO_KEYWORDS)
    if is_ipo:
        score += 6
        breakdown["ipo"] = 6

    # 3) 融资
    is_fund = any(k in blob_low for k in FUNDING_KEYWORDS)
    if is_fund:
        val, cur = _parse_amount(blob)
        if val > 0:
            fscore = _tier_for_funding(val, cur)
            score += fscore
            breakdown["funding"] = fscore

    # 4) 收购
    is_ma = any(k in blob_low for k in MA_KEYWORDS)
    if is_ma:
        val, cur = _parse_amount(blob)
        if val > 0:
            mscore = 0
            for low, sc in MA_TIERS:
                if val >= low:
                    mscore = sc
                    break
            score += mscore
            breakdown["ma"] = mscore

    # 5) 时效（动态）
    days = _days_ago(article.get("date", ""))
    rscore = _recency_score(days)
    score += rscore
    breakdown["recency"] = rscore

    final = round(min(10.0, score), 2)
    return final, breakdown


if __name__ == "__main__":
    tests = [
        {"title": "ABC Care 完成 2 亿美元 C 轮融资", "summary": "", "date": "2026-07-08"},
        {"title": "Welltower 以 80 亿美元收购养老社区运营商", "summary": "", "date": "2026-07-01"},
        {"title": "某银发企业登陆纳斯达克 IPO", "summary": "", "date": "2026-06-20"},
        {"title": "某养老平台获 3000 万元天使轮", "summary": "", "date": "2026-05-01"},
        {"title": "老年游戏厂商发布新版本", "summary": "", "date": "2026-07-05"},
    ]
    for t in tests:
        s, b = compute_signal_strength(t, source_tier=2)
        print(f"signal={s:5} | {t['title'][:24]:24} | {b}")
