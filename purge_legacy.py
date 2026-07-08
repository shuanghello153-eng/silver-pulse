#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存量噪音自动复查 (L2 自我纠错 · 防复发)

教训：2026-07-08 发现 173 条 scored 里有 127 条是收紧闸门前漏入的泛科技/融资
噪音（Tripo AI / OpenAI / SK Hynix 等），因相关性闸门只在「采集时」生效，对
已入库的旧数据无效，导致噪音长期堆积。

本模块让闸门「 retroactive（回溯）」生效：每次跑批对 scored_latest.json 存量条目
重过 is_relevant 两级闸门，清掉任何新判定为不相关的旧条目。
- 幂等：每天跑，无噪音则空操作。
- 安全：清理前先按时间戳备份。
- 不依赖网络：纯本地过滤。
"""
import json
import os
import shutil
import sys
import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import config
import collector

SCORED_PATH = os.path.join(config.DATA_DIR, "scored_latest.json")


def run_daily_step():
    if not os.path.exists(SCORED_PATH):
        print("[purge_legacy] scored_latest.json 不存在，跳过")
        return
    with open(SCORED_PATH, "r", encoding="utf-8") as f:
        scored = json.load(f)
    before = len(scored)

    kept = []
    removed = []
    for it in scored:
        title = it.get("title") or ""
        summary = it.get("summary") or ""
        text = f"{title} {summary}"
        entity = it.get("entity_name")
        if collector.is_relevant(text, entity_name=entity):
            kept.append(it)
        else:
            removed.append(it)

    after = len(kept)
    dropped = before - after
    if dropped == 0:
        print("[purge_legacy] 存量无新噪音，无需清理 (共 %d 条)" % before)
        return

    # 备份后写回
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = SCORED_PATH + ".bak_" + ts
    shutil.copy2(SCORED_PATH, bak)
    with open(SCORED_PATH, "w", encoding="utf-8") as f:
        json.dump(kept, f, ensure_ascii=False, indent=2)
    print("[purge_legacy] 自动清理存量噪音 %d 条 (保留 %d)，备份 %s"
          % (dropped, after, os.path.basename(bak)))
    # 列出被清来源，便于观察噪音主要来自哪类信源
    from collections import Counter
    c = Counter(it.get("source", "?") for it in removed)
    top = ", ".join("%s:%d" % (s, n) for s, n in c.most_common(5))
    print("[purge_legacy] 噪音来源 Top5: %s" % top)


if __name__ == "__main__":
    run_daily_step()
