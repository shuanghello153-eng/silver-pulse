# -*- coding: utf-8 -*-
# 扫描所有 out/*.json 的 recommend 是否通过 L4（在合并进 DB 前先发现）
import json, glob, re, os
SIG_KW = ["信号"]
INFO_KW = ["信息", "资料", "披露", "数据", "透明度", "公开"]
DIFF_KW = ["差异", "独特", "打法", "模式", "定位", "反常识", "壁垒", "亮点"]
COPY_KW = ["复制", "借鉴", "可学", "照搬", "落地", "国内", "抄"]
FP = ["成立于", "创立于", "轮次",
      r"(A轮|B轮|C轮|D轮|E轮|F轮|Pre-?A轮?|天使轮|种子轮|Series\s?[A-Fa-f])",
      r"轮(融资|募|资金)", r"(本轮|上轮|前轮)", r"(融资|募|IPO|ipo|上市)[额次]",
      r"融[资了]?[约]?\d", r"\d+万?美元", r"\d+亿", r"\d+万元", r"\$\d"]

def is_regex(p):
    return ("\\" in p) or ("[" in p) or ("?" in p) or ("(" in p)

def forbidden(rec):
    for p in FP:
        if is_regex(p):
            if re.search(p, rec):
                return p
        elif p in rec:
            return p
    return None

issues = 0
for fn in sorted(glob.glob("out/batch_*_out.json")):
    data = json.load(open(fn, encoding="utf-8"))
    ents = data.get("enterprises", []) if isinstance(data, dict) else data
    print("=== %s (%d家) ===" % (fn, len(ents)))
    for e in ents:
        rec = e.get("recommend")
        s = e.get("serial"); nm = e.get("name")
        if not isinstance(rec, str) or not rec.strip():
            print("  [%s] %s: EMPTY recommend" % (s, nm)); issues += 1; continue
        L = len(rec)
        fpr = forbidden(rec)
        miss = []
        if not any(w in rec for w in SIG_KW): miss.append("信号")
        if not any(w in rec for w in INFO_KW): miss.append("信息")
        if not any(w in rec for w in DIFF_KW): miss.append("差异")
        if not any(w in rec for w in COPY_KW): miss.append("复制")
        flags = []
        if L < 30 or L > 200: flags.append("LEN%d" % L)
        if fpr: flags.append("FORBID:%s" % fpr)
        if miss: flags.append("MISS:%s" % ",".join(miss))
        if flags:
            print("  [%s] %s: %s" % (s, nm, " | ".join(flags)))
            print("       %s" % rec[:140])
            issues += 1
print("SCAN DONE, issues=%d" % issues)
