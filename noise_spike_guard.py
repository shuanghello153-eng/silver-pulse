# -*- coding: utf-8 -*-
"""
noise_spike_guard.py — Loop Engineering L2 进化层（写查分离中的「进化」角色）。

loop_audit.py 是「查」（发现问题并报告），本模块是「进化」（保守修正）。

检测三类异常（与昨日基线对比）：
  1. 噪音 spike：今日噪音数 vs 昨日突增 >50% 且绝对值 > 10
  2. 精选暴跌：今日精选数 vs 昨日 < 50% 且绝对值 < 5
  3. 规则漂移：config.py 修改时间晚于 about.html 生成时间（规则改了但说明页没同步）

保守回调（护栏：零模型成本、绝不改架构、改动前备份 + 留痕）：
  - 噪音 spike 连续 2 天 → 把噪音项中出现频次最高的源域名写入 data/noise_blocklist.json
    （collector.py 下次采集读取并剔除，纯数据文件，不改源码）
  - 改动前自动 git 备份 config.py
  - 所有动作写入 data/pitfalls_log.json，小爽可随时回看/回滚
  - 精选暴跌 / 规则漂移：仅告警，不自动改（需人判断，避免误伤）

基线存储：data/l2_baseline.json（昨日噪音数 / 精选数 / config mtime）
调用：run_daily.py 在 loop_audit 之后调用本模块。
"""
import os
import json
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONFIG_PATH = os.path.join(BASE_DIR, "config.py")
ABOUT_PATH = os.path.join(OUTPUT_DIR, "about.html")
SCORED_PATH = os.path.join(DATA_DIR, "scored_latest.json")
BASELINE_PATH = os.path.join(DATA_DIR, "l2_baseline.json")
BLOCKLIST_PATH = os.path.join(DATA_DIR, "noise_blocklist.json")
PITFALLS_PATH = os.path.join(DATA_DIR, "pitfalls_log.json")

# 阈值
NOISE_SPIKE_RATIO = 1.5      # 今日噪音 > 昨日 × 1.5
NOISE_SPIKE_ABS = 10         # 且绝对值 > 10
CURATED_CRASH_RATIO = 0.5     # 今日精选 < 昨日 × 0.5
CURATED_CRASH_ABS = 5         # 且绝对值 < 5
CONSECUTIVE_DAYS = 2          # 连续几天触发才自动回调


def _load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _load_baseline():
    return _load_json(BASELINE_PATH, {})


def _config_mtime():
    try:
        return os.path.getmtime(CONFIG_PATH)
    except Exception:
        return 0.0


def _about_mtime():
    try:
        return os.path.getmtime(ABOUT_PATH)
    except Exception:
        return 0.0


def _noise_and_curated(scored):
    """统计噪音数与精选数。噪音 = 不通过 is_relevant 闸门的条目。"""
    if not scored:
        return 0, 0
    from collector import is_relevant
    noise = 0
    curated = 0
    noise_sources = []
    for it in scored:
        title = it.get("title", "")
        summary = it.get("summary", "")
        if not is_relevant(title, it.get("entity_name")) and not is_relevant(summary, it.get("entity_name")):
            noise += 1
            src = it.get("source") or it.get("source_name") or ""
            if src:
                noise_sources.append(src)
        if it.get("is_selected") or it.get("curated") or it.get("view") == "curated":
            curated += 1
    return noise, curated, noise_sources


def _log_pitfall(event_type, detail, action="ALERT"):
    log = _load_json(PITFALLS_PATH, [])
    if not isinstance(log, list):
        log = []
    log.append({
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": event_type,
        "action": action,
        "detail": detail,
    })
    log = log[-30:]  # 仅留最近30条
    _save_json(PITFALLS_PATH, log)
    return log


def _backup_config():
    """改动前 git 备份 config.py。"""
    try:
        bak = CONFIG_PATH + ".bak_%s" % datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy2(CONFIG_PATH, bak)
        return bak
    except Exception as e:
        return "BACKUP_FAILED: %s" % e


