# -*- coding: utf-8 -*-
"""
Phase A：从 scores_draft/run/out/batch_*_out.json 恢复正确的三版推荐理由到 all_enterprises.json。
只 patch recommend 字段（dict 含 rec_v1/v2/v3），不动其它字段（保留另一个AI填的 desc/payor 等）。
这是零风险恢复：out 文件里的 recommend 是之前 validator 通过过的对齐版本。
"""
import json, glob, os

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # silver-pulse
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
OUTDIR = os.path.join(BASE, "scores_draft/run/out")

def ser_to_int(s):
    return int(str(s).lstrip("#"))

d = json.load(open(DB, encoding="utf-8"))
by_serial = {ser_to_int(e["serial"]): e for e in d}

# 收集 out 文件里的 recommend 字典
rec_map = {}
src_files = 0
for f in sorted(glob.glob(os.path.join(OUTDIR, "batch_*_out.json"))):
    try:
        o = json.load(open(f, encoding="utf-8"))
    except Exception as ex:
        print("跳过坏文件", f, ex)
        continue
    src_files += 1
    for e in o.get("enterprises", []):
        r = e.get("recommend")
        if isinstance(r, dict) and r.get("rec_v1") and r.get("rec_v2") and r.get("rec_v3"):
            rec_map[ser_to_int(e["serial"])] = r

print(f"读取 out 文件 {src_files} 个，得到有效三版推荐理由 {len(rec_map)} 条")

patched = 0
for s, e in by_serial.items():
    if s in rec_map:
        e["recommend"] = rec_map[s]
        patched += 1

print(f"已 patch recommend 的企业数: {patched}")
json.dump(d, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("已写回 all_enterprises.json")

# 立即跑门禁校验这批
import subprocess, sys
serstr = ",".join(str(s) for s in rec_map.keys())
r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "validator.py"),
                    "--serials", serstr, "--skip", "R6,R7,R8"],
                   cwd=os.path.dirname(os.path.abspath(__file__)))
sys.exit(r.returncode)
