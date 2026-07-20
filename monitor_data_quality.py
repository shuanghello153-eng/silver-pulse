# -*- coding: utf-8 -*-
"""
Silver Pulse — 只读数据质量监控 (Data Quality Monitor)
=====================================================
定位：领导视角的"独立测量仪"。只 READ 真相源，绝不 WRITE 任何源数据/配置。
产出：人类可读报告(md) + 机器快照(json) + 趋势历史(history.json)。

它测量什么（不依赖任何业务规则，故与打标签/评分/企业库团队零冲突）：
  1. 字段完整度（每个字段有多少数据、缺多少）
  2. 分类字段分布（一级/二级分类、阶段、地区、成立年代）
  3. 资讯健康度（条数、新鲜度、精选占比、主体漂移）
  4. 趋势（与上次快照对比，看数据是在变好还是变差）

它【不】做什么（避免冲突）：
  - 不校验标签是否合规（那是标签库团队的 rules）
  - 不评分、不重写企业库、不改 config
仅把"空字段清单 / 库外主体清单"作为信号抛给其他团队接手。
"""
import json
import os
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
ENT_PATH = os.path.join(BASE, "data", "enterprise", "all_enterprises.json")
SCORED_PATH = os.path.join(BASE, "data", "scored_latest.json")
OUTDIR = os.path.join(BASE, "data", "monitoring")
HISTORY_PATH = os.path.join(OUTDIR, "history.json")
os.makedirs(OUTDIR, exist_ok=True)

PLACEHOLDER_EMPTY = {"", "未披露", "N/A", "na", "null", "none", "nan", "待补充", "—", "-"}


def load_json(p):
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[warn] 无法解析 {p}: {e}")
        return None


def is_empty(v):
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip().lower() in PLACEHOLDER_EMPTY
    if isinstance(v, (list, dict)):
        return len(v) == 0
    return False


def completeness(records, field):
    """返回 (填充数, 总数, 填充率%)。field 支持 'a.b' 取嵌套。"""
    total = 0
    filled = 0
    for r in records:
        if not isinstance(r, dict):
            continue
        if "." in field:
            a, b = field.split(".", 1)
            node = r.get(a)
            val = node.get(b) if isinstance(node, dict) else None
        else:
            val = r.get(field)
        total += 1
        if not is_empty(val):
            filled += 1
    rate = (filled / total * 100) if total else 0.0
    return filled, total, rate


def distribution(records, field, top=None):
    """分类字段取值计数。"""
    from collections import Counter
    c = Counter()
    for r in records:
        if not isinstance(r, dict):
            continue
        if "." in field:
            a, b = field.split(".", 1)
            node = r.get(a)
            v = node.get(b) if isinstance(node, dict) else None
        else:
            v = r.get(field)
        if v is None:
            c["(空)"] += 1
            continue
        if isinstance(v, list):
            for x in v:
                c[str(x)] += 1
        else:
            c[str(v)] += 1
    items = c.most_common(top) if top else sorted(c.items(), key=lambda x: -x[1])
    return items


