# -*- coding: utf-8 -*-
"""
daily_health.py — 每日健康报告（Loop Engineering 可观测性增强 V1）。

在 loop_audit 之后运行，生成：
  data/HEALTH_REPORT.md   — 当日健康快照（人类可读）
  data/health_history.json — 历史趋势（追加数组，供未来 sparkline/折线）

零模型成本，纯统计 + 文件读写。
"""
import json
import os
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

TZ_SH = timezone(timedelta(hours=8))

SCORED_PATH = os.path.join(DATA_DIR, "scored_latest.json")
HEALTH_MD = os.path.join(DATA_DIR, "HEALTH_REPORT.md")
HISTORY_PATH = os.path.join(DATA_DIR, "health_history.json")
ENTERPRISE_PATH = os.path.join(DATA_DIR, "enterprise", "all_enterprises.json")
L2_AUDIT_PATH = os.path.join(DATA_DIR, "L2_AUDIT.md")


def _load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else []


def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compute_metrics():
    """从当前数据文件计算全部指标。"""
    scored = _load_json(SCORED_PATH, [])
    enterprises = _load_json(ENTERPRISE_PATH, [])

    # 基础计数
    total_news = len(scored)
    # 精选（final_score >= 阈值）
    high_count = sum(1 for a in scored if float(a.get("final_score", 0)) >= 6.0)
    watch_count = sum(1 for a in scored if 4.0 <= float(a.get("final_score", 0)) < 6.0)
    noise_count = sum(1 for a in scored if a.get("is_job_spam"))
    manual_count = sum(1 for a in scored if a.get("source") in ("manual", "manual_seed"))

    # 精选率
    select_rate = (high_count / total_news * 100) if total_news else 0

    # 信源分布
    src_counts = {}
    for a in scored:
        s = a.get("source", "unknown")
        src_counts[s] = src_counts.get(s, 0) + 1
    top_sources = sorted(src_counts.items(), key=lambda x: -x[1])[:5]
    bottom_sources = sorted(src_counts.items(), key=lambda x: x[1])[:3]

    # 领域分布
    domain_counts = {}
    for a in scored:
        for d in (a.get("domains") or []):
            domain_counts[d] = domain_counts.get(d, 0) + 1
    top_domains = sorted(domain_counts.items(), key=lambda x: -x[1])[:5]

    # 事件类型分布
    event_counts = {}
    for a in scored:
        e = a.get("event_type", "未知")
        event_counts[e] = event_counts.get(e, 0) + 1

    # 企业库
    ent_total = len(enterprises)
    ent_with_funding = sum(1 for e in enterprises if e.get("funding_latest") and isinstance(e["funding_latest"], dict))

    # 评分分布
    scores = [float(a.get("final_score", 0)) for a in scored]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0

    # 收藏数据
    # feedback.jsonl 由网站「同步云端」写入，这里只检查是否存在和行数
    fb_path = os.path.join(DATA_DIR, "feedback.jsonl")
    fav_count = 0
    if os.path.exists(fb_path):
        with open(fb_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    fav_count += 1

    return {
        "date": datetime.now(TZ_SH).strftime("%Y-%m-%d %H:%M"),
        "news": {
            "total": total_news,
            "high": high_count,
            "watch": watch_count,
            "noise": noise_count,
            "manual": manual_count,
            "select_rate_pct": round(select_rate, 1),
        },
        "scores": {
            "avg": round(avg_score, 2),
            "max": round(max_score, 1),
            "min": round(min_score, 1),
        },
        "top_sources": top_sources,
        "bottom_sources": bottom_sources,
        "top_domains": top_domains,
        "event_types": dict(sorted(event_counts.items(), key=lambda x: -x[1])),
        "enterprise": {
            "total": ent_total,
            "with_funding": ent_with_funding,
        },
        "feedback": {
            "favorites_count": fav_count,
            "loop3_active": fav_count > 0,
        },
    }


def generate_report(m):
    """生成 HEALTH_REPORT.md。"""
    lines = [
        "# Silver Pulse 每日健康报告",
        "",
        f"> 生成时间：{m['date']}（北京时间）",
        "",
        "---",
        "",
        "## 资讯看板",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| 总资讯数 | **{m['news']['total']}** |",
        f"| 精选 (≥6.0) | **{m['news']['high']}** ({m['news']['select_rate_pct']}%) |",
        f"| 观察 (4–5.9) | {m['news']['watch']} |",
        f"| 噪音(已过滤标记) | {m['news']['noise']} |",
        f"| Manual 种子 | {m['news']['manual']} |",
        "",
        "## 评分分布",
        "",
        f"- 平均分：**{m['scores']['avg']}** / 最高：{m['scores']['max']} / 最低：{m['scores']['min']}",
        "",
        "## TOP 5 信源",
        "",
    ]
    for src, cnt in m["top_sources"]:
        lines.append(f"- **{src}**：{cnt} 条")
    lines.append("")
    lines.append("## 事件类型分布")
    lines.append("")
    for evt, cnt in list(m["event_types"].items())[:8]:
        lines.append(f"- **{evt}**：{cnt}")
    lines.append("")
    lines.append("## 企业库")
    lines.append("")
    lines.append(
        f"- 总数：**{m['enterprise']['total']} 家** / 有融资信息：{m['enterprise']['with_funding']} 家"
    )
    lines.append("")
    lines.append("## 反馈闭环状态")
    lines.append("")
    if m["feedback"]["loop3_active"]:
        lines.append(
            f"- ✅ L3 反馈回灌 **已激活**：收藏 {m['feedback']['favorites_count']} 条"
        )
    else:
        lines.append("- ⏸ L3 反馈回灌待激活（需在网站配置 Token → 同步云端）")
    lines.append("")
    lines.append("---")
    lines.append("*本报告由 `daily_health.py` 自动生成，零模型成本。*")
    return "\n".join(lines)


def append_history(m):
    """追加一条到 health_history.json（保持数组 ≤ 90 天）。"""
    history = _load_json(HISTORY_PATH, [])
    history.append({
        "date": m["date"],
        "total": m["news"]["total"],
        "high": m["news"]["high"],
        "select_rate": m["news"]["select_rate_pct"],
        "avg_score": m["scores"]["avg"],
        "fav_count": m["feedback"]["favorites_count"],
    })
    # 只保留最近 90 天
    cutoff = (datetime.now(TZ_SH) - timedelta(days=90)).strftime("%Y-%m-%d")
    history = [h for h in history if h["date"] >= cutoff]
    _save_json(HISTORY_PATH, history)


def run_daily_step():
    print("[daily_health] 开始计算每日健康指标...")
    try:
        m = compute_metrics()
    except Exception as e:
        print("[daily_health] 指标计算失败: %s" % e)
        return

    report = generate_report(m)
    with open(HEALTH_MD, "w", encoding="utf-8") as f:
        f.write(report)
    print("[daily_health] %s -> %s (%d bytes)" % (HEALTH_MD, len(report), len(report.encode())))

    append_history(m)
    print(
        "[daily_health] 完成: 资讯%d/精选%d(%.1f%%)/均分%.1f/收藏%d条/L3=%s"
        % (
            m["news"]["total"],
            m["news"]["high"],
            m["news"]["select_rate_pct"],
            m["scores"]["avg"],
            m["feedback"]["favorites_count"],
            "激活" if m["feedback"]["loop3_active"] else "待激活",
        )
    )


if __name__ == "__main__":
    run_daily_step()
