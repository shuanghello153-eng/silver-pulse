# -*- coding: utf-8 -*-
"""
selection/cluster.py — 事件聚类引擎（Loop 方向 1 前置激活）。

对 scored_latest.json 中所有条目做事件聚类：
  1. 主规则：(entity_name, event_type) 精确匹配 → 同簇
  2. 余弦回退：event_type 相同 + title 向量余弦 > CLUSTER_SIM_THRESHOLD → 同簇

输出：
  - 每条资讯的 cluster_id (str) 写回 scored_latest.json
  - is_main: bool (簇内主条目)
  - cluster_size: int (簇大小)

零模型成本，纯关键词 + 数学。
"""
import json
import os
import re
from collections import defaultdict
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCORED_PATH = os.path.join(DATA_DIR, "scored_latest.json")

# 简单分词器（英文空格 + 中文按字切 + 去停用词）
_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "can", "shall",
    "of", "in", "to", "for", "with", "on", "at", "by", "from",
    "as", "into", "through", "during", "before", "after",
    "above", "between", "out", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "just", "and", "but", "if", "or",
    "because", "until", "while", "this", "that", "these", "those",
    "it", "its", "he", "she", "they", "them", "his", "her", "their",
    "what", "which", "who", "whom", "about", "against", "up",
    "的", "了", "在", "是", "和", "与", "或", "对", "为", "中",
    "及", "等", "将", "已", "被", "把", "从", "到", "以", "也",
    "都", "而", "但", "又", "很", "就", "不", "这", "那",
}


def _tokenize(text):
    """简单分词：小写 + 英文拆单词 + 中文单字 + 过滤停用词+短词+纯数字。"""
    if not text:
        return []
    text = text.lower()
    # 提取英文单词
    en_words = re.findall(r"[a-z]{2,}", text)
    # 提取中文单字（保留有意义的）
    cn_chars = [c for c in text if "\u4e00" <= c <= "\u9fff"]
    tokens = [w for w in en_words + cn_chars if w not in _STOP_WORDS and not w.isdigit()]
    return tokens


def _vec(tokens):
    """token 列表 → {token: count} 字典向量。"""
    v = defaultdict(int)
    for t in tokens:
        v[t] += 1
    return dict(v)


