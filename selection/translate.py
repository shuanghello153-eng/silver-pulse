# -*- coding: utf-8 -*-
"""Zero-cost Chinese fallback for title/summary translation.

No model API -> just ensure title_cn/summary_cn exist (fall back to the
original title/summary) so downstream rendering & novelty detection never
hit empty strings. Exposes run_daily_step() for run_daily.py.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCORED = os.path.join("data", "scored_latest.json")


def run_daily_step():
    if not os.path.exists(SCORED):
        print("[translate] no scored_latest.json, skip")
        return
    data = json.load(open(SCORED, encoding="utf-8"))
    for it in data:
        if not it.get("title_cn"):
            it["title_cn"] = it.get("title", "")
        if not it.get("summary_cn"):
            it["summary_cn"] = it.get("summary", "")
    json.dump(data, open(SCORED, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[translate] ensured title_cn/summary_cn for %d items" % len(data))


if __name__ == "__main__":
    run_daily_step()
