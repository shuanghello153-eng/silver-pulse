# -*- coding: utf-8 -*-
# 载入 DB 原记录 → 应用覆盖字段 → 写出 draft_#XXXX.json（保留所有未覆盖字段）
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "..", "data/enterprise/all_enterprises.json"))

def main():
    serial = sys.argv[1]
    ovf = sys.argv[2]
    d = json.load(open(DB, encoding="utf-8"))
    rec = [x for x in d if x.get("serial") == serial]
    if not rec:
        print("NOT FOUND", serial); sys.exit(1)
    rec = rec[0]
    ov = json.load(open(ovf, encoding="utf-8"))
    for k, v in ov.items():
        if v is not None:
            rec[k] = v
    out = os.path.join(HERE, f"draft_{serial}.json")
    json.dump(rec, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("WROTE", out)

if __name__ == "__main__":
    main()
