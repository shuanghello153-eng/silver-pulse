import json
for fn in ["tag_review_all.json","nonsilver_all.json"]:
    d = json.load(open(fn, encoding="utf-8"))
    print("="*50, fn, "type=", type(d))
    if isinstance(d, list):
        print("  len:", len(d))
        print("  sample[0]:", json.dumps(d[0], ensure_ascii=False)[:600])
    elif isinstance(d, dict):
        print("  keys:", list(d.keys())[:10])
        k0 = list(d.keys())[0]
        print("  sample[",k0,"]:", json.dumps(d[k0], ensure_ascii=False)[:600])