def _cosine(va, vb):
    """两个稀疏向量的余弦相似度。"""
    if not va or not vb:
        return 0.0
    all_keys = set(va) | set(vb)
    dot = sum(va.get(k, 0) * vb.get(k, 0) for k in all_keys)
    na = math.sqrt(sum(x * x for x in va.values()))
    nb = math.sqrt(sum(x * x for x in vb.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def run_daily_step(threshold=None):
    """
    聚类全部 scored_latest 条目，写回 cluster_id / is_main / cluster_size。
    """
    try:
        from config import CLUSTER_SIM_THRESHOLD
    except ImportError:
        CLUSTER_SIM_THRESHOLD = 0.82

    if threshold is None:
        threshold = CLUSTER_SIM_THRESHOLD
        # 可选覆盖：threshold_override.json 里的 CLUSTER_SIM_THRESHOLD 字段。
        # 仅当 ENABLE_AUTO_THRESHOLD 开启（Loop 进化步已激活）时生效，
        # 护栏：绝不默认自动改阈值（与 config.ENABLE_AUTO_THRESHOLD 约定一致）。
        # 离线回测请直接用 run_daily_step(threshold=...) 传参，无需改此处。
        try:
            from config import ENABLE_AUTO_THRESHOLD
            if ENABLE_AUTO_THRESHOLD:
                ov_path = os.path.join(DATA_DIR, "threshold_override.json")
                if os.path.exists(ov_path):
                    ov = json.load(open(ov_path, "r", encoding="utf-8"))
                    if "CLUSTER_SIM_THRESHOLD" in ov:
                        threshold = float(ov["CLUSTER_SIM_THRESHOLD"])
        except Exception:
            pass

    if not os.path.exists(SCORED_PATH):
        print("[cluster] scored_latest.json 不存在，跳过")
        return

    with open(SCORED_PATH, "r", encoding="utf-8") as f:
        arts = json.load(f)

    n = len(arts)
    print("[cluster] 开始聚类 %d 条资讯，阈值 %.2f..." % (n, threshold))

    # 预处理：分词 + 向量
    for art in arts:
        blob = (art.get("title_cn") or "") + " " + (art.get("title") or "")
        art["_tokens"] = _tokenize(blob)
        art["_vec"] = _vec(art["_tokens"])

    # ---- Step 1: 主规则聚类 (entity_name + event_type) ----
    clusters = {}  # key -> [indices]
    entity_map = defaultdict(list)  # (entity_norm, event_type) -> [idx]

    for i, art in enumerate(arts):
        entity = (art.get("entity_name") or "").strip().lower()
        etype = (art.get("event_type") or "").strip()
        key = (entity, etype)
        if entity and etype:
            entity_map[key].append(i)

    # 把主规则匹配的归簇
    cluster_id_counter = 0
    idx_to_cluster = {}
    for key, indices in entity_map.items():
        cid = f"C{cluster_id_counter:04d}"
        cluster_id_counter += 1
        for idx in indices:
            idx_to_cluster[idx] = cid
            clusters.setdefault(cid, []).append(idx)

    # ---- Step 2: 余弦回退（未归入任何簇的条目）----
    unassigned = [i for i in range(n) if i not in idx_to_cluster]
    # 按 event_type 分组后做余弦比较
    type_groups = defaultdict(list)
    for i in unassigned:
        etype = (arts[i].get("event_type") or "").strip()
        if etype:
            type_groups[etype].append(i)
        else:
            # 无 event_type 的单独成簇
            cid = f"C{cluster_id_counter:04d}"
            cluster_id_counter += 1
            idx_to_cluster[i] = cid
            clusters.setdefault(cid, []).append(i)

    for etype, group_indices in type_groups.items():
        for i in group_indices:
            if i in idx_to_cluster:
                continue
            vi = arts[i]["_vec"]
            matched = False
            for j in group_indices:
                if i == j or j not in idx_to_cluster:
                    continue
                sim = _cosine(vi, arts[j]["_vec"])
                if sim >= threshold:
                    # 归入 j 所在簇
                    cid = idx_to_cluster[j]
                    idx_to_cluster[i] = cid
                    clusters[cid].append(i)
                    matched = True
                    break  # 只归第一个匹配簇
            if not matched:
                # 新簇
                cid = f"C{cluster_id_counter:04d}"
                cluster_id_counter += 1
                idx_to_cluster[i] = cid
                clusters.setdefault(cid, []).append(i)

    # 处理完全没分类到的（理论上不会发生）
    for i in range(n):
        if i not in idx_to_cluster:
            cid = f"C{cluster_id_counter:04d}"
            cluster_id_counter += 1
            idx_to_cluster[i] = cid
            clusters.setdefault(cid, []).append(i)

    # ---- 写回结果 ----
    total_clusters = len(clusters)
    multi_clusters = sum(1 for c in clusters.values() if len(c) > 1)

    for i, art in enumerate(arts):
        cid = idx_to_cluster[i]
        members = clusters[cid]
        art["cluster_id"] = cid
        art["is_main"] = (i == members[0])  # 第一条为主条
        art["cluster_size"] = len(members)
        # 清理临时字段
        art.pop("_tokens", None)
        art.pop("_vec", None)

    with open(SCORED_PATH, "w", encoding="utf-8") as f:
        json.dump(arts, f, ensure_ascii=False, indent=2)

    print(
        "[cluster] 完成：%d 条 → %d 簇（多成员簇 %d，孤立 %d）"
        % (n, total_clusters, multi_clusters, total_clusters - multi_clusters)
    )


if __name__ == "__main__":
    run_daily_step()
