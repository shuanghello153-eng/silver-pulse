import json, glob
for fp in sorted(glob.glob("scores_draft/run_v2/out/batch_*_out.json")):
    d=json.load(open(fp,encoding="utf-8"))
    for e in d["enterprises"]:
        if e["serial"]=="#0743":
            print(fp, "| rec=", repr(e["recommend"]))
            print("   sig/info/diff/copy=", e["signal_strength"], e["info_score"], e["diff_score"], e["copy_score"])
