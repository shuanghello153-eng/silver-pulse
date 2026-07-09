# -*- coding: utf-8 -*-
"""
enterprise_score.py — Enterprise research-value scorer (代码实现, 零 AI 成本).

Computes each enterprise's research-value score (0-100) in pure code:
  - base_value (0-70): size / info-richness / model-diff / China-comparability
  - event_boost (0-30): dynamic boost from recent related news signals

Writes:
  - data/enterprise/enterprise_scores.json   (keyed by serial)
  - writes `research_value` back into all_enterprises.json `value_score`
    (preserves ALL other fields, including prior enrichment).

No AI calls. Deterministic.
"""
import os
import re
import sys
import json
import glob
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

ENT_DIR = os.path.join(config.DATA_DIR, "enterprise")
ALL_PATH = os.path.join(ENT_DIR, "all_enterprises.json")
SCORES_PATH = os.path.join(ENT_DIR, "enterprise_scores.json")

# reference date if no news present
REFERENCE_TODAY = "2026-07-07"

LISTED_KW = ["上市", "IPO", "Nasdaq", "NYSE", "HKEX", "港股", "美股", "上市公司"]
V3_TAGS = ["模式创新", "订阅制", "B2B2C", "硬件+服务", "对标标的"]
V3_KEYWORDS = ["创新", "独特", "订阅", "平台", "生态"]
REGION_DOMESTIC = {"国内", "domestic"}
REGION_OVERSEAS = {"海外", "overseas"}


# ----------------------------------------------------------------------------
# funding_total parsing helpers
# ----------------------------------------------------------------------------
def _funding_str(ent):
    """Return a lower-cased string representation of funding_total, or ''."""
    ft = ent.get("funding_total")
    if ft is None:
        return ""
    if isinstance(ft, dict):
        parts = [str(ft.get("display", "") or ""), str(ft.get("amount", "") or "")]
        return " ".join(p for p in parts if p).lower()
    return str(ft).lower()


def _funding_present(ent):
    """funding_total is 'present' only if it carries a real (non-未披露) value."""
    s = _funding_str(ent)
    if not s:
        return False
    if "未披露" in s or "none" in s or s.strip() in ("", "{}"):
        return False
    return True


def _funding_amount_millions(ent):
    """Best-effort parse of funding_total into an approximate magnitude in
    millions (USD/ RMB treated on one scale per the spec: 'million USD or 亿').

    Unit scaling: 亿 -> x100 (1亿 ≈ 100M), 万 -> x0.01, B/billion -> x1000,
    M/million -> x1. Returns float >=0 (0 if no parseable number).
    """
    s = _funding_str(ent)
    if not s:
        return 0.0
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if not m:
        return 0.0
    num = float(m.group(1))
    if "亿" in s:
        return num * 100.0
    if "万" in s:
        return num * 0.01
    if "b" in s or "billion" in s:
        return num * 1000.0
    # default: M / million or bare number
    return num


# ----------------------------------------------------------------------------
# base_value components
# ----------------------------------------------------------------------------
def _v1_size(ent):
    s = _funding_str(ent)
    tags = ent.get("tags") or []
    if any(k.lower() in s for k in LISTED_KW) or ("IPO上市" in tags):
        return 25
    if _funding_present(ent) and _funding_amount_millions(ent) >= 100.0:
        return 20
    if _funding_present(ent):
        return 12
    inv = ent.get("investors") or ""
    if isinstance(inv, list):
        inv = " ".join(str(x) for x in inv)
    if str(inv).strip():
        return 8
    if any(t in ("种子轮", "成长期") for t in tags):
        return 6
    return 3


def _v2_info(ent, news_cov=None):
    desc = (ent.get("description") or "").strip()
    hl = (ent.get("highlights") or "").strip()
    bm = (ent.get("business_model") or "").strip()
    score = 0
    if desc and hl and bm and (len(desc) + len(hl) + len(bm) > 100):
        score += 10
    if (ent.get("website_url") or "").strip():
        score += 5
    if (ent.get("crunchbase_url") or "").strip():
        score += 3
    # V2(信息丰富度) 现为最高权重分量(用户决策: 信息丰富度权重更大)。
    base = min(20, score)
    # ---- forward-compat: news_coverage enrichment (V2 agents fill later) ----
    # If a news_coverage.json / news_coverage_batch*.json is present with a
    # `news_count` per serial, scale V2 up to reward real media footprint:
    #   news_count>=20 -> +8, 10-19 -> +5, 5-9 -> +2, else base (no change).
    # Loaded gracefully; if absent this branch is skipped entirely.
    if news_cov:
        serial = ent.get("serial")
        nc = news_cov.get(serial)
        ncount = 0
        if isinstance(nc, dict):
            ncount = nc.get("news_count", 0) or 0
        elif isinstance(nc, int):
            ncount = nc
        if ncount >= 20:
            base += 8
        elif ncount >= 10:
            base += 5
        elif ncount >= 5:
            base += 2
    return base


