#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_deliverables.py — 独立核验近期已提交成果是否"真生效"（信任但验证）

背景：Silver Pulse 有多条并行分身/自动化在跑，常宣称"已完成 X"。本脚本只读数据，
对以下已提交成果做硬断言，避免"声称完成但实际回退/悬空"：
  - T50 企业-资讯关联  (enterprise_scores.json.related_news_ids → scored_latest.json.id)
  - T12 事件簇对照卡   (关联资讯必须有可跳转 url + 同事件 cluster_id 可分组)
  - D-15/D-16 推荐理由空壳修复 + entity_name 补全
  - 资讯 final_score 完整性
  - S-01 signal_strength 字段落地状态（INFO，待全量重评）
  - 渲染产物 vs 数据一致性（enterprise.html 卡片数 == all_enterprises.json 条数，防 04-25 类孤儿重生成漂移）

用法：python verify_deliverables.py
输出：打印 JSON 摘要 + 写 data/verify_deliverables_report.json
特点：只读、幂等、对"活跃分身正在写数据文件"做了重试保护，不依赖任何外部服务。
"""
import json
import os
import time
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))


def load_robust(relpath, retries=3, delay=0.3):
    """健壮读取 JSON：活跃分身可能正在重写该文件，短暂重试避免读到半截内容。"""
    path = os.path.join(ROOT, relpath)
    last_err = None
    for _ in range(retries):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, OSError) as e:
            last_err = e
            time.sleep(delay)
    raise RuntimeError(f"无法读取 {relpath}: {last_err}")


def main():
    report = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "script": "verify_deliverables.py",
        "checks": [],
    }

    # ---- 载入数据 ----
    news = load_robust("data/scored_latest.json")  # list, 63 条
    es = load_robust("data/enterprise/enterprise_scores.json")  # dict, 1325 家(key=serial)
    ent_all = load_robust("data/enterprise/all_enterprises.json")  # list, 1325 家
    # 消费契约（见 gen_enterprise.py 446-448 + 159）：related_news_ids 存的是
    # 新闻 URL，news_map 按 url 建索引，且带前缀兜底(split("?")[0] startswith)。
    # 因此核验必须用 URL 作 key，不能用 news.id（短整型）——用 id 查会得到假阳性。
    news_by_url = {n.get("url"): n for n in news if isinstance(n, dict) and n.get("url")}

    # ---- Check 1: T50 企业-资讯关联（按 URL 契约） ----
    assoc_ents = [k for k, v in es.items() if v.get("related_news_ids")]
    total_links = sum(len(v.get("related_news_ids") or []) for v in es.values())
    dangling = []
    for k, v in es.items():
        for nid in v.get("related_news_ids") or []:
            if nid not in news_by_url:
                # 复刻消费端前缀兜底逻辑，确认是否真断链
                key = (nid or "").split("?")[0]
                if not any(u.startswith(key) for u in news_by_url if key):
                    dangling.append({"ent": k, "news_id": nid})
    c1 = {
        "name": "T50 企业-资讯关联回填(URL契约+前缀兜底)",
        "enterprises_with_assoc": len(assoc_ents),
        "total_assoc_links": total_links,
        "dangling_refs": len(dangling),
        "dangling_sample": dangling[:5],
        "consumer_fallback": "gen_enterprise.py 159+161 前缀兜底已复刻",
        "status": "PASS" if not dangling else "WARN",
    }
    report["checks"].append(c1)

    # ---- Check 2: T12 事件簇 — 关联资讯可跳转 + 可分组 ----
    missing_url = 0
    missing_cluster = 0
    for k, v in es.items():
        for nid in v.get("related_news_ids") or []:
            n = news_by_url.get(nid)
            if n is None:
                continue
            if not n.get("url"):
                missing_url += 1
            if not n.get("cluster_id"):
                missing_cluster += 1
    c2 = {
        "name": "T12 事件簇对照卡-数据就绪",
        "missing_url": missing_url,
        "missing_cluster_id": missing_cluster,
        "status": "PASS" if (missing_url == 0 and missing_cluster == 0) else "WARN",
    }
    report["checks"].append(c2)

    # ---- Check 3: D-15/D-16 推荐理由空壳 + entity_name 补全 ----
    empty_rec = 0
    bug = 0
    empty_entity = 0
    for n in news:
        r = n.get("recommendation") or n.get("recommend_reason")
        if r is None or (isinstance(r, str) and r.strip() == ""):
            empty_rec += 1
        elif isinstance(r, str) and "：。" in r:
            bug += 1
        if not n.get("entity_name"):
            empty_entity += 1
    c3 = {
        "name": "D-15/D-16 推荐理由&entity_name",
        "news_total": len(news),
        "empty_recommend": empty_rec,
        "colon_dot_bug": bug,
        "empty_entity_name": empty_entity,
        "entity_fill_rate": round(1 - empty_entity / max(1, len(news)), 3),
        "status": "PASS" if (empty_rec == 0 and bug == 0) else "FAIL",
    }
    report["checks"].append(c3)

    # ---- Check 4: 资讯 final_score 完整性 ----
    bad_score = 0
    for n in news:
        fs = n.get("final_score")
        if not isinstance(fs, (int, float)) or not (0 <= fs <= 10):
            bad_score += 1
    c4 = {
        "name": "资讯 final_score 完整性",
        "bad": bad_score,
        "status": "PASS" if bad_score == 0 else "FAIL",
    }
    report["checks"].append(c4)

    # ---- Check 5: S-01 signal_strength 字段落地 ----
    ss_count = sum(1 for n in news if "signal_strength" in n)
    has_ss = ss_count == len(news) and len(news) > 0
    if ss_count == len(news) and len(news) > 0:
        c5_status, c5_note = "PASS", f"全部 {ss_count}/{len(news)} 条已含 signal_strength（纯脚本回填，无key）"
    elif ss_count > 0:
        c5_status, c5_note = "WARN", f"部分落地 {ss_count}/{len(news)} 条，仍有缺失"
    else:
        c5_status, c5_note = "INFO", "字段尚未写入 scored_latest（待跑 backfill_signal_strength.py），属预期，非失败"
    c5 = {
        "name": "S-01 signal_strength 字段",
        "present": has_ss,
        "count": ss_count,
        "total": len(news),
        "status": c5_status,
        "note": c5_note,
    }
    report["checks"].append(c5)

    # ---- Check 6: 渲染产物 vs 数据一致性（防孤儿重生成/未提交漂移） ----
    # 背景：后台"企业库扩充"自动化可能重跑 gen_enterprise 但被截断未提交，导致仓库
    # HTML 卡片数与 data 实际企业数不一致（2026-07-10 04:25 真实发生过）。
    # 本检查直接比对 enterprise.html 的 ent-card 卡片数与 all_enterprises.json 条数。
    try:
        with open(os.path.join(ROOT, "enterprise.html"), encoding="utf-8") as f:
            ent_html = f.read()
        rendered_cards = ent_html.count('class="ent-card"')
    except (FileNotFoundError, OSError):
        rendered_cards = None
    if isinstance(ent_all, list):
        data_ents = len(ent_all)
    else:
        data_ents = len(ent_all.get("items", ent_all.get("enterprises", [])))
    if rendered_cards is None:
        c6_status, c6_note = "INFO", "enterprise.html 未找到，跳过渲染比对"
    elif rendered_cards == data_ents:
        c6_status, c6_note = "PASS", f"渲染卡片数 {rendered_cards} == 数据企业数 {data_ents}，无漂移"
    else:
        c6_status, c6_note = "WARN", (
            f"渲染卡片数 {rendered_cards} != 数据企业数 {data_ents}，"
            "疑似孤儿重生成/未提交漂移（参考 2026-07-10 04:25 修复）"
        )
    c6 = {
        "name": "渲染产物 vs 数据一致性(enterprise.html)",
        "rendered_cards": rendered_cards,
        "data_enterprises": data_ents,
        "status": c6_status,
        "note": c6_note,
    }
    report["checks"].append(c6)

    blocking = [c for c in report["checks"] if c["status"] in ("FAIL", "WARN")]
    report["overall"] = "PASS" if not blocking else "NEEDS_ATTENTION"

    out_path = os.path.join(ROOT, "data", "verify_deliverables_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n报告已写: {out_path}")
    return 0 if report["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
