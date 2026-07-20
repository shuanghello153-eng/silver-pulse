import json, importlib.util, sys
spec = importlib.util.spec_from_file_location("wr", "write_recommends.py")
wr = importlib.util.module_from_spec(spec); spec.loader.exec_module(wr)
RECS = wr.RECS
sys.path.insert(0, ".")
import check_single as C
d = json.load(open('batches_full/batch_patch_gap.json', encoding='utf-8'))
by = {x['serial']: x for x in d}
print("source count", len(d), "RECS count", len(RECS))
missing = [s for s in by if s not in RECS]
print("missing RECS for serials:", missing)
# field issues using ORIGINAL fields
def cl(s): return len(''.join(s.split()))
fails_field = []
for s, e in by.items():
    dc = e.get('desc_cn','') or ''
    sr = e.get('silver_reason','') or ''
    pm = e.get('payor_model','')
    issues=[]
    if cl(dc) < 80 or dc.startswith(('是一家','致力于','专注于','作为一家','作为国内')):
        issues.append(f"R6(dc={cl(dc)})")
    if cl(sr) < 30:
        issues.append(f"R7(sr={cl(sr)})")
    if pm not in C.CANON:
        issues.append(f"R8({pm})")
    if issues:
        fails_field.append((s, issues))
print(f"\n=== {len(fails_field)} entries need field fixes (orig fields) ===")
for s, iss in fails_field:
    print(s, iss)
