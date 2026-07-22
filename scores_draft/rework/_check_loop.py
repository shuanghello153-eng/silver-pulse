# -*- coding: utf-8 -*-
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_single as C

MYSER = ["0120","0199","0263","0296","0343","0373","0415","0438","0465","0498",
"0522","0546","0571","0595","0618","0640","0663","0689","0707","0731",
"0759","0778","0795","0821","0841","0859","0884","0912","0933","0955",
"0970","0993","1014","1031","1055","1068","1091","1104","1127","1152",
"1176","1193","1217","1240","1259","1276","1298","1313","1336","1360",
"1373","1398","1422","1439","1462","1483","1501","1524"]

fails = {}
passn = 0
for s in MYSER:
    fp = os.path.join(HERE, "drafts_v5", f"draft_#{s}.json")
    try:
        d = json.load(open(fp, encoding="utf-8"))
    except Exception as e:
        fails[s] = "LOAD:" + str(e)
        continue
    try:
        ctx = C._ctx_from_db(d.get("serial", ""))
        tmp = dict(ctx)
        for k in ("recommend", "desc_cn", "highlights", "stage", "funding_latest", "funding_total"):
            if k in d and d[k] is not None:
                tmp[k] = d[k]
        iss = C.validate(tmp)
    except Exception as e:
        fails[s] = "EXC:" + str(e)
        continue
    if iss:
        fails[s] = iss
    else:
        passn += 1

print("PASS", passn, "FAIL", len(fails))
for k, v in fails.items():
    print("FAIL", k, v)
