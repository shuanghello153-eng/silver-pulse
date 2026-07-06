"""
Compact scoring module — lightweight prompt for AI scoring.
Unlike the old version, this asks for a compact output:
just final_score, tags, recommendation (no detailed dimension breakdown).
"""
import json
import os
from datetime import datetime

from config import SCORING_DIMENSIONS, DATA_DIR, HIGH_VALUE_THRESHOLD, WATCH_THRESHOLD, NEWS_EVENT_TYPES, TAG_POOL

SCORED_FILE = os.path.join(DATA_DIR, "scored_latest.json")


def compute_final_score(scores):
    """Calculate weighted final score from dimension scores."""
    total = 0
    for dim in SCORING_DIMENSIONS:
        key = dim["name"] if "name" in dim else dim["label"]
        total += scores.get(key, 0) * dim["weight"]
    return round(total, 1)


def classify_score(final_score):
    if final_score >= HIGH_VALUE_THRESHOLD:
        return "high"
    elif final_score >= WATCH_THRESHOLD:
        return "watch"
    else:
        return "archive"


def load_scored():
    if os.path.exists(SCORED_FILE):
        with open(SCORED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_scored(articles):
    with open(SCORED_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(articles)} scored articles to {SCORED_FILE}")


def build_scoring_prompt(articles):
    """
    Compact scoring prompt — asks for minimal output to save tokens/cost.
    Output: final_score + category + tags + recommendation (2-3 sentences).
    """
    dim_desc = " ".join([
        f"{d['label']}({d['weight']*100:.0f}%)" for d in SCORING_DIMENSIONS
    ])

    articles_text = []
    for i, art in enumerate(articles):
        articles_text.append(
            f"[{i}] {art.get('title','')}\n"
            f"    src: {art.get('source','')} | date: {art.get('date','')}\n"
            f"    summary: {art.get('summary','')[:200]}"
        )

    industry_list = "|".join(list(TAG_POOL.keys()))
    event_list = "|".join(list(NEWS_EVENT_TYPES.keys()))

    prompt = f"""你是银发经济研究专家。对以下资讯打分(0-10分,四维加权:{dim_desc})和推荐理由。

【标签规则 — 严格遵守】
标签只能从以下27个白名单中选择，禁止自创标签：
  行业标签(最多选2个): {industry_list}
  事件标签(最多选1个): {event_list}
不要输出上述列表之外的任何标签。例如"银发经济""AI""36氪""上海"等都不是有效标签。

输出JSON数组,每条格式:
{{"id":0,"final_score":7.5,"category":"high|watch|archive","tags":["行业标签","事件标签"],"recommendation":"2-3句推荐理由,说清为什么值得关注、对中国市场有什么参照"}}

资讯列表:
{chr(10).join(articles_text)}

只输出JSON数组。high>=7.0, watch>=5.0, archive<5.0。"""
    return prompt