def _auto_block_noise_domains(noise_sources):
    """连续噪音 spike → 把高频噪音源域名写入 noise_blocklist.json。"""
    from collections import Counter
    cnt = Counter(noise_sources)
    top = [d for d, _ in cnt.most_common(5) if cnt[d] >= 2]  # 至少出现2次的源才封
    if not top:
        return []
    existing = _load_json(BLOCKLIST_PATH, {})
    if not isinstance(existing, dict):
        existing = {}
    domains = set(existing.get("domains", []))
    new = [d for d in top if d not in domains]
    domains.update(top)
    _save_json(BLOCKLIST_PATH, {
        "domains": sorted(domains),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "note": "由 noise_spike_guard 自动封禁的高频噪音源（连续2天 spike）",
    })
    return new


def run_daily_step():
    print("\n=== L2 Noise Spike Guard (进化层) ===")
    scored = _load_json(SCORED_PATH)
    if not scored:
        # scored 可能是 {items: [...]} 结构
        scored = _load_json(SCORED_PATH, {})
        if isinstance(scored, dict):
            scored = scored.get("items", [])

    noise, curated, noise_sources = _noise_and_curated(scored)
    baseline = _load_baseline()

    prev_noise = baseline.get("noise")
    prev_curated = baseline.get("curated")
    prev_spike_days = baseline.get("noise_spike_days", 0)

    alerts = []
    auto_actions = []

    # 1. 噪音 spike
    if prev_noise is not None and prev_noise > 0:
        if noise > prev_noise * NOISE_SPIKE_RATIO and noise > NOISE_SPIKE_ABS:
            alerts.append("噪音 spike：今日 %d > 昨日 %d ×%.1f" % (noise, prev_noise, NOISE_SPIKE_RATIO))
            spike_days = prev_spike_days + 1
            # 连续2天 → 自动回调
            if spike_days >= CONSECUTIVE_DAYS:
                bak = _backup_config()
                added = _auto_block_noise_domains(noise_sources)
                _log_pitfall("noise_spike", "连续%d天 spike，自动封禁噪音源: %s (config备份:%s)" % (spike_days, added, bak), action="AUTO_BLOCK")
                auto_actions.append("自动封禁 %d 个高频噪音源: %s" % (len(added), added))
                spike_days = 0  # 重置
        else:
            spike_days = 0
    else:
        spike_days = 0

    # 2. 精选暴跌
    if prev_curated is not None and prev_curated > 0:
        if curated < prev_curated * CURATED_CRASH_RATIO and curated < CURATED_CRASH_ABS:
            alerts.append("精选暴跌：今日 %d < 昨日 %d ×%.1f" % (curated, prev_curated, CURATED_CRASH_RATIO))
            _log_pitfall("curated_crash", "今日精选 %d vs 昨日 %d" % (curated, prev_curated), action="ALERT")

    # 3. 规则漂移
    if _config_mtime() > _about_mtime() + 5:  # 5秒容差
        alerts.append("规则漂移：config.py 已修改但 about.html 未重新生成")
        _log_pitfall("rule_drift", "config mtime > about mtime", action="ALERT")

    # 更新基线
    _save_json(BASELINE_PATH, {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "noise": noise,
        "curated": curated,
        "noise_spike_days": spike_days,
        "config_mtime": _config_mtime(),
    })

    # 输出
    if alerts:
        print("  ⚠️ 发现 %d 项异常：" % len(alerts))
        for a in alerts:
            print("    - %s" % a)
    if auto_actions:
        print("  🔧 自动回调：")
        for a in auto_actions:
            print("    - %s" % a)
    if not alerts and not auto_actions:
        print("  🟢 无异常，基线已更新 (noise=%d curated=%d)" % (noise, curated))

    return {
        "alerts": len(alerts),
        "auto_actions": len(auto_actions),
        "noise": noise,
        "curated": curated,
    }


if __name__ == "__main__":
    run_daily_step()
