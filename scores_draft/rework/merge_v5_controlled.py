# -*- coding: utf-8 -*-
"""受控合并器 V5：只把 drafts_v5/ 里通过门禁的 recommend 写回主库。
安全设计：
  - 只读 drafts_v5/（绝不碰 drafts_v4 已知废稿）
  - 只写 recommend 字段 + update_time，不写 desc/silver/payor（后续单独受控pass）
  - 只处理 rework 队列(882)内的 serial，绝不碰 620 已干净企业
  - recommend 决策用 REC_SKIP(R6/R7/R8不阻塞)，但 R10 跨企业去重对照【主库现有全部recommend + 本批】
  - 只有最终 PASS 才写回；R10 失败不写回
用法：python merge_v5_controlled.py [--commit]
"""
import json, os, sys, glob, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DRAFTS_DIR = os.path.join(HERE, "drafts_v5")
QUEUE = json.load(open(os.path.join(HERE, "_rework_queue.json"), encoding="utf-8"))
QSET = set(str(s).lstrip("#") for s in QUEUE)
REC_SKIP = {"R10", "R6", "R7", "R8"}


def load_db():
    return json.load(open(DB_PATH, encoding="utf-8"))


def save_db(db):
    json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"已保存主库: {DB_PATH} ({len(db)}家)")


def main():
    do_commit = "--commit" in sys.argv
    files = sorted(glob.glob(os.path.join(DRAFTS_DIR, "draft_*.json")))
    by_serial = defaultdict(list)
    for fp in files:
        try:
            d = json.load(open(fp, encoding="utf-8"))
        except Exception:
            continue
        s = str(d.get("serial", "")).lstrip("#")
        if s in QSET:
            by_serial[s].append(d)

    db = load_db()
    db_idx = {str(e.get("serial", "")).lstrip("#"): e for e in db}
    # 主库现有全部 recommend（用于 R10 对照，防引入与已干净串雷同）
    existing_recs = [e["recommend"] for e in db if isinstance(e.get("recommend"), str)]

    # ── 第一遍：recommend 单企业校验（R1-R9 skip R6/R7/R8）──
    valid = {}
    fail_single = []
    for s, lst in by_serial.items():
        best = max(lst, key=lambda d: C.content_len(d.get("recommend") or ""))
        entry = db_idx.get(s)
        if not entry:
            fail_single.append((s, "库中未找到"))
            continue
        ctx = dict(entry)
        ctx["recommend"] = best.get("recommend")
        errs = C.validate(ctx, others=None, skip=REC_SKIP)
        if errs:
            fail_single.append((s, "; ".join(errs)))
        else:
            valid[s] = best

    # ── 第二遍：R10 跨企业去重（本批互比 + 对照主库现有recommend）──
    recs = [(s, valid[s].get("recommend", "")) for s in valid if isinstance(valid[s].get("recommend"), str)]
    # 虚拟语料：本批 + 主库现有（主库串标记 EXIST）
    corpus = [(s, r) for s, r in recs] + [("EXIST", r) for r in existing_recs if isinstance(r, str)]

    def _norm(t):
        return re.sub(r"\s", "", t or "")

    def _tri(t):
        t = _norm(t)
        return set(t[i:i + 3] for i in range(len(t) - 2)) if len(t) >= 3 else set(t)

    def _cs(t):
        return set(_norm(t))

    char_sets = [_cs(r) for s, r in corpus]
    tris = [_tri(r) for s, r in corpus]
    inv = {}
    for i, tr in enumerate(tris):
        for g in tr:
            inv.setdefault(g, []).append(i)
    r10_fail = set()
    checked = 0
    n = len(recs)
    for i in range(n):
        seen = set()
        for g in tris[i]:
            for j in inv.get(g, []):
                if j <= i:
                    continue
                if j in seen:
                    continue
                seen.add(j)
                sa, sb = char_sets[i], char_sets[j]
                if not sa or not sb:
                    continue
                if len(sa & sb) / len(sa | sb) <= 0.5:
                    continue
                checked += 1
                si, ri = recs[i]
                sj, rj = corpus[j]
                if ri == rj:
                    r10_fail.add(si)
                    if sj != "EXIST":
                        r10_fail.add(sj)
                elif C.lcs_len(ri, rj) >= 15:
                    r10_fail.add(si)
                    if sj != "EXIST":
                        r10_fail.add(sj)
    print(f"  [R10] 比对 {checked} 对 | 失败 {len(r10_fail)} 家")

    final = [s for s in valid if s not in r10_fail]
    final_fail = fail_single + [(s, "R10:跨企业雷同") for s in r10_fail if s in valid]

    print(f"\n{'='*60}\nV5受控合并报告 (drafts_v5, 队列内 {len(by_serial)} 家)")
    print(f"  单企业PASS: {len(valid)}")
    print(f"  R10失败:    {len([s for s in r10_fail if s in valid])}")
    print(f"  最终写回:   {len(final)}")
    print(f"  不写回:     {len(final_fail)}")
    if final_fail:
        print("  不写回明细(前20):")
        for s, e in final_fail[:20]:
            print(f"    {s}: {e[:100]}")
        if len(final_fail) > 20:
            print(f"    ... 还有 {len(final_fail)-20} 家")

    if do_commit and final:
        for s in final:
            entry = db_idx[s]
            entry["recommend"] = valid[s].get("recommend")
            entry["update_time"] = "2026-07-19"
        save_db(db)
        print(f"\n已写回 {len(final)} 家 recommend（仅recommend字段，未动620干净企业，未碰drafts_v4）")
    elif not do_commit:
        print("\n[预览模式] 加 --commit 才实际写回主库")


if __name__ == "__main__":
    main()
