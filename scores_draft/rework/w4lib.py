# -*- coding: utf-8 -*-
"""Reusable rewrite worker for w4-new1. Process one batch: write recommends + field fixes, self-check (skip R10)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_single as C

OUT = os.path.join(HERE, "drafts_v4")

def process(BATCH, RECOMMENDS, DESC_FIX=None, SILVER_FIX=None, PAYOR_FIX=None):
    DESC_FIX = DESC_FIX or {}
    SILVER_FIX = SILVER_FIX or {}
    PAYOR_FIX = PAYOR_FIX or {}
    data = json.load(open(os.path.join(HERE, "batches_full", BATCH), encoding="utf-8"))
    by = {e["serial"]: e for e in data}
    fails = 0
    skip = 0
    for serial, rec in RECOMMENDS.items():
        if serial not in by:
            print("WARN skip %s (not in %s)" % (serial, BATCH))
            skip += 1
            continue
        e = dict(by[serial])
        e["recommend"] = rec
        if serial in DESC_FIX: e["desc_cn"] = DESC_FIX[serial]
        if serial in SILVER_FIX: e["silver_reason"] = SILVER_FIX[serial]
        if serial in PAYOR_FIX: e["payor_model"] = PAYOR_FIX[serial]
        iss = C.validate(e, skip={"R10"})
        draft = {"serial": serial, "recommend": rec}
        if serial in DESC_FIX: draft["desc_cn"] = DESC_FIX[serial]
        if serial in SILVER_FIX: draft["silver_reason"] = SILVER_FIX[serial]
        if serial in PAYOR_FIX: draft["payor_model"] = PAYOR_FIX[serial]
        fn = os.path.join(OUT, "draft_%s.json" % serial.replace("#", ""))
        json.dump(draft, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        if iss:
            fails += 1
            print("FAIL", serial, iss)
        else:
            print("PASS", serial)
    print("=== %s: %d entries, fails: %d, skipped: %d ===" % (BATCH, len(RECOMMENDS), fails, skip))
    return fails
