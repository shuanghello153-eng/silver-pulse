import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))
db = json.load(open(DB, encoding="utf-8"))
by={e["serial"]:e for e in db}
# 取脏清单前6家
dirty=json.load(open("_dirty_R10.json",encoding="utf-8"))["dirty_serials"][:6]
for s in dirty:
    e=by.get(s,{})
    name=e.get("name") or e.get("公司名称") or "?"
    biz=e.get("business") or e.get("业务") or e.get("简介") or ""
    comp=e.get("国内竞品") or e.get("竞品") or ""
    rec=e.get("recommend") or ""
    print("="*60)
    print(f"[{s}] {name}")
    print(f"  业务: {str(biz)[:140]}")
    print(f"  国内竞品: {str(comp)[:100]}")
    print(f"  recommend({len(rec)}字): {rec}")
