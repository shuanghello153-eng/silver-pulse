# -*- coding: utf-8 -*-
"""
selection/backtest_cluster.py — 聚类阈值回测（离线，不污染生产）

用法: python selection/backtest_cluster.py
在同一份 scored_latest.json 上，临时把 CLUSTER_SIM_THRESHOLD 设为
0.70 / 0.75 / 0.82 三档，分别跑聚类，统计：
  - 每档簇数、多成员簇数、平均簇大小
  - 误合并(不同事件被强行并掉)案例：簇内两两余弦最低相似度过低
  - 漏合并(本应同簇但没并)案例：同 event_type 且相似度>=阈值却分属不同簇
  - 0.82 下被合并进主条的高分"关键但被压低"事件

结果打印 + 写 data/backtest_cluster_result.json（供报告引用）。
"""
import json
import os
import copy
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCORED_PATH = os.path.join(DATA_DIR, "scored_latest.json")
OUT_PATH = os.path.join(DATA_DIR, "backtest_cluster_result.json")

sys.path.insert(0, os.path.join(BASE_DIR, "selection"))
import cluster as cluster_mod  # noqa


def _title(a):
    return (a.get("title_cn") or a.get("title") or "").strip()


def run_threshold(threshold, pristine):
    """在临时副本上跑聚类，返回 (result_list, sim_cache)。"""
    tmp = os.path.join(DATA_DIR, "_tmp_scored_backtest.json")
    json.dump(pristine, open(tmp, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    cluster_mod.SCORED_PATH = tmp
    cluster_mod.run_daily_step(threshold=threshold)
    result = json.load(open(tmp, "r", encoding="utf-8"))
    os.remove(tmp)
    # run_daily_step 会 pop 掉 _vec；按相同顺序从 pristine 重新挂回向量用于分析
    for i, a in enumerate(result):
        a["_vec"] = pristine[i]["_vec"]
    return result


def pairwise_min_sim(members):
    """簇内两两余弦最低相似度（单成员返回 1.0）。"""
    if len(members) < 2:
        return 1.0
    mn = 1.0
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            s = cluster_mod._cosine(members[i]["_vec"], members[j]["_vec"])
            if s < mn:
                mn = s
    return mn


def main():
    pristine = json.load(open(SCORED_PATH, "r", encoding="utf-8"))
    # 预计算向量（复用 cluster 内部逻辑，但不写回）
    for a in pristine:
        blob = (a.get("title_cn") or "") + " " + (a.get("title") or "")
        a["_tokens"] = cluster_mod._tokenize(blob)
        a["_vec"] = cluster_mod._vec(a["_tokens"])

    thresholds = [0.70, 0.75, 0.82]
    report = {"thresholds": {}, "misfire_merge": {}, "miss_merge": {}}

    for thr in thresholds:
        result = run_threshold(thr, copy.deepcopy(pristine))
        # 按 cluster_id 分组
        groups = {}
        for a in result:
            groups.setdefault(a["cluster_id"], []).append(a)
        total = len(groups)
        multi = [g for g in groups.values() if len(g) > 1]
        isolated = total - len(multi)
        sizes = [len(g) for g in groups.values()]
        avg_multi = (sum(len(g) for g in multi) / len(multi)) if multi else 0.0
        max_size = max(sizes) if sizes else 0

        report["thresholds"][str(thr)] = {
            "total_clusters": total,
            "multi_clusters": len(multi),
            "isolated_clusters": isolated,
            "avg_size_multi": round(avg_multi, 2),
            "max_cluster_size": max_size,
            "merge_rate_pct": round(100.0 * len(multi) / total, 1),
        }

        # 误合并：多成员簇内两两最低相似度过低
        danger = []
        for cid, g in groups.items():
            if len(g) < 2:
                continue
            mn = pairwise_min_sim(g)
            if mn < 0.45:  # 低于此值的同簇对，多半是不同事件被链合并掉
                danger.append({
                    "cluster_id": cid,
                    "size": len(g),
                    "min_pairwise_sim": round(mn, 3),
                    "titles": [_title(a) for a in g],
                    "final_scores": [a.get("final_score") for a in g],
                })
        report["misfire_merge"][str(thr)] = danger

        # 漏合并：同 event_type、相似度>=阈值，却分属不同簇
        miss = []
        items = [a for a in result]
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if a["event_type"] != b["event_type"]:
                    continue
                if a["cluster_id"] == b["cluster_id"]:
                    continue
                s = cluster_mod._cosine(a["_vec"], b["_vec"])
                if s >= thr:
                    miss.append({
                        "sim": round(s, 3),
                        "title_a": _title(a),
                        "title_b": _title(b),
                        "event_type": a["event_type"],
                    })
        # 按相似度降序，取 top
        miss.sort(key=lambda x: -x["sim"])
        report["miss_merge"][str(thr)] = miss[:15]

    # 0.82 档：被合并进主条的高分"关键但被压低"事件
    result_082 = run_threshold(0.82, copy.deepcopy(pristine))
    groups = {}
    for a in result_082:
        groups.setdefault(a["cluster_id"], []).append(a)
    suppressed = []
    for cid, g in groups.items():
        if len(g) < 2:
            continue
        # main = members[0]
        main = g[0]
        for a in g[1:]:
            # 非主条且分数明显高于主条 → 被压低
            if (a.get("final_score") or 0) > (main.get("final_score") or 0):
                suppressed.append({
                    "cluster_id": cid,
                    "main_title": _title(main),
                    "main_score": main.get("final_score"),
                    "suppressed_title": _title(a),
                    "suppressed_score": a.get("final_score"),
                    "penalty_applied": 1.5,
                })
    report["suppressed_at_082"] = suppressed

    # 召回增益：在 0.70 / 0.75 合并、但在 0.82 未合并的"同事件"对
    def merged_pairs(result):
        g = {}
        for idx, a in enumerate(result):
            g.setdefault(a["cluster_id"], []).append(idx)
        pairs = set()
        for members in g.values():
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    x, y = sorted((members[i], members[j]))
                    pairs.add((x, y))
        return pairs

    r070 = run_threshold(0.70, copy.deepcopy(pristine))
    r075 = run_threshold(0.75, copy.deepcopy(pristine))
    p082 = merged_pairs(result_082)
    p075 = merged_pairs(r075)
    p070 = merged_pairs(r070)

    def gain_pairs(lower_res, lower_pairs, base_pairs, thr_label):
        out = []
        for (x, y) in lower_pairs - base_pairs:
            a, b = lower_res[x], lower_res[y]
            sim = cluster_mod._cosine(a["_vec"], b["_vec"])
            out.append({
                "sim": round(sim, 3),
                "event_type": a["event_type"],
                "title_a": _title(a),
                "title_b": _title(b),
            })
        out.sort(key=lambda z: -z["sim"])
        return out

    report["recall_gain_075_vs_082"] = gain_pairs(r075, p075, p082, "0.75")
    report["recall_gain_070_vs_082"] = gain_pairs(r070, p070, p082, "0.70")

    # 打印每一档的多成员簇明细（用于人工判断误合并）
    report["multi_clusters_detail"] = {}
    for thr in thresholds:
        res = run_threshold(thr, copy.deepcopy(pristine))
        g = {}
        for a in res:
            g.setdefault(a["cluster_id"], []).append(a)
        detail = []
        for cid, members in g.items():
            if len(members) < 2:
                continue
            sims = []
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    sims.append(round(cluster_mod._cosine(
                        members[i]["_vec"], members[j]["_vec"]), 3))
            detail.append({
                "cluster_id": cid,
                "size": len(members),
                "min_pairwise_sim": min(sims) if sims else 1.0,
                "titles": [_title(m) for m in members],
                "final_scores": [m.get("final_score") for m in members],
            })
        detail.sort(key=lambda z: z["cluster_id"])
        report["multi_clusters_detail"][str(thr)] = detail

    json.dump(report, open(OUT_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # ---- 打印摘要 ----
    print("=" * 70)
    print("聚类阈值回测摘要（数据量=%d 条，entity_name 100%% 为空）" % len(pristine))
    print("=" * 70)
    print("%-6s %8s %8s %10s %12s %10s" %
          ("阈值", "总簇数", "多员簇", "孤立簇", "多员均大小", "最大簇"))
    for thr in thresholds:
        t = report["thresholds"][str(thr)]
        print("%-6.2f %8d %8d %10d %12.2f %10d" % (
            thr, t["total_clusters"], t["multi_clusters"],
            t["isolated_clusters"], t["avg_size_multi"], t["max_cluster_size"]))
    print("-" * 70)
    for thr in thresholds:
        d = report["misfire_merge"][str(thr)]
        m = report["miss_merge"][str(thr)]
        print("[%.2f] 误合并簇=%d  漏合并对=%d" % (thr, len(d), len(m)))
    print("-" * 70)
    print("召回增益（降到该阈值多并掉、0.82 漏并的'同事件'对）：")
    print("  0.75 vs 0.82: %d 对" % len(report["recall_gain_075_vs_082"]))
    print("  0.70 vs 0.82: %d 对" % len(report["recall_gain_070_vs_082"]))
    print("-" * 70)
    print("0.82 下被压低的'关键事件'（非主条且分数>主条）：%d 条" %
          len(suppressed))
    for s in suppressed:
        print("  主条(%.2f): %s" % (s["main_score"], s["main_title"][:40]))
        print("  被压(%.2f): %s" % (s["suppressed_score"], s["suppressed_title"][:40]))
    print("=" * 70)
    print("各档多成员簇明细 + 召回增益见：", OUT_PATH)


if __name__ == "__main__":
    main()
