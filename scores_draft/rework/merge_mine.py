# -*- coding: utf-8 -*-
"""受控合并器（指定 serial 版）：只合并我手工确认过的草稿，绝不碰其他文件。
用法：python merge_mine.py --commit #0041 #0058 ...
R10 内联实现（不依赖 check_single._cross_fail），逻辑与 merge_v5_controlled.py 一致。
"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DRAFTS_DIR = os.path.join(HERE, "drafts_v5")
REC_SKIP = {"R10", "R6", "R7", "R8"}

def _norm(t): return re.sub(r"\s", "", t or "")
def _tri(t):
    t = _norm(t)
    return set(t[i:i+3] for i in range(len(t)-2)) if len(t) >= 3 else set(t)
def _cs(t): return set(_norm(t))

def cross_fail(txt, corpus_texts):
    """返回 True 如果 txt 与任一语料文本 LCS>=15 且字符集Jaccard>0.5"""
    rt, rc = _tri(txt), _cs(txt)
    for other in corpus_texts:
        oc, ocs = _tri(other), _cs(other)
        if not rc or not ocs: continue
        if len(rc & ocs) / len(rc | ocs) <= 0.5: continue
        if C.lcs_len(txt, other) >= 15:
            return True
    return False

def main():
    do_commit = "--commit" in sys.argv
    targets = [a for a in sys.argv[1:] if a != "--commit"]
    if not targets:
        print("用法: python merge_mine.py --commit #0041 #0058 ...")
        return
    tset = set(t.lstrip("#") for t in targets)

    db = json.load(open(DB_PATH, encoding="utf-8"))
    db_idx = {str(e.get("serial", "")).lstrip("#"): e for e in db}
    existing = [e["recommend"] for e in db if isinstance(e.get("recommend"), str)]

    valid = {}
    fails = []
    for s in tset:
        fp = os.path.join(DRAFTS_DIR, f"draft_#{s}.json")
        if not os.path.exists(fp):
            fails.append((s, "草稿不存在")); continue
        d = json.load(open(fp, encoding="utf-8"))
        e = db_idx.get(s)
        if not e:
            fails.append((s, "库中未找到")); continue
        ctx = dict(e); ctx["recommend"] = d.get("recommend")
        errs = C.validate(ctx, others=None, skip=REC_SKIP)
        if errs:
            fails.append((s, "; ".join(errs)))
        else:
            valid[s] = d.get("recommend")

    r10_fail = set()
    for s, r in valid.items():
        if cross_fail(r, existing):
            r10_fail.add(s)
    final = [s for s in valid if s not in r10_fail]

    print(f"目标: {len(tset)} | 单家PASS: {len(valid)} | R10失败: {len(r10_fail)} | 写回: {len(final)}")
    for s, e in fails:
        print(f"  FAIL {s}: {e[:80]}")
    for s in r10_fail:
        print(f"  R10 {s}: 跨企业雷同")

    if do_commit and final:
        for s in final:
            db_idx[s]["recommend"] = valid[s]
            db_idx[s]["update_time"] = "2026-07-20"
        json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"已写回 {len(final)} 家")
        os.system(f'cd "{BASE}" && git add -A && git commit -q -m "rework: 合并Batch1手工草稿{len(final)}家(过单家门禁+R10零雷同)"')
        print("已 git commit")
    else:
        print("[预览] 加 --commit 写回")

if __name__ == "__main__":
    main()
