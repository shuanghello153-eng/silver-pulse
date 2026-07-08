# -*- coding: utf-8 -*-
"""Rule-based fallback for the L3 model 4-dim scoring (signal/writing/cn_fit/urgency).

When no model API is configured, this module derives the four model-owned
dimensions purely from keywords so that reapply_centrality can compute a
differentiated final_score and the 精选 view gets populated. Zero cost.

Exposes run_daily_step() so run_daily.py can call it as a pipeline stage.
"""
import json
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from score_and_merge import detect_event  # reuse event detection
import config  # SELECT_THRESHOLDS etc.

SCORED = os.path.join("data", "scored_latest.json")

CN_KW = ["中国", "国内", "本土", "国产", "银发", "china", "chinese", "央视",
         "a股", "港股", "沪深", "科创板", "北交所", "深圳", "北京", "上海"]
EVENT_HIGH_URGENCY = {"融资", "收购并购", "IPO上市", "政策法规"}
AMOUNT_RE = re.compile(
    r"(\$\s?[\d.]+\s?(?:billion|bn|million|m)?|\d+\.?\d*\s?(?:亿|万)\s?(?:元|美元|人民币)?)",
    re.I,
)


def _clamp(x, lo=0.0, hi=10.0):
    try:
        return max(lo, min(hi, float(x)))
    except (TypeError, ValueError):
        return lo


def score_signal(art):
    # Prefer collector's signal_score; fall back to final_score.
    s = art.get("signal_score")
    if s is None:
        s = art.get("final_score", 0)
    return _clamp(s)


def score_writing(art):
    blob = "%s %s" % (art.get("title", ""), art.get("summary", ""))
    v = 4.0
    if AMOUNT_RE.search(blob):
        v += 2.0
    if len(art.get("summary", "") or "") >= 150:
        v += 2.0
    ev = art.get("event_type") or detect_event(blob)
    if ev in ("融资", "收购并购", "IPO上市", "政策法规", "产品发布"):
        v += 2.0
    return _clamp(v)


def score_cn_fit(art):
    blob = "%s %s" % (art.get("title", ""), art.get("summary", ""))
    base = 3.0 if art.get("region") == "domestic" else 0.0
    if any(k.lower() in blob.lower() for k in CN_KW):
        base += 5.0
    return _clamp(base)


def score_urgency(art):
    blob = "%s %s" % (art.get("title", ""), art.get("summary", ""))
    ev = art.get("event_type") or detect_event(blob)
    v = 2.0
    if ev in EVENT_HIGH_URGENCY:
        v += 4.0
    if AMOUNT_RE.search(blob):
        v += 2.0
    d = art.get("date", "")
    try:
        dd = datetime.strptime(d, "%Y-%m-%d")
        days = (datetime.now() - dd).days
        if days <= 2:
            v += 2.0
        elif days <= 7:
            v += 1.0
    except Exception:
        pass
    return _clamp(v)


def run_daily_step():
    if not os.path.exists(SCORED):
        print("[score_skill] no scored_latest.json, skip")
        return
    data = json.load(open(SCORED, encoding="utf-8"))
    for it in data:
        ds = it.get("dim_scores") or {}
        blob = "%s %s" % (it.get("title", ""), it.get("summary", ""))
        if not it.get("event_type"):
            it["event_type"] = detect_event(blob)
        ds["signal"] = score_signal(it)
        ds["writing"] = score_writing(it)
        ds["cn_fit"] = score_cn_fit(it)
        ds["urgency"] = score_urgency(it)
        it["dim_scores"] = ds
        # curation flags that drive the 精选 view
        view = it.get("view", "")
        fs = it.get("final_score", 0) or 0
        it["is_curated"] = bool(view == "curated" or fs >= 5.0)
        it["is_selected"] = bool(it["is_curated"] or fs >= 5.0)
        if "entity_name" not in it:
            it["entity_name"] = ""
        if "cluster_id" not in it:
            it["cluster_id"] = None
    json.dump(data, open(SCORED, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[score_skill] filled 4 dims + curation flags for %d items" % len(data))


if __name__ == "__main__":
    run_daily_step()
