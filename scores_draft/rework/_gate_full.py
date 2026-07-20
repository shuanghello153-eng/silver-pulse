# -*- coding: utf-8 -*-
import json, sys, collections, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_single import validate

DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))
d = json.load(open(DB, encoding="utf-8"))
others = [e.get("recommend", "") for e in d if isinstance(e.get("recommend"), str)]
passc = 0
failc = 0
reason_counter = collections.Counter()
dict_cnt = 0
str_cnt = 0
for e in d:
    r = e.get("recommend")
    if isinstance(r, dict):
        dict_cnt += 1
    elif isinstance(r, str):
        str_cnt += 1
    try:
        iss = validate(e, None)  # skip R10 (O(n^2) too slow for full scan)
    except Exception as ex:
        iss = ["EXC:" + str(ex)]
    if iss:
        failc += 1
        for i in iss:
            reason_counter[i.split(":")[0]] += 1
    else:
        passc += 1
print("=== V4 gate full DB", len(d), "===")
print("PASS:", passc, "FAIL:", failc)
print("dict recommend:", dict_cnt, "str recommend:", str_cnt)
print("--- fail reason by rule ---")
for k, v in reason_counter.most_common(25):
    print("  %s: %d" % (k, v))
