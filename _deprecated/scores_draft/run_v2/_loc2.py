import json, glob
for fp in sorted(glob.glob("scores_draft/run_v2/out/batch_*_out.json")):
    d=json.load(open(fp,encoding="utf-8"))
    for e in d["enterprises"]:
        if e["serial"]=="#0037":
            print(fp, "| rec=", repr(e["recommend"]))
            print("   diff/copy=", e["diff_score"], e["copy_score"], "| payor=", e.get("payor_model"))
