"""Zero-cost re-apply: override news `industry`(赛道核心度) dim with a
code-derived centrality score, then recompute final_score.

Why: the 赛道核心度 should NOT be guessed by the model (costs points + inconsistent).
We map each news item's domain (an enterprise L1 category, matched by L1/L2 keywords)
to CATEGORY_CENTRALITY. This is fully deterministic and free.

Run:  python reapply_centrality.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config  # noqa: E402

SCORED = os.path.join("data", "scored_latest.json")


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
        final = sum((ds.get(k, 0) or 0) * w[k]["weight"] for k in w)
        adj = config.SOURCE_ADJ.get(it.get("tier"), 0.0)
        it["final_score"] = round(final + adj, 2)
    json.dump(data, open(SCORED, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"reapplied centrality + final_score to {len(data)} items -> {SCORED}")


if __name__ == "__main__":
    main()
