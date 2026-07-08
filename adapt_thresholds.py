# -*- coding: utf-8 -*-
"""
adapt_thresholds.py — Loop 自我进化 · 数据驱动阈值自适应（方向 1，P1）

设计（零模型成本，纯统计 + 文件覆盖层）：
  - 读 data/scored_latest.json 算当日「精选率」(final_score >= 6.0 占比)。
  - 对照 config.SELECT_RATE_TARGET (15%–25%) 目标带：
      精选率 < 下限 → 阈值 -THRESHOLD_DELTA（放宽，多进精选）
      精选率 > 上限 → 阈值 +THRESHOLD_DELTA（收紧，少进精选）
      区间内      → 稳定，不调。
  - 护栏：
      * 仅写入 data/threshold_override.json 覆盖层，绝不直接改 config.py 源码。
      * 默认 config.ENABLE_AUTO_THRESHOLD = False → 只"建议 + 记历史"，不生效。
        置 True 且 reapply_centrality 接入 override 层后，才真正改变线上精选。
      * 每轮只动一档、步长夹紧（THRESHOLD_FLOOR 下限），杜绝阈值漂移失控。
  - 每次运行追加 data/threshold_history.json（供趋势 + 可观测）。

不改动线上行为（flag 默认关），可安全每日运行；owner 拍板后再激活。
"""
import json
import os
from datetime import datetime, timezone, timedelta

import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TZ_SH = timezone(timedelta(hours=8))

SCORED_PATH = os.path.join(DATA_DIR, "scored_latest.json")
OVERRIDE_PATH = os.path.join(DATA_DIR, "threshold_override.json")
HISTORY_PATH = os.path.join(DATA_DIR, "threshold_history.json")


def _load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else []


def compute_select_rate(scored):
    total = len(scored)
    if not total:
        return 0.0, 0, 0
    high = sum(1 for a in scored if float(a.get("final_score", 0)) >= 6.0)
    return round(high / total * 100, 1), high, total


def recommend(thresholds, select_rate, target, delta, floor):
    """返回调整后的 thresholds 副本 + 是否真有改动。"""
    lo, hi = target
    adjusted = {t: dict(v) for t, v in thresholds.items()}
    changed = False
    if select_rate < lo:
        # 精选太少 → 放宽松（减阈）
        for t, tv in adjusted.items():
            for k in ("high", "watch"):
                new = round(tv[k] - delta, 2)
                if new >= floor[k]:
                    tv[k] = new
                    changed = True
    elif select_rate > hi:
        # 精选太多 → 收紧（加阈）
        for t, tv in adjusted.items():
            for k in ("high", "watch"):
                tv[k] = round(tv[k] + delta, 2)
                changed = True
    return adjusted, changed


def run_daily_step():
    print("[adapt_thresholds] 开始阈值自适应分析...")
    scored = _load_json(SCORED_PATH, [])
    select_rate, high, total = compute_select_rate(scored)
    print("[adapt_thresholds] 精选率=%.1f%% (%d/%d)" % (select_rate, high, total))

    base = {t: dict(v) for t, v in config.SELECT_THRESHOLDS.items()}
    adjusted, changed = recommend(
        base, select_rate, config.SELECT_RATE_TARGET,
        config.THRESHOLD_DELTA, config.THRESHOLD_FLOOR,
    )

    override = {
        "SELECT_THRESHOLDS": adjusted,
        "CLUSTER_SIM_THRESHOLD": config.CLUSTER_SIM_THRESHOLD,
        "generated_at": datetime.now(TZ_SH).strftime("%Y-%m-%d %H:%M"),
        "select_rate": select_rate,
        "applied": bool(config.ENABLE_AUTO_THRESHOLD),
        "note": "默认 applied=false（ENABLE_AUTO_THRESHOLD=False）。owner 拍板后激活。",
    }
    # 始终写 override 文件（覆盖层），但 applied 标记反映是否真生效
    with open(OVERRIDE_PATH, "w", encoding="utf-8") as f:
        json.dump(override, f, ensure_ascii=False, indent=2)

    # 追加历史
    hist = _load_json(HISTORY_PATH, [])
    hist.append({
        "date": datetime.now(TZ_SH).strftime("%Y-%m-%d"),
        "select_rate": select_rate,
        "high": high,
        "total": total,
        "delta_applied": bool(config.ENABLE_AUTO_THRESHOLD and changed),
        "applied": bool(config.ENABLE_AUTO_THRESHOLD),
    })
    cutoff = (datetime.now(TZ_SH) - timedelta(days=365)).strftime("%Y-%m-%d")
    hist = [h for h in hist if h["date"] >= cutoff]
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

    if config.ENABLE_AUTO_THRESHOLD and changed:
        print("[adapt_thresholds] 已写入生效 override（精选率 %.1f%% 越界，已 ±%.1f 调整）"
              % (select_rate, config.THRESHOLD_DELTA))
    elif changed:
        print("[adapt_thresholds] 建议微调（精选率 %.1f%% 越界），但 ENABLE_AUTO_THRESHOLD=False → 未生效"
              % select_rate)
    else:
        print("[adapt_thresholds] 精选率 %.1f%% 在目标带内，阈值稳定" % select_rate)
    print("[adapt_thresholds] 进化决策已记入 threshold_history.json / threshold_override.json")
    return {"select_rate": select_rate, "changed": changed,
            "applied": bool(config.ENABLE_AUTO_THRESHOLD)}


if __name__ == "__main__":
    run_daily_step()
