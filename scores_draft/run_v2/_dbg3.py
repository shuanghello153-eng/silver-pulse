import json
db=json.load(open("data/enterprise/all_enterprises.json",encoding="utf-8"))
for s in ["#1116","#1222","#1223","#1224"]:
    e=db[[x["serial"] for x in db].index(s)]
    print(s, "| name=",e.get("name"), "| bm=",e.get("business_model"), "| bmc=",e.get("business_model_cn"), "| cat2=",e.get("category_l2"))
    print("   REC:", e.get("recommend"))
