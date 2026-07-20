# -*- coding: utf-8 -*-
import json, glob, sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C

def main():
    SERIALS = set()
    for b in [52,53,54,55,56,57,58,59]:
        data = json.load(open(f"batches_full/batch_src_0{b}.json", encoding="utf-8"))
        for e in data:
            SERIALS.add(e["serial"])
    recs = {}
    for f in glob.glob("drafts_v4/draft_*.json"):
        d = json.load(open(f, encoding="utf-8"))
        if d.get("serial") in SERIALS and d.get("recommend"):
            recs[d["serial"]] = d["recommend"]
    ks = list(recs)
    sys.stderr.write("n=" + str(len(ks)) + "\n"); sys.stderr.flush()
    cnt = 0
    worst = []
    for i in range(len(ks)):
        for j in range(i+1, len(ks)):
            a, b = recs[ks[i]], recs[ks[j]]
            ov = C.lcs_len(a, b)
            if ov >= 15:
                sa, sb = set(a), set(b)
                r = len(sa & sb) / len(sa | sb) if (sa | sb) else 0
                if r > 0.5:
                    cnt += 1
                    if len(worst) < 8:
                        worst.append((ks[i], ks[j], round(r, 2), ov))
    print("R10>0.5 pairs:", cnt)
    for w in worst:
        print("  ", w)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(2)
