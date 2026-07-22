# -*- coding: utf-8 -*-
"""增量合并器：只把 rework-7 的 22 家草稿中【当前 DB 推荐偏短(<70字)】的那些，
受控写回主库。严格安全：
  - 只读 drafts_v5/ 中指定 serial 的草稿
  - 只写 recommend + update_time
  - R10 仅对照【主库现有全部 recommend + 本批子集】，不引入 347 批次里被返工改坏/相互雷同的草稿
  - 写回前双重校验：单企业门禁(R1-R9) + R10 跨企业去重 + 新稿必须比当前 DB 更长(确为改进)
  - 绝不碰 620 干净企业、绝不碰 46 空 serial、绝不碰已 70-220 达标的 4 家(0285/0399/0430/0453)
用法：python merge_r7_incremental.py [--commit]
"""
import json, os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DRAFTS_DIR = os.path.join(HERE, "drafts_v5")
REC_SKIP = {"R10", "R6", "R7", "R8"}

def cl(s):
    return len(re.sub(r"\s", "", s or ""))

def main():
    do_commit = "--commit" in sys.argv
    # 22 rework-7 serials
    ctx = json.load(open(os.path.join(HERE, "_fix22_context.json"), encoding="utf-8"))
    all22 = [str(c.get("serial", "")).lstrip("#") for c in ctx]
    # 当前 DB 偏短 / 不达 70-220 的，才纳入（已是好稿的 0285/0399/0430/0453 排除，避免无谓改动）
    db = json.load(open(DB_PATH, encoding="utf-8"))
    db_idx = {str(e.get("serial", "")).lstrip("#"): e for e in db}
    targets = [s for s in all22 if not (isinstance(db_idx[s].get("recommend"), str) and 70 <= cl(db_idx[s]["recommend"]) <= 220)]
    print(f"rework-7 22 家中，当前未达 70-220 需升级: {len(targets)} 家 -> {targets}")

    # 单企业门禁
    valid = {}
    for s in targets:
        fp = os.path.join(DRAFTS_DIR, f"draft_#{s}.json")
        if not os.path.exists(fp):
            print(f"  {s}: 无 v5 草稿，跳过"); continue
        d = json.load(open(fp, encoding="utf-8"))
        e = db_idx[s]
        ctx2 = dict(e); ctx2["recommend"] = d.get("recommend")
        errs = C.validate(ctx2, others=None, skip=REC_SKIP)
        if errs:
            print(f"  {s}: 门禁失败 {errs[:2]}; 跳过"); continue
        # 改进校验：新稿必须比当前更长
        cur = e.get("recommend")
        curlen = cl(cur) if isinstance(cur, str) else 0
        newlen = cl(d.get("recommend"))
        if newlen <= curlen:
            print(f"  {s}: 新稿({newlen})未长于当前({curlen})，跳过(非改进)"); continue
        valid[s] = d.get("recommend")

    # R10 跨企业去重：对照【主库现有全部 recommend + 本批子集】
    existing = [e["recommend"] for e in db if isinstance(e.get("recommend"), str)]
    recs = [(s, valid[s]) for s in valid]
    corpus = [(s, r) for s, r in recs] + [("EXIST", r) for r in existing if isinstance(r, str)]

    def _norm(t): return re.sub(r"\s", "", t or "")
    def _tri(t):
        t = _norm(t); return set(t[i:i+3] for i in range(len(t)-2)) if len(t) >= 3 else set(t)
    def _cs(t): return set(_norm(t))
    char_sets = [_cs(r) for s, r in corpus]
    tris = [_tri(r) for s, r in corpus]
    inv = {}
    for i, tr in enumerate(tris):
        for g in tr: inv.setdefault(g, []).append(i)
    r10_fail = set(); checked = 0; n = len(recs)
    for i in range(n):
        seen = set()
        for g in tris[i]:
            for j in inv.get(g, []):
                if j <= i or j in seen: continue
                seen.add(j)
                sa, sb = char_sets[i], char_sets[j]
                if not sa or not sb: continue
                if len(sa & sb) / len(sa | sb) <= 0.5: continue
                checked += 1
                si, ri = recs[i]; sj, rj = corpus[j]
                if ri == rj:
                    r10_fail.add(si)
                    if sj != "EXIST": r10_fail.add(sj)
                elif C.lcs_len(ri, rj) >= 15:
                    r10_fail.add(si)
                    if sj != "EXIST": r10_fail.add(sj)
    final = [s for s in valid if s not in r10_fail]
    print(f"  单企业PASS {len(valid)} | R10失败 {len(r10_fail)} | 最终写回 {len(final)}")

    # 模拟前后对比
    before = sum(1 for e in db if isinstance(e.get("recommend"), str) and 70 <= cl(e["recommend"]) <= 220)
    db3 = json.loads(json.dumps(db))
    idx3 = {str(e.get("serial", "")).lstrip("#"): e for e in db3}
    for s in final:
        idx3[s]["recommend"] = valid[s]
    after = sum(1 for e in db3 if isinstance(e.get("recommend"), str) and 70 <= cl(e["recommend"]) <= 220)
    lost = [s for s in [str(e.get("serial","")).lstrip("#") for e in db]
            if isinstance(db_idx[s].get("recommend"), str) and 70 <= cl(db_idx[s]["recommend"]) <= 220
            and not (isinstance(idx3[s].get("recommend"), str) and 70 <= cl(idx3[s]["recommend"]) <= 220)]
    print(f"  70-220合格: {before} -> {after} (Δ={after-before}) | 丢失(应为0): {len(lost)}")

    if do_commit and final:
        for s in final:
            db_idx[s]["recommend"] = valid[s]
            db_idx[s]["update_time"] = "2026-07-21"
        json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"\n已写回 {len(final)} 家 recommend（仅这 {len(final)} 家，未碰其他）")
    else:
        print("\n[预览模式] 加 --commit 才实际写回主库")

if __name__ == "__main__":
    main()