def _v3_model(ent):
    tags = ent.get("tags") or []
    if any(t in V3_TAGS for t in tags):
        return 15
    bm = (ent.get("business_model") or "")
    if any(k in bm for k in V3_KEYWORDS):
        return 10
    return 4


def _v4_learnability(ent, v3):
    """V4 = LEARNABILITY / BENCHMARK value (redefined per Q9; was 'cn_fit').

    NOT 'is it comparable to China' (which is trivially true for domestic).
    It is the degree to which the enterprise is a BENCHMARK worth Chinese
    entrepreneurs / researchers STUDYING ("以海外为镜").

      overseas: learnable (tag `对标标的` OR business_model mentions
                可借鉴/参考/模式) -> 15; notable model (V3>=10) -> 10; else 6
      domestic : listed/large benchmark (funding_total display contains
                上市/IPO/Nasdaq/NYSE/HKEX/港股/美股/上市公司 OR tag `IPO上市`)
                -> 15; novel model (V3>=10) -> 12; else 8

    Cap 15.
    """
    tags = ent.get("tags") or []
    bm = ent.get("business_model") or ""
    region = (ent.get("region") or "").strip()
    is_overseas = region in REGION_OVERSEAS
    is_domestic = region in REGION_DOMESTIC

    learnable = ("对标标的" in tags) or any(
        k in bm for k in ("可借鉴", "参考", "模式")
    )
    # domestic listed/large benchmark check (S1 high signal)
    ft_str = _funding_str(ent)
    listed = any(k.lower() in ft_str for k in LISTED_KW) or ("IPO上市" in tags)

    if is_overseas:
        if learnable:
            return 15
        if v3 >= 10:
            return 10
        return 6
    if is_domestic:
        # 国内企业: "标杆可借鉴(V4)"权重调小(用户决策)。
        # 国内处于早期、标杆稀少(海外10个≈国内1个), 不靠 V4 拉开分差;
        # 国内企业分数主要由 V2(信息丰富度) + 最新事件(event_boost) 决定。
        if listed:
            return 12
        if v3 >= 10:
            return 9
        return 6
    return 6  # unknown region: neutral baseline


def compute_base_value(ent, news_cov=None):
    v1 = _v1_size(ent)
    v2 = _v2_info(ent, news_cov)
    v3 = _v3_model(ent)
    v4 = _v4_learnability(ent, v3)
    return min(70, v1 + v2 + v3 + v4), (v1, v2, v3, v4)


def _evidence_depth(ent):
    """连续「资料厚度」微调分 (0~12)，游离于 base 的 70 上限之外。

    目的（DATA 分身 B1/B5 报告痛点）：base_value 全是粗离散档，大量头部
    企业撞档并列、天花板卡在 61（S/A 级永远空缺）。本项按企业携带的
    **可量化证据丰富度** 打连续小分，让"资料越全 = 越好写 = 研究价值越高"
    的企业自然往上分层、打破并列，直接强化小爽认同的"信息丰富度最高权重"。

    纯代码、零 AI、确定性；只读已有字段，不新增任何数据依赖。
    """
    depth = 0.0
    desc = (ent.get("description") or "").strip()
    hl = (ent.get("highlights") or "").strip()
    bm = (ent.get("business_model") or "").strip()
    # 描述厚度：每 60 字 +1，上限 4
    depth += min(4.0, len(desc) / 60.0)
    # 亮点：有且详实 +2，仅有 +1
    depth += 2.0 if len(hl) > 40 else (1.0 if hl else 0.0)
    # 商业模式描述厚度：每 30 字 +1，上限 2
    depth += min(2.0, len(bm) / 30.0)
    # 可追溯外链
    if (ent.get("website_url") or "").strip():
        depth += 1.0
    if (ent.get("crunchbase_url") or "").strip():
        depth += 1.0
    # 投资方数量（可核信息源）
    inv = ent.get("investors") or ""
    if isinstance(inv, list):
        inv_n = len([x for x in inv if str(x).strip()])
    else:
        inv_n = 1 if str(inv).strip() else 0
    depth += min(2.0, float(inv_n))
    # 标签密度（每 2 个 +1，上限 2）
    tags = ent.get("tags") or []
    depth += min(2.0, len(tags) / 2.0)
    return min(12.0, depth)


