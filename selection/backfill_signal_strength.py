# -*- coding: utf-8 -*-
"""
selection/backfill_signal_strength.py — 回填 signal_strength / signal_breakdown 到 scored_latest.json

背景（2026-07-10，T26 信号阶段收尾）：
  score_and_merge.py 自 2026-07-09 起已对「新采集」条目写入 signal_strength，
  但存量 63 条 scored_latest.json 由更早版本产出，缺该字段（verify 报告 INFO 已指出）。
  本脚本用与 score_and_merge 第152-162行 *完全一致* 的 compute_signal_strength 口径，
  对存量条目做 **加法** 补字段，不动任何其它字段、不改 final_score。

特性：
  - 零模型成本（纯脚本）。
  - 先备份 scored_latest.json（时间戳 bak），失败可回退。
  - 幂等：已含 signal_strength 的条目跳过。
  - 对未来 score_and_merge 运行无害（存量条目保留该字段）。

用法：python -m selection.backfill_signal_strength   （项目根目录执行）
"""
import json
import os
import shutil
import sys
from datetime import datetime

# 允许以模块方式运行：确保项目根在 sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from selection.signal_strength import compute_signal_strength  # noqa: E402
import config  # noqa: E402

SCORED = os.path.join(ROOT, "data", "scored_latest.json")


def _tier_for(item):
    """复刻 score_and_merge 的 tier 取法：source_id→config，否则 item['tier']，否则 2。"""
    src_id = item.get("source_id", "")
    if src_id and getattr(config, "SOURCES", None):
        t = config.SOURCES.get(src_id, {}).get("tier")
        if t is not None:
            return t
    return item.get("tier", 2)


def main():
    if not os.path.exists(SCORED):
        print("[ERR] 找不到", SCORED)
        return 1
    # 备份
    bak = SCORED + ".bak_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(SCORED, bak)
    print("[backup]", bak)

    with open(SCORED, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print("[ERR] scored_latest.json 顶层非 list")
        return 1

    n_add = 0
    n_skip = 0
    for it in data:
        if "signal_strength" in it:
            n_skip += 1
            continue
        tier = _tier_for(it)
        s, bd = compute_signal_strength(
            {
                "title": it.get("title", ""),
                "summary": it.get("summary", ""),
                "date": it.get("date", ""),
            },
            source_tier=tier,
        )
        it["signal_strength"] = s
        it["signal_breakdown"] = bd
        n_add += 1

    with open(SCORED, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[done] 新增 signal_strength: {n_add} 条 | 跳过(已有): {n_skip} | 共 {len(data)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
