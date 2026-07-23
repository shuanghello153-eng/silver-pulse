import json, glob
targets={"#1153","#1155","#1156","#1158","#1173"}
for fp in sorted(glob.glob("scores_draft/run_v2/out/batch_*_out.json")):
    d=json.load(open(fp,encoding="utf-8"))
    for e in d["enterprises"]:
        if e["serial"] in targets:
            print(fp.split("\\")[-1], e["serial"], "| sig/info/diff/copy=",e["signal_strength"],e["info_score"],e["diff_score"],e["copy_score"])
            print("   rec=", repr(e["recommend"]))
