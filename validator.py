#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silver Pulse 银脉 — 每日管线自检 (loop-engineering validator)

每天管线跑完后执行，读取当日数据产物与生成页，做一轮规则自检，
把状态写到项目根目录 STATE.md。

仅使用标准库: json, os, re, datetime, sys

不修改任何其它文件，不触发管线。
"""

import json
import os
import re
import sys
import datetime

# 让同目录下的 config 可被 import
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import config  # noqa: E402

BASE_DIR = _HERE
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SCORED_PATH = os.path.join(DATA_DIR, "scored_latest.json")
ENT_PATH = os.path.join(DATA_DIR, "enterprise", "all_enterprises.json")
ABOUT_PATH = os.path.join(OUTPUT_DIR, "about.html")
STATE_PATH = os.path.join(BASE_DIR, "STATE.md")


def _lower(text):
    """统一小写的辅助函数，匹配前先规整文本。"""
    if text is None:
        return ""
    return str(text).lower()


def _load_json(path):
    """读 JSON；缺失或解析失败都返回 (None, '缺失'/'解析失败')。"""
    if not os.path.exists(path):
        return None, "缺失"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), "ok"
    except Exception as e:  # noqa: BLE001
        return None, "解析失败: %s" % e


def _read_text(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:  # noqa: BLE001
        return None


def _enterprise_names(enterprises):
    """收集企业库里的全部名称 (name + name_cn)。"""
    names = set()
    for e in enterprises or []:
        n = e.get("name")
        if n:
            names.add(str(n).strip())
        nc = e.get("name_cn")
        if nc:
            names.add(str(nc).strip())
    return names


def _has_funding(e):
    """判断企业是否有融资信息；funding_latest 可能是 str 或 dict。"""
    fl = e.get("funding_latest")
    if isinstance(fl, dict):
        fl = fl.get("display") or fl.get("amount") or ""
    fl = str(fl or "").strip()
    return fl != ""


def _read_prev_noise(state_path):
    """从上一版 STATE.md 读出『误入噪音嫌疑』数值，用于反弹检测。"""
    if not os.path.exists(state_path):
        return None
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            for line in f:
                m = re.search(r"误入噪音嫌疑:\s*(\d+)", line)
                if m:
                    return int(m.group(1))
    except Exception:
        pass
    return None


def main():
    """执行全套自检，打印报告并写出 STATE.md。返回 0。"""
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    checks = []  # (label, status, detail)

    # ---- 读取数据 ----
    scored, scored_status = _load_json(SCORED_PATH)
    if scored is None:
        scored = []
    enterprises, ent_status = _load_json(ENT_PATH)
    if enterprises is None:
        enterprises = []

    # ---- 基础计数 ----
    total_scored = len(scored)
    curated_count = sum(
        1
        for it in scored
        if it.get("is_curated") or it.get("is_selected")
    )
    source_counts = {}
    for it in scored:
        s = it.get("source") or "未知"
        source_counts[s] = source_counts.get(s, 0) + 1

    # ---- 噪音嫌疑 ----
    ent_names = _enterprise_names(enterprises)
    weak_kw = getattr(config, "SILVER_WEAK_KEYWORDS", [])
    strong_kw = getattr(config, "SILVER_STRONG_KEYWORDS", [])
    noise_suspects = []
    for it in scored:
        title = _lower(it.get("title"))
        summary = _lower(it.get("summary"))
        text = title + " " + summary
        entity = it.get("entity_name")
        # 命中任一弱词
        hits_weak = any(kw in text for kw in weak_kw)
        if not hits_weak:
            continue
        # 且未命中任何强词
        hits_strong = any(kw in text for kw in strong_kw)
        if hits_strong:
            continue
        # 且主体不在企业库
        if entity and str(entity).strip() in ent_names:
            continue
        noise_suspects.append(it.get("title") or it.get("entity_name") or "(无标题)")

    noise_count = len(noise_suspects)
    noise_sample = noise_suspects[:8]

    # ---- 噪音反弹检测 (L2 自我纠错信号) ----
    prev_noise = _read_prev_noise(STATE_PATH)
    noise_spike = bool(
        prev_noise is not None and noise_count > prev_noise + 30
    )

    # ---- 企业库计数 ----
    enterprise_total = len(enterprises)
    enterprise_with_funding = sum(1 for e in enterprises if _has_funding(e))
    if enterprise_total > 0:
        funding_pct = round(enterprise_with_funding / enterprise_total * 100, 1)
    else:
        funding_pct = 0.0

    # ---- 数据日期 (取 scored 中最大 date) ----
    data_dates = [
        it.get("date") for it in scored if isinstance(it.get("date"), str) and it.get("date")
    ]
    data_date = max(data_dates) if data_dates else "未知"

    # ---- 数据新鲜度 (P4：防止『采集到0条却静默展示旧数据』) ----
    today_str = now.strftime("%Y-%m-%d")
    fresh = (data_date == today_str)

    # ---- about.html 规则漂移检查 ----
    about_text = _read_text(ABOUT_PATH)
    drift_detail_parts = []
    if about_text is None:
        drift_ok = False
        drift_detail_parts.append("about.html 缺失")
    else:
        tl = _lower(about_text)
        c1 = "每日" in about_text
        c2 = "每周一" not in about_text
        c3 = "研究价值" in about_text
        c4 = ("强词" in about_text) or ("两级" in about_text) or ("SILVER_STRONG" in about_text)
        c5 = "评分功能暂停中" not in about_text
        drift_ok = c1 and c2 and c3 and c4 and c5
        drift_detail_parts.append("每日:%s" % ("OK" if c1 else "FAIL"))
        drift_detail_parts.append("非每周一:%s" % ("OK" if c2 else "FAIL"))
        drift_detail_parts.append("研究价值:%s" % ("OK" if c3 else "FAIL"))
        drift_detail_parts.append("两级相关性描述:%s" % ("OK" if c4 else "FAIL"))
        drift_detail_parts.append("评分未暂停:%s" % ("OK" if c5 else "FAIL"))
    drift_detail = " ".join(drift_detail_parts)

    # ---- 状态判定 ----
    if (not drift_ok) or curated_count == 0:
        status = "FAIL"
    elif (not fresh) or noise_spike or noise_count > 0 or funding_pct < 30:
        status = "WARN"
    else:
        status = "OK"

    # ---- 收集各项检查 ----
    checks.append((
        "数据读取",
        "OK" if scored_status == "ok" else "WARN",
        "scored_latest.json: %s | all_enterprises.json: %s" % (scored_status, ent_status),
    ))
    checks.append((
        "资讯总数",
        "OK" if total_scored > 0 else "WARN",
        "total_scored=%d" % total_scored,
    ))
    checks.append((
        "精选数",
        "FAIL" if curated_count == 0 else "OK",
        "curated_count=%d" % curated_count,
    ))
    checks.append((
        "噪音嫌疑",
        "WARN" if noise_count > 0 else "OK",
        "noise_suspects=%d (sample: %s)" % (
            noise_count,
            " | ".join(noise_sample) if noise_sample else "无",
        ),
    ))
    checks.append((
        "企业库融资覆盖",
        "WARN" if (enterprise_total > 0 and funding_pct < 30) else "OK",
        "enterprise_total=%d 有融资=%d (%.1f%%)" % (
            enterprise_total, enterprise_with_funding, funding_pct),
    ))
    checks.append((
        "规则漂移",
        "OK" if drift_ok else "FAIL",
        drift_detail,
    ))
    checks.append((
        "数据新鲜度",
        "OK" if fresh else "WARN",
        "data_date=%s (今日=%s)" % (data_date, today_str),
    ))
    if noise_spike:
        checks.append((
            "噪音反弹",
            "WARN",
            "noise %d > 前次 %d，建议收紧弱词/提高信号门槛" % (noise_count, prev_noise),
        ))

    # 来源分布
    src_line = ", ".join("%s:%d" % (k, v) for k, v in sorted(
        source_counts.items(), key=lambda x: -x[1]))
    if not src_line:
        src_line = "无"

    # ---- 打印报告 ----
    print("=" * 60)
    print("Silver Pulse 银脉 每日自检报告")
    print("更新时间: %s" % now_str)
    print("=" * 60)
    for label, st, detail in checks:
        print("[%s] %s — %s" % (st, label, detail))
    print("-" * 60)
    print("来源分布: %s" % src_line)
    print("数据日期: %s" % data_date)
    print("总状态: %s" % status)
    print("=" * 60)

    # ---- 写出 STATE.md ----
    state_lines = []
    state_lines.append("# Silver Pulse 状态 STATE.md")
    state_lines.append("更新时间: %s" % now_str)
    state_lines.append("数据日期: %s" % data_date)
    state_lines.append("新鲜度: %s (今日=%s)" % ("OK" if fresh else "WARN", today_str))
    if noise_spike:
        state_lines.append("噪音反弹: 是 (%d > 前次 %d)" % (noise_count, prev_noise))
    state_lines.append("资讯总数: %d | 精选数: %d" % (total_scored, curated_count))
    sample_txt = (" (sample: " + " | ".join(noise_sample) + ")") if noise_sample else ""
    state_lines.append("误入噪音嫌疑: %d%s" % (noise_count, sample_txt))
    state_lines.append("企业总数: %d | 有融资: %d (%.1f%%)" % (
        enterprise_total, enterprise_with_funding, funding_pct))
    state_lines.append("规则漂移: %s %s" % ("OK" if drift_ok else "FAIL", drift_detail))
    state_lines.append("状态: %s" % status)
    state_text = "\n".join(state_lines) + "\n"

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        f.write(state_text)

    print("STATE.md 已写入: %s" % STATE_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
