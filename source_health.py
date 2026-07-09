# -*- coding: utf-8 -*-
"""
source_health.py — 源健康监控 + 增量跨周去重（零模型成本）。

两个职责：
  (A) 增量跨周去重：
      - 持久化每源「已见 URL 集合 + 上次采集日期」到 data/seen_urls.json
      - collector 在抓取时用 seen 集合过滤掉跨周重复 URL（保留归档，不删数据）
      - Google News 查询窗口由写死的 when:7d 改为「增量窗口」：
        活跃源用 after:<上次文章日期-1d>，沉默/首次源用 when:14d 兜底
  (B) 源健康监控：
      - 每次采集后统计每源本次产出（raw / 跨周去重跳过 / 新入）
      - 连续 N 周（默认 3 周）0 产出 → 标记 suspected_dead（疑似失效）并告警
      - 连续 N 周抓取异常（超时/403/空响应）→ 标记 dead，建议降权跳过
      - 输出 data/health_report.json + data/SOURCE_HEALTH.md + 控制台摘要

全部在 build time 运行，结果落 JSON/MD，不碰静态产物、不阻断主流程。
"""
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

SEEN_PATH = os.path.join(DATA_DIR, "seen_urls.json")      # 增量去重状态
HEALTH_PATH = os.path.join(DATA_DIR, "source_health.json")  # 源健康持久状态
REPORT_PATH = os.path.join(DATA_DIR, "health_report.json")  # 本次健康报告
REPORT_MD = os.path.join(DATA_DIR, "SOURCE_HEALTH.md")    # 可读摘要

# 判定阈值（config 化前先用常量，零成本、易调）
SUSPECTED_DEAD_WEEKS = 3   # 连续 N 周 0 产出 → 疑似失效
DEAD_ERROR_WEEKS = 2         # 连续 N 周抓取异常 → 视为 dead（建议跳过）


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------
def url_hash(url):
    """与 collector.url_hash 同算法，避免循环 import（md5 前 12 位）。"""
    import hashlib
    return hashlib.md5(url.encode()).hexdigest()[:12]


