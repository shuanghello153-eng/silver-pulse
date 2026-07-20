import json, os, sys, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import check_single as c
DB = c.DB
log = []
try:
    d = json.load(open(DB, encoding='utf-8'))
    log.append("loaded DB records=%d" % len(d))
    by = {str(e.get('serial', '')).lstrip('#'): e for e in d}
    f = "drafts_v5/draft_#1040.json"
    r = json.load(open(os.path.join(HERE, "..", f), encoding='utf-8'))
    s = r.get('serial', '')
    ctx = by.get(str(s).lstrip('#'), {})
    tmp = dict(ctx)
    tmp['recommend'] = r.get('recommend', '')
    iss = c.validate(tmp, others=[r.get('recommend','')], skip=['R6','R7','R8'])
    log.append("validate %s -> %s" % (s, iss))
except Exception:
    log.append("EXC: " + traceback.format_exc())
open(os.path.join(HERE, "test_one.log"), "w", encoding="utf-8").write("\n".join(log))
print("\n".join(log))
