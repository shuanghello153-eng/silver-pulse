# -*- coding: utf-8 -*-
"""
scoped merge：只处理 _new_serials.txt 里列出的"新产草稿"，
逐家过单企业门禁(R1-R-novelty, 不含R10)，再做 R10 跨企业查重
（新草稿之间 + 新草稿 vs 主库已合并的好字符串）。
只有两步都过的才写回主库。用法：
  python merge_scoped.py            # 预览
  python merge_scoped.py --commit   # 实际写回
"""
import json, os, sys, glob, re, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_single as C

BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DRAFTS_DIR = os.path.join(HERE, "drafts_v4")
SERIAL_FILE = os.path.join(HERE, "_new_serials.txt")

do_commit = "--commit" in sys.argv


def load_db():
    return json.load(open(DB_PATH, encoding="utf-8"))


def save_db(db):
    json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def find_draft(serial):
    cands = [
        os.path.join(DRAFTS_DIR, f"draft_#{serial}.json"),
        os.path.join(DRAFTS_DIR, f"draft_{serial}.json"),
    ]
    files = [f for f in cands if os.path.exists(f)]
    if not files:
        return None
    best = None
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if best is None or C.content_len(d.get("recommend") or "") > C.content_len(best.get("recommend") or ""):
            best = d
    return best


def main():
    serials = []
    for line in open(SERIAL_FILE, encoding="utf-8"):
        serials += line.split()
    print(f"待处理新草稿 serial 数: {len(serials)}", flush=True)

    db = load_db()
    db_idx = {e.get("serial"): e for e in db}

    # ── 第一遍：单企业门禁 ──
    valid_serials = []
    valid_drafts = {}
    fail_single = []
    for serial in serials:
        draft = find_draft(serial)
        if not draft:
            fail_single.append((serial, "未找到草稿文件"))
            continue
        entry = db_idx.get(serial) or db_idx.get("#" + serial)
        if not entry:
            fail_single.append((serial, "库中未找到该serial"))
            continue
        ctx = dict(entry)
        ctx["recommend"] = draft.get("recommend")
        for k in ("desc_cn", "silver_reason", "payor_model"):
            if draft.get(k):
                ctx[k] = draft[k]
        errs = C.validate(ctx, others=None, skip={"R10"})
        if errs:
            fail_single.append((serial, "; ".join(errs)))
        else:
            valid_serials.append(serial)
            valid_drafts[serial] = draft
    print(f"单企业PASS: {len(valid_serials)}  FAIL: {len(fail_single)}", flush=True)

    # ── 第二遍：R10 跨企业（新草稿之间 + 新 vs 已合并好字符串） ──
    def _norm(t):
        return re.sub(r"\s", "", t or "")

    def _trigrams(t):
        t = _norm(t)
        return set(t[i:i + 3] for i in range(len(t) - 2)) if len(t) >= 3 else set(t)

    def _charset(t):
        t = _norm(t)
        return set(t) if t else set()

    # 已合并的好字符串（主库里长度>=70的字符串 recommend）
    merged_recs = []
    for e in db:
        r = e.get("recommend")
        if isinstance(r, str) and C.content_len(r) >= 70:
            merged_recs.append((e.get("serial"), r))

    new_recs = [(s, valid_drafts[s].get("recommend", "") ) for s in valid_serials
                if isinstance(valid_drafts[s].get("recommend"), str)]

    # 候选池：新草稿在前，已合并在后（索引区分）
    all_recs = new_recs + merged_recs
    n_new = len(new_recs)
    n_all = len(all_recs)
    char_sets = [_charset(r) for s, r in all_recs]
    tris = [_trigrams(r) for s, r in all_recs]
    inv = {}
    for i, tr in enumerate(tris):
        for g in tr:
            inv.setdefault(g, []).append(i)

    r10_fail = set()
    r10_detail = []
    checked = 0
    for i in range(n_all):
        if i >= n_new:
            continue  # 只以新草稿为基准查重
        seen = set()
        for g in tris[i]:
            for j in inv.get(g, []):
                if j <= i or j in seen:
                    continue
                seen.add(j)
                sa, sb = char_sets[i], char_sets[j]
                if not sa or not sb:
                    continue
                if len(sa & sb) / len(sa | sb) <= 0.5:
                    continue
                checked += 1
                s_i, r_i = all_recs[i]
                s_j, r_j = all_recs[j]
                if r_i == r_j:
                    r10_fail.add(s_i)
                    r10_detail.append((s_i, f"R10:与{s_j}完全重合"))
                elif C.lcs_len(r_i, r_j) >= 15:
                    r10_fail.add(s_i)
                    r10_detail.append((s_i, f"R10:与{s_j}雷同(重合>0.5)"))
    print(f"[R10] 实际比对候选对: {checked}  新草稿被拦: {len(r10_fail)}", flush=True)

    final_pass = [s for s in valid_serials if s not in r10_fail]
    final_fail = fail_single + [(s, d) for s, d in r10_detail]

    print("=" * 60)
    print(f"scoped合并报告 (新草稿 {len(serials)} 家)")
    print(f"  单企业PASS:   {len(valid_serials)}")
    print(f"  R10拦下:      {len(r10_detail)}")
    print(f"  最终PASS:     {len(final_pass)}")
    print(f"  最终FAIL:     {len(final_fail)}")
    if final_fail:
        print("  FAIL明细(前25):")
        for s, d in final_fail[:25]:
            print(f"    {s}: {d[:130]}")
        if len(final_fail) > 25:
            print(f"    ...还有 {len(final_fail) - 25} 家")
    print("=" * 60)

    if do_commit and final_pass:
        written = 0
        for s in final_pass:
            d = valid_drafts[s]
            e = db_idx.get(s) or db_idx.get("#" + s)
            if d.get("recommend"):
                e["recommend"] = d["recommend"]
            if d.get("desc_cn"):
                e["desc_cn"] = d["desc_cn"]
            if d.get("silver_reason"):
                e["silver_reason"] = d["silver_reason"]
            if d.get("payor_model"):
                e["payor_model"] = d["payor_model"]
            e["update_time"] = "2026-07-19"
            written += 1
        save_db(db)
        print(f"已写回主库: {written} 家（含 recommend/desc_cn/silver_reason/payor_model）")
    else:
        print("[预览模式] 加 --commit 才写回主库")


if __name__ == "__main__":
    main()
