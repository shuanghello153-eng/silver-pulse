# -*- coding: utf-8 -*-
"""只校验 rework 队列内的草稿（467家在队列里有草稿的），做 R1-R9 + 内部R10。
不碰 631 个 orphan 草稿（那是干净620的备份/旧脏管线残留），避免误覆盖主库干净串。
"""
import json, os, re, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DRAFTS_DIR = os.path.join(HERE, "drafts_v4")
QUEUE = json.load(open(os.path.join(HERE, "_rework_queue.json"), encoding="utf-8"))
qset = set(s.lstrip("#") for s in QUEUE)

db = json.load(open(DB_PATH, encoding="utf-8"))
db_idx = {str(e.get("serial","")).lstrip("#"): e for e in db}

# 收集 in-queue 草稿，按 serial 去重取最长
files = sorted(glob.glob(os.path.join(DRAFTS_DIR, "draft_*.json")))
by_serial = defaultdict(list)
for fp in files:
    try:
        d = json.load(open(fp, encoding="utf-8"))
    except Exception:
        continue
    s = str(d.get("serial","")).lstrip("#")
    if s in qset:
        by_serial[s].append(d)

draft_list = []
for s, lst in by_serial.items():
    best = max(lst, key=lambda d: C.content_len(d.get("recommend") or ""))
    draft_list.append((s, best))

print(f"队列内草稿去重后: {len(draft_list)} 家")

# 第一遍：单企业校验，分两种口径
#  (A) 全量 R1-R9 (skip R10) —— 用于看"其他字段(desc/silver/payor)问题"
#  (B) 只针对 recommend 文本质量 (skip R10,R6,R7,R8) —— 这才是合并决策依据
#      因为 R6/R7/R8 是关于公司其他字段，不是 recommend 返工范围，不能否决 recommend 合并。
REC_SKIP = {"R10","R6","R7","R8"}
pass_single = {}      # recommend 文本合格
fail_single = {}      # recommend 文本不合格
other_field_issues = {}  # 全量校验里 R6/R7/R8 等问题（仅供参考，不阻止合并）
for s, draft in draft_list:
    entry = db_idx.get(s)
    if not entry:
        fail_single[s] = ["库中未找到"]
        continue
    ctx = dict(entry)
    ctx["recommend"] = draft.get("recommend")
    for k in ("desc_cn","silver_reason","payor_model"):
        if k in draft and draft[k]:
            ctx[k] = draft[k]
    errs_full = C.validate(ctx, others=None, skip={"R10"})
    errs_rec = C.validate(ctx, others=None, skip=REC_SKIP)
    # 拆出 R6/R7/R8
    ofi = [e for e in errs_full if e.split(":")[0] in ("R6","R7","R8")]
    if errs_rec:
        fail_single[s] = errs_rec
    else:
        pass_single[s] = draft
        if ofi:
            other_field_issues[s] = ofi

print(f"recommend文本 PASS: {len(pass_single)} | FAIL: {len(fail_single)}")
print(f"  (其中另有 {len(other_field_issues)} 家 recommend合格但其他字段偏弱，合并时仍只写recommend，不写弱字段)")

# 第二遍：内部 R10（队内互比，仅 recommend 文本合格者）
recs = [(s, pass_single[s].get("recommend","")) for s in pass_single if isinstance(pass_single[s].get("recommend"),str)]
n = len(recs)
def _norm(t): return re.sub(r"\s","",t or "")
def _tri(t):
    t=_norm(t)
    return set(t[i:i+3] for i in range(len(t)-2)) if len(t)>=3 else set(t)
def _cs(t): return set(_norm(t))
char_sets=[_cs(r) for s,r in recs]
tris=[_tri(r) for s,r in recs]
inv={}
for i,tr in enumerate(tris):
    for g in tr: inv.setdefault(g,[]).append(i)
r10_fail=set()
checked=0
for i in range(n):
    seen=set()
    for g in tris[i]:
        for j in inv.get(g,[]):
            if j<=i or j in seen: continue
            seen.add(j)
            sa,sb=char_sets[i],char_sets[j]
            if not sa or not sb: continue
            if len(sa&sb)/len(sa|sb) <= 0.5: continue
            checked+=1
            si,ri=recs[i]; sj,rj=recs[j]
            if ri==rj:
                r10_fail.add(si); r10_fail.add(sj)
            elif C.lcs_len(ri,rj)>=15:
                r10_fail.add(si); r10_fail.add(sj)
print(f"内部R10 比对 {checked} 对 | 雷同失败 {len(r10_fail)} 家")

final_pass = [s for s in pass_single if s not in r10_fail]
final_fail = dict(fail_single)
for s in r10_fail:
    final_fail[s] = final_fail.get(s, []) + ["R10:队内雷同"]

print(f"\n最终 recommend-合格(待合并): {len(final_pass)}")
print(f"最终 recommend-不合格(需重洗): {len(final_fail)}")

# 失败原因聚合（仅 recommend 相关）
reason_counter = Counter()
for s, errs in final_fail.items():
    for e in errs:
        key = e.split(":")[0].split("（")[0]
        reason_counter[key]+=1
print("\n失败原因分布(recommend相关):")
for k,v in reason_counter.most_common():
    print(f"  {k}: {v}")

# 没草稿的队列 serials
no_draft = qset - set(by_serial.keys())
print(f"\n队列中完全没有草稿的 serials: {len(no_draft)}")
print(f"守恒检查: PASS {len(final_pass)} + FAIL {len(final_fail)} + 无草稿 {len(no_draft)} = {len(final_pass)+len(final_fail)+len(no_draft)} (应= {len(qset)})")

# 保存
out = {
    "final_pass": sorted(final_pass),
    "final_fail": {k: final_fail[k] for k in sorted(final_fail)},
    "other_field_issues": {k: other_field_issues[k] for k in sorted(other_field_issues)},
    "no_draft": sorted(no_draft),
}
json.dump(out, open(os.path.join(HERE, "_queue_validation.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n已存 _queue_validation.json")