def main():
    today = datetime.date.today().isoformat()
    ents = load_json(ENT_PATH) or []
    scored = load_json(SCORED_PATH) or []

    lines = []
    lines.append(f"# 数据质量监控报告 · {today}\n")
    lines.append("> 本报告为**只读测量**，不修改任何源数据。标签合规校验归标签库团队，评分归评分团队。\n")

    # ---------- 1. 总览 ----------
    lines.append(f"## 一、总览\n")
    lines.append(f"- 企业库总数：**{len(ents)}**")
    lines.append(f"- 资讯总数：**{len(scored) if isinstance(scored, list) else 'n/a'}**")

    # ---------- 2. 字段完整度 ----------
    lines.append(f"\n## 二、企业字段完整度（填充率 %）\n")
    FIELDS = [
        "name_cn", "website_url", "crunchbase_url", "founded", "stage",
        "funding_latest.amount", "funding_total", "investors", "news_coverage",
        "highlights", "desc_cn", "region", "category_l1", "category_l2",
        "tag_l1", "tag_l2", "business_model", "payor_model", "value_score",
    ]
    lines.append("| 字段 | 填充数 | 总数 | 填充率 |")
    lines.append("|---|---|---|---|")
    comp_rows = []
    for f in FIELDS:
        filled, total, rate = completeness(ents, f)
        comp_rows.append((f, filled, total, rate))
        lines.append(f"| `{f}` | {filled} | {total} | {rate:.1f}% |")

    # ---------- 3. 分类分布 ----------
    lines.append(f"\n## 三、分类字段分布\n")
    for fld, title in [("category_l1", "一级分类"), ("stage", "阶段"), ("region", "地区")]:
        lines.append(f"\n### {title}（`{fld}`）\n")
        dist = distribution(ents, fld, top=15)
        if not dist:
            lines.append("（无数据）")
            continue
        for k, v in dist:
            lines.append(f"- {k}: **{v}**")

    # 成立年代
    lines.append(f"\n### 成立年代分布（`founded`）\n")
    by_decade = {}
    for r in ents:
        if not isinstance(r, dict):
            continue
        fv = r.get("founded")
        if is_empty(fv):
            by_decade["(空)"] = by_decade.get("(空)", 0) + 1
            continue
        try:
            y = int(str(fv)[:4])
            dec = f"{(y // 10) * 10}s"
            by_decade[dec] = by_decade.get(dec, 0) + 1
        except Exception:
            by_decade["(无法解析)"] = by_decade.get("(无法解析)", 0) + 1
    for k in sorted(by_decade.keys()):
        lines.append(f"- {k}: **{by_decade[k]}**")

    # ---------- 4. 资讯健康度 ----------
    if isinstance(scored, list) and scored:
        lines.append(f"\n## 四、资讯健康度\n")
        n = len(scored)
        lines.append(f"- 资讯条数：**{n}**")
        # 日期
        dates = []
        for r in scored:
            d = r.get("date") or r.get("published")
            if d:
                dates.append(str(d)[:10])
        if dates:
            dates_sorted = sorted(dates)
            lines.append(f"- 日期范围：{dates_sorted[0]} ~ {dates_sorted[-1]}")
            lines.append(f"- 最新一条：{dates_sorted[-1]}（距今天 { (datetime.date.today() - datetime.date.fromisoformat(dates_sorted[-1])).days } 天）")
        # 精选 / 主体
        curated = sum(1 for r in scored if r.get("is_curated") or r.get("is_selected"))
        lines.append(f"- 被精选(is_curated/is_selected)：**{curated}** / {n}")
        # 漂移：entity_name 不在企业库
        ent_names = set()
        for r in ents:
            for key in ("name", "name_cn"):
                v = r.get(key)
                if v and not is_empty(v):
                    ent_names.add(str(v).strip())
        drift = []
        for r in scored:
            en = r.get("entity_name")
            if not en or is_empty(en):
                continue
            en_s = str(en).strip()
            if len(en_s) < 2:
                continue
            if en_s not in ent_names:
                drift.append((en_s, r.get("title", "")[:40]))
        # 轻量分类：疑似噪声 vs 疑似真实主体（仅提示，不判定）
        NOISE_TOKENS = ("发布", "上线", "指数", "方案", "国补", "普惠", "万元", "奶商",
                        "异化", "政部", "湖南", "英国", "烟台", "在粤", "新项目", "个人养老",
                        "城乡", "视频", "洞察", "报告", "建设", "行动", "对接", "招商", "活动",
                        "圆满", "共振", "路径", "全文", "助力", "政策", "宣布", "推出", "完成",
                        "收购", "融资", "获", "亿", "万", "%", "总理", "部长", "书记", "政府")
        real_subjects, noise_subjects = [], []
        for en_s, t in drift:
            if any(tok in en_s for tok in NOISE_TOKENS):
                noise_subjects.append((en_s, t))
            else:
                real_subjects.append((en_s, t))
        lines.append(f"- 主体漂移（资讯主体不在企业库）：**{len(drift)}** 条")
        lines.append(f"  - 疑似真实主体（优先补）：**{len(real_subjects)}** 条")
        lines.append(f"  - 疑似抽取噪声（可忽略）：**{len(noise_subjects)}** 条")

    # ---------- 5. 趋势 ----------
    lines.append(f"\n## 五、趋势（与上次快照对比）\n")
    history = []
    if os.path.exists(HISTORY_PATH):
        try:
            history = json.load(open(HISTORY_PATH, encoding="utf-8"))
        except Exception:
            history = []
    prev = history[-1] if history else None
    if prev:
        lines.append(f"- 上次快照：{prev.get('date')}（企业 {prev.get('n_ent')}，资讯 {prev.get('n_scored')}）")
        for f, filled, total, rate in comp_rows:
            pr = prev.get("comp", {}).get(f)
            if pr is not None:
                delta = rate - pr
                arrow = "▲" if delta > 0.5 else ("▼" if delta < -0.5 else "—")
                lines.append(f"  - `{f}`: {rate:.1f}% ({arrow} {delta:+.1f}% vs 上次)")
    else:
        lines.append("（首次运行，无历史基线。下次运行起可看趋势。）")

    # ---------- 6. 给兄弟团队的信号 ----------
    lines.append(f"\n## 六、给其他团队的信号（仅列出，不处理）\n")
    # 缺失最严重字段
    worst = sorted(comp_rows, key=lambda x: x[3])[:5]
    lines.append("**字段完整度最差的 5 项（企业库团队可优先补）：**")
    for f, filled, total, rate in worst:
        lines.append(f"- `{f}`: 仅 {rate:.1f}% 填充")
    if isinstance(scored, list) and scored and drift:
        lines.append(f"\n**资讯主体但企业库缺失（企业库/信源团队可补，共 {len(drift)} 条）：**")
        lines.append(f"\n_疑似真实主体（{len(real_subjects)} 条，优先）——_")
        for en, t in real_subjects[:40]:
            lines.append(f"- {en}（例：{t}…）")
        if len(real_subjects) > 40:
            lines.append(f"- …另有 {len(real_subjects)-40} 条未列出")
        lines.append(f"\n_疑似抽取噪声（{len(noise_subjects)} 条，可忽略）——_")
        for en, t in noise_subjects[:15]:
            lines.append(f"- {en}（例：{t}…）")
        if len(noise_subjects) > 15:
            lines.append(f"- …另有 {len(noise_subjects)-15} 条未列出")

    lines.append(f"\n---\n_本报告由 monitor_data_quality.py 生成，只读、零写入。_")

    report = "\n".join(lines)
    report_path = os.path.join(OUTDIR, f"数据质量监控_{today}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    # 快照
    snapshot = {
        "date": today,
        "n_ent": len(ents),
        "n_scored": len(scored) if isinstance(scored, list) else 0,
        "comp": {f: rate for f, _, _, rate in comp_rows},
    }
    history.append(snapshot)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"[ok] 报告已写: {report_path}")
    print(f"[ok] 快照已追加: {HISTORY_PATH} (共 {len(history)} 次记录)")
    print(f"[summary] 企业 {len(ents)} 家; 资讯 {len(scored) if isinstance(scored,list) else 0} 条; 漂移 {len(drift) if isinstance(scored,list) and scored else 'n/a'} 条")


if __name__ == "__main__":
    main()
