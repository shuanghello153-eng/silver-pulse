# -*- coding: utf-8 -*-
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "..", "data/enterprise/all_enterprises.json"))
def main():
    serial = sys.argv[1]
    d = json.load(open(DB, encoding="utf-8"))
    rec = [x for x in d if x.get("serial") == serial][0]
    keys = ["serial","name_cn","name_en","recommend","desc_cn","silver_reason",
            "payor_model","founded_year","stage","funding","funding_latest",
            "funding_total","highlights","events","business_model","coverage_regions",
            "domestic_competitors","rv"]
    for k in keys:
        v = rec.get(k)
        print("==%s==" % k)
        print(json.dumps(v, ensure_ascii=False))
    print("==OTHER_FIELDS==")
    print([k for k in rec.keys() if k not in keys])
if __name__ == "__main__": main()
