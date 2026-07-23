import json
m=json.load(open("scores_draft/run_v2/manifest.json",encoding="utf-8"))
ab=[x for x in m if x["tier"] in ("A","B")]
print("Tier A/B 批次数:",len(ab))
for x in ab:
    print(f"  batch {x['batch']:03d} | tier={x['tier']} | n={x['n']} | scored_in_db={x['scored_in_db']} | legacy_out={x['has_legacy_out']}")
# 同时输出这批的 serials 供子智能体
import os
os.makedirs("scores_draft/run_v2/batches_ab",exist_ok=True)
for x in ab:
    json.dump(x,open(f"scores_draft/run_v2/batches_ab/batch_{x['batch']:03d}_meta.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("已写出 14 批 meta")
