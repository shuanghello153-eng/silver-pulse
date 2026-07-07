# -*- coding: utf-8 -*-
"""
Silver Pulse 自我迭代闭环 (P2)
================================
让选题引擎能"自我审视、持续进化"，而不是做完就放着。

组成:
  1. feedback.jsonl  —— 小爽/另一种子对每条精选的判读反馈
       每行一条 JSON: {"date":"2026-07-07","item_id":"<url或标题hash>",
                        "tier":1|2|3,"verdict":"hit"|"miss"|"partial",
                        "note":"为什么准/不准"}
  2. backtest.py     —— 读取 scored_latest.json + feedback.jsonl，
       - 统计当前各层级精选/观察分布
       - 用反馈计算各层级命中率
       - 给出阈值调参建议 (命中率低→收紧, 高→放宽召回)
       - 模拟阈值变动对精选数量的影响 (回测)

用法:
  python backtest.py            # 打印分布 + 回测报告
  (日常: 小爽在 feedback.jsonl 追加反馈后跑一次，据建议调 config.SELECT_THRESHOLDS)

设计原则: 终分/精选/聚类 仍 100% 代码算 (铁律不变)；本脚本只"建议"阈值，
不替代评分逻辑。阈值调整需人工确认后写入 config.py。
"""
import json
import os
from collections import defaultdict

from config import SELECT_THRESHOLDS, SOURCE_NAME_TO_TIER

BASE = os.path.dirname(os.path.abspath(__file__))
SCORED = os.path.join(BASE, "data", "scored_latest.json")
FEEDBACK = os.path.join(BASE, "data", "feedback.jsonl")


def load_articles():
    return json.load(open(SCORED, encoding="utf-8"))


def tier_of(art):
    return SOURCE_NAME_TO_TIER.get(art.get("source"), 2)


def selection_stats(articles):
    stats = defaultdict(lambda: {"total": 0, "high": 0, "watch": 0})
    for a in articles:
        t = tier_of(a)
        fs = a.get("final_score") or 0
        th = SELECT_THRESHOLDS[t]
        stats[t]["total"] += 1
        if fs >= th["high"]:
            stats[t]["high"] += 1
        elif fs >= th["watch"]:
            stats[t]["watch"] += 1
    return stats


def simulate(articles, override):
    counts = defaultdict(int)
    for a in articles:
        t = tier_of(a)
        fs = a.get("final_score") or 0
        th = override.get(t, SELECT_THRESHOLDS[t])
        hi = th[0] if isinstance(th, tuple) else th["high"]
        if fs >= hi:
            counts[t] += 1
    return counts


def load_feedback():
    if not os.path.exists(FEEDBACK):
        return []
    out = []
    for line in open(FEEDBACK, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def main():
    arts = load_articles()
    stats = selection_stats(arts)
    print("=== 当前精选分布 (按信源层级) ===")
    tot_high = 0
    for t in sorted(stats):
        s = stats[t]
        tot_high += s["high"]
        print("  T%d: 总%d | 精选(high)%d | 观察(watch)%d | 阈值 high≥%.1f / watch≥%.1f"
              % (t, s["total"], s["high"], s["watch"],
                 SELECT_THRESHOLDS[t]["high"], SELECT_THRESHOLDS[t]["watch"]))
    print("  精选合计: %d 条" % tot_high)

    fb = load_feedback()
    if fb:
        per = defaultdict(lambda: {"hit": 0, "miss": 0, "partial": 0})
        for f in fb:
            per[f.get("tier")][f.get("verdict", "partial")] += 1
        print("\n=== 反馈命中率 (按层级) ===")
        for t, v in sorted(per.items()):
            n = v["hit"] + v["miss"] + v["partial"]
            if n:
                print("  T%s: n=%d 命中率=%.0f%%" % (t, n, 100 * v["hit"] / n))
        print("\n=== 阈值调参建议 ===")
        for t, v in sorted(per.items()):
            n = v["hit"] + v["miss"] + v["partial"]
            if n >= 5:
                prec = v["hit"] / n
                cur = SELECT_THRESHOLDS[int(t)]["high"] if isinstance(t, int) else SELECT_THRESHOLDS[t]["high"]
                if prec < 0.5:
                    print("  T%s: 命中率%.0f%%偏低 → 建议 high 阈值 %.1f→%.1f (收紧)" % (t, 100 * prec, cur, cur + 0.5))
                elif prec > 0.85:
                    print("  T%s: 命中率%.0f%%较高 → 可考虑 high 阈值 %.1f→%.1f (放宽召回)" % (t, 100 * prec, cur, max(0.0, cur - 0.3)))
    else:
        print("\n(暂无反馈数据 feedback.jsonl 为空 — 小爽追加判读后重跑本脚本即可回测)")

    print("\n=== 阈值回测模拟 (全部 high+0.5) ===")
    ov = {t: (SELECT_THRESHOLDS[t]["high"] + 0.5, SELECT_THRESHOLDS[t]["watch"] + 0.5)
          for t in SELECT_THRESHOLDS}
    c = simulate(arts, ov)
    print("  精选数变化:", dict(sorted(c.items())))


if __name__ == "__main__":
    main()
