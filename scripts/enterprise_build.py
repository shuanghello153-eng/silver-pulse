# -*- coding: utf-8 -*-
"""
半自动流水线编排脚本（脚本接脚本，省积分）

设计意图（V7.4 新增）：
  原流程里"判断之外"的脚本环节是手工作坊式调用的 —— AI 先跑门禁、再手动合并、
  再手动跑生成器、再手动跑部署，每次都要 AI 逐个调脚本并读取中间产物，既耗积分
  又容易漏步。本脚本把 **确定性的脚本环节串成一条**，AI 只需在"语义判断"环节
  动手，判断完调用本脚本一次即可完成：门禁 → 合并 → 生成 →（可选）部署。

  ⚠️ 步骤 8（小爽审核）仍由人卡点：本脚本默认【不部署】，只合并+生成出本地预览；
     拿到小爽"可以入库"的确认后，再加 --deploy 才真正发布。

用法：
  python enterprise_build.py                  # 门禁 → 合并草稿 → 生成 output/（本地预览，不部署）
  python enterprise_build.py --deploy         # 上述 + 部署 gh-pages（须小爽已审核通过）
  python enterprise_build.py --candidates x.json   # 指定候选人（list of draft dict）
  python enterprise_build.py --drafts dir     # 指定草稿目录（默认 scores_draft/rework/drafts_v5）

门禁：check_single（R1-R4/R-name/R-redundancy/R-noabs/R-jargon/R-filler/R10）+ check_description（D1-D4）
"""
import json
import os
import re
import sys
import subprocess
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
REWORK = os.path.join(BASE, "scores_draft/rework")
DEFAULT_DRAFTS = os.path.join(REWORK, "drafts_v5")

sys.path.insert(0, REWORK)
import check_single as C
import check_description as CD


def load_candidates(args):
    if args.candidates:
        return json.load(open(args.candidates, encoding="utf-8"))
    d = args.drafts or DEFAULT_DRAFTS
    if not os.path.isdir(d):
        print(f"草稿目录不存在：{d}")
        return []
    out = []
    for fp in sorted(os.listdir(d)):
        if not fp.startswith("draft_") or not fp.endswith(".json"):
            continue
        try:
            out.append(json.load(open(os.path.join(d, fp), encoding="utf-8")))
        except Exception as e:
            print(f"  [skip] {fp} 读失败：{e}")
    return out


def run_gates(cands):
    """跑门禁，返回 (passed, failures)。"""
    db = json.load(open(DB, encoding="utf-8"))
    recs = [e["recommend"] for e in db if isinstance(e.get("recommend"), str)]
    failures = {}
    for c in cands:
        serial = c.get("serial", "?")
        # 合并上下文：用草稿字段覆盖 DB 字段供校验
        ctx = {}
        for e in db:
            if str(e.get("serial", "")).lstrip("#") == str(serial).lstrip("#"):
                ctx = dict(e)
                break
        merged = dict(ctx)
        for k in ("recommend", "description", "desc_cn", "highlights",
                  "stage", "funding_latest", "funding_total", "source_urls"):
            if k in c and c[k] is not None:
                merged[k] = c[k]
        iss = C.validate(merged, others=recs)
        iss += CD.validate_desc(merged)
        if iss:
            failures[serial] = iss
    return (len(cands) - len(failures), failures)


def safe_merge(cands):
    """安全增量合并：只更新候选人 serial 对应的记录，不碰其他字段/其他企业。"""
    import shutil
    shutil.copyfile(DB, DB + ".bak")  # 合并前备份，便于回滚
    db = json.load(open(DB, encoding="utf-8"))
    idx = {str(e.get("serial", "")).lstrip("#"): e for e in db}
    updated, added = 0, 0
    for c in cands:
        serial = str(c.get("serial", "")).lstrip("#")
        if serial in idx:
            for k, v in c.items():
                if k == "serial":
                    continue
                if v is not None:
                    idx[serial][k] = v
            idx[serial]["update_time"] = idx[serial].get("update_time") or "2026-07-24"
            updated += 1
        else:
            rec = dict(c)
            if "update_time" not in rec or not rec.get("update_time"):
                rec["update_time"] = "2026-07-24"
            db.append(rec)
            added += 1
    json.dump(db, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return updated, added


def main():
    ap = argparse.ArgumentParser(description="半自动流水线编排（门禁→合并→生成→部署）")
    ap.add_argument("--candidates", help="候选人 JSON")
    ap.add_argument("--drafts", help="草稿目录")
    ap.add_argument("--deploy", action="store_true", help="合并+生成后部署 gh-pages（须小爽已审核）")
    ap.add_argument("--skip-gate", action="store_true", help="跳过门禁（不推荐）")
    args = ap.parse_args()

    cands = load_candidates(args)
    if not cands:
        print("无候选人，退出")
        return

    # 1. 门禁
    if not args.skip_gate:
        passed, failures = run_gates(cands)
        print(f"门禁：{passed}/{len(cands)} 通过")
        if failures:
            print("以下未过门禁，终止（先修再跑）：")
            for s, iss in failures.items():
                print(f"  #{s}: {iss}")
            sys.exit(1)
        print("✅ 门禁全部通过")
    else:
        print("⚠️ 已跳过门禁（--skip-gate）")

    # 2. 安全合并
    updated, added = safe_merge(cands)
    print(f"已合并：更新 {updated} 家 / 新增 {added} 家 → all_enterprises.json")

    # 3. 生成 output/
    print("生成 output/ ...")
    try:
        subprocess.run([sys.executable, "gen_enterprise.py"], cwd=BASE, check=True)
    except Exception as e:
        print(f"[warn] gen_enterprise.py 调用失败：{e}（请手动跑）")
    try:
        subprocess.run([sys.executable, "generator.py"], cwd=BASE, check=True)
    except Exception:
        pass  # 有些项目 generator.py 不独立存在，gen_enterprise 已生成 output/

    # 4. 部署（人工卡点后）
    if args.deploy:
        print("部署 gh-pages ...")
        try:
            subprocess.run([sys.executable, "deploy_ghpages.py"], cwd=BASE, check=True)
            print("✅ 已部署")
        except Exception as e:
            print(f"[warn] 部署失败：{e}（请手动 deploy_ghpages.py）")
    else:
        print("📋 已生成本地预览 output/（未部署）。小爽审核通过后加 --deploy 发布。")


if __name__ == "__main__":
    main()
