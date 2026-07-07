"""Zero-cost re-apply: override news `industry`(赛道核心度) dim with a
code-derived centrality score, then recompute final_score.

Why: the 赛道核心度 should NOT be guessed by the model (costs points + inconsistent).
We map each news item's domain (an enterprise L1 category, matched by L1/L2 keywords)
to CATEGORY_CENTRALITY. This is fully deterministic and free.

Run:  python reapply_centrality.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config  # noqa: E402

SCORED = os.path.join("data", "scored_latest.json")

# ---- 反常识度 (novelty_surprise): 代码关键词判定，零成本 ----
NOVELTY_SURPRISE_KW = [
    "减值", "impairment", "write-down", "writeoff", "write-off", "关店", "closure",
    "关闭门店", "停运", "裁员", "layoff", "退出", "exit", "破产", "bankrupt",
    "亏损", "loss", "暴雷", "关停", "撤出", "shutdown", "wind-down", "暴跌",
    "plunge", "诉讼", "lawsuit", "fraud", "丑闻", "scandal", "下滑", "暴减",
]
NOVELTY_TRIGGER_KW = [
    "收购", "并购", "acquisition", "收购并购", "融资", "funding", "raise", "ipo",
    "上市", "扩张", "利好", "partnership", "合作", "投资", "invest", "估值",
]


def detect_amount_usd(text):
    """Rough USD extraction: supports $Xbn/$Xm, X亿美元, X亿人民币."""
    if not text:
        return 0
    m = re.search(r"\$\s*([\d.]+)\s*(billion|bn|million|m)", text, re.I)
    if m:
        v = float(m.group(1))
        return v * (1_000_000_000 if m.group(2).lower().startswith(("b", "bn")) else 1_000_000)
    m = re.search(r"([\d.]+)\s*亿美元", text)
    if m:
        return float(m.group(1)) * 100_000_000
    m = re.search(r"([\d.]+)\s*亿人民币", text)
    if m:
        return float(m.group(1)) * 100_000_000
    return 0


def detect_novelty(text, event_type, amount_usd):
    """0-10: 预期违背/反常识钩子。纯代码判定。"""
    text = (text or "").lower()
    has_surprise = any(k.lower() in text for k in NOVELTY_SURPRISE_KW)
    has_trigger = any(k.lower() in text for k in NOVELTY_TRIGGER_KW)
    score = 0
    if has_surprise and has_trigger:
        score += 6
    elif has_surprise:
        score += 3
    if (event_type or "") in ("收购并购",) and has_surprise:
        score += 2
    if amount_usd and amount_usd >= 100_000_000:
        score += 2
    return min(10, score)


def classify_domain(text):
    """Return (domain_l1, centrality) for the given text, or (None, None)."""
    text = (text or "").lower()
    best, best_c = None, -1
    for dom in config.NEWS_DOMAINS:
        keys = [dom] + list(config.ENTERPRISE_CATEGORIES.get(dom, {}).get("l2", []))
        for k in keys:
            if k.lower() in text:
                c = config.CATEGORY_CENTRALITY.get(dom, config.CATEGORY_CENTRALITY_DEFAULT)
                if c > best_c:
                    best_c, best = c, dom
                break
    return best, (best_c if best is not None else None)


def main():
    data = json.load(open(SCORED, encoding="utf-8"))
    w = config.NEWS_SCORING_DIMS
    for it in data:
        ds = it.get("dim_scores") or {}
        blob = " ".join([
            it.get("title_cn") or "", it.get("summary_cn") or "",
            it.get("title") or "", it.get("summary") or "",
        ])
        dom, cen = classify_domain(blob)
        if cen is None:
            cen = config.CATEGORY_CENTRALITY_DEFAULT
        ds["industry"] = cen
        it["domain"] = dom
        it["centrality"] = cen
        nov = detect_novelty(blob, it.get("event_type") or "", detect_amount_usd(blob))
        ds["novelty"] = nov
        final = sum((ds.get(k, 0) or 0) * w[k]["weight"] for k in w)
        adj = config.SOURCE_ADJ.get(it.get("tier"), 0.0)
        it["final_score"] = round(final + adj, 2)
    json.dump(data, open(SCORED, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"reapplied centrality + final_score to {len(data)} items -> {SCORED}")


if __name__ == "__main__":
    main()
