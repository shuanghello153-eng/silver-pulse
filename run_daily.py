#!/usr/bin/env python3
"""
run_daily.py — Silver Pulse 每周全流水线编排器 (Phase 2).

按固定顺序运行每日管道，每步用 try/except 包裹，出错打印但继续：
    collector.collect_all()
    -> score_and_merge.main()
    -> selection.enterprise_score.main()
    -> generator.main()
    -> gen_enterprise.main()
    -> gen_about.main()

采集(collector)可能因网络失败；若失败，后续步骤继续使用本地已有数据，
不应使整条脚本崩溃。最后打印汇总。
"""
import os
import sys
import traceback
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

STEPS = [
    # [COST: zero] RSS 采集 48 信源 + Google News + manual 种子注入
    #   （含增量跨周去重 + 每源健康统计，落 seen_urls.json / source_health.json）
    ("collector.collect_all()", "collector", "collect_all", ()),
    # [COST: zero] 源健康监控 + 健康报告（data/health_report.json + 控制台摘要）
    #   在采集步骤后运行，不阻断主流程；即便上游失败也基于已有数据出报告。
    ("source_health.build_report()", "source_health", "build_report", ()),
    # [COST: zero] 阶段2 低模二筛（relevance_screener）：二筛严出，
    #   默认 ENABLE_RELEVANCE_SCREENER=False -> 该步为空操作，不影响现有流水线。
    ("selection.relevance_screener.run_daily_step()", "selection.relevance_screener", "run_daily_step", ()),
    # [COST: zero] 信号过滤 + 聚合 + history 去重
    ("score_and_merge.main()", "score_and_merge", "main", ()),
    # [COST: zero] 企业实体名回填（用企业库名称/别名匹配标题+摘要，
    #   供聚类主规则(entity+event_type)与推荐理由使用；匹配不到留空，绝不瞎填）
    ("selection.enrich_entity.run_daily_step()", "selection.enrich_entity", "run_daily_step", ()),
    # [COST: zero] L2 自纠：两级闸门重过存量，清旧噪音
    ("purge_legacy.run_daily_step()", "purge_legacy", "run_daily_step", ()),
    # [COST: model-optional] L3 5 维打分（规则兜底；无模型跳过）
    ("selection.score_skill.run_daily_step()", "selection.score_skill", "run_daily_step", ()),
    # [COST: model-optional] 中文翻译回填（规则兜底；无模型跳过）
    ("selection.translate.run_daily_step()", "selection.translate", "run_daily_step", ()),
    # [COST: zero] L3 反馈闭环：读 feedback.jsonl → ±0.03 权重微调
    ("feedback_loop.run_daily_step()", "feedback_loop", "run_daily_step", ()),
    # [COST: zero] 赛道核心度关键词覆盖 + 终分重算（含 user_pref）
    ("reapply_centrality.main()", "reapply_centrality", "main", ()),
    # [COST: zero] 事件聚类：(entity,event_type)精确匹配 + 余弦回退 → cluster_id
    ("selection.cluster.run_daily_step()", "selection.cluster", "run_daily_step", ()),
    # [COST: zero] 推荐理由重算（变体库轮换去重）
    ("selection.recommend.run_daily_step()", "selection.recommend", "run_daily_step", ()),
    # [COST: zero] 企业研究价值分（base_value + event_boost）
    ("selection.enterprise_score.main()", "selection.enterprise_score", "main", ()),
    # [COST: zero] 企业-资讯关联重建（T40）：必须位于 enterprise_score 之后，
    # 否则上一步重写 enterprise_scores.json 会把 related_news_ids 清空。
    ("selection.rebuild_association.run_daily_step()", "selection.rebuild_association", "run_daily_step", ()),
    # [COST: zero] 自动反哺企业标签
    ("tag_enterprises.run_daily_step()", "tag_enterprises", "run_daily_step", ()),
    # [COST: zero] 生成 index.html（资讯看板 + 选题雷达）
    ("generator.main()", "generator", "main", ()),
    # [COST: zero] 生成 enterprise.html（企业库 + TOP15）
    ("gen_enterprise.main()", "gen_enterprise", "main", ()),
    # [COST: zero] 生成 about.html（规则 SSoT）
    ("gen_about.main()", "gen_about", "main", ()),
    # [COST: zero] 自检：写 STATE.md
    ("validator.main()", "validator", "main", ()),
    # [COST: zero] L2 质量自审（HTML走查/数据质量/回归检测）
    ("loop_audit.run_daily_step()", "loop_audit", "run_daily_step", ()),
    # [COST: zero] L2 进化层（噪音spike/精选暴跌/规则漂移检测+封禁）
    ("noise_spike_guard.run_daily_step()", "noise_spike_guard", "run_daily_step", ()),
    # [COST: zero] 三道零成本校验：死链检测 / JSON 字段断言 / 评分一致性抽样
    #   （生成 HTML 之后、部署之前）。字段断言硬错可阻断部署；其余仅报告。
    ("selfcheck.run_daily_step()", "selfcheck", "run_daily_step", ()),
    # [COST: zero] 可观测性：每日健康报告 + 趋势历史
    ("daily_health.run_daily_step()", "daily_health", "run_daily_step", ()),
    # [COST: zero] Loop 自我进化：阈值自适应（方向1）。默认 ENABLE_AUTO_THRESHOLD=False
    # → 只产出"进化建议 + threshold_history.json/override 覆盖层"，不改线上精选行为；
    # owner 拍板后置 True 并由 reapply_centrality 读 override 才生效。
    ("adapt_thresholds.run_daily_step()", "adapt_thresholds", "run_daily_step", ()),
]