def _load(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _today():
    return datetime.now().strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# (A) 增量跨周去重状态
# ---------------------------------------------------------------------------
def load_seen_state():
    s = _load(SEEN_PATH, {"sources": {}, "updated": None})
    if "sources" not in s:
        s["sources"] = {}
    return s


def save_seen_state(state):
    state["updated"] = datetime.now(timezone.utc).isoformat()
    _save(SEEN_PATH, state)
    return state


def update_seen_state(state, source_id, source_config, new_articles,
                      run_raw, run_dup):
    """把本次增量新抓到的 URL 写入 seen 集合，并更新上次文章日期/运行日期。

    不删除任何旧数据 —— seen 只存 hash+日期，原始文章仍在 raw_*.json / scored_latest.json。
    """
    today = _today()
    src = state["sources"].get(source_id, {})
    seen = src.setdefault("seen", {})
    max_date = src.get("last_article_date")
    for a in new_articles:
        h = url_hash(a.get("url", ""))
        if h:
            seen[h] = today
        d = a.get("date", "")
        if d and len(d) >= 10:
            if max_date is None or d > max_date:
                max_date = d
    src["last_run"] = today
    src["last_article_date"] = max_date or src.get("last_article_date")
    src["total_raw"] = int(src.get("total_raw", 0)) + run_raw
    src["total_dup"] = int(src.get("total_dup", 0)) + run_dup
    state["sources"][source_id] = src
    return state


# ---------------------------------------------------------------------------
# (B) 源健康状态
# ---------------------------------------------------------------------------
def load_health():
    return _load(HEALTH_PATH, {})


def save_health(health):
    _save(HEALTH_PATH, health)
    return health


def record_source_run(source_id, source_config, raw=0, dup=0,
                      new_pre=0, new=0, error=None):
    """每源每次采集后调用：更新健康状态并写回 source_health.json。"""
    health = load_health()
    today = _today()
    rec = health.get(source_id, {
        "name": source_config.get("name", source_id),
        "tier": source_config.get("tier"),
        "region": source_config.get("region"),
        "first_seen": today,
        "total_runs": 0, "total_raw": 0, "total_new": 0,
        "consecutive_zero": 0, "consecutive_error": 0,
        "last_run": None, "last_ok_run": None,
        "last_raw": 0, "last_new": 0, "last_dup": 0,
        "status": "unknown", "action": "monitor", "last_error": None,
    })
    rec["name"] = source_config.get("name", source_id)
    rec["tier"] = source_config.get("tier")
    rec["region"] = source_config.get("region")
    rec["total_runs"] += 1
    rec["total_raw"] += raw
    rec["total_new"] += new
    rec["last_run"] = today
    rec["last_raw"] = raw
    rec["last_new"] = new
    rec["last_dup"] = dup

    if error:
        rec["consecutive_error"] += 1
        rec["last_error"] = str(error)[:200]
    else:
        rec["consecutive_error"] = 0
        rec["last_error"] = None

    if raw == 0 and not error:
        rec["consecutive_zero"] += 1
    else:
        rec["consecutive_zero"] = 0

    if raw > 0 or new > 0:
        rec["last_ok_run"] = today

    # 状态分级（软降/告警，不自动改生产权重，遵循护栏）
    if rec["consecutive_error"] >= DEAD_ERROR_WEEKS:
        rec["status"] = "dead"
        rec["action"] = "skip_collect(downweight)"
    elif rec["consecutive_zero"] >= SUSPECTED_DEAD_WEEKS:
        rec["status"] = "suspected_dead"
        rec["action"] = "alert+manual_review"
    elif rec["consecutive_zero"] >= 1 or rec["consecutive_error"] >= 1:
        rec["status"] = "watch"
        rec["action"] = "monitor"
    else:
        rec["status"] = "healthy"
        rec["action"] = "normal"

    health[source_id] = rec
    save_health(health)
    return rec


# ---------------------------------------------------------------------------
# 健康报告
# ---------------------------------------------------------------------------
def _latest_raw_path():
    try:
        files = [f for f in os.listdir(DATA_DIR)
                 if re.match(r"raw_\d{8}\.json$", f)]
        if not files:
            return None
        files.sort()
        return os.path.join(DATA_DIR, files[-1])
    except Exception:
        return None


def _relevant_per_source(raw_path):
    out = Counter()
    if not raw_path or not os.path.exists(raw_path):
        return out
    arts = _load(raw_path, [])
    for a in arts:
        sid = a.get("source_id") or ""
        if sid:
            out[sid] += 1
    return out


def seed_from_history():
    """首次/演示用：从采集日志回填 source_health.json，暴露长期 0 产出的源。

    采用 data/run_logs/collector_*.log 里的【真实抓取量】（"Collected N
    articles" 是采集期看到的原始条数，而非过相关性后的 raw_*.json），因此
    不会把「活着但相关性低」的源误判为失效。仅当某源在全部可用的日志里
    原始抓取量都为 0（挂掉/被墙/改版），才标记为 suspected_dead。

    全 manual 频道（intentionally 不自动采集）的源不纳入失效判定。
    """
    from config import SOURCES
    log_dir = os.path.join(DATA_DIR, "run_logs")
    logs = sorted(
        f for f in os.listdir(log_dir)
        if re.match(r"collector_\d{8}\.log$", f)
    ) if os.path.isdir(log_dir) else []
    if not logs:
        return 0

    # name -> source_id（反向索引）
    name2id = {v.get("name"): k for k, v in SOURCES.items() if v.get("name")}

    # 逐日志：每源每日期的原始抓取量。
    # 注意：collector 对「抓到 0 条」打的是 "[NAME] No entries found"，
    # 对「抓到 N>0 条」打的是 "[NAME] Collected N articles"。两种都要解析，
    # 才能区分「被抓取但 0 产出」与「本次运行根本没轮到它（中断/部分运行）」。
    per_date = {}   # date -> {sid: raw}（只在真正被抓取的源有记录）
    for f in logs:
        date = f[10:18]
        path = os.path.join(log_dir, f)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except Exception:
            continue
        cur = {}
        for m in re.finditer(r"\[(.+?)\] Collected (\d+) articles", text):
            sid = name2id.get(m.group(1))
            if sid:
                cur[sid] = cur.get(sid, 0) + int(m.group(2))
        for m in re.finditer(r"\[(.+?)\] No entries found", text):
            sid = name2id.get(m.group(1))
            if sid and sid not in cur:
                cur[sid] = 0   # 被抓取但 0 产出（不覆盖已统计到的 >0）
        if cur:
            per_date[date] = cur
    if not per_date:
        return 0

    dates = sorted(per_date)
    health = load_health()
    for sid, cfg in SOURCES.items():
        if sid in health and health[sid].get("total_runs", 0) > 0:
            continue  # 已有真实运行记录，不覆盖
        # 全 manual 频道 → 不自动采集，跳过失效判定
        chs = cfg.get("l2_channels", [])
        if chs and all(c[2] == "manual" for c in chs):
            continue
        # 只统计「本次运行真正轮到该源」的日志；没轮到的（部分/中断运行）不计为 0
        present = [(d, per_date[d].get(sid)) for d in dates if sid in per_date[d]]
        if not present:
            continue  # 所有可用日志里都没抓到它（数据不足），留 unknown
        counts = [c for _, c in present]
        cz = sum(1 for c in counts if c == 0)
        last_raw = counts[-1]
        last_ok = next((d for d, c in present if c > 0), None)
        # 状态分级（仅按真实抓取量 0 判定，避免误杀低相关性源）
        # 生产规则：连续 ≥N 周 0 产出 → suspected_dead。
        # 回填特例：可用日志不足 N 周、但该源在「所有被抓到的运行」里都 0，
        #   也标红（至少 2 次真实抓取都为 0），避免真·失效源被漏掉。
        all_zero = (len(present) >= 2 and all(c == 0 for c in counts))
        rec = health.get(sid, {
            "name": cfg.get("name", sid), "tier": cfg.get("tier"),
            "region": cfg.get("region"), "first_seen": dates[0],
            "total_runs": len(present), "total_raw": sum(counts),
            "total_new": sum(counts), "last_run": present[-1][0],
            "last_ok_run": last_ok, "last_raw": last_raw,
            "last_new": last_raw, "last_dup": 0,
            "status": "unknown", "action": "monitor", "last_error": None,
        })
        rec["total_runs"] = len(present)
        rec["total_raw"] = sum(counts)
        rec["last_run"] = present[-1][0]
        rec["last_raw"] = last_raw
        rec["last_new"] = last_raw
        rec["last_ok_run"] = last_ok
        rec["consecutive_zero"] = cz
        if cz >= SUSPECTED_DEAD_WEEKS or all_zero:
            rec["status"] = "suspected_dead"
            rec["action"] = "alert+manual_review"
        elif cz >= 1:
            rec["status"] = "watch"
            rec["action"] = "monitor"
        else:
            rec["status"] = "healthy"
            rec["action"] = "normal"
        health[sid] = rec
    save_health(health)
    return len(dates)


def build_report(raw_path=None):
    """汇总健康状态 + 去重统计，产出 health_report.json / SOURCE_HEALTH.md / 控制台摘要。

    返回报告 dict。失败不抛异常（由调用方 try 包裹）。
    """
    if raw_path is None:
        raw_path = _latest_raw_path()
    health = load_health()
    seen_state = load_seen_state()
    rel = _relevant_per_source(raw_path)

    # 用 config 初始化未收录的源，保证报告覆盖全部配置源
    from config import SOURCES
    for sid, cfg in SOURCES.items():
        if sid not in health:
            chs = cfg.get("l2_channels", [])
            all_manual = bool(chs) and all(c[2] == "manual" for c in chs)
            health[sid] = {
                "name": cfg.get("name", sid), "tier": cfg.get("tier"),
                "region": cfg.get("region"), "first_seen": None,
                "total_runs": 0, "total_raw": 0, "total_new": 0,
                "consecutive_zero": 0, "consecutive_error": 0,
                "last_run": None, "last_ok_run": None,
                "last_raw": 0, "last_new": 0, "last_dup": 0,
                "status": "manual" if all_manual else "unknown",
                "action": "skip(auto)", "last_error": None,
            }

    total_src = len(health)
    zero_src = [s for s, r in health.items()
                if r.get("last_raw", 0) == 0 and r.get("status") != "manual"]
    suspected = [s for s, r in health.items() if r.get("status") == "suspected_dead"]
    dead = [s for s, r in health.items() if r.get("status") == "dead"]

    # 跨周去重累计：从 seen 状态算（全量抓取中已被 seen 过滤掉的重复占比）
    tot_raw = sum(int(s.get("total_raw", 0)) for s in seen_state.get("sources", {}).values())
    tot_dup = sum(int(s.get("total_dup", 0)) for s in seen_state.get("sources", {}).values())
    dup_rate = (tot_dup / tot_raw * 100.0) if tot_raw else 0.0

    per_source = []
    for sid, r in sorted(health.items(), key=lambda x: -x[1].get("last_raw", 0)):
        per_source.append({
            "source_id": sid,
            "name": r.get("name"),
            "tier": r.get("tier"),
            "region": r.get("region"),
            "last_raw": r.get("last_raw", 0),
            "last_new": r.get("last_new", 0),
            "last_dup": r.get("last_dup", 0),
            "relevant": rel.get(sid, 0),
            "consecutive_zero": r.get("consecutive_zero", 0),
            "consecutive_error": r.get("consecutive_error", 0),
            "status": r.get("status"),
            "action": r.get("action"),
            "last_error": r.get("last_error"),
        })

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_snapshot": os.path.basename(raw_path) if raw_path else None,
        "totals": {
            "sources": total_src,
            "with_output": total_src - len(zero_src),
            "zero_output": len(zero_src),
            "suspected_dead": len(suspected),
            "dead": len(dead),
            "dup_rate_pct": round(dup_rate, 1),
        },
        "suspected_dead": [{"source_id": s, "name": health[s].get("name")} for s in suspected],
        "dead": [{"source_id": s, "name": health[s].get("name")} for s in dead],
        "zero_output": [{"source_id": s, "name": health[s].get("name")} for s in zero_src],
        "per_source": per_source,
    }
    _save(REPORT_PATH, report)
    _write_md(report)
    _print_summary(report)
    return report


