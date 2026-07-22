# -*- coding: utf-8 -*-
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REWORK = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, REWORK)
from check_single import validate, content_len

BATCH = os.path.join(REWORK, "batches_score", "batch_49.json")
data = json.load(open(BATCH, encoding="utf-8"))

ok = 0
for e in data:
    serial = e.get("serial")
    rec = e.get("current_recommend")
    ctx = {
        "serial": serial,
        "name": e.get("name_cn") or "",
        "name_cn": e.get("name_cn") or "",
        "desc_cn": e.get("desc_cn") or "",
        "highlights": e.get("highlights") or [],
        "stage": e.get("stage") or "",
        "recommend": rec,
        "_is_v5_already": e.get("_is_v5_already"),
    }
    iss = validate(ctx)  # single -> R10 not triggered
    cl = content_len(rec)
    flag = "V5" if e.get("_is_v5_already") else "REW"
    status = "PASS" if not iss else "FAIL"
    if not iss:
        ok += 1
    print(f"[{status}] {serial} ({flag}) len={cl} :: {' | '.join(iss) if iss else ''}")

print(f"\nTOTAL {len(data)} | PASS {ok} | FAIL {len(data)-ok}")
