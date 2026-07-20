import json, glob, os, sys, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import check_single as c
DB = c.DB
LOG = os.path.join(HERE, "selftest.log")
def log(msg):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(msg + "\n")
open(LOG, "w", encoding="utf-8").write("")
try:
    d = json.load(open(DB, encoding='utf-8'))
    by = {str(e.get('serial', '')).lstrip('#'): e for e in d}
    my = set()
    for b in range(22, 32):
        arr = json.load(open(os.path.join(HERE, "..", "_batches", "batch_%03d.json" % b), encoding='utf-8'))
        my.update(arr)
    DD = os.path.join(HERE, "..", "drafts_v5")
    allf = sorted(glob.glob(os.path.join(DD, 'draft_#*.json')))
    files = []
    for f in allf:
        base = os.path.basename(f)
        ser = base[len("draft_"):-len(".json")]
        if ser in my:
            files.append(f)
    log("my=%d files=%d" % (len(my), len(files)))
    skip = ['R6', 'R7', 'R8', 'R10']  # R10 由合并门禁跨全量校验
    passed = failed = 0
    for f in files:
        try:
            r = json.load(open(f, encoding='utf-8'))
            s = r.get('serial', '')
            ctx = by.get(str(s).lstrip('#'), {})
            tmp = dict(ctx)
            tmp['recommend'] = r.get('recommend', '')
            iss = c.validate(tmp, others=[r.get('recommend','')], skip=skip)
            if iss:
                failed += 1
                log("FAIL %s: %s" % (s, iss))
            else:
                passed += 1
                log("PASS %s" % s)
        except Exception:
            failed += 1
            log("ERR %s: %s" % (f, traceback.format_exc().splitlines()[-1]))
    log("SUMMARY total=%d pass=%d fail=%d" % (len(files), passed, failed))
except Exception:
    log("EXC: " + traceback.format_exc())
print("done; see selftest.log")