def _write_md(report):
    t = report["totals"]
    lines = [
        "# Silver Pulse · 源健康监控报告",
        "",
        "> 生成时间（UTC）：%s" % report["generated_at"],
        "> 数据快照：%s" % (report.get("raw_snapshot") or "（无）"),
        "",
        "---",
        "",
        "## 总览",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        "| 监控源总数 | %d |" % t["sources"],
        "| 本周有产出 | %d |" % t["with_output"],
        "| 本周 0 产出 | %d |" % t["zero_output"],
        "| 疑似失效(连续≥3周0产出) | **%d** |" % t["suspected_dead"],
        "| 抓取异常(dead) | %d |" % t["dead"],
        "| 跨周去重率(累计) | %.1f%% |" % t["dup_rate_pct"],
        "",
    ]
    if report["suspected_dead"]:
        lines.append("## ⚠ 疑似失效源（建议人工复核 / 换源）")
        lines.append("")
        for s in report["suspected_dead"]:
            lines.append("- **%s**（%s）" % (s["name"], s["source_id"]))
        lines.append("")
    if report["dead"]:
        lines.append("## ⛔ 抓取异常源（建议降权跳过）")
        lines.append("")
        for s in report["dead"]:
            lines.append("- **%s**（%s）" % (s["name"], s["source_id"]))
        lines.append("")
    lines.append("## 各源明细")
    lines.append("")
    lines.append("| 源 | 档位 | 区域 | 本周raw | 新入 | 跨周去重跳过 | 相关产出 | 连续0周 | 状态 |")
    lines.append("|----|------|------|--------|------|--------------|----------|---------|------|")
    for p in report["per_source"]:
        lines.append("| %s | T%s | %s | %d | %d | %d | %d | %d | %s |" % (
            p["name"], p["tier"], p["region"], p["last_raw"], p["last_new"],
            p["last_dup"], p["relevant"], p["consecutive_zero"], p["status"],
        ))
    lines.append("")
    lines.append("---")
    lines.append("*本报告由 `source_health.py` 自动生成，零模型成本。*")
    try:
        with open(REPORT_MD, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception:
        pass


def _print_summary(report):
    t = report["totals"]
    print("[source_health] 源健康报告: 监控%d源 / 有产出%d / 0产出%d / "
          "疑似失效%d / dead%d / 跨周去重率%.1f%%" % (
              t["sources"], t["with_output"], t["zero_output"],
              t["suspected_dead"], t["dead"], t["dup_rate_pct"]))
    if report["suspected_dead"]:
        names = ", ".join(s["name"] for s in report["suspected_dead"][:8])
        more = " …" if len(report["suspected_dead"]) > 8 else ""
        print("[source_health] ⚠ 疑似失效源: %s%s" % (names, more))
    if report["dead"]:
        names = ", ".join(s["name"] for s in report["dead"][:8])
        print("[source_health] ⛔ dead源: %s" % names)


# ---------------------------------------------------------------------------
# 独立运行入口：直接跑 `python source_health.py` 也能出报告（用最新快照）
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    n = seed_from_history()
    if n:
        print("[source_health] 已用 %d 个历史快照回填健康状态" % n)
    rep = build_report()
    print("[source_health] 报告已写入 %s" % REPORT_PATH)
