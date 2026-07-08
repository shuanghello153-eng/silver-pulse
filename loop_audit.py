# -*- coding: utf-8 -*-
"""
L2 Quality Audit Module — Loop Engineering Layer 2.

Every daily pipeline run, this module automatically inspects:
1. HTML structural health (empty blocks, missing elements, oversized blocks)
2. Data quality (noise rate, selected rate, freshness)
3. UI consistency across 3 pages (sidebar order, filter style, card style)
4. Known-issue regression (noise stacking, deploy failures, score anomalies)

Outputs: data/L2_AUDIT.md (human-readable report) + console summary.
Integrated into run_daily.py after validator, before deploy.
"""
import os
import json
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
AUDIT_PATH = os.path.join(DATA_DIR, "L2_AUDIT.md")

# Known issues to track (regression detection)
KNOWN_ISSUES = [
    {
        "id": "noise_stacking",
        "name": "噪音堆积（旧数据漏网）",
        "check": lambda issues: any(i["severity"] == "CRITICAL" and "noise" in i.get("tags", []) for i in issues),
        "description": "噪音数 > 30 视为堆积，需要 purge_legacy 清理",
    },
    {
        "id": "empty_radar",
        "name": "选题雷达空壳（已移除，验证不残留）",
        "check": lambda issues: any("radar-block" in i.get("detail", "") for i in issues),
        "description": "radar-block 已删除，如果 HTML 中仍存在则为回归",
    },
    {
        "id": "select_broken",
        "name": "企业库标签下拉残留（已改胶囊）",
        "check": lambda issues: any("tag-select" in i.get("detail", "") for i in issues),
        "description": "标签 select 已改为 pill 按钮，如果残留则为回归",
    },
    {
        "id": "tier_filter_residual",
        "name": "层级/特色筛选残留（已删除）",
        "check": lambda issues: any("data-group=\"tier\"" in i.get("detail", "") or "data-group=\"special\"" in i.get("detail", "") for i in issues),
        "description": "层级/特色筛选行已删除，残留为回归",
    },
    {
        "id": "tag_explosion",
        "name": "标签云爆炸（筛选胶囊过多无折叠）",
        "check": lambda issues: any("tag_explosion" in i.get("tags", []) for i in issues),
        "description": "筛选胶囊数超阈值且无折叠机制，会导致页面炸屏（2026-07-08 曾发生）",
    },
]


