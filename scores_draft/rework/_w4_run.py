# -*- coding: utf-8 -*-
"""Generic w4-1 runner: load batch + recommends.json, write drafts, run gate, print overlaps.
Usage: python _w4_run.py <batch_file.json> <recommends.json>
recommends.json: {"#XXXX": "recommend string", ...}
"""
import json, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_single import validate, _field_texts

def lcs_sub(a, b):
    a, b = re.sub(r"\s", "", a or ""), re.sub(r"\s", "", b or "")
    if not a or not b:
        return 0, ""
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    end = 0; best = 0
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

batch_file = sys.argv[1]
rec_file = sys.argv[2]
batch = json.load(open(batch_file, encoding="utf-8"))
RECS = json.load(open(rec_file, encoding="utf-8"))
ctx = {e["serial"]: e for e in batch}
OUT = os.path.join(HERE, "drafts_v4")
os.makedirs(OUT, exist_ok=True)

fails = {}
for serial, rec in RECS.items():
    if serial not in ctx:
        print("!! serial not in batch:", serial); continue
    out = {"serial": serial, "recommend": rec}
    fn = os.path.join(OUT, f"draft_{serial}.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    c = dict(ctx[serial]); c["recommend"] = rec
    iss = validate(c)
    if iss:
        fails[serial] = iss
        print("###", serial, "FAILS:", iss)
        for fname, ftext in _field_texts(c):
            t = 8
            for p, tv in THR.items():
                if fname.startswith(p):
                    t = tv; break
            ln, sub = lcs_sub(rec, ftext)
            if ln >= t:
                print(f"    [{ln}>={t}] {fname}: …{sub}…")

print("TOTAL", len(RECS), "FAIL", len(fails))
