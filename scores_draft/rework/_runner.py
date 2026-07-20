# -*- coding: utf-8 -*-
"""独立合并执行器：复用 check_single 门禁，避免 merge_v4.main 的 stdout 被沙箱吞掉。
分两步：先只跑校验写报告(_runner_report.txt)，确认后再写回主库。
"""
import json, glob, os, sys, time, re
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DRAFTS_DIR = os.path.join(HERE, "drafts_v4")

DO_WRITE = "--write" in sys.argv

log = open(os.path.join(HERE, "_runner_log.txt"), "w", encoding="utf-8")
def L(*a):
    s = " ".join(map(str, a))
    log.write(s + "\n"); log.flush()
    print(s, flush=True)

t0 = time.time()
draft_files = sorted(glob.glob(os.path.join(DRAFTS_DIR, "draft_*.json")))
L("草稿文件:", len(draft_files))

by_serial = defaultdict(list)
for fp in draft_files:
    try:
        d = json.load(open(fp, encoding="utf-8"))
    except Exception:
        continue
    s = d.get("serial", "")
    if s:
        by_serial[s].append(d)
draft_list = [max(v, key=lambda d: C.content_len(d.get("recommend") or "")) for v in by_serial.values()]
L("去重后草稿:", len(draft_list), " 多版本已择优:", sum(1 for v in by_serial.values() if len(v) > 1))

db = json.load(open(DB_PATH, encoding="utf-8"))
db_idx = {e["serial"]: e for e in db}
L("主库:", len(db))

# 第一遍：单企业校验
valid_serials = []
valid_drafts = {}
fail_single = []
flag_list = []
for draft in draft_list:
    serial = draft.get("serial", "")
    entry = db_idx.get(serial)
    if not entry:
        fail_single.append((serial, "库中未找到"))
        continue
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
        if draft.get("flag"):
            flag_list.append(draft["flag"])
L("单企业 PASS:", len(valid_serials), " FAIL:", len(fail_single))

# 第二遍：快速跨企业 R10（bigram 倒排索引筛候选）
def _bigrams(t):
    t = re.sub(r"\s", "", t)
    return set(t[i:i + 2] for i in range(len(t) - 1)) if len(t) >= 2 else set(t)
valid_recs = [(s, valid_drafts[s].get("recommend", "")) for s in valid_serials
              if isinstance(valid_drafts[s].get("recommend"), str)]
n = len(valid_recs)
bgs = [_bigrams(r) for s, r in valid_recs]
inv = {}
for i, bg in enumerate(bgs):
    for g in bg:
        inv.setdefault(g, []).append(i)
cand = set()
for i in range(n):
    seen = set()
    for g in bgs[i]:
        for j in inv.get(g, []):
            if j > i and j not in seen:
                seen.add(j); cand.add((i, j))
r10_fail = set()
r10_detail = []
for i, j in cand:
    si, ri = valid_recs[i]; sj, rj = valid_recs[j]
    if ri == rj:
        r10_fail.add(si); r10_fail.add(sj)
        r10_detail.append((si, f"R10:跨企业与{sj}完全重合")); continue
    ov = C.lcs_len(ri, rj)
    if ov >= 15:
        sa = set(re.sub(r"\s", "", ri)); sb = set(re.sub(r"\s", "", rj))
        if sa and sb and len(sa & sb) / len(sa | sb) > 0.5:
            r10_fail.add(si); r10_fail.add(sj)
            r10_detail.append((si, f"R10:跨企业与{sj}雷同(重合>0.5)"))
L("R10 候选对:", len(cand), " R10 FAIL:", len(r10_fail))

final_pass = [s for s in valid_serials if s not in r10_fail]
final_fail = fail_single + r10_detail
L("最终 PASS:", len(final_pass), " 最终 FAIL:", len(final_fail))
L("耗时: %.1fs" % (time.time() - t0))

if flag_list:
    L("源数据疑误 flag 数:", len(flag_list))
    json.dump(flag_list, open(os.path.join(HERE, "flags_v4.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

if final_fail:
    L("--- FAIL 明细(前30) ---")
    for s, e in final_fail[:30]:
        L("  ", s, e[:100])

# 写回主库
if DO_WRITE and final_pass:
    written = 0
    for s in final_pass:
        d = valid_drafts[s]; e = db_idx[s]
        if "recommend" in d: e["recommend"] = d["recommend"]
        if "desc_cn" in d: e["desc_cn"] = d["desc_cn"]
        if "silver_reason" in d: e["silver_reason"] = d["silver_reason"]
        if "payor_model" in d: e["payor_model"] = d["payor_model"]
        e["update_time"] = "2026-07-19"
        written += 1
    json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    L("已写回主库:", written, "家")

L("=== DONE ===")