def _read_file(path):
    """Safe file read."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _check_html_structure(html_str, page_name, issues):
    """Check HTML for structural problems."""
    if not html_str:
        issues.append({
            "page": page_name,
            "severity": "CRITICAL",
            "category": "html",
            "message": f"{page_name} HTML 为空或读取失败",
            "detail": "",
            "tags": [],
        })
        return

    # Check for empty blocks (large empty divs)
    empty_blocks = re.findall(r'<div[^>]*>\s*</div>', html_str)
    if len(empty_blocks) > 5:
        issues.append({
            "page": page_name,
            "severity": "WARN",
            "category": "html",
            "message": f"发现 {len(empty_blocks)} 个空 div 块",
            "detail": "empty divs",
            "tags": [],
        })

    # Check for radar-block residue (should be removed)
    if "radar-block" in html_str:
        issues.append({
            "page": page_name,
            "severity": "CRITICAL",
            "category": "regression",
            "message": "选题雷达块(radar-block)残留，应已删除",
            "detail": "radar-block found",
            "tags": [],
        })

    # Check for tier/special filter residue
    if 'data-group="tier"' in html_str or 'data-group="special"' in html_str:
        issues.append({
            "page": page_name,
            "severity": "CRITICAL",
            "category": "regression",
            "message": "层级/特色筛选行残留，应已删除",
            "detail": 'data-group="tier" or data-group="special" found',
            "tags": [],
        })

    # Check for old select#ent-tag residue
    if "tag-select" in html_str and page_name == "enterprise":
        issues.append({
            "page": page_name,
            "severity": "CRITICAL",
            "category": "regression",
            "message": "企业库标签下拉(select.tag-select)残留，应已改为胶囊按钮",
            "detail": "tag-select found in enterprise.html",
            "tags": [],
        })

    # Check sidebar order (fav should be before about)
    fav_pos = html_str.find("nav-fav")
    about_pos = html_str.find('href="about.html"')
    if fav_pos > 0 and about_pos > 0 and fav_pos > about_pos:
        issues.append({
            "page": page_name,
            "severity": "WARN",
            "category": "ui",
            "message": "侧栏顺序错误：我的收藏应在网站说明之前",
            "detail": "nav-fav after about.html link",
            "tags": [],
        })

    # Check for fav empty state
    if "fav-empty" not in html_str and page_name in ("index", "enterprise"):
        issues.append({
            "page": page_name,
            "severity": "WARN",
            "category": "ui",
            "message": "收藏空状态提示(fav-empty)缺失",
            "detail": "fav-empty class not found",
            "tags": [],
        })

    # 标签云爆炸回归检测（2026-07-08 曾因渲染全部标签导致炸屏）
    # 若筛选胶囊数过多且没有折叠机制 -> 视为回归
    pill_count = html_str.count('data-tag=')
    has_fold = ('ent-toggle-tags' in html_str) or ('toggle-more-tags' in html_str)
    if page_name == "enterprise" and pill_count > 40 and not has_fold:
        issues.append({
            "page": page_name,
            "severity": "CRITICAL",
            "category": "regression",
            "message": "企业库标签云爆炸：%d 个筛选胶囊且无折叠机制" % pill_count,
            "detail": "pill_count=%d, no fold" % pill_count,
            "tags": ["tag_explosion"],
        })
    if page_name == "index" and pill_count > 30 and not has_fold:
        issues.append({
            "page": page_name,
            "severity": "WARN",
            "category": "regression",
            "message": "资讯页标签过多：%d 个筛选胶囊且无折叠机制" % pill_count,
            "detail": "pill_count=%d, no fold" % pill_count,
            "tags": ["tag_explosion"],
        })

    # === 视觉/交互层检测（肉眼可见低级 bug 的自动抓手）===
    html_no_script = re.sub(r"<script>.*?</script>", "", html_str, flags=re.S)

    # 1) 死 JS 引用：脚本里 getElementById 的目标 id 在 HTML 中不存在。
    #    曾出现 ent-sort 下拉被删但 JS 仍引用 -> 排序失效。此类回归必须抓出。
    script_parts = re.findall(r"<script>(.*?)</script>", html_str, re.S)
    script_all = "\n".join(script_parts)
    ref_ids = set(re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", script_all))
    html_ids = set(re.findall(r'\bid="([^"]+)"', html_str))
    # 排除"懒创建"模式：getElementById 拿到 null 后，代码用 createElement 动态创建该
    # id（防御式写法，如 fav-empty 收藏空状态）。这类引用在静态 HTML 中无 id 实体，
    # 不应判为死引用，否则会误阻断部署。判据：同一变量被赋 getElementById('x') 后，
    # 后续出现 `var.id='x'` 且脚本含 createElement。
    lazy_created = set()
    for rid in ref_ids:
        m = re.search(
            r"var\s+(\w+)\s*=\s*(?:document\.)?getElementById\(['\"]" + re.escape(rid) + r"['\"]\)",
            script_all,
        )
        if m and "createElement" in script_all:
            var = re.escape(m.group(1))
            if re.search(var + r"\.id\s*=\s*['\"]" + re.escape(rid) + r"['\"]", script_all):
                lazy_created.add(rid)
    missing_ids = sorted(i for i in ref_ids if i not in html_ids and i not in lazy_created)
    if missing_ids:
        issues.append({
            "page": page_name,
            "severity": "CRITICAL",
            "category": "regression",
            "message": "JS 引用了不存在的元素 id: %s" % ", ".join(missing_ids[:5]),
            "detail": "dead getElementById: " + ", ".join(missing_ids[:5]),
            "tags": ["dead_js"],
        })

    # 2) 残留 <select> 下拉框（应全部改为标签胶囊/箭头按钮）
    if "<select" in html_no_script:
        issues.append({
            "page": page_name,
            "severity": "CRITICAL",
            "category": "regression",
            "message": "页面仍存在 <select> 下拉框（应改为标签/箭头按钮）",
            "detail": "select element found in body",
            "tags": ["select_residual"],
        })

    # 3) 重复筛选按钮：同 data-group 下同一 data-value 出现多次（如重复融资行）
    for grp in ("event", "domain", "tag", "time", "reg", "cat", "l2"):
        vals = re.findall(r'data-group="%s" data-value="([^"]+)"' % grp, html_no_script)
        dups = sorted({v for v in vals if v != "all" and vals.count(v) > 1})
        if dups:
            issues.append({
                "page": page_name,
                "severity": "WARN",
                "category": "ui",
                "message": "筛选按钮重复：%s 组内 %s 出现多次" % (grp, ", ".join(dups[:5])),
                "detail": "dup data-value in group %s: %s" % (grp, ", ".join(dups[:5])),
                "tags": ["dup_filter"],
            })


def _check_data_quality(scored, issues):
    """Check scored_latest.json data quality."""
    if not scored:
        issues.append({
            "page": "data",
            "severity": "CRITICAL",
            "category": "data",
            "message": "scored_latest.json 为空或读取失败",
            "detail": "",
            "tags": ["noise"],
        })
        return

    total = len(scored)

    # Noise check (items that fail relevance gate)
    from collector import is_relevant
    noise_count = 0
    for item in scored:
        title = item.get("title", "")
        summary = item.get("summary", "")
        if not is_relevant(title, summary):
            noise_count += 1

    noise_rate = noise_count / total if total > 0 else 0
    if noise_count > 30:
        issues.append({
            "page": "data",
            "severity": "CRITICAL",
            "category": "data",
            "message": f"噪音堆积：{noise_count}/{total} 条 ({noise_rate:.0%}) 不通过相关性闸门",
            "detail": f"noise={noise_count}",
            "tags": ["noise"],
        })
    elif noise_count > 5:
        issues.append({
            "page": "data",
            "severity": "WARN",
            "category": "data",
            "message": f"噪音偏高：{noise_count}/{total} 条不通过相关性闸门",
            "detail": f"noise={noise_count}",
            "tags": ["noise"],
        })

    # Selected rate check
    selected = sum(1 for it in scored if it.get("is_selected") or it.get("curated"))
    sel_rate = selected / total if total > 0 else 0
    if sel_rate < 0.1 and total > 10:
        issues.append({
            "page": "data",
            "severity": "WARN",
            "category": "data",
            "message": f"精选率过低：{selected}/{total} ({sel_rate:.0%})，精选可能为空",
            "detail": f"selected={selected}",
            "tags": [],
        })
    if sel_rate > 0.95 and total > 10:
        issues.append({
            "page": "data",
            "severity": "WARN",
            "category": "data",
            "message": f"精选率过高：{selected}/{total} ({sel_rate:.0%})，筛选阈值可能过松",
            "detail": f"selected={selected}",
            "tags": [],
        })

    # Data freshness
    today = datetime.now().strftime("%Y-%m-%d")
    dates = [it.get("date") for it in scored if isinstance(it.get("date"), str)]
    latest_date = max(dates) if dates else "unknown"
    if latest_date != today and latest_date != "unknown":
        issues.append({
            "page": "data",
            "severity": "WARN",
            "category": "data",
            "message": f"数据非今日：最新日期 {latest_date}（今日 {today}）",
            "detail": f"latest={latest_date}",
            "tags": [],
        })

    return {
        "total": total,
        "noise": noise_count,
        "noise_rate": noise_rate,
        "selected": selected,
        "sel_rate": sel_rate,
        "latest_date": latest_date,
    }


def _check_ui_consistency(index_html, ent_html, about_html, issues):
    """Check consistency across 3 pages."""
    # Sidebar should be identical structure
    for name, html_str in [("index", index_html), ("enterprise", ent_html), ("about", about_html)]:
        if "Silver Pulse" not in html_str:
            issues.append({
                "page": name,
                "severity": "CRITICAL",
                "category": "ui",
                "message": f"{name} 页面缺少 Silver Pulse 标识，侧栏可能缺失",
                "detail": "sidebar missing",
                "tags": [],
            })

    # Check feed-rec style consistency (should be ★ italic, not blue block)
    if index_html and 'class="feed-rec"' in index_html:
        # Check it's not the old blue-block style
        if "background:var(--accent-light)" in index_html and "border-left:3px solid" in index_html:
            # This might be from other elements, check more specifically
            pass  # The CSS is in ui_common, so we check there

    # Check that all 3 pages have FEEDBACK_JS
    for name, html_str in [("index", index_html), ("enterprise", ent_html), ("about", about_html)]:
        if name != "about" and "spToggleFav" not in html_str:
            issues.append({
                "page": name,
                "severity": "WARN",
                "category": "ui",
                "message": f"{name} 页面缺少收藏功能(FEEDBACK_JS)",
                "detail": "spToggleFav not found",
                "tags": [],
            })


def _check_recommendation_quality(scored, issues):
    """Check recommendation text quality."""
    if not scored:
        return

    # Check for duplicate recommendations (same text used too many times)
    rec_counts = {}
    for item in scored:
        rec = item.get("recommendation", "")
        if rec:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1

    max_dup = max(rec_counts.values()) if rec_counts else 0
    if max_dup > 5:
        issues.append({
            "page": "data",
            "severity": "WARN",
            "category": "content",
            "message": f"推荐理由重复度过高：最多一条理由被用了 {max_dup} 次",
            "detail": f"max_dup={max_dup}",
            "tags": [],
        })

    # Check for old template patterns (title-amount duplication)
    old_pattern_count = 0
    for item in scored:
        title = item.get("title", "")
        rec = item.get("recommendation", "")
        # If title contains a number and rec contains the same number
        numbers_in_title = set(re.findall(r'[\d,.]+亿|[\d,.]+万|[\d,.]+千万', title))
        for num in numbers_in_title:
            if num in rec:
                old_pattern_count += 1
                break

    if old_pattern_count > 3:
        issues.append({
            "page": "data",
            "severity": "WARN",
            "category": "content",
            "message": f"推荐理由与标题金额重复：{old_pattern_count} 条推荐理由重复了标题中的金额",
            "detail": f"dup_amount={old_pattern_count}",
            "tags": [],
        })


def run_daily_step():
    """Main entry point for run_daily.py pipeline."""
    print("\n=== L2 Quality Audit ===")

    issues = []

    # 1. Read HTML files
    index_html = _read_file(os.path.join(OUTPUT_DIR, "index.html"))
    ent_html = _read_file(os.path.join(OUTPUT_DIR, "enterprise.html"))
    about_html = _read_file(os.path.join(OUTPUT_DIR, "about.html"))

    # 2. Check HTML structure
    _check_html_structure(index_html, "index", issues)
    _check_html_structure(ent_html, "enterprise", issues)
    _check_html_structure(about_html, "about", issues)

    # 3. Check data quality
    scored = _read_json(os.path.join(DATA_DIR, "scored_latest.json"))
    data_stats = _check_data_quality(scored, issues)

    # 4. Check UI consistency
    _check_ui_consistency(index_html, ent_html, about_html, issues)

    # 5. Check recommendation quality
    _check_recommendation_quality(scored, issues)

    # 6. Known issue regression
    regression_hits = []
    for ki in KNOWN_ISSUES:
        if ki["check"](issues):
            regression_hits.append(ki["name"])

    # 7. Generate report
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    critical = [i for i in issues if i["severity"] == "CRITICAL"]
    warns = [i for i in issues if i["severity"] == "WARN"]

    report_lines = [
        f"# L2 质量自审报告",
        f"",
        f"**生成时间**: {now}",
        f"**状态**: {'🔴 有严重问题' if critical else '🟡 有警告' if warns else '🟢 全部通过'}",
        f"",
        f"## 概览",
        f"",
        f"| 指标 | 值 |",
        f"|---|---|",
    ]

    if data_stats:
        report_lines.extend([
            f"| 资讯总数 | {data_stats['total']} |",
            f"| 噪音数 | {data_stats['noise']} ({data_stats['noise_rate']:.0%}) |",
            f"| 精选数 | {data_stats['selected']} ({data_stats['sel_rate']:.0%}) |",
            f"| 最新日期 | {data_stats['latest_date']} |",
        ])
    else:
        report_lines.append("| 数据 | 读取失败 |")

    report_lines.extend([
        f"| 严重问题 | {len(critical)} |",
        f"| 警告 | {len(warns)} |",
        f"| 已知问题回归 | {len(regression_hits)} |",
        f"",
    ])

    if critical:
        report_lines.append("## 🔴 严重问题（必须修复后才能部署）")
        report_lines.append("")
        for i, issue in enumerate(critical, 1):
            report_lines.append(f"### {i}. [{issue['page']}] {issue['message']}")
            if issue.get("detail"):
                report_lines.append(f"- 详情: `{issue['detail']}`")
            report_lines.append("")

    if warns:
        report_lines.append("## 🟡 警告（不影响部署，但需关注）")
        report_lines.append("")
        for i, issue in enumerate(warns, 1):
            report_lines.append(f"### {i}. [{issue['page']}] {issue['message']}")
            if issue.get("detail"):
                report_lines.append(f"- 详情: `{issue['detail']}`")
            report_lines.append("")

    if regression_hits:
        report_lines.append("## ⚠️ 已知问题回归")
        report_lines.append("")
        for name in regression_hits:
            report_lines.append(f"- **{name}**")
        report_lines.append("")

    if not issues:
        report_lines.append("## 🟢 全部通过")
        report_lines.append("")
        report_lines.append("本次自审未发现任何问题。")
        report_lines.append("")

    # Known issues registry (always show)
    report_lines.append("## 📋 已知问题登记册（回归检测项）")
    report_lines.append("")
    for ki in KNOWN_ISSUES:
        status = "🔴 回归!" if ki["check"](issues) else "🟢 正常"
        report_lines.append(f"- {status} **{ki['name']}**: {ki['description']}")
    report_lines.append("")

    report = "\n".join(report_lines)

    # Write report
    with open(AUDIT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    # Console summary
    print(f"  状态: {'🔴 CRITICAL' if critical else '🟡 WARN' if warns else '🟢 PASS'}")
    print(f"  严重: {len(critical)} | 警告: {len(warns)} | 回归: {len(regression_hits)}")
    if data_stats:
        print(f"  数据: {data_stats['total']}条 | 噪音={data_stats['noise']} | 精选={data_stats['selected']} | 日期={data_stats['latest_date']}")
    print(f"  报告: {AUDIT_PATH}")

    # Return status for run_daily decision
    return {
        "critical": len(critical),
        "warns": len(warns),
        "regression": len(regression_hits),
        "has_blocking": len(critical) > 0,
    }


if __name__ == "__main__":
    result = run_daily_step()
    print(f"\nBlocking: {result['has_blocking']}")
