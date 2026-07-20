import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))
db = json.load(open(DB, encoding="utf-8"))
# 旧格式(dict)样例
cnt=0
for e in db:
    r=e.get("recommend")
    if isinstance(r,dict):
        print("="*50)
        print(f"[{e['serial']}] {e.get('name')}")
        # 打印dict的key和内容摘要
        for k,v in r.items():
            s=str(v)
            print(f"  {k}: {s[:90]}")
        cnt+=1
        if cnt>=3: break
