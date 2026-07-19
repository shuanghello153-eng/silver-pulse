# -*- coding: utf-8 -*-
import sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # rework dir holds check_single.py
DB = os.path.normpath(os.path.join(HERE, "..", "..", "..", "data/enterprise/all_enterprises.json"))

def run(serial):
    d = json.load(open(DB, encoding="utf-8"))
    rec = [x for x in d if x.get("serial") == serial]
    ctx = rec[0] if rec else {}
    fp = os.path.join(HERE, f"draft_{serial}.json")
    dr = json.load(open(fp, encoding="utf-8"))
    e = dict(ctx)
    for k, v in dr.items():
        if v is not None:
            e[k] = v
    import check_single
    iss = check_single.validate(e, others=None, skip={"R10"})
    print("PASS" if not iss else "FAIL: " + str(iss))
    return iss

if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(s, end=" -> ")
        run(s)
