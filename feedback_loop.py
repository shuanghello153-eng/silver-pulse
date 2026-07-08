"""
feedback_loop.py — Loop Engineering 的 L3（外部反馈）闭环：收藏回灌评分。

这是「最慢但最重要」的一层：小爽在网站上 ⭐收藏 的选题/企业，导出的
feedback.jsonl 会被本模块读取，统计她的真实偏好，并**安全地**微调选题评分权重
（仅 novelty / signal 等可在上下限内浮动 ±0.03，绝不改架构、绝不烧积分）。

机制（写查分离 + 边界控制）：
  - 本模块只「读」收藏 + 「算」偏好 + 「写」user_pref.json（不修改 config.py 架构）
  - reapply_centrality 在算终分时读取 user_pref.json 并应用（带上下限夹紧）
  - 每次调整都留痕到 user_pref.json 的 history，便于回看与回滚

无 feedback.jsonl 时本模块为空操作（graceful no-op），绝不中断流水线。
"""
import json
import os
import hashlib
from collections import Counter, defaultdict

from config import DATA_DIR, NEWS_SCORING_DIMS

SCORED_PATH = os.path.join(DATA_DIR, "scored_latest.json")
ENT_PATH = os.path.join(DATA_DIR, "enterprise", "all_enterprises.json")
FEEDBACK_PATH = os.path.join(DATA_DIR, "feedback.jsonl")
PREF_PATH = os.path.join(DATA_DIR, "user_pref.json")

# 权重可调维度的上下限（防止失控）
WEIGHT_BOUNDS = {
    "industry": (0.12, 0.24),
    "signal": (0.18, 0.30),
    "writing": (0.10, 0.20),
    "cn_fit": (0.14, 0.24),
    "urgency": (0.10, 0.20),
    "novelty": (0.06, 0.16),
}
DELTA_CAP = 0.03  # 单次最多浮动 0.03


def _hash(url):
    return hashlib.md5((url or "").encode()).hexdigest()[:10]


def _load_feedback():
    if not os.path.exists(FEEDBACK_PATH):
        return []
    rows = []
    with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def _resolve_news(rows):
    """把收藏的 news id 解析成文章特征。"""
    if not os.path.exists(SCORED_PATH):
        return []
    with open(SCORED_PATH, "r", encoding="utf-8") as f:
        news = json.load(f)
    by_hash = {_hash(a.get("url", "")): a for a in news}
    out = []
    for r in rows:
        if r.get("type") != "news":
            continue
        a = by_hash.get(r.get("id", ""))
        if a:
            out.append(a)
    return out


def _resolve_ents(rows):
    if not os.path.exists(ENT_PATH):
        return []
    with open(ENT_PATH, "r", encoding="utf-8") as f:
        ents = json.load(f)
    by_serial = {e.get("serial"): e for e in ents}
    out = []
    for r in rows:
        if r.get("type") != "ent":
            continue
        e = by_serial.get(r.get("id", ""))
        if e:
            out.append(e)
    return out


def run_daily_step():
    rows = _load_feedback()
    if not rows:
        print("[feedback_loop] 无 feedback.jsonl，跳过（空操作）")
        return None

    news = _resolve_news(rows)
    ents = _resolve_ents(rows)

    # 统计偏好
    news_event = Counter(a.get("event_type", "") for a in news)
    news_domain = Counter()
    for a in news:
        for d in (a.get("domains") or []):
            news_domain[d] += 1
    news_region = Counter(a.get("region", "") for a in news)
    novalities = [float(a.get("novelty") or 0) for a in news]
    avg_novel = sum(novalities) / len(novalities) if novalities else 0

    ent_cat = Counter(e.get("category_l1", "") for e in ents)
    ent_region = Counter(e.get("region", "") for e in ents)
    ent_funded = sum(1 for e in ents if (e.get("funding_total") or e.get("funding_latest")))
    ent_ipo = sum(1 for e in ents if _is_ipo(e))

    # —— 安全权重微调建议 ——
    pref = _load_pref()
    cur_weights = pref.get("weights", {k: NEWS_SCORING_DIMS[k]["weight"] for k in NEWS_SCORING_DIMS})
    delta = {}

    # 规则1：收藏的资讯平均反常识度高 -> 微提 novelty 权重（呼应小爽 S3 反常识标准）
    if avg_novel >= 6.5 and "novelty" in cur_weights:
        delta["novelty"] = min(DELTA_CAP, WEIGHT_BOUNDS["novelty"][1] - cur_weights["novelty"])
    # 规则2：收藏里海外企业偏多 -> 微提 cn_fit（以海外为镜）
    overseas_news = news_region.get("海外", 0)
    if overseas_news and overseas_news >= len(news) * 0.6 and "cn_fit" in cur_weights:
        delta["cn_fit"] = min(DELTA_CAP, WEIGHT_BOUNDS["cn_fit"][1] - cur_weights["cn_fit"])

    # 应用并夹紧
    new_weights = dict(cur_weights)
    for k, dv in delta.items():
        if dv and abs(dv) > 0:
            lo, hi = WEIGHT_BOUNDS[k]
            new_weights[k] = round(min(hi, max(lo, cur_weights[k] + dv)), 3)

    # 写回 user_pref.json（带历史留痕）
    pref["weights"] = new_weights
    pref.setdefault("history", [])
    pref["history"].append({
        "favorites": len(rows),
        "news": len(news),
        "ents": len(ents),
        "avg_novelty": round(avg_novel, 2),
        "delta": delta,
    })
    pref["history"] = pref["history"][-10:]  # 仅留最近10次
    with open(PREF_PATH, "w", encoding="utf-8") as f:
        json.dump(pref, f, ensure_ascii=False, indent=2)

    # 生成人读报告
    report = (
        "# 用户偏好反馈报告（L3 外部反馈闭环）\n\n"
        f"- 收藏总数：{len(rows)}（资讯 {len(news)} / 企业 {len(ents)}）\n"
        f"- 收藏资讯平均反常识度：{avg_novel:.1f}\n"
        f"- 资讯事件偏好：{dict(news_event)}\n"
        f"- 资讯地区偏好：{dict(news_region)}\n"
        f"- 企业分类偏好：{dict(ent_cat)}\n"
        f"- 企业中有融资：{ent_funded} / 已IPO：{ent_ipo}\n"
        f"- 本次权重微调：{delta if delta else '无（在阈值内或样本不足）'}\n"
        f"- 当前权重：{new_weights}\n"
    )
    with open(os.path.join(DATA_DIR, "feedback_report.md"), "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[feedback_loop] 收藏={len(rows)} 资讯={len(news)} 企业={len(ents)} "
          f"权重微调={delta if delta else '无'}")
    return pref


def _is_ipo(ent):
    parts = []
    for key in ("funding_latest", "funding_total"):
        blob = ent.get(key) or {}
        if isinstance(blob, dict):
            parts.append(str(blob.get("round", "")))
            parts.append(str(blob.get("display", "")))
        elif isinstance(blob, str):
            parts.append(blob)
    parts.append(ent.get("description", "") or "")
    parts.append(ent.get("desc_cn", "") or "")
    blob = " ".join(parts).lower()
    return any(k in blob for k in ["ipo", "上市", "纳斯达克", "nasdaq", "nyse",
                                    "港股", "主板", "挂牌", "公开募股", "上市公司"])


def _load_pref():
    if os.path.exists(PREF_PATH):
        try:
            with open(PREF_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"weights": {k: NEWS_SCORING_DIMS[k]["weight"] for k in NEWS_SCORING_DIMS}}


if __name__ == "__main__":
    run_daily_step()