# ----------------------------------------------------------------------------
# event_boost (dynamic, from news)
# ----------------------------------------------------------------------------
def _parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return None


def compute_event_boost(ent, news, today_dt):
    """Return (event_boost, last_event_date, related_ids, top_event)."""
    name = (ent.get("name") or "").strip().lower()
    if not name:
        return 0, None, [], None
    related = []
    for n in news:
        en = (n.get("entity_name") or "").strip().lower()
        if en and en == name:
            related.append(n)
    if not related:
        return 0, None, [], None

    last_event_date = max(
        (n.get("date", "") for n in related if n.get("date")), default=None
    )

    # top event = event_type of highest-signal related news (ties -> newest)
    top_event = None
    best = None
    for n in related:
        sig = n.get("signal_score", 0) or 0
        dt = _parse_date(n.get("date", ""))
        key = (sig, dt.timestamp() if dt else 0)
        if best is None or key > best[0]:
            best = (key, n.get("event_type"))
    if best:
        top_event = best[1]

    boost = 0
    # 7-day window
    in7 = [
        n for n in related
        if (n.get("date") and (today_dt - _parse_date(n["date"])).days <= 7)
    ]
    if in7:
        max_sig = max((n.get("signal_score", 0) or 0) for n in in7)
        if max_sig >= 7:
            boost += config.EVENT_BOOST["signal_ge_7"]
        elif max_sig >= 5:
            boost += config.EVENT_BOOST["signal_5_7"]

    # 30-day window: M&A / IPO event
    in30 = [
        n for n in related
        if (n.get("date") and 0 <= (today_dt - _parse_date(n["date"])).days <= 30)
    ]
    if any(n.get("event_type") in ("收购并购", "IPO上市") for n in in30):
        boost += config.EVENT_BOOST["ma_ipo_event"]

    boost = min(boost, config.EVENT_BOOST["cap"])
    related_ids = [n.get("url", "") or n.get("url_hash", "") for n in related]
    return boost, last_event_date, related_ids, top_event


