import json, sys

DATA = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/all_enterprises.json"

serials = []
for b in ["batch_012","batch_013","batch_014"]:
    p = f"G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/rework/inbox/{b}.txt"
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                serials.append(int(line))

with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

idx = {}
for rec in data:
    s = rec.get("serial")
    if isinstance(s, str):
        idx[s] = rec  # keyed by "#0474" form

def serial_key(num):
    return f"#{int(num):04d}"

fields = ["serial","name","name_cn","region","founded","stage","tag_l1","tag_l2",
          "business_tags","funding_latest","funding_total","investors","desc_cn",
          "business_model","business_model_cn","recommend","payor_model",
          "signal_strength","info_score","diff_score","copy_score","research_value",
          "silver_verdict","silver_reason","website_url","category_l1","category_l2",
          "description","highlights","news_coverage","events"]

out = {}
for s in serials:
    key = f"#{int(s):04d}"
    if key in idx:
        rec = idx[key]
        out[key] = {k: rec.get(k) for k in fields}
    else:
        out[key] = {"__MISSING__": True}

with open("G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/rework/_mine_extracted.json",
          "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("extracted:", len(out), "missing:", sum(1 for v in out.values() if v.get('__MISSING__')))
print("keys:", list(out.keys()))