def git_pull_main():
    """拉取远端 main，使流水线能读到用户从网站「同步云端」上传的 feedback.jsonl（收藏云端桥接）。
    失败不阻断流水线（本地已有数据可继续）。"""
    try:
        import subprocess
        r = subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"],
                           cwd=BASE_DIR, capture_output=True, text=True, timeout=90)
        head = (r.stdout or r.stderr or "").strip().replace("\n", " ")[:220]
        print("[run_daily] git pull main -> rc=%s %s" % (r.returncode, head))
    except Exception as e:
        print("[run_daily] git pull skipped: %s" % e)


def run_step(label, module_name, func_name, args):
    try:
        mod = __import__(module_name, fromlist=[func_name])
        func = getattr(mod, func_name)
        print("\n>>> STEP: %s" % label)
        ret = func(*args)
        print("<<< OK: %s" % label)
        return True, None, ret
    except Exception as e:  # noqa: BLE001
        err = "%s: %s" % (type(e).__name__, e)
        print("!!! FAILED: %s -> %s" % (label, err))
        traceback.print_exc()
        return False, err, None


def main():
    print("=" * 64)
    print("Silver Pulse 每周流水线  %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 64)
    git_pull_main()

    steps = STEPS
    if os.environ.get("SKIP_COLLECTOR"):
        steps = [s for s in steps if s[0] != "collector.collect_all()"]
        print("[run_daily] SKIP_COLLECTOR set -> skipping collector, using existing raw_*.json")
    results = []
    for label, module_name, func_name, args in steps:
        ok, err, ret = run_step(label, module_name, func_name, args)
        results.append((label, ok, err, ret))

    print("\n" + "=" * 64)
    print("汇总 SUMMARY")
    print("=" * 64)
    for label, ok, err, ret in results:
        status = "OK " if ok else "FAIL"
        detail = "" if ok else "  (%s)" % err
        print("  [%s] %s%s" % (status, label, detail))

    failed = [r for r in results if not r[1]]
    if failed:
        print("\n%d 个步骤失败（详见上方）。其余步骤产出已生成。" % len(failed))
    else:
        print("\n全部步骤成功完成。")
    print("=" * 64)

    # Deploy ONLY if critical steps succeeded. A failed pipeline must never push
    # a half-built / stale artifact (the bug that produced an inconsistent site on
    # 2026-07-08). STATE.md is still written by the validator step for the 09:00 补跑.
    critical_labels = {"collector.collect_all()", "score_and_merge.main()", "generator.main()"}
    critical_failed = [label for label, ok, _, _ in results if not ok and label in critical_labels]
    # L2 质量自审：若 loop_audit 报告 CRITICAL 问题（dead JS / 残余 select / 重复筛选
    # / 已知问题回归等），同样阻断部署——绝不让有可见缺陷的版本上线。
    audit_blocking = []
    for label, ok, err, ret in results:
        if label == "loop_audit.run_daily_step()" and ok and isinstance(ret, dict) and ret.get("has_blocking"):
            audit_blocking.append("loop_audit(%d critical)" % ret["critical"])
    # 三道校验：仅「字段断言硬错」阻断部署（死链/评分不一致仅报告，不阻断）。
    selfcheck_blocking = []
    for label, ok, err, ret in results:
        if label == "selfcheck.run_daily_step()" and ok and isinstance(ret, dict) and ret.get("has_blocking"):
            selfcheck_blocking.append("selfcheck(%d 硬错)" % ret.get("schema_hard_errors", 0))
    if critical_failed or audit_blocking or selfcheck_blocking:
        blocked_by = []
        if critical_failed:
            blocked_by.append("步骤失败: " + ", ".join(critical_failed))
        if audit_blocking:
            blocked_by.append("质量自审: " + ", ".join(audit_blocking))
        if selfcheck_blocking:
            blocked_by.append("三道校验: " + ", ".join(selfcheck_blocking))
        print("DEPLOY skipped: -> %s" % " | ".join(blocked_by))
        print("STATE.md 已标 FAIL，09:00 补跑将重试。")
    else:
        try:
            import deploy_ghpages
            ok_d, msg_d = deploy_ghpages.deploy()
            print("DEPLOY gh-pages: %s" % msg_d)
        except Exception as e:  # noqa: BLE001
            print("DEPLOY gh-pages skipped: %s" % e)

    # 退出码与部署门槛一致：关键步失败 / 质量自审 CRITICAL / 三道校验硬错 阻断 → 失败（1），触发补跑
    return 0 if not (critical_failed or audit_blocking or selfcheck_blocking) else 1


if __name__ == "__main__":
    sys.exit(main())
