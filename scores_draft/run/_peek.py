import json
# wave state
try:
    ws = json.load(open("_wave_state.json", encoding="utf-8"))
    print("=== _wave_state.json ===")
    print(json.dumps(ws, ensure_ascii=False, indent=1)[:1500])
except Exception as ex:
    print("wave_state err", ex)

# MANIFEST structure
m = json.load(open("MANIFEST.json", encoding="utf-8"))
print("\n=== MANIFEST type:", type(m))
if isinstance(m, dict):
    print("keys:", list(m.keys())[:20])
    for k in list(m.keys())[:3]:
        print(f"  [{k}] ->", str(m[k])[:300])
elif isinstance(m, list):
    print("len:", len(m))
    print("sample[0]:", str(m[0])[:400])
