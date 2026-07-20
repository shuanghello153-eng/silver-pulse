import json, collections
p="data/enterprise/all_enterprises.json"
data=json.load(open(p,encoding="utf-8"))
n=len(data)
print("TOTAL:",n)
cnt=collections.Counter(); nonempty=collections.Counter()
for e in data:
    for k,v in e.items():
        cnt[k]+=1
        if v not in (None,"",[],{},0) and not (isinstance(v,str) and v.strip()==""):
            nonempty[k]+=1
print("\n=== FIELD: present/total, nonempty/total ===")
for k in sorted(cnt):
    print(f"{k:24s} {cnt[k]:4d}/{n}  ne={nonempty[k]:4d}")
print("\n=== SAMPLE VALUES per field (up to 3 non-empty, truncated) ===")
for k in sorted(cnt):
    samples=[]
    for e in data:
        v=e.get(k)
        if v not in (None,"",[],{},0) and not (isinstance(v,str) and v.strip()==""):
            s=json.dumps(v,ensure_ascii=False)
            if len(s)>120: s=s[:120]+"…"
            samples.append(s)
        if len(samples)>=3: break
    print(f"\n[{k}] ({nonempty[k]} non-empty)")
    for s in samples: print("   -",s)
