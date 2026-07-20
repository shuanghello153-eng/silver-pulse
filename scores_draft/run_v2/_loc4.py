import json, glob
for fp in sorted(glob.glob("scores_draft/run_v2/out/batch_*_out.json")):
    d=json.load(open(fp,encoding="utf-8"))
    for e in d["enterprises"]:
        if e["serial"]=="#0853":
            print(fp.split("\\")[-1], e["serial"], "| info=",e["info_score"],"diff=",e["diff_score"],"copy=",e["copy_score"],"sig=",e["signal_strength"])
            print("   rec=", repr(e["recommend"]))
