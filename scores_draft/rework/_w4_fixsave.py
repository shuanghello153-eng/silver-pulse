# -*- coding: utf-8 -*-
"""w4-fix: 用新 recommend 替换草稿并跑门禁（逐条，不做跨企业R10）。
输入：一个 json 文件，内容为 {serial(数字串或#xxxx): recommend字符串}
用法：
  python _w4_fixsave.py myfix.json            # 只校验，打印违规与冲突子串
  python _w4_fixsave.py myfix.json --save     # 校验通过才写盘
diagnostic: 对每条 R-field-dedup 打印最长公共子串，便于改写。
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_single import validate, _field_texts

BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
db = json.load(open(DB, encoding="utf-8"))
by = {str(x.get("serial", "")).lstrip("#"): x for x in db}

def lcs_sub(a, b):
    a, b = re.sub(r"\s", "", a or ""), re.sub(r"\s", "", b or "")
    if not a or not b: return 0, ""
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    end = best = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                if dp[i][j] > best:
                    best = dp[i][j]; end = i
            else:
                dp[i][j] = 0
    return best, a[end-best:end]

THR = {"desc_cn":10,"silver_reason":10,"description":10,"highlights":8,"funding_latest":8,"funding_total":8}

src = json.load(open(sys.argv[1], encoding="utf-8"))
save = "--save" in sys.argv
allok = True
for skey, rec in src.items():
    # 支持两种格式：字符串(仅recommend) 或 dict(含 recommend/payor_model/desc_cn/silver_reason)
    if isinstance(rec, dict):
        rec_text = rec.get("recommend")
        extra = {k: rec[k] for k in ("payor_model", "desc_cn", "silver_reason") if k in rec}
    else:
        rec_text = rec
        extra = {}
    s = str(skey).lstrip("#")
    e = by.get(s)
    if not e:
        print("### %s NOT IN DB" % s); allok = False; continue
    dp = os.path.join(HERE, "drafts_v4", "draft_%s.json" % e.get("serial"))   # draft_#XXXX.json (canonical)
    leg = os.path.join(HERE, "drafts_v4", "draft_%s.json" % s)                # draft_XXXX.json (legacy, 无#)
    # 合并草稿：先读 legacy 再读 #，保证 # 优先
    draft = {}
    for p in (leg, dp):
        if os.path.exists(p):
            draft.update(json.load(open(p, encoding="utf-8")))
    cand = dict(e)  # 以库内全字段卡为基准（含 desc/silver/tags/payor）
    # 草稿里若改过这些字段则并入；否则用库内值
    for k in ("desc_cn","silver_reason","payor_model"):
        if k in draft and draft[k] is not None:
            cand[k] = draft[k]
    # 本批次提供的修正（优先级最高）
    for k, v in extra.items():
        if v is not None:
            cand[k] = v
    cand["recommend"] = rec_text
    iss = validate(cand)  # others=None 跳过R10
    print("\n### %s  %s" % (e.get("serial"), "PASS" if not iss else "FAIL"))
    if iss:
        allok = False
        for it in iss:
            print("   -", it)
        # 详细 dedup 冲突子串
        if any(it.startswith("R-field-dedup") for it in iss):
            c = dict(e)
            for k in ("desc_cn","silver_reason","payor_model"):
                if k in draft and draft[k] is not None: c[k] = draft[k]
            for fname, ftext in _field_texts(c):
                t = 8
                for p, tv in THR.items():
                    if fname.startswith(p): t = tv; break
                ln, sub = lcs_sub(rec, ftext)
                if ln >= t:
                    print(f"     [>{t}] {fname}: …{sub}…")
    if save and not iss:
        json.dump(cand, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("   -> 已写盘", dp)
        # 同步 legacy 无#文件（若已存在），防止合并阶段 last-write-wins 被旧稿覆盖
        if os.path.exists(leg) and os.path.abspath(leg) != os.path.abspath(dp):
            json.dump(cand, open(leg, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            print("   -> 已同步 legacy", leg)
print("\n==== ALL OK:", allok, "====")
