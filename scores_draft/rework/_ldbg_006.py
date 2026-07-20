# -*- coding: utf-8 -*-
"""提娶 recommend 与字段的最长公共子串，定位 R-field-dedup 重叠。"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
sys.path.insert(0, HERE)
from check_single import _field_texts
import importlib
cs = importlib.import_module("check_single")

def lcs_sub(a, b):
    a = cs.re.sub(r"\s", "", a); b = cs.re.sub(r"\s", "", b)
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    end = 0; best = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1]+1
                if dp[i][j] > best:
                    best = dp[i][j]; end = i
            else:
                dp[i][j] = 0
    return a[end-best:end], best

# 复用 _gen 里的 RECOMMENDS（直接重新读取）
src = open(os.path.join(HERE, "_gen_w4_2_006.py"), encoding="utf-8").read()
ns = {"__file__": os.path.join(HERE, "_gen_w4_2_006.py")}
exec(src.split("def ser")[0], ns)  # 仅执行到 RECOMMENDS 定义前
RECOMMENDS = ns["RECOMMENDS"]

d = json.load(open(DB, encoding="utf-8"))
by = {str(e.get("serial","")).lstrip("#"): e for e in d}

fails = ["#1059","#0849","#0667","#1162","#1167","#1320","#0480","#0481"]
for s in fails:
    e = by[s.lstrip("#")]
    r = RECOMMENDS[s]
    print(f"\n===== {s} =====")
    for fname, ftext in _field_texts(e):
        sub, ln = lcs_sub(r, ftext)
        thr = 8
        for p,t in {"desc_cn":10,"silver_reason":10,"description":10,"highlights":8,"funding_latest":8,"funding_total":8}.items():
            if fname.startswith(p): thr=t; break
        if ln >= thr:
            print(f"  [{fname}] LCS={ln}(>= {thr}): 「{sub}」")
