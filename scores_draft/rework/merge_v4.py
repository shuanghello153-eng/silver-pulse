# -*- coding: utf-8 -*-
"""
V4 合并器：把 drafts_v4/ 下的工人草稿合并回主库 all_enterprises.json。
校验策略：先逐家做单企业V4校验(R1-R-novelty，不含R10)，再做跨企业R10校验。
只有两步都通过的企业才写回主库；R10失败的不写回（不污染主库）。

用法：python merge_v4.py [--commit] [--drafts-dir drafts_v4]
"""
import json, os, sys, glob, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DRAFTS_DIR = os.path.join(HERE, "drafts_v4")


def load_db():
    return json.load(open(DB_PATH, encoding="utf-8"))


def save_db(db):
    json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"已保存主库: {DB_PATH} ({len(db)}家)")


def find_drafts(drafts_dir=None):
    d = drafts_dir or DRAFTS_DIR
    # 修复：原只匹配 draft_#*.json，漏掉 241 份命名 draft_0013.json（无#）的草稿，
    # 其中 120 家为独有 serial，会永久丢失。改为同时匹配两种命名。
    files = sorted(glob.glob(os.path.join(d, "draft_*.json")))
    return files


def main():
    do_commit = "--commit" in sys.argv
    drafts_dir = None
    for i, a in enumerate(sys.argv):
        if a == "--drafts-dir" and i + 1 < len(sys.argv):
            drafts_dir = sys.argv[i + 1]

    draft_files = find_drafts(drafts_dir)
    if not draft_files:
        print(f"未找到任何草稿文件: {DRAFTS_DIR}")
        sys.exit(1)

    # 去重：同一 serial 可能有多版草稿（# 版与无# 版），取 recommend 最长（最完整）的一版
    from collections import defaultdict
    by_serial = defaultdict(list)
    for fp in draft_files:
        try:
            d = json.load(open(fp, encoding="utf-8"))
        except Exception:
            continue
        s = d.get("serial", "")
        if s:
            by_serial[s].append(d)
    draft_list = []
    dup_count = 0
    for s, lst in by_serial.items():
        if len(lst) > 1:
            dup_count += 1
        best = max(lst, key=lambda d: C.content_len(d.get("recommend") or ""))
        draft_list.append(best)

    print(f"找到 {len(draft_files)} 个草稿文件 → 去重后 {len(draft_list)} 家（含 {dup_count} 家多版本已择优）")

    db = load_db()
    db_idx = {e["serial"]: e for e in db}

    # ── 第一遍：单企业内部校验(R1-R-novelty，不含R10) ──
    # 只收集“通过单企业校验”的草稿，暂不改主库
    valid_serials = []          # 单企业校验通过的serial
    valid_drafts = {}           # serial -> draft（通过单企业校验）
    fail_single = []
    flag_list = []

    t0 = time.time()
    for draft in draft_list:
        serial = draft.get("serial", "")
        entry = db_idx.get(serial)
        if not entry:
            fail_single.append((serial, f"库中未找到{serial}"))
            continue
        # 用草稿recommend + 主库其它字段构造完整上下文做校验
        ctx = dict(entry)
        ctx["recommend"] = draft.get("recommend")
        for k in ("desc_cn", "silver_reason", "payor_model"):
            if k in draft and draft[k]:
                ctx[k] = draft[k]
        errs = C.validate(ctx, others=None, skip={"R10"})
        if errs:
            fail_single.append((serial, "; ".join(errs)))
        else:
            valid_serials.append(serial)
            valid_drafts[serial] = draft
            flag = draft.get("flag")
            if flag:
                flag_list.append(flag)

    dt_single = time.time() - t0

    # ── 第二遍：跨企业R10校验（仅对通过第一遍的）──
    # 修复：原实现 validate(others=全部) 做 O(n^2) 全量 LCS，约1000条时直接卡死被杀。
    # 现方案：3-gram 倒排只找"有公共3字子串"的候选对；对每对先用【字符集Jaccard】
    # 做廉价初筛(>0.5 才可能雷同)，只有初筛过的才跑昂贵 LCS。判断口径与门禁R10一致
    # （lcs_len>=15 且 Jaccard>0.5，或完全重合）。
    import re as _re
    valid_recs = [(s, valid_drafts[s].get("recommend", "")) for s in valid_serials
                  if isinstance(valid_drafts[s].get("recommend"), str)]
    n = len(valid_recs)

    def _norm(t):
        return _re.sub(r"\s", "", t or "")

    def _trigrams(t):
        t = _norm(t)
        if len(t) < 3:
            return set(t)
        return set(t[i:i + 3] for i in range(len(t) - 2))

    def _charset(t):
        t = _norm(t)
        return set(t) if t else set()

    char_sets = [_charset(r) for s, r in valid_recs]
    tris = [_trigrams(r) for s, r in valid_recs]
    inv = {}
    for i, tr in enumerate(tris):
        for g in tr:
            inv.setdefault(g, []).append(i)
    r10_fail_set = set()
    r10_fail_detail = []
    checked = 0
    for i in range(n):
        seen = set()
        for g in tris[i]:
            for j in inv.get(g, []):
                if j <= i or j in seen:
                    continue
                seen.add(j)
                sa, sb = char_sets[i], char_sets[j]
                if not sa or not sb:
                    continue
                # 廉价初筛：字符集重叠不超过0.5 → 字面/意思都不雷同，直接跳过
                if len(sa & sb) / len(sa | sb) <= 0.5:
                    continue
                checked += 1
                s_i, r_i = valid_recs[i]
                s_j, r_j = valid_recs[j]
                if r_i == r_j:
                    r10_fail_set.add(s_i); r10_fail_set.add(s_j)
                    r10_fail_detail.append((s_i, f"R10:跨企业与{s_j}完全重合"))
                elif C.lcs_len(r_i, r_j) >= 15:
                    r10_fail_set.add(s_i); r10_fail_set.add(s_j)
                    r10_fail_detail.append((s_i, f"R10:跨企业与{s_j}雷同(重合>0.5)"))
    print(f"  [R10] 候选对初筛后实际比对: {checked} 对", flush=True)

    final_pass = [s for s in valid_serials if s not in r10_fail_set]
    final_fail = fail_single + [(s, d) for s, d in r10_fail_detail]

    total_time = time.time() - t0
    print(f"\n{'='*60}")
    print(f"V4合并报告 ({len(draft_list)}家去重后草稿)")
    print(f"{'='*60}")
    print(f"  单企业PASS:   {len(valid_serials)}")
    print(f"  单企业FAIL:   {len(fail_single)}")
    print(f"  R10跨企业FAIL:{len(r10_fail_detail)}")
    print(f"  最终PASS:     {len(final_pass)}")
    print(f"  最终FAIL:     {len(final_fail)}")
    print(f"  耗时:         {total_time:.1f}s")

    if final_fail:
        print(f"\n  FAIL明细:")
        for s, errs in final_fail[:20]:
            print(f"    {s}: {errs[:120]}")
        if len(final_fail) > 20:
            print(f"    ... 还有 {len(final_fail)-20} 家")

    if flag_list:
        print(f"\n  源数据疑误flag({len(flag_list)}条):")
        for f in flag_list:
            print(f"    {f}")

    # ── 写回：只有最终PASS的企业才改主库 ──
    written = 0
    if do_commit and final_pass:
        for s in final_pass:
            draft = valid_drafts[s]
            entry = db_idx[s]
            if "recommend" in draft:
                entry["recommend"] = draft["recommend"]
            if "desc_cn" in draft:
                entry["desc_cn"] = draft["desc_cn"]
            if "silver_reason" in draft:
                entry["silver_reason"] = draft["silver_reason"]
            if "payor_model" in draft:
                entry["payor_model"] = draft["payor_model"]
            entry["update_time"] = "2026-07-18"
            written += 1
        save_db(db)
        print(f"\n 已写回主库: {written} 家 PASS（R10失败{len(r10_fail_detail)}家未写回）")
    elif not do_commit:
        print(f"\n [预览模式] 加 --commit 参数才实际写回主库（本次不会改动主库）")

    # 保存flag清单
    if flag_list:
        flags_path = os.path.join(HERE, "flags_v4.json")
        json.dump(flag_list, open(flags_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"  flags已存: {flags_path}")


if __name__ == "__main__":
    main()
