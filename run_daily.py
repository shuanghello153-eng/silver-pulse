#!/usr/bin/env python3
"""
run_daily.py — Silver Pulse 每日全流水线编排器 (Phase 2).

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
    ("collector.collect_all()", "collector", "collect_all", ()),
    ("score_and_merge.main()", "score_and_merge", "main", ()),
    # L2 自我纠错：对存量 scored 重过两级闸门，自动清掉收紧前漏入的旧噪音（防复发）
    ("purge_legacy.run_daily_step()", "purge_legacy", "run_daily_step", ()),
    # L3 模型 5 维打分（Skill 封装，零成本规则兜底；无模型则跳过，绝不中断）
    ("selection.score_skill.run_daily_step()", "selection.score_skill", "run_daily_step", ()),
    # 中文翻译回填（Skill 封装，零成本；无模型则跳过，绝不中断）
    ("selection.translate.run_daily_step()", "selection.translate", "run_daily_step", ()),
    # L3 外部反馈闭环：读收藏 feedback.jsonl -> 安全微调评分权重 (user_pref.json)
    ("feedback_loop.run_daily_step()", "feedback_loop", "run_daily_step", ()),
    # 赛道核心度: 用代码关键词覆盖 industry 维度(零成本), 并重算终分（含 user_pref 权重）
    ("reapply_centrality.main()", "reapply_centrality", "main", ()),
    # 推荐理由重算（T24+T30）：每次跑批用差异化模板重算全部条目，带入 entity/领域/反常识度
    ("selection.recommend.run_daily_step()", "selection.recommend", "run_daily_step", ()),
    ("selection.enterprise_score.main()", "selection.enterprise_score", "main", ()),
    # 自动反哺企业标签（资讯事件 + 融资字段 -> 企业 tags，供融资/IPO 筛选）
    ("tag_enterprises.run_daily_step()", "tag_enterprises", "run_daily_step", ()),
    ("generator.main()", "generator", "main", ()),
    ("gen_enterprise.main()", "gen_enterprise", "main", ()),
    ("gen_about.main()", "gen_about", "main", ()),
    # 自检：写 STATE.md（供 06:00 自审与 09:00 补跑读取）
    ("validator.main()", "validator", "main", ()),
    # L2 质量自审（Loop Engineering Layer 2）：HTML走查/数据质量/UI一致性/已知问题回归
    ("loop_audit.run_daily_step()", "loop_audit", "run_daily_step", ()),
    # L2 进化层（Loop Engineering Layer 2 写查分离之「进化」）：噪音spike/精选暴跌/规则漂移检测+保守回调
    ("noise_spike_guard.run_daily_step()", "noise_spike_guard", "run_daily_step", ()),
]


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
    print("Silver Pulse 每日流水线  %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 64)

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
    if critical_failed or audit_blocking:
        blocked_by = []
        if critical_failed:
            blocked_by.append("步骤失败: " + ", ".join(critical_failed))
        if audit_blocking:
            blocked_by.append("质量自审: " + ", ".join(audit_blocking))
        print("DEPLOY skipped: -> %s" % " | ".join(blocked_by))
        print("STATE.md 已标 FAIL，09:00 补跑将重试。")
    else:
        try:
            import deploy_ghpages
            ok_d, msg_d = deploy_ghpages.deploy()
            print("DEPLOY gh-pages: %s" % msg_d)
        except Exception as e:  # noqa: BLE001
            print("DEPLOY gh-pages skipped: %s" % e)

    # 退出码与部署门槛一致：关键步失败 或 质量自审 CRITICAL 阻断 → 视为失败（1），触发补跑
    return 0 if not (critical_failed or audit_blocking) else 1


if __name__ == "__main__":
    sys.exit(main())