# ----------------------------------------------------------------------------
# News-coverage enrichment loader (forward-compat; graceful skip if absent)
# ----------------------------------------------------------------------------
def load_news_coverage():
    """Load news_coverage enrichment if present; else return {}.

    Accepts `news_coverage.json` or `news_coverage_batch*.json` (first found
    wins). Tolerates either keying:
      {serial: <int news_count>}                or
      {serial: {"news_count": <int>}}           or
      [ {serial, news_count}, ... ]
    Returns dict {serial: {"news_count": int}}.
    """
    candidates = [os.path.join(ENT_DIR, "news_coverage.json")]
    candidates += sorted(glob.glob(os.path.join(ENT_DIR, "news_coverage_batch*.json")))
    for path in candidates:
        if not os.path.exists(path):
            continue
        try:
            data = json.load(open(path, "r", encoding="utf-8"))
        except Exception:
            continue
        cov = {}
        if isinstance(data, dict):
            for serial, val in data.items():
                if isinstance(val, int):
                    cov[serial] = {"news_count": val}
                elif isinstance(val, dict):
                    nc = val.get("news_count")
                    if isinstance(nc, int):
                        cov[serial] = {"news_count": nc}
        elif isinstance(data, list):
            for it in data:
                if not isinstance(it, dict):
                    continue
                serial = it.get("serial")
                nc = it.get("news_count")
                if serial and isinstance(nc, int):
                    cov[serial] = {"news_count": nc}
        if cov:
            return cov
    return {}


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    ents = json.load(open(ALL_PATH, "r", encoding="utf-8"))
    news_path = os.path.join(config.DATA_DIR, "scored_latest.json")
    news = []
    if os.path.exists(news_path):
        news = json.load(open(news_path, "r", encoding="utf-8"))

    # forward-compat news coverage (graceful: {} if absent)
    news_cov = load_news_coverage()

    # today = most recent news date, else reference
    news_dates = [n.get("date", "") for n in news if n.get("date")]
    today_str = max(news_dates) if news_dates else REFERENCE_TODAY
    today_dt = _parse_date(today_str) or _parse_date(REFERENCE_TODAY)

    scores = {}
    for ent in ents:
        serial = ent.get("serial")
        region = (ent.get("region") or "").strip()
        is_overseas = region in REGION_OVERSEAS
        base, (v1, v2, v3, v4) = compute_base_value(ent, news_cov)
        boost, last_date, rids, top_event = compute_event_boost(ent, news, today_dt)
        # MIRROR_BONUS: explicit "以海外为镜" adjustment, overseas only (cap 100)
        mirror = config.MIRROR_BONUS if is_overseas else 0
        # 连续资料厚度微调（0~12，游离于 base 70 上限外）：打破头部并列、
        # 让天花板突破 61 使 S/A 级不再空缺（DATA B1/B5 报告痛点）。
        depth = _evidence_depth(ent)
        rv = min(100, base + boost + mirror + depth)

        # ---- worth_deep_write: 4 standards (S1 size / S2 event /
        #      S3 model diff / S4 cn_fit>=12) ----
        s1 = v1 >= 20
        s2 = boost > 0
        s3 = v3 >= 10
        s4 = v4 >= 12
        hit_labels = []
        if s1:
            hit_labels.append("S1大企业")
        if s2:
            hit_labels.append("S2近期事件")
        if s3:
            hit_labels.append("S3差异化模式")
        if s4:
            hit_labels.append("S4标杆可借鉴")
        worth = (rv >= 45) or (len(hit_labels) >= 2)
        if worth:
            reason = "命中标准: " + " / ".join(hit_labels) + " —— 值得深度写"
        else:
            reason = ("未达深度写标准（rv=%d，命中%d项：%s）"
                      % (rv, len(hit_labels), " / ".join(hit_labels) or "无"))

        # 研究价值分级 (S/A/B/C) — 借鉴评分.md 的 F 级思路
        grade = "—"
        for g, thr in sorted(config.ENTERPRISE_GRADE.items(),
                             key=lambda kv: -kv[1]):
            if rv >= thr:
                grade = g
                break

        scores[serial] = {
            "research_value": int(rv),
            "grade": grade,
            "base_value": int(base),
            "event_boost": int(boost),
            "mirror_bonus": int(mirror),
            "evidence_depth": round(float(depth), 1),
            "v1": int(v1), "v2": int(v2), "v3": int(v3), "v4": int(v4),
            "last_event_date": last_date,
            "related_news_ids": rids,
            "top_event": top_event,
            "worth_deep_write": bool(worth),
            "deep_write_reason": reason,
        }

    json.dump(scores, open(SCORES_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # NOTE: all_enterprises.json `value_score` write-back is OWNED BY THE FINAL
    # MERGE STEP in this run. We deliberately do NOT modify all_enterprises.json
    # here, to avoid clobbering other in-flight enrichment fields.

    # ---- reporting ----
    rvs = [s["research_value"] for s in scores.values()]
    boosted = sum(1 for s in scores.values() if s["event_boost"] > 0)
    deep = sum(1 for s in scores.values() if s["worth_deep_write"])
    print("=" * 60)
    print("ENTERPRISE RESEARCH-VALUE SCORER")
    print("=" * 60)
    print(f"enterprises scored   : {len(scores)}")
    print(f"research_value min   : {min(rvs)}")
    print(f"research_value max   : {max(rvs)}")
    print(f"research_value mean  : {sum(rvs)/len(rvs):.1f}")
    print(f"got event_boost>0    : {boosted}")
    print(f"worth_deep_write=True: {deep}")
    print("-" * 60)
    by_serial = {e.get("serial"): e for e in ents}
    top = sorted(scores.items(), key=lambda kv: kv[1]["research_value"],
                 reverse=True)[:10]
    print("TOP 10 by research_value:")
    for serial, s in top:
        ent = by_serial.get(serial, {})
        nm = ent.get("name", serial)
        rg = ent.get("region", "?")
        print(f"  {nm:<26} rv={s['research_value']:<3} "
              f"region={rg:<4} worth_deep={s['worth_deep_write']} "
              f"reason={s['deep_write_reason']}")


if __name__ == "__main__":
    main()
