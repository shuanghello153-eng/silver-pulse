# -*- coding: utf-8 -*-
"""真实门禁：把 drafts_v4 里每一家草稿，合并进主库对应条目后，逐家过 check_single.py。
分两种口径报：
  A) 推荐理由写作质量门禁（跳过 R6/R7/R8/R10，只看推荐理由文本本身）
  B) 全字段门禁（跳过 R10，看整条记录是否达标）
"""
import json, re, glob, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_single import validate

DB = json.load(open("../../data/enterprise/all_enterprises.json", encoding="utf-8"))
def norm(s): return re.sub(r"\D", "", str(s or ""))
db_by = {norm(e.get("serial")): e for e in DB}

SAFE = ["recommend", "desc_cn", "silver_reason", "payor_model", "update_time", "flag"]

def load_drafts():
    dv = {}
    for f in glob.glob("drafts_v4/*.json"):
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        ser = j.get("serial") or j.get("企业序号") or j.get("企业序号")
        if ser:
            dv[norm(ser)] = j
    return dv

dv = load_drafts()
print("草稿文件匹配DB家数:", len(dv), " / 主库:", len(DB))

rec_pass = rec_fail = 0
full_pass = full_fail = 0
rec_rules = collections.Counter()
full_rules = collections.Counter()
# 草稿携带字段情况
carry_full = carry_partial = carry_reconly = 0
rec_fail_examples = []
rec_pass_examples = []

for ser, j in dv.items():
    e = db_by.get(ser)
    if not e:
        continue
    r = j.get("recommend") or j.get("推荐理由")
    if not (isinstance(r, str) and r.strip()):
        continue
    # 合并：草稿带的 safe 字段覆盖主库
    e2 = dict(e)
    for k in SAFE:
        if k in j and j[k] is not None:
            e2[k] = j[k]

    # 携带字段统计
    has = lambda k: k in j and isinstance(j[k], str) and j[k].strip()
    cc = sum(1 for k in ("recommend", "desc_cn", "silver_reason", "payor_model") if (k == "recommend" or has(k)))
    if has("desc_cn") and has("silver_reason") and has("payor_model"):
        carry_full += 1
    elif has("desc_cn") or has("silver_reason") or has("payor_model"):
        carry_partial += 1
    else:
        carry_reconly += 1

    # A) 推荐理由写作质量
    iss_rec = validate(e2, None, skip={"R6", "R7", "R8", "R10"})
    # B) 全字段
    iss_full = validate(e2, None, skip={"R10"})

    if iss_rec:
        rec_fail += 1
        for i in iss_rec:
            rec_rules[i.split(":")[0]] += 1
        if len(rec_fail_examples) < 4:
            rec_fail_examples.append((ser, e.get("name_cn") or e.get("name"), r, iss_rec))
    else:
        rec_pass += 1
        if len(rec_pass_examples) < 3:
            rec_pass_examples.append((ser, e.get("name_cn") or e.get("name"), r))

    if iss_full:
        full_fail += 1
        for i in iss_full:
            full_rules[i.split(":")[0]] += 1
    else:
        full_pass += 1

N = rec_pass + rec_fail
print("\n=== A) 推荐理由写作质量门禁（只看文本本身，不含R6/R7/R8）===")
print(f"通过 {rec_pass} / 未过 {rec_fail} / 总计 {N}")
print("--- 未过原因分布 ---")
for k, v in rec_rules.most_common():
    print(f"  {k}: {v}")

print("\n=== B) 全字段门禁（含 desc/silver/payor）===")
print(f"通过 {full_pass} / 未过 {full_fail} / 总计 {N}")
print("--- 未过原因分布 ---")
for k, v in full_rules.most_common():
    print(f"  {k}: {v}")

print("\n=== 草稿携带字段情况（决定为什么全字段通过率低）===")
print(f"携带 recommend+desc+silver+payor 全4项: {carry_full}")
print(f"携带其中部分: {carry_partial}")
print(f"只携带 recommend(其余用主库旧值): {carry_reconly}")

print("\n=== 推荐理由写作『未过』真实样例（你能直接读，判断质量）===")
for ser, nm, r, iss in rec_fail_examples:
    print(f"\n■ {ser} | {nm}")
    print(f"  理由({len(re.sub(chr(32),'',r))}字): {r}")
    print(f"  门禁判死: {iss}")

print("\n=== 推荐理由写作『通过』真实样例 ===")
for ser, nm, r in rec_pass_examples:
    print(f"\n■ {ser} | {nm}")
    print(f"  理由({len(re.sub(chr(32),'',r))}字): {r}")
