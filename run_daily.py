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
    # L3 模型 5 维打分（Skill 封装，零成本规则兜底；无模型则跳过，绝不中断）
    ("selection.score_skill.run_daily_step()", "selection.score_skill", "run_daily_step", ()),
    # 中文翻译回填（Skill 封装，零成本；无模型则跳过，绝不中断）
    ("selection.translate.run_daily_step()", "selection.translate", "run_daily_step", ()),
    # 赛道核心度: 用代码关键词覆盖 industry 维度(零成本), 并重算终分
    ("reapply_centrality.main()", "reapply_centrality", "main", ()),
    ("selection.enterprise_score.main()", "selection.enterprise_score", "main", ()),
    ("generator.main()", "generator", "main", ()),
    ("gen_enterprise.main()", "gen_enterprise", "main", ()),
    ("gen_about.main()", "gen_about", "main", ()),
]


def run_step(label, module_name, func_name, args):
    try:
        mod = __import__(module_name, fromlist=[func_name])
        func = getattr(mod, func_name)
        print("\n>>> STEP: %s" % label)
        func(*args)
        print("<<< OK: %s" % label)
        return True, None
    except Exception as e:  # noqa: BLE001
        err = "%s: %s" % (type(e).__name__, e)
        print("!!! FAILED: %s -> %s" % (label, err))
        traceback.print_exc()
        return False, err


def main():
    print("=" * 64)
    print("Silver Pulse 每日流水线  %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 64)

    results = []
    for label, module_name, func_name, args in STEPS:
        ok, err = run_step(label, module_name, func_name, args)
        results.append((label, ok, err))

    print("\n" + "=" * 64)
    print("汇总 SUMMARY")
    print("=" * 64)
    for label, ok, err in results:
        status = "OK " if ok else "FAIL"
        detail = "" if ok else "  (%s)" % err
        print("  [%s] %s%s" % (status, label, detail))

    failed = [r for r in results if not r[1]]
    if failed:
        print("\n%d 个步骤失败（详见上方）。其余步骤产出已生成。" % len(failed))
    else:
        print("\n全部步骤成功完成。")
    print("=" * 64)

    # Best-effort deploy to gh-pages (never fails the data pipeline)
    try:
        import deploy_ghpages
        ok_d, msg_d = deploy_ghpages.deploy()
        print("DEPLOY gh-pages: %s" % msg_d)
    except Exception as e:  # noqa: BLE001
        print("DEPLOY gh-pages skipped: %s" % e)

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
