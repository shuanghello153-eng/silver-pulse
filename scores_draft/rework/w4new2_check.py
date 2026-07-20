# -*- coding: utf-8 -*-
"""w4-new2 自检/写出 公共模块。校验逻辑对齐 rework_merge.py：
对草稿里提供的 recommend/desc_cn/silver_reason/payor_model 全覆盖到上下文再跑 validate。"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))
DRAFTDIR = os.path.join(HERE, "drafts_v4")
sys.path.insert(0, HERE)
from check_single import validate

_db_cache = None

def load_db():
    global _db_cache
    if _db_cache is None:
        _db_cache = json.load(open(DB, encoding="utf-8"))
    return _db_cache

def write_drafts(recs):
    """recs: {serial: draft_dict} 写出 draft_<serial>.json"""
    os.makedirs(DRAFTDIR, exist_ok=True)
    for serial, d in recs.items():
        fn = os.path.join(DRAFTDIR, "draft_" + serial + ".json")
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=0)
    return len(recs)

def check(recs, skip=None):
    """recs: {serial: draft_dict(含recommend,可选desc_cn/silver_reason/payor_model)}。
    返回 (fails_dict, total)。skip 默认只跳过 R10（对齐 team-lead 要求）。
    注意：check_single.validate 的 R10 分支不读 skip，故用 others=None 真正关闭 R10。"""
    skip = skip or ["R10"]
    db = load_db()
    ctxmap = {e.get("serial"): e for e in db}
    fails = {}
    for serial, d in recs.items():
        e = dict(ctxmap.get(serial, {}))
        if isinstance(d, dict):
            for k in ("recommend", "desc_cn", "silver_reason", "payor_model"):
                if k in d and d[k] is not None:
                    e[k] = d[k]
        else:
            e["recommend"] = d
        iss = validate(e, others=None, skip=skip)
        if iss:
            fails[serial] = iss
    return fails, len(recs)

if __name__ == "__main__":
    db = load_db()
    ctxmap = {e.get("serial"): e for e in db}
    recs = {}
    for fn in os.listdir(DRAFTDIR):
        if fn.startswith("draft_") and fn.endswith(".json"):
            d = json.load(open(os.path.join(DRAFTDIR, fn), encoding="utf-8"))
            recs[d["serial"]] = d
    fails, total = check(recs)
    print(f"校验 {total} 家 | 通过 {total-len(fails)} | 未过 {len(fails)}")
    for s, iss in fails.items():
        print("  FAIL", s, iss)
